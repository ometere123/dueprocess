# DueProcess

**Consensus-backed procedural validity for GenLayer Intelligent Contracts.**

DueProcess is a standalone reusable Intelligent Contract primitive for processes where *how* a decision is reached matters independently of the decision itself.

It does not decide whether a governance outcome, procurement award, disciplinary ruling, agent action, or other decision was substantively correct. It answers a narrower and composable question:

> Did the declared actors complete the required public steps, in the required order, after the required waiting periods, before the required deadlines, with public evidence that independently satisfies each frozen criterion?

That distinction matters. A decision can be substantively reasonable and still be procedurally invalid.

## Why GenLayer

Ordinary smart contracts can enforce timestamps, addresses, dependencies, and hashes, but they cannot reliably determine whether a public notice, response record, decision publication, or execution record *semantically satisfies* a natural-language procedural requirement.

DueProcess splits those responsibilities:

- **GenLayer consensus** verifies only the semantic evidence question for a frozen step.
- **Deterministic contract logic** enforces role authority, dependency order, waiting periods, deadlines, invalidation, immutability, and final validity.
- **Consumer contracts** can gate consequential actions on `is_valid(instance_id, expected_charter_hash)`.

## Protocol model

A reusable procedure is defined as a **sealed charter**:

```text
Charter
├── Roles
│   ├── NOTICE_AUTHORITY
│   ├── RESPONDENT
│   ├── DECISION_MAKER
│   └── EXECUTOR
└── Steps
    ├── 1. Publish notice
    ├── 2. Opportunity to respond      depends on 1; wait >= 48h
    ├── 3. Publish decision             depends on 2
    └── 4. Execute decision             depends on 3; wait >= 1h
```

Each step freezes its required role, natural-language evidence criterion, mandatory/optional status, predecessor dependencies, minimum delay, and optional deadline. Dependencies may only point to earlier steps, making cycles impossible by construction.

Once sealed, the charter receives a `definition_hash`. A process instance pins that exact hash forever.

## Consensus design

`submit_step` fetches public HTTPS evidence and asks the leader for a bounded result: `SATISFIED`, `NOT_SATISFIED`, `AMBIGUOUS`, or `UNAVAILABLE`. For `SATISFIED`, the result must include a short verbatim excerpt from the fetched source.

The custom `run_nondet_unsafe` validator does **not** trust the leader result. Every validator independently fetches the same public source, re-runs the frozen criterion evaluation, requires the stable verdict to match, and verifies a `SATISFIED` excerpt is literally present in the independently fetched source.

The LLM never controls role authorization, dependency order, waiting periods, deadlines, terminal invalidation, or final validity.

## Procedural violations

Weak, ambiguous, or unavailable evidence is retryable and does not by itself invalidate the process. But when the **authorized role holder** acts before a required predecessor, before a waiting period has elapsed, or after a frozen deadline, DueProcess records a `PROCEDURAL_VIOLATION` and permanently moves the process to `INVALID`.

Unauthorized callers revert before they can create a meaningful attempt, preventing grief invalidation.

## Cross-contract reuse

`contracts/protected_executor.py` is intentionally tiny. It proves the primitive boundary: another Intelligent Contract performs a typed view call to `is_valid(instance_id, expected_charter_hash)` and refuses its own state transition unless the procedure is valid.

A real consumer can be a treasury, governance executor, escrow release, reputation updater, agent permission gate, or other IC. The consumer pins the charter hash, so validity under a different procedure cannot be substituted.

## Public interface

Important writes:

```text
create_charter(title, purpose)
add_role(charter_id, label)
add_step(charter_id, label, role_id, criterion, mandatory, min_delay, deadline)
add_dependency(step_id, predecessor_step_id)
seal_charter(charter_id)
open_process(charter_id)
bind_role(instance_id, role_id, actor)
start_process(instance_id)
submit_step(instance_id, step_id, evidence_url)
expire_process(instance_id)
finalize_process(instance_id)
```

Important reads include `get_charter`, `get_step`, `get_process`, `get_instance_step`, `get_attempt`, `current_charter_hash`, and `is_valid`.

## Security boundaries

DueProcess deliberately does **not** claim that a public source is globally authoritative merely because it is public; that a procedurally valid outcome is substantively correct; that private evidence can be verified; or that a failed evidence URL proves non-compliance. Consumers should only trust charter hashes whose procedure and evidence surface they actually accept.

See `docs/THREAT_MODEL.md` for the complete adversarial model.

## Live target: Studio development preview

The submission proof targets GenLayer's Consensus v0.6 Studio development preview, not stable Studionet.

```text
Chain ID:      61997
Canonical RPC: https://studio-dev.genlayer.com/api
Web UI:        https://studio-dev.genlayer.com
Browser alias: https://studio-next.genlayer.com
Explorer:      https://explorer-studio-dev.genlayer.com
CLI alias:     studio-dev
Currency:      GEN
```

The preview is a separate chain/deployment from stable Studionet (`61999`). Do not point the stable `studionet` preset at the preview RPC.

Consensus v0.6 deploys and writes are fee-aware. Use live estimation through the matching RC tooling rather than hardcoding a fee value, and record finalized deposit/consumption/refund data for the submission proof. See `docs/STUDIO_DEV_MIGRATION.md`.

## Repository layout

```text
contracts/
  dueprocess.py
  protected_executor.py

tests/direct/
  test_dueprocess.py

tests/integration/
  test_studionet_lifecycle.py  # now configured for Studio-dev through gltest.config.yaml

docs/
  ARCHITECTURE.md
  THREAT_MODEL.md
  REVIEWER_DEMO.md
  STUDIO_DEV_MIGRATION.md

scripts/
  preflight.py
  check_studio_dev.py
```

There is intentionally **no frontend**. This repository targets the standalone **Intelligent Contracts** category, not Projects.

## Local verification

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-test.txt

genvm-lint check contracts/dueprocess.py
genvm-lint check contracts/protected_executor.py
pytest tests/direct -v
python scripts/preflight.py
```

Before any live signing/deployment, verify the target chain without a wallet:

```bash
python scripts/check_studio_dev.py
```

It must report chain ID `61997`.

Before submission, complete the live lifecycle in `docs/REVIEWER_DEMO.md` and record finalized deployment/transaction/fee evidence in `DEPLOYMENT.md`.

## License

MIT.
