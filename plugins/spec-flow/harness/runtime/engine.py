"""Deterministic project-local approval and run controller."""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import tempfile
import uuid
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Set, Tuple

from .contracts import ContractError, document_digest, read_document, safe_path, validate_document, validate_release
from .codex_adapter import AdapterError, NativeCodexAdapter
from .store import Store, StoreError
from .profiles import DEFAULT_PROFILES, LEGACY_PROFILES, validate_profiles


class EngineError(RuntimeError):
    def __init__(self, code: str, message: str, *, details: Optional[Mapping[str, Any]] = None):
        super().__init__(message)
        self.code = code
        self.details = dict(details or {})


# Public initialization default, also used by legacy-folder migration.
PROFILES = DEFAULT_PROFILES

CACHE_DIRS = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".tox", ".venv", "venv", "node_modules"}
EXCLUDED_TOP = {".git", ".specs", ".spec-flow"}
ZERO_TEST_PATTERNS = ("ran 0 tests", "no tests ran", "no tests to run")
MAX_PACKET_BYTES = 262144
PHASE_ALIASES = {
    "constitution": "constitution", "architecture": "architecture", "structure": "structure",
    "infrastructure": "infrastructure", "roadmap": "roadmap", "spec": "spec", "specify": "spec",
    "clarify": "clarify", "plan": "plan", "tasks": "tasks", "analyze": "analyze",
    "implement": "implement", "converge": "converge", "review-release": "review-release",
    "finishing-branch": "finishing-branch",
}


