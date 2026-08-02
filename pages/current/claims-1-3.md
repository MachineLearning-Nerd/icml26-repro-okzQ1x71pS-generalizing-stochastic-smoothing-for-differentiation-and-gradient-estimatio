# Claims 1–3 — theorem calibration

Status: **VERIFIED** for all three finite numerical identities. These faithful finite checks corroborate formulas; they are not universal proofs.

| Claim | Contract | Observed | Threshold |
| --- | --- | ---: | ---: |
| Lemma 3 | `f(x)=|x|`, `x=0.37`, unit Laplace and triangular perturbations | 0 / 0 | ≤1e-8 |
| Theorem 7 | location and scale derivatives vs independent finite differences | 9.95e-12 / 1.53e-11 | <1e-7 |
| Theorem 8 | output covariance derivatives vs finite differences | 2.37e-11 / 5.20e-10 | <1e-7 |

Negative control: Gaussian score substituted for Laplace gives error `0.0536939670`, required `>0.04`.

- Code: [`numerics.py`](https://huggingface.co/spaces/DineshAI/okzQ1x71pS/blob/main/repro/numerics.py), [`run.py`](https://huggingface.co/spaces/DineshAI/okzQ1x71pS/blob/main/repro/run.py)
- Raw/checker evidence: [`cumulative_result.json`](https://huggingface.co/spaces/DineshAI/okzQ1x71pS/blob/main/evidence/run_cbb3de08/cumulative_result.json)
- Contracts and controls: [`.openresearch/artifacts/claim_1`](https://huggingface.co/spaces/DineshAI/okzQ1x71pS/tree/main/.openresearch/artifacts/claim_1)

Limitations: deterministic calibration at disclosed functions and points; no claim of exhaustive proof.
