# Claim 6 source audit

The exact claim spans all four named demonstrations, so success on only one application cannot verify it.

- Section 4.2: sets of five four-digit MNIST images; exact-match ordering accuracy; 100,000 Adam steps at learning rate 0.001 and batch size 100; 12 seeds; the cited two-convolution CNN; gamma selected from `{1, 1/3, 0.1}`.
- Section 4.3: official 12x12 Warcraft maps; first ResNet18 block; 50 Adam epochs, batch size 70, learning rate 0.001 with tenfold drops at epochs 30 and 40; five seeds.
- Section 4.4: Utah teapot, four camera degrees of freedom; 1,000 Adam steps with betas `(0.5, 0.99)`, initial learning rate 0.3 and cosine schedule; 768 seeds; success within five degrees.
- Section 4.5: TEM-simulator v1.3, 400x400 micrographs, two- and four-parameter searches, ground truth 300 kV / 3 mm / centered specimen, Adam betas `(0.5, 0.9)`, and 20 repetitions for random search. The paper does not disclose the full simulator input deck, TMV asset, Adam learning rate, or optimization horizon.

The paper reports GPU runtimes for the first three applications, but this campaign is CPU-only. The first route therefore measures the exact MNIST protocol's CPU throughput independently before deciding whether a full run is feasible. It is not acceptance evidence by itself.
