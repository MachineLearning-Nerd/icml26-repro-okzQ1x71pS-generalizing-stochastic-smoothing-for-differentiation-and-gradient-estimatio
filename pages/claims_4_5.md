# Claims 4–5 — Section 4 operator benchmark

Status before the first HF run: **BLOCKED**.

The current verifier is `repro/section4.py`, superseding the judged 1D proxy. It covers six distributions, hard sorting at `n=3,5`, 8-neighborhood paths at `8x8,12x12`, 1,000/1,024 samples, and all 447 feasible sampling/covariate/antithetic cells.

The verifier uses exact quadrature/finite-difference sorting oracles, independently scrambled Sobol path oracles, confidence intervals, path-validity checks, and a wrong-score negative control. The fixed command will print the complete raw CSV between `RAW_SECTION4_CSV` markers and exit nonzero when the contract fails.

Exact source quantifiers, acceptance thresholds, deviations, and method are under `.openresearch/artifacts/claims_4_5/`.
