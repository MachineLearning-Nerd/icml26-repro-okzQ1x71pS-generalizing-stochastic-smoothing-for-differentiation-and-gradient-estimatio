# Claims 4–5 evaluation

Current status: **Claim 5 VERIFIED; Claim 4 BLOCKED pending the official-data corrective child run.**

The first full-domain run completed all 447 cells but was rejected because its Cartesian RQMC construction used tensor-product axis jitter and its path-oracle uncertainty check failed. A corrective run fixed Cartesian RQMC and verified Claim 5 in all 12 ranking cells, but retained synthetic near-constant shortest-path inputs; Claim 4 therefore remained BLOCKED. The current child uses MD5-verified official Warcraft maps and independently calibrated, held-out non-vacuity checks. `repro/run.py` will replace this provisional status only from HF evidence. A failed gate is not silently converted to a pass.
