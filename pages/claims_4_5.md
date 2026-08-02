# Claims 4–5 — Section 4 operator benchmark

Current status: **BLOCKED**, pending the corrective HF run.

The current verifier is `repro/section4.py`, superseding both the judged 1D proxy and a **Historical rejected baseline** that used the wrong Cartesian randomization. It covers six distributions, hard sorting at `n=3,5`, 8-neighborhood paths at `8x8,12x12`, 1,000/1,024 samples, and all 447 feasible sampling/covariate/antithetic cells.

The verifier uses exact quadrature/finite-difference sorting oracles, independently jittered Cartesian cells, four independently scrambled Sobol path-oracle blocks totaling 262,144 samples per distribution/grid, confidence intervals, path-validity checks, a wrong-score negative control, and a separate raw-file checker. The fixed command will print the complete raw CSV between `RAW_SECTION4_CSV` markers and exit nonzero when the contract fails.

Exact source quantifiers, acceptance thresholds, deviations, and method are under `.openresearch/artifacts/claims_4_5/`.

The frozen parent run is preserved under `.openresearch/artifacts/claims_4_5/HISTORICAL_REJECTED_BASELINE.md`; it is evidence of a rejected route, not the current result.
