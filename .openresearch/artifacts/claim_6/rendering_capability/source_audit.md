# Rendering source audit

- Paper: 4-DoF Utah-teapot pose optimization; 1,000 Adam steps; betas `(0.5, 0.99)`; learning rate `0.3` with cosine annealing; 768 seeds; success below five degrees.
- Primary cited source: `Felix-Petersen/gendr@c89269cb38eef7a95be703154f676a56d791958f`, retrieved 2026-08-02 with an explicit User-Agent.
- Fixed SHA-256: `experiments/opt_camera.py` `926ad20864e018fb9b945ac374f57b146d676f8bb15f78b1364bbbe05b0359f1`; `experiments/data/teapot.obj` `2f833c87e691d949dfa1325df94efe3c25e95b948c7f147e2d08e3ffb719fcda`; `setup.py` `fe2452a26d699ca09269054086444370f3c5f3e1bed1db2366c0a4ca8fd588a6`; `README.md` `b1bf5f6c79136ae674798f7e439de58ce1b4188faae37d509d1452797f184a03`.
- The cited source requires CUDA and is not the paper's black-box smoothing implementation. The executable audit tests that boundary directly on HF `cpu-upgrade`.
