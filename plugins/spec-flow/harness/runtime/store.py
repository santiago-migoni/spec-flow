"""Atomic local storage for approvals and per-run event streams."""

from __future__ import annotations

import fcntl
import json
import os
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Dict, Iterator, List, Mapping, Optional

from .contracts import ContractError, safe_path


class StoreError(RuntimeError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


class Store:
    """Own all persistent harness state below a project root."""

    def __init__(self, root: Path):
        self.root = Path(root).resolve()
        try:
            self.directory = safe_path(self.root, ".spec-flow")
        except ContractError as exc:
            raise StoreError("unsafe_registry", str(exc)) from exc
        self.runs = self.directory / "runs"
        self.approvals_path = self.directory / "approvals.jsonl"
        self.lock_path = self.directory / "lock"

    @contextmanager
    def locked(self, *, create: bool = True) -> Iterator[None]:
        try:
            safe_path(self.root, ".spec-flow")
        except ContractError as exc:
            raise StoreError("unsafe_registry", str(exc)) from exc
        if create:
            self.directory.mkdir(parents=True, exist_ok=True)
            self.runs.mkdir(parents=True, exist_ok=True)
        elif not self.directory.is_dir() or not self.lock_path.is_file():
            raise StoreError("uninitialized", "harness registry is not initialized")
        # Resolve after mkdir too: never follow a replaced registry directory outside the project.
        try:
            safe_path(self.root, ".spec-flow/lock")
        except ContractError as exc:
            raise StoreError("unsafe_registry", str(exc)) from exc
        with self.lock_path.open("a+b") as lock_stream:
            fcntl.flock(lock_stream.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(lock_stream.fileno(), fcntl.LOCK_UN)

    def write_json_atomic(self, path: Path, value: Mapping[str, Any]) -> None:
        try:
            safe_path(self.root, path.relative_to(self.root))
        except ValueError as exc:
            raise StoreError("unsafe_registry", "registry file resolves outside the project") from exc
        except ContractError as exc:
            raise StoreError("unsafe_registry", str(exc)) from exc
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
        fd, name = tempfile.mkstemp(prefix="." + path.name + ".", dir=str(path.parent))
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                stream.write(payload)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(name, path)
            self._fsync_directory(path.parent)
        finally:
            if os.path.exists(name):
                os.unlink(name)

    @staticmethod
    def _fsync_directory(directory: Path) -> None:
        fd = os.open(str(directory), os.O_RDONLY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)

    def read_jsonl(self, path: Path, *, sequence_field: Optional[str] = None) -> List[Dict[str, Any]]:
        try:
            safe_path(self.root, path.relative_to(self.root))
        except (ValueError, ContractError) as exc:
            raise StoreError("unsafe_registry", "registry log resolves outside the project") from exc
        if not path.exists():
            return []
        rows: List[Dict[str, Any]] = []
        try:
            with path.open("r", encoding="utf-8") as stream:
                for number, line in enumerate(stream, 1):
                    if not line.endswith("\n"):
                        raise StoreError("corrupt_log", "{} line {} is incomplete".format(path, number))
                    try:
                        item = json.loads(line)
                    except json.JSONDecodeError as exc:
                        raise StoreError("corrupt_log", "{} line {} is invalid JSON".format(path, number)) from exc
                    if not isinstance(item, dict):
                        raise StoreError("corrupt_log", "{} line {} must be a JSON object".format(path, number))
                    if sequence_field and item.get(sequence_field) != number:
                        raise StoreError("corrupt_log", "{} has invalid {} at line {}".format(path, sequence_field, number))
                    rows.append(item)
        except UnicodeError as exc:
            raise StoreError("corrupt_log", "{} is not UTF-8".format(path)) from exc
        return rows

    def append_jsonl(self, path: Path, item: Mapping[str, Any], *, sequence_field: Optional[str] = None) -> Dict[str, Any]:
        try:
            safe_path(self.root, path.relative_to(self.root))
        except (ValueError, ContractError) as exc:
            raise StoreError("unsafe_registry", "registry log resolves outside the project") from exc
        path.parent.mkdir(parents=True, exist_ok=True)
        self.read_jsonl(path, sequence_field=sequence_field)
        value = dict(item)
        if sequence_field:
            value[sequence_field] = len(self.read_jsonl(path, sequence_field=sequence_field)) + 1
        payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
        with path.open("a", encoding="utf-8") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        self._fsync_directory(path.parent)
        return value

    def create_run(self, run_id: str) -> Path:
        path = safe_path(self.root, ".spec-flow/runs/{}".format(run_id))
        try:
            path.mkdir(parents=True, exist_ok=False)
            (path / "packets").mkdir()
            (path / "evidence").mkdir()
        except FileExistsError as exc:
            raise StoreError("run_exists", "run already exists") from exc
        return path

    def run_dir(self, run_id: str) -> Path:
        path = safe_path(self.root, ".spec-flow/runs/{}".format(run_id))
        if not path.is_dir():
            raise StoreError("run_not_found", "run not found")
        return path

    def read_events(self, run_id: str) -> List[Dict[str, Any]]:
        return self.read_jsonl(self.run_dir(run_id) / "events.jsonl", sequence_field="seq")

    def append_event(self, run_id: str, event: str, data: Mapping[str, Any], reducer: Callable[[List[Dict[str, Any]]], Dict[str, Any]]) -> Dict[str, Any]:
        path = self.run_dir(run_id) / "events.jsonl"
        previous = self.read_jsonl(path, sequence_field="seq")
        row = {"event": event, "data": dict(data)}
        prospective = dict(row)
        prospective["seq"] = len(previous) + 1
        events = previous + [prospective]
        state = reducer(events)
        appended = self.append_jsonl(path, row, sequence_field="seq")
        self.write_json_atomic(self.run_dir(run_id) / "state.json", state)
        return appended

    def read_state(self, run_id: str, reducer: Callable[[List[Dict[str, Any]]], Dict[str, Any]], *, repair: bool = False) -> Dict[str, Any]:
        events = self.read_events(run_id)
        if not events:
            raise StoreError("corrupt_log", "run has no events")
        state = reducer(events)
        state_path = self.run_dir(run_id) / "state.json"
        try:
            stored = json.loads(state_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, UnicodeError):
            stored = None
        if repair and stored != state:
            self.write_json_atomic(state_path, state)
        return state

    def approvals(self) -> List[Dict[str, Any]]:
        return self.read_jsonl(self.approvals_path, sequence_field="seq")

    def append_approval(self, receipt: Mapping[str, Any]) -> Dict[str, Any]:
        return self.append_jsonl(self.approvals_path, receipt, sequence_field="seq")

    def run_ids(self) -> List[str]:
        if not self.runs.exists():
            return []
        try:
            safe_path(self.root, ".spec-flow/runs")
        except ContractError as exc:
            raise StoreError("unsafe_registry", str(exc)) from exc
        return sorted(path.name for path in self.runs.iterdir() if path.is_dir())
