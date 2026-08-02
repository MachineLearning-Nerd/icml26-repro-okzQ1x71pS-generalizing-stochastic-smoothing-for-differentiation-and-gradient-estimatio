# MNIST exact-protocol throughput route

This route reconstructs the cited NeuralSort four-digit generator, the paper's exact CNN shape, n=5 row-cross-entropy ranking loss, 256-sample Laplace smoothing with randomized Latin hypercube sampling and the LOO covariate, batch size 100, and Adam at learning rate 0.001.

After five unmeasured warmup steps, exactly 100 steps are timed on HF `cpu-upgrade`. The observed seconds per step are multiplied by the disclosed 100,000 steps and 12 seeds only to estimate the resource requirement. Initial and post-calibration exact-match accuracies are reported to prevent a vacuous timing-only run. The independent checker requires the official MNIST cardinalities and raw-file hashes, exact protocol metadata, finite losses, CPU-only execution, and an explicit BLOCKED verdict.

This is not a downscaled reproduction result and cannot verify Claim 6. It is a calibrated decision route toward or away from the full protocol.
