# Claims 4–5 method

`repro/section4.py` independently reconstructs the two paper operators and every disclosed feasible method combination.

Sorting uses 64 deterministic-seed repetitions. Its oracle is independent of the score estimator: one-dimensional adaptive quadrature computes every expected permutation-matrix entry, then centered finite differences at two step sizes compute and cross-check the gradient. Cartesian RQMC independently samples one point inside every Cartesian cell, exactly as Section 3 defines it; the rejected tensor-product-jitter implementation is preserved only on its frozen parent branch.

Shortest paths use Dijkstra's algorithm on the complete 8-neighborhood. Positive costs are obtained from perturbed log-costs, so the black box is defined for every real perturbation. Each oracle averages four independent scrambled-Sobol blocks of 65,536 samples, or 262,144 samples per distribution and grid size. A vector-valued Student-t 95% uncertainty radius must be below 20% of the smallest evaluated estimator error in the same case. The benchmark uses 24 repetitions of 1,024 samples per feasible cell. Confidence intervals use Student's t distribution.

The negative control applies a Gaussian score to Laplace samples. It must be at least 1.25 times worse than the correct score. Sixteen paths at each grid size are independently checked for binary values, endpoints, and 8-neighborhood connectivity.

The fixed command remains `uv sync --frozen --no-dev && .venv/bin/python -m repro.run`. The run writes JSON and CSV, prints both to the OpenResearch log, invokes `repro/check_section4.py` as a separate raw-file checker, and exits nonzero on any failed contract cell.
