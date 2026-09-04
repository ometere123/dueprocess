"""High-signal StudioNet lifecycle checks for DueProcess.

Direct Mode covers deterministic/adversarial branches cheaply. This suite deploys
both Intelligent Contracts on StudioNet, exercises real semantic consensus over
public HTTPS fixtures, and proves a second IC consumes DueProcess validity.
"""

from gltest import get_contract_factory, get_default_account
from gltest.assertions import tx_execution_failed, tx_execution_succeeded


DUEPROCESS = "dueprocess.py"
PROTECTED_EXECUTOR = "protected_executor.py"
TX_KW = {"consensus_max_rotations": 3, "wait_interval": 10000, "wait_retries": 30}

# Pin fixture content to an immutable repository commit so every validator sees
# the same reviewer evidence even if main changes later.
FIXTURE_COMMIT = "a156a47b0f5f00ff65d8b65ad8d42ed1b3a691f2"
RAW = f"https://raw.githubusercontent.com/ometere123/dueprocess/{FIXTURE_COMMIT}/fixtures"
NOTICE_URL = f"{RAW}/notice.txt"
RESPONSE_URL = f"{RAW}/response.txt"
DECISION_URL = f"{RAW}/decision.txt"
EXECUTION_URL = f"{RAW}/execution.txt"


def assert_success(receipt):
    assert tx_execution_succeeded(receipt), receipt


def deploy_dueprocess():
    factory = get_contract_factory(contract_file_path=DUEPROCESS)
    contract = factory.deploy(
        account=get_default_account(),
        consensus_max_rotations=3,
        wait_interval=10000,
        wait_retries=30,
    )
    assert contract.address
    return contract


def create_demo_charter(contract):
    account = get_default_account()
    assert_success(contract.create_charter(args=[
        "Public Decision Procedure",
        "A reusable four-step notice, response, decision, and execution procedure.",
    ]).transact(account=account, **TX_KW))

    charter_id = 1
    roles = [
        ("NOTICE_AUTHORITY", 1),
        ("RESPONDENT", 2),
        ("DECISION_MAKER", 3),
        ("EXECUTOR", 4),
    ]
    for label, expected_id in roles:
        receipt = contract.add_role(args=[charter_id, label]).transact(account=account, **TX_KW)
        assert_success(receipt)
        assert contract.get_role(args=[expected_id]).call()["label"] == label

    steps = [
        (
            "Publish notice",
            1,
            "The public source establishes that formal notice of Proposal DP-7 was published for affected participants.",
            0,
            1800,
        ),
        (
            "Opportunity to respond",
            2,
            "The public source establishes that the affected participant submitted a response to Proposal DP-7.",
            0,
            1800,
        ),
        (
            "Publish decision",
            3,
            "The public source establishes that the designated decision maker published the final decision for Proposal DP-7.",
            0,
            1800,
        ),
        (
            "Execute decision",
            4,
            "The public source establishes that the designated executor carried out the finalized decision for Proposal DP-7.",
            0,
            1800,
        ),
    ]
    for label, role_id, criterion, min_delay, deadline in steps:
        assert_success(contract.add_step(args=[
            charter_id, label, role_id, criterion, True, min_delay, deadline,
        ]).transact(account=account, **TX_KW))

    assert_success(contract.add_dependency(args=[2, 1]).transact(account=account, **TX_KW))
    assert_success(contract.add_dependency(args=[3, 2]).transact(account=account, **TX_KW))
    assert_success(contract.add_dependency(args=[4, 3]).transact(account=account, **TX_KW))
    assert_success(contract.seal_charter(args=[charter_id]).transact(account=account, **TX_KW))

    charter = contract.get_charter(args=[charter_id]).call()
    assert charter["status_name"] == "SEALED"
    assert len(charter["definition_hash"]) == 64
    return charter_id, charter["definition_hash"]


def open_and_bind(contract, charter_id):
    account = get_default_account()
    assert_success(contract.open_process(args=[charter_id]).transact(account=account, **TX_KW))
    # Fresh deployment starts at process id 1; subsequent call increments.
    current = contract.next_process_id.call() if hasattr(contract, "next_process_id") else None
    process_id = int(current) - 1 if current is not None else 1
    for role_id in (1, 2, 3, 4):
        assert_success(contract.bind_role(args=[process_id, role_id, account.address]).transact(account=account, **TX_KW))
    assert_success(contract.start_process(args=[process_id]).transact(account=account, **TX_KW))
    return process_id


def test_real_consensus_validity_and_cross_contract_gate():
    account = get_default_account()
    due = deploy_dueprocess()
    charter_id, charter_hash = create_demo_charter(due)

    valid_id = open_and_bind(due, charter_id)
    for step_id, url in ((1, NOTICE_URL), (2, RESPONSE_URL), (3, DECISION_URL), (4, EXECUTION_URL)):
        receipt = due.submit_step(args=[valid_id, step_id, url]).transact(account=account, **TX_KW)
        assert_success(receipt)
        attempt_id = due.get_instance_step(args=[valid_id, step_id]).call()["last_attempt_id"]
        attempt = due.get_attempt(args=[attempt_id]).call()
        assert attempt["verdict_name"] == "SATISFIED"
        assert attempt["evidence"]

    assert_success(due.finalize_process(args=[valid_id]).transact(account=account, **TX_KW))
    valid = due.get_process(args=[valid_id]).call()
    assert valid["status_name"] == "VALID"
    assert due.is_valid(args=[valid_id, charter_hash]).call() is True

    consumer_factory = get_contract_factory(contract_file_path=PROTECTED_EXECUTOR)
    consumer = consumer_factory.deploy(
        args=[due.address],
        account=account,
        consensus_max_rotations=3,
        wait_interval=10000,
        wait_retries=30,
    )
    assert consumer.address

    good_action = "11" * 32
    gate = consumer.execute(args=[valid_id, charter_hash, good_action]).transact(account=account, **TX_KW)
    assert_success(gate)
    assert consumer.was_executed(args=[good_action]).call() is True

    # A second process deliberately attempts the decision before notice/response.
    assert_success(due.open_process(args=[charter_id]).transact(account=account, **TX_KW))
    invalid_id = valid_id + 1
    for role_id in (1, 2, 3, 4):
        assert_success(due.bind_role(args=[invalid_id, role_id, account.address]).transact(account=account, **TX_KW))
    assert_success(due.start_process(args=[invalid_id]).transact(account=account, **TX_KW))

    violation = due.submit_step(args=[invalid_id, 3, DECISION_URL]).transact(account=account, **TX_KW)
    assert_success(violation)
    invalid = due.get_process(args=[invalid_id]).call()
    assert invalid["status_name"] == "INVALID"
    assert invalid["invalid_code"] == "DEPENDENCY_MISSING"
    assert due.is_valid(args=[invalid_id, charter_hash]).call() is False

    bad_action = "22" * 32
    denied = consumer.execute(args=[invalid_id, charter_hash, bad_action]).transact(account=account, **TX_KW)
    assert tx_execution_failed(denied), denied
    assert consumer.was_executed(args=[bad_action]).call() is False
