"""Explicit, hash-pinned migration from legacy feature folders to releases."""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Set, Tuple

from .contracts import ContractError, document_digest, normalize_release, read_document, safe_path, validate_release
from .store import Store

LEGACY_RE = re.compile(r"^[0-9]{3}-.+$")


class MigrationError(RuntimeError):
    def __init__(self, code: str, message: str, details: Optional[Mapping[str, Any]] = None):
        super().__init__(message)
        self.code = code
        self.details = dict(details or {})


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class Migration:
    def __init__(self, root: Path, store: Store):
        self.root = Path(root).resolve()
        self.store = store

    def preview(self, mapping: Any, candidate_dir: Optional[str], replacements: Any = None,
                imports: Any = None) -> Dict[str, Any]:
        manifest = self._manifest(mapping, candidate_dir, replacements or [], imports or {})
        return {"manifest": manifest, "digest": sha(canonical(manifest))}

    def _manifest(self, mapping: Any, candidate_dir: Optional[str], replacements: Any,
                  imports: Any) -> Dict[str, Any]:
        mappings = self._mapping(mapping)
        replacements = self._replacements(replacements)
        sources, head = self._source_snapshot()
        found = sorted((Path(".specs") / p.name).as_posix() for p in self.specs.iterdir()
                       if p.is_dir() and LEGACY_RE.fullmatch(p.name))
        mapped = sorted(row["legacy"] for row in mappings)
        if found != mapped:
            missing, extra = sorted(set(found) - set(mapped)), sorted(set(mapped) - set(found))
            if missing:
                raise MigrationError("migration_mapping_required", "every legacy directory needs an explicit mapping", {"missing": missing})
            raise MigrationError("migration_mapping_invalid", "mapping contains an unknown legacy directory", {"unknown": extra})
        active = [row for row in mappings if "release" in row]
        candidate = Path(candidate_dir).expanduser().resolve() if candidate_dir else None
        files: List[Dict[str, str]] = []
        if active:
            if candidate is None:
                raise MigrationError("migration_candidate_required", "active releases require a candidate overlay")
            files = self._candidate_files(candidate)
        elif candidate and candidate.exists():
            if not candidate.is_dir():
                raise MigrationError("migration_candidate_invalid", "candidate path must be a directory")
        self._collisions(files, replacements, sources, candidate)
        allowed_root = {"constitution.md", "architecture.md", "structure.md", "infrastructure.md", "roadmap.md", "backlog.md"}
        active_dirs = {"release-" + row["release"] for row in active}
        for item in files:
            rel = Path(item["path"]).relative_to(".specs")
            if len(rel.parts) == 1 and rel.name not in allowed_root:
                raise MigrationError("migration_candidate_invalid", "candidate contains an unsupported root document: " + str(rel))
            if len(rel.parts) > 1 and rel.parts[0] not in active_dirs:
                raise MigrationError("migration_candidate_invalid", "candidate contains an unmapped release or nested path: " + str(rel))
            if len(rel.parts) > 1 and rel.parts[0] in active_dirs:
                if len(rel.parts) != 2 or rel.name not in {"spec.md", "plan.md", "tasks.md"}:
                    raise MigrationError("migration_candidate_invalid", "release overlay may contain only spec.md, plan.md, and tasks.md")
                if (self.specs / rel.parts[0]).exists():
                    raise MigrationError("migration_collision", "mapped release directory already exists: " + rel.parts[0])
        self._validate_overlay(mappings, replacements, candidate, files)
        imports_out = self._imports(imports, mappings, candidate, files, replacements, sources)
        seed = {"project_root": str(self.root), "git_head": head, "sources": sources,
                "mapping": mappings, "replacements": replacements,
                "candidate_dir": str(candidate) if candidate else None,
                "candidates": files, "imports": imports_out}
        ident = uuid.uuid5(uuid.NAMESPACE_URL, sha(canonical(seed))).hex
        return {"schema_version": 1, "migration_id": ident, **seed}

    @property
    def specs(self) -> Path:
        return safe_path(self.root, ".specs")

    def _mapping(self, value: Any) -> List[Dict[str, Any]]:
        if not isinstance(value, list) or not value:
            raise MigrationError("migration_mapping_invalid", "mapping must be a nonempty list")
        result, paths, releases = [], set(), set()
        for row in value:
            if not isinstance(row, dict):
                raise MigrationError("migration_mapping_invalid", "mapping entries must be objects")
            legacy = row.get("legacy")
            if not isinstance(legacy, str) or legacy != (Path(".specs") / Path(legacy).name).as_posix() or not LEGACY_RE.fullmatch(Path(legacy).name):
                raise MigrationError("migration_mapping_invalid", "legacy must name a direct .specs/NNN-name directory")
            path = safe_path(self.root, legacy)
            if not path.is_dir():
                raise MigrationError("migration_mapping_invalid", "legacy directory does not exist: " + legacy)
            if legacy in paths:
                raise MigrationError("migration_mapping_invalid", "legacy directories must be mapped once")
            paths.add(legacy)
            if set(row) == {"legacy", "archive"} and row.get("archive") is True:
                result.append({"legacy": legacy, "archive": True})
            elif set(row) == {"legacy", "release"}:
                try:
                    release = normalize_release(row["release"])
                except ContractError as exc:
                    raise MigrationError("migration_mapping_invalid", str(exc)) from exc
                if release in releases:
                    raise MigrationError("migration_mapping_invalid", "release mapping must be unique: " + release)
                releases.add(release)
                result.append({"legacy": legacy, "release": release})
            else:
                raise MigrationError("migration_mapping_invalid", "entry needs release or archive:true")
        return sorted(result, key=lambda item: item["legacy"])

    def _replacements(self, value: Any) -> List[Dict[str, str]]:
        if not isinstance(value, list):
            raise MigrationError("migration_mapping_invalid", "replacements must be a list")
        out, seen = [], set()
        for row in value:
            if not isinstance(row, dict) or set(row) != {"path", "source_sha256", "equivalence"}:
                raise MigrationError("migration_mapping_invalid", "replacement needs path, source_sha256, equivalence")
            path, digest, equivalence = row["path"], row["source_sha256"], row["equivalence"]
            if not isinstance(path, str) or not path.startswith(".specs/") or ".." in Path(path).parts:
                raise MigrationError("migration_mapping_invalid", "replacement path must be under .specs")
            if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
                raise MigrationError("migration_mapping_invalid", "replacement source hash must be SHA-256")
            if not isinstance(equivalence, dict) or path in seen:
                raise MigrationError("migration_mapping_invalid", "replacement needs unique path and explicit equivalence")
            safe_path(self.root, path)
            if (set(equivalence) != {"statement", "source_excerpt", "target_excerpt"} or
                    not all(isinstance(equivalence.get(k), str) and equivalence[k].strip()
                            for k in ("statement", "source_excerpt", "target_excerpt"))):
                raise MigrationError("migration_mapping_invalid", "equivalence requires statement and exact source/target excerpts")
            out.append({"path": path, "source_sha256": digest, "equivalence": equivalence})
            seen.add(path)
        return sorted(out, key=lambda row: row["path"])

    def _git(self, *args: str) -> bytes:
        try:
            return subprocess.run(["git", "-C", str(self.root), *args], check=True,
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout
        except (OSError, subprocess.CalledProcessError) as exc:
            raise MigrationError("migration_git_required", "migration requires a committed Git project") from exc

    def _source_snapshot(self) -> Tuple[List[Dict[str, str]], str]:
        if not self.specs.is_dir():
            raise MigrationError("migration_source_invalid", ".specs directory is missing")
        head = self._git("rev-parse", "HEAD").decode("ascii").strip()
        status = self._git("status", "--porcelain=v1", "--untracked-files=all", "--", ".specs").decode("utf-8", "replace")
        if status:
            raise MigrationError("migration_source_dirty", ".specs must exactly match Git HEAD", {"status": status.splitlines()})
        entries = self._git("ls-tree", "-r", "-z", "--full-tree", "HEAD", "--", ".specs").split(b"\0")
        tracked = {}
        for entry in filter(None, entries):
            meta, raw = entry.split(b"\t", 1)
            mode, kind, _ = meta.decode("ascii").split()
            path = raw.decode("utf-8")
            if mode not in {"100644", "100755"} or kind != "blob":
                raise MigrationError("migration_unsafe_source", "non-regular Git entry: " + path)
            tracked[path] = True
        result = []
        for directory, dirnames, filenames in os.walk(self.specs, followlinks=False):
            for name in dirnames:
                if (Path(directory) / name).is_symlink():
                    raise MigrationError("migration_unsafe_source", "symlink in .specs")
            for name in filenames:
                path = Path(directory) / name
                rel = path.relative_to(self.root).as_posix()
                if path.is_symlink() or not path.is_file() or rel not in tracked:
                    raise MigrationError("migration_source_dirty", "untracked or non-regular source: " + rel)
                data = path.read_bytes()
                if data != self._git("show", "HEAD:" + rel):
                    raise MigrationError("migration_source_dirty", "source bytes differ from Git HEAD: " + rel)
                result.append({"path": rel, "sha256": sha(data)})
        if set(tracked) != {item["path"] for item in result}:
            raise MigrationError("migration_source_dirty", "Git HEAD .specs inventory differs from disk")
        return sorted(result, key=lambda item: item["path"]), head

    def _candidate_files(self, candidate: Path) -> List[Dict[str, str]]:
        specs = candidate / ".specs"
        if not candidate.is_dir() or not specs.is_dir() or [p.name for p in candidate.iterdir()] != [".specs"]:
            raise MigrationError("migration_candidate_invalid", "candidate directory must contain only a .specs overlay")
        result = []
        for directory, dirs, files in os.walk(specs, followlinks=False):
            if any((Path(directory) / name).is_symlink() for name in [*dirs, *files]):
                raise MigrationError("migration_candidate_invalid", "candidate overlay cannot contain symlinks")
            for name in files:
                path = Path(directory) / name
                if not path.is_file():
                    raise MigrationError("migration_candidate_invalid", "candidate entries must be files")
                result.append({"path": (Path(".specs") / path.relative_to(specs)).as_posix(), "sha256": sha(path.read_bytes())})
        if not result:
            raise MigrationError("migration_candidate_invalid", "candidate overlay is empty")
        return sorted(result, key=lambda row: row["path"])

    def _collisions(self, files: Sequence[Mapping[str, str]], replacements: Sequence[Mapping[str, str]],
                    sources: Sequence[Mapping[str, str]], candidate: Optional[Path]) -> None:
        existing = {row["path"]: row["sha256"] for row in sources}
        replace = {row["path"]: row["source_sha256"] for row in replacements}
        targets = {row["path"] for row in files}
        if set(replace) - targets:
            raise MigrationError("migration_candidate_invalid", "replacement path is absent from candidate overlay")
        for path, digest in replace.items():
            if existing.get(path) != digest:
                raise MigrationError("migration_source_stale", "replacement source does not match Git HEAD: " + path)
            old = safe_path(self.root, path).read_text(encoding="utf-8")
            new = (candidate / path).read_text(encoding="utf-8") if candidate else ""
            replacement = next(row for row in replacements if row["path"] == path)
            self._validate_equivalence(replacement["equivalence"], old, new)
        conflicts = sorted(path for path in targets if path in existing and path not in replace)
        if conflicts:
            raise MigrationError("migration_collision", "candidate target already exists", {"paths": conflicts})

    def _validate_overlay(self, mappings: Sequence[Mapping[str, Any]], replacements: Sequence[Mapping[str, str]],
                          candidate: Optional[Path], files: Sequence[Mapping[str, str]]) -> None:
        active = [item for item in mappings if "release" in item]
        if not active:
            return
        mirror_temp = tempfile.TemporaryDirectory(prefix="spec-flow-migrate-")
        try:
            mirror = Path(mirror_temp.name)
            shutil.copytree(self.specs, mirror / ".specs")
            specs = candidate / ".specs"
            replace_paths = {row["path"] for row in replacements}
            for item in files:
                dest = mirror / item["path"]
                if item["path"] in replace_paths:
                    dest.unlink()
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(specs / Path(item["path"]).relative_to(".specs"), dest)
            for item in mappings:
                shutil.rmtree(mirror / item["legacy"], ignore_errors=True)
            listed = {item["path"] for item in files}
            for item in active:
                directory = "release-" + item["release"]
                required = {".specs/{}/{}".format(directory, name) for name in ("spec.md", "plan.md", "tasks.md")}
                if not required <= listed:
                    raise MigrationError("migration_candidate_invalid", "overlay must provide complete release " + item["release"])
                try:
                    validate_release(mirror, item["release"])
                except ContractError as exc:
                    raise MigrationError("migration_candidate_invalid", str(exc)) from exc
        finally:
            mirror_temp.cleanup()

    def _imports(self, imports: Any, mappings: Sequence[Mapping[str, Any]], candidate: Optional[Path],
                 files: Sequence[Mapping[str, str]], replacements: Sequence[Mapping[str, str]],
                 sources: Sequence[Mapping[str, str]]) -> Dict[str, List[Dict[str, Any]]]:
        if not isinstance(imports, dict) or set(imports) - {"approvals", "evidence"}:
            raise MigrationError("migration_import_invalid", "imports accepts approvals and evidence lists")
        out = {}
        for kind in ("approvals", "evidence"):
            entries = imports.get(kind, [])
            if not isinstance(entries, list):
                raise MigrationError("migration_import_invalid", kind + " imports must be a list")
            out[kind] = [self._one_import(kind, row, mappings, candidate, files, replacements, sources) for row in entries]
        return out

    def _one_import(self, kind: str, row: Any, mappings: Sequence[Mapping[str, Any]], candidate: Optional[Path],
                    candidates: Sequence[Mapping[str, str]], replacements: Sequence[Mapping[str, str]],
                    sources: Sequence[Mapping[str, str]]) -> Dict[str, Any]:
        if not isinstance(row, dict) or set(row) != {"source", "target", "equivalence"}:
            raise MigrationError("migration_import_invalid", "import entry needs source, target, and equivalence")
        source, target, equivalence = row["source"], row["target"], row["equivalence"]
        if not isinstance(source, str) or not source.strip() or not isinstance(target, str) or not target.strip():
            raise MigrationError("migration_import_invalid", "import source and target must be nonempty strings")
        if not isinstance(equivalence, dict):
            raise MigrationError("migration_import_invalid", "equivalence must provide mapped source and target excerpts")
        if not any(source.startswith(item["legacy"] + "/") for item in mappings):
            raise MigrationError("migration_import_invalid", "import source must be inside a mapped legacy directory")
        source_path = safe_path(self.root, source)
        try:
            raw = source_path.read_bytes()
            record = json.loads(raw.decode("utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise MigrationError("migration_import_invalid", "import source must be JSON") from exc
        item: Dict[str, Any] = {"source": source, "target": target, "equivalence": equivalence,
                                "source_sha256": sha(raw), "record": record, "status": "pending"}
        if kind == "approvals":
            item.update(self._classify_approval(item, mappings, replacements, candidate, candidates))
        else:
            item.update(self._classify_evidence(item, mappings, candidate, candidates, sources))
        return item

    def _classify_approval(self, item: Mapping[str, Any], mappings: Sequence[Mapping[str, Any]],
                           replacements: Sequence[Mapping[str, str]], candidate: Optional[Path],
                           candidates: Sequence[Mapping[str, str]]) -> Dict[str, Any]:
        rec, target = item["record"], item["target"]
        fields = {"schema_version", "kind", "path", "digest", "actor", "statement", "source"}
        if not isinstance(rec, dict) or set(rec) != fields or rec.get("schema_version") != 1 or rec.get("kind") != "spec-flow-approval-receipt":
            return {"reason": "source is not an explicit recognized approval receipt"}
        try:
            original = safe_path(self.root, rec["path"])
            origin = next((row for row in mappings if item["source"].startswith(row["legacy"] + "/")), None)
            replacement = next((row for row in replacements if row["path"] == rec["path"]), None)
            decision_is_legacy = origin is not None and rec["path"].startswith(origin["legacy"] + "/")
            decision_is_replacement = replacement is not None and rec["path"] == target
            if not decision_is_legacy and not decision_is_replacement:
                return {"reason": "receipt does not identify a mapped legacy decision or explicit replacement"}
            expected_original = replacement["source_sha256"] if decision_is_replacement else rec["digest"]
            if sha(original.read_bytes()) != rec["digest"] or rec["digest"] != expected_original:
                return {"reason": "original decision bytes do not match receipt or replacement pin"}
            if not target.startswith(".specs/"):
                return {"reason": "approval target must be under .specs"}
            target_path = (candidate / target) if candidate and target in {f["path"] for f in candidates} else safe_path(self.root, target)
            is_release_target = "release" in origin and target.startswith(".specs/release-{}/".format(origin["release"]))
            is_replacement = target in {row["path"] for row in replacements}
            if not is_release_target and not is_replacement:
                return {"reason": "approval target is not mapped to a release or explicit replacement"}
            target_digest = document_digest(target_path)
        except (KeyError, ContractError, OSError, ValueError):
            return {"reason": "receipt source or conversion target is missing or unsafe"}
        if not all(isinstance(rec.get(key), str) and rec[key].strip() for key in ("path", "digest", "actor", "statement", "source")):
            return {"reason": "receipt has missing provenance fields"}
        old_text = original.read_text(encoding="utf-8")
        new_text = target_path.read_text(encoding="utf-8")
        try:
            self._validate_decision_equivalence(item["equivalence"], original, target_path)
        except MigrationError as exc:
            return {"reason": str(exc)}
        return {"status": "imported", "target_digest": target_digest}

    def _classify_evidence(self, item: Mapping[str, Any], mappings: Sequence[Mapping[str, Any]],
                           candidate: Optional[Path], candidates: Sequence[Mapping[str, str]],
                           sources: Sequence[Mapping[str, str]]) -> Dict[str, Any]:
        record = item["record"]
        fields = {"schema_version", "kind", "task_id", "step_id", "command", "expected", "result",
                  "source_files", "source_digests", "code_files", "code_hash"}
        if not isinstance(record, dict) or set(record) != fields or record.get("schema_version") != 1 or record.get("kind") != "spec-flow-step-evidence":
            return {"reason": "source is not an explicit recognized step-evidence record"}
        origin = next((row for row in mappings if item["source"].startswith(row["legacy"] + "/")), None)
        target = item["target"]
        if origin is None or "release" not in origin or target != ".specs/release-{}/tasks.md".format(origin["release"]):
            return {"reason": "evidence target must map to the originating legacy directory's release tasks"}
        target_path = candidate / target if candidate and target in {row["path"] for row in candidates} else safe_path(self.root, target)
        try:
            tasks_doc = read_document(target_path)
        except (ContractError, OSError) as exc:
            return {"reason": "candidate task contract is unavailable: {}".format(exc)}
        task_id, step_id = record.get("task_id"), record.get("step_id")
        task_contract = next((task for task in tasks_doc["contract"].get("tasks", []) if task.get("id") == task_id), None)
        step = next((step for step in task_contract.get("steps", []) if step.get("id") == step_id), None) if task_contract else None
        if not step:
            return {"reason": "task or step ID does not match the candidate contract"}
        verification = step["verification"]
        result = record.get("result")
        if (record.get("command") != verification.get("command") or record.get("expected") != verification.get("expected")
                or not isinstance(result, dict) or type(result.get("exit_code")) is not int or result.get("exit_code") != 0
                or not isinstance(result.get("output"), str) or not result["output"].strip()):
            return {"reason": "recorded command, expected result, or successful output differs from the candidate step"}
        source_files = record.get("source_files")
        source_hashes = {row["path"]: row["sha256"] for row in sources}
        if not isinstance(source_files, dict) or not source_files:
            return {"reason": "evidence has no exact source-file hashes"}
        for path, digest in source_files.items():
            if not any(path.startswith(row["legacy"] + "/") for row in mappings) or source_hashes.get(path) != digest:
                return {"reason": "evidence source files do not match committed legacy bytes"}
        code_files = record.get("code_files")
        if not isinstance(code_files, dict) or set(code_files) != set(task_contract.get("files", [])):
            return {"reason": "code hashes do not cover exactly the candidate task scope"}
        if record.get("code_hash") != sha(canonical(code_files)):
            return {"reason": "code fingerprint does not match its file hashes"}
        try:
            for path, digest in code_files.items():
                current = safe_path(self.root, path)
                if current.is_symlink() or not current.is_file() or sha(current.read_bytes()) != digest:
                    return {"reason": "tested code no longer matches current bytes: {}".format(path)}
                if self._git("show", "HEAD:" + path) != current.read_bytes():
                    return {"reason": "tested code is not the committed source: {}".format(path)}
        except (ContractError, MigrationError, OSError):
            return {"reason": "tested code source is unsafe, missing, or not committed"}
        try:
            expected_digests = self._release_document_digests(origin["release"], candidate, candidates)
        except (ContractError, MigrationError, OSError, KeyError, ValueError):
            return {"reason": "release source documents cannot be pinned"}
        # The historical record must pin the complete relevant decision closure,
        # and those decisions must still match the candidate. Roadmap release
        # grouping is the one structural addition: other roadmap decisions remain
        # covered by the comparison.
        try:
            old_doc_digests = self._historical_decision_closure(
                origin, candidate, candidates, sources
            )
        except (ContractError, MigrationError, OSError, ValueError, KeyError):
            return {"reason": "historical decision closure is missing, stale, or not equivalent to the candidate"}
        pinned = record.get("source_digests")
        if not isinstance(pinned, dict) or pinned != old_doc_digests:
            return {"reason": "historical evidence source-document digests do not match committed legacy documents"}
        source_path = safe_path(self.root, item["source"])
        target_text = target_path.read_text(encoding="utf-8")
        equivalence = item["equivalence"]
        if (set(equivalence) != {"statement", "source_excerpt", "target_excerpt"}
                or not isinstance(equivalence.get("statement"), str) or not equivalence["statement"].strip()
                or equivalence.get("source_excerpt") != source_path.read_text(encoding="utf-8")
                or equivalence.get("target_excerpt") != target_text):
            return {"reason": "evidence mapping must identify the complete original record and candidate tasks document"}
        return {"status": "imported", "release": origin["release"], "task_id": task_id, "step_id": step_id,
                "task_digest": document_digest(target_path), "source_digests": expected_digests,
                "historical_source_digests": pinned,
                "code_files": code_files, "verified_step": {"command": record["command"], "expected": record["expected"],
                                  "observed": result["output"], "exit_code": 0,
                                  "output_sha256": sha(result["output"].encode("utf-8"))}}

    def _historical_decision_closure(self, origin: Mapping[str, Any], candidate: Optional[Path],
                                     candidates: Sequence[Mapping[str, str]],
                                     sources: Sequence[Mapping[str, str]]) -> Dict[str, str]:
        source_inventory = {row["path"] for row in sources}
        candidate_paths = {row["path"] for row in candidates}
        required = {origin["legacy"] + "/" + name for name in ("spec.md", "plan.md", "tasks.md")}
        if not required <= source_inventory:
            raise MigrationError("migration_evidence_unverifiable", "historical spec, plan, and tasks are all required")
        release_prefix = ".specs/release-{}/".format(origin["release"])
        mappings = {origin["legacy"] + "/" + name: release_prefix + name
                    for name in ("spec.md", "plan.md", "tasks.md")}
        seen: Dict[str, str] = {}
        visited: Set[str] = set()

        def target_for(source_rel: str) -> str:
            return mappings.get(source_rel, source_rel)

        def read_source(source_rel: str) -> Path:
            if source_rel not in source_inventory:
                raise MigrationError("migration_evidence_unverifiable", "historical dependency is absent: " + source_rel)
            return safe_path(self.root, source_rel)

        def read_target(target_rel: str) -> Path:
            if candidate and target_rel in candidate_paths:
                return candidate / target_rel
            return safe_path(self.root, target_rel)

        def visit(source_rel: str) -> None:
            if source_rel in visited:
                return
            visited.add(source_rel)
            source_path = read_source(source_rel)
            source_doc = read_document(source_path)
            target_rel = target_for(source_rel)
            target_path = read_target(target_rel)
            target_doc = read_document(target_path)
            if self._decision_projection(source_doc) != self._decision_projection(target_doc):
                raise MigrationError("migration_evidence_unverifiable", "historical decision changed: " + source_rel)
            seen[source_rel] = document_digest(source_path)
            translated_dependencies = []
            for dependency in source_doc["contract"].get("depends_on", []):
                dep_path = dependency["path"]
                # Resolve old release-local references against the legacy folder;
                # shared strategy/design references retain their root-relative path.
                old_release_prefix = ".specs/release-{}/".format(origin["release"])
                if dep_path.startswith(old_release_prefix) and Path(dep_path).name in {"spec.md", "plan.md", "tasks.md"}:
                    source_dependency = origin["legacy"] + "/" + Path(dep_path).name
                elif dep_path.startswith(origin["legacy"] + "/"):
                    source_dependency = dep_path
                elif dep_path.startswith(".specs/"):
                    source_dependency = dep_path
                else:
                    raise MigrationError("migration_evidence_unverifiable", "historical dependency escapes .specs: " + dep_path)
                dependency_source_path = read_source(source_dependency)
                if document_digest(dependency_source_path) != dependency["digest"]:
                    raise MigrationError("migration_evidence_unverifiable", "historical dependency digest is stale: " + dep_path)
                visit(source_dependency)
                translated_dependencies.append(target_for(source_dependency))

            target_dependencies = []
            for dependency in target_doc["contract"].get("depends_on", []):
                target_dependency = dependency["path"]
                target_dependency_path = read_target(target_dependency)
                if document_digest(target_dependency_path) != dependency["digest"]:
                    raise MigrationError("migration_evidence_unverifiable", "candidate dependency digest is stale: " + target_dependency)
                target_dependencies.append(target_dependency)
            if sorted(translated_dependencies) != sorted(target_dependencies):
                raise MigrationError("migration_evidence_unverifiable", "candidate decision closure adds or removes a dependency: " + target_rel)

        for required_path in sorted(required):
            visit(required_path)
        return dict(sorted(seen.items()))

    @staticmethod
    def _decision_projection(document: Mapping[str, Any]) -> Any:
        contract = dict(document["contract"])
        kind = contract.get("kind")
        for field in ("id", "revision", "depends_on", "status"):
            contract.pop(field, None)
        if kind == "roadmap":
            # A new explicit release selection is migration metadata. Preserve
            # every other roadmap decision in the equivalence check.
            contract.pop("releases", None)
        return {"prose": document["prose"], "contract": contract}

    def _release_document_digests(self, release: str, candidate: Optional[Path],
                                  candidates: Sequence[Mapping[str, str]]) -> Dict[str, str]:
        candidate_paths = {item["path"] for item in candidates}
        initial = [".specs/constitution.md", ".specs/roadmap.md"] + [
            ".specs/release-{}/{}".format(release, name) for name in ("spec.md", "plan.md", "tasks.md")]
        seen: Dict[str, str] = {}

        def visit(path: str) -> None:
            if path in seen:
                return
            if candidate and path in candidate_paths:
                full = candidate / path
            else:
                full = safe_path(self.root, path)
            document = read_document(full)
            seen[path] = document_digest(full)
            for reference in document["contract"].get("depends_on", []):
                visit(reference["path"])

        for path in initial:
            visit(path)
        return dict(sorted(seen.items()))

    @staticmethod
    def _validate_equivalence(equivalence: Mapping[str, Any], source_text: str, target_text: str) -> None:
        if not isinstance(equivalence, dict) or set(equivalence) != {"statement", "source_excerpt", "target_excerpt"}:
            raise MigrationError("migration_equivalence_invalid", "equivalence needs a statement and mapped excerpts")
        for field in ("statement", "source_excerpt", "target_excerpt"):
            if not isinstance(equivalence[field], str) or not equivalence[field].strip():
                raise MigrationError("migration_equivalence_invalid", "equivalence fields must be nonempty strings")
        if equivalence["source_excerpt"] != source_text or equivalence["target_excerpt"] != target_text:
            raise MigrationError("migration_equivalence_invalid", "equivalence must include the complete exact source and candidate documents")

    @staticmethod
    def _validate_decision_equivalence(equivalence: Mapping[str, Any], source_path: Path, target_path: Path) -> None:
        source_text = source_path.read_text(encoding="utf-8")
        target_text = target_path.read_text(encoding="utf-8")
        Migration._validate_equivalence(equivalence, source_text, target_text)
        try:
            source = read_document(source_path)
            target = read_document(target_path)
        except ContractError as exc:
            raise MigrationError("migration_equivalence_invalid", "plain prose cannot establish structural decision equivalence") from exc

        def decision(document: Mapping[str, Any]) -> Any:
            contract = dict(document["contract"])
            # These are document-identity and dependency metadata. All prose and
            # all other decision-bearing structured fields must remain identical.
            for field in ("id", "revision", "depends_on", "status"):
                contract.pop(field, None)
            return {"prose": document["prose"], "contract": contract}

        if decision(source) != decision(target):
            raise MigrationError("migration_equivalence_invalid", "approval conversion changes decision prose or structured decision fields")

    def apply(self, manifest: Any, digest: Any, candidate_dir: Optional[str], authorization: Any) -> Dict[str, Any]:
        if not isinstance(manifest, dict) or not isinstance(digest, str) or sha(canonical(manifest)) != digest:
            raise MigrationError("migration_preview_invalid", "preview digest does not match manifest")
        if manifest.get("project_root") != str(self.root):
            raise MigrationError("migration_preview_invalid", "preview belongs to another project")
        if not isinstance(authorization, dict) or not all(isinstance(authorization.get(key), str) and authorization[key].strip()
                                                          for key in ("actor", "statement", "source")):
            raise MigrationError("migration_authorization_required", "authorization needs actor, statement, and source")
        current_candidate = str(Path(candidate_dir).expanduser().resolve()) if candidate_dir else None
        if current_candidate != manifest.get("candidate_dir"):
            raise MigrationError("migration_candidate_stale", "candidate path changed since preview")
        journal_path = safe_path(self.root, ".spec-flow/migrations/{}/journal.json".format(manifest["migration_id"]))
        if journal_path.exists():
            try:
                journal = json.loads(journal_path.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, json.JSONDecodeError) as exc:
                raise MigrationError("migration_journal_corrupt", "existing migration journal is unreadable") from exc
            if journal.get("digest") != digest or journal.get("manifest") != manifest:
                raise MigrationError("migration_id_conflict", "migration identity already has different inputs")
            return self._continue(manifest, digest, journal["authorization"], journal)
        imports = {kind: [{key: item[key] for key in ("source", "target", "equivalence")} for item in manifest["imports"][kind]]
                   for kind in ("approvals", "evidence")}
        try:
            fresh = self.preview(manifest["mapping"], candidate_dir, manifest["replacements"], imports)
        except MigrationError as exc:
            if exc.code == "migration_source_dirty":
                raise MigrationError("migration_source_stale", str(exc), exc.details) from exc
            if exc.code == "migration_candidate_invalid":
                raise MigrationError("migration_candidate_stale", str(exc), exc.details) from exc
            raise
        if fresh["manifest"]["sources"] != manifest["sources"] or fresh["manifest"]["git_head"] != manifest["git_head"]:
            raise MigrationError("migration_source_stale", "committed source changed after preview")
        if fresh["manifest"]["candidates"] != manifest["candidates"]:
            raise MigrationError("migration_candidate_stale", "candidate bytes changed after preview")
        if fresh["digest"] != digest:
            raise MigrationError("migration_preview_stale", "preview inputs or validation no longer match")
        return self._continue(manifest, digest, authorization)

    def resume(self, migration_id: str) -> Dict[str, Any]:
        if not isinstance(migration_id, str) or not re.fullmatch(r"[0-9a-f]{32}", migration_id):
            raise MigrationError("migration_not_found", "migration ID is invalid")
        journal_path = safe_path(self.root, ".spec-flow/migrations/{}/journal.json".format(migration_id))
        try:
            journal = json.loads(journal_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise MigrationError("migration_not_found", "journal is missing or unreadable") from exc
        if journal.get("migration_id") != migration_id:
            raise MigrationError("migration_journal_corrupt", "journal ID does not match")
        return self._continue(journal["manifest"], journal["digest"], journal["authorization"], journal)

    def _continue(self, manifest: Mapping[str, Any], digest: str, authorization: Mapping[str, str],
                  journal: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        ident = manifest["migration_id"]
        base = safe_path(self.root, ".spec-flow/migrations/" + ident)
        jpath = base / "journal.json"
        if journal is None:
            base.mkdir(parents=True, exist_ok=True)
            journal = {"schema_version": 1, "migration_id": ident, "digest": digest,
                       "manifest": dict(manifest), "authorization": dict(authorization), "status": "staged"}
            self.store.write_json_atomic(jpath, journal)
            self.store.write_json_atomic(base / "imports.json", manifest["imports"])
        self._stage_candidates(manifest, base)
        if journal.get("status") == "completed":
            self._finalize(manifest, ident, digest, journal, jpath)
            return self._result(manifest)
        self._archive(manifest, ident)
        self._promote(manifest, base)
        self._remove_sources(manifest, ident)
        self._validate_final(manifest)
        self._finalize(manifest, ident, digest, journal, jpath)
        return self._result(manifest)

    def _stage_candidates(self, manifest: Mapping[str, Any], base: Path) -> None:
        if not manifest.get("candidate_dir"):
            return
        original = Path(manifest["candidate_dir"]) / ".specs"
        staged = base / "candidate" / ".specs"
        for item in manifest["candidates"]:
            target = staged / Path(item["path"]).relative_to(".specs")
            if target.exists():
                if target.is_symlink() or not target.is_file() or sha(target.read_bytes()) != item["sha256"]:
                    raise MigrationError("migration_candidate_stale", "staged candidate differs from preview")
                continue
            source = original / Path(item["path"]).relative_to(".specs")
            if not source.is_file() or source.is_symlink() or sha(source.read_bytes()) != item["sha256"]:
                raise MigrationError("migration_candidate_stale", "candidate bytes changed before staging")
            self._write(target, source.read_bytes(), exclusive=True)

    def _finalize(self, manifest: Mapping[str, Any], ident: str, digest: str,
                  journal: Dict[str, Any], journal_path: Path) -> None:
        self._validate_final(manifest)
        self._import_approvals(manifest, ident)
        self._import_evidence(manifest, ident)
        config = self.root / ".spec-flow/config.json"
        if not config.exists():
            from .engine import PROFILES
            self.store.write_json_atomic(config, {"schema_version": 1, "profiles": PROFILES, "retry_limit": 3})
            (self.root / ".spec-flow/runs").mkdir(parents=True, exist_ok=True)
        if journal.get("status") != "completed":
            journal["status"] = "completed"
            journal["completed_at"] = datetime.now(timezone.utc).isoformat()
            self.store.write_json_atomic(journal_path, journal)
        self.store.write_json_atomic(journal_path.parent / "complete.json", {
            "migration_id": ident, "digest": digest, "completed_at": journal["completed_at"]})

    def _archive(self, manifest: Mapping[str, Any], ident: str) -> None:
        archive = safe_path(self.root, ".spec-flow/legacy/" + ident + "/sources")
        expected = {row["path"]: row["sha256"] for row in manifest["sources"]}
        for mapping in manifest["mapping"]:
            rel = mapping["legacy"]
            src, dest = safe_path(self.root, rel), archive / Path(rel).name
            if dest.exists():
                self._verify_tree(dest, rel, expected)
            elif src.exists():
                self._verify_tree(src, rel, expected)
                dest.parent.mkdir(parents=True, exist_ok=True)
                os.rename(src, dest)
                self._verify_tree(dest, rel, expected)
            else:
                raise MigrationError("migration_archive_missing", "source and archive are both missing: " + rel)
        archive_root = archive
        for replacement in manifest["replacements"]:
            rel = replacement["path"]
            src = safe_path(self.root, rel)
            dest = archive_root / "replacements" / Path(rel).relative_to(".specs")
            if not dest.exists():
                if sha(src.read_bytes()) != replacement["source_sha256"]:
                    raise MigrationError("migration_source_stale", "replacement changed during migration: " + rel)
                self._write(dest, src.read_bytes(), exclusive=True)
            elif sha(dest.read_bytes()) != replacement["source_sha256"]:
                raise MigrationError("migration_archive_conflict", "replacement archive differs")

    def _verify_tree(self, directory: Path, rel: str, all_expected: Mapping[str, str]) -> None:
        expected = {path: digest for path, digest in all_expected.items() if path.startswith(rel + "/")}
        actual = {}
        for path in directory.rglob("*"):
            if path.is_symlink():
                raise MigrationError("migration_unsafe_source", "symlink encountered in source/archive")
            if path.is_file():
                actual[(Path(rel) / path.relative_to(directory)).as_posix()] = sha(path.read_bytes())
        if actual != expected:
            raise MigrationError("migration_source_stale", "source tree changed after preview: " + rel)

    def _promote(self, manifest: Mapping[str, Any], base: Path) -> None:
        staged = base / "candidate" / ".specs"
        replacements = {row["path"]: row["source_sha256"] for row in manifest["replacements"]}
        for item in manifest["candidates"]:
            target = safe_path(self.root, item["path"])
            if target.is_file() and sha(target.read_bytes()) == item["sha256"]:
                continue
            if target.exists() and (item["path"] not in replacements or sha(target.read_bytes()) != replacements[item["path"]]):
                raise MigrationError("migration_collision", "destination changed during apply: " + item["path"])
            source = staged / Path(item["path"]).relative_to(".specs")
            if not source.is_file() or sha(source.read_bytes()) != item["sha256"]:
                raise MigrationError("migration_candidate_stale", "staged candidate changed: " + item["path"])
            self._write(target, source.read_bytes())

    def _remove_sources(self, manifest: Mapping[str, Any], ident: str) -> None:
        archive = safe_path(self.root, ".spec-flow/legacy/" + ident + "/sources")
        expected = {row["path"]: row["sha256"] for row in manifest["sources"]}
        for mapping in manifest["mapping"]:
            src = safe_path(self.root, mapping["legacy"])
            if src.exists():
                dest = archive / Path(mapping["legacy"]).name
                self._verify_tree(dest, mapping["legacy"], expected)
                self._verify_partial_tree(src, mapping["legacy"], expected)
                shutil.rmtree(src)

    def _verify_partial_tree(self, directory: Path, rel: str, all_expected: Mapping[str, str]) -> None:
        expected = {path: digest for path, digest in all_expected.items() if path.startswith(rel + "/")}
        for path in directory.rglob("*"):
            if path.is_symlink():
                raise MigrationError("migration_unsafe_source", "symlink encountered while reconciling source")
            if path.is_file():
                relative = (Path(rel) / path.relative_to(directory)).as_posix()
                if expected.get(relative) != sha(path.read_bytes()):
                    raise MigrationError("migration_source_stale", "source changed during interrupted migration: " + relative)

    def _validate_final(self, manifest: Mapping[str, Any]) -> None:
        for mapping in manifest["mapping"]:
            if safe_path(self.root, mapping["legacy"]).exists():
                raise MigrationError("migration_incomplete", "legacy source remains")
            if "release" in mapping:
                try:
                    validate_release(self.root, mapping["release"])
                except ContractError as exc:
                    raise MigrationError("migration_candidate_invalid", str(exc)) from exc
        if any(p.is_dir() and LEGACY_RE.fullmatch(p.name) for p in self.specs.iterdir()):
            raise MigrationError("migration_incomplete", "unmapped legacy directories remain")

    def _import_approvals(self, manifest: Mapping[str, Any], ident: str) -> None:
        existing = self.store.approvals()
        for item in manifest["imports"]["approvals"]:
            if item["status"] != "imported":
                continue
            record = item["record"]
            receipt = {
                "path": item["target"], "digest": item["target_digest"],
                "actor": record["actor"], "statement": record["statement"], "source": record["source"],
                "imported": True, "migration_id": ident, "original_path": record["path"],
                "original_digest": record["digest"], "conversion_equivalence": item["equivalence"],
                "import_source": item["source"], "created_at": datetime.now(timezone.utc).isoformat(),
            }
            prior = next((row for row in existing if row.get("migration_id") == ident and row.get("import_source") == item["source"]), None)
            if prior:
                stable = set(receipt) - {"created_at"}
                if any(prior.get(key) != receipt[key] for key in stable):
                    raise MigrationError("migration_import_conflict", "approval import identity has conflicting receipt")
                continue
            self.store.append_approval(receipt)
            existing.append(receipt)

    def _import_evidence(self, manifest: Mapping[str, Any], ident: str) -> None:
        items = manifest.get("imports", {}).get("evidence", [])
        if not items:
            return
        path = safe_path(self.root, ".spec-flow/migrations/{}/imported-evidence.jsonl".format(ident))
        rows = self.store.read_jsonl(path, sequence_field="seq")
        by_id = {row.get("import_id"): row for row in rows}
        for item in items:
            import_id = sha(canonical({"migration_id": ident, "source": item["source"], "source_sha256": item["source_sha256"], "target": item["target"]}))
            existing = by_id.get(import_id)
            value = {"import_id": import_id, **item}
            if existing:
                if any(existing.get(key) != data for key, data in value.items()):
                    raise MigrationError("migration_import_conflict", "evidence import identity has conflicting record")
                continue
            row = self.store.append_jsonl(path, value, sequence_field="seq")
            rows.append(row)
            by_id[import_id] = row
    def _write(self, path: Path, data: bytes, exclusive: bool = False) -> None:
        safe_path(self.root, path.relative_to(self.root))
        path.parent.mkdir(parents=True, exist_ok=True)
        if exclusive and path.exists():
            raise MigrationError("migration_archive_conflict", "archive already exists")
        fd, temp = tempfile.mkstemp(prefix="." + path.name + ".", dir=str(path.parent))
        try:
            with os.fdopen(fd, "wb") as stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp, path)
            Store._fsync_directory(path.parent)
        finally:
            if os.path.exists(temp):
                os.unlink(temp)

    def _result(self, manifest: Mapping[str, Any]) -> Dict[str, Any]:
        imports = manifest.get("imports", {})
        return {"completed": True, "migration_id": manifest["migration_id"], "source_git_head": manifest["git_head"],
                "archive": ".spec-flow/legacy/" + manifest["migration_id"] + "/sources",
                "active_releases": [row["release"] for row in manifest["mapping"] if "release" in row],
                "approval_imports": {status: sum(row["status"] == status for row in imports.get("approvals", []))
                                     for status in ("imported", "pending")},
                "evidence_imports": {status: sum(row["status"] == status for row in imports.get("evidence", []))
                                     for status in ("imported", "pending")}}
