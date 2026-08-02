# Claims 4–5 limitations and deviations

- The paper does not release exact variance-study inputs, repeat counts, or code. Deterministic, fully specified inputs are used instead, so absolute errors are not compared to paper tables.
- Shortest path is evaluated on exponentiated perturbed log-costs. This makes all 8-neighborhood edge costs positive for every distribution, including unbounded Cauchy noise.
- Cartesian antithetic sampling is included only for `n=3`, matching the paper's feasibility table. Gumbel is asymmetric and has no antithetic cells.
- The benchmark is full scale in disclosed dimensions, distributions, sample counts, and method combinations; it is an independent reconstruction rather than an execution of unavailable author code.
- Four independently scrambled path-oracle blocks quantify uncertainty. This is stricter than the paper, which reports no repeat count or oracle uncertainty; failure of the calibrated threshold leaves the claim BLOCKED.
