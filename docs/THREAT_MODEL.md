# Threat Model

DueProcess protects the integrity of a frozen public procedure, not the substantive correctness of its outcome.

## Malicious leader

A leader may fabricate `SATISFIED`, invent evidence, or suppress ambiguity. The custom validator independently fetches and re-evaluates the same source. The verdict must agree, and a `SATISFIED` excerpt must be present in the validator's independently fetched page.

## Prompt-injection source

Public evidence is hostile data. The task prompt explicitly prevents source text from redefining the criterion or protocol, and deterministic state-machine checks occur outside the nondeterministic block. Common instruction-like charter criteria are rejected before sealing.

## Unauthorized griefing

An outsider may try to submit a later step early to invalidate someone else's process. This fails: unauthorized callers revert before an attempt exists. Only the address bound to the step's required role can create a procedurally meaningful attempt.

## Authorized premature action

This is exactly the behaviour the primitive is intended to detect. Missing predecessors, early execution, and late execution are deterministic violations and permanently invalidate the process.

## Mid-process actor substitution

Role bindings freeze at `start_process`.

## Rule substitution

Charters become immutable at `seal_charter`, and every process pins the resulting `definition_hash`. Consumers pin that same hash.

## Endpoint outage or weak evidence

`UNAVAILABLE`, `AMBIGUOUS`, and `NOT_SATISFIED` do not automatically invalidate a process. They leave the step pending for retry. An outage is not treated as proof of non-compliance.

## Deadline laundering

Anyone may call `expire_process` after a mandatory deadline. An incomplete mandatory step then produces terminal `INVALID`, preventing later backfill.

## Consumer replay

`ProtectedExecutor` records consumed action hashes and refuses duplicate execution.

## Explicit non-goals

DueProcess does not establish source authority, legal enforceability, substantive fairness, private evidence, or completeness of a charter. A `VALID` result means the exact pinned procedure represented by the charter was completed according to its encoded role, evidence, ordering, and timing requirements.
