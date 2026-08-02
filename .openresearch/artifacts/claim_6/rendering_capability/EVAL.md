# Rendering capability evaluation

Status before HF execution: **BLOCKED**.

The current fixed command writes `result.json`, runs `python -m repro.check_rendering`, prints both raw result and checker output, and exits nonzero if source identity, protocol, capability, control, allocation, or verdict checks fail. Numerical output is accepted only from the HF run log.
