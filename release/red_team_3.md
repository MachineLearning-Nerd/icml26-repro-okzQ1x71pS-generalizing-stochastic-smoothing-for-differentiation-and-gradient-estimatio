# Evaluator-blind review 3

Scope: fresh candidate assembled from exact judged Space revision `a1e96bb5ea2a3bc5106352c8ac10194358c04c57` plus only the text allowlist after canonical Marimo formatting. Review starts at `README.md`; OpenResearch descriptions, local experiment logs, dashboard files, and unpublished-branch knowledge are excluded as evidence.

Files opened, in order:

1. `README.md`
2. `pages/index.md`
3. `pages/current/page.md`
4. `pages/current/claims-1-3.md`
5. linked cumulative results, source, independent checker, and controls
6. `pages/current/claims-4-5.md`
7. linked 447-row CSV, result JSON, checker JSON, source, and controls
8. `pages/current/claim-6.md`
9. linked outputs, checker outputs, source audits, methods, and limitations for all four routes
10. `pages/current/visibility.md`
11. `pages/current/release.md`
12. `reports/full-reproduction/report.md` and all six SVG figures
13. `notebooks/reproduction.py`
14. `release/subset_check.json`
15. `release/upload_allowlist.txt`
16. `release/upload_manifest.sha256`

Claim conclusions from the candidate alone: Claims 1–3 VERIFIED; Claim 4 VERIFIED over the explicit 447-cell contract; Claim 5 VERIFIED under its explicit 12-case/1% criterion and triangular feasibility exception; Claim 6 BLOCKED after four materially distinct routes, with no invalid falsification.

Visibility conclusion: complete. Every visibility-matrix cell is reachable from the canonical entrypoint. Current verification precedes historical evidence; the old page is labeled exactly **Historical rejected baseline**. The judged 17-path set remains a subset, 14 non-navigation historical files are byte-identical, and the three changed historical paths expose current evidence. The final HF regression is the authority for executable checks, including warning-free Marimo validation; publication remains blocked unless that run reports every scientific and release gate true.
