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
| GenLayer CLI alias | `studionet` | `studio-dev` |
| gltest v0.30 RC alias | `studionet` | `studio_devnet` |
| Currency | GEN | GEN |

`studio-next.genlayer.com` may be used to open the preview UI, but programmatic clients should use the canonical `https://studio-dev.genlayer.com/api` endpoint.

Do not relabel the stable `studionet` preset or point it at the preview RPC. The chain ID and consensus deployment must move together.

Important naming distinction: the GenLayer CLI uses `studio-dev`; gltest v0.30 RC uses the built-in `studio_devnet` name.

## Runtime compatibility boundary

The network migration does **not** require rewriting DueProcess's Intelligent Contract runtime header. DueProcess intentionally keeps its existing hash-pinned `py-genlayer` dependency so the contract execution environment remains reproducible.

For that reason this repository separates:

- `requirements-direct.txt`: the proven Direct Mode harness for the contract's pinned runtime;
- `requirements-test.txt`: the Consensus v0.6 Studio-dev RC client/fee/integration tooling.

Do not upgrade or replace the contract's `py-genlayer` hash merely to make an RC Direct Mode loader use a newer SDK generation. Treat a contract-runtime migration as a separate code migration with its own audit and tests.

## Compatible Studio-dev RC tooling

The preview launched with the Consensus v0.6-compatible release-candidate family:

- GenLayer Studio: v0.123 RC
- GenLayer CLI: v0.40 RC (`npm install -g genlayer@rc`)
- genlayer-js: v2.0 RC
- genlayer-py: v0.19 RC
- gltest / genlayer-test: v0.30 RC

The repository pins `genlayer-test` to `v0.30.0-rc.2` in `requirements-test.txt` for the Studio-dev integration/fee path.

## Fee model

Consensus v0.6 introduces fee-funded deploy/write transactions. Treat the fee quote as protocol data, not a hand-written constant.

Recommended flow:

1. run representative branches;
2. generate a measured `fee-profile.json`;
3. request a live fee estimate against Studio-dev using that profile/preset;
4. submit the returned `distribution` and `feeValue` unchanged;
5. wait through finalization;
6. record fee deposit, consumed amount, and refund separately.

The live integration test bootstraps its first measurements by calling the current network's `estimate_transaction_fees` API for every deploy/write. Running it with `--fee-profile fee-profile.json` records finalized observations and produces the profile for later canonical CLI deployments.

The profile stores measured execution allocations, not a forever-valid fee price. Current network prices/caps must still be used at signing time.

For CLI operations, use the current fee-profile/fee-preset estimation path rather than inventing a GEN amount. The CLI supports `--fee-profile`, `--fee-preset`, `--fee-value`, and explicit fee JSON when needed.

Do not infer GenLayer protocol fees from EVM gas. Studio may report gasless EVM behavior while consensus fees are enabled.

## Agent preflight

### A. Repository and CLI

```bash
git clone https://github.com/ometere123/dueprocess.git
cd dueprocess
git checkout main
git pull --ff-only
git rev-parse HEAD

node --version
npm install -g genlayer@rc
genlayer --version
genlayer network list
genlayer network set studio-dev
genlayer network info
```

Then verify the chain independently without a signer:

```bash
python scripts/check_studio_dev.py
```

It must report:

- canonical RPC `https://studio-dev.genlayer.com/api`;
- chain ID `61997`;
- explorer `https://explorer-studio-dev.genlayer.com`.

If anything reports 61999 or the stable Studio RPC, stop before signing.

### B. Pinned Direct Mode verification

Use a separate environment. `genlayer-test v0.29` predates the `studio_devnet` config key, so temporarily swap in the localnet-only Direct Mode config while the suite runs.

```bash
python -m venv .venv-direct
source .venv-direct/bin/activate   # Windows PowerShell: .venv-direct\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements-direct.txt

genvm-lint check contracts/dueprocess.py
genvm-lint check contracts/protected_executor.py

cp gltest.direct.config.yaml gltest.config.yaml
pytest tests/direct -v
git restore gltest.config.yaml

python scripts/preflight.py
```

Expected result: both contracts validate and all 13 adversarial Direct Mode tests pass.

### C. Studio-dev RC verification

Use another environment:

```bash
python -m venv .venv-studio
source .venv-studio/bin/activate   # Windows PowerShell: .venv-studio\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements-test.txt

python scripts/check_studio_dev.py
genvm-lint check contracts/dueprocess.py
genvm-lint check contracts/protected_executor.py
python -m py_compile tests/integration/test_studionet_lifecycle.py scripts/check_studio_dev.py
python scripts/preflight.py
```

## Wallet and funding

Use a dedicated 61997 test wallet. Never commit its private key, mnemonic, browser-wallet session token, keystore password, or `.env` file.

Stable Studionet state is separate. An address can be the same, but a balance/deployment/transaction from chain 61999 is not evidence or funding for chain 61997.

Use the Studio-dev faucet/account selector to obtain test GEN for the new chain when available. Fund enough for:

