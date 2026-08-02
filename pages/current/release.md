# Release forecast

- Previous live judged score: `8/12`
- Conservative projected score range after the proposed change: `8–10/12`
- Best-supported possible new score: `10/12` — **forecast, not a judge result**

| Claim | Current points | Possible points | Confidence | Evidence status | Basis and remaining risk |
| --- | ---: | ---: | --- | --- | --- |
| 1 | 2 | 2 | HIGH | VERIFIED | Direct identity plus wrong-score control; finite calibration is not universal proof |
| 2 | 2 | 2 | HIGH | VERIFIED | Independent finite differences at ~1e-11 |
| 3 | 2 | 2 | HIGH | VERIFIED | Covariance finite differences at ≤5.21e-10 |
| 4 | 1 | 2 | HIGH | VERIFIED | 447 faithful cells, official data, oracles, raw CSV; evaluator interpretation risk |
| 5 | 1 | 2 | HIGH | VERIFIED | Target within 1% of minimum in 12/12 cases; interpretation risk |
| 6 | 0 | 0 | LOW | BLOCKED | Four routes complete; exact applications and valid falsification unavailable |

Current total score: `8/12`. Conservative projected total: `8–10/12`. Best-supported possible total: `10/12`, forecast only.

Claims 4–5 changed from toy to faithful `VERIFIED` evidence. Claim 6 changed from unattempted to rigorously `BLOCKED` after MNIST, Warcraft, rendering, and TEM routes. It remains blocked by missing author code/assets/configuration and prohibited GPU requirements.

After every gate passes: upload only the exact text allowlist to existing Space `DineshAI/okzQ1x71pS` with the Hugging Face text API; verify revision/hashes; mark awaiting judge; mirror exact text paths to GitHub `main`. No second Space.
