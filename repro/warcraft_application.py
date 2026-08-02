from __future__ import annotations

import hashlib
import io
import math
import multiprocessing
import os
import tarfile
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import torch
import torch.nn as nn
from torchvision.models import resnet18

from .section4 import (
    WARCRAFT_BYTES,
    WARCRAFT_MD5,
    WARCRAFT_URL,
    _download_warcraft_archive,
    shortest_path_batch,
    shortest_path_indicator,
)


SIZE = 12
BATCH_SIZE = 70
SMOOTHING_SAMPLES = 100
GAMMA = 0.1
WARMUP_STEPS = 2
CALIBRATION_STEPS = 20
PAPER_EPOCHS = 50
PAPER_SEEDS = 5
SOURCE_COMMIT = "027e82ee818530f2823851d6530e0d2c8657bbcb"
ARRAY_NAMES = (
    "train_maps.npy",
    "train_vertex_weights.npy",
    "train_shortest_paths.npy",
    "test_maps.npy",
    "test_vertex_weights.npy",
    "test_shortest_paths.npy",
)


class WarcraftFirstBlockResNet18(nn.Module):
    def __init__(self):
        super().__init__()
        backbone = resnet18(weights=None)
        self.conv1 = backbone.conv1
        self.bn1 = backbone.bn1
        self.relu = backbone.relu
        self.maxpool = backbone.maxpool
        self.layer1 = backbone.layer1
        self.pool = nn.AdaptiveMaxPool2d((SIZE, SIZE))

    def forward(self, maps):
        values = self.conv1(maps)
        values = self.bn1(values)
        values = self.relu(values)
        values = self.maxpool(values)
        values = self.layer1(values)
        return self.pool(values).mean(dim=1).flatten(1)


def _sha256(data):
    return hashlib.sha256(data).hexdigest()


def _load_official_arrays():
    archive = _download_warcraft_archive()
    payloads = {}
    member_names = {}
    with tarfile.open(archive, "r|gz") as bundle:
        for member in bundle:
            name = next(
                (
                    candidate
                    for candidate in ARRAY_NAMES
                    if member.name.endswith(f"/12x12/{candidate}")
                    or member.name == f"12x12/{candidate}"
                ),
                None,
            )
            if name is None:
                continue
            handle = bundle.extractfile(member)
            if handle is None:
                raise RuntimeError(f"could not read {member.name}")
            payloads[name] = handle.read()
            member_names[name] = member.name
    missing = sorted(set(ARRAY_NAMES) - set(payloads))
    if missing:
        raise RuntimeError(f"missing official Warcraft arrays: {missing}")
    arrays = {
        name: np.load(io.BytesIO(payload), allow_pickle=False)
        for name, payload in payloads.items()
    }
    audit = {
        name: {
            "member": member_names[name],
            "bytes": len(payloads[name]),
            "sha256": _sha256(payloads[name]),
            "shape": list(arrays[name].shape),
            "dtype": str(arrays[name].dtype),
        }
        for name in ARRAY_NAMES
    }
    return arrays, audit


def _channel_first(maps):
    maps = np.asarray(maps, dtype=np.float32)
    if maps.ndim != 4:
        raise RuntimeError(f"expected four-dimensional Warcraft maps, got {maps.shape}")
    if maps.shape[-1] == 3:
        maps = np.moveaxis(maps, -1, 1)
    if maps.shape[1:] != (3, SIZE, SIZE):
        raise RuntimeError(f"unexpected Warcraft map shape {maps.shape}")
    return maps


def _path_arrays(values):
    values = np.asarray(values, dtype=np.float32)
    if values.shape[1:] == (SIZE, SIZE):
        return values.reshape(len(values), SIZE * SIZE)
    if values.shape[1:] == (SIZE * SIZE,):
        return values
    raise RuntimeError(f"unexpected path or weight shape {values.shape}")


def _solve_chunk(log_costs):
    return shortest_path_batch(log_costs, SIZE)


def _parallel_paths(executor, log_costs, workers):
    chunks = [chunk for chunk in np.array_split(log_costs, workers) if len(chunk)]
    return np.concatenate(list(executor.map(_solve_chunk, chunks)), axis=0)


def _latin_logistic_noise(rng, batch):
    random_order = rng.random((batch, SMOOTHING_SAMPLES, SIZE * SIZE))
    cells = np.argsort(random_order, axis=1)
    uniforms = (cells + rng.random(cells.shape)) / SMOOTHING_SAMPLES
    uniforms = np.clip(uniforms, 1e-7, 1.0 - 1e-7)
    return np.log(uniforms / (1.0 - uniforms))


