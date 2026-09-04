import pytest


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