- the profiling lifecycle;
- canonical DueProcess deployment;
- canonical ProtectedExecutor deployment;
- the valid-process proof;
- the invalid-process proof;
- retry/headroom if a semantic transaction needs it.

Do not guess the exact amount in advance. Start from live estimates/profile measurements and check the wallet balance before each deployment phase.

For live gltest, use a persistent funded signer instead of gltest's automatically generated ephemeral Studio account:

```bash
cp .env.example .env
# Edit .env locally:
# STUDIO_DEV_PRIVATE_KEY=0x...

cp gltest.studio-dev.config.example.yaml gltest.config.yaml
```

`.env` is gitignored. Never commit it.

## Build the fee profile first

With `.venv-studio` active and the 61997 signer funded:

```bash
gltest tests/integration/test_studionet_lifecycle.py -v -s \
  --network studio_devnet \
  --fee-profile fee-profile.json \
  --fee-profile-headroom 1.25
```

The integration test itself:

1. obtains live fee estimates for its deploy/write transactions;
2. deploys DueProcess;
3. builds and seals a charter;
4. completes a valid process;
5. deploys and exercises ProtectedExecutor;
6. creates an invalid process and verifies the gate refuses it;
7. waits through finalization so fee observations are settled;
8. records the measured profile when `--fee-profile` is enabled.

If the bootstrap estimate is insufficient, use the receipt/error to adjust the allocation assumptions deliberately. Do not replace this with an arbitrary fixed GEN fee.

After the live test:

```bash
git restore gltest.config.yaml
```

Keep `.env` local. Review `fee-profile.json`; only commit the profile if the live run completed successfully and the file contains measured allocations rather than secrets.

## Canonical deployment commands

After a successful profile run, deploy fresh canonical submission contracts using the measured profile and current live fee prices.

DueProcess:

```bash
genlayer network set studio-dev
genlayer network info
python scripts/check_studio_dev.py

genlayer deploy \
  --contract contracts/dueprocess.py \
  --fee-profile fee-profile.json \
  --fee-preset standard
```

Wait until the deployment is finalized and confirm execution succeeded. Record the 61997 DueProcess address and explorer link.

Then deploy the consumer with that exact new-chain address:

```bash
genlayer deploy \
  --contract contracts/protected_executor.py \
  --args <DUEPROCESS_61997_ADDRESS> \
  --fee-profile fee-profile.json \
  --fee-preset standard
```

If using browser-wallet signing, use the CLI's browser-wallet option. If using the CLI keystore, use the configured/unlocked account. Do not put raw private keys directly on the command line.

## Canonical live proof sequence

Use `docs/REVIEWER_DEMO.md` as the source of truth.

### Process A — valid

1. Create a charter.
2. Add four roles: `NOTICE_AUTHORITY`, `RESPONDENT`, `DECISION_MAKER`, `EXECUTOR`.
3. Add four mandatory steps: notice, response, decision, execution.
4. Add dependencies 2→1, 3→2, 4→3.
5. Seal the charter and save its `definition_hash`.
6. Open process A.
7. Bind every role to the intended actor(s).
8. Start process A.
9. Submit the four public evidence records in order and confirm each becomes `SATISFIED`.
10. Finalize process A and confirm `VALID`.
11. Confirm `is_valid(A, charter_hash) == true`.
12. Execute a fresh `action_hash` through ProtectedExecutor and confirm success.

The repository's immutable fixture evidence is pinned at commit `a156a47b0f5f00ff65d8b65ad8d42ed1b3a691f2` under `fixtures/`.

### Process B — invalid

1. Open a second process against the same sealed charter.
2. Bind roles and start it.
3. Have the bound decision maker attempt the decision step before its required predecessor is complete.
4. Confirm `PROCEDURAL_VIOLATION` / `DEPENDENCY_MISSING` and terminal `INVALID`.
5. Confirm `is_valid(B, charter_hash) == false`.
6. Attempt a different ProtectedExecutor `action_hash` and confirm execution is refused.

## Evidence to record

Populate `DEPLOYMENT.md` with real 61997 data only:

- current final Git commit SHA;
- wallet public address only;
- chain ID 61997;
- DueProcess address;
- ProtectedExecutor address;
- deployment transaction IDs;
- `explorer-studio-dev.genlayer.com` links;
- consensus status;
- execution result;
- fee deposit;
- fee consumed;
- fee refunded after finalization;
- charter definition hash;
- valid process ID;
- invalid process ID;
- at least one semantic `SATISFIED` transaction with consensus evidence;
- ProtectedExecutor success transaction;
- ProtectedExecutor refusal evidence.

A transaction is not submission evidence merely because consensus says accepted/finalized. Confirm contract execution succeeded as well. Prefer finalized receipts so fee accounting is settled.

## Completion checkpoint

The agent should not report “done” until:

- chain guard says 61997;
- both CI environments are green;
- the funded live integration passes;
- `fee-profile.json` is measured successfully;
- both canonical contracts are finalized on 61997;
- valid and invalid consumer-gate proofs are complete;
- `DEPLOYMENT.md` contains real evidence with no placeholders;
- no secret file/key was committed;
- all final source/evidence changes are pushed to `main`.
