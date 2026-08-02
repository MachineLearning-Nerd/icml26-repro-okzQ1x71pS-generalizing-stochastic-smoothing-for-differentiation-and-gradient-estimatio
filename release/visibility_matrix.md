# Release visibility matrix

Traversal: `README.md` → `pages/index.md` → `pages/current/page.md`. All raw paths are downloadable from the same Space revision.

| Claim | Canonical page | Code visible | Data inline | Raw link | Checker | Control | Exact claim tested | Reviewer verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `pages/current/claims-1-3.md` | Yes | Yes | `cumulative_result.json` | cumulative | wrong score | Yes | Ready: VERIFIED |
| 2 | `pages/current/claims-1-3.md` | Yes | Yes | `cumulative_result.json` | cumulative | finite differences | Yes | Ready: VERIFIED |
| 3 | `pages/current/claims-1-3.md` | Yes | Yes | `cumulative_result.json` | cumulative | finite differences | Yes | Ready: VERIFIED |
| 4 | `pages/current/claims-4-5.md` | Yes | Yes | `section4_raw.csv` | `section4_checker.json` | wrong score/non-vacuity | Yes | Ready: VERIFIED |
| 5 | `pages/current/claims-4-5.md` | Yes | Yes | `section4_raw.csv` | `section4_checker.json` | feasibility exception | Yes | Ready: VERIFIED |
| 6 | `pages/current/claim-6.md` | Yes | Yes | four result JSONs | four checker JSONs | distinct per route | Yes | Ready: BLOCKED |

Common provenance visible on the current page: fixed command, lockfile, scientific and release Git SHAs, deterministic seeds, actual allocation, runtime, cost, limitations, deviations, and historical supersession.
