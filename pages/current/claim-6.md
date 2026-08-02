# Claim 6 — four application demonstrations

Status: **BLOCKED**. Confidence: **LOW** after three verification routes and the mandatory fourth falsification route. The exact claim quantifies over all four named demonstrations.

| Route | Exact paper scale | CPU evidence | Result/control |
| --- | --- | --- | --- |
| MNIST | n=5, 100k steps, 12 seeds, batch 100, 256 Laplace/RLHS/LOO | official data; 100 measured steps | validation 0.007→0.326; test 0.307; projected 34.10h/seed; **BLOCKED** |
| Warcraft | 50 epochs, five seeds, batch 70, 100 Logistic/RLHS/LOO | official 10k/1k; 20 measured steps | loss 0.07251→0.04354; 64/64 quantization-compatible; missing-start control 0/64 valid; **BLOCKED** |
| Utah teapot | 4 DoF, 1,000 steps, 768 seeds | pinned GenDR capability/protocol audit | four CUDA extensions; CPU build fails; shallow patch still CUDA-dependent; **BLOCKED** |
| TEM | 400x400; exact 2D/4D domains; Adam betas (0.5,0.9) | authenticated archives and safe manifests | corruption rejected; no exact deck/optimizer; no counterexample; **BLOCKED** |

TEM is an existential historical claim. Missing assets, capability failure, or a substitute cannot falsify it; `counterexample_found=false` and `all_paper_assumptions_satisfied=false`.

- MNIST: [`raw`](https://huggingface.co/spaces/DineshAI/okzQ1x71pS/blob/main/evidence/run_cbb3de08/mnist_result.json), [`checker`](https://huggingface.co/spaces/DineshAI/okzQ1x71pS/blob/main/evidence/run_cbb3de08/mnist_checker.json)
- Warcraft: [`raw`](https://huggingface.co/spaces/DineshAI/okzQ1x71pS/blob/main/evidence/run_cbb3de08/warcraft_result.json), [`checker`](https://huggingface.co/spaces/DineshAI/okzQ1x71pS/blob/main/evidence/run_cbb3de08/warcraft_checker.json)
- Rendering: [`raw`](https://huggingface.co/spaces/DineshAI/okzQ1x71pS/blob/main/evidence/run_cbb3de08/rendering_result.json), [`checker`](https://huggingface.co/spaces/DineshAI/okzQ1x71pS/blob/main/evidence/run_cbb3de08/rendering_checker.json)
- TEM: [`raw`](https://huggingface.co/spaces/DineshAI/okzQ1x71pS/blob/main/evidence/run_cbb3de08/tem_result.json), [`checker`](https://huggingface.co/spaces/DineshAI/okzQ1x71pS/blob/main/evidence/run_cbb3de08/tem_checker.json)
- Code and limitations: [`repro`](https://huggingface.co/spaces/DineshAI/okzQ1x71pS/tree/main/repro), [`.openresearch/artifacts/claim_6`](https://huggingface.co/spaces/DineshAI/okzQ1x71pS/tree/main/.openresearch/artifacts/claim_6)

Unblocking requires author code/assets/configuration and full-scale compute. GPU use remains prohibited.
