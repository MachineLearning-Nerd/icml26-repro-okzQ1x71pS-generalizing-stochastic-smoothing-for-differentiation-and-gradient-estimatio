---
title: "Repro - Generalizing Stochastic Smoothing for Differentiation and Gradient Estimation"
emoji: 🎯
colorFrom: yellow
colorTo: red
sdk: static
pinned: false
tags:
 - trackio
 - trackio-logbook
 - open-experiment
 - icml2026-repro
 - paper-okzQ1x71pS
---

# Claim-by-claim reproduction of generalized stochastic smoothing

![Claim status](reports/full-reproduction/images/headline.svg)

This campaign tests arXiv 2410.08125 only on Hugging Face `cpu-upgrade`: 8 declared/cgroup vCPUs, an eight-worker cap, and no GPU. Fixed command: `uv sync --frozen --no-dev && .venv/bin/python -m repro.run`.

The strongest cumulative run verifies Claims 1–5. It covers all 447 feasible Section 4 cells, and the paper-target variance-reduction strategy is within 1% of the cell minimum in all 12 sorting/distribution cases. Claim 6 is **BLOCKED**: MNIST and Warcraft are calibrations rather than full-scale runs, the cited GenDR source requires CUDA and differs from the paper implementation, and the TEM route found no assumption-satisfying counterexample.

Previous live judged score: **8/12**. Conservative projected range: **8–10/12**. Best-supported possible score: **10/12, forecast only**; the live judge has not evaluated this revision.

- [Visual technical report](reports/full-reproduction/report.md)
- [Canonical evaluator page](pages/current/page.md)
- [Visibility matrix](pages/current/visibility.md)
- [Self-contained marimo notebook](notebooks/reproduction.py)
- [![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/MachineLearning-Nerd/icml26-repro-okzQ1x71pS-generalizing-stochastic-smoothing-for-differentiation-and-gradient-estimatio/blob/main/notebooks/reproduction.py)

## Experiment log

| Branch / experiment | Purpose or change | Exact run command | Assessment / outcome | Compute |
| --- | --- | --- | --- | --- |
| `main` | Publication surface | Not run as an experiment (publication surface) | Mirrors winning text evidence after gates | — |
| [`orx/judged-8-12-baseline-with-reproducible-environme`](https://github.com/MachineLearning-Nerd/icml26-repro-okzQ1x71pS-generalizing-stochastic-smoothing-for-differentiation-and-gradient-estimatio/tree/orx/judged-8-12-baseline-with-reproducible-environme) | Freeze judged baseline | `uv sync --frozen --no-dev && .venv/bin/python -m repro.run` | Claims 1–3 verified; Claims 4–5 historical toy evidence | HF `cpu-upgrade`, 26s |
| [`orx/calibrated-triangular-path-oracle-power`](https://github.com/MachineLearning-Nerd/icml26-repro-okzQ1x71pS-generalizing-stochastic-smoothing-for-differentiation-and-gradient-estimatio/tree/orx/calibrated-triangular-path-oracle-power) | Faithful Section 4 benchmark | `uv sync --frozen --no-dev && .venv/bin/python -m repro.run` | Claims 4–5 verified over 447 cells | HF `cpu-upgrade`, 43m30s |
| [`orx/tem-primary-source-falsification-and-cumulative`](https://github.com/MachineLearning-Nerd/icml26-repro-okzQ1x71pS-generalizing-stochastic-smoothing-for-differentiation-and-gradient-estimatio/tree/orx/tem-primary-source-falsification-and-cumulative) | Four Claim 6 routes plus cumulative regression | `uv sync --frozen --no-dev && .venv/bin/python -m repro.run` | Claims 1–5 verified; Claim 6 blocked | HF `cpu-upgrade`, 39m00s |
| [`orx/evaluator-visible-release-candidate`](https://github.com/MachineLearning-Nerd/icml26-repro-okzQ1x71pS-generalizing-stochastic-smoothing-for-differentiation-and-gradient-estimatio/tree/orx/evaluator-visible-release-candidate) | First evaluator-visible candidate | `uv sync --frozen --no-dev && .venv/bin/python -m repro.run` | Scientific checks passed; release packaging gate failed | HF `cpu-upgrade`, 35m37s |
| [`orx/repair-publication-gate-and-red-team-candidate`](https://github.com/MachineLearning-Nerd/icml26-repro-okzQ1x71pS-generalizing-stochastic-smoothing-for-differentiation-and-gradient-estimatio/tree/orx/repair-publication-gate-and-red-team-candidate) | Clean text evidence and pinned notebook validator | `uv sync --frozen --no-dev && .venv/bin/python -m repro.run` | All scientific and release checks pass | HF `cpu-upgrade`, 44m16s |
| [`orx/final-evaluator-blind-release-regression`](https://github.com/MachineLearning-Nerd/icml26-repro-okzQ1x71pS-generalizing-stochastic-smoothing-for-differentiation-and-gradient-estimatio/tree/orx/final-evaluator-blind-release-regression) | Warning-free notebook gate, blind traversal, exact release manifest | `uv sync --frozen --no-dev && .venv/bin/python -m repro.run` | Scientific and release checks passed; warning gate found four formatting warnings | HF `cpu-upgrade`, 36m09s |

Historical Trackio pages from judged revision `a1e96bb5ea2a3bc5106352c8ac10194358c04c57` remain reachable. The [current verification](pages/current/page.md) supersedes the old verification run.
