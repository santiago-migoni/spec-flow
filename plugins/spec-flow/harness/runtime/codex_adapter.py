"""Read-only attestation and persistent ownership for native Codex execution.

This module never invokes model APIs or native agent tools. The Codex-side
orchestrator supplies capability probes and native agent identifiers; this
adapter checks those references against local rollout records.
"""

from __future__ import annotations

import fcntl
import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Optional


class AdapterError(RuntimeError):
    def __init__(self, code: str, message: str, *, details: Optional[Mapping[str, Any]] = None):
        super().__init__(message)
        self.code = code
        self.details = dict(details or {})


class NativeCodexAdapter:
    """Validate host supplied references and bind them to local Codex records."""

    production = True
    PROFILES = {
        "orchestrator": ("gpt-6-sol", "high"),
        "implementer": ("gpt-6-luna", "high"),
        "reviewer": ("gpt-6-sol", "high"),
    }
    OPERATIONS = {"spawn_agent", "wait_agent", "interrupt_agent", "list_agents"}

    def __init__(self, root: Path):
        self.root = Path(root).resolve()

    def capabilities(self, report: Any, owner: str) -> Dict[str, Any]:
        if not isinstance(report, dict):
            raise AdapterError("capability_report_invalid", "native capability report must be an object")
        operations = report.get("operations")
        evidence = report.get("probe_evidence")
        if not isinstance(operations, dict) or not isinstance(evidence, dict):
            raise AdapterError("capability_report_invalid", "capability report requires operations and probe_evidence objects")
        missing = sorted(name for name in self.OPERATIONS if operations.get(name) is not True or not isinstance(evidence.get(name), str) or not evidence[name].strip())
        if missing:
            raise AdapterError("native_capability_unavailable", "native Codex capabilities are missing or unprobed", details={"operations": missing})
        session = self.attest_session(owner, "orchestrator")
        return {"operations": sorted(self.OPERATIONS), "inventory_reference": self._nonempty_report_reference(report.get("inventory_reference")),
                "probe_evidence_references": dict(evidence),
                "basis": "host-supplied capability references; Python does not enumerate native tools",
                "owner_session": session}

    @staticmethod
    def _nonempty_report_reference(value: Any) -> str:
        if not isinstance(value, str) or not value.strip():
            raise AdapterError("capability_report_invalid", "capability report requires an inventory_reference")
        return value.strip()

    def attest_session(self, session_id: str, role: str, *, parent_session: Optional[str] = None,
                       agent_path: Optional[str] = None, require_finished: bool = False,
                       task_marker: Optional[str] = None, after: Optional[str] = None) -> Dict[str, Any]:
        if role not in self.PROFILES:
            raise AdapterError("invalid_role", "unknown host attestation role")
        path = self._find_session(session_id)
        records = self._read_records(path)
        metas = [row for row in records if row.get("type") == "session_meta"]
        if len(metas) != 1:
            raise AdapterError("host_attestation_missing", "session log must contain exactly one session_meta record")
        meta = metas[0].get("payload")
        if not isinstance(meta, dict) or meta.get("id") != session_id:
            raise AdapterError("host_attestation_mismatch", "session_meta id does not match the requested session")
        source = meta.get("source")
        lineage = source.get("subagent", {}).get("thread_spawn", {}) if isinstance(source, dict) else {}
        if parent_session is not None and (not isinstance(lineage, dict) or lineage.get("parent_thread_id") != parent_session):
            raise AdapterError("host_parent_mismatch", "native child session is not linked to the run owner")
        if agent_path is not None and (not isinstance(lineage, dict) or lineage.get("agent_path") != agent_path):
            raise AdapterError("host_agent_mismatch", "native child session agent_path does not match the spawn response")
        prompt_rows = [row for row in records if row.get("type") == "response_item" and isinstance(row.get("payload"), dict)
                       and row["payload"].get("type") == "message" and row["payload"].get("role") == "user"]
        if task_marker is not None and not any(task_marker in self._strings(row) for row in prompt_rows):
            raise AdapterError("host_task_marker_missing", "native session does not contain the prepared task packet marker")
        if after is not None:
            timestamps = [row.get("timestamp") for row in records if row.get("type") == "turn_context" and isinstance(row.get("timestamp"), str)]
            if not timestamps or max(timestamps) < after:
                raise AdapterError("host_agent_reused", "native session turn predates this prepared attempt")
        expected_model, expected_effort = self.PROFILES[role]
        turns = [row for row in records if row.get("type") == "turn_context"]
        if not turns:
            raise AdapterError("host_attestation_missing", "session log contains no turn_context records")
        mismatches = []
        for index, row in enumerate(turns):
            payload = row.get("payload")
            collaboration = payload.get("collaboration_mode") if isinstance(payload, dict) else None
            settings = collaboration.get("settings") if isinstance(collaboration, dict) else None
            model = payload.get("model") if isinstance(payload, dict) else None
            effort = settings.get("reasoning_effort") if isinstance(settings, dict) else None
            if model != expected_model or effort != expected_effort:
                mismatches.append({"turn": index, "model": model, "effort": effort})
        if mismatches:
            raise AdapterError("host_profile_mismatch", "one or more session turns do not match the required role profile", details={"expected": {"model": expected_model, "effort": expected_effort}, "mismatches": mismatches})
        lifecycle = self._agent_lifecycle(records)
        if require_finished and lifecycle not in {"completed", "aborted"}:
            raise AdapterError("agent_still_active", "native agent has no terminal lifecycle record", details={"lifecycle": lifecycle})
        lifecycle_rows = [row for row in records if row.get("type") == "event_msg" and isinstance(row.get("payload"), dict)
                          and row["payload"].get("type") in {"task_started", "task_complete", "turn_aborted"}]
        marker_rows = [row for row in prompt_rows if task_marker is not None and task_marker in self._strings(row)]
        attestation = {"session_id": session_id, "role": role, "model": expected_model, "effort": expected_effort,
                       "log_path": str(path), "agent_lifecycle": lifecycle, "parent_session": lineage.get("parent_thread_id") if isinstance(lineage, dict) else None,
                       "agent_path": lineage.get("agent_path") if isinstance(lineage, dict) else None,
                       "record_hashes": {"session_meta": self._record_hash(metas[0]),
                                         "turn_contexts": [self._record_hash(row) for row in turns],
                                         "lifecycle": self._record_hash(lifecycle_rows),
                                         "task_marker": self._record_hash(marker_rows) if task_marker is not None else None}}
        attestation["attestation_sha256"] = self._record_hash(attestation)
        return attestation

    @staticmethod
    def _agent_lifecycle(records: Iterable[Mapping[str, Any]]) -> str:
        lifecycle = "unknown"
        for row in records:
            if row.get("type") != "event_msg":
                continue
            payload = row.get("payload")
            if not isinstance(payload, dict):
                continue
            kind = payload.get("type")
            if kind == "task_started":
                lifecycle = "active"
            elif kind == "task_complete":
                lifecycle = "completed"
            elif kind == "turn_aborted":
                lifecycle = "aborted"
        return lifecycle

    def acquire(self, run_id: str, release: str, owner: str) -> Dict[str, str]:
        git_dir, common = self._git_directories()
        if git_dir == common:
            raise AdapterError("linked_worktree_required", "production implementation requires an isolated linked Git worktree")
        top_text = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], cwd=self.root, stderr=subprocess.DEVNULL, text=True).strip()
        top = Path(top_text).resolve()
        if top != self.root:
            raise AdapterError("worktree_root_required", "controller root must be the Git worktree root", details={"worktree_root": str(top)})
        registry = common / "spec-flow-active-controller.json"
        lock_path = common / "spec-flow-active-controller.lock"
        registration = {"run_id": run_id, "release": release, "worktree": str(self.root), "owner": owner}
        try:
            common.mkdir(parents=True, exist_ok=True)
            with lock_path.open("a+b") as lock:
                fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
                if registry.exists():
                    try:
                        previous = json.loads(registry.read_text(encoding="utf-8"))
                    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
                        raise AdapterError("ownership_registry_corrupt", "active controller registration is unreadable") from exc
                    if previous != registration:
                        raise AdapterError("run_already_active", "another worktree or chat owns this repository controller")
                else:
                    self._write_atomic(registry, registration)
                fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
        except AdapterError:
            raise
        except OSError as exc:
            raise AdapterError("ownership_registry_unavailable", "could not persist cross-worktree controller ownership") from exc
        return {"git_common_dir": str(common), "registration": str(registry), **registration}

    def assert_lease(self, state: Mapping[str, Any]) -> None:
        _, common = self._git_directories()
        registry = common / "spec-flow-active-controller.json"
        try:
            value = json.loads(registry.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            if state.get("status") == "completed" and not registry.exists():
                return
            raise AdapterError("ownership_lease_missing", "persistent controller ownership is missing or unreadable") from exc
        expected = {"run_id": state["run_id"], "release": state["release"], "worktree": str(self.root), "owner": state["owner"]}
        if value != expected:
            raise AdapterError("ownership_lease_mismatch", "persistent controller ownership does not match this run")

    def release(self, state: Mapping[str, Any]) -> None:
        _, common = self._git_directories()
        registry = common / "spec-flow-active-controller.json"
        lock_path = common / "spec-flow-active-controller.lock"
        with lock_path.open("a+b") as lock:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
            if state.get("status") == "completed" and not registry.exists():
                fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
                return
            self.assert_lease(state)
            registry.unlink(missing_ok=True)
            fcntl.flock(lock.fileno(), fcntl.LOCK_UN)

    def takeover(self, state: Mapping[str, Any], new_owner: str) -> Dict[str, Any]:
        # Host inspection is read-only. The compare-and-replace below repeats
        # the lease check under the common lock, preventing a stale caller from
        # transferring another controller's registration.
        previous_owner = state["owner"]
        old_owner = self.attest_session(previous_owner, "orchestrator", require_finished=True)
        self.attest_session(new_owner, "orchestrator")
        child = None
        active = state.get("active_task")
        if active:
            task_state = state.get("tasks", {}).get(active, {})
            bound = task_state.get("agent")
            if isinstance(bound, dict):
                marker = "SPEC_FLOW_PACKET_SHA256=" + task_state.get("packet_sha256", "")
                child = self.attest_session(bound["session_id"], "implementer", parent_session=bound.get("parent_session") or previous_owner,
                                            agent_path=bound["agent_path"], task_marker=marker,
                                            after=task_state.get("prepared_at"), require_finished=True)
        _, common = self._git_directories()
        registry = common / "spec-flow-active-controller.json"
        lock_path = common / "spec-flow-active-controller.lock"
        try:
            with lock_path.open("a+b") as lock:
                fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
                try:
                    current = json.loads(registry.read_text(encoding="utf-8"))
                except (OSError, UnicodeError, json.JSONDecodeError) as exc:
                    raise AdapterError("ownership_lease_missing", "persistent controller ownership is missing or unreadable") from exc
                identity = {"run_id": state["run_id"], "release": state["release"], "worktree": str(self.root)}
                expected = {**identity, "owner": previous_owner}
                transferred = {**identity, "owner": new_owner}
                if current not in (expected, transferred):
                    raise AdapterError("ownership_lease_mismatch", "takeover target no longer owns the repository controller")
                # The lease write and the run event are separate durable
                # writes. If the process dies between them, retrying takeover
                # must finish the event instead of leaving both owners stuck.
                # Accept an already-transferred lease only after the same old
                # owner/new owner/child terminal records were corroborated
                # above, and only for this exact run/release/worktree tuple.
                if current == expected:
                    current["owner"] = new_owner
                    self._write_atomic(registry, current)
                fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
        except AdapterError:
            raise
        except OSError as exc:
            raise AdapterError("ownership_registry_unavailable", "could not transfer controller ownership") from exc
        return {"previous_owner": old_owner, "new_owner": new_owner, "native_agent": child}

    def _git_directories(self) -> tuple[Path, Path]:
        try:
            git_dir_text = subprocess.check_output(["git", "rev-parse", "--absolute-git-dir"], cwd=self.root, stderr=subprocess.DEVNULL, text=True).strip()
            common_text = subprocess.check_output(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"], cwd=self.root, stderr=subprocess.DEVNULL, text=True).strip()
        except (OSError, subprocess.CalledProcessError) as exc:
            raise AdapterError("git_worktree_unavailable", "could not resolve Git worktree ownership") from exc
        git_dir, common = Path(git_dir_text).resolve(), Path(common_text).resolve()
        if not git_dir.is_dir() or not common.is_dir():
            raise AdapterError("git_worktree_unavailable", "Git directory or common directory is unavailable")
        return git_dir, common

    def _find_session(self, session_id: str) -> Path:
        if not isinstance(session_id, str) or not session_id.strip():
            raise AdapterError("host_attestation_missing", "owner or agent session id is required")
        codex_home = os.environ.get("CODEX_HOME")
        base = Path(codex_home).expanduser() if codex_home else Path.home() / ".codex"
        sessions = base / "sessions"
        if not sessions.is_dir():
            raise AdapterError("host_logs_unavailable", "Codex session log directory is unavailable", details={"path": str(sessions)})
        # Rollout filenames vary by host version; identify sessions by the authoritative meta id.
        for path in sessions.rglob("rollout-*.jsonl"):
            if not path.stem.endswith(session_id):
                continue
            try:
                with path.open("r", encoding="utf-8") as stream:
                    first_line = stream.readline()
                    row = json.loads(first_line)
                    payload = row.get("payload") if isinstance(row, dict) else None
                    if isinstance(row, dict) and row.get("type") == "session_meta" and isinstance(payload, dict) and payload.get("id") == session_id:
                        return path
            except (OSError, UnicodeError):
                continue
            except json.JSONDecodeError as exc:
                raise AdapterError("host_log_corrupt", "candidate Codex session log begins with invalid JSON", details={"path": str(path)}) from exc
        raise AdapterError("host_attestation_missing", "no local Codex session log matches the requested id", details={"session_id": session_id})

    @staticmethod
    def _read_records(path: Path) -> list[Dict[str, Any]]:
        records = []
        try:
            with path.open("r", encoding="utf-8") as stream:
                lines = stream.readlines()
                for index, line in enumerate(lines):
                    try:
                        row = json.loads(line)
                    except json.JSONDecodeError as exc:
                        if index == len(lines) - 1 and not line.endswith("\n"):
                            raise AdapterError("host_evidence_pending", "Codex session log ends with an incomplete record") from exc
                        raise AdapterError("host_log_corrupt", "Codex session log contains malformed JSON", details={"line": index + 1}) from exc
                    if not isinstance(row, dict):
                        raise AdapterError("host_log_corrupt", "Codex session log record must be an object", details={"line": index + 1})
                    records.append(row)
        except AdapterError:
            raise
        except (OSError, UnicodeError) as exc:
            raise AdapterError("host_logs_unavailable", "Codex session log cannot be read") from exc
        return records

    @staticmethod
    def _strings(value: Any) -> str:
        if isinstance(value, str):
            return value
        if isinstance(value, dict):
            return " ".join(NativeCodexAdapter._strings(item) for item in value.values())
        if isinstance(value, list):
            return " ".join(NativeCodexAdapter._strings(item) for item in value)
        return ""

    @staticmethod
    def _record_hash(value: Any) -> str:
        encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    @staticmethod
    def _write_atomic(path: Path, value: Mapping[str, Any]) -> None:
        fd, temp_name = tempfile.mkstemp(prefix="." + path.name + ".", dir=str(path.parent))
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                json.dump(value, stream, ensure_ascii=False, sort_keys=True, indent=2)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp_name, path)
            directory_fd = os.open(str(path.parent), os.O_RDONLY)
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
        finally:
            if os.path.exists(temp_name):
                os.unlink(temp_name)
