# Claims 4–5 evaluation

Current status: **BLOCKED**, pending the corrective child run.

The first full-domain run completed all 447 cells but was rejected because its Cartesian RQMC construction used tensor-product axis jitter and its path-oracle uncertainty check failed. That frozen node is labeled **Historical rejected baseline**. The current verifier uses independent per-cell jitter, 262,144-sample path oracles, and a separate checker. `repro/run.py` will replace this provisional status only from evaluator-visible run evidence. A failed ranking is not silently converted to a pass.
