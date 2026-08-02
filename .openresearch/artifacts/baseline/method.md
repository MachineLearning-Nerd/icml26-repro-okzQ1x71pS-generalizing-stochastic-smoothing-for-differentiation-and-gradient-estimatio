# Baseline method

Claims 1-3 are rerun with independent quadrature and central finite differences. Claim 1 includes a deliberately wrong Gaussian score for a Laplace density. Claims 4-5 rerun only the historical 1D proxy and are explicitly rejected as current verification. Claim 6 is BLOCKED in this baseline.

Fixed command: `uv sync --frozen --no-dev && .venv/bin/python -m repro.run`

Seed: 2024. Estimated useful cores: 2. Selected compute: Hugging Face `cpu-upgrade`; the run prints the actual logical CPU allocation and wall time.
