# Claims 4–5 — full Section 4 benchmark

Status: **VERIFIED**.

Contract: Gaussian, Logistic, Gumbel, Cauchy, Laplace, Triangular; sorting `n=3,5`; 8-neighborhood paths `8x8,12x12`; 1,000/1,024 samples; all feasible MC, antithetic MC, Cartesian/Latin QMC/RQMC, covariate, and pairing cells. The raw CSV has exactly 447 rows.

Official Warcraft maps are MD5-verified. Sorting uses quadrature/finite-difference oracles. Paths use held-out perturbations, path validity, calibrated scrambled blocks (262,144 samples per distribution/grid; 2,097,152 for Triangular), confidence intervals, and non-vacuity checks.

Claim 5 criterion: the paper target is within 1% of its cell minimum. Result: 12/12 cases. Target is Cartesian RQMC + LOO without antithetic pairing for five distributions, with the paper's feasible Latin-QMC + LOO target for Triangular.

Negative control: wrong Gaussian-for-Laplace score increases error `0.09017→0.51723` (`5.736x`).

- Code: [`section4.py`](https://huggingface.co/spaces/DineshAI/okzQ1x71pS/blob/main/repro/section4.py), [`check_section4.py`](https://huggingface.co/spaces/DineshAI/okzQ1x71pS/blob/main/repro/check_section4.py)
- Raw CSV: [`section4_raw.csv`](https://huggingface.co/spaces/DineshAI/okzQ1x71pS/blob/main/evidence/run_cbb3de08/section4_raw.csv)
- Checker: [`section4_checker.json`](https://huggingface.co/spaces/DineshAI/okzQ1x71pS/blob/main/evidence/run_cbb3de08/section4_checker.json)
- Contract/source/method/limitations and rejected pages: [`.openresearch/artifacts/claims_4_5`](https://huggingface.co/spaces/DineshAI/okzQ1x71pS/tree/main/.openresearch/artifacts/claims_4_5)

Deviation: independent reconstruction from the paper and official data, not unreleased author code. Thresholds and feasibility exceptions are explicit.
