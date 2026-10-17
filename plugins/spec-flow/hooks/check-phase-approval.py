#!/usr/bin/env python3
"""Guard supported Claude Code Edit, MultiEdit, and Write operations via Engine."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any, List

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

from harness.runtime.engine import Engine, EngineError  # noqa: E402


def deny(reason: str) -> None:
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                               "permissionDecisionReason": reason}}, ensure_ascii=False))


def supported_paths(event: Any) -> List[str] | None:
    if not isinstance(event, dict):
        raise ValueError("hook event must be a JSON object")
    name = event.get("tool_name", event.get("name"))
    if name not in {"Edit", "MultiEdit", "Write"}:
        return None
    value = event.get("tool_input")
    if not isinstance(value, dict):
        raise ValueError("supported write event has no object tool_input")
    paths = value.get("file_path")
    if not isinstance(paths, str) or not paths.strip():
        raise ValueError("{} event must identify a nonempty file_path".format(name))
    return [paths]


def main() -> int:
    try:
        event = json.load(sys.stdin)
        raw_paths = supported_paths(event)
        if raw_paths is None:
            return 0
    except (json.JSONDecodeError, UnicodeDecodeError, ValueError) as exc:
        deny("Cannot validate supported write: {}".format(exc))
        return 0

    cwd = Path(str(event.get("cwd") or Path.cwd())).resolve()
    try:
        root_text = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=cwd, check=True,
                                   capture_output=True, text=True, timeout=2).stdout.strip()
        root = Path(root_text).resolve()
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        root = None

    if root is None:
        candidates = [cwd, *cwd.parents]
        root = next((candidate for candidate in candidates
                     if (candidate / ".spec-flow" / "config.json").is_file() or (candidate / ".specs").is_dir()), None)
        if root is None:
            return 0

    paths: List[str] = []
    try:
        for value in raw_paths:
            target = Path(value)
            absolute = (target if target.is_absolute() else cwd / target).resolve()
            paths.append(absolute.relative_to(root).as_posix())
    except (OSError, ValueError) as exc:
        deny("Cannot validate supported write path inside the Git project: {}".format(exc))
        return 0

    configured = (root / ".spec-flow" / "config.json").is_file()
    legacy = (root / ".specs").is_dir() and any((root / ".specs").glob("[0-9][0-9][0-9]-*"))
    canonical_target = any(path.startswith(".specs/") and path.split("/")[-1] in {
        "constitution.md", "architecture.md", "structure.md", "infrastructure.md", "roadmap.md", "spec.md", "plan.md", "tasks.md"
    } for path in paths)
    if not configured and not legacy and not canonical_target:
        # The plugin hook is optional and must not gate unrelated repositories.
        return 0

    try:
        result = Engine(root).dispatch("hook-check", {"paths": paths})
    except EngineError as exc:
        deny("{}: {}".format(exc.code, str(exc)))
        return 0
    except Exception as exc:  # fail closed for an unexpected validator/runtime error
        deny("hook validator failed closed: {}".format(exc))
        return 0
    if result.get("allowed") is not True:
        deny("Spec-Flow did not authorize this supported write.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
