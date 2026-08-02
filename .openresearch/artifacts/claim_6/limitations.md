# Claim 6 limitations and deviations

- The authors' application implementation is not publicly linked in the paper or discoverable from the cited project pages. This campaign reconstructs disclosed protocols from the paper and cited primary repositories.
- This first MNIST route times 100 steps and does not run 100,000 steps or 12 seeds. It must remain BLOCKED regardless of its accuracy or loss.
- The paper does not identify the cross-validated gamma or exact variance-reduction cell for each MNIST table entry. This calibration uses the disclosed candidate gamma 1/3 and the paper's stated generally preferred randomized Latin/LOO combination.
- Torchvision's 60,000-image training split is divided deterministically into 55,000 train and 5,000 validation images to match the cited NeuralSort cardinalities.
- Warcraft training, rendering, and TEM optimization are not part of this route.
