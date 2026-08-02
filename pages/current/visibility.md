# Evaluator visibility matrix

Traversal: [`pages/index.md`](#/index) → [Current verification](#/current). Raw links point to downloadable Space files; checkers exit nonzero on failure.

| Claim | Canonical page | Code visible | Data inline | Raw link | Checker | Control | Exact claim tested | Reviewer verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | [Claims 1–3](#/current-claims-1-3) | Yes | Yes | `cumulative_result.json` | cumulative | wrong score | Yes | Ready: VERIFIED |
| 2 | [Claims 1–3](#/current-claims-1-3) | Yes | Yes | `cumulative_result.json` | cumulative | finite differences | Yes | Ready: VERIFIED |
| 3 | [Claims 1–3](#/current-claims-1-3) | Yes | Yes | `cumulative_result.json` | cumulative | finite differences | Yes | Ready: VERIFIED |
| 4 | [Claims 4–5](#/current-claims-4-5) | Yes | Yes | `section4_raw.csv` | `section4_checker.json` | wrong score/non-vacuity | Yes | Ready: VERIFIED |
| 5 | [Claims 4–5](#/current-claims-4-5) | Yes | Yes | `section4_raw.csv` | `section4_checker.json` | feasibility exception | Yes | Ready: VERIFIED |
| 6 | [Claim 6](#/current-claim-6) | Yes | Yes | four result JSONs | four checker JSONs | distinct per route | Yes | Ready: BLOCKED |

Common provenance on the current page: command, lockfile, Git SHA, seeds, allocation, cgroup quota, worker cap, runtime, cost, limitations, and historical supersession.
