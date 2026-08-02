# Current verification

![Claims 1–5 verified; Claim 6 blocked](https://huggingface.co/spaces/DineshAI/okzQ1x71pS/resolve/main/reports/full-reproduction/images/headline.svg)

Canonical evaluator entrypoint for arXiv 2410.08125. Code at Git SHA `75d1f2c6c76c2c642ba59319a097a79a4f5e504d` supersedes the **Historical rejected baseline** at judged Space revision `a1e96bb5ea2a3bc5106352c8ac10194358c04c57`.

Fixed command: `uv sync --frozen --no-dev && .venv/bin/python -m repro.run`

Winning run `cbb3de08-48e9-48a0-87c9-5ffb65d6e9cb`: HF `cpu-upgrade`; 8 declared/cgroup vCPUs; worker cap 8; 64 host-visible CPUs; no GPU; scientific runtime 2287.088s; job runtime 39m00s; estimated scientific cost $0.01906. Seeds are inline in each application JSON.

| Claim | Exact tested statement | Result | Headline evidence |
| --- | --- | --- | --- |
| 1 | Lemma 3 identity for absolutely continuous, possibly nondifferentiable densities | **VERIFIED** | Laplace/Triangular errors 0; wrong-score error 0.053694 |
| 2 | Theorem 7 location and scale-matrix gradients | **VERIFIED** | errors 9.95e-12 and 1.53e-11 |
| 3 | Theorem 8 output-covariance derivatives | **VERIFIED** | errors 2.37e-11 and 5.20e-10 |
| 4 | Six-distribution Section 4 benchmark over all feasible cells | **VERIFIED** | 447/447 cells; official Warcraft data; checker passes |
| 5 | Paper-target Cartesian RQMC + LOO, with triangular feasibility exception | **VERIFIED** | within 1% of minimum in 12/12 cases |
| 6 | All four MNIST, Warcraft, rendering, and TEM demonstrations | **BLOCKED** | four routes complete; no valid falsification |

- [Claims 1–3: contract, assumptions, code, raw data](#/current-claims-1-3)
- [Claims 4–5: benchmark, ranking, raw CSV, checker](#/current-claims-4-5)
- [Claim 6: four routes, limitations, raw JSON](#/current-claim-6)
- [Evaluator visibility matrix](#/current-visibility)
- [Release forecast](#/current-release)
- [Visual report](https://huggingface.co/spaces/DineshAI/okzQ1x71pS/blob/main/reports/full-reproduction/report.md)
- [Marimo notebook](https://huggingface.co/spaces/DineshAI/okzQ1x71pS/blob/main/notebooks/reproduction.py)
- [Raw cumulative JSON](https://huggingface.co/spaces/DineshAI/okzQ1x71pS/blob/main/evidence/run_cbb3de08/cumulative_result.json)

Every current verifier exits nonzero on failed evidence. The cumulative run records `all_regressions_passed: true`.
