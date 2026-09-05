"""Repository-level checks that do not require a running GenLayer Studio."""

from pathlib import Path
import ast
import sys

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = [ROOT / "contracts" / "dueprocess.py", ROOT / "contracts" / "protected_executor.py"]
NETWORK_CONFIG = ROOT / "gltest.config.yaml"

REQUIRED_DUEPROCESS = [
    "run_nondet_default",
    "inspect_evidence_once",
    "seal_charter",
    "submit_step",
    "expire_process",
    "finalize_process",
    "is_valid",
    "definition_hash",
    "PROCEDURAL_VIOLATION",
]
REQUIRED_CONSUMER = ["@gl.contract.interface", "is_valid", "dueprocess.view().is_valid", "action was already executed"]
REQUIRED_STUDIO_DEV = ["studio_devnet:"]


def check_file(path: Path, required: list[str]) -> list[str]:
    errors = []
    text = path.read_text(encoding="utf-8")
    try:
        ast.parse(text, filename=str(path))
    except SyntaxError as exc:
        errors.append(f"{path.name}: syntax error: {exc}")
    for needle in required:
        if needle not in text:
            errors.append(f"{path.name}: missing required marker {needle!r}")
    return errors


def check_event_topics(path: Path) -> list[str]:
    errors = []
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        is_event = any(
            isinstance(base, ast.Attribute)
            and isinstance(base.value, ast.Attribute)
            and isinstance(base.value.value, ast.Name)
            and base.value.value.id == "gl"
            and base.value.attr == "chain"
            and base.attr == "Event"
            for base in node.bases
        )
        if not is_event:
            continue
        init = next((item for item in node.body if isinstance(item, ast.FunctionDef) and item.name == "__init__"), None)
        indexed = len(init.args.posonlyargs) - 1 if init else 0
        if 1 + indexed > 4:
            errors.append(f"{node.name}: event topic count exceeds GenVM limit ({1 + indexed})")
        if node.name == "StepAttempted" and indexed != 3:
            errors.append(f"StepAttempted: expected exactly 3 indexed fields, found {indexed}")
    return errors


def main() -> int:
    errors = []
    errors.extend(check_file(CONTRACTS[0], REQUIRED_DUEPROCESS))
    errors.extend(check_file(CONTRACTS[1], REQUIRED_CONSUMER))
    errors.extend(check_event_topics(CONTRACTS[0]))

    due = CONTRACTS[0].read_text(encoding="utf-8")
    if "self." in due[due.find("def semantic_check"):due.find("class DueProcess")]:
        errors.append("semantic_check unexpectedly references contract storage")
    if "gl.get_contract_at" in due[due.find("def semantic_check"):due.find("class DueProcess")]:
        errors.append("semantic_check unexpectedly performs a cross-contract call")

    network = NETWORK_CONFIG.read_text(encoding="utf-8")
    for needle in REQUIRED_STUDIO_DEV:
        if needle not in network:
            errors.append(f"gltest.config.yaml: missing Studio-dev marker {needle!r}")
    if "https://studio.genlayer.com/api" in network:
        errors.append("gltest.config.yaml still contains the stable Studionet RPC")

    if errors:
        for error in errors:
            print("FAIL", error)
        return 1
    print("PASS: syntax, architectural, and Studio-dev target preflight checks succeeded")
    return 0


if __name__ == "__main__":
    sys.exit(main())
