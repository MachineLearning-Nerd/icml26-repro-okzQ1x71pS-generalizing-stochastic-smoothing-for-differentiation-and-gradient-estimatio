from __future__ import annotations

import csv
import io
import json
import platform
import subprocess
import sys
import time
from pathlib import Path

from .mnist_application import run_mnist_calibration
from .numerics import baseline_variance_proxy, lemma3_check, theorem7_check, theorem8_check
from .rendering_application import run_rendering_capability_audit
from .resources import CPU_UPGRADE_USD_PER_HOUR, cpu_allocation
from .section4 import run_section4
from .tem_application import run_tem_falsification_audit
from .warcraft_application import run_warcraft_calibration


def git_sha():
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], check=True, capture_output=True, text=True
    ).stdout.strip()


def main():
    started = time.perf_counter()
    print("STAGE claims_1_3", flush=True)
    claim1 = lemma3_check()
    claim2 = theorem7_check()
    claim3 = theorem8_check()
    variance_proxy = baseline_variance_proxy()
    print("STAGE section_4", flush=True)
    section4 = run_section4()
    section4_rows = section4.pop("rows")
    print("STAGE mnist_calibration", flush=True)
    mnist = run_mnist_calibration()
    print("STAGE warcraft_calibration", flush=True)
    warcraft = run_warcraft_calibration()
    print("STAGE rendering_capability_audit", flush=True)
    rendering = run_rendering_capability_audit()
    print("STAGE tem_falsification_audit", flush=True)
    tem = run_tem_falsification_audit()
    print("STAGE independent_checkers", flush=True)

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
    warcraft_directory = Path(".openresearch/artifacts/claim_6/warcraft_calibration")
    warcraft_directory.mkdir(parents=True, exist_ok=True)
    warcraft_result_path = warcraft_directory / "result.json"
    warcraft_result_path.write_text(json.dumps(warcraft, indent=2) + "\n")
    warcraft_checker = subprocess.run(
        [sys.executable, "-m", "repro.check_warcraft", str(warcraft_result_path)],
        capture_output=True,
        text=True,
    )
    warcraft_checker_output = (
        json.loads(warcraft_checker.stdout)
        if warcraft_checker.stdout.strip()
        else {"passed": False, "stderr": warcraft_checker.stderr}
    )
    rendering_directory = Path(".openresearch/artifacts/claim_6/rendering_capability")
    rendering_directory.mkdir(parents=True, exist_ok=True)
    rendering_result_path = rendering_directory / "result.json"
    rendering_result_path.write_text(json.dumps(rendering, indent=2) + "\n")
    rendering_checker = subprocess.run(
        [sys.executable, "-m", "repro.check_rendering", str(rendering_result_path)],
        capture_output=True,
        text=True,
    )
    rendering_checker_output = (
        json.loads(rendering_checker.stdout)
        if rendering_checker.stdout.strip()
        else {"passed": False, "stderr": rendering_checker.stderr}
    )
    tem_directory = Path(".openresearch/artifacts/claim_6/tem_falsification")
    tem_directory.mkdir(parents=True, exist_ok=True)
    tem_result_path = tem_directory / "result.json"
    tem_result_path.write_text(json.dumps(tem, indent=2) + "\n")
    tem_checker = subprocess.run(
        [sys.executable, "-m", "repro.check_tem", str(tem_result_path)],
        capture_output=True,
        text=True,
    )
    tem_checker_output = (
        json.loads(tem_checker.stdout)
        if tem_checker.stdout.strip()
        else {"passed": False, "stderr": tem_checker.stderr}
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
        "warcraft_calibration_independent_checker": warcraft_checker.returncode == 0,
        "rendering_capability_independent_checker": rendering_checker.returncode == 0,
        "tem_falsification_independent_checker": tem_checker.returncode == 0,
    }
    checks = {name: bool(passed) for name, passed in checks.items()}
    elapsed = time.perf_counter() - started
    resources = cpu_allocation(required_cores=32)
    result = {
        "paper": "arXiv:2410.08125",
        "git_sha": git_sha(),
        "fixed_command": "uv sync --frozen --no-dev && .venv/bin/python -m repro.run",
        "environment": {
            **resources,
            "python": platform.python_version(),
            "platform": platform.platform(),
            "runtime_seconds": elapsed,
            "estimated_cost_usd": elapsed / 3600.0 * CPU_UPGRADE_USD_PER_HOUR,
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
                "reason": "Four distinct routes are complete, but MNIST and Warcraft remain bounded calibrations, the cited renderer is CUDA-only and not the paper implementation, and the TEM route found no valid counterexample or complete protocol.",
                "mnist_calibration": mnist,
                "warcraft_calibration": warcraft,
                "rendering_capability_audit": rendering,
                "tem_falsification_audit": tem,
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
        "warcraft_independent_checker": warcraft_checker_output,
        "rendering_independent_checker": rendering_checker_output,
        "tem_independent_checker": tem_checker_output,
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
    print("=== WARCRAFT_CALIBRATION ===")
    print(json.dumps(warcraft, indent=2))
    print("=== END_WARCRAFT_CALIBRATION ===")
    print("=== WARCRAFT_INDEPENDENT_CHECKER ===")
    print(json.dumps(warcraft_checker_output, indent=2))
    print("=== END_WARCRAFT_INDEPENDENT_CHECKER ===")
    print("=== RENDERING_CAPABILITY_AUDIT ===")
    print(json.dumps(rendering, indent=2))
    print("=== END_RENDERING_CAPABILITY_AUDIT ===")
    print("=== RENDERING_INDEPENDENT_CHECKER ===")
    print(json.dumps(rendering_checker_output, indent=2))
    print("=== END_RENDERING_INDEPENDENT_CHECKER ===")
    print("=== TEM_FALSIFICATION_AUDIT ===")
    print(json.dumps(tem, indent=2))
    print("=== END_TEM_FALSIFICATION_AUDIT ===")
    print("=== TEM_INDEPENDENT_CHECKER ===")
    print(json.dumps(tem_checker_output, indent=2))
    print("=== END_TEM_INDEPENDENT_CHECKER ===")
    print("=== RAW_SECTION4_CSV ===")
    print(raw_csv, end="")
    print("=== END_RAW_SECTION4_CSV ===")
    if not result["all_regressions_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
