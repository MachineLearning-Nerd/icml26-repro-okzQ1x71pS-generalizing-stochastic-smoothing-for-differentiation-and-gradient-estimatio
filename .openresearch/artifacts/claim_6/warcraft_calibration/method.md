# Warcraft route: official-data CPU calibration

This route reconstructs the Section 4.3 application from the paper and the cited primary Warcraft repository at commit `027e82ee818530f2823851d6530e0d2c8657bbcb`. It uses the official 12x12-grid archive (DOI `10.17617/3.YJCQ5S`), all 10,000 training maps, and the full 1,000-map test split. Each map image is RGB 96x96; vertex weights and paths are 12x12.

The model is the cited `CombRenset18`: ResNet18 through `layer1`, adaptive max pooling to 12x12, and averaging the 64 channels. The declared paper protocol is Adam at 0.001, batch size 70, 50 epochs, learning-rate drops after epochs 30 and 40, and five seeds. The measured route executes two warm-up and 20 optimizer steps for an independently measured CPU throughput projection. It does not advance the epoch scheduler.

The tested smoothing cell uses 100 Logistic samples, independently randomized Latin hypercubes for each batch item, the LOO covariate, and MSE against the ground-truth hard path. The paper does not disclose the chosen Figure 6 gamma or the output-to-cost transform, so this reconstruction fixes gamma 0.1 from the disclosed Figure 7 sweep and interprets network outputs as log vertex costs.

Before training, the independent oracle recomputes shortest paths from the official vertex weights for 64 held-out examples. The official weights are stored as `float16`, so the current oracle requires valid paths and overlap of independently computed path-cost intervals induced by half-precision quantization. Exact binary encoding and exact post-serialization cost remain diagnostics, not acceptance conditions. A deterministic negative control removes the required start cell from every official path and must make all 64 paths invalid. The checker exits nonzero if the archive, protocol, primary source commit, oracle, control, CPU allocation, throughput, finite-loss, or honest-BLOCKED contracts fail.

This supersedes both historical rejected verifiers: exact encoding at frozen run `a53fa2d7-1c5b-4a06-82a5-b5007ded9f34`, and exact cost over serialized half-precision weights at frozen run `c9293803-334e-461f-9112-e13c45151f62`.

The fixed command remains:

```text
uv sync --frozen --no-dev && .venv/bin/python -m repro.run
```
