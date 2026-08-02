from __future__ import annotations

import json
import sys
from pathlib import Path

from .tem_application import SOURCES


def check(path):
    result = json.loads(Path(path).read_text())
    protocol = result["paper_protocol"]
    sources = result["primary_source_audit"]
    falsification = result["falsification"]
    checks = {
        "exact_claim_logic_recorded": result["claim_logic"]["quantifier"]
        == "existential historical empirical demonstration"
        and len(result["claim_logic"]["assumptions"]) == 6
        and "every stated assumption" in result["claim_logic"]["falsification_requirement"],
        "exact_image_and_ground_truth_recorded": protocol["image_shape"] == [400, 400]
        and protocol["ground_truth"]
        == {
            "acceleration_voltage_kv": 300,
            "focal_length_mm": 3,
            "x_position_nm": 0,
            "y_position_nm": 0,
        },
        "exact_search_domains_recorded": protocol["two_parameter_domain"]
        == {"acceleration_voltage_kv": [0, 1000], "x_position_nm": [-5, 5]}
        and protocol["four_parameter_domain"]
        == {
            "acceleration_voltage_kv": [0, 600],
            "focal_length_mm": [0, 6],
            "x_position_nm": [-3, 3],
            "y_position_nm": [-3, 3],
        },
        "exact_disclosed_optimizer_recorded": protocol["optimizer"] == "Adam"
        and protocol["adam_betas"] == [0.5, 0.9]
        and protocol["random_search_repetitions"] == 20,
        "primary_archive_identities_verified": set(sources) == set(SOURCES)
        and all(sources[name]["identity_verified"] for name in SOURCES)
        and all(
            any(attempt.get("identity_match") for attempt in sources[name]["attempts"])
            for name in SOURCES
        ),
        "archives_are_safe_and_auditable": all(
            sources[name]["archive"]["is_zip"]
            and sources[name]["archive"]["all_paths_safe"]
            and sources[name]["archive"]["member_count"] > 0
            for name in SOURCES
        ),
        "cpu_capability_recorded_without_proxy_claim": result["cpu_capability"][
            "elf_candidate_count"
        ]
        >= 0
        and result["cpu_capability"]["exact_demonstration_executed"] is False,
        "negative_control_fails_as_intended": result["negative_control"][
            "failed_as_intended"
        ]
        and result["negative_control"]["identity_verifier_rejected_corruption"],
        "four_distinct_routes_recorded": len(falsification["routes_completed"]) == 4
        and len(set(falsification["routes_completed"])) == 4,
        "no_invalid_falsification": falsification["counterexample_found"] is False
        and falsification["all_paper_assumptions_satisfied"] is False
        and "cannot contradict" in falsification["conclusion"],
        "cpu_allocation_recorded": result["environment"][
            "selected_flavor_declared_vcpus"
        ]
        == 8
        and result["environment"]["gpu_requested"] is False,
        "honest_blocked_verdict": result["verdict"] == "BLOCKED"
        and "No assumption-satisfying counterexample" in result["reason"],
    }
    output = {"checks": checks, "passed": all(checks.values())}
    print(json.dumps(output, indent=2))
    return output["passed"]


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python -m repro.check_tem RESULT.json")
    raise SystemExit(0 if check(sys.argv[1]) else 1)
