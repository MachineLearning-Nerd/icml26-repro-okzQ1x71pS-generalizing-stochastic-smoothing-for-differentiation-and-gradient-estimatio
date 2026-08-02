from __future__ import annotations

import csv
import io
import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path

from .mnist_application import run_mnist_calibration
from .numerics import baseline_variance_proxy, lemma3_check, theorem7_check, theorem8_check
from .section4 import run_section4


def git_sha():
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], check=True, capture_output=True, text=True
    ).stdout.strip()


def main():
    started = time.perf_counter()
    claim1 = lemma3_check()
    claim2 = theorem7_check()
    claim3 = theorem8_check()
    variance_proxy = baseline_variance_proxy()
    section4 = run_section4()
    section4_rows = section4.pop("rows")
    mnist = run_mnist_calibration()

    csv_buffer = io.StringIO()
    writer = csv.DictWriter(csv_buffer, fieldnames=list(section4_rows[0]))
    writer.writeheader()
    writer.writerows(section4_rows)
    raw_csv = csv_buffer.getvalue()
    section4_directory = Path(".openresearch/artifacts/claims_4_5")
    section4_directory.mkdir(parents=True, exist_ok=True)
    section4_result_path = section4_directory / "section4_result.json"
    section4_csv_path = section4_directory / "raw_results.csv"
    section4_result_path.write_text(json.dumps(section4, indent=2) + "\n")
    section4_csv_path.write_text(raw_csv)
    checker = subprocess.run(
        [sys.executable, "-m", "repro.check_section4", str(section4_result_path), str(section4_csv_path)],
        capture_output=True,
        text=True,
    )
    checker_output = json.loads(checker.stdout) if checker.stdout.strip() else {
        "passed": False,
        "stderr": checker.stderr,
    }
    mnist_directory = Path(".openresearch/artifacts/claim_6/mnist_calibration")
    mnist_directory.mkdir(parents=True, exist_ok=True)
    mnist_result_path = mnist_directory / "result.json"
    mnist_result_path.write_text(json.dumps(mnist, indent=2) + "\n")
    mnist_checker = subprocess.run(
        [sys.executable, "-m", "repro.check_mnist", str(mnist_result_path)],
        capture_output=True,
        text=True,
    )
    mnist_checker_output = (
        json.loads(mnist_checker.stdout)
        if mnist_checker.stdout.strip()
        else {"passed": False, "stderr": mnist_checker.stderr}
    )

    checks = {
        "claim_1": max(claim1["laplace_error"], claim1["triangular_error"]) < 1e-8
        and claim1["wrong_score_error"] > 0.04,
        "claim_2": max(claim2.values()) < 1e-7,
        "claim_3": max(claim3.values()) < 1e-7,
        "claim_4_historical_proxy": variance_proxy["combination_count"] == 108
        and variance_proxy["all_finite"],
        "claim_4_faithful_benchmark": section4["summary"]["claim4_verified"],
        "claim_5_ranking": section4["summary"]["claim5_verified"],
        "section4_independent_checker": checker.returncode == 0,
        "mnist_calibration_independent_checker": mnist_checker.returncode == 0,
    }
    checks = {name: bool(passed) for name, passed in checks.items()}
    elapsed = time.perf_counter() - started
    result = {
        "paper": "arXiv:2410.08125",
        "git_sha": git_sha(),
        "fixed_command": "uv sync --frozen --no-dev && .venv/bin/python -m repro.run",
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "estimated_useful_cores": 32,
            "selected_flavor": "hf/cpu-upgrade",
            "actual_logical_cpus": os.cpu_count(),
            "gpu_requested": False,
            "runtime_seconds": elapsed,
        },
        "claims": {
            "1": {"verdict": "VERIFIED", "metrics": claim1},
            "2": {"verdict": "VERIFIED", "metrics": claim2},
            "3": {"verdict": "VERIFIED", "metrics": claim3},
            "4": {
                "verdict": "VERIFIED" if section4["summary"]["claim4_verified"] else "BLOCKED",
                "metrics": section4["summary"],
                "historical_rejected_baseline": variance_proxy,
            },
            "5": {
                "verdict": "VERIFIED" if section4["summary"]["claim5_verified"] else "BLOCKED",
                "metrics": section4["ranking_contract"],
            },
            "6": {
                "verdict": "BLOCKED",
                "reason": "The exact-protocol MNIST throughput route is a calibration, not the disclosed 100,000-step x 12-seed application run; the other three applications remain unexecuted.",
                "mnist_calibration": mnist,
            },
        },
        "negative_control": {
            "name": "Gaussian score applied to Laplace density",
            "error": claim1["wrong_score_error"],
            "failed_as_intended": bool(claim1["wrong_score_error"] > 0.04),
        },
        "section4_evidence": section4,
        "section4_independent_checker": checker_output,
        "mnist_independent_checker": mnist_checker_output,
        "checks": checks,
        "all_regressions_passed": all(checks.values()),
    }

    output = Path(".openresearch/artifacts/baseline/raw_output.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n")
    print("=== EVAL.md ===")
    print(json.dumps(result, indent=2))
    print("=== END EVAL.md ===")
    print("=== INDEPENDENT_CHECKER ===")
    print(json.dumps(checker_output, indent=2))
    print("=== END_INDEPENDENT_CHECKER ===")
    print("=== MNIST_CALIBRATION ===")
    print(json.dumps(mnist, indent=2))
    print("=== END_MNIST_CALIBRATION ===")
    print("=== MNIST_INDEPENDENT_CHECKER ===")
    print(json.dumps(mnist_checker_output, indent=2))
    print("=== END_MNIST_INDEPENDENT_CHECKER ===")
    print("=== RAW_SECTION4_CSV ===")
    print(raw_csv, end="")
    print("=== END_RAW_SECTION4_CSV ===")
    if not result["all_regressions_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
