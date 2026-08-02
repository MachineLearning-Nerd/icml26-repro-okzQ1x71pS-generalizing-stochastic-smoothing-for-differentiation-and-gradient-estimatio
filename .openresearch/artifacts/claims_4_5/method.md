# Claims 4–5 method

`repro/section4.py` independently reconstructs the two paper operators and every disclosed feasible method combination.

Sorting uses 24 deterministic repetitions. Its oracle is independent of the score estimator: one-dimensional adaptive quadrature computes every expected permutation-matrix entry, then centered finite differences at two step sizes compute and cross-check the gradient.

Shortest paths use Dijkstra's algorithm on the complete 8-neighborhood. Positive costs are obtained from perturbed log-costs, so the black box is defined for every real perturbation. Each oracle averages two independent scrambled-Sobol estimates of 16,384 samples; their disagreement is audited. The benchmark uses 12 repetitions of 1,024 samples per feasible cell. Confidence intervals use Student's t distribution.

The negative control applies a Gaussian score to Laplace samples. It must be at least 1.25 times worse than the correct score. Sixteen paths at each grid size are independently checked for binary values, endpoints, and 8-neighborhood connectivity.

The fixed command remains `uv sync --frozen --no-dev && .venv/bin/python -m repro.run`. The run writes JSON and CSV, prints both to the OpenResearch log, and exits nonzero on any failed contract cell.
