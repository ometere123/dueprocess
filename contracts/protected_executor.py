# v0.1.0
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *
from dataclasses import dataclass


@gl.contract_interface
class IDueProcess:
    class View:
        def is_valid(self, instance_id: u256, expected_charter_hash: str) -> bool: ...
    class Write:
        pass


@allow_storage
@dataclass
class ExecutionReceipt:
    caller: Address
    instance_id: u256
    charter_hash: str
    action_hash: str


class ProtectedExecutor(gl.Contract):
    """Minimal consumer proving that another IC can gate execution on DueProcess validity."""

    dueprocess_address: Address
    executions: TreeMap[str, ExecutionReceipt]
    execution_count: u256

    def __init__(self, dueprocess_address: Address):
        self.dueprocess_address = dueprocess_address
        self.execution_count = u256(0)

    @gl.public.write
    def execute(self, instance_id: u256, expected_charter_hash: str, action_hash: str) -> None:
        action_hash = str(action_hash).strip().lower()
        if len(action_hash) != 64:
            raise gl.vm.UserError("EXPECTED: action_hash must be a 32-byte hex digest")
        for char in action_hash:
            if char not in "0123456789abcdef":
                raise gl.vm.UserError("EXPECTED: action_hash must be lowercase hex")

        dueprocess = IDueProcess(self.dueprocess_address)
        if not dueprocess.view().is_valid(instance_id, expected_charter_hash):
            raise gl.vm.UserError("EXPECTED: due process requirement is not valid")
        if action_hash in self.executions:
            raise gl.vm.UserError("EXPECTED: action was already executed")

        self.executions[action_hash] = ExecutionReceipt(
            caller=gl.message.sender_address,
            instance_id=instance_id,
            charter_hash=str(expected_charter_hash),
            action_hash=action_hash,
        )
        self.execution_count = u256(int(self.execution_count) + 1)

    @gl.public.view
    def was_executed(self, action_hash: str) -> bool:
        return str(action_hash).strip().lower() in self.executions

    @gl.public.view
    def get_execution(self, action_hash: str) -> dict:
        key = str(action_hash).strip().lower()
        if key not in self.executions:
            raise gl.vm.UserError("EXPECTED: unknown execution")
        item = self.executions[key]
        return {
            "caller": str(item.caller),
            "instance_id": int(item.instance_id),
            "charter_hash": str(item.charter_hash),
            "action_hash": str(item.action_hash),
        }
