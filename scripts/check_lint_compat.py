"""Run genvm-lint while isolating documented Studio-dev tool mismatches."""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path


KNOWN = (
    re.compile(r"gl\.nondet\.\* call in 'inspect_evidence_once' not reachable from equivalence principle block"),
    re.compile(r"Failed to load SDK: .*runners/py-genlayer/5j/.*\.tar.*not found"),
)


def main() -> int:
    lint = shutil.which("genvm-lint") or str(Path(sys.executable).with_name("genvm-lint.exe"))
    failures = []
    for path in sys.argv[1:]:
        result = subprocess.run(
            [lint, "check", path],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        print(result.stdout, end="")
        unexpected = [
            line for line in result.stdout.splitlines()
            if (line.strip().startswith("line ") or "Failed to load SDK:" in line)
            and not any(pattern.search(line) for pattern in KNOWN)
        ]
        if result.returncode and unexpected:
            failures.extend(f"{path}: {line}" for line in unexpected)
    if failures:
        print("Unexpected genvm-lint diagnostics:")
        print("\n".join(failures))
        return 1
    print("Known genvm-lint Studio-dev compatibility diagnostics isolated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
