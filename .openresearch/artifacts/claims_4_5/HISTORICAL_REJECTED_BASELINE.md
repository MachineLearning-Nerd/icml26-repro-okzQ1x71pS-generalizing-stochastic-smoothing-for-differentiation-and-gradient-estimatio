# Historical rejected baseline

Commit `1deb3262fbb425f3ff53020c4e64e9cb661fa85f`, run `dac6c903-b365-4609-8cd9-e1fb2cffb0ee`, completed all 447 cells on Hugging Face `cpu-upgrade` in 783.242 verifier seconds with 64 logical CPUs and no GPU.

This is not the current verifier. It used a tensor product of axis-jittered coordinates for Cartesian RQMC rather than an independent point in every Cartesian cell. Its path oracle also failed the prespecified stability check in 8 of 12 cases. Claims 4 and 5 therefore remained BLOCKED. The raw JSON and CSV are preserved beside this page.

The current verifier is `repro/section4.py` on the descendant branch and supersedes this rejected route.
