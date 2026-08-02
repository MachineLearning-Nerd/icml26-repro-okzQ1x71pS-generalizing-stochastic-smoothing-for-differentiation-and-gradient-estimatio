from __future__ import annotations

import json
import sys
from pathlib import Path

from .rendering_application import EXPECTED_HASHES, SOURCE_COMMIT


def check(path):
    result = json.loads(Path(path).read_text())
    protocol = result["paper_protocol"]
    source = result["source_audit"]
    capability = result["capability_test"]
    checks = {
        "exact_paper_scale_recorded": protocol["steps"] == 1000
        and protocol["seeds"] == 768
        and protocol["camera_degrees_of_freedom"] == 4,
        "exact_optimizer_recorded": protocol["optimizer"] == "Adam"
        and protocol["adam_betas"] == [0.5, 0.99]
        and protocol["initial_learning_rate"] == 0.3
        and protocol["scheduler"] == "CosineAnnealingLR",
        "exact_pose_domain_recorded": protocol["initial_orientation_error_degrees"] == [15, 75]
        and protocol["ground_truth_camera_distance"] == [2.5, 4.0]
        and protocol["initial_camera_distance"] == [2.0, 10.0]
        and protocol["success_orientation_error_below_degrees"] == 5,
        "pinned_primary_source": source["commit"] == SOURCE_COMMIT
        and all(
            source["files"][name]["sha256"] == expected
            for name, expected in EXPECTED_HASHES.items()
        ),
        "source_capability_audited": source["camera_script_hardcodes_cuda"]
        and source["setup_cuda_extension_count"] == 4
        and source["setup_cuda_kernel_count"] == 4
        and source["readme_explicitly_requires_cuda"],
        "source_is_not_exact_paper_implementation": source["cited_script_uses_normal_angles_not_uniform_sphere"]
        and source["cited_script_uses_internal_differentiable_renderer_not_black_box_sampling"],
        "cpu_build_fails_for_cuda_reason": capability["failed"]
        and capability["torch_cuda_available"] is False
        and capability["torch_cuda_build"] is None
        and capability["nvcc_path"] is None,
        "negative_control_fails_as_intended": result["negative_control"]["failed_as_intended"],
        "cpu_allocation_recorded": result["environment"]["selected_flavor_declared_vcpus"] == 8
        and result["environment"]["gpu_requested"] is False,
        "honest_blocked_verdict": result["verdict"] == "BLOCKED"
        and "substituting" in result["reason"],
    }
    output = {"checks": checks, "passed": all(checks.values())}
    print(json.dumps(output, indent=2))
    return output["passed"]


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python -m repro.check_rendering RESULT.json")
    raise SystemExit(0 if check(sys.argv[1]) else 1)
