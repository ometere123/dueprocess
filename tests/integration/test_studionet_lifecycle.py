"""High-signal Studio-dev lifecycle checks for DueProcess.

Direct Mode covers deterministic/adversarial branches cheaply. This suite deploys
both Intelligent Contracts on the Consensus v0.6 Studio development preview
(chain 61997), exercises real semantic consensus over public HTTPS fixtures,
and proves a second IC consumes DueProcess validity.

Every deploy/write uses a live v0.6 fee estimate and waits through finalization.
When this test is run with --fee-profile, gltest records finalized consumption and
builds the measured profile that should be used for later deployment/submission.
"""

import os

from gltest import get_contract_factory, get_default_account
from gltest.assertions import tx_execution_failed, tx_execution_succeeded
from gltest.clients import get_gl_client


DUEPROCESS = "dueprocess.py"
PROTECTED_EXECUTOR = "protected_executor.py"
TX_KW = {
    "consensus_max_rotations": 3,
    "wait_until": "finalized",
    "wait_interval": 10000,
    "wait_retries": 60,
}

# Bootstrap allocation used only to fund the profiling transactions. The live
# network supplies current prices/caps and returns the actual distribution and
# feeValue. The generated fee-profile.json replaces this bootstrap suggestion
# for repeat deployments and writes.
FEE_ESTIMATE_OPTIONS = {
    "leaderTimeunitsAllocation": 100,
    "validatorTimeunitsAllocation": 200,
    "totalMessageFees": 0,
    "rotations": [1],
}

# Pin evidence to an immutable repository commit so all validators inspect the
# exact same public bytes even if main changes later.
FIXTURE_COMMIT = "a156a47b0f5f00ff65d8b65ad8d42ed1b3a691f2"
RAW = f"https://raw.githubusercontent.com/ometere123/dueprocess/{FIXTURE_COMMIT}/fixtures"
NOTICE_URL = f"{RAW}/notice.txt"
RESPONSE_URL = f"{RAW}/response.txt"
DECISION_URL = f"{RAW}/decision.txt"
EXECUTION_URL = f"{RAW}/execution.txt"


def transaction_fee_preset():
    estimate = get_gl_client().estimate_transaction_fees(FEE_ESTIMATE_OPTIONS)
    return {
        "distribution": estimate["distribution"],
        "feeValue": estimate["feeValue"],
    }


def tx(function):
    return function.transact(fees=transaction_fee_preset(), **TX_KW)


def assert_success(receipt):
    assert tx_execution_succeeded(receipt), receipt


def deploy_dueprocess():
    factory = get_contract_factory(contract_file_path=DUEPROCESS)
    existing = os.environ.get("CANONICAL_DUEPROCESS_ADDRESS")
    if existing:
        return factory.build_contract(existing, account=get_default_account())
    contract = factory.deploy(
        account=get_default_account(),
        fees=transaction_fee_preset(),
        consensus_max_rotations=3,
        wait_until="finalized",
        wait_interval=10000,
        wait_retries=60,
    )
    assert contract.address
    return contract


