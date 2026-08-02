from __future__ import annotations

import hashlib
import math
import os
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision.datasets import MNIST


CALIBRATION_STEPS = 100
WARMUP_STEPS = 5
PAPER_TRAINING_STEPS = 100_000
PAPER_SEEDS = 12
BATCH_SIZE = 100
SET_SIZE = 5
DIGITS = 4
SMOOTHING_SAMPLES = 256
GAMMA = 1.0 / 3.0


class SortingCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(1, 32, 5, padding=2)
        self.conv2 = nn.Conv2d(32, 64, 5, padding=2)
        self.fc1 = nn.Linear(DIGITS * 7 * 7 * 64, 64)
        self.fc2 = nn.Linear(64, 1)

    def forward(self, images):
        values = F.max_pool2d(F.relu(self.conv1(images)), 2)
        values = F.max_pool2d(F.relu(self.conv2(values)), 2)
        values = F.relu(self.fc1(values.flatten(1)))
        return self.fc2(values).reshape(-1, SET_SIZE)


def _sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        while chunk := handle.read(8 * 1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _digit_pools(targets):
    return [torch.flatnonzero(targets == digit) for digit in range(10)]


def _multi_mnist_batch(images, pools, generator):
    numbers = torch.randint(
        0, 10**DIGITS, (BATCH_SIZE, SET_SIZE), generator=generator
    )
    flattened = numbers.flatten()
    digit_columns = [
        torch.div(flattened, 10**power, rounding_mode="floor") % 10
        for power in range(DIGITS - 1, -1, -1)
    ]
    selected = torch.empty(
        (len(flattened), DIGITS, 28, 28), dtype=torch.float32
    )
    for column, labels in enumerate(digit_columns):
        for digit, pool in enumerate(pools):
            positions = torch.flatnonzero(labels == digit)
            if len(positions) == 0:
                continue
            offsets = torch.randint(len(pool), (len(positions),), generator=generator)
            selected[positions, column] = images[pool[offsets]].float() / 255.0
    return selected.reshape(-1, 1, DIGITS * 28, 28), numbers


def _ranks(values):
    order = torch.argsort(values, dim=-1, stable=True)
    return torch.argsort(order, dim=-1, stable=True)


def _latin_laplace_noise(generator):
    uniforms = torch.empty((SMOOTHING_SAMPLES, SET_SIZE))
    for dimension in range(SET_SIZE):
        cells = torch.randperm(SMOOTHING_SAMPLES, generator=generator)
        jitter = torch.rand(SMOOTHING_SAMPLES, generator=generator)
        uniforms[:, dimension] = (cells + jitter) / SMOOTHING_SAMPLES
    uniforms = uniforms.clamp(1e-7, 1.0 - 1e-7)
    return torch.where(
        uniforms < 0.5,
        torch.log(2.0 * uniforms),
        -torch.log(2.0 * (1.0 - uniforms)),
    )


def smoothed_permutation(values, generator):
    noise = _latin_laplace_noise(generator)
    perturbed = values[:, None, :] + GAMMA * noise[None, :, :]
    ranks = _ranks(perturbed)
    permutations = F.one_hot(ranks, num_classes=SET_SIZE).float()
    mean = permutations.mean(dim=1)
    centered = SMOOTHING_SAMPLES / (SMOOTHING_SAMPLES - 1) * (
        permutations - mean[:, None]
    )
    scores = torch.sign(noise) / GAMMA
    jacobian = torch.einsum("bsir,sj->birj", centered, scores) / SMOOTHING_SAMPLES
    linear = torch.einsum("birj,bj->bir", jacobian.detach(), values)
    return mean.detach() + linear - linear.detach()


def _loss(model, images, numbers, generator):
    values = model(images)
    probabilities = smoothed_permutation(values, generator)
    target = F.one_hot(_ranks(numbers), num_classes=SET_SIZE).float()
    return -(target * torch.log(probabilities + 1e-6)).sum() / (BATCH_SIZE * SET_SIZE)


def _exact_match(model, images, pools, seed, batches=10):
    generator = torch.Generator().manual_seed(seed)
    correct = 0
    total = 0
    model.eval()
    with torch.no_grad():
        for _ in range(batches):
            batch_images, numbers = _multi_mnist_batch(images, pools, generator)
            predicted = _ranks(model(batch_images))
            correct += int(torch.all(predicted == _ranks(numbers), dim=1).sum())
            total += BATCH_SIZE
    model.train()
    return correct / total


def run_mnist_calibration():
    torch.manual_seed(24_102_025)
    threads = min(32, os.cpu_count() or 1)
    torch.set_num_threads(threads)
    root = Path(".cache/openresearch/mnist")
    train = MNIST(root, train=True, download=True)
    test = MNIST(root, train=False, download=True)
    train_images = train.data[:55_000]
    validation_images = train.data[55_000:]
    train_pools = _digit_pools(train.targets[:55_000])
    validation_pools = _digit_pools(train.targets[55_000:])
    test_pools = _digit_pools(test.targets)

    model = SortingCNN()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    data_generator = torch.Generator().manual_seed(31_415)
    noise_generator = torch.Generator().manual_seed(27_182)
    initial_accuracy = _exact_match(model, validation_images, validation_pools, 41_421)
    losses = []
    measured_started = None
    for step in range(WARMUP_STEPS + CALIBRATION_STEPS):
        if step == WARMUP_STEPS:
            measured_started = time.perf_counter()
        batch_images, numbers = _multi_mnist_batch(train_images, train_pools, data_generator)
        optimizer.zero_grad()
        loss = _loss(model, batch_images, numbers, noise_generator)
        loss.backward()
        optimizer.step()
        if step >= WARMUP_STEPS:
            losses.append(float(loss.detach()))
    measured_seconds = time.perf_counter() - measured_started
    final_accuracy = _exact_match(model, validation_images, validation_pools, 41_421)
    test_accuracy = _exact_match(model, test.data, test_pools, 51_521)
    seconds_per_step = measured_seconds / CALIBRATION_STEPS
    projected_single_seed_hours = seconds_per_step * PAPER_TRAINING_STEPS / 3600.0
    projected_serial_hours = projected_single_seed_hours * PAPER_SEEDS

    raw_files = sorted((root / "MNIST" / "raw").glob("*"))
    return {
        "route": "exact-protocol throughput calibration, not full training",
        "paper_protocol": {
            "set_size": SET_SIZE,
            "digits_per_image": DIGITS,
            "training_steps": PAPER_TRAINING_STEPS,
            "seeds": PAPER_SEEDS,
            "batch_size": BATCH_SIZE,
            "optimizer": "Adam",
            "learning_rate": 0.001,
            "architecture": [
                "Conv2d(1,32,5,padding=2)",
                "ReLU",
                "MaxPool2d(2)",
                "Conv2d(32,64,5,padding=2)",
                "ReLU",
                "MaxPool2d(2)",
                "Linear(12544,64)",
                "ReLU",
                "Linear(64,1)",
            ],
            "distribution": "Laplace",
            "samples": SMOOTHING_SAMPLES,
            "sampling": "randomized Latin hypercube",
            "covariate": "LOO",
            "gamma": GAMMA,
            "loss": "row cross-entropy against the exact hard permutation",
        },
        "calibration": {
            "warmup_steps": WARMUP_STEPS,
            "measured_steps": CALIBRATION_STEPS,
            "measured_seconds": measured_seconds,
            "seconds_per_step": seconds_per_step,
            "projected_single_seed_hours": projected_single_seed_hours,
            "projected_twelve_seed_serial_hours": projected_serial_hours,
            "initial_validation_exact_match": initial_accuracy,
            "final_validation_exact_match": final_accuracy,
            "test_exact_match_after_calibration": test_accuracy,
            "loss_first_ten_mean": float(np.mean(losses[:10])),
            "loss_last_ten_mean": float(np.mean(losses[-10:])),
            "all_losses_finite": bool(np.all(np.isfinite(losses))),
        },
        "data_audit": {
            "torchvision_train_images": len(train.data),
            "train_split_images": len(train_images),
            "validation_split_images": len(validation_images),
            "test_images": len(test.data),
            "raw_files": {
                path.name: {"bytes": path.stat().st_size, "sha256": _sha256(path)}
                for path in raw_files
                if path.is_file()
            },
        },
        "environment": {
            "estimated_useful_cores": 32,
            "actual_logical_cpus": os.cpu_count(),
            "torch_threads": threads,
            "gpu_requested": False,
        },
        "seeds": {
            "model": 24_102_025,
            "training_data": 31_415,
            "training_noise": 27_182,
            "validation": 41_421,
            "test": 51_521,
        },
        "verdict": "BLOCKED",
        "reason": "The disclosed 100,000-step, 12-seed protocol was calibrated but not run in this route.",
    }
