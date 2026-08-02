from __future__ import annotations

import csv
import json
from pathlib import Path
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "run_cbb3de08"


def load_json(path: Path):
    return json.loads(path.read_text())


def main():
    required = [
        "README.md",
        "logbook.json",
        "pages/index.md",
        "pages/current/page.md",
        "pages/current/claims-1-3.md",
        "pages/current/claims-4-5.md",
        "pages/current/claim-6.md",
        "pages/current/visibility.md",
        "pages/current/release.md",
        "reports/full-reproduction/report.md",
        "notebooks/reproduction.py",
        "evidence/run_cbb3de08/cumulative_result.json",
        "evidence/run_cbb3de08/section4_raw.csv",
    ]
    checks = {f"exists:{path}": (ROOT / path).is_file() for path in required}

    cumulative = load_json(EVIDENCE / "cumulative_result.json")
    checks["cumulative_regressions_pass"] = cumulative["all_regressions_passed"] is True
    checks["exact_verdicts"] = [cumulative["claims"][str(i)]["verdict"] for i in range(1, 7)] == [
        "VERIFIED",
        "VERIFIED",
        "VERIFIED",
        "VERIFIED",
        "VERIFIED",
        "BLOCKED",
    ]

    checker_names = ["section4", "mnist", "warcraft", "rendering", "tem"]
    for name in checker_names:
        output = load_json(EVIDENCE / f"{name}_checker.json")
        checks[f"checker:{name}"] = output["passed"] is True and all(output["checks"].values())

    with (EVIDENCE / "section4_raw.csv").open(newline="") as source:
        rows = list(csv.DictReader(source))
    checks["section4_has_447_rows"] = len(rows) == 447

    svgs = sorted((ROOT / "reports" / "full-reproduction" / "images").glob("*.svg"))
    checks["six_evidence_figures"] = len(svgs) == 6
    for svg in svgs:
        try:
            ElementTree.parse(svg)
            checks[f"valid_svg:{svg.name}"] = True
        except ElementTree.ParseError:
            checks[f"valid_svg:{svg.name}"] = False

    logbook = load_json(ROOT / "logbook.json")
    children = logbook["root"]["children"]
    checks["current_navigation_first"] = children[0]["slug"] == "current"
    checks["historical_verifier_labeled"] = any(
        child["slug"] == "verification-run" and "Historical rejected baseline" in child["title"]
        for child in children
    )

    visibility = (ROOT / "pages" / "current" / "visibility.md").read_text()
    checks["six_visibility_rows"] = sum(line.startswith("| ") and line.split("|")[1].strip().isdigit() for line in visibility.splitlines()) == 6
    checks["visibility_has_no_missing_marker"] = "| No |" not in visibility and "MISSING" not in visibility.upper()

    manifest_lines = (ROOT / ".openresearch" / "protected" / "judged_space_manifest.sha256").read_text().splitlines()
    checks["protected_manifest_has_17_files"] = len(manifest_lines) == 17
    checks["protected_verifier_hash_corrected"] = any(
        line == "11c2b8c23021317059dd3750509ae55dfb00566705b7304ee3c5e326563bfe1b  pages/verification-run/page.md"
        for line in manifest_lines
    )

    text_paths = [ROOT / path for path in required if (ROOT / path).suffix in {".md", ".json", ".py"}]
    forbidden = ["HF_TOKEN=", "HUGGING_FACE_HUB_TOKEN=", "api_key=", "BEGIN PRIVATE KEY"]
    checks["no_literal_secret_assignments"] = not any(
        marker in path.read_text(errors="replace") for path in text_paths for marker in forbidden
    )

    passed = all(checks.values())
    print(json.dumps({"checks": checks, "passed": passed}, indent=2))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
