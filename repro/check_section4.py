from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path


DISTRIBUTIONS = ("Gaussian", "Logistic", "Gumbel", "Cauchy", "Laplace", "Triangular")


def check(result_path, csv_path):
    result = json.loads(Path(result_path).read_text())
    with Path(csv_path).open(newline="") as handle:
        rows = list(csv.DictReader(handle))

    finite = all(math.isfinite(float(row["mean_l2_error"])) for row in rows)
    sorting_cases = []
    ranking_pass = True
    for size in ("n=3", "n=5"):
        for distribution in DISTRIBUTIONS:
            candidates = [
                row
                for row in rows
                if row["domain"] == "sorting"
                and row["size"] == size
                and row["distribution"] == distribution
                and row["antithetic"] == "False"
            ]
            minimum = min(float(row["mean_l2_error"]) for row in candidates)
            target_strategy = "QMC-latin" if distribution == "Triangular" else "RQMC-cartesian"
            target = next(
                row
                for row in candidates
                if row["strategy"] == target_strategy and row["covariate"] == "LOO"
            )
            target_error = float(target["mean_l2_error"])
            passed = target_error <= 1.01 * minimum
            ranking_pass = ranking_pass and passed
            sorting_cases.append(
                {
                    "size": size,
                    "distribution": distribution,
                    "target_strategy": target_strategy,
                    "target_error": target_error,
                    "minimum_error": minimum,
                    "passed": passed,
                }
            )

    summary = result["summary"]
    checks = {
        "row_count_447": len(rows) == 447,
        "all_mean_errors_finite": finite,
        "six_distributions": sorted({row["distribution"] for row in rows}) == sorted(DISTRIBUTIONS),
        "four_operator_sizes": sorted({row["size"] for row in rows})
        == ["12x12", "8x8", "n=3", "n=5"],
        "summary_row_count_matches": summary["cell_count"] == len(rows),
        "official_dataset_md5_matches": result["warcraft_dataset_audit"]["verified_md5"]
        == result["warcraft_dataset_audit"]["published_md5"]
        == "acea5ea60a47664ff189923a84814e96",
        "official_8x8_and_12x12_maps_used": set(
            result["warcraft_dataset_audit"]["members_used"]
        )
        == {"8", "12"},
        "held_out_path_perturbations_non_vacuous": all(
            0.1 <= audit["held_out_path_change_rate"] <= 0.9
            for audit in result["path_scale_calibration"]
        ),
        "twelve_path_scale_calibrations": len(result["path_scale_calibration"]) == 12,
        "all_paths_valid": all(
            audit["all_binary"] and audit["all_connected_8_neighborhood"]
            for audit in result["path_checks"]
        ),
        "path_oracle_uncertainty_passes": all(
            audit["uncertainty_over_minimum_error"] < 0.2
            for audit in result["path_oracle_audit"]
        ),
        "wrong_score_control_passes": result["negative_control"]["wrong_over_correct"] > 1.25,
        "paper_ranking_passes": ranking_pass,
    }
    output = {"checks": checks, "sorting_cases": sorting_cases, "passed": all(checks.values())}
    print(json.dumps(output, indent=2))
    return output["passed"]


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: python -m repro.check_section4 RESULT.json RESULTS.csv")
    raise SystemExit(0 if check(sys.argv[1], sys.argv[2]) else 1)
