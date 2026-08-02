# Claim 6 source audit

The exact claim spans all four named demonstrations, so success on only one application cannot verify it.

- Section 4.2: sets of five four-digit MNIST images; exact-match ordering accuracy; 100,000 Adam steps at learning rate 0.001 and batch size 100; 12 seeds; the cited two-convolution CNN; gamma selected from `{1, 1/3, 0.1}`.
- Section 4.3: official 12x12 Warcraft maps; first ResNet18 block; 50 Adam epochs, batch size 70, learning rate 0.001 with tenfold drops at epochs 30 and 40; five seeds.
- Section 4.4: Utah teapot, four camera degrees of freedom; 1,000 Adam steps with betas `(0.5, 0.99)`, initial learning rate 0.3 and cosine schedule; 768 seeds; success within five degrees.
- Section 4.5: TEM-simulator v1.3, 400x400 micrographs, two- and four-parameter searches, ground truth 300 kV / 3 mm / centered specimen, Adam betas `(0.5, 0.9)`, and 20 repetitions for random search. The paper does not disclose the full simulator input deck, TMV asset, Adam learning rate, or optimization horizon.

The paper reports GPU runtimes for the first three applications, but this campaign is CPU-only. The first route therefore measures the exact MNIST protocol's CPU throughput independently before deciding whether a full run is feasible. It is not acceptance evidence by itself.

For Warcraft, the paper cites the primary `martius-lab/blackbox-differentiation-combinatorial-solvers` repository. Its live source was fixed at commit `027e82ee818530f2823851d6530e0d2c8657bbcb` before reconstruction. `warcraft_shortest_path/models.py` defines the application model as ResNet18 `conv1`, `bn1`, `relu`, `maxpool`, and `layer1`, followed by adaptive 12x12 max pooling and a mean over 64 channels. `warcraft_shortest_path/data_utils.py` defines channel-first maps normalized with full-training-set channel means and standard deviations. The paper overrides the older repository configuration with learning rate 0.001 and specifies smoothing of the algorithm with MSE against the hard path.
