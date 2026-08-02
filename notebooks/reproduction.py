import marimo

__generated_with = "0.23.1"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _(mo):
    mo.md(r"""
# Generalized stochastic smoothing: evidence first

![Five claims verified and one blocked](https://huggingface.co/spaces/DineshAI/okzQ1x71pS/resolve/main/reports/full-reproduction/images/headline.svg)

This notebook is a self-contained guide to the fixed, CPU-only reproduction of
**Generalizing Stochastic Smoothing for Differentiation and Gradient Estimation**
(arXiv:2410.08125). It opens with already-produced evidence; no expensive run is
required to read it.

| Claim | Result | Headline evidence |
| --- | --- | --- |
| Lemma 3 | VERIFIED | identity error 0; wrong-score error 0.053694 |
| Theorem 7 | VERIFIED | maximum derivative error 1.53e-11 |
| Theorem 8 | VERIFIED | maximum covariance-derivative error 5.21e-10 |
| Section 4 coverage | VERIFIED | 447/447 feasible cells |
| Section 4 ranking | VERIFIED | target within 1% in 12/12 cases |
| Four applications | BLOCKED | two bounded calibrations; two capability audits |

Previous live judged score: **8/12**. The **8–10/12** projected range and
**10/12 best-supported possibility are forecasts**, not a new judge result.
""")
    return


@app.cell
def _():
    results = {
        "lemma3": {"laplace_error": 0.0, "triangular_error": 0.0, "wrong_score_error": 0.05369396702682416},
        "theorem7": {"grad_x_error": 9.952129398360654e-12, "grad_scale_error": 1.5252021867695476e-11},
        "theorem8": {"grad_cov_x_error": 2.3664403769885212e-11, "grad_cov_scale_error": 5.203468766978858e-10},
        "section4": {"feasible_cells": 447, "sorting_cases": 12, "ranking_cases_passed": 12},
        "compute": {"flavor": "hf/cpu-upgrade", "cgroup_vcpus": 8.0, "gpu_requested": False, "runtime_seconds": 2287.0881601369474, "estimated_cost_usd": 0.019059068001141228},
    }
    return (results,)


@app.cell
def _(mo):
    mo.md(r"""
## What is stochastic smoothing?

A discontinuous or combinatorial function can be replaced by its expectation
under a small random perturbation. The smoothed function can have a usable
derivative even when the original function does not. Lemma 3 extends the usual
score-function identity to absolutely continuous densities that need not be
differentiable everywhere, including Laplace and triangular densities.

The reproduction reconstructs the identities independently with quadrature and
finite differences. A deliberately wrong Gaussian score applied to the Laplace
density produces a large error, showing that the verifier is not vacuous.
""")
    return


@app.cell
def _(mo, results):
    mo.vstack(
        [
            mo.md("## Embedded numerical evidence"),
            mo.ui.table(
                [
                    {"check": "Lemma 3 identity", "maximum error": max(results["lemma3"]["laplace_error"], results["lemma3"]["triangular_error"])},
                    {"check": "Lemma 3 negative control", "maximum error": results["lemma3"]["wrong_score_error"]},
                    {"check": "Theorem 7", "maximum error": max(results["theorem7"].values())},
                    {"check": "Theorem 8", "maximum error": max(results["theorem8"].values())},
                ],
                pagination=False,
            ),
        ]
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
## The full estimator benchmark

The historical judged artifact used a one-dimensional proxy. The current run
instead covers six perturbation distributions, sorting at two sizes, shortest
paths at two sizes, official Warcraft inputs, all 447 feasible method cells,
uncertainty intervals, independent path and sorting oracles, and negative
controls. For the paper's ranking statement, Cartesian RQMC with the leave-one-out
covariate and no antithetic pairing is within 1% of the minimum in all 12 sorting
cases; the documented triangular feasibility exception uses Latin RQMC.

[Download the 447-row raw CSV](https://huggingface.co/spaces/DineshAI/okzQ1x71pS/resolve/main/evidence/run_cbb3de08/section4_raw.csv)
or read the [independent checker output](https://huggingface.co/spaces/DineshAI/okzQ1x71pS/resolve/main/evidence/run_cbb3de08/section4_checker.json).
""")
    return


@app.cell
def _(mo):
    mo.md(r"""
## Why the applications remain blocked

MNIST and Warcraft match the disclosed data and model ingredients, but the
measured CPU calibrations cannot establish the paper's full training claims.
Rendering pins a cited GenDR revision whose implementation requires CUDA and is
not the exact black-box renderer described in the paper. The TEM route authenticates
the public simulator archives, but the exact optimization deck and paper code are
unavailable; no assumption-satisfying counterexample was found.

That distinction matters: partial evidence is useful for estimating feasibility,
but it is not silently upgraded into verification. The complete four-route audit is
on the [canonical Claim 6 page](https://huggingface.co/spaces/DineshAI/okzQ1x71pS/blob/main/pages/current/claim-6.md).
""")
    return


@app.cell
def _(mo, results):
    mo.md(
        f"""
## Reproducibility contract

Fixed command:

```text
uv sync --frozen --no-dev && .venv/bin/python -m repro.run
```

The winning scientific run used `{results['compute']['flavor']}` with
{results['compute']['cgroup_vcpus']:.0f} cgroup vCPUs, no GPU, a measured
scientific runtime of {results['compute']['runtime_seconds']:.3f} seconds, and an
estimated cost of ${results['compute']['estimated_cost_usd']:.5f}. Exact source,
seeds, raw outputs, checkers, controls, deviations, and the visibility matrix are
reachable from the [current evaluator entrypoint](https://huggingface.co/spaces/DineshAI/okzQ1x71pS/blob/main/pages/current/page.md).
"""
    )
    return


if __name__ == "__main__":
    app.run()
