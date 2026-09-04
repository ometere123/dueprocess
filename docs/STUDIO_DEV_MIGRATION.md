# Studio-dev / Consensus v0.6 migration

DueProcess uses the GenLayer Studio development preview for its live submission proof.

## Network identity

| Setting | Stable Studionet (old target) | Studio development preview (new target) |
| --- | --- | --- |
| Chain ID | `61999` | `61997` |
| RPC | `https://studio.genlayer.com/api` | `https://studio-dev.genlayer.com/api` |
| Web app | `https://studio.genlayer.com` | `https://studio-dev.genlayer.com` |
| Browser alias | — | `https://studio-next.genlayer.com` |
| Explorer | `https://explorer-studio.genlayer.com` | `https://explorer-studio-dev.genlayer.com` |
| CLI alias | `studionet` | `studio-dev` |
| Currency | GEN | GEN |

`studio-next.genlayer.com` may be used to open the preview UI, but programmatic clients should use the canonical `https://studio-dev.genlayer.com/api` endpoint.

Do not relabel the stable `studionet` preset or point it at the preview RPC. The chain ID and consensus deployment must move together.

## Compatible RC tooling

This migration intentionally uses the Consensus v0.6-compatible release-candidate family released with the preview:

- GenLayer Studio: v0.123 RC
- GenLayer CLI: v0.40 RC (`npm install -g genlayer@rc`)
- genlayer-js: v2.0 RC
- genlayer-py: v0.19 RC
- gltest / genlayer-test: v0.30 RC

The repository pins `genlayer-test` to `v0.30.0-rc.2` for Python integration/direct tooling.

## Fee model

Consensus v0.6 introduces fee-funded deploy/write transactions. Treat the fee quote as protocol data, not a hand-written constant.

Recommended flow:

1. run representative contract branches;
2. generate/maintain a `fee-profile.json` if using profiling;
3. request a live fee estimate against Studio-dev;
4. submit the returned `distribution` and `feeValue` unchanged;
5. wait for finalization;
6. record deposit, consumed fees, and refund separately.

For CLI operations, omitting a manually supplied `--fee-value` lets the current RC derive the required deposit through the supported fee-estimation path. `genlayer estimate-fees` can be used when an explicit quote is needed.

Do not infer GenLayer protocol fees from EVM gas. Studio may report gasless EVM behavior while consensus fees are enabled.

## Agent preflight

From a clean checkout:

```bash
node --version
npm install -g genlayer@rc
genlayer --version
genlayer network list
genlayer network set studio-dev
genlayer network info

python -m venv .venv
source .venv/bin/activate   # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements-test.txt

genvm-lint check contracts/dueprocess.py
genvm-lint check contracts/protected_executor.py
pytest tests/direct -v
python scripts/preflight.py
```

Expected network after `genlayer network set studio-dev`:

- RPC resolves to the Studio development preview;
- `eth_chainId` resolves to `61997`;
- explorer evidence uses `explorer-studio-dev.genlayer.com`.

If the CLI reports 61999 or the stable Studio RPC, stop and fix the network selection before signing anything.

## Wallet and funding

Use a dedicated test wallet. Never commit its private key, mnemonic, browser-wallet session token, keystore password, or `.env` file.

The signer must have enough Studio-dev GEN to cover the quoted fee deposits for two contract deployments plus the complete valid and invalid demo flows. Use the built-in Studio-dev faucet/account selector if available. Recheck balance before deployment and before the semantic-step sequence.

Because Studio-dev is a preview environment, state can reset. A balance, deployment, or transaction from stable Studionet is not proof for chain 61997.

## Live proof sequence

1. Deploy `DueProcess` and wait for a successful finalized outcome.
2. Deploy `ProtectedExecutor(DueProcessAddress)` and wait for finalization.
3. Create roles/steps/dependencies and seal a charter.
4. Run Process A through all four semantic steps, finalize it `VALID`, then prove `ProtectedExecutor.execute` succeeds.
5. Run Process B and deliberately have the bound decision maker attempt a dependent step too early; prove terminal `INVALID`.
6. Prove `ProtectedExecutor.execute` refuses Process B.
7. Record every address, transaction ID, explorer link, consensus/execution outcome, and finalized fee/refund in `DEPLOYMENT.md`.

## Success criteria

For submission evidence, do not treat a transaction as successful merely because it has an accepted/finalized consensus status. Confirm execution completed successfully as well. Prefer finalized receipts when recording fee results.
