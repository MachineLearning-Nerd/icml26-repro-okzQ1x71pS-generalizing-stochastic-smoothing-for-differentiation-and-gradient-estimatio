# Claims 4–5 method

`repro/section4.py` independently reconstructs the two paper operators and every disclosed feasible method combination.

Sorting uses 64 deterministic-seed repetitions. Its oracle is independent of the score estimator: one-dimensional adaptive quadrature computes every expected permutation-matrix entry, then centered finite differences at two step sizes compute and cross-check the gradient. Cartesian RQMC independently samples one point inside every Cartesian cell, exactly as Section 3 defines it; the rejected tensor-product-jitter implementation is preserved only on its frozen parent branch.

Shortest paths use the official Warcraft dataset (DOI `10.17617/3.YJCQ5S`, Dataverse file 102059). The 915,169,563-byte archive is downloaded only in the HF job and must match its published MD5 `acea5ea60a47664ff189923a84814e96`. The archive publishes native 12x12 weights but no 8x8 split, so the 8x8 case is the prespecified top-left crop of those official 12x12 weights. For each grid size, the selected training map is the one whose coefficient of variation is closest to the median among the first 256 maps; this deterministic input-only rule does not inspect estimator rankings.

The operator is Dijkstra's algorithm on the complete 8-neighborhood. Positive costs are obtained from perturbed log-costs, so the black box is defined for every real perturbation. For each distribution and size, a prespecified ten-point scale sweep uses 256 scrambled-Sobol perturbations and selects the scale closest to a 50% path-change rate. A disjoint 256-point validation seed must produce a 10–90% path-change rate. This prevents a constant-path benchmark without selecting scales from the estimator result.

The official-data pilot used four independent scrambled-Sobol blocks of 65,536 samples per distribution and grid size. That was sufficient for ten of twelve cases (uncertainty/error ratios 0.099--0.133), but the Triangular ratios were 0.316 at 8x8 and 0.530 at 12x12. This child retains four blocks for those ten resolved cases and prespecifies 32 independent blocks for each Triangular case. The fixed vector-valued Student-t 95% uncertainty-radius gate remains below 20% of the smallest evaluated estimator error; it was not relaxed after seeing the pilot. The benchmark uses 24 repetitions of 1,024 samples per feasible cell. Confidence intervals use Student's t distribution.

The negative control applies a Gaussian score to Laplace samples. It must be at least 1.25 times worse than the correct score. Sixteen paths for every distribution and grid size are independently checked for binary values, endpoints, and 8-neighborhood connectivity.

The fixed command remains `uv sync --frozen --no-dev && .venv/bin/python -m repro.run`. The run writes JSON and CSV, prints both to the OpenResearch log, invokes `repro/check_section4.py` as a separate raw-file checker, and exits nonzero on any failed contract cell.
