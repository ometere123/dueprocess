# Architecture

DueProcess separates **semantic verification** from **procedural enforcement**.

## State

- `Charter`: reusable procedure definition; mutable only while draft, then hash-sealed.
- `RoleDefinition`: symbolic role such as `RESPONDENT` or `EXECUTOR`.
- `StepDefinition`: required role, public-evidence criterion, dependencies, minimum delay, deadline, mandatory flag.
- `ProcessInstance`: pins one sealed charter hash and concrete role bindings.
- `InstanceStep`: per-process completion state.
- `StepAttempt`: immutable audit record for semantic attempts and deterministic violations.

## State machines

```text
Charter: DRAFT -> SEALED

Process: DRAFT -> ACTIVE -> VALID
                    |
                    +-> INVALID

DRAFT -> ABORTED
```

`VALID`, `INVALID`, and `ABORTED` are terminal.

## Consensus boundary

Only this question is nondeterministic:

> Does this independently fetched public source materially satisfy this exact frozen step criterion?

The leader returns a bounded verdict and grounded excerpt. Validators independently re-fetch and re-evaluate. Stable verdicts must agree, and `SATISFIED` evidence must literally occur in the validator-fetched source.

## Deterministic boundary

The LLM cannot affect:

- charter ownership or immutability;
- role binding and caller authorization;
- dependency completion;
- waiting periods;
- deadlines;
- invalidation;
- mandatory-step completeness;
- charter/final hashes;
- the consumer's `is_valid` gate.

Dependencies may only point to earlier-created steps. The procedure DAG is therefore acyclic by construction.

## Why authorized violations are recorded instead of reverted

An unauthorized caller has no procedural standing and is rejected before mutation.

An authorized role holder acting out of order is different: the attempted premature action is itself relevant process history. DueProcess records `PROCEDURAL_VIOLATION` and terminally invalidates the instance, preventing retroactive laundering by completing the missing predecessor later.

## Composition

`ProtectedExecutor` performs a typed synchronous IC-to-IC view call. It proceeds only if the process is terminal `VALID`, has a final hash, and its pinned charter hash matches the exact hash expected by the consumer. It also prevents action-hash replay.
