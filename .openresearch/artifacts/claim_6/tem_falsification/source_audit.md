# TEM primary-source audit

- Simulator: `https://sourceforge.net/projects/tem-simulator/files/TEM-simulator_1.3.zip/download`, published size 425,791 bytes, MD5 `5c47d4946ecc222f27be7dce03e0228b`.
- TMV example: `https://sourceforge.net/projects/tem-simulator/files/Simulation_example_TMV_v2.zip/download`, published size 887,170 bytes, MD5 `a56518e96a88f922b0529a5e67a19ed3`.
- Retrieval uses the explicit browser User-Agent `OpenResearch-Reproduction/1.0` inside the HF CPU job. The verifier requires an exact published identity match, a safe ZIP manifest, and hashes every member.
- The paper fixes TEM-simulator v1.3 and parameter ranges but does not publish the authors' exact simulator deck, mapping from the public TMV example to their specimen, smoothing implementation, initializations, Adam learning rate, or optimization horizon.