class Engine:
    def __init__(self, root: os.PathLike[str] | str, *, adapter: Optional[Any] = None):
        self.root = Path(root).resolve()
        if not self.root.is_dir():
            raise EngineError("invalid_root", "project root must be an existing directory")
        self.store = Store(self.root)
        self.adapter = adapter if adapter is not None else NativeCodexAdapter(self.root)

    def dispatch(self, operation: str, payload: Mapping[str, Any]) -> Dict[str, Any]:
        if not isinstance(payload, dict):
            raise EngineError("invalid_input", "operation input must be a JSON object")
        methods = {
            "capabilities": self._capabilities,
            "initialize": self._initialize,
            "configure-profiles": self._configure_profiles,
            "digest": self._digest,
            "validate": self._validate,
            "approve": self._approve,
            "gate": self._gate,
            "start": self._start,
            "authorize": self._authorize,
            "prepare": self._prepare,
            "restore-packet": self._restore_packet,
            "bind-agent": self._bind_agent,
            "result": self._result,
            "retry": self._retry,
            "reconcile": self._reconcile,
            "verify": self._verify,
            "review": self._review,
            "close": self._close,
            "resume": self._resume,
            "takeover": self._takeover,
            "phase-ready": self._phase_ready,
            "review-phase": self._review_phase,
            "commit-phase": self._commit_phase,
            "refresh-evidence": self._refresh_evidence,
            "release-review": self._release_review,
            "complete": self._complete,
            "hook-check": self._hook_check,
            "status": self._status,
            "interrupt": self._interrupt,
            "abandon": self._abandon,
            "migrate-preview": self._migrate_preview,
            "migrate-apply": self._migrate_apply,
            "migrate-resume": self._migrate_resume,
        }
        if operation not in methods:
            raise EngineError("unknown_operation", "unknown operation: {}".format(operation))
        if operation == "migrate-preview":
            return methods[operation](payload)
        if operation in {"migrate-apply", "migrate-resume"}:
            with self.store.locked(create=True):
                return methods[operation](payload)
        if operation in {"status", "complete", "hook-check"}:
            self._reject_legacy_if_present()
            return methods[operation](payload)
        self._reject_legacy_if_present()
        if operation in {"digest", "validate", "gate"}:
            return methods[operation](payload)
        if operation != "initialize":
            self._config()
        with self.store.locked(create=True):
            return methods[operation](payload)

    @staticmethod
    def _fields(payload: Mapping[str, Any], required: Iterable[str], optional: Iterable[str] = ()) -> None:
        required_set, optional_set = set(required), set(optional)
        missing = sorted(required_set - set(payload))
        unknown = sorted(set(payload) - required_set - optional_set)
        if missing:
            raise EngineError("invalid_input", "missing input fields: {}".format(", ".join(missing)))
        if unknown:
            raise EngineError("invalid_input", "unknown input fields: {}".format(", ".join(unknown)))

    @staticmethod
    def _native_task_name(prefix: str, marker: str) -> str:
        return prefix + hashlib.sha256(marker.encode("utf-8")).hexdigest()

    @staticmethod
    def _nonempty(value: Any, name: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise EngineError("invalid_input", "{} must be a nonempty string".format(name))
        return value.strip()

    def _reject_legacy_if_present(self) -> None:
        registry = self.root / ".spec-flow" / "migrations"
        if registry.exists():
            try:
                safe_path(self.root, ".spec-flow/migrations")
            except ContractError as exc:
                raise EngineError("unsafe_registry", str(exc)) from exc
            for directory in registry.iterdir():
                if directory.is_dir() and not (directory / "complete.json").is_file():
                    raise EngineError("migration_incomplete", "migration journal requires migrate-resume", details={"migration_id": directory.name})
        specs = self.root / ".specs"
        if not specs.exists():
            return
        try:
            specs = safe_path(self.root, ".specs")
        except ContractError as exc:
            raise EngineError("unsafe_path", str(exc)) from exc
        if any(path.is_dir() and re.match(r"^[0-9]{3}-.+", path.name) for path in specs.iterdir()):
            raise EngineError("migration_required", "legacy .specs/NNN-feature directories require migration before harness operations")

    def _migrate_preview(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        self._fields(payload, ("mapping", "candidate_dir"), ("replacements", "imports"))
        from .migration import Migration, MigrationError
        try:
            return Migration(self.root, self.store).preview(payload["mapping"], payload["candidate_dir"],
                                                            payload.get("replacements", []), payload.get("imports", {}))
        except MigrationError as exc:
            raise EngineError(exc.code, str(exc), details=exc.details) from exc

    def _migrate_apply(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        self._fields(payload, ("manifest", "digest", "candidate_dir", "authorization"))
        from .migration import Migration, MigrationError
        try:
            return Migration(self.root, self.store).apply(payload["manifest"], payload["digest"], payload["candidate_dir"], payload["authorization"])
        except MigrationError as exc:
            raise EngineError(exc.code, str(exc), details=exc.details) from exc
        except StoreError as exc:
            raise EngineError(exc.code, str(exc)) from exc

    def _migrate_resume(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        self._fields(payload, ("migration_id",))
        from .migration import Migration, MigrationError
        try:
            return Migration(self.root, self.store).resume(payload["migration_id"])
        except MigrationError as exc:
            raise EngineError(exc.code, str(exc), details=exc.details) from exc
        except StoreError as exc:
            raise EngineError(exc.code, str(exc)) from exc

    def _config_path(self) -> Path:
        try:
            return safe_path(self.root, ".spec-flow/config.json")
        except ContractError as exc:
            raise EngineError("unsafe_registry", str(exc)) from exc

    def _config(self, *, required: bool = True) -> Optional[Dict[str, Any]]:
        path = self._config_path()
        if not path.exists():
            if required:
                raise EngineError("uninitialized", "run initialize before using the harness")
            return None
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, UnicodeError) as exc:
            raise EngineError("invalid_config", "harness config is unreadable or invalid JSON") from exc
        if (not isinstance(value, dict) or value.get("schema_version") != 1
                or type(value.get("retry_limit")) is not int or value.get("retry_limit") != 3):
            raise EngineError("invalid_config", "harness config has an unsupported schema or retry limit")
        try:
            value["profiles"] = validate_profiles(value.get("profiles"))
        except ValueError as exc:
            raise EngineError("invalid_config", str(exc)) from exc
        return value

    def _initialize(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        self._fields(payload, ())
        config_path = self._config_path()
        if config_path.exists():
            self._config()
            self._ensure_registry_gitignore()
            return {"status": "initialized", "config_path": str(config_path), "already_initialized": True}
        config = {"schema_version": 1, "profiles": PROFILES, "retry_limit": 3}
        self.store.write_json_atomic(config_path, config)
        (self.root / ".spec-flow" / "runs").mkdir(parents=True, exist_ok=True)
        self._ensure_registry_gitignore()
        return {"status": "initialized", "config_path": str(config_path), "already_initialized": False}

    def _configure_profiles(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        self._fields(payload, ("profiles",))
        config = self._config()
        try:
            profiles = validate_profiles(payload["profiles"])
        except ValueError as exc:
            raise EngineError("invalid_profiles", str(exc)) from exc
        changed = profiles != config["profiles"]
        if changed:
            config["profiles"] = profiles
            self.store.write_json_atomic(self._config_path(), config)
        return {"profiles": profiles, "changed": changed, "applies_to": "new_runs_only"}

    def _ensure_registry_gitignore(self) -> None:
        path = self.root / ".spec-flow" / ".gitignore"
        lines = ["# Spec-Flow generated state and bounded context packets", "/lock", "/runs/*/state.json", "/runs/*/packets/"]
        existing = path.read_text(encoding="utf-8") if path.exists() else ""
        additions = [line for line in lines if line not in existing.splitlines()]
        if additions:
            with path.open("a", encoding="utf-8") as stream:
                if existing and not existing.endswith("\n"):
                    stream.write("\n")
                stream.write("\n".join(additions) + "\n")

    def _phase_controller(self):
        from .phases import PhaseController
        controller = getattr(self, "_phases", None)
        if controller is None:
            controller = self._phases = PhaseController(self)
        return controller

    def _phase_ready(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        return self._phase_controller().ready(payload)

    def _review_phase(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        return self._phase_controller().review(payload)

    def _commit_phase(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        return self._phase_controller().commit(payload)

    def _refresh_evidence(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        return self._phase_controller().refresh_evidence(payload)

    def _release_review(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        return self._phase_controller().release_review(payload)

    def _complete(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        return self._phase_controller().complete(payload)

    def _hook_check(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        """Read-only PreToolUse authorization for explicitly supported writes."""
        self._fields(payload, ("paths",))
        paths = payload["paths"]
        if not isinstance(paths, list) or not paths or not all(isinstance(item, str) and item.strip() for item in paths):
            raise EngineError("invalid_input", "hook paths must be a nonempty list of project-relative strings")
        targets: List[str] = []
        for value in paths:
            if Path(value).is_absolute() or ".." in Path(value).parts:
                raise EngineError("unsafe_path", "hook paths must be relative and must not traverse the project root")
            path = self._project_path(value)
            relative = path.relative_to(self.root).as_posix()
            if relative == ".spec-flow" or relative.startswith(".spec-flow/"):
                raise EngineError("protected_runtime_state", "Codex tools cannot patch Spec-Flow runtime, registry, packet, or audit state")
            targets.append(relative)

        docs = []
        code_targets = []
        for relative in targets:
            parts = Path(relative).parts
            if len(parts) == 3 and parts[0] == ".specs" and parts[1].startswith("release-v") and parts[2] in {"spec.md", "plan.md", "tasks.md"}:
                docs.append(relative)
            elif len(parts) == 2 and parts[0] == ".specs" and parts[1] in {"architecture.md", "structure.md", "infrastructure.md", "roadmap.md"}:
                docs.append(relative)
            elif parts and parts[0] == ".specs":
                continue
            else:
                code_targets.append(relative)

        for relative in docs:
            path = self._project_path(relative)
            name = path.name
            release = self._infer_release(path)
            if name in {"architecture.md", "structure.md", "infrastructure.md"}:
                prerequisites = [self._project_path(".specs/constitution.md")]
            elif name == "roadmap.md":
                if path.exists():
                    try:
                        doc = validate_document(self.root, path)
                        prerequisites = self._gate_prerequisites("roadmap", path, doc["contract"], release)
                    except ContractError as exc:
                        raise EngineError("contract_invalid", str(exc)) from exc
                else:
                    prerequisites = [self._project_path(".specs/constitution.md")]
            else:
                predecessor = {"spec.md": ".specs/roadmap.md", "plan.md": self._release_path(release, "spec.md").relative_to(self.root).as_posix(),
                               "tasks.md": self._release_path(release, "plan.md").relative_to(self.root).as_posix()}.get(name)
                prerequisites = [self._project_path(predecessor)] if predecessor else []
            for prerequisite in prerequisites:
                self._require_approved(prerequisite)

        if code_targets:
            active = []
            for run_id in self.store.run_ids():
                state = self._state(run_id)
                if state.get("status") == "active" and state.get("active_task"):
                    active.append(state)
            if len(active) != 1:
                raise EngineError("active_task_required", "implementation writes require exactly one active, authorized task")
            state = active[0]
            task_id = state["active_task"]
            task = self._task_contract(state, task_id)
            task_state = state.get("tasks", {}).get(task_id, {})
            if task["phase"] not in state["authorized_phases"]:
                raise EngineError("phase_not_authorized", "active task phase lacks current execution authorization")
            if task_state.get("status") != "running" or not task_state.get("agent"):
                raise EngineError("native_agent_required", "implementation writes require a prepared task with a bound native agent")
            self._owned_state({"run_id": state["run_id"], "owner": state["owner"]})
            self._ensure_approvals_current(state)
            allowed = self._allowed_paths(task)
            outside = sorted(set(code_targets) - allowed)
            if outside:
                raise EngineError("out_of_scope_changes", "write paths exceed the active task's approved file scope", details={"paths": outside, "task_id": task_id})
        return {"allowed": True, "paths": targets, "active_task": active[0]["active_task"] if code_targets else None}

    def _digest(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        self._fields(payload, ("path",))
        path = self._project_path(payload["path"])
        return {"path": path.relative_to(self.root).as_posix(), "digest": document_digest(path)}

    def _validate(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        self._fields(payload, (), ("release", "path"))
        if ("release" in payload) == ("path" in payload):
            raise EngineError("invalid_input", "provide exactly one of release or path")
        try:
            if "path" in payload:
                path = self._project_path(payload["path"])
                result = validate_document(self.root, path)
                return {"valid": True, "path": path.relative_to(self.root).as_posix(), "kind": result["contract"]["kind"], "digest": document_digest(path)}
            result = validate_release(self.root, self._nonempty(payload["release"], "release"))
        except ContractError as exc:
            raise EngineError("contract_invalid", str(exc)) from exc
        return {"valid": True, "release": result["release"], "documents": ["spec", "plan", "tasks"]}

    def _project_path(self, value: Any) -> Path:
        if not isinstance(value, str) or not value.strip():
            raise EngineError("invalid_input", "path must be a nonempty project-relative string")
        try:
            return safe_path(self.root, value)
        except ContractError as exc:
            raise EngineError("unsafe_path", str(exc)) from exc

    def _approval_map(self) -> Dict[str, Dict[str, Any]]:
        try:
            rows = self.store.approvals()
        except StoreError as exc:
            raise EngineError(exc.code, str(exc)) from exc
        latest: Dict[str, Dict[str, Any]] = {}
        for row in rows:
            path = row.get("path")
            if isinstance(path, str):
                latest[path] = row
        return latest

    def _current_approval(self, path: Path, receipts: Optional[Mapping[str, Mapping[str, Any]]] = None) -> bool:
        receipts = self._approval_map() if receipts is None else receipts
        key = path.relative_to(self.root).as_posix()
        receipt = receipts.get(key)
        if not receipt:
            return False
        try:
            current = document_digest(path)
        except ContractError:
            return False
        return receipt.get("digest") == current and all(isinstance(receipt.get(field), str) and receipt[field].strip() for field in ("actor", "statement", "source"))

    def _dependency_paths(self, path: Path) -> List[Path]:
        try:
            document = validate_document(self.root, path)
        except ContractError as exc:
            raise EngineError("contract_invalid", str(exc)) from exc
        dependencies = []
        for reference in document["contract"]["depends_on"]:
            dependencies.append(self._project_path(reference["path"]))
        return dependencies

    def _approval_closure(self, path: Path) -> List[Path]:
        ordered: List[Path] = []
        visiting: Set[Path] = set()
        visited: Set[Path] = set()

        def visit(current: Path) -> None:
            current = current.resolve()
            if current in visiting:
                raise EngineError("dependency_cycle", "document dependency cycle detected")
            if current in visited:
                return
            visiting.add(current)
            for dependency in self._dependency_paths(current):
                visit(dependency)
            visiting.remove(current)
            visited.add(current)
            ordered.append(current)

        visit(path)
        return ordered

    def _require_approved(self, path: Path) -> None:
        receipts = self._approval_map()
        for dependency in self._approval_closure(path):
            if not self._current_approval(dependency, receipts):
                raise EngineError("dependency_not_approved", "document or dependency is not currently approved: {}".format(dependency.relative_to(self.root)))

    def _approve(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        self._fields(payload, ("path", "actor", "statement", "source"), ("release",))
        path = self._project_path(payload["path"])
        actor = self._nonempty(payload["actor"], "actor")
        statement = self._nonempty(payload["statement"], "statement")
        source = self._nonempty(payload["source"], "source")
        try:
            document = validate_document(self.root, path)
        except ContractError as exc:
            raise EngineError("contract_invalid", str(exc)) from exc
        for prerequisite in self._gate_prerequisites(document["contract"]["kind"], path, document["contract"], payload.get("release")):
            self._require_approved(prerequisite)
        for dependency in self._approval_closure(path)[:-1]:
            if not self._current_approval(dependency):
                raise EngineError("dependency_not_approved", "approve dependencies first: {}".format(dependency.relative_to(self.root)))
        digest = document_digest(path)
        receipt = {"path": path.relative_to(self.root).as_posix(), "digest": digest, "actor": actor, "statement": statement, "source": source, "created_at": self._now()}
        # Approval retries are common after a lost CLI response. Reuse the
        # exact receipt, while preserving a new receipt for a changed statement.
        for existing in self.store.approvals():
            if all(existing.get(key) == receipt[key] for key in ("path", "digest", "actor", "statement", "source")):
                return {"approved": True, "path": receipt["path"], "digest": digest,
                        "sequence": existing.get("seq"), "already_approved": True}
        try:
            row = self.store.append_approval(receipt)
        except StoreError as exc:
            raise EngineError(exc.code, str(exc)) from exc
        return {"approved": True, "path": receipt["path"], "digest": digest, "sequence": row["seq"]}

    def _gate(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        self._fields(payload, (), ("path", "phase", "kind", "release"))
        config = self._config(required=False)
        if config is None:
            return {"ready": False, "reason": "uninitialized", "missing_approvals": []}
        selector = payload.get("phase", payload.get("kind"))
        if "path" in payload:
            path = self._project_path(payload["path"])
            try:
                document = validate_document(self.root, path)
            except ContractError as exc:
                raise EngineError("contract_invalid", str(exc)) from exc
            kind = document["contract"]["kind"]
            prerequisites = self._gate_prerequisites(kind, path, document["contract"], payload.get("release"))
        elif selector in PHASE_ALIASES:
            phase = PHASE_ALIASES[selector]
            prerequisites = self._phase_prerequisites(phase, payload.get("release"))
            if phase in {"clarify", "analyze", "implement", "converge"}:
                self._validate_phase_documents(phase, payload.get("release"))
        else:
            raise EngineError("invalid_input", "gate requires a valid path, phase, or kind")
        receipts = self._approval_map()
        missing: List[str] = []
        invalid: List[Dict[str, str]] = []
        for item in prerequisites:
            try:
                closure = self._approval_closure(item)
            except EngineError as exc:
                invalid.append({"path": item.relative_to(self.root).as_posix(), "reason": str(exc)})
                continue
            for source in closure:
                relative = source.relative_to(self.root).as_posix()
                if not self._current_approval(source, receipts) and relative not in missing:
                    missing.append(relative)
        return {"ready": not missing and not invalid, "missing_approvals": missing, "invalid_prerequisites": invalid}

    def _gate_prerequisites(self, kind: str, path: Path, contract: Mapping[str, Any], release: Optional[str]) -> List[Path]:
        if kind == "constitution":
            return []
        if kind in {"architecture", "structure", "infrastructure"}:
            return [self._project_path(".specs/constitution.md")]
        if kind == "roadmap":
            return [self._project_path(".specs/constitution.md")] + [self._project_path(ref["path"]) for ref in contract["depends_on"]]
        if kind == "spec":
            return [self._project_path(".specs/roadmap.md")]
        if kind == "plan":
            return [self._release_path(release or self._infer_release(path), "spec.md")]
        if kind == "tasks":
            return [self._release_path(release or self._infer_release(path), "plan.md")]
        return []

    @staticmethod
    def _infer_release(path: Path) -> Optional[str]:
        parent = path.parent.name
        return parent[len("release-"):] if parent.startswith("release-v") else None

    def _phase_prerequisites(self, phase: str, release: Optional[str]) -> List[Path]:
        if phase == "constitution":
            return []
        if phase in {"architecture", "structure", "infrastructure"}:
            return [self._project_path(".specs/constitution.md")]
        if phase == "roadmap":
            return [self._project_path(".specs/constitution.md")]
        if phase == "spec":
            return [self._project_path(".specs/roadmap.md")]
        if phase == "clarify":
            return [self._release_path(release, "spec.md")]
        if phase == "plan":
            return [self._release_path(release, "spec.md")]
        if phase == "tasks":
            return [self._release_path(release, "plan.md")]
        if phase == "analyze":
            return [self._release_path(release, name) for name in ("spec.md", "plan.md", "tasks.md")]
        if phase in {"implement", "converge", "review-release", "finishing-branch"}:
            return self._release_documents(release)
        return []

    def _validate_phase_documents(self, phase: str, release: Optional[str]) -> None:
        if phase == "clarify":
            path = self._release_path(release, "spec.md")
            try:
                validate_document(self.root, path)
            except ContractError as exc:
                raise EngineError("contract_invalid", str(exc)) from exc
        elif phase in {"analyze", "implement", "converge"}:
            try:
                validate_release(self.root, self._release_version(release))
            except ContractError as exc:
                raise EngineError("contract_invalid", str(exc)) from exc

    def _release_version(self, value: Optional[str]) -> str:
        if value is None:
            raise EngineError("release_required", "this phase requires a release")
        from .contracts import normalize_release
        try:
            return normalize_release(value)
        except ContractError as exc:
            raise EngineError("invalid_release", str(exc)) from exc

    def _release_path(self, release: Optional[str], filename: str) -> Path:
        version = self._release_version(release)
        return self._project_path(".specs/release-{}/{}".format(version, filename))

    def _release_documents(self, release: Optional[str]) -> List[Path]:
        return [self._project_path(".specs/constitution.md"), self._project_path(".specs/roadmap.md")] + [self._release_path(release, name) for name in ("spec.md", "plan.md", "tasks.md")]

    def _document_closure(self, roots: Iterable[Path]) -> List[Path]:
        result: List[Path] = []
        for path in roots:
            try:
                closure = self._approval_closure(path)
            except EngineError as exc:
                if exc.code in {"contract_invalid", "dependency_cycle"}:
                    raise EngineError("approval_stale", "an approved document dependency is no longer valid") from exc
                raise
            for dependency in closure:
                if dependency not in result:
                    result.append(dependency)
        return result

    def _start(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        self._fields(payload, ("release", "owner", "authorization", "capabilities"), ("phases",))
        config = self._config()
        # Migration may create the runtime config directly, without going
        # through initialize. Install cache ignores on the first mutating run
        # entry while preserving tracked event/audit evidence.
        self._ensure_registry_gitignore()
        version = self._release_version(payload["release"])
        owner = self._nonempty(payload["owner"], "owner")
        auth = self._authorization(payload["authorization"])
        if not isinstance(payload["capabilities"], dict):
            raise EngineError("invalid_input", "capabilities must be an object")
        # A repeated start must attest against the existing run, never today's defaults.
        try:
            prior_states = [self.store.read_state(run_id, self._reduce_events) for run_id in self.store.run_ids()]
        except StoreError as exc:
            raise EngineError(exc.code, str(exc)) from exc
        candidates = [row for row in prior_states if row["release"] == version and row["owner"] == owner
                      and row["status"] in {"active", "interrupted", "completed"}]
        profile_state = next((row for row in candidates if row["status"] != "completed"), candidates[0] if candidates else None)
        if profile_state is not None:
            capability_report = self._run_adapter_call(profile_state, "capabilities", payload["capabilities"], owner)
        else:
            capability_report = self._adapter_call("capabilities", payload["capabilities"], owner,
                                                   profiles=config["profiles"], require_catalog=True)
        try:
            validated = validate_release(self.root, version)
        except ContractError as exc:
            raise EngineError("contract_invalid", str(exc)) from exc
        approval_roots = self._release_documents(version)
        try:
            for path in approval_roots:
                self._require_approved(path)
        except EngineError as exc:
            if exc.code == "dependency_not_approved":
                raise EngineError("approval_required", str(exc)) from exc
            raise
        task_items = validated["tasks"]["contract"]["tasks"]
        task_phases = list(dict.fromkeys(item["phase"] for item in task_items))
        phases = payload.get("phases")
        if phases is None:
            phases = task_phases[:1]
        if not isinstance(phases, list) or not phases or not all(isinstance(p, str) and p for p in phases):
            raise EngineError("invalid_input", "phases must be a nonempty string list")
        if set(phases) - set(task_phases):
            raise EngineError("invalid_input", "authorized phases must occur in tasks.md")
        prior_attempts: Dict[str, int] = {}
        for run_id in self.store.run_ids():
            try:
                existing = self.store.read_state(run_id, self._reduce_events)
            except StoreError as exc:
                raise EngineError(exc.code, str(exc)) from exc
            if existing.get("release") == version:
                for task_id, task_state in existing.get("tasks", {}).items():
                    prior_attempts[task_id] = max(prior_attempts.get(task_id, 0), int(task_state.get("attempt", 0)))
            if existing["status"] in {"active", "interrupted"}:
                if existing["release"] == version and existing["owner"] == owner:
                    self._run_adapter_call(existing, "acquire", run_id, version, owner)
                    imported = self._credit_migrated_evidence(run_id, version, task_items)
                    current = self._state(run_id)
                    return {"run_id": run_id, "status": current["status"], "already_running": True,
                            "authorized_phases": current["authorized_phases"],
                            "imported_completed": imported["completed"], "pending_imports": imported["pending"]}
                raise EngineError("run_already_active", "another run owns the project")
            if existing["status"] == "completed" and existing["release"] == version and existing["owner"] == owner:
                closure = self._phase_controller().complete({"release": version, "run_id": run_id})
                if closure["complete"]:
                    return {"run_id": run_id, "status": "completed", "already_completed": True,
                            "authorized_phases": existing["authorized_phases"], "imported_completed": [], "pending_imports": []}
                raise EngineError("run_closure_pending", "phase work is committed but final release audit/closure is incomplete", details={"reasons": closure["reasons"]})
        run_id = str(uuid.uuid4())
        self.store.create_run(run_id)
        try:
            self.store.append_event(run_id, "started", {
                "run_id": run_id, "release": version, "owner": owner, "authorized_phases": list(dict.fromkeys(phases)),
                "authorization": auth, "capabilities": capability_report, "profiles": config["profiles"],
                "documents": {path.relative_to(self.root).as_posix(): document_digest(path) for path in self._document_closure(approval_roots)},
                "task_ids": [item["id"] for item in task_items], "task_contracts": task_items,
                "phase_contracts": validated["plan"]["contract"]["phases"],
                "prior_attempts": prior_attempts,
            }, self._reduce_events)
        except StoreError as exc:
            shutil.rmtree(self.store.run_dir(run_id), ignore_errors=True)
            raise EngineError(exc.code, str(exc)) from exc
        try:
            self._adapter_call("acquire", run_id, version, owner, profiles=config["profiles"], require_catalog=True)
        except EngineError:
            shutil.rmtree(self.store.run_dir(run_id), ignore_errors=True)
            raise
        try:
            reused = self._credit_prior_run_evidence(run_id)
            imported = self._credit_migrated_evidence(run_id, version, task_items)
        except StoreError as exc:
            raise EngineError(exc.code, str(exc)) from exc
        state = self._state(run_id)
        return {"run_id": run_id, "status": state["status"], "authorized_phases": list(dict.fromkeys(phases)),
                "reused_completed": reused, "imported_completed": imported["completed"], "pending_imports": imported["pending"]}

    def _capabilities(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        self._fields(payload, ("owner", "report"), ("run_id",))
        owner = self._nonempty(payload["owner"], "owner")
        if "run_id" in payload:
            state = self._state(self._nonempty(payload["run_id"], "run_id"))
            self._require_owner(state, owner)
            return self._run_adapter_call(state, "capabilities", payload["report"], owner)
        return self._adapter_call("capabilities", payload["report"], owner,
                                  profiles=self._config()["profiles"], require_catalog=True)

    def _credit_prior_run_evidence(self, run_id: str) -> List[str]:
        """Reuse only exact, still-current completed evidence from an earlier same-release run."""
        state = self._state(run_id)
        credited: List[str] = []
        for task in state["task_contracts"]:
            task_id = task["id"]
            current = self._state(run_id).get("tasks", {}).get(task_id, {})
            if current.get("status") == "completed":
                continue
            for prior_id in reversed(self.store.run_ids()):
                if prior_id == run_id:
                    continue
                prior = self._state(prior_id)
                if prior.get("release") != state["release"]:
                    continue
                prior_task = next((item for item in prior["task_contracts"] if item.get("id") == task_id), None)
                evidence = prior.get("tasks", {}).get(task_id, {})
                if (prior_task != task or evidence.get("status") != "completed"
                        or evidence.get("source_digests") != state["documents"]
                        or not evidence.get("step_evidence") or not evidence.get("code_fingerprint")):
                    continue
                try:
                    self._ensure_evidence_current(prior, task_id, evidence, enforce_snapshot=False)
                except EngineError:
                    continue
                expected_steps = {step["id"] for step in task["steps"]}
                if set(evidence["step_evidence"]) != expected_steps:
                    continue
                if any(item.get("source_digests") != state["documents"] for item in evidence["step_evidence"].values()):
                    continue
                evidence_path = self.store.run_dir(run_id) / "evidence" / "{}-prior-{}.json".format(task_id, prior_id)
                record = {"task_id": task_id, "prior_run_id": prior_id, "source_digests": state["documents"],
                          "code_fingerprint": evidence["code_fingerprint"], "verified_snapshot": evidence.get("verified_snapshot"),
                          "steps": list(evidence["step_evidence"].values()), "review": evidence.get("review"),
                          "prior_evidence_path": evidence.get("evidence_path")}
                self.store.write_json_atomic(evidence_path, record)
                self._append(run_id, "prior_run_credited", {"task_id": task_id, "prior_run_id": prior_id,
                    "steps": record["steps"], "code_fingerprint": record["code_fingerprint"],
                    "attempt": int(state.get("prior_attempts", {}).get(task_id, 0)),
                    "verified_snapshot": record["verified_snapshot"], "source_digests": record["source_digests"],
                    "evidence_path": evidence_path.relative_to(self.root).as_posix(), "review": record["review"]})
                credited.append(task_id)
                break
        return credited

    def _credit_migrated_evidence(self, run_id: str, release: str,
                                  task_items: Sequence[Mapping[str, Any]]) -> Dict[str, List[Any]]:
        """Credit only explicit historical step records that still match this release and code."""
        registry = safe_path(self.root, ".spec-flow/migrations")
        if not registry.is_dir():
            return {"completed": [], "pending": []}
        documents = self._state(run_id)["documents"]
        tasks_path = ".specs/release-{}/tasks.md".format(release)
        migration_rows: List[Tuple[str, Dict[str, Any]]] = []
        pending: List[Dict[str, Any]] = []
        for directory in sorted(registry.iterdir()):
            if not directory.is_dir() or not (directory / "complete.json").is_file():
                continue
            evidence_path = safe_path(self.root, directory.relative_to(self.root) / "imported-evidence.jsonl")
            try:
                rows = self.store.read_jsonl(evidence_path, sequence_field="seq")
            except StoreError as exc:
                raise EngineError(exc.code, str(exc)) from exc
            for row in rows:
                if row.get("release") != release:
                    continue
                if row.get("status") != "imported":
                    pending.append({"migration_id": directory.name, "source": row.get("source"),
                                   "reason": row.get("reason", "historical evidence is pending"),
                                   "task_id": (row.get("record") or {}).get("task_id") if isinstance(row.get("record"), dict) else None})
                    continue
                migration_rows.append((directory.name, row))

        completed: List[str] = []
        contracts = {item["id"]: item for item in task_items}
        groups: Dict[str, List[Tuple[str, Dict[str, Any]]]] = {}
        for ident, row in migration_rows:
            task_id = row.get("task_id")
            if task_id not in contracts:
                pending.append({"migration_id": ident, "source": row.get("source"), "task_id": task_id,
                                "reason": "task no longer exists in the approved release"})
                continue
            groups.setdefault(task_id, []).append((ident, row))
        for task_id, contract in contracts.items():
            rows = groups.get(task_id, [])
            if not rows:
                continue
            current_state = self._state(run_id)
            if current_state["tasks"].get(task_id, {}).get("status") == "completed" or current_state.get("active_task") == task_id:
                continue
            by_step = {row.get("step_id"): (ident, row) for ident, row in rows}
            reasons = []
            if len(by_step) != len(rows):
                reasons.append("duplicate imported step records")
            if set(by_step) != {step["id"] for step in contract["steps"]}:
                reasons.append("imported evidence does not cover every current task step")
            pinned_task_digest = documents.get(tasks_path)
            current_task_digest = document_digest(self._project_path(tasks_path))
            if current_task_digest != pinned_task_digest:
                raise EngineError("approval_stale", "approved task document changed while starting run")
            code_files = set(contract["files"])
            fingerprint = {}
            for filename in sorted(code_files):
                path = self._project_path(filename)
                fingerprint[filename] = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() and not path.is_symlink() else None
            canonical_hash = hashlib.sha256(json.dumps(fingerprint, ensure_ascii=False, sort_keys=True,
                                                        separators=(",", ":")).encode("utf-8")).hexdigest()
            steps = []
            for step in contract["steps"]:
                imported = by_step.get(step["id"])
                if imported is None:
                    continue
                ident, row = imported
                if row.get("task_digest") != pinned_task_digest or row.get("source_digests") != documents:
                    reasons.append("imported source pins differ from the currently approved document closure")
                if set(row.get("code_files", {})) != code_files or row.get("code_files") != fingerprint or row.get("record", {}).get("code_hash") != canonical_hash:
                    reasons.append("tested code no longer matches imported evidence")
                proof = row.get("verified_step", {})
                verification = step["verification"]
                if proof.get("command") != verification.get("command") or proof.get("expected") != verification.get("expected") or proof.get("exit_code") != 0 or not proof.get("observed", "").strip():
                    reasons.append("imported verification differs from the current step")
                steps.append({"step_id": step["id"], "migration_id": ident, "import_id": row.get("import_id"),
                              "code_files": row.get("code_files"), "verified_step": proof})
            if reasons:
                pending.extend({"task_id": task_id, "reason": reason} for reason in dict.fromkeys(reasons))
                continue
            snapshot = self._snapshot_code()
            scope = self._task_scope_files(self._state(run_id), contract)
            self._append(run_id, "migration_credited", {
                "task_id": task_id, "migration_ids": sorted({ident for ident, _ in rows}),
                "imports": [row.get("import_id") for _, row in rows], "steps": steps,
                "verified_snapshot": snapshot, "code_fingerprint": self._scope_fingerprint(snapshot, scope),
                "credited_at": self._now(),
            })
            completed.append(task_id)
        return {"completed": completed, "pending": pending}

    def _authorize(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        self._fields(payload, ("run_id", "owner", "phases", "authorization"))
        state = self._owned_state(payload)
        if state["status"] != "active" or state.get("active_task"):
            raise EngineError("run_not_ready", "phase authorization requires an idle active run")
        phases = payload["phases"]
        if not isinstance(phases, list) or not phases or not all(isinstance(p, str) and p for p in phases):
            raise EngineError("invalid_input", "phases must be a nonempty string list")
        known = {task["phase"] for task in state["task_contracts"]}
        if set(phases) - known:
            raise EngineError("invalid_input", "authorized phases must occur in tasks.md")
        phases_by_id = {item["id"]: item for item in state["phase_contracts"]}
        for phase_id in phases:
            unfinished = [task["id"] for task in state["task_contracts"]
                          if task["phase"] in phases_by_id[phase_id]["depends_on"]
                          and state["tasks"].get(task["id"], {}).get("status") != "completed"]
            if unfinished:
                raise EngineError("phase_dependency_not_complete", "complete prior phase tasks before authorizing this phase")
        auth = self._authorization(payload["authorization"])
        updated = list(dict.fromkeys(state["authorized_phases"] + phases))
        self._append(payload["run_id"], "authorized", {"phases": updated, "authorization": auth})
        return {"run_id": payload["run_id"], "authorized_phases": updated}

    def _prepare(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        self._fields(payload, ("run_id", "owner", "task_id"))
        state = self._owned_state(payload)
        self._require_active(state)
        if state.get("active_task"):
            raise EngineError("task_already_active", "the run already has an active task attempt")
        task_id = self._nonempty(payload["task_id"], "task_id")
        task = self._task_contract(state, task_id)
        task_state = state["tasks"].get(task_id, {})
        if task_state.get("status") == "completed":
            raise EngineError("task_completed", "task is already complete")
        if task_state.get("status") == "reconciliation_required":
            raise EngineError("reconciliation_required", "reconcile the interrupted attempt before starting another")
        if task["phase"] not in state["authorized_phases"]:
            raise EngineError("phase_not_authorized", "task phase is outside the run authorization")
        phase = next((item for item in state["phase_contracts"] if item["id"] == task["phase"]), None)
        if phase is None:
            raise EngineError("contract_invalid", "task phase is absent from the approved plan")
        phase_dependencies: Set[str] = set()
        for prior_phase in phase["depends_on"]:
            prior_state = state.get("phases", {}).get(prior_phase, {})
            if prior_state.get("status") != "committed":
                raise EngineError("phase_dependency_not_committed", "phase dependency requires a validated prior phase commit: {}".format(prior_phase))
            self._phase_controller()._validate_recorded_commit(state, prior_phase, prior_state)
            phase_dependencies.update(item["id"] for item in state["task_contracts"] if item["phase"] == prior_phase)
        completed_dependencies = set(task["depends_on"]) | phase_dependencies
        for dependency in task["depends_on"]:
            if state["tasks"].get(dependency, {}).get("status") != "completed":
                raise EngineError("task_dependency_not_complete", "task dependency is not complete: {}".format(dependency))
        for dependency in sorted(completed_dependencies):
            dependency_state = state["tasks"].get(dependency, {})
            if dependency_state.get("status") == "completed":
                self._ensure_evidence_current(state, dependency, dependency_state, enforce_snapshot=False)
        self._ensure_approvals_current(state)
        attempt = int(state.get("prior_attempts", {}).get(task_id, 0)) + int(task_state.get("attempt", 0)) + 1
        retry_limit = self._config()["retry_limit"]
        if attempt > retry_limit:
            raise EngineError("retry_limit", "task reached the maximum of {} attempts".format(retry_limit))
        baseline = self._snapshot_code()
        packet = self._build_task_packet(state, payload["run_id"], task_id, attempt, self._now(), state["owner"])
        scoped_files = set(packet["scope_files"])
        source_rows = packet["sources"]
        selected_acceptance = packet["selected_acceptance"]
        packet_path = self.store.run_dir(payload["run_id"]) / "packets" / "{}-{}.json".format(task_id, attempt)
        self._ensure_approvals_current(state)
        if packet_path.exists():
            try:
                packet = json.loads(packet_path.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, json.JSONDecodeError) as exc:
                raise EngineError("packet_corrupt", "existing immutable packet is unreadable") from exc
            if packet.get("run_id") != payload["run_id"] or packet.get("task_id") != task_id or packet.get("attempt") != attempt:
                raise EngineError("packet_exists", "orphan packet does not match the current attempt")
            if ((state["profile_snapshot"] and packet.get("profiles") != state["profiles"])
                    or (not state["profile_snapshot"] and "profiles" in packet)):
                raise EngineError("packet_profile_mismatch", "orphan packet profiles differ from the pinned run")
            if packet.get("sources") != source_rows or packet.get("scope_files") != sorted(scoped_files) or packet.get("source_digests") != state["documents"] or packet.get("selected_acceptance") != selected_acceptance:
                raise EngineError("approval_stale", "orphan packet sources or scope changed before adoption")
        self._write_immutable_json(packet_path, packet)
        self._append(payload["run_id"], "prepared", {
            "task_id": task_id, "attempt": attempt, "packet_path": packet_path.relative_to(self.root).as_posix(),
            "packet_sha256": packet["packet_sha256"], "baseline": baseline, "scope_files": sorted(scoped_files),
            "source_digests": state["documents"], "attempt_owner": state["owner"],
            "prepared_at": packet["created_at"],
        })
        marker = "SPEC_FLOW_PACKET_SHA256=" + packet["packet_sha256"]
        return {"run_id": payload["run_id"], "task_id": task_id, "attempt": attempt, "packet_path": str(packet_path),
                "packet_sha256": packet["packet_sha256"], "native_task_name": self._native_task_name("luna_", marker),
                "scope_files": sorted(scoped_files)}

    def _build_task_packet(self, state: Mapping[str, Any], run_id: str, task_id: str, attempt: int,
                           created_at: str, owner: str) -> Dict[str, Any]:
        task = self._task_contract(state, task_id)
        scoped_files = self._task_scope_files(state, task)
        packet_sources = []
        for relative, digest in sorted(state["documents"].items()):
            path = self._project_path(relative)
            doc = read_document(path)
            projected = self._packet_source_projection(relative, doc["contract"], doc["prose"], task, state)
            packet_sources.append({"path": path.relative_to(self.root).as_posix(), "digest": digest,
                                   "contract": projected["contract"], "prose": projected["prose"]})
        selected_acceptance = {criterion["id"]: criterion for criterion in read_document(self._release_path(state["release"], "spec.md"))["contract"]["acceptance"]
                               if criterion["id"] in task["acceptance"]}
        packet = {"run_id": run_id, "task_id": task_id, "attempt": attempt,
                  "owner": owner, "task": task, "sources": packet_sources,
                  "selected_acceptance": selected_acceptance, "scope_files": sorted(scoped_files),
                  "source_digests": state["documents"], "created_at": created_at}
        if state["profile_snapshot"]:
            packet["profiles"] = state["profiles"]
        canonical = json.dumps(packet, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        if len(canonical) > MAX_PACKET_BYTES:
            raise EngineError("packet_too_large", "task context packet exceeds the configured size bound", details={"bytes": len(canonical), "maximum": MAX_PACKET_BYTES})
        packet["packet_sha256"] = hashlib.sha256(canonical).hexdigest()
        return packet

    def _restore_packet(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        self._fields(payload, ("run_id", "owner", "kind"), ("task_id", "phase_id"))
        run_id = self._nonempty(payload["run_id"], "run_id")
        owner = self._nonempty(payload["owner"], "owner")
        kind = payload["kind"]
        if kind not in {"task", "phase"}:
            raise EngineError("invalid_input", "restore-packet kind must be task or phase")
        if (kind == "task" and ("task_id" not in payload or "phase_id" in payload)) or (kind == "phase" and ("phase_id" not in payload or "task_id" in payload)):
            raise EngineError("invalid_input", "restore-packet requires exactly task_id or phase_id for its kind")
        try:
            state = self.store.read_state(run_id, self._reduce_events, repair=False)
        except StoreError as exc:
            raise EngineError(exc.code, str(exc)) from exc
        self._require_owner(state, owner)
        if getattr(self.adapter, "production", False):
            self._run_adapter_call(state, "assert_lease", state)
            self._run_adapter_call(state, "attest_session", owner, "orchestrator")
        self._ensure_approvals_current(state)
        if kind == "task":
            task_id = self._nonempty(payload["task_id"], "task_id")
            task_state = state.get("tasks", {}).get(task_id, {})
            if not task_state.get("attempt") or not task_state.get("packet_path") or not task_state.get("packet_sha256"):
                raise EngineError("packet_pin_missing", "task has no recorded packet pin to restore")
            created_at = task_state.get("packet_created_at")
            if not created_at:
                raise EngineError("packet_timestamp_unavailable", "the original task packet timestamp was not recorded; restore cannot invent one")
            packet = self._build_task_packet(state, run_id, task_id, task_state["attempt"], created_at,
                                             task_state.get("attempt_owner", owner))
            path = self._project_path(task_state["packet_path"])
            expected_hash = task_state["packet_sha256"]
            if packet["packet_sha256"] != expected_hash:
                raise EngineError("packet_restore_mismatch", "current approved sources or task scope do not reproduce the recorded task packet")
            restored = self._restore_task_packet_file(path, packet, expected_hash)
            return {"run_id": run_id, "kind": kind, "task_id": task_id, "packet_path": str(path),
                    "packet_sha256": expected_hash, "restored": restored, "attempt": task_state["attempt"]}
        phase_id = self._nonempty(payload["phase_id"], "phase_id")
        phase_state = state.get("phases", {}).get(phase_id, {})
        if phase_state.get("status") not in {"ready", "reviewed"} or not phase_state.get("packet_path") or not phase_state.get("packet_sha256"):
            raise EngineError("phase_packet_pin_missing", "phase has no ready packet pin to restore")
        return self._phase_controller().restore_packet(state, phase_id)

    def _restore_task_packet_file(self, path: Path, packet: Mapping[str, Any], expected_hash: str) -> bool:
        if path.exists():
            try:
                current = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, json.JSONDecodeError) as exc:
                raise EngineError("packet_corrupt", "existing task packet is unreadable; refusing to replace it") from exc
            actual = current.get("packet_sha256") if isinstance(current, dict) else None
            unhashed = {key: value for key, value in current.items() if key != "packet_sha256"} if isinstance(current, dict) else {}
            actual_content_hash = hashlib.sha256(json.dumps(unhashed, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
            if actual != expected_hash or actual_content_hash != expected_hash:
                raise EngineError("packet_corrupt", "existing task packet does not match its immutable event pin; refusing to replace it")
            return False
        if packet.get("packet_sha256") != expected_hash:
            raise EngineError("packet_restore_mismatch", "rebuilt task packet does not match its immutable event pin")
        self._write_immutable_json(path, packet)
        return True

    def _packet_source_projection(self, relative: str, contract: Mapping[str, Any], prose: str,
                                  task: Mapping[str, Any], state: Mapping[str, Any]) -> Dict[str, Any]:
        projected = dict(contract)
        if contract.get("kind") == "tasks":
            by_id = {item["id"]: item for item in state["task_contracts"]}
            selected: Set[str] = set()
            def add_task(identifier: str) -> None:
                if identifier in selected:
                    return
                selected.add(identifier)
                for dependency in by_id[identifier]["depends_on"]:
                    add_task(dependency)
            add_task(task["id"])
            projected["tasks"] = [item for item in contract["tasks"] if item["id"] in selected]
            prose = ""
        elif contract.get("kind") == "spec":
            acceptance_ids = set(task["acceptance"])
            criteria = [item for item in contract["acceptance"] if item["id"] in acceptance_ids]
            story_ids = {item["story"] for item in criteria}
            projected["acceptance"] = criteria
            projected["stories"] = [item for item in contract["stories"] if item["id"] in story_ids]
            # Scoped criteria can reference quality targets and examples in the prose.
            # Retain context from both existing specs and the current template.
            prose = self._packet_sections(prose, {
                "Release outcome", "Release-specific nonfunctional requirements",
                "Edge cases and non-goals", "Outcome measurement", "Open questions",
                "Purpose and selected release", "Users, context, and expected outcome",
                "Scope and exclusions", "Approved bases and constraints",
                "Rules, acceptance, and examples", "Quality and conditions of done",
                "Edge cases, errors, and compatibility", "Post-delivery measurement",
                "Assumptions, dependencies, and open questions",
            })
        elif contract.get("kind") == "plan":
            phases = {item["id"]: item for item in contract["phases"]}
            relevant: Set[str] = set()
            def add_phase(identifier: str) -> None:
                if identifier in relevant:
                    return
                relevant.add(identifier)
                for dependency in phases[identifier]["depends_on"]:
                    add_phase(dependency)
            phase = next(item for item in state["phase_contracts"] if item["id"] == task["phase"])
            add_phase(task["phase"])
            for dependency in phase["depends_on"]:
                add_phase(dependency)
            projected["phases"] = [item for item in contract["phases"] if item["id"] in relevant]
        elif contract.get("kind") == "roadmap":
            projected["releases"] = [item for item in contract.get("releases", []) if item.get("version") == state["release"]]
            prose = ""
        return {"contract": projected, "prose": prose}

    @staticmethod
    def _packet_sections(markdown: str, selected: Set[str]) -> str:
        output = []
        lines = markdown.splitlines()
        index = 0
        heading = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
        while index < len(lines):
            match = heading.match(lines[index])
            if not match or match.group(2).strip() not in selected:
                index += 1
                continue
            level = len(match.group(1))
            title = match.group(2).strip()
            body = []
            cursor = index + 1
            while cursor < len(lines):
                next_heading = heading.match(lines[cursor])
                if next_heading and len(next_heading.group(1)) <= level:
                    break
                body.append(lines[cursor])
                cursor += 1
            content = "\n".join(body).strip()
            if content:
                output.append(match.group(1) + " " + title + "\n\n" + content)
            index = cursor
        return "\n\n".join(output)

    def _bind_agent(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        self._fields(payload, ("run_id", "owner", "task_id", "agent_id", "session_id", "agent_path"))
        state = self._owned_state(payload)
        self._require_active_task(state, payload["task_id"])
        task_state = state.get("tasks", {}).get(payload["task_id"], {})
        if task_state.get("status") not in {"running", "reconciliation_required"} or task_state.get("agent"):
            raise EngineError("invalid_transition", "bind-agent requires one prepared attempt without a bound agent")
        agent_id = self._nonempty(payload["agent_id"], "agent_id")
        session_id = self._nonempty(payload["session_id"], "session_id")
        agent_path = self._nonempty(payload["agent_path"], "agent_path")
        if agent_id != agent_path:
            raise EngineError("host_agent_mismatch", "agent_id must equal the canonical agent_path returned by the native spawn response")
        marker = "SPEC_FLOW_PACKET_SHA256=" + task_state.get("packet_sha256", "")
        parent_session = task_state.get("attempt_owner", state["owner"])
        evidence = self._run_adapter_call(state, "attest_session", session_id, "implementer", parent_session=parent_session, agent_path=agent_path,
                                      task_marker=marker, after=task_state.get("prepared_at"))
        self._append(payload["run_id"], "agent_bound", {"task_id": payload["task_id"], "attempt": task_state["attempt"],
                                                          "agent_id": agent_id, "session_id": session_id,
                                                          "agent_path": agent_path, "parent_session": parent_session,
                                                          "attestation": evidence})
        return {"run_id": payload["run_id"], "task_id": payload["task_id"], "agent_id": agent_id, "session_id": session_id, "bound": True}

    def _result(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        self._fields(payload, ("run_id", "owner", "task_id", "result"))
        state = self._owned_state(payload)
        self._require_active_task(state, payload["task_id"])
        if state.get("tasks", {}).get(payload["task_id"], {}).get("status") not in {"running", "result_received"}:
            raise EngineError("invalid_transition", "result cannot be changed after verification or review")
        result = payload["result"]
        if not isinstance(result, dict) or not result:
            raise EngineError("invalid_input", "result must be a nonempty object")
        host_attestation = None
        if getattr(self.adapter, "production", False):
            host_attestation = self._validate_agent_result(payload["run_id"], payload["task_id"], state, result)
        self._append(payload["run_id"], "result_received", {"task_id": payload["task_id"], "result": result,
                                                               "host_attestation": host_attestation, "received_at": self._now()})
        return {"run_id": payload["run_id"], "task_id": payload["task_id"], "recorded": True, "closed": False}

    def _retry(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        self._fields(payload, ("run_id", "owner", "task_id", "reason", "hypothesis"))
        state = self._owned_state(payload)
        self._require_active_task(state, payload["task_id"])
        task_state = state["tasks"].get(payload["task_id"], {})
        if task_state.get("status") != "verification_failed":
            raise EngineError("retry_not_ready", "retry requires a failed verification result")
        reason = self._nonempty(payload["reason"], "reason")
        hypothesis = self._nonempty(payload["hypothesis"], "hypothesis")
        if task_state.get("attempt", 0) >= self._config()["retry_limit"]:
            raise EngineError("retry_limit", "task reached the maximum of {} attempts".format(self._config()["retry_limit"]))
        self._append(payload["run_id"], "retry_requested", {"task_id": payload["task_id"], "reason": reason, "hypothesis": hypothesis})
        return {"run_id": payload["run_id"], "task_id": payload["task_id"], "retry_ready": True}

    def _reconcile(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        self._fields(payload, ("run_id", "owner", "task_id", "disposition", "evidence"), ("result", "reason", "hypothesis", "native_inspection"))
        state = self._owned_state(payload)
        self._require_owner(state, payload["owner"])
        task_id = self._nonempty(payload["task_id"], "task_id")
        if state.get("active_task") != task_id or state.get("tasks", {}).get(task_id, {}).get("status") != "reconciliation_required":
            raise EngineError("reconciliation_not_required", "task has no interrupted attempt requiring reconciliation")
        evidence = self._nonempty(payload["evidence"], "evidence")
        task_state = state["tasks"][task_id]
        if payload["disposition"] == "no_spawn":
            native = None
            if getattr(self.adapter, "production", False):
                native = self._run_adapter_call(state, "attest_no_spawn", state["owner"], task_state, payload.get("native_inspection"))
                baseline = task_state.get("attempt_baseline", task_state.get("baseline", {}))
                changed = self._changed_paths(baseline, self._snapshot_code())
                if changed:
                    raise EngineError("no_spawn_worktree_changed", "task files changed after preparation; bind and reconcile the native child instead of claiming no spawn",
                                      details={"paths": sorted(changed)})
            self._append(payload["run_id"], "reconciled_no_spawn", {"task_id": task_id, "attempt": task_state["attempt"],
                "evidence": evidence, "native_attestation": native, "at": self._now()})
            return {"run_id": payload["run_id"], "task_id": task_id, "disposition": "no_spawn", "retry_ready": True}
        if getattr(self.adapter, "production", False):
            native = self._attest_bound_agent(state, task_id, task_state)
            if native.get("agent_lifecycle") not in {"completed", "aborted"}:
                raise EngineError("agent_still_active", "inspect or stop the native agent before reconciliation")
        if payload["disposition"] == "accept_result":
            result = payload.get("result")
            if not isinstance(result, dict) or not result:
                raise EngineError("invalid_input", "accept_result requires a nonempty result object")
            if getattr(self.adapter, "production", False):
                native = self._validate_agent_result(payload["run_id"], task_id, state, result, allowed_lifecycles={"completed", "aborted"})
            self._append(payload["run_id"], "reconciled_result", {"task_id": task_id, "result": result,
                                                                    "host_attestation": native if getattr(self.adapter, "production", False) else None,
                                                                    "evidence": evidence, "at": self._now()})
            return {"run_id": payload["run_id"], "task_id": task_id, "disposition": "accept_result"}
        if payload["disposition"] == "retry":
            reason = self._nonempty(payload.get("reason"), "reason")
            hypothesis = self._nonempty(payload.get("hypothesis"), "hypothesis")
            if task_state.get("attempt", 0) >= self._config()["retry_limit"]:
                raise EngineError("retry_limit", "task reached the maximum of {} attempts".format(self._config()["retry_limit"]))
            self._append(payload["run_id"], "reconciled_retry", {
                "task_id": task_id, "evidence": evidence, "reason": reason, "hypothesis": hypothesis,
            })
            return {"run_id": payload["run_id"], "task_id": task_id, "disposition": "retry", "retry_ready": True}
        raise EngineError("invalid_input", "reconciliation disposition must be accept_result, retry, or no_spawn")

    def _verify(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        self._fields(payload, ("run_id", "owner", "task_id"), ("inspection_evidence", "timeout_seconds"))
        state = self._owned_state(payload)
        self._require_active_task(state, payload["task_id"])
        self._ensure_approvals_current(state)
        task = self._task_contract(state, payload["task_id"])
        task_state = state["tasks"].get(payload["task_id"], {})
        if task_state.get("status") != "result_received" or not task_state.get("result"):
            raise EngineError("result_required", "record a nonempty result before verification")
        reported_blockers = task_state["result"].get("blockers", []) if isinstance(task_state.get("result"), dict) else []
        if reported_blockers:
            raise EngineError("agent_blocked", "agent reported unresolved blockers", details={"blockers": reported_blockers})
        attempt = task_state.get("attempt")
        baseline = task_state.get("baseline", {})
        before = self._snapshot_code()
        unauthorized = self._changed_paths(baseline, before) - self._allowed_paths(task)
        if unauthorized:
            self._verification_failure(payload["run_id"], payload["task_id"], "out_of_scope_changes", "changed files exceed task scope", {"paths": sorted(unauthorized)})
        timeout = payload.get("timeout_seconds", 60)
        if not isinstance(timeout, (int, float)) or timeout <= 0 or timeout > 300:
            raise EngineError("invalid_input", "timeout_seconds must be between 0 and 300")
        inspection_evidence = payload.get("inspection_evidence", {})
        if not isinstance(inspection_evidence, dict):
            raise EngineError("invalid_input", "inspection_evidence must be an object")
        outputs: List[Dict[str, Any]] = []
        source_digests = dict(state["documents"])
        for step in task["steps"]:
            verification = step["verification"]
            step_id = step["id"]
            if "command" in verification:
                try:
                    completed = subprocess.run(
                        verification["command"], cwd=str(self.root), shell=False, check=False,
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace",
                        timeout=timeout,
                    )
                except subprocess.TimeoutExpired as exc:
                    self._verification_failure(payload["run_id"], payload["task_id"], "verification_timeout", "verification step timed out: {}".format(step_id), {"output": str(exc.stdout or "")[-4000:]})
                except OSError as exc:
                    self._verification_failure(payload["run_id"], payload["task_id"], "verification_failed", "could not run verification step {}: {}".format(step_id, exc))
                # Verification commands are evidence-producing checks, not
                # implementation steps. Check immediately after every command
                # so a later step cannot restore and conceal an earlier edit.
                during = self._snapshot_code()
                mutated = self._changed_paths(before, during)
                if mutated:
                    self._verification_failure(payload["run_id"], payload["task_id"], "verification_mutated_code",
                                               "verification command changed project files: {}".format(step_id),
                                               {"paths": sorted(mutated)})
                output = completed.stdout or ""
                lowered = output.lower()
                if completed.returncode != 0:
                    self._verification_failure(payload["run_id"], payload["task_id"], "verification_failed", "verification command failed: {}".format(step_id), {"exit_code": completed.returncode, "output": output[-4000:]})
                if not output.strip():
                    self._verification_failure(payload["run_id"], payload["task_id"], "verification_empty", "verification produced no output: {}".format(step_id))
                if any(pattern in lowered for pattern in ZERO_TEST_PATTERNS):
                    self._verification_failure(payload["run_id"], payload["task_id"], "verification_empty_suite", "verification reported no tests executed: {}".format(step_id), {"output": output[-4000:]})
                observed = output[-4000:]
                exit_code = completed.returncode
            else:
                evidence = inspection_evidence.get(step_id)
                if not isinstance(evidence, str) or not evidence.strip():
                    raise EngineError("inspection_evidence_required", "inspection step requires explicit evidence: {}".format(step_id))
                output = evidence.strip()
                observed = evidence.strip()
                exit_code = None
            if not output.strip():
                self._verification_failure(payload["run_id"], payload["task_id"], "verification_empty", "verification evidence is empty: {}".format(step_id))
            outputs.append({
                "step_id": step_id, "command": verification.get("command"), "inspection": verification.get("inspection"),
                "expected": verification["expected"], "observed": observed, "exit_code": exit_code,
                "output": output[-4000:], "output_sha256": hashlib.sha256(output.encode("utf-8")).hexdigest(),
                "source_digests": source_digests,
            })
        after = self._snapshot_code()
        unauthorized = self._changed_paths(baseline, after) - self._allowed_paths(task)
        if unauthorized:
            self._verification_failure(payload["run_id"], payload["task_id"], "out_of_scope_changes", "verification changed files outside task scope", {"paths": sorted(unauthorized)})
        fingerprint = self._scope_fingerprint(after, self._task_scope_files(state, task))
        for output in outputs:
            output["code_fingerprint"] = fingerprint
        evidence_path = self.store.run_dir(payload["run_id"]) / "evidence" / "{}-{}-verify.json".format(payload["task_id"], attempt)
        self.store.write_json_atomic(evidence_path, {"task_id": payload["task_id"], "attempt": attempt, "steps": outputs, "code_fingerprint": fingerprint})
        self._append(payload["run_id"], "verified", {
            "task_id": payload["task_id"], "attempt": attempt, "steps": outputs,
            "code_fingerprint": fingerprint, "evidence_path": evidence_path.relative_to(self.root).as_posix(),
            "verified_snapshot": after, "source_digests": state["documents"],
        })
        return {"run_id": payload["run_id"], "task_id": payload["task_id"], "passed": True, "steps": outputs, "evidence_path": str(evidence_path)}

    def _review(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        self._fields(payload, ("run_id", "owner", "task_id", "verdict", "evidence"))
        state = self._owned_state(payload)
        self._require_active_task(state, payload["task_id"])
        verdict = payload["verdict"]
        if verdict not in {"pass", "changes"}:
            raise EngineError("invalid_input", "review verdict must be pass or changes")
        evidence = self._nonempty(payload["evidence"], "evidence")
        task_state = state["tasks"].get(payload["task_id"], {})
        if task_state.get("status") != "verified" or not task_state.get("step_evidence"):
            raise EngineError("verification_required", "task requires current verification before review")
        self._ensure_evidence_current(state, payload["task_id"], task_state)
        self._ensure_approvals_current(state)
        self._append(payload["run_id"], "reviewed", {"task_id": payload["task_id"], "verdict": verdict, "evidence": evidence, "reviewed_at": self._now()})
        return {"run_id": payload["run_id"], "task_id": payload["task_id"], "verdict": verdict}

    def _verification_failure(self, run_id: str, task_id: str, code: str, message: str, details: Optional[Mapping[str, Any]] = None) -> None:
        self._append(run_id, "verification_failed", {
            "task_id": task_id, "code": code, "message": message, "details": dict(details or {}),
        })
        raise EngineError(code, message, details=details)

    def _close(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        self._fields(payload, ("run_id", "owner", "task_id"))
        state = self._owned_state(payload)
        self._require_owner(state, payload["owner"])
        task_id = self._nonempty(payload["task_id"], "task_id")
        task_state = state["tasks"].get(task_id, {})
        if task_state.get("status") == "completed":
            self._update_task_progress(state)
            return {"run_id": payload["run_id"], "task_id": task_id, "status": "completed", "already_completed": True, "run_dir": str(self.store.run_dir(payload["run_id"]))}
        self._require_active_task(state, task_id)
        if (task_state.get("review") or {}).get("verdict") != "pass":
            raise EngineError("review_required", "a passing review is required before close")
        self._ensure_evidence_current(state, task_id, task_state)
        self._ensure_approvals_current(state)
        self._append(payload["run_id"], "closed", {"task_id": task_id, "closed_at": self._now(), "run_completed": False})
        updated_state = self._state(payload["run_id"])
        self._update_task_progress(updated_state)
        return {
            "run_id": payload["run_id"], "task_id": task_id,
            "status": "completed", "already_completed": False, "run_completed": False,
            "run_dir": str(self.store.run_dir(payload["run_id"])),
            "tasks_digest": document_digest(self._release_path(state["release"], "tasks.md")),
        }

    def _abandon(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        self._fields(payload, ("run_id", "owner", "reason", "authorization"))
        run_id = self._nonempty(payload["run_id"], "run_id")
        owner = self._nonempty(payload["owner"], "owner")
        reason = self._nonempty(payload["reason"], "reason")
        authorization = self._authorization(payload["authorization"])
        state = self._state(run_id)
        self._require_owner(state, owner)
        if state.get("status") == "abandoned":
            if getattr(self.adapter, "production", False):
                self._run_adapter_call(state, "release", state)
            return {"run_id": run_id, "status": "abandoned", "already_abandoned": True, "history_preserved": True}
        if state.get("status") not in {"active", "interrupted", "completed"}:
            raise EngineError("run_not_abandonable", "only an active, interrupted, or closure-pending run can be abandoned")
        if state.get("release_review"):
            raise EngineError("run_not_abandonable", "a run with a final release-review audit cannot be abandoned")
        unresolved_task = None
        if state.get("active_task"):
            task_id = state["active_task"]
            task_state = state.get("tasks", {}).get(task_id, {})
            if task_state.get("status") != "verification_failed" or task_state.get("attempt", 0) < self._config()["retry_limit"]:
                raise EngineError("active_task_requires_reconciliation", "inspect and reconcile the active native task before abandoning the run",
                                  details={"task_id": task_id, "task_status": task_state.get("status")})
            unresolved_task = {"task_id": task_id, "status": task_state["status"], "attempt": task_state["attempt"],
                               "host_attestation": None}
        if getattr(self.adapter, "production", False):
            self._run_adapter_call(state, "assert_lease", state)
            self._run_adapter_call(state, "attest_session", owner, "orchestrator")
            if unresolved_task:
                native = self._attest_bound_agent(state, task_id, task_state)
                if native.get("agent_lifecycle") not in {"completed", "aborted"}:
                    raise EngineError("agent_still_active", "inspect or stop the native agent before abandoning an exhausted failed task")
                unresolved_task["host_attestation"] = native
        abandonment = {"reason": reason, "authorization": authorization, "abandoned_at": self._now()}
        if unresolved_task:
            abandonment["unresolved_task"] = unresolved_task
        self._append(run_id, "abandoned", abandonment)
        updated = self._state(run_id)
        self._run_adapter_call(updated, "release", updated)
        return {"run_id": run_id, "status": "abandoned", "already_abandoned": False, "history_preserved": True}

    def _interrupt(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        self._fields(payload, ("run_id", "owner"))
        state = self._owned_state(payload)
        self._require_owner(state, payload["owner"])
        if state["status"] not in {"active", "interrupted"}:
            raise EngineError("run_not_active", "only an active run can be interrupted")
        if state["status"] == "interrupted":
            return {"run_id": payload["run_id"], "status": "interrupted", "already_interrupted": True}
        self._append(payload["run_id"], "interrupted", {"interrupted_at": self._now()})
        return {"run_id": payload["run_id"], "status": "interrupted", "reconciliation_required": bool(state.get("active_task"))}

    def _resume(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        self._fields(payload, ("run_id", "owner"))
        try:
            self.store.read_state(payload["run_id"], self._reduce_events, repair=True)
        except StoreError as exc:
            raise EngineError(exc.code, str(exc)) from exc
        state = self._owned_state(payload)
        self._require_owner(state, payload["owner"])
        if state["status"] != "interrupted":
            raise EngineError("run_not_interrupted", "only an interrupted run can be resumed")
        agent_status = None
        if getattr(self.adapter, "production", False) and state.get("active_task"):
            task_state = state["tasks"].get(state["active_task"], {})
            if task_state.get("agent"):
                agent_status = self._attest_bound_agent(state, state["active_task"], task_state)
        self._append(payload["run_id"], "resumed", {"resumed_at": self._now()})
        active_task = state.get("active_task")
        if active_task:
            task_state = state["tasks"].get(active_task, {})
            if not task_state.get("result"):
                self._append(payload["run_id"], "reconciliation_required", {"task_id": active_task, "reason": "attempt interrupted before an agent result was recorded"})
        imported = self._credit_migrated_evidence(payload["run_id"], state["release"], state["task_contracts"])
        new_state = self._state(payload["run_id"])
        self._update_task_progress(new_state)
        return {"run_id": payload["run_id"], "status": new_state["status"], "reconciliation_required": bool(new_state.get("active_task")),
                "native_agent": agent_status,
                "imported_completed": imported["completed"], "pending_imports": imported["pending"]}

    def _takeover(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        self._fields(payload, ("run_id", "previous_owner", "owner", "reconciliation"))
        run_id = self._nonempty(payload["run_id"], "run_id")
        previous_owner = self._nonempty(payload["previous_owner"], "previous_owner")
        owner = self._nonempty(payload["owner"], "owner")
        reconciliation = self._nonempty(payload["reconciliation"], "reconciliation")
        state = self._state(run_id)
        self._require_owner(state, previous_owner)
        if state.get("status") != "interrupted":
            raise EngineError("takeover_requires_interrupted_run", "takeover requires an interrupted run")
        result = self._run_adapter_call(state, "takeover", state, owner)
        self._append(run_id, "ownership_transferred", {"previous_owner": previous_owner, "owner": owner,
                                                        "reconciliation": reconciliation,
                                                        "host_inspection": result, "transferred_at": self._now()})
        return {"run_id": run_id, "owner": owner, "authorized_phases": state["authorized_phases"],
                "reconciliation_required": bool(state.get("active_task")), "resume_required": True}

    def _status(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        self._fields(payload, (), ("run_id",))
        config = self._config(required=False)
        if config is None:
            return {"status": "uninitialized", "initialized": False, "runs": []}
        if "run_id" in payload:
            try:
                state = self.store.read_state(payload["run_id"], self._reduce_events, repair=False)
            except StoreError as exc:
                raise EngineError(exc.code, str(exc)) from exc
            return state
        runs = []
        for run_id in self.store.run_ids():
            try:
                state = self.store.read_state(run_id, self._reduce_events, repair=False)
            except StoreError as exc:
                raise EngineError(exc.code, str(exc)) from exc
            runs.append({"run_id": run_id, "release": state["release"], "status": state["status"], "owner": state["owner"]})
        return {"status": "initialized", "initialized": True, "runs": runs}

    def _authorization(self, value: Any) -> Dict[str, str]:
        if not isinstance(value, dict) or set(value) != {"actor", "statement", "source"}:
            raise EngineError("invalid_input", "authorization requires actor, statement, and source")
        return {key: self._nonempty(value[key], "authorization." + key) for key in ("actor", "statement", "source")}

    def _append(self, run_id: str, event: str, data: Mapping[str, Any]) -> None:
        try:
            self.store.append_event(run_id, event, {**dict(data), "at": self._now()}, self._reduce_events)
        except StoreError as exc:
            raise EngineError(exc.code, str(exc)) from exc

    def _run_adapter_call(self, state: Mapping[str, Any], method: str, *args: Any, **kwargs: Any) -> Any:
        return self._adapter_call(method, *args, profiles=state["profiles"],
                                  require_catalog=state["profile_snapshot"], **kwargs)

    def _adapter_call(self, method: str, *args: Any, profiles=None, require_catalog=False, **kwargs: Any) -> Any:
        configure = getattr(self.adapter, "configure_profiles", None)
        if configure is None and getattr(self.adapter, "production", False):
            raise EngineError("adapter_unavailable", "production adapter must support explicit role profile binding")
        if configure is not None:
            try:
                configure(validate_profiles(profiles), require_catalog=require_catalog)
            except (ValueError, AdapterError) as exc:
                raise EngineError("invalid_profiles", str(exc)) from exc
        callback = getattr(self.adapter, method, None)
        if callback is None:
            raise EngineError("adapter_unavailable", "native Codex adapter does not support {}".format(method))
        try:
            return callback(*args, **kwargs)
        except AdapterError as exc:
            raise EngineError(exc.code, str(exc), details=exc.details) from exc

    def _state(self, run_id: str) -> Dict[str, Any]:
        try:
            state = self.store.read_state(run_id, self._reduce_events, repair=False)
        except StoreError as exc:
            raise EngineError(exc.code, str(exc)) from exc
        active_task = state.get("active_task")
        task_state = state.get("tasks", {}).get(active_task, {}) if active_task else {}
        packet_path = task_state.get("packet_path")
        packet_sha = task_state.get("packet_sha256")
        if packet_path and packet_sha:
            path = self._project_path(packet_path)
            try:
                packet = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, json.JSONDecodeError) as exc:
                raise EngineError("packet_corrupt", "active attempt packet is unavailable or unreadable") from exc
            unhashed = {key: value for key, value in packet.items() if key != "packet_sha256"} if isinstance(packet, dict) else {}
            actual_sha = hashlib.sha256(json.dumps(unhashed, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
            if (not isinstance(packet, dict) or actual_sha != packet_sha or packet.get("run_id") != run_id
                    or packet.get("task_id") != active_task or packet.get("attempt") != task_state.get("attempt")
                    or not isinstance(packet.get("created_at"), str) or not packet["created_at"]):
                raise EngineError("packet_corrupt", "active attempt packet does not match its immutable event pin")
            if ((state["profile_snapshot"] and packet.get("profiles") != state["profiles"])
                    or (not state["profile_snapshot"] and "profiles" in packet)):
                raise EngineError("packet_profile_mismatch", "active packet profiles differ from the pinned run")
            # Older prepared events did not persist a separate prepared_at field.
            # Recover the exact immutable packet timestamp without changing the
            # event log or allowing a child predating this attempt to bind.
            task_state["prepared_at"] = packet["created_at"]
        return state

    def _owned_state(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        run_id = self._nonempty(payload.get("run_id"), "run_id")
        owner = self._nonempty(payload.get("owner"), "owner")
        state = self._state(run_id)
        self._require_owner(state, owner)
        if getattr(self.adapter, "production", False):
            self._run_adapter_call(state, "assert_lease", state)
            self._run_adapter_call(state, "attest_session", owner, "orchestrator")
        return state

    def _attest_bound_agent(self, state: Mapping[str, Any], task_id: str, task_state: Mapping[str, Any]) -> Dict[str, Any]:
        bound = task_state.get("agent")
        if not isinstance(bound, dict):
            raise EngineError("agent_binding_required", "task reconciliation requires a bound native implementer session")
        marker = "SPEC_FLOW_PACKET_SHA256=" + task_state.get("packet_sha256", "")
        return self._run_adapter_call(state, "attest_session", bound["session_id"], "implementer", parent_session=bound.get("parent_session", state["owner"]),
                                  agent_path=bound["agent_path"], task_marker=marker,
                                  after=task_state.get("prepared_at"))

    def _validate_agent_result(self, run_id: str, task_id: str, state: Mapping[str, Any], result: Mapping[str, Any],
                               *, allowed_lifecycles: Set[str] = frozenset({"completed"})) -> Dict[str, Any]:
        required = {"summary", "files_modified", "checks", "evidence", "blockers"}
        if set(result) != required or not isinstance(result.get("files_modified"), list) or not isinstance(result.get("checks"), list) or not isinstance(result.get("evidence"), list) or not isinstance(result.get("blockers"), list):
            raise EngineError("invalid_agent_result", "native agent result requires summary, files_modified, checks, evidence, and blockers")
        task_state = state["tasks"].get(task_id, {})
        evidence = self._attest_bound_agent(state, task_id, task_state)
        if evidence.get("agent_lifecycle") not in allowed_lifecycles:
            raise EngineError("agent_not_completed", "native agent lifecycle is not eligible to submit this task result")
        baseline = task_state.get("baseline", {})
        actual = self._changed_paths(baseline, self._snapshot_code())
        reported = result["files_modified"]
        if not all(isinstance(path, str) and path and Path(path).as_posix() == path and not Path(path).is_absolute() and ".." not in Path(path).parts for path in reported) or len(set(reported)) != len(reported) or set(reported) != actual:
            raise EngineError("agent_file_report_mismatch", "agent-reported files must match the actual worktree changes", details={"reported": sorted(set(reported)), "actual": sorted(actual)})
        task = self._task_contract(state, task_id)
        checks = result["checks"]
        if not isinstance(result.get("summary"), str) or not result["summary"].strip() or not checks or not result["evidence"]:
            raise EngineError("invalid_agent_result", "agent result needs a summary, checks, and evidence")
        if not all(isinstance(item, dict) and all(isinstance(item.get(key), str) and item[key].strip() for key in ("step_id", "check", "result")) for item in checks):
            raise EngineError("invalid_agent_result", "each check requires step_id, check, and result strings")
        if {item["step_id"] for item in checks} != {step["id"] for step in task["steps"]}:
            raise EngineError("invalid_agent_result", "checks must cover each task step exactly once")
        if not all(isinstance(item, dict) and all(isinstance(item.get(key), str) and item[key].strip() for key in ("kind", "reference", "description")) for item in result["evidence"]):
            raise EngineError("invalid_agent_result", "each evidence item requires kind, reference, and description strings")
        if not all(isinstance(item, dict) and all(isinstance(item.get(key), str) and item[key].strip() for key in ("summary", "reason")) for item in result["blockers"]):
            raise EngineError("invalid_agent_result", "each blocker requires summary and reason strings")
        return evidence

    @staticmethod
    def _require_owner(state: Mapping[str, Any], owner: str) -> None:
        if state.get("owner") != owner:
            raise EngineError("wrong_owner", "operation owner does not match the run owner")

    @staticmethod
    def _require_active(state: Mapping[str, Any]) -> None:
        if state.get("status") != "active":
            raise EngineError("run_not_active", "run is not active")

    def _require_active_task(self, state: Mapping[str, Any], task_id: Any) -> None:
        self._require_active(state)
        task_id = self._nonempty(task_id, "task_id")
        if state.get("active_task") != task_id:
            raise EngineError("task_not_active", "task does not own the active attempt")

    @staticmethod
    def _task_contract(state: Mapping[str, Any], task_id: str) -> Dict[str, Any]:
        for task in state["task_contracts"]:
            if task["id"] == task_id:
                return task
        raise EngineError("task_not_found", "task is not part of the approved release: {}".format(task_id))

    def _ensure_approvals_current(self, state: Mapping[str, Any]) -> None:
        receipts = self._approval_map()
        for relative, digest in state["documents"].items():
            path = self._project_path(relative)
            if document_digest(path) != digest or not self._current_approval(path, receipts):
                raise EngineError("approval_stale", "approved source changed or approval is missing: {}".format(relative))
            try:
                closure = self._approval_closure(path)
            except EngineError as exc:
                if exc.code in {"contract_invalid", "dependency_cycle"}:
                    raise EngineError("approval_stale", "an approved document dependency is no longer valid") from exc
                raise
            for dependency in closure:
                dep_rel = dependency.relative_to(self.root).as_posix()
                if dep_rel not in state["documents"] or document_digest(dependency) != state["documents"][dep_rel] or not self._current_approval(dependency, receipts):
                    raise EngineError("approval_stale", "transitive approved source changed: {}".format(dep_rel))

    def _task_scope_files(self, state: Mapping[str, Any], task: Mapping[str, Any]) -> Set[str]:
        by_id = {item["id"]: item for item in state["task_contracts"]}
        result: Set[str] = set()

        def include(item: Mapping[str, Any]) -> None:
            for name in item["files"]:
                path = self._project_path(name)
                if path.is_dir():
                    raise EngineError("directory_scope_unsupported", "task scopes must enumerate files explicitly: {}".format(name))
                result.add(Path(name).as_posix())
            for dependency in item["depends_on"]:
                include(by_id[dependency])

        include(task)
        return result

    @staticmethod
    def _allowed_paths(task: Mapping[str, Any]) -> Set[str]:
        allowed: Set[str] = set()
        for name in task["files"]:
            normalized = Path(name).as_posix().rstrip("/")
            allowed.add(normalized)
        return allowed

    def _snapshot_code(self) -> Dict[str, str]:
        snapshot: Dict[str, str] = {}
        for directory, dirnames, filenames in os.walk(self.root, topdown=True, followlinks=False):
            kept_dirs = []
            for name in dirnames:
                path = Path(directory) / name
                relative = path.relative_to(self.root).as_posix()
                if any(part in CACHE_DIRS or part in EXCLUDED_TOP for part in Path(relative).parts):
                    continue
                if path.is_symlink():
                    payload = b"symlink:" + os.readlink(str(path)).encode("utf-8", errors="replace")
                    snapshot[relative] = hashlib.sha256(payload).hexdigest()
                    continue
                kept_dirs.append(name)
            dirnames[:] = kept_dirs
            for name in filenames:
                path = Path(directory) / name
                relative = path.relative_to(self.root).as_posix()
                if any(part in CACHE_DIRS or part in EXCLUDED_TOP for part in Path(relative).parts):
                    continue
                try:
                    if path.is_symlink():
                        payload = b"symlink:" + os.readlink(str(path)).encode("utf-8", errors="replace")
                    elif path.is_file():
                        payload = path.read_bytes()
                    else:
                        continue
                except OSError as exc:
                    raise EngineError("snapshot_failed", "could not snapshot {}: {}".format(relative, exc)) from exc
                snapshot[relative] = hashlib.sha256(payload).hexdigest()
        return snapshot

    @staticmethod
    def _changed_paths(before: Mapping[str, str], after: Mapping[str, str]) -> Set[str]:
        return {path for path in set(before) | set(after) if before.get(path) != after.get(path)}

    @staticmethod
    def _path_allowed(path: str, allowed: Set[str]) -> bool:
        return any(path == item or item.endswith("/") and path.startswith(item) for item in allowed)

    def _scope_fingerprint(self, snapshot: Mapping[str, str], files: Iterable[str]) -> Dict[str, Optional[str]]:
        result: Dict[str, Optional[str]] = {}
        for filename in files:
            safe_path(self.root, filename)
            result[filename] = snapshot.get(filename)
        return dict(sorted(result.items()))

    def _ensure_evidence_current(self, state: Mapping[str, Any], task_id: str, task_state: Mapping[str, Any], *, enforce_snapshot: bool = True) -> None:
        if enforce_snapshot:
            verified_snapshot = task_state.get("verified_snapshot")
            if not isinstance(verified_snapshot, dict):
                raise EngineError("verification_required", "task verification has no complete project snapshot")
            changed = self._changed_paths(verified_snapshot, self._snapshot_code())
            if changed:
                scope = self._task_scope_files(state, self._task_contract(state, task_id))
                outside = sorted(path for path in changed if not any(self._path_allowed(path, {item, item + "/"}) for item in scope))
                if outside:
                    raise EngineError("out_of_scope_changes", "project changed outside task scope after verification", details={"paths": outside})
                raise EngineError("code_stale", "task files changed after verification", details={"paths": sorted(changed)})
        expected = task_state.get("code_fingerprint")
        if not expected:
            raise EngineError("verification_required", "task has no recorded code fingerprint")
        current = self._scope_fingerprint(self._snapshot_code(), self._task_scope_files(state, self._task_contract(state, task_id)))
        if current != expected:
            changed = sorted(path for path in set(current) | set(expected) if current.get(path) != expected.get(path))
            raise EngineError("code_stale", "task files changed after verification", details={"paths": changed})

    def _update_task_progress(self, state: Mapping[str, Any], closing_task: Optional[str] = None) -> None:
        path = self._release_path(state["release"], "tasks.md")
        try:
            path = safe_path(self.root, path.relative_to(self.root))
            original = path.read_text(encoding="utf-8")
        except (ContractError, OSError, UnicodeError) as exc:
            raise EngineError("unsafe_path", "cannot update generated task progress: {}".format(exc)) from exc
        marker_start = "<!-- spec-flow:generated:start -->"
        marker_end = "<!-- spec-flow:generated:end -->"
        existing = re.search(r"\n<!-- spec-flow:generated:start -->.*?<!-- spec-flow:generated:end -->(?:\r?\n)*\Z", original, re.DOTALL)
        base = original[:existing.start()] if existing else original
        completed = {task_id for task_id, info in state["tasks"].items() if info.get("status") == "completed"}
        if closing_task:
            completed.add(closing_task)
        lines = ["- [{}] {}".format("x" if task["id"] in completed else " ", task["id"]) for task in state["task_contracts"]]
        updated = base.rstrip("\r\n") + "\n\n" + marker_start + "\n" + "\n".join(lines) + "\n" + marker_end + "\n"
        fd, name = tempfile.mkstemp(prefix="." + path.name + ".", dir=str(path.parent))
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                stream.write(updated)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(name, path)
            Store._fsync_directory(path.parent)
        finally:
            if os.path.exists(name):
                os.unlink(name)

    def _write_immutable_json(self, path: Path, value: Mapping[str, Any]) -> None:
        if path.exists():
            try:
                previous = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError, UnicodeError) as exc:
                raise EngineError("packet_corrupt", "existing immutable packet is unreadable") from exc
            stable_keys = ("run_id", "task_id", "attempt", "owner", "task", "sources", "scope_files")
            if not isinstance(previous, dict) or any(previous.get(key) != value.get(key) for key in stable_keys):
                raise EngineError("packet_exists", "existing packet does not match the approved attempt")
            recorded_hash = previous.get("packet_sha256")
            unhashed = {key: item for key, item in previous.items() if key != "packet_sha256"}
            actual_hash = hashlib.sha256(json.dumps(unhashed, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
            if recorded_hash != actual_hash:
                raise EngineError("packet_corrupt", "existing immutable packet hash does not match its content")
            return
        try:
            safe_path(self.root, path.relative_to(self.root))
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("x", encoding="utf-8") as stream:
                json.dump(value, stream, ensure_ascii=False, sort_keys=True, indent=2)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            Store._fsync_directory(path.parent)
        except FileExistsError as exc:
            raise EngineError("packet_exists", "immutable packet already exists") from exc
        except (ContractError, OSError) as exc:
            raise EngineError("unsafe_path", "could not write immutable packet: {}".format(exc)) from exc

    @staticmethod
    def _reduce_events(events: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
        try:
            return Engine._reduce_event_rows(events)
        except StoreError:
            raise
        except (KeyError, TypeError, ValueError, AttributeError) as exc:
            raise StoreError("corrupt_log", "run event contains malformed fields") from exc

    @staticmethod
    def _reduce_event_rows(events: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
        state: Dict[str, Any] = {}
        for event in events:
            kind = event.get("event")
            data = event.get("data")
            if not isinstance(data, dict):
                raise StoreError("corrupt_log", "event data must be an object")
            if kind == "started":
                if state:
                    raise StoreError("corrupt_log", "run contains more than one start event")
                try:
                    pinned_profiles = validate_profiles(data["profiles"] if "profiles" in data else LEGACY_PROFILES)
                except ValueError as exc:
                    raise StoreError("corrupt_log", "invalid run profile snapshot: {}".format(exc)) from exc
                state = {
                    "profiles": pinned_profiles, "profile_snapshot": "profiles" in data,
                    "run_id": data["run_id"], "release": data["release"], "owner": data["owner"],
                    "status": "active", "authorized_phases": list(data["authorized_phases"]),
                    "authorization": [data["authorization"]], "capabilities": data["capabilities"],
                    "documents": dict(data["documents"]), "task_ids": list(data["task_ids"]),
                    "task_contracts": list(data["task_contracts"]), "phase_contracts": list(data["phase_contracts"]),
                    "tasks": {}, "phases": {}, "active_task": None, "migration_evidence_pending": [],
                    "prior_attempts": dict(data.get("prior_attempts", {})),
                }
            elif not state:
                raise StoreError("corrupt_log", "run event precedes start event")
            elif kind == "authorized":
                state["authorized_phases"] = list(data["phases"])
                state["authorization"].append(data["authorization"])
            elif kind == "ownership_transferred":
                state["owner"] = data["owner"]
                state.setdefault("ownership_reconciliations", []).append({"previous_owner": data["previous_owner"],
                                                                           "owner": data["owner"],
                                                                           "reconciliation": data["reconciliation"],
                                                                           "at": data["transferred_at"]})
            elif kind == "prepared":
                task = state["tasks"].setdefault(data["task_id"], {})
                # Keep the first attempt baseline as the task's cumulative
                # authorization boundary; retries must not make earlier
                # out-of-scope edits disappear from later verification.
                original_baseline = task.get("baseline", data["baseline"])
                task.update({"attempt": data["attempt"], "status": "running", "packet_path": data["packet_path"],
                             "packet_sha256": data.get("packet_sha256"),
                             "prepared_at": data.get("prepared_at", data.get("at")),
                             "packet_created_at": data.get("prepared_at"),
                             "baseline": original_baseline, "attempt_baseline": data["baseline"], "scope_files": data["scope_files"],
                             "source_digests": data["source_digests"], "attempt_owner": data.get("attempt_owner", state["owner"]),
                             "agent": None, "result": None, "failure": None, "step_evidence": {}, "review": None,
                             "code_fingerprint": None, "verified_snapshot": None, "evidence_path": None,
                             "reconciliation_evidence": None, "no_spawn_attestation": None,
                             "retry_reason": None, "retry_hypothesis": None, "closed_at": None})
                state["active_task"] = data["task_id"]
                state["reconciliation_required"] = False
            elif kind == "agent_bound":
                task = state["tasks"].setdefault(data["task_id"], {})
                task["agent"] = {"agent_id": data["agent_id"], "session_id": data["session_id"],
                                 "agent_path": data["agent_path"], "parent_session": data.get("parent_session"),
                                 "attestation": data["attestation"]}
            elif kind == "result_received":
                task = state["tasks"].setdefault(data["task_id"], {})
                task["result"] = data["result"]
                task["status"] = "result_received"
            elif kind == "reconciled_result":
                task = state["tasks"].setdefault(data["task_id"], {})
                task["result"] = data["result"]
                task["reconciliation_evidence"] = data["evidence"]
                task["status"] = "result_received"
            elif kind == "verification_failed":
                task = state["tasks"].setdefault(data["task_id"], {})
                task["failure"] = {"code": data["code"], "message": data["message"], "details": data.get("details", {})}
                task["status"] = "verification_failed"
            elif kind == "retry_requested":
                task = state["tasks"].setdefault(data["task_id"], {})
                task["status"] = "needs_changes"
                task["retry_reason"] = data["reason"]
                task["retry_hypothesis"] = data["hypothesis"]
                state["active_task"] = None
            elif kind == "reconciled_no_spawn":
                task = state["tasks"].setdefault(data["task_id"], {})
                task["status"] = "needs_changes"
                task["reconciliation_evidence"] = data["evidence"]
                task["no_spawn_attestation"] = data.get("native_attestation")
                state["active_task"] = None
                state["reconciliation_required"] = False
            elif kind == "reconciled_retry":
                task = state["tasks"].setdefault(data["task_id"], {})
                task["status"] = "needs_changes"
                task["reconciliation_evidence"] = data["evidence"]
                task["retry_reason"] = data["reason"]
                task["retry_hypothesis"] = data["hypothesis"]
                state["active_task"] = None
            elif kind == "verified":
                task = state["tasks"].setdefault(data["task_id"], {})
                task["step_evidence"] = {item["step_id"]: item for item in data["steps"]}
                task["code_fingerprint"] = data["code_fingerprint"]
                task["verified_snapshot"] = data["verified_snapshot"]
                task["evidence_path"] = data["evidence_path"]
                task["status"] = "verified"
                task["source_digests"] = dict(data.get("source_digests", {}))
            elif kind == "reviewed":
                task = state["tasks"].setdefault(data["task_id"], {})
                task["review"] = {"verdict": data["verdict"], "evidence": data["evidence"], "at": data["reviewed_at"]}
                if data["verdict"] == "pass":
                    task["status"] = "reviewed"
                else:
                    task["status"] = "needs_changes"
                    state["active_task"] = None
            elif kind == "task_evidence_refreshed":
                task = state["tasks"].setdefault(data["task_id"], {})
                task.update({"step_evidence": {item["step_id"]: item for item in data["steps"]},
                             "code_fingerprint": data["code_fingerprint"], "verified_snapshot": data["verified_snapshot"],
                             "source_digests": data["source_digests"], "evidence_path": data["evidence_path"]})
            elif kind == "phase_ready":
                state.setdefault("phases", {})[data["phase_id"]] = {"status": "ready", "parent": data["parent"],
                    "tree": data["tree"], "diff_sha256": data["diff_sha256"], "staged_paths": data["staged_paths"],
                    "source_digests": data["source_digests"], "packet_path": data["packet_path"],
                    "packet_sha256": data["packet_sha256"], "marker": data["marker"], "ready_at": data["at"],
                    "packet_created_at": data.get("packet_created_at"), "review": None}
            elif kind == "phase_reviewed":
                phase = state.setdefault("phases", {}).setdefault(data["phase_id"], {})
                phase["review"] = {key: data[key] for key in ("verdict", "reviewer_session", "reviewer_agent_id", "evidence", "review_packet_sha256", "host_attestation", "reviewed_at")}
                phase["status"] = "reviewed" if data["verdict"] == "pass" else "ready"
            elif kind == "phase_committed":
                phase = state.setdefault("phases", {}).setdefault(data["phase_id"], {})
                phase.update({"status": "committed", "commit": data["commit"], "receipt_path": data["receipt_path"]})
                if all(state.get("phases", {}).get(item["id"], {}).get("status") == "committed" for item in state["phase_contracts"]):
                    state["status"] = "completed"
            elif kind == "release_reviewed":
                state["release_review"] = {"record": data["record"], "roadmap_reference": data["roadmap_reference"], "reviewed_at": data["reviewed_at"]}
            elif kind == "closed":
                task = state["tasks"].setdefault(data["task_id"], {})
                task["status"] = "completed"
                task["closed_at"] = data["closed_at"]
                state["active_task"] = None
                state["reconciliation_required"] = False
            elif kind == "prior_run_credited":
                task = state["tasks"].setdefault(data["task_id"], {})
                task.update({"status": "completed", "step_evidence": {item["step_id"]: item for item in data["steps"]},
                             "code_fingerprint": data["code_fingerprint"], "verified_snapshot": data["verified_snapshot"],
                             "source_digests": dict(data["source_digests"]), "attempt": int(data.get("attempt", 0)),
                             "evidence_path": data["evidence_path"],
                             "review": data.get("review"), "prior_run_id": data["prior_run_id"], "closed_at": event.get("at")})
            elif kind == "abandoned":
                state["status"] = "abandoned"
                state["abandonment"] = {"reason": data["reason"], "authorization": data["authorization"],
                                         "abandoned_at": data["abandoned_at"]}
                if data.get("unresolved_task"):
                    state["abandonment"]["unresolved_task"] = data["unresolved_task"]
                    state["active_task"] = None
                    state["reconciliation_required"] = False
            elif kind == "migration_credited":
                task = state["tasks"].setdefault(data["task_id"], {})
                task.update({"status": "completed", "historical_evidence": list(data["steps"]),
                             "migration_ids": list(data["migration_ids"]), "closed_at": data["credited_at"],
                             "verified_snapshot": data["verified_snapshot"],
                             "code_fingerprint": data["code_fingerprint"]})
            elif kind == "interrupted":
                state["status"] = "interrupted"
            elif kind == "resumed":
                state["status"] = "active"
                state["reconciliation_required"] = bool(state.get("active_task"))
            elif kind == "reconciliation_required":
                state["reconciliation_required"] = True
                task = state["tasks"].setdefault(data["task_id"], {})
                task["status"] = "reconciliation_required"
            else:
                raise StoreError("corrupt_log", "unknown run event: {}".format(kind))
        if not state:
            raise StoreError("corrupt_log", "run has no start event")
        return state

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
