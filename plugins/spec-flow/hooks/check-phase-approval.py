#!/usr/bin/env python3
"""Block writes to gated .specs artifacts until their predecessor is approved."""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Any


def emit_deny(reason: str) -> None:
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            }
        )
    )


def patch_paths(command: str) -> list[str]:
    """Return paths named by Codex apply_patch directives in the command."""
    paths: list[str] = []
    for line in command.splitlines():
        match = re.match(r"^\*\*\*\s+(?:Update|Add|Delete) File:\s*(.+?)\s*$", line)
        if match:
            paths.append(match.group(1))
            continue
        match = re.match(r"^\*\*\*\s+Move to:\s*(.+?)\s*$", line)
        if match:
            paths.append(match.group(1))
    return paths


def gate_predecessor(target: str, cwd: Path) -> tuple[Path, str] | None:
    """Map a gated output path to its required predecessor artifact."""
    normalized = target.replace("\\", os.sep)
    target_path = Path(normalized)
    absolute = Path(os.path.abspath(target_path if target_path.is_absolute() else cwd / target_path))
    parts = absolute.parts
    try:
        specs_index = parts.index(".specs")
    except ValueError:
        return None

    repo_root = Path(*parts[:specs_index])
    relative = parts[specs_index + 1 :]
    if len(relative) == 2 and relative[1] == "spec.md":
        return repo_root / ".specs" / "constitution.md", "spec.md"
    if len(relative) == 2 and relative[1] == "plan.md":
        return repo_root / ".specs" / relative[0] / "spec.md", "plan.md"
    if len(relative) == 2 and relative[1] == "tasks.md":
        return repo_root / ".specs" / relative[0] / "plan.md", "tasks.md"
    return None


def table_cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def separator_row(line: str) -> bool:
    cells = table_cells(line)
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)


def read_status(path: Path) -> tuple[str, str | None]:
    """Return (state, status), where state is missing, legacy, or present."""
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return "missing", None
    except (OSError, UnicodeDecodeError) as exc:
        return "unreadable", str(exc)

    for index, line in enumerate(lines):
        if not line.lstrip().startswith("|"):
            continue
        headers = [cell.casefold() for cell in table_cells(line)]
        if "status" not in headers:
            continue
        if index + 2 >= len(lines):
            return "invalid", "the document-control table has no status row"
        if not separator_row(lines[index + 1]):
            return "invalid", "the document-control table is malformed"
        values = table_cells(lines[index + 2])
        status_index = headers.index("status")
        if status_index >= len(values):
            return "present", ""
        return "present", values[status_index]
    return "legacy", None


def main() -> int:
    try:
        event: Any = json.load(sys.stdin)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return 0
    if not isinstance(event, dict):
        return 0

    tool_input = event.get("tool_input", {})
    command = tool_input.get("command", "") if isinstance(tool_input, dict) else ""
    if not isinstance(command, str):
        return 0

    try:
        cwd = Path(str(event.get("cwd") or Path.cwd())).resolve()
    except OSError:
        cwd = Path.cwd()

    for target in patch_paths(command):
        requirement = gate_predecessor(target, cwd)
        if requirement is None:
            continue
        predecessor, output_name = requirement
        state, status = read_status(predecessor)
        relative_predecessor = predecessor
        try:
            relative_predecessor = predecessor.relative_to(cwd)
        except ValueError:
            pass

        if state == "missing":
            emit_deny(
                f"Cannot write {output_name}: required predecessor "
                f"{relative_predecessor} does not exist. Complete and approve the prior phase first."
            )
            return 0
        if state == "unreadable":
            emit_deny(
                f"Cannot verify approval for {output_name}: required predecessor "
                f"{relative_predecessor} could not be read ({status})."
            )
            return 0
        if state == "invalid":
            emit_deny(
                f"Cannot write {output_name}: required predecessor "
                f"{relative_predecessor} has {status}. Ask the user to review it."
            )
            return 0
        if state == "legacy":
            continue
        if status is None or status == "":
            emit_deny(
                f"Cannot write {output_name}: required predecessor "
                f"{relative_predecessor} has no status value. Ask the user to review it."
            )
            return 0
        if status.casefold() == "draft":
            emit_deny(
                f"Cannot write {output_name}: required predecessor "
                f"{relative_predecessor} has Status: Draft. Ask the user to approve it first."
            )
            return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
