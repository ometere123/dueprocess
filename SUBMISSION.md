# DueProcess — Intelligent Contracts submission notes

## One-liner

A reusable GenLayer primitive that proves whether a public process followed its frozen roles, evidence requirements, ordering, waiting periods, and deadlines before another contract acts on the result.

## What it is

DueProcess separates **procedural validity** from substantive correctness.

A charter defines symbolic roles and ordered/dependent steps. Each step combines deterministic constraints with a bounded natural-language criterion for public evidence. Once sealed, the charter is immutable and hash-pinned by every process instance.

GenLayer consensus is used only where ordinary smart contracts are insufficient: deciding whether a public source semantically establishes that a required procedural step occurred. Validators independently re-fetch the source and re-run the criterion evaluation.

Role identity, dependency order, delays, deadlines, invalidation, finalization, and consumer gating remain deterministic.

## Why this is a primitive rather than an app

DueProcess has no product frontend and no domain-specific workflow. A DAO, procurement system, agent executor, escrow, reputation system, treasury, or governance tool can define its own charter and consume `is_valid(instance_id, charter_hash)`.

`ProtectedExecutor` is included only to prove cross-contract composition.

## Consensus mechanism

Leader output is a bounded structured verdict: `SATISFIED`, `NOT_SATISFIED`, `AMBIGUOUS`, or `UNAVAILABLE`. `SATISFIED` must include a short verbatim source excerpt.

The custom validator independently fetches the same public source and re-evaluates the same frozen criterion. It rejects the leader unless the stable verdict agrees. For `SATISFIED`, it also requires the leader's evidence excerpt to occur in the validator's independently fetched page.

This is substantive validation, not format validation.

## Deterministic protocol mechanics

- dependencies point only to earlier steps, making cycles impossible;
- roles bind before start and freeze;
- only the bound role holder can make a procedurally meaningful attempt;
- unauthorized callers cannot grief/invalidate a process;
- authorized out-of-order, too-early, or too-late actions permanently invalidate the instance;
- weak/ambiguous/unavailable evidence is retryable and does not falsely become a breach;
- mandatory-step deadline expiry can be crystallized permissionlessly;
- final validity is pinned to the exact sealed charter hash;
- the consumer contract rejects invalid processes and action replay.

## Reusability proof

The repository includes a second Intelligent Contract, `ProtectedExecutor`, which performs a typed IC-to-IC view call to DueProcess and refuses to execute unless the exact process and charter hash are valid.

The intended live proof runs on the Consensus v0.6 **Studio development preview (chain 61997)** and demonstrates both a valid procedure unlocking the consumer and an invalid procedure being refused by the same consumer.

## Network / fee evidence

The submission evidence targets the Studio development preview rather than stable Studionet. Programmatic clients use `https://studio-dev.genlayer.com/api`; explorer evidence uses `https://explorer-studio-dev.genlayer.com`.

Consensus v0.6 deploy/write transactions are fee-aware. Live evidence records the finalized fee deposit, consumption, and refund rather than assuming a fixed or zero fee.

## Limits

DueProcess does not claim that public evidence is authoritative merely because it exists, and `VALID` does not mean a decision was substantively correct or legally enforceable. It means the frozen procedure represented by the pinned charter was completed according to the contract's evidence, role, ordering, and timing rules.