def _smoothed_mse(log_costs, targets, rng, executor, workers):
    noise = _latin_logistic_noise(rng, len(log_costs))
    perturbed = log_costs.detach().numpy()[:, None, :] + GAMMA * noise
    paths = _parallel_paths(executor, perturbed.reshape(-1, SIZE * SIZE), workers)
    paths = paths.reshape(len(log_costs), SMOOTHING_SAMPLES, SIZE * SIZE)
    mean_paths = paths.mean(axis=1)
    target_array = targets.numpy()
    loss_value = float(np.mean((mean_paths - target_array) ** 2))
    output_gradient = 2.0 * (mean_paths - target_array) / (len(log_costs) * SIZE * SIZE)
    centered = SMOOTHING_SAMPLES / (SMOOTHING_SAMPLES - 1) * (
        paths - mean_paths[:, None, :]
    )
    scores = np.tanh(noise / 2.0) / GAMMA
    input_gradient = np.einsum(
        "bso,bsi,bo->bi", centered, scores, output_gradient, optimize=True
    ) / SMOOTHING_SAMPLES
    gradient = torch.from_numpy(input_gradient).to(dtype=log_costs.dtype)
    surrogate = torch.sum(log_costs * gradient)
    return torch.tensor(loss_value, dtype=log_costs.dtype) + surrogate - surrogate.detach()


def _valid_path(indicator):
    active = set(np.flatnonzero(indicator > 0.5).tolist())
    if 0 not in active or SIZE * SIZE - 1 not in active:
        return False
    frontier = [0]
    visited = {0}
    while frontier:
        node = frontier.pop()
        row, column = divmod(node, SIZE)
        for row_delta in (-1, 0, 1):
            for column_delta in (-1, 0, 1):
                if row_delta == column_delta == 0:
                    continue
                neighbor_row = row + row_delta
                neighbor_column = column + column_delta
                neighbor = neighbor_row * SIZE + neighbor_column
                if (
                    0 <= neighbor_row < SIZE
                    and 0 <= neighbor_column < SIZE
                    and neighbor in active
                    and neighbor not in visited
                ):
                    visited.add(neighbor)
                    frontier.append(neighbor)
    return visited == active and SIZE * SIZE - 1 in visited


def _exact_match(model, maps, targets):
    predictions = []
    model.eval()
    with torch.no_grad():
        for start in range(0, len(maps), BATCH_SIZE):
            log_costs = model(maps[start : start + BATCH_SIZE]).numpy()
            predictions.append(shortest_path_batch(log_costs, SIZE))
    model.train()
    predictions = np.concatenate(predictions, axis=0)
    target_array = targets.numpy()
    return {
        "exact_match": float(np.mean(np.all(predictions == target_array, axis=1))),
        "all_predictions_valid_paths": bool(all(_valid_path(path) for path in predictions)),
        "predicted_path_length_mean": float(predictions.sum(axis=1).mean()),
    }


