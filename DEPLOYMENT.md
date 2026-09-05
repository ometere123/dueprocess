# Deployment evidence

## Final canonical deployment

- Network: Studio development preview (Consensus v0.6)
- Chain ID: `61997`
- RPC: `https://studio-dev.genlayer.com/api`
- Explorer: `https://explorer-studio-dev.genlayer.com`
- Signer public address: `0x0d5540e0aD4B92Aa0ad4e5F1b8cD645ee1E363E7`

### DueProcess — reusable Intelligent Contract primitive

- Source: 47,328 bytes
- SHA-256: `329dab95d3dc8fb19936d8361a8274ffe2133fcd841c794e5bb3a68520321c9e`
- Address: `0x171cb0490c6C835e45D062EBbce2cEDcef61Bf42`
- Deployment transaction: `0x103156b937ecd1b8956b59999e027b02bde22da666aae5de4da105d0267f2df`
- Explorer: `https://explorer-studio-dev.genlayer.com/tx/0x103156b937ecd1b8956b59999e027b02bde22da666aae5de4da105d0267f2df`
- Final status: `FINALIZED`; consensus `ACCEPTED`; execution `FINISHED_WITH_RETURN / SUCCESS`
- Fee deposit: `100000000000010352 wei`; consumed: `79001500000823 wei`; refund: `99920998500009529 wei`

### ProtectedExecutor — reference consumer / cross-contract composability proof

- Source: 3,167 bytes
- SHA-256: `8928e371d2daed60f0ac4837a2c6bd6e17927162fe285bc3afe0600160b9ad34`
- Address: `0x6eb897E15f94d24dd53fFa37A3c175095DB54735`
- Bound DueProcess: `0x171cb0490c6C835e45D062EBbce2cEDcef61Bf42`
- Deployment transaction: `0x6a725e48f24229779727983da21f570dd4df220c025c16e14e6b6076b4c036f8`
- Explorer: `https://explorer-studio-dev.genlayer.com/tx/0x6a725e48f24229779727983da21f570dd4df220c025c16e14e6b6076b4c036f8`
- Final status: `FINALIZED`; consensus `ACCEPTED`; execution `FINISHED_WITH_RETURN / SUCCESS`
- Fee deposit: `100000000000010352 wei`; consumed: `78655000000823 wei`; refund: `99921345000009529 wei`

## Final lifecycle evidence

- Charter ID: `1`
- Definition hash: `b68e1e36ba6ee30105d369d6851bcae775cc81eaf808f89f3d67c16bfbd6fbdf`
- Process A: ID `1`; final status `VALID`; final hash `96e21980d2a64f53b07642946e5edec82980ea7f62d5d51ac80bc477d9039c9e`; all four steps `SATISFIED`; `is_valid == true`; good action executed and `was_executed == true`.
- Process A semantic step transactions include step 1 `0xaf1ba5c50fc7f7e435eef9a918cbe2013e25dc12ede90f1b7799a2fbdad7ca50` and step 2 `0x9d7cdecbc4fb4df8ecd3c3232ef9a6eba64e36da8718ca371413e709aa645106`; steps 3–4 remain in the finalized lifecycle receipt history.
- Process B: ID `2`; final status `INVALID`; violation step `3`; code `DEPENDENCY_MISSING`; `is_valid == false`.
- Process B ProtectedExecutor refusal: `0xc843f7fb0b5ef2cacea9f5a0dec02dcb65dc6ce6e6dbbf4e3b68f31fda3c75aa`; `was_executed == false`.

## Superseded migration deployments

These were successful migration deployments, superseded only after live testing exposed v0.3 compatibility differences: `0xb1971098715130D2B44F4cAD89C9138830503BC1` (raw timestamp exposure), `0x7D2D7683E6ED899467c89F3AeAB193Fd9B7EFC56` (removed `run_nondet_unsafe`), and `0xaeDf19550F5846EDdd5ee61BA71bBfAE1d1B1b74` (`StepAttempted` exceeded the four-topic limit).
