# Claim 1 evaluation

Verdict: **VERIFIED**.

The exact source assumptions and numerical instance are in `claim_contract.json`. The cumulative baseline run `abd54655-bcdb-47e8-99aa-9faeb6692588` produced zero quadrature-versus-closed-form error for both permitted nonsmooth densities. A deliberately wrong Gaussian score produced error `0.05369396702682416`, exceeding the predeclared failure threshold `0.04`.

The verifier is `lemma3_check` in `repro/numerics.py`; `repro/run.py` exits nonzero if either identity exceeds `1e-8` or the negative control does not fail.
