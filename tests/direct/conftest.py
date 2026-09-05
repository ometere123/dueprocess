from pathlib import Path
from typing import Any, Callable, Optional

import pytest
from gltest.direct import loader as direct_loader
from gltest.direct.loader import deploy_contract


PINNED_GENVM_BUNDLE = "v0.6.0-rc3"


if __import__("sys").platform == "win32":
    # gltest 0.30.0rc2 keeps fd 0 open on the injected message file until
    # the imported SDK consumes it. Windows cannot unlink that file during
    # loader cleanup, although the injection itself has succeeded.
    _inject_message_to_fd0 = direct_loader._inject_message_to_fd0

    def _windows_safe_message_injection(vm):
        try:
            _inject_message_to_fd0(vm)
        except PermissionError:
            pass

    direct_loader._inject_message_to_fd0 = _windows_safe_message_injection


@pytest.fixture
def direct_deploy(direct_vm) -> Callable[..., Any]:
    """Load the contract's pinned runner from the v0.6 GenVM bundle."""
    def _deploy(
        contract_path: str,
        *args: Any,
        sdk_version: Optional[str] = None,
        **kwargs: Any,
    ) -> Any:
        path = Path(contract_path)
        if not path.is_absolute():
            if path.exists():
                path = path.resolve()
            else:
                for base in (
                    Path.cwd(),
                    Path.cwd() / "contracts",
                    Path.cwd() / "intelligent-contracts",
                ):
                    candidate = base / contract_path
                    if candidate.exists():
                        path = candidate.resolve()
                        break

        return deploy_contract(
            path,
            direct_vm,
            *args,
            sdk_version=sdk_version or PINNED_GENVM_BUNDLE,
            **kwargs,
        )

    return _deploy


@pytest.fixture(autouse=True)
def _enable_pickling_validation(direct_vm):
    direct_vm.check_pickling = True
    original_refresh = direct_vm._refresh_gl_message

    def refresh_with_datetime():
        original_refresh()
        import sys
        gl = sys.modules.get("genlayer.gl")
        if gl is not None and isinstance(getattr(gl, "message_raw", None), dict):
            gl.message_raw["datetime"] = direct_vm._datetime

    direct_vm._refresh_gl_message = refresh_with_datetime
    direct_vm._refresh_gl_message()
    yield
