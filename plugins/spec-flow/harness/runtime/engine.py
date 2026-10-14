"""Deterministic project-local approval and run controller."""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Set, Tuple

from .contracts import ContractError, document_digest, read_document, safe_path, validate_document, validate_release
from .store import Store, StoreError


class EngineError(RuntimeError):
    def __init__(self, code: str, message: str, *, details: Optional[Mapping[str, Any]] = None):
        super().__init__(message)
        self.code = code
        self.details = dict(details or {})


PROFILES = {
    "orchestrator": {"id": "gpt-6-sol", "effort": "high"},
    "implementer": {"id": "gpt-6-luna", "effort": "high"},
    "reviewer": {"id": "gpt-6-sol", "effort": "high"},
}
CACHE_DIRS = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".tox", ".venv", "venv", "node_modules"}
EXCLUDED_TOP = {".git", ".specs", ".spec-flow"}
ZERO_TEST_PATTERNS = ("ran 0 tests", "no tests ran", "no tests to run")
PHASE_ALIASES = {
    "constitution": "constitution", "architecture": "architecture", "structure": "structure",
    "infrastructure": "infrastructure", "roadmap": "roadmap", "spec": "spec", "specify": "spec",
    "clarify": "clarify", "plan": "plan", "tasks": "tasks", "analyze": "analyze",
    "implement": "implement", "converge": "converge", "review-release": "review-release",
    "finishing-branch": "finishing-branch",
}