def create_demo_charter(contract):
    charter_id = 1
    if not os.environ.get("CANONICAL_DUEPROCESS_ADDRESS"):
        assert_success(tx(contract.create_charter(args=[
            "Public Decision Procedure",
            "A reusable four-step notice, response, decision, and execution procedure.",
        ])))
    else:
        existing = contract.get_charter(args=[charter_id]).call()
        assert existing["title"] == "Demo Charter"
        assert existing["purpose"] == "Procedural validity demonstration"
    for label, expected_id in (
        ("NOTICE_AUTHORITY", 1),
        ("RESPONDENT", 2),
        ("DECISION_MAKER", 3),
        ("EXECUTOR", 4),
    ):
        assert_success(tx(contract.add_role(args=[charter_id, label])))
        assert contract.get_role(args=[expected_id]).call()["label"] == label

    for label, role_id, criterion in (
        (
            "Publish notice",
            1,
            "The public source establishes that formal notice of Proposal DP-7 was published for affected participants.",
        ),
        (
            "Opportunity to respond",
            2,
            "The public source establishes that the affected participant submitted a response to Proposal DP-7.",
        ),
        (
            "Publish decision",
            3,
            "The public source establishes that the designated decision maker published the final decision for Proposal DP-7.",
        ),
        (
            "Execute decision",
            4,
            "The public source establishes that the designated executor carried out the finalized decision for Proposal DP-7.",
        ),
    ):
        assert_success(tx(contract.add_step(args=[
            charter_id, label, role_id, criterion, True, 0, 1800,
        ])))

    assert_success(tx(contract.add_dependency(args=[2, 1])))
    assert_success(tx(contract.add_dependency(args=[3, 2])))
    assert_success(tx(contract.add_dependency(args=[4, 3])))
    assert_success(tx(contract.seal_charter(args=[charter_id])))

    charter = contract.get_charter(args=[charter_id]).call()
    assert charter["status_name"] == "SEALED"
    assert len(charter["definition_hash"]) == 64
    return charter_id, charter["definition_hash"]


def open_and_bind(contract, charter_id, process_id):
    account = get_default_account()
    assert_success(tx(contract.open_process(args=[charter_id])))
    process = contract.get_process(args=[process_id]).call()
    assert process["status_name"] == "DRAFT"
    for role_id in (1, 2, 3, 4):
        assert_success(tx(contract.bind_role(args=[process_id, role_id, account.address])))
    assert_success(tx(contract.start_process(args=[process_id])))
    return process_id


def test_real_consensus_validity_and_cross_contract_gate():
    account = get_default_account()
    due = deploy_dueprocess()
    charter_id, charter_hash = create_demo_charter(due)

    valid_id = open_and_bind(due, charter_id, 1)
    for step_id, url in ((1, NOTICE_URL), (2, RESPONSE_URL), (3, DECISION_URL), (4, EXECUTION_URL)):
        receipt = tx(due.submit_step(args=[valid_id, step_id, url]))
        assert_success(receipt)
        state = due.get_instance_step(args=[valid_id, step_id]).call()
        attempt = due.get_attempt(args=[state["last_attempt_id"]]).call()
        assert attempt["verdict_name"] == "SATISFIED"
        assert attempt["evidence"]

    assert_success(tx(due.finalize_process(args=[valid_id])))
    valid = due.get_process(args=[valid_id]).call()
    assert valid["status_name"] == "VALID"
    assert due.is_valid(args=[valid_id, charter_hash]).call() is True

    consumer_factory = get_contract_factory(contract_file_path=PROTECTED_EXECUTOR)
    existing_consumer = os.environ.get("CANONICAL_PROTECTED_EXECUTOR_ADDRESS")
    if existing_consumer:
        consumer = consumer_factory.build_contract(existing_consumer, account=account)
    else:
        consumer = consumer_factory.deploy(
            args=[due.address],
            account=account,
            fees=transaction_fee_preset(),
            consensus_max_rotations=3,
            wait_until="finalized",
            wait_interval=10000,
            wait_retries=60,
        )
    assert consumer.address

    good_action = "11" * 32
    assert_success(tx(consumer.execute(args=[valid_id, charter_hash, good_action])))
    assert consumer.was_executed(args=[good_action]).call() is True

    invalid_id = open_and_bind(due, charter_id, 2)
    # The bound decision-maker deliberately attempts step 3 before steps 1 and 2.
    violation = tx(due.submit_step(args=[invalid_id, 3, DECISION_URL]))
    assert_success(violation)
    invalid = due.get_process(args=[invalid_id]).call()
    assert invalid["status_name"] == "INVALID"
    assert invalid["invalid_code"] == "DEPENDENCY_MISSING"
    assert due.is_valid(args=[invalid_id, charter_hash]).call() is False

    bad_action = "22" * 32
    denied = tx(consumer.execute(args=[invalid_id, charter_hash, bad_action]))
    assert tx_execution_failed(denied), denied
    assert consumer.was_executed(args=[bad_action]).call() is False
