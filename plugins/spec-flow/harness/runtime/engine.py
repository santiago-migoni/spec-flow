"""Deterministic approval controller for Spec-Flow documents."""

from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Set

from .contracts import ContractError, document_digest, safe_path, validate_document, validate_release
from .store import Store, StoreError


class EngineError(RuntimeError):
    def __init__(self, code: str, message: str, *, details: Optional[Mapping[str, Any]] = None):
        super().__init__(message)
        self.code = code
        self.details = dict(details or {})


PHASE_ALIASES = {
    "constitution": "constitution", "architecture": "architecture", "structure": "structure",
    "infrastructure": "infrastructure", "roadmap": "roadmap", "spec": "spec", "specify": "spec",
    "clarify": "clarify", "plan": "plan", "tasks": "tasks", "analyze": "analyze",
    "implement": "implement",
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
            "hook-check": self._hook_check,
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
        if operation == "hook-check":
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
        if not isinstance(value, dict) or value.get("schema_version") != 1:
            raise EngineError("invalid_config", "harness config has an unsupported schema")
        return value

    def _initialize(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        self._fields(payload, ())
        config_path = self._config_path()
        if config_path.exists():
            self._config()
            self._ensure_registry_gitignore()
            return {"status": "initialized", "config_path": str(config_path), "already_initialized": True}
        self.store.write_json_atomic(config_path, {"schema_version": 1})
        self._ensure_registry_gitignore()
        return {"status": "initialized", "config_path": str(config_path), "already_initialized": False}

    def _ensure_registry_gitignore(self) -> None:
        path = self.root / ".spec-flow" / ".gitignore"
        lines = ["# Spec-Flow local lock", "/lock"]
        existing = path.read_text(encoding="utf-8") if path.exists() else ""
        additions = [line for line in lines if line not in existing.splitlines()]
        if additions:
            with path.open("a", encoding="utf-8") as stream:
                if existing and not existing.endswith("\n"):
                    stream.write("\n")
                stream.write("\n".join(additions) + "\n")

    def _hook_check(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        """Read-only PreToolUse check: document prerequisites and registry protection only."""
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
                raise EngineError("protected_runtime_state", "Editing tools cannot write Spec-Flow registry or approval state")
            targets.append(relative)

        for relative in targets:
            parts = Path(relative).parts
            is_release_doc = len(parts) == 3 and parts[0] == ".specs" and parts[1].startswith("release-v") and parts[2] in {"spec.md", "plan.md", "tasks.md"}
            is_strategy_doc = len(parts) == 2 and parts[0] == ".specs" and parts[1] in {"architecture.md", "structure.md", "infrastructure.md", "roadmap.md"}
            if not (is_release_doc or is_strategy_doc):
                continue
            path = self._project_path(relative)
            contract: Dict[str, Any] = {"depends_on": []}
            if path.exists():
                try:
                    contract = validate_document(self.root, path)["contract"]
                except ContractError as exc:
                    raise EngineError("contract_invalid", str(exc)) from exc
            kind = Path(relative).stem
            for prerequisite in self._gate_prerequisites(kind, path, contract, self._infer_release(path)):
                self._require_approved(prerequisite)
        return {"allowed": True, "paths": targets}

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
        if not path.is_file():
            raise EngineError("dependency_not_approved", "prerequisite document is missing; write and approve it first: {}".format(path.relative_to(self.root).as_posix()))
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
            if phase in {"clarify", "analyze", "implement"}:
                self._validate_phase_documents(phase, payload.get("release"))
        else:
            raise EngineError("invalid_input", "gate requires a valid path, phase, or kind")
        receipts = self._approval_map()
        missing: List[str] = []
        invalid: List[Dict[str, str]] = []
        for item in prerequisites:
            if not item.is_file():
                relative = item.relative_to(self.root).as_posix()
                if relative not in missing:
                    missing.append(relative)
                continue
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
        if phase == "implement":
            return self._release_documents(release)
        return []

    def _validate_phase_documents(self, phase: str, release: Optional[str]) -> None:
        if phase == "clarify":
            path = self._release_path(release, "spec.md")
            try:
                validate_document(self.root, path)
            except ContractError as exc:
                raise EngineError("contract_invalid", str(exc)) from exc
        elif phase in {"analyze", "implement"}:
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

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
