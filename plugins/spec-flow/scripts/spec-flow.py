#!/usr/bin/env python3
"""Run one deterministic Spec-Flow harness operation.

Usage: python3 scripts/spec-flow.py --root PROJECT OP --input JSON_FILE
The command reads a JSON object and writes one JSON result to stdout. Errors
are emitted as {"error": {"code", "message", "details"}} with exit status 2.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

from harness.runtime.engine import Engine, EngineError  # noqa: E402
from harness.runtime.contracts import ContractError  # noqa: E402
from harness.runtime.store import StoreError  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, help="consuming project root")
    parser.add_argument(
        "operation",
        choices=("initialize", "digest", "validate", "approve", "gate", "hook-check", "migrate-preview", "migrate-apply", "migrate-resume"),
    )
    parser.add_argument("--input", required=True, help="path to a JSON object containing operation input")
    args = parser.parse_args(argv)
    try:
        input_path = Path(args.input)
        payload = json.loads(input_path.read_text(encoding="utf-8"))
        result = Engine(args.root).dispatch(args.operation, payload)
    except EngineError as exc:
        _emit({"error": {"code": exc.code, "message": str(exc), "details": exc.details}})
        return 2
    except ContractError as exc:
        _emit({"error": {"code": "contract_invalid", "message": str(exc), "details": {}}})
        return 2
    except StoreError as exc:
        _emit({"error": {"code": exc.code, "message": str(exc), "details": {}}})
        return 2
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        _emit({"error": {"code": "invalid_input", "message": str(exc), "details": {}}})
        return 2
    _emit(result)
    return 0


def _emit(value: object) -> None:
    print(json.dumps(value, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    raise SystemExit(main())
