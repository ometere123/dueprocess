# Reviewer Demo

The strongest review path proves **semantic consensus + deterministic invalidation + real cross-contract consumption**.

## Deploy

1. Deploy `contracts/dueprocess.py`.
2. Deploy `contracts/protected_executor.py` with the finalized DueProcess address.
3. Record both finalized addresses and transaction links in `DEPLOYMENT.md`.

## Create one charter

Roles:

- `NOTICE_AUTHORITY`
- `RESPONDENT`
- `DECISION_MAKER`
- `EXECUTOR`

Mandatory steps:

1. Publish notice.
2. Opportunity to respond — depends on 1 and has a short demo wait.
3. Publish decision — depends on 2.
4. Execute decision — depends on 3 and has another short demo wait.

Use public pages that StudioNet validators can independently fetch. Seal the charter and record its `definition_hash`.

## Process A — valid

1. Open process A and bind all roles.
2. Start.
3. Submit notice evidence; verify `SATISFIED`.
4. Wait, then submit response evidence; verify `SATISFIED`.
5. Submit decision evidence; verify `SATISFIED`.
6. Wait, then submit execution evidence; verify `SATISFIED`.
7. Finalize; verify `VALID` and `is_valid(A, charter_hash) == true`.
8. Call `ProtectedExecutor.execute(A, charter_hash, action_hash)` and verify success.

## Process B — invalid

1. Open process B against the same charter and bind roles.
2. Start.
3. Complete notice.
4. Have the bound `DECISION_MAKER` attempt step 3 before step 2 is complete.
5. Verify `PROCEDURAL_VIOLATION / DEPENDENCY_MISSING` and terminal `INVALID`.
6. Verify `is_valid(B, charter_hash) == false`.
7. Call `ProtectedExecutor.execute(B, charter_hash, second_action_hash)` and verify refusal.

## Consensus proof

Capture a finalized Studio transaction for at least one semantic `SATISFIED` step showing validator consensus. Pair it with the Direct Mode adversarial test where the leader claims `SATISFIED` while the independent validator sees `NOT_SATISFIED` and rejects the forged result.

This single demo demonstrates why DueProcess is not just another classifier: semantic judgment is only one component inside a deterministic procedural protocol whose result is actually consumed by another Intelligent Contract.
