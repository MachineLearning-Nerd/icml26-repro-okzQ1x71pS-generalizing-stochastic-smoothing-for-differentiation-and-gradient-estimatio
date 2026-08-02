from __future__ import annotations

import json
import math
import sys
from pathlib import Path


def check(path):
    result = json.loads(Path(path).read_text())
    protocol = result["paper_protocol"]
    calibration = result["calibration"]
    data = result["data_audit"]
    checks = {
        "exact_disclosed_training_target_recorded": protocol["training_steps"] == 100_000
        and protocol["seeds"] == 12,
        "exact_batch_and_optimizer_recorded": protocol["batch_size"] == 100
        and protocol["optimizer"] == "Adam"
        and protocol["learning_rate"] == 0.001,
        "exact_n5_four_digit_task": protocol["set_size"] == 5
        and protocol["digits_per_image"] == 4,
        "cited_cnn_shape": protocol["architecture"]
        == [
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
        "paper_256_sample_laplace_cell": protocol["distribution"] == "Laplace"
        and protocol["samples"] == 256
        and protocol["covariate"] == "LOO",
        "measured_not_formula_derived": calibration["warmup_steps"] == 5
        and calibration["measured_steps"] == 100
        and calibration["measured_seconds"] > 0,
        "finite_throughput_projection": all(
            math.isfinite(calibration[name]) and calibration[name] > 0
            for name in (
                "seconds_per_step",
                "projected_single_seed_hours",
                "projected_twelve_seed_serial_hours",
            )
        ),
        "losses_finite": calibration["all_losses_finite"],
        "official_mnist_cardinality": data["torchvision_train_images"] == 60_000
        and data["train_split_images"] == 55_000
        and data["validation_split_images"] == 5_000
        and data["test_images"] == 10_000,
        "raw_dataset_hashes_present": len(data["raw_files"]) >= 2
        and all(item["bytes"] > 0 and len(item["sha256"]) == 64 for item in data["raw_files"].values()),
        "cpu_only": result["environment"]["gpu_requested"] is False,
        "honest_blocked_verdict": result["verdict"] == "BLOCKED"
        and "not run" in result["reason"],
    }
    output = {"checks": checks, "passed": all(checks.values())}
    print(json.dumps(output, indent=2))
    return output["passed"]


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python -m repro.check_mnist RESULT.json")
    raise SystemExit(0 if check(sys.argv[1]) else 1)
