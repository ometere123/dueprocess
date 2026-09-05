"""Allow only the two confirmed genvm-linter 0.11.1rc2 false positives."""

from __future__ import annotations

import ast
import json
import shutil
import subprocess
import sys
from pathlib import Path


def allowed(path: Path, diagnostic: dict, tree: ast.Module) -> bool:
    code = diagnostic.get("code")
    line = diagnostic.get("line")
    if code == "E014":
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and node.lineno == line:
                return any(
                    isinstance(item, ast.Attribute)
                    and item.attr == "allow"
                    and isinstance(item.value, ast.Attribute)
                    and item.value.attr == "storage"
                    and isinstance(item.value.value, ast.Name)
                    and item.value.value.id == "gl"
                    for item in node.decorator_list
                )
    if code == "E010" and line in (356, 371):
        source = path.read_text(encoding="utf-8")
        return (
            "def inspect_evidence_once" in source
            and "gl.vm.run_nondet_default(leader_fn, validator_fn)" in source
        )
    return False


def main() -> int:
    failed = False
    lint_exe = shutil.which("genvm-lint")
    if lint_exe is None:
        candidate = Path(sys.executable).with_name("genvm-lint.exe")
        if candidate.exists():
            lint_exe = str(candidate)
    if lint_exe is None:
        print("STATIC LINT: genvm-lint executable not found")
        return 1

    for raw_path in sys.argv[1:]:
        path = Path(raw_path)
        result = subprocess.run(
            [lint_exe, "lint", str(path), "--json"],
            text=True,
            capture_output=True,
        )
        try:
            report = json.loads(result.stdout)
        except json.JSONDecodeError:
            print(f"STATIC LINT: invalid JSON output for {path}\n{result.stdout}{result.stderr}")
            return 1
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        diagnostics = report.get("warnings", []) + report.get("errors", [])
        unexpected = [item for item in diagnostics if not allowed(path, item, tree)]
        if unexpected:
            failed = True
            print(f"STATIC LINT: unexpected diagnostics in {path}")
            for item in unexpected:
                print(json.dumps(item, sort_keys=True))
        else:
            for item in diagnostics:
                print(
                    f"ALLOWED RC2: {path}:{item.get('line')}: "
                    f"{item.get('code')} {item.get('msg', '')}"
                )
    if failed:
        return 1
    print("STATIC LINT: PASS WITH CONFIRMED GENVM-LINTER 0.11.1rc2 COMPATIBILITY GAPS")
    print("Allowed: E010 run_nondet_default reachability gap; E014 gl.storage.allow decorator gap")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