def run_warcraft_calibration():
    torch.manual_seed(24_103_025)
    rng = np.random.default_rng(31_416)
    threads = min(32, os.cpu_count() or 1)
    workers = min(32, os.cpu_count() or 1)
    torch.set_num_threads(threads)
    arrays, member_audit = _load_official_arrays()
    train_maps = _channel_first(arrays["train_maps.npy"])
    test_maps = _channel_first(arrays["test_maps.npy"])
    train_paths = _path_arrays(arrays["train_shortest_paths.npy"])
    test_paths = _path_arrays(arrays["test_shortest_paths.npy"])
    train_weights = _path_arrays(arrays["train_vertex_weights.npy"])
    test_weights = _path_arrays(arrays["test_vertex_weights.npy"])

    channel_mean = train_maps.mean(axis=(0, 2, 3), dtype=np.float64).astype(np.float32)
    channel_std = train_maps.std(axis=(0, 2, 3), dtype=np.float64).astype(np.float32)
    if np.any(channel_std <= 0):
        raise RuntimeError("official Warcraft maps have a zero-variance channel")
    train_maps = (train_maps - channel_mean[None, :, None, None]) / channel_std[None, :, None, None]
    test_maps = (test_maps - channel_mean[None, :, None, None]) / channel_std[None, :, None, None]
    train_maps = torch.from_numpy(train_maps)
    test_maps = torch.from_numpy(test_maps)
    train_paths = torch.from_numpy(train_paths)
    test_paths = torch.from_numpy(test_paths)

    oracle_count = min(64, len(test_weights))
    oracle_paths = np.asarray(
        [shortest_path_indicator(np.log(np.maximum(row, 1e-12)), SIZE) for row in test_weights[:oracle_count]]
    )
    oracle_labels = test_paths[:oracle_count].numpy()
    shifted_labels = np.roll(oracle_labels, 1, axis=1)
    oracle_audit = {
        "examples": oracle_count,
        "official_label_exact_match": float(np.mean(np.all(oracle_paths == oracle_labels, axis=1))),
        "all_oracle_paths_valid": bool(all(_valid_path(path) for path in oracle_paths)),
        "negative_control": {
            "name": "cyclically shift every official path label by one flattened cell",
            "exact_match": float(np.mean(np.all(oracle_paths == shifted_labels, axis=1))),
            "failed_as_intended": bool(np.mean(np.all(oracle_paths == shifted_labels, axis=1)) < 0.1),
        },
    }

    model = WarcraftFirstBlockResNet18()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    scheduler = torch.optim.lr_scheduler.MultiStepLR(optimizer, milestones=[30, 40], gamma=0.1)
    initial_test = _exact_match(model, test_maps, test_paths)
    order = rng.permutation(len(train_maps))
    losses = []
    measured_started = None
    with ProcessPoolExecutor(
        max_workers=workers, mp_context=multiprocessing.get_context("spawn")
    ) as executor:
        for step in range(WARMUP_STEPS + CALIBRATION_STEPS):
            if step == WARMUP_STEPS:
                measured_started = time.perf_counter()
            start = step * BATCH_SIZE
            indices = order[start : start + BATCH_SIZE]
            if len(indices) != BATCH_SIZE:
                raise RuntimeError("calibration unexpectedly exhausted the training permutation")
            optimizer.zero_grad()
            log_costs = model(train_maps[indices])
            loss = _smoothed_mse(log_costs, train_paths[indices], rng, executor, workers)
            loss.backward()
            optimizer.step()
            if step >= WARMUP_STEPS:
                losses.append(float(loss.detach()))
    measured_seconds = time.perf_counter() - measured_started
    final_test = _exact_match(model, test_maps, test_paths)
    seconds_per_step = measured_seconds / CALIBRATION_STEPS
    steps_per_epoch = math.ceil(len(train_maps) / BATCH_SIZE)
    projected_single_seed_hours = seconds_per_step * steps_per_epoch * PAPER_EPOCHS / 3600.0

    return {
        "route": "official-data exact-protocol CPU throughput calibration, not full training",
        "paper_protocol": {
            "dataset": "official Warcraft 12x12 split",
            "epochs": PAPER_EPOCHS,
            "seeds": PAPER_SEEDS,
            "batch_size": BATCH_SIZE,
            "optimizer": "Adam",
            "learning_rate": 0.001,
            "scheduler_milestones_epochs": [30, 40],
            "scheduler_gamma": 0.1,
            "model": "ResNet18 conv1/bn1/relu/maxpool/layer1, AdaptiveMaxPool2d(12,12), mean over 64 channels",
            "model_source_commit": SOURCE_COMMIT,
            "distribution": "Logistic",
            "samples": SMOOTHING_SAMPLES,
            "sampling": "randomized Latin hypercube",
            "covariate": "LOO",
            "smoothing_target": "shortest-path algorithm",
            "loss": "MSE against ground-truth hard path",
        },
        "reconstruction_choices": {
            "gamma": GAMMA,
            "gamma_reason": "fixed disclosed Figure 7 sweep value; the paper does not identify a single selected gamma for Figure 6",
            "cost_parameterization": "network output is log vertex cost and is exponentiated by the shortest-path oracle",
            "noise_independence": "one independently randomized Latin design per batch item and step",
            "scheduler_instantiated_but_not_advanced": scheduler.last_epoch,
        },
        "calibration": {
            "warmup_steps": WARMUP_STEPS,
            "measured_steps": CALIBRATION_STEPS,
            "measured_seconds": measured_seconds,
            "seconds_per_step": seconds_per_step,
            "steps_per_paper_epoch": steps_per_epoch,
            "projected_single_seed_hours": projected_single_seed_hours,
            "projected_five_seed_serial_hours": projected_single_seed_hours * PAPER_SEEDS,
            "losses": losses,
            "loss_first_five_mean": float(np.mean(losses[:5])),
            "loss_last_five_mean": float(np.mean(losses[-5:])),
            "all_losses_finite": bool(np.all(np.isfinite(losses))),
            "initial_full_test": initial_test,
            "final_full_test": final_test,
        },
        "data_audit": {
            "source_url": WARCRAFT_URL,
            "dataset_doi": "10.17617/3.YJCQ5S",
            "archive_bytes": WARCRAFT_BYTES,
            "archive_md5": WARCRAFT_MD5,
            "train_examples": len(train_maps),
            "test_examples": len(test_maps),
            "normalization_mean": channel_mean.tolist(),
            "normalization_std": channel_std.tolist(),
            "members": member_audit,
        },
        "oracle_audit": oracle_audit,
        "environment": {
            "estimated_useful_cores": 32,
            "actual_logical_cpus": os.cpu_count(),
            "torch_threads": threads,
            "path_workers": workers,
            "gpu_requested": False,
        },
        "seeds": {"model": 24_103_025, "data_and_noise": 31_416},
        "verdict": "BLOCKED",
        "reason": "The disclosed 50-epoch, five-seed protocol was calibrated but not run; this route cannot establish the complete four-application claim.",
    }
