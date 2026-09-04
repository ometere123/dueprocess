"""Read-only guard for the DueProcess Studio-dev deployment target.

No wallet or secret is required. The script refuses to pass unless the canonical
Studio-dev RPC reports chain ID 61997.
"""

from __future__ import annotations

import json
import sys
from urllib.request import Request, urlopen

RPC = "https://studio-dev.genlayer.com/api"
EXPECTED_CHAIN_ID = 61997
EXPLORER = "https://explorer-studio-dev.genlayer.com"


def rpc(method: str, params: list | None = None):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params or []}).encode()
    request = Request(RPC, data=body, headers={"Content-Type": "application/json"}, method="POST")
    with urlopen(request, timeout=20) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if "error" in payload:
        raise RuntimeError(f"RPC {method} failed: {payload['error']}")
    return payload.get("result")


def parse_chain_id(value) -> int:
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        return int(value, 0)
    raise ValueError(f"unexpected eth_chainId value: {value!r}")


def main() -> int:
    try:
        raw_chain_id = rpc("eth_chainId")
        chain_id = parse_chain_id(raw_chain_id)
    except Exception as exc:
        print(f"FAIL: unable to verify Studio-dev RPC: {exc}", file=sys.stderr)
        return 1

    if chain_id != EXPECTED_CHAIN_ID:
        print(
            f"FAIL: {RPC} reported chain {chain_id}; expected {EXPECTED_CHAIN_ID}. "
            "Do not sign or deploy until this is resolved.",
            file=sys.stderr,
        )
        return 2

    print("PASS: Studio-dev network identity verified")
    print(f"RPC: {RPC}")
    print(f"Chain ID: {chain_id}")
    print(f"Explorer: {EXPLORER}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
