# Claim 1 — nonsmooth perturbation densities

Status: **VERIFIED**.

Lemma 3 permits absolutely continuous perturbation densities that need not have differentiable densities, subject to its finiteness and almost-everywhere score assumptions. The current verifier tests `f(x)=|x|` at `x=0.37` with unit Laplace and symmetric triangular noise.

| Check | Result | Contract |
|---|---:|---:|
| Laplace identity error | 0.0 | ≤ 1e-8 |
| Triangular identity error | 0.0 | ≤ 1e-8 |
| Wrong Gaussian score | 0.0536939670 | > 0.04 |

Run: `abd54655-bcdb-47e8-99aa-9faeb6692588`; Git SHA: `448579491ffe35e7b113204da313cdcbc7405da0`; command: `uv sync --frozen --no-dev && .venv/bin/python -m repro.run`; HF `cpu-upgrade`; 64 logical CPUs; no GPU; verifier time 0.284 s.

Code: `repro/numerics.py` and `repro/run.py`. Raw output, the exact contract, independent checker, and negative control are under `.openresearch/artifacts/claim_1/`.
