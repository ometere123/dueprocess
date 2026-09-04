# Deployment evidence

Status: **STUDIO-DEV READY — LIVE DEPLOYMENT EVIDENCE NOT YET RECORDED**

This file is intentionally not populated with invented addresses, transaction hashes, or fee values.

## Target deployment

DueProcess now targets the GenLayer **Studio development preview** / Consensus v0.6 release-candidate environment.

- Studio web app: `https://studio-dev.genlayer.com`
- Browser alias: `https://studio-next.genlayer.com`
- Canonical RPC: `https://studio-dev.genlayer.com/api`
- Chain ID: `61997`
- Currency: `GEN`
- Explorer: `https://explorer-studio-dev.genlayer.com`
- CLI network alias: `studio-dev`

Do not deploy this evidence run against stable Studionet (`61999`, `https://studio.genlayer.com/api`). The two Studio environments have different chain IDs and consensus deployments.

Deploy, in order:

1. `contracts/dueprocess.py`
2. `contracts/protected_executor.py` with the finalized DueProcess address as constructor input.

## Fee policy

Consensus v0.6 writes are fee-aware. Do **not** invent or hardcode a fixed fee value in this document.

For each deploy/write:

1. use the matching v0.6-compatible RC tooling;
2. estimate the transaction using the live Studio-dev fee configuration;
3. submit the exact returned fee `distribution` and `feeValue` (or allow the supported CLI/SDK path to derive them automatically);
4. keep enough GEN in the signer wallet to cover the quoted deposit plus retries;
5. after finalization, record the deposit, consumed fees, and refund separately.

Unused protocol fee budget may be refunded at finalization. Studio's outer EVM gas layer can be gasless while GenLayer consensus fees are still enabled, so do not use `eth_gasPrice` as the fee source.

## Record after deployment

### DueProcess

- Network: Studio development preview / chain 61997
- Contract address:
- Deployment transaction:
- Explorer link:
- Consensus status:
- Execution result:
- Fee deposit:
- Fee consumed:
- Fee refunded:
- Finalized at:

### ProtectedExecutor

- Network: Studio development preview / chain 61997
- Contract address:
- Deployment transaction:
- Explorer link:
- Consensus status:
- Execution result:
- Fee deposit:
- Fee consumed:
- Fee refunded:
- Finalized at:

## Lifecycle evidence

Record exact finalized transaction links and fee outcomes for:

- charter creation;
- role creation;
- step creation;
- dependency creation;
- charter seal;
- valid process open/bind/start;
- each valid semantic step attempt;
- valid process finalization;
- successful `ProtectedExecutor.execute`;
- invalid process open/bind/start;
- premature authorized step attempt;
- terminal invalidation;
- failed `ProtectedExecutor.execute` against the invalid process.

A transaction counts as successful evidence only when the protocol status reaches `ACCEPTED`/`FINALIZED` **and** contract execution reports successful completion (for example `FINISHED_WITH_RETURN`). Prefer finalized receipts for the submission evidence so fee consumption/refunds are settled.

See `docs/REVIEWER_DEMO.md` and `docs/STUDIO_DEV_MIGRATION.md` for the exact review and migration path.
