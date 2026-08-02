# Final release report

- Previous live judged score: `8/12`
- Conservative projected score range after the proposed change: `8–10/12`
- Best-supported possible new score: `10/12` — **forecast, not a judge result**

| Claim | Current points | Possible points | Confidence | Evidence status | Basis and remaining risk |
| --- | ---: | ---: | --- | --- | --- |
| 1 | 2 | 2 | HIGH | VERIFIED | Direct identity and wrong-score control; finite calibration is not universal proof |
| 2 | 2 | 2 | HIGH | VERIFIED | Independent finite differences at machine precision |
| 3 | 2 | 2 | HIGH | VERIFIED | Independent covariance finite differences at ≤5.21e-10 |
| 4 | 1 | 2 | HIGH | VERIFIED | 447 faithful cells, official data, independent oracles, raw CSV; evaluator interpretation risk remains |
| 5 | 1 | 2 | HIGH | VERIFIED | Target within 1% in 12/12 cases; evaluator interpretation risk remains |
| 6 | 0 | 0 | LOW | BLOCKED | Four distinct routes complete; exact full applications and a valid counterexample remain unavailable |

Current total score: `8/12`. Conservative projected total: `8–10/12`. Best-supported possible total: `10/12`, forecast only. Claims 4–5 changed from toy to faithful VERIFIED evidence. Claim 6 changed from unattempted to rigorously BLOCKED after three verification routes and one mandatory falsification route.

## Baseline and heads

- Baseline repository SHA requested: `a569320ddadea61fe3c33b7aaa5cb44cd8c1fe36`
- Baseline experiment commit: `4485794`
- Judged HF Head: `a1e96bb5ea2a3bc5106352c8ac10194358c04c57`
- Judge Head: `a1e96bb5ea2a3bc5106352c8ac10194358c04c57`
- Winning scientific branch/SHA: `orx/tem-primary-source-falsification-and-cumulative` / `75d1f2c6c76c2c642ba59319a097a79a4f5e504d`
- Passing evaluator candidate branch/SHA: `orx/repair-publication-gate-and-red-team-candidate` / `f2a974d677660fa7168072c3c710ccf15bdc9efa`
- Final release input: `orx/final-evaluator-blind-release-regression` at its published branch tip

## Experiment tree and compute

The tree descends from the fixed baseline through a small Section 4 bush, promotes the calibrated 447-cell winner, then stacks MNIST, Warcraft, rendering, TEM, and evaluator-product decisions. Every child inherits the same command:

```text
uv sync --frozen --no-dev && .venv/bin/python -m repro.run
```

All 18 completed campaign jobs used HF `cpu-upgrade`; no GPU was requested. Through the passing evaluator candidate they consumed 40,512 job-seconds (11.253h), an estimated `$0.3376` at `$0.03/hour`. The final regression is reported separately after it terminates. The scientific winner used 2,287.088s (`$0.01906`); the passing publication-gate run used 2,611.389s (`$0.02176`) and 44m16s job time. Both recorded 8 declared/cgroup vCPUs, worker limit 8, and no GPU.

Key run ledger (all invoked with the exact fixed command above):

| Run | Status | Purpose | Job runtime |
| --- | --- | --- | ---: |
| `abd54655` | done | judged baseline | 26s |
| `dac6c903` | failed | first faithful Section 4 route | 13m35s |
| `5c881a1d` | failed | Cartesian RQMC/oracle route | 42m46s |
| `f9ed697d` | done | calibrated Section 4 winner | 43m30s |
| `8c5fd1e1` | done | MNIST calibration | 1h14m |
| `a53fa2d7` | failed | Warcraft calibration repair lineage | 1h40m |
| `c9293803` | failed | rendering plus cumulative historical rejected verifier | 44m40s |
| `cbb3de08` | done | TEM falsification plus scientific cumulative winner | 39m00s |
| `aa51605b` | failed | first evaluator product; packaging gate caught defects | 35m37s |
| `174c64f5` | done | repaired evaluator product and release gate | 44m16s |

The complete run ledger remains in OpenResearch. Failed runs are retained as lineage evidence and are never presented as current verification.

## Evidence

- Canonical pages: `pages/current/`
- Scientific raw data: `evidence/run_cbb3de08/`
- Passing publication-gate output: `evidence/run_174c64f5/`
- Durable contracts and limitations: `.openresearch/artifacts/`
- Visual report and six figures: `reports/full-reproduction/`
- Tutorial notebook: `notebooks/reproduction.py`
- Evaluator traversal: `release/red_team_1.md`, `release/red_team_2.md`
- Visibility matrix: `release/visibility_matrix.md`
- Historical subset proof: `release/subset_check.json`
- Exact text operations: `release/upload_allowlist.txt`
- File hashes: `release/upload_manifest.sha256`

## Claim result summary

Claims 1–3 remain VERIFIED in the cumulative regression. Claims 4–5 are VERIFIED over the reconstructed full benchmark contract. Claim 6 remains BLOCKED because bounded CPU calibrations cannot verify the exact full application demonstrations, the cited renderer is CUDA-only and not the exact paper implementation, and the TEM public package lacks the exact protocol; the mandatory falsification route found no assumption-satisfying counterexample.

## Commands and publication action

Startup and orchestration commands used: `orx skill`, the four named `orx skill <name>` guides, `orx projects --json`, `orx project view`, `orx runs`, `orx exp status`, `orx create-experiment`, `orx exp run`, `orx exp wait`, `orx logs`, `orx exp desc`, `git fetch`, `git checkout`, `git status --short`, `git rev-parse`, `git diff --check`, `git commit`, `git push`, `git ls-remote`, `hf download`, `uv lock --upgrade-package marimo`, and SHA-256/subset/traversal inspections. Repeated wait/status/log calls differed only by run ID and bounded monitoring window. Every research run used:

```text
orx exp run <experiment-id> --flavor cpu-upgrade --timeout 14400 --image ghcr.io/astral-sh/uv:python3.12-bookworm-slim
```

Exact publication action after the final regression passes: submit only the 92 newline-delimited paths in `release/upload_allowlist.txt` as text additions/updates in one Hugging Face `create_commit` API call to the existing Space `DineshAI/okzQ1x71pS`; do not delete any path and do not create another Space. Then download that exact revision, verify hashes/traversal, mark awaiting judge, and fast-forward the same text commit lineage to GitHub `main`.