class Engine:
    def __init__(self, root: os.PathLike[str] | str):
        self.root = Path(root).resolve()
        if not self.root.is_dir():
            raise EngineError("invalid_root", "project root must be an existing directory")
        self.store = Store(self.root)

    def dispatch(self, operation: str, payload: Mapping[str, Any]) -> Dict[str, Any]:
        if not isinstance(payload, dict):
            raise EngineError("invalid_input", "operation input must be a JSON object")
        methods = {
            "initialize": self._initialize,
            "digest": self._digest,
            "validate": self._validate,
            "approve": self._approve,
            "gate": self._gate,
            "start": self._start,
            "authorize": self._authorize,
            "prepare": self._prepare,
            "result": self._result,
            "retry": self._retry,
            "reconcile": self._reconcile,
            "verify": self._verify,
            "review": self._review,
            "close": self._close,
            "resume": self._resume,
            "status": self._status,
            "interrupt": self._interrupt,
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
        if operation == "status":
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
        if (not isinstance(value, dict) or value.get("schema_version") != 1 or value.get("profiles") != PROFILES
                or type(value.get("retry_limit")) is not int or value.get("retry_limit") != 3):
            raise EngineError("invalid_config", "harness config has an unsupported schema or model profile")
        return value

    def _initialize(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        self._fields(payload, ())
        config_path = self._config_path()
        if config_path.exists():
            self._config()
            return {"status": "initialized", "config_path": str(config_path), "already_initialized": True}
        config = {"schema_version": 1, "profiles": PROFILES, "retry_limit": 3}
        self.store.write_json_atomic(config_path, config)
        (self.root / ".spec-flow" / "runs").mkdir(parents=True, exist_ok=True)
        return {"status": "initialized", "config_path": str(config_path), "already_initialized": False}

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
        self._config()
        version = self._release_version(payload["release"])
        owner = self._nonempty(payload["owner"], "owner")
        auth = self._authorization(payload["authorization"])
        if not isinstance(payload["capabilities"], dict):
            raise EngineError("invalid_input", "capabilities must be an object")
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
        for run_id in self.store.run_ids():
            try:
                existing = self.store.read_state(run_id, self._reduce_events)
            except StoreError as exc:
                raise EngineError(exc.code, str(exc)) from exc
            if existing["status"] in {"active", "interrupted"}:
                if existing["release"] == version and existing["owner"] == owner:
                    imported = self._credit_migrated_evidence(run_id, version, task_items)
                    current = self._state(run_id)
                    return {"run_id": run_id, "status": current["status"], "already_running": True,
                            "authorized_phases": current["authorized_phases"],
                            "imported_completed": imported["completed"], "pending_imports": imported["pending"]}
                raise EngineError("run_already_active", "another run owns the project")
            if existing["status"] == "completed" and existing["release"] == version and existing["owner"] == owner:
                return {"run_id": run_id, "status": "completed", "already_completed": True,
                        "authorized_phases": existing["authorized_phases"], "imported_completed": [], "pending_imports": []}
        run_id = str(uuid.uuid4())
        try:
            self.store.create_run(run_id)
            self.store.append_event(run_id, "started", {
                "run_id": run_id, "release": version, "owner": owner, "authorized_phases": list(dict.fromkeys(phases)),
                "authorization": auth, "capabilities": payload["capabilities"],
                "documents": {path.relative_to(self.root).as_posix(): document_digest(path) for path in self._document_closure(approval_roots)},
                "task_ids": [item["id"] for item in task_items], "task_contracts": task_items,
                "phase_contracts": validated["plan"]["contract"]["phases"],
            }, self._reduce_events)
            imported = self._credit_migrated_evidence(run_id, version, task_items)
        except StoreError as exc:
            raise EngineError(exc.code, str(exc)) from exc
        state = self._state(run_id)
        return {"run_id": run_id, "status": state["status"], "authorized_phases": list(dict.fromkeys(phases)),
                "imported_completed": imported["completed"], "pending_imports": imported["pending"]}

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
        for prior_phase in phase["depends_on"]:
            unfinished = [item["id"] for item in state["task_contracts"] if item["phase"] == prior_phase and state["tasks"].get(item["id"], {}).get("status") != "completed"]
            if unfinished:
                raise EngineError("phase_dependency_not_complete", "phase dependency still has open tasks: {}".format(", ".join(unfinished)))
        for dependency in task["depends_on"]:
            if state["tasks"].get(dependency, {}).get("status") != "completed":
                raise EngineError("task_dependency_not_complete", "task dependency is not complete: {}".format(dependency))
        self._ensure_approvals_current(state)
        attempt = int(task_state.get("attempt", 0)) + 1
        retry_limit = self._config()["retry_limit"]
        if attempt > retry_limit:
            raise EngineError("retry_limit", "task reached the maximum of {} attempts".format(retry_limit))
        baseline = self._snapshot_code()
        scoped_files = self._task_scope_files(state, task)
        release_docs = self._release_documents(state["release"])
        source_rows = []
        for path in release_docs:
            doc = read_document(path)
            source_rows.append({
                "path": path.relative_to(self.root).as_posix(),
                "digest": document_digest(path),
                "contract": doc["contract"],
                "prose": doc["prose"],
            })
        packet = {
            "run_id": payload["run_id"], "task_id": task_id, "attempt": attempt,
            "owner": state["owner"], "task": task, "sources": source_rows,
            "scope_files": sorted(scoped_files), "created_at": self._now(),
        }
        packet_path = self.store.run_dir(payload["run_id"]) / "packets" / "{}-{}.json".format(task_id, attempt)
        self._write_immutable_json(packet_path, packet)
        self._append(payload["run_id"], "prepared", {
            "task_id": task_id, "attempt": attempt, "packet_path": packet_path.relative_to(self.root).as_posix(),
            "baseline": baseline, "scope_files": sorted(scoped_files), "source_digests": state["documents"],
        })
        return {"run_id": payload["run_id"], "task_id": task_id, "attempt": attempt, "packet_path": str(packet_path), "scope_files": sorted(scoped_files)}

    def _result(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        self._fields(payload, ("run_id", "owner", "task_id", "result"))
        state = self._owned_state(payload)
        self._require_active_task(state, payload["task_id"])
        if state.get("tasks", {}).get(payload["task_id"], {}).get("status") not in {"running", "result_received"}:
            raise EngineError("invalid_transition", "result cannot be changed after verification or review")
        result = payload["result"]
        if not isinstance(result, dict) or not result:
            raise EngineError("invalid_input", "result must be a nonempty object")
        self._append(payload["run_id"], "result_received", {"task_id": payload["task_id"], "result": result, "received_at": self._now()})
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
        self._fields(payload, ("run_id", "owner", "task_id", "disposition", "evidence"), ("result", "reason", "hypothesis"))
        state = self._owned_state(payload)
        self._require_owner(state, payload["owner"])
        task_id = self._nonempty(payload["task_id"], "task_id")
        if state.get("active_task") != task_id or state.get("tasks", {}).get(task_id, {}).get("status") != "reconciliation_required":
            raise EngineError("reconciliation_not_required", "task has no interrupted attempt requiring reconciliation")
        evidence = self._nonempty(payload["evidence"], "evidence")
        task_state = state["tasks"][task_id]
        if payload["disposition"] == "accept_result":
            result = payload.get("result")
            if not isinstance(result, dict) or not result:
                raise EngineError("invalid_input", "accept_result requires a nonempty result object")
            self._append(payload["run_id"], "reconciled_result", {"task_id": task_id, "result": result, "evidence": evidence, "at": self._now()})
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
        raise EngineError("invalid_input", "reconciliation disposition must be accept_result or retry")

    def _verify(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        self._fields(payload, ("run_id", "owner", "task_id"), ("inspection_evidence", "timeout_seconds"))
        state = self._owned_state(payload)
        self._require_active_task(state, payload["task_id"])
        self._ensure_approvals_current(state)
        task = self._task_contract(state, payload["task_id"])
        task_state = state["tasks"].get(payload["task_id"], {})
        if task_state.get("status") != "result_received" or not task_state.get("result"):
            raise EngineError("result_required", "record a nonempty result before verification")
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
            "verified_snapshot": after,
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
        finished = all(state["tasks"].get(item, {}).get("status") == "completed" for item in state["task_ids"] if item != task_id)
        run_completed = finished
        self._append(payload["run_id"], "closed", {"task_id": task_id, "closed_at": self._now(), "run_completed": run_completed})
        updated_state = self._state(payload["run_id"])
        self._update_task_progress(updated_state)
        return {
            "run_id": payload["run_id"], "task_id": task_id,
            "status": "completed", "already_completed": False, "run_completed": run_completed,
            "run_dir": str(self.store.run_dir(payload["run_id"])),
            "tasks_digest": document_digest(self._release_path(state["release"], "tasks.md")),
        }

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
                "imported_completed": imported["completed"], "pending_imports": imported["pending"]}

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

    def _state(self, run_id: str) -> Dict[str, Any]:
        try:
            return self.store.read_state(run_id, self._reduce_events, repair=False)
        except StoreError as exc:
            raise EngineError(exc.code, str(exc)) from exc

    def _owned_state(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        run_id = self._nonempty(payload.get("run_id"), "run_id")
        owner = self._nonempty(payload.get("owner"), "owner")
        state = self._state(run_id)
        self._require_owner(state, owner)
        return state

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
            result.update(item["files"])
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
            allowed.add(normalized + "/")
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

    def _ensure_evidence_current(self, state: Mapping[str, Any], task_id: str, task_state: Mapping[str, Any]) -> None:
        verified_snapshot = task_state.get("verified_snapshot")
        if not isinstance(verified_snapshot, dict):
            raise EngineError("verification_required", "task verification has no complete project snapshot")
        changed = self._changed_paths(verified_snapshot, self._snapshot_code())
        if changed:
            scope = self._task_scope_files(state, self._task_contract(state, task_id))
            outside = sorted(path for path in changed if not any(path == item or path.startswith(item.rstrip("/") + "/") for item in scope))
            if outside:
                raise EngineError("out_of_scope_changes", "project changed outside task scope after verification", details={"paths": outside})
            raise EngineError("code_stale", "task files changed after verification", details={"paths": sorted(changed)})
        expected = task_state.get("code_fingerprint")
        if not expected:
            raise EngineError("verification_required", "task has no recorded code fingerprint")
        current = self._scope_fingerprint(self._snapshot_code(), self._task_scope_files(state, self._task_contract(state, task_id)))
        if current != expected:
            raise EngineError("code_stale", "task files changed after verification")

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
                state = {
                    "run_id": data["run_id"], "release": data["release"], "owner": data["owner"],
                    "status": "active", "authorized_phases": list(data["authorized_phases"]),
                    "authorization": [data["authorization"]], "capabilities": data["capabilities"],
                    "documents": dict(data["documents"]), "task_ids": list(data["task_ids"]),
                    "task_contracts": list(data["task_contracts"]), "phase_contracts": list(data["phase_contracts"]),
                    "tasks": {}, "active_task": None, "migration_evidence_pending": [],
                }
            elif not state:
                raise StoreError("corrupt_log", "run event precedes start event")
            elif kind == "authorized":
                state["authorized_phases"] = list(data["phases"])
                state["authorization"].append(data["authorization"])
            elif kind == "prepared":
                task = state["tasks"].setdefault(data["task_id"], {})
                task.update({"attempt": data["attempt"], "status": "running", "packet_path": data["packet_path"],
                             "baseline": data["baseline"], "scope_files": data["scope_files"],
                             "source_digests": data["source_digests"], "result": None,
                             "step_evidence": {}, "review": None, "code_fingerprint": None})
                state["active_task"] = data["task_id"]
                state["reconciliation_required"] = False
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
            elif kind == "reviewed":
                task = state["tasks"].setdefault(data["task_id"], {})
                task["review"] = {"verdict": data["verdict"], "evidence": data["evidence"], "at": data["reviewed_at"]}
                if data["verdict"] == "pass":
                    task["status"] = "reviewed"
                else:
                    task["status"] = "needs_changes"
                    state["active_task"] = None
            elif kind == "closed":
                task = state["tasks"].setdefault(data["task_id"], {})
                task["status"] = "completed"
                task["closed_at"] = data["closed_at"]
                state["active_task"] = None
                state["reconciliation_required"] = False
                if data.get("run_completed"):
                    state["status"] = "completed"
            elif kind == "migration_credited":
                task = state["tasks"].setdefault(data["task_id"], {})
                task.update({"status": "completed", "historical_evidence": list(data["steps"]),
                             "migration_ids": list(data["migration_ids"]), "closed_at": data["credited_at"],
                             "verified_snapshot": data["verified_snapshot"],
                             "code_fingerprint": data["code_fingerprint"]})
                if all(state["tasks"].get(task_id, {}).get("status") == "completed" for task_id in state["task_ids"]):
                    state["status"] = "completed"
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
