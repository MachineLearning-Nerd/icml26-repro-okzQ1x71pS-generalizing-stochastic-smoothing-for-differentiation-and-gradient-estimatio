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
    oracle = result["oracle_audit"]
    checks = {
        "exact_disclosed_training_target_recorded": protocol["epochs"] == 50
        and protocol["seeds"] == 5,
        "exact_optimizer_schedule_recorded": protocol["batch_size"] == 70
        and protocol["optimizer"] == "Adam"
        and protocol["learning_rate"] == 0.001
        and protocol["scheduler_milestones_epochs"] == [30, 40]
        and protocol["scheduler_gamma"] == 0.1,
        "cited_primary_model_fixed": protocol["model_source_commit"]
        == "027e82ee818530f2823851d6530e0d2c8657bbcb"
        and protocol["model"]
        == "ResNet18 conv1/bn1/relu/maxpool/layer1, AdaptiveMaxPool2d(12,12), mean over 64 channels",
        "paper_variance_reduction_cell": protocol["distribution"] == "Logistic"
        and protocol["samples"] == 100
        and protocol["sampling"] == "randomized Latin hypercube"
        and protocol["covariate"] == "LOO",
        "official_archive_identity": data["archive_bytes"] == 915_169_563
        and data["archive_md5"] == "acea5ea60a47664ff189923a84814e96",
        "official_cardinality": data["train_examples"] == 10_000
        and data["test_examples"] == 1_000,
        "six_array_hashes_present": len(data["members"]) == 6
        and all(
            item["bytes"] > 0 and len(item["sha256"]) == 64
            for item in data["members"].values()
        ),
        "independent_path_oracle_confirms_quantization_compatible_labels": oracle["examples"] == 64
        and oracle["source_weight_dtype"] == "float16"
        and oracle["official_label_quantization_compatible_cost_match"] == 1.0
        and oracle["official_labels_all_valid_paths"]
        and oracle["all_oracle_paths_valid"],
        "negative_control_fails_as_intended": oracle["negative_control"]["failed_as_intended"]
        and oracle["negative_control"]["valid_path_fraction"] == 0.0
        and "required start cell" in oracle["negative_control"]["name"],
        "measured_not_formula_derived": calibration["warmup_steps"] == 2
        and calibration["measured_steps"] == 20
        and calibration["measured_seconds"] > 0,
        "finite_losses_and_projection": calibration["all_losses_finite"]
        and len(calibration["losses"]) == 20
        and all(
            math.isfinite(calibration[name]) and calibration[name] > 0
            for name in (
                "seconds_per_step",
                "projected_single_seed_hours",
                "projected_five_seed_serial_hours",
            )
        ),
        "full_test_predictions_are_paths": calibration["initial_full_test"]["all_predictions_valid_paths"]
        and calibration["final_full_test"]["all_predictions_valid_paths"],
        "cpu_allocation_recorded": result["environment"]["gpu_requested"] is False
        and result["environment"]["selected_flavor_declared_vcpus"] == 8
        and result["environment"]["path_workers"] == result["environment"]["worker_limit"]
        and result["environment"]["path_workers"] <= 8,
        "honest_blocked_verdict": result["verdict"] == "BLOCKED"
        and "not run" in result["reason"],
    }
    output = {"checks": checks, "passed": all(checks.values())}
    print(json.dumps(output, indent=2))
    return output["passed"]


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python -m repro.check_warcraft RESULT.json")
    raise SystemExit(0 if check(sys.argv[1]) else 1)
