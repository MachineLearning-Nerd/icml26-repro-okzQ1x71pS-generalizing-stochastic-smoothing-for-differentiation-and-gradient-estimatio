# Historical rejected baseline

Frozen run `c9293803-334e-461f-9112-e13c45151f62` at commit `552b78becdb9a78629f679370b913c514c668eaa` completed every Warcraft computation but required exact agreement between official-label cost and independently recomputed cost over weights serialized as `float16`.

It observed exact encoding and exact stored-cost agreement on 61/64 examples (`0.953125`), a maximum absolute cost gap of `0.0009765625`, and valid official and oracle paths for all examples. Its cyclic-shift control left 9/64 paths valid (`0.140625`), above a prespecified `<0.1` threshold. The checker therefore exited nonzero.

That verifier is rejected because it ignored the published half-precision quantization interval and used a chance-sensitive control threshold. The current verifier records exact stored-cost agreement but accepts only when all official paths are compatible with the independent optimum under explicit half-precision cost intervals. Its deterministic negative control removes the required start cell and must invalidate every path.
