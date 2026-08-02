# Claims 4–5 evaluation

Current status: **Claim 5 VERIFIED; Claim 4 BLOCKED pending the calibrated-power child run.**

The first full-domain run completed all 447 cells but was rejected because its Cartesian RQMC construction used tensor-product axis jitter and its path-oracle uncertainty check failed. A corrective run fixed Cartesian RQMC and verified Claim 5 in all 12 ranking cells, but retained synthetic near-constant shortest-path inputs; Claim 4 therefore remained BLOCKED. The next official-data run passed archive integrity, all 12 held-out non-vacuity checks, coverage, topology, controls, and every non-Triangular oracle check. It remained BLOCKED because four oracle blocks were underpowered for Triangular (uncertainty/error 0.316 at 8x8 and 0.530 at 12x12, versus the fixed 0.20 gate).

This calibrated-power child raises only the unresolved Triangular reference-oracle power from four to 32 independent blocks. It retains the original 0.20 gate, every exact method cell, and every cumulative regression. `repro/run.py` will replace this provisional status only from HF evidence. A failed gate is not silently converted to a pass.
