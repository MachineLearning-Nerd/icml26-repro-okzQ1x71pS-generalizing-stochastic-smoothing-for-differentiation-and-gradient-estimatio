# Rendering route: pinned-source CPU capability gate

The fixed command downloads the exact cited GenDR commit, validates four prespecified source hashes, audits the teapot mesh and disclosed pose protocol, and runs `.venv/bin/python setup.py build_ext` on HF `cpu-upgrade`. It records Torch's CUDA build state, runtime GPU availability, `nvcc`, build output, CPU allocation, and runtime.

The negative control changes only the camera script's `device` token to CPU and confirms that all four CUDA extensions remain required. This rejects a superficial patch as an alleged CPU implementation.

No pose result is produced. A different CPU renderer would be a substitute, while the cited camera script itself differs from the paper's input distribution and smoothing construction. The only honest verdict is `BLOCKED`.
