# Source audit

- Primary source: https://ar5iv.labs.arxiv.org/html/2410.08125
- Retrieval: 2026-08-02, explicit User-Agent `OpenResearch-Reproduction/1.0 (paper audit; contact via repository)`
- HTML SHA-256: `053740ba5182819585699124d6672d9772e91b5d080cb3b047d74f7dd54dc8fd`
- arXiv source archive: https://export.arxiv.org/e-print/2410.08125
- Source archive SHA-256: `3412645ed7d51a75388b91252a3c2dfd74781806e5b73b0f97a944f0d95430bb`

Anchors and quantifiers:

- Claim 1: `#Thmtheorem3`, Section 2, source label `cor:continuous-dae`. The density is absolutely continuous, not necessarily differentiable; the result is stated everywhere, with the undefined score removed on a zero-measure set.
- Claim 2: `#Thmtheorem7`, Section 2, source label `thm:multivar`. The scale matrix is invertible and the multivariate density is absolutely continuous on R^n.
- Claim 3: `#Thmtheorem8`, Section 2, source label `thm:output-covar`. Both input and scale-matrix derivatives of the output covariance are stated under Theorem 7's assumptions.
- Claims 4-5: `#S4.SS1`, Section 4.1. The actual functions are hard permutation matrices and 8-neighborhood shortest-path maps; six distributions, all combinations of three variance-reduction axes, 1,024 samples (1,000 for Cartesian n=3), sorting sizes n=3 and n=5, and shortest-path sizes 8x8 and 12x12. The paper's conclusion is Cartesian RQMC + LOO + no antithetic when Cartesian sampling is feasible.
- Claim 6: `#S4.SS2` through `#S4.SS5`, Sections 4.2-4.5. The applications are 4-digit MNIST sorting at n=5, Warcraft 12x12 shortest paths, Utah-teapot 4-DoF pose recovery, and TEM simulation optimization with 2 and 4 parameters.

The judged Space paraphrase omitted important application and benchmark details. Those details govern all child contracts.
