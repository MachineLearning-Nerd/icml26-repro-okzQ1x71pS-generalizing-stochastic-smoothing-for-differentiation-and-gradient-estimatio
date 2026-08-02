# Claims 4–5 source audit

- Primary HTML: <https://ar5iv.labs.arxiv.org/html/2410.08125>, retrieved 2026-08-02 with explicit User-Agent; SHA-256 `053740ba5182819585699124d6672d9772e91b5d080cb3b047d74f7dd54dc8fd`.
- arXiv source archive: <https://export.arxiv.org/e-print/2410.08125>; SHA-256 `3412645ed7d51a75388b91252a3c2dfd74781806e5b73b0f97a944f0d95430bb`.
- Section 4.1 defines the operators as the hard permutation matrix and the binary 8-neighborhood shortest path.
- Figure 2 uses sorting sizes `n=3,5`; Figure 3 uses `8x8,12x12` path maps.
- Both figures use 1,024 samples, except Cartesian sorting at `n=3`, which uses `10^3=1,000`.
- The three axes are sampling strategy, covariate, and antithetic pairing. Tables 2–3 enumerate up to 24 feasible combinations per setting.
- The prose conclusion selects Cartesian RQMC + LOO + no antithetic whenever Cartesian sampling is feasible. The immediately preceding paragraph explicitly identifies triangular noise as an exception, selecting Latin QMC because boundary scores dominate.

The paper does not disclose the exact cost maps, sorting input vectors, repeat count, or implementation code. This reconstruction therefore cannot use absolute table values as an acceptance criterion; it tests the complete disclosed domain and the disclosed ranking pattern.
