# Historical rejected baseline

Frozen run `a53fa2d7-1c5b-4a06-82a5-b5007ded9f34` at commit `10ab5598233c6c6885567059ff30cfffb9df3b49` completed the official-data Warcraft calibration but rejected the independent oracle because only 61 of 64 recomputed optimal paths had the same binary encoding as the official label.

The result is preserved: exact-encoding match `0.953125`, loss first-five mean `0.0721171`, loss last-five mean `0.0399204`, initial test exact match `0.031`, final test exact match `0.178`, and measured time `133.191` seconds for 20 steps. The shifted-label control matched zero paths. The verifier exited nonzero.

This was over-strict because equality of binary encodings is not equality of shortest-path optima when ties exist. The current verifier in `repro/check_warcraft.py` instead requires that both paths are valid and that their independently computed objective costs agree, while reporting exact encoding separately.
