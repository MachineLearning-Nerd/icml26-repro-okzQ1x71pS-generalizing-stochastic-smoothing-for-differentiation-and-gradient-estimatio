# Claims 4–5 limitations and deviations

- The paper does not release its exact sorting inputs, repeat counts, or variance-study code. Deterministic sorting inputs are used, so absolute sorting errors are not compared to paper tables. Shortest paths use the official Warcraft dataset rather than synthetic inputs.
- Shortest path is evaluated on exponentiated perturbed log-costs. This makes all 8-neighborhood edge costs positive for every distribution, including unbounded Cauchy noise.
- Cartesian antithetic sampling is included only for `n=3`, matching the paper's feasibility table. Gumbel is asymmetric and has no antithetic cells.
- The benchmark is full scale in disclosed dimensions, distributions, sample counts, and method combinations; it is an independent reconstruction rather than an execution of unavailable author code.
- Four independently scrambled path-oracle blocks quantify uncertainty. This is stricter than the paper, which reports no repeat count or oracle uncertainty; failure of the calibrated threshold leaves the claim BLOCKED.
- One deterministic representative training map per grid size is used across all path estimators. This tests every disclosed method cell without claiming coverage of every Warcraft map.
