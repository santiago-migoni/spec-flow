"""Read and validate Spec-Flow's Markdown contract documents."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Set, Union

from .yaml_format import load_contract, dump_contract


class ContractError(ValueError):
    """Raised when a contract document or its references are invalid."""


KINDS = {
    "constitution",
    "architecture",
    "structure",
    "infrastructure",
    "roadmap",
    "spec",
    "plan",
    "tasks",
}
RELEASE_RE = re.compile(r"^v?(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")
CONTRACT_BLOCK_RE = re.compile(r"```spec-flow\s*\n(.*?)\n```", re.DOTALL)
GENERATED_BLOCK_RE = re.compile(
    r"\n<!-- spec-flow:generated:start -->\r?\n.*?\r?\n<!-- spec-flow:generated:end -->(?:\r?\n)*\Z",
    re.DOTALL,
)
PLACEHOLDER_RE = re.compile(
    r"\[(?:TODO|TBD|PLACEHOLDER|FILL[ -]?ME|REPLACE[ -]?ME|\.\.\.)\]"
    r"|<(?:TODO|TBD|PLACEHOLDER)[^>]*>|^\s*(?:TODO|TBD|PLACEHOLDER|\.{3,})\s*$"
    r"|^>\s*\*\*Authoring notes",
    re.IGNORECASE | re.MULTILINE,
)


def normalize_release(value: object) -> str:
    """Return a canonical vX.Y.Z release identifier for strict numeric SemVer."""
    if not isinstance(value, str) or not RELEASE_RE.fullmatch(value):
        raise ContractError("release must be strict numeric semver in X.Y.Z or vX.Y.Z form")
    return value if value.startswith("v") else "v" + value


def safe_path(root: Union[str, Path], relative: Union[str, Path]) -> Path:
    """Resolve a project-relative path and reject traversal or symlink escape."""
    root_path = Path(root).resolve()
    raw = Path(relative)
    if raw.is_absolute() or any(part == ".." for part in raw.parts):
        raise ContractError("path must be relative and must not traverse its root")
    resolved = (root_path / raw).resolve()
    try:
        resolved.relative_to(root_path)
    except ValueError as exc:
        raise ContractError("path resolves outside the project root") from exc
    return resolved


YAML_HEADER_RE = re.compile(r"\A---\r?\n(.*?)^---[ \t]*(?:\r?\n|$)", re.DOTALL | re.MULTILINE)


def contract_region(text: str):
    """Return the sole contract span, encoding and object; reject mixed sources."""
    legacy = list(CONTRACT_BLOCK_RE.finditer(text))
    header = YAML_HEADER_RE.match(text)
    if text.startswith(("---\n", "---\r\n")):
        if header is None or legacy:
            raise ContractError("document requires one closed YAML header and no JSON contract block")
        if "<!-- spec-flow:generated:" in header.group(0):
            raise ContractError("generated progress cannot enclose or precede the contract")
        try:
            contract = load_contract(header.group(1))
        except ValueError as exc:
            raise ContractError(str(exc)) from exc
        match, encoding = header, "yaml"
    else:
        if len(legacy) != 1:
            raise ContractError("document requires one YAML frontmatter header or one legacy spec-flow JSON block")
        match, encoding = legacy[0], "json"
        try:
            contract = json.loads(match.group(1))
        except json.JSONDecodeError as exc:
            raise ContractError("spec-flow contract block contains invalid JSON: {}".format(exc)) from exc
    if not isinstance(contract, dict):
        raise ContractError("spec-flow contract must be a mapping object")
    return match, encoding, contract


def read_document_text(text: str) -> Dict[str, Any]:
    match, _, contract = contract_region(text)
    prose = (text[:match.start()] + text[match.end():]).strip()
    prose = _strip_generated_tail(prose).strip()
    return {"contract": contract, "prose": prose}


def render_document(contract: Mapping[str, Any], prose: str) -> str:
    """Create a new Markdown decision document with YAML frontmatter."""
    return "---\n" + dump_contract(dict(contract)) + "\n---\n\n" + prose.strip() + "\n"


def replace_contract(text: str, contract: Mapping[str, Any]) -> str:
    """Update a contract without silently converting existing documents."""
    match, encoding, _ = contract_region(text)
    encoded = ("---\n" + dump_contract(dict(contract)) + "\n---\n" if encoding == "yaml"
               else "```spec-flow\n" + json.dumps(dict(contract), ensure_ascii=False, indent=2) + "\n```")
    return text[:match.start()] + encoded + text[match.end():]


def read_document(path: Union[str, Path]) -> Dict[str, Any]:
    """Read YAML frontmatter or an existing fenced JSON decision contract."""
    document_path = Path(path)
    try:
        text = document_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise ContractError("cannot read document: {}".format(document_path)) from exc
    return read_document_text(text)


def _strip_generated_tail(text: str) -> str:
    start_count = text.count("<!-- spec-flow:generated:start -->")
    end_count = text.count("<!-- spec-flow:generated:end -->")
    matches = list(GENERATED_BLOCK_RE.finditer(text))
    if start_count == end_count == 0:
        return text
    if start_count != 1 or end_count != 1 or len(matches) != 1:
        raise ContractError("generated progress must be one complete trailing generated block; move any text added after it above the block")
    match = matches[0]
    body = text[match.start():match.end()]
    progress = re.sub(
        r"\A\n<!-- spec-flow:generated:start -->\r?\n|\r?\n<!-- spec-flow:generated:end -->(?:\r?\n)*\Z",
        "",
        body,
    )
    lines = progress.splitlines()
    header = bool(lines and re.fullmatch(r"Progress(?: view)?(?: is)? maintained by (?:the )?(?:Spec-Flow )?harness\.", lines[0]))
    checkbox_lines = lines[1:] if header else lines
    if header:
        if any(
            not re.fullmatch(r"- \[[ xX]\] T-[0-9]{3,}", line)
            and not re.fullmatch(r"progress: [0-9]{1,3}%", line, re.IGNORECASE)
            for line in checkbox_lines
        ):
            raise ContractError("generated progress block may contain only task progress lines")
    else:
        # Historical task progress blocks omitted the explanatory header. Keep
        # accepting that exact narrow shape while rejecting arbitrary prose.
        if lines and all(
            re.fullmatch(r"- \[[ xX]\] T-[0-9]{3,}", line)
            or re.fullmatch(r"progress: [0-9]{1,3}%", line, re.IGNORECASE)
            for line in lines
        ):
            return text[:match.start()].rstrip("\r\n") + "\n"
        record_match = re.fullmatch(r"\n<!-- spec-flow:generated:start -->\nSpec-Flow derived record:\n(\{.*\})\n<!-- spec-flow:generated:end -->\n*", body, re.DOTALL)
        if record_match is None:
            raise ContractError("generated release record must be one strict trailing JSON record")
        try:
            record = json.loads(record_match.group(1))
        except json.JSONDecodeError as exc:
            raise ContractError("generated release record contains invalid JSON") from exc
        if not isinstance(record, dict) or json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":")) != record_match.group(1):
            raise ContractError("generated release record must use canonical JSON")
        _validate_generated_record(record)
    # Progress insertion is defined to add a trailing block after a blank-line
    # boundary. Canonicalize only that boundary, preserving decision prose.
    return text[:match.start()].rstrip("\r\n") + "\n"


def _validate_generated_record(record: Mapping[str, Any]) -> None:
    if record.get("schema") == "spec-flow.derived-release.v1":
        required = {"schema", "kind", "release", "run_id", "technical_status", "phase_commits",
                    "impact_status", "impact_evidence", "delivery_status", "publication", "external_side_effects"}
        _require(set(record) == required and record.get("kind") == "release-review", "derived release record has an unsupported shape")
        _require(record.get("technical_status") == "complete", "derived release record technical_status must be complete")
        _require(record.get("impact_status") in {"observed", "pending", "unavailable"}, "derived release record has an invalid impact status")
        _require(record.get("delivery_status") in {"branch_committed", "branch_retained", "not_integrated"}, "derived release record has an invalid delivery status")
        _require(record.get("publication") is False and record.get("external_side_effects") is False, "derived release record cannot claim publication or external side effects")
        _require(isinstance(record.get("run_id"), str) and bool(record["run_id"]), "derived release record requires run_id")
        _require(isinstance(record.get("impact_evidence"), list) and all(isinstance(ref, str) and ref.strip() and "\n" not in ref for ref in record["impact_evidence"]), "derived release record impact evidence must contain references")
        commits: Any = record.get("phase_commits")
        _require(isinstance(commits, list) and bool(commits), "derived release record requires phase commit references")
        for item in commits:
            _require(isinstance(item, dict) and set(item) == {"phase_id", "sha"}, "derived phase commit reference has an invalid shape")
            _require(isinstance(item["phase_id"], str) and re.fullmatch(r"PH-[0-9]{2,}", item["phase_id"]) is not None, "derived phase ID is invalid")
            _require(isinstance(item["sha"], str) and re.fullmatch(r"[0-9a-f]{40,64}", item["sha"]) is not None, "derived phase commit SHA is invalid")
    elif record.get("schema") == "spec-flow.derived-reference.v1":
        required = {"schema", "kind", "release", "run_id", "spec_path", "impact_status"}
        _require(set(record) == required and record.get("kind") == "roadmap-reference", "roadmap derived reference has an unsupported shape")
        _require(isinstance(record.get("run_id"), str) and bool(record["run_id"]), "roadmap derived reference requires run_id")
        _require(isinstance(record.get("spec_path"), str) and re.fullmatch(r"\.specs/release-v[0-9]+\.[0-9]+\.[0-9]+/spec\.md", record["spec_path"]) is not None, "roadmap derived reference has an invalid spec path")
        _require(record.get("impact_status") in {"observed", "pending", "unavailable"}, "roadmap derived reference has an invalid impact status")
    else:
        raise ContractError("generated record schema is not recognized")
    try:
        normalize_release(record.get("release"))
    except ContractError as exc:
        raise ContractError("generated record release must be strict numeric semver") from exc


def _digest_content(text: str) -> bytes:
    """Normalize non-decision status/progress fields before hashing content."""
    if text.startswith(("---\n", "---\r\n")):
        match, _, contract = contract_region(text)
        if "<!-- spec-flow:generated:" in text[:match.end()]:
            raise ContractError("generated progress cannot enclose or precede the contract")
        body = _strip_generated_tail(text[match.end():]).strip()
        contract = dict(contract)
        contract.pop("status", None)
        canonical = json.dumps(contract, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
        return ("spec-flow-yaml-v1\n" + canonical + "\n" + body).encode("utf-8")
    block_matches = list(CONTRACT_BLOCK_RE.finditer(text))
    generated_marked = "<!-- spec-flow:generated:" in text
    if generated_marked:
        if len(block_matches) != 1:
            raise ContractError("generated progress must follow exactly one contract block")
        _strip_generated_tail(text[block_matches[0].end() :])
        if "<!-- spec-flow:generated:start -->" not in text[block_matches[0].end() :]:
            raise ContractError("generated progress cannot enclose or precede the contract")
        text = text[: block_matches[0].end()] + _strip_generated_tail(text[block_matches[0].end() :])
    match = CONTRACT_BLOCK_RE.search(text)
    if match:
        try:
            contract = json.loads(match.group(1))
        except json.JSONDecodeError:
            # Invalid contracts still have a deterministic digest; validation reports parse errors.
            pass
        else:
            if isinstance(contract, dict):
                contract.pop("status", None)
                canonical = json.dumps(contract, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
                text = text[: match.start()] + "```spec-flow\n" + canonical + "\n```" + text[match.end() :]
    return text.encode("utf-8")


def document_digest(path: Union[str, Path]) -> str:
    """Return SHA-256 of decision content, ignoring generated blocks and contract status."""
    document_path = Path(path)
    try:
        text = document_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise ContractError("cannot read document: {}".format(document_path)) from exc
    return hashlib.sha256(_digest_content(text)).hexdigest()


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip()) and not PLACEHOLDER_RE.search(value)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def _validate_dependency_refs(root: Path, contract: Mapping[str, Any]) -> None:
    refs: Any = contract.get("depends_on")
    _require(isinstance(refs, list), "depends_on must be a list")
    for ref in refs:
        _require(isinstance(ref, dict), "each document dependency must be an object")
        path = ref.get("path")
        digest = ref.get("digest")
        _require(_nonempty_string(path), "document dependency path must be a nonempty relative path")
        _require(isinstance(digest, str) and re.fullmatch(r"[0-9a-f]{64}", digest) is not None,
                 "document dependency digest must be a lowercase SHA-256 hex string")
        resolved = safe_path(root, path)
        _require(resolved.is_file(), "document dependency does not exist: {}".format(path))
        _require(document_digest(resolved) == digest, "document dependency digest is stale: {}".format(path))


def _validate_spec(contract: Mapping[str, Any]) -> Set[str]:
    stories: Any = contract.get("stories")
    _require(isinstance(stories, list) and bool(stories), "spec stories must be a nonempty list")
    story_ids: Set[str] = set()
    for story in stories:
        _require(isinstance(story, dict), "each story must be an object")
        identifier = story.get("id")
        _require(_nonempty_string(identifier) and re.fullmatch(r"US-[0-9]{3,}", identifier) is not None,
                 "story id must use US- followed by at least three digits")
        _require(identifier not in story_ids, "duplicate story id: {}".format(identifier))
        _require(_nonempty_string(story.get("title")), "story {} requires a title".format(identifier))
        _require(_nonempty_string(story.get("description")), "story {} requires a description".format(identifier))
        story_ids.add(identifier)
    criteria: Any = contract.get("acceptance")
    _require(isinstance(criteria, list) and bool(criteria), "spec acceptance must be a nonempty list")
    ids: Set[str] = set()
    for criterion in criteria:
        _require(isinstance(criterion, dict), "each acceptance criterion must be an object")
        identifier = criterion.get("id")
        _require(_nonempty_string(identifier), "acceptance criterion id must be nonempty")
        _require(identifier not in ids, "duplicate acceptance criterion id: {}".format(identifier))
        ids.add(identifier)
        _require(_nonempty_string(criterion.get("description")), "acceptance description must be nonempty")
        _require(criterion.get("story") in story_ids, "acceptance criterion {} references an unknown story".format(identifier))
    return ids


def _validate_tasks(contract: Mapping[str, Any], root: Path) -> None:
    tasks: Any = contract.get("tasks")
    _require(isinstance(tasks, list) and bool(tasks), "tasks contract must contain a nonempty tasks list")
    task_ids: Set[str] = set()
    step_ids: Set[str] = set()
    by_id: Dict[str, Mapping[str, Any]] = {}
    for task in tasks:
        _require(isinstance(task, dict), "each task must be an object")
        identifier = task.get("id")
        _require(_nonempty_string(identifier), "task id must be nonempty")
        _require(re.fullmatch(r"T-[0-9]{3,}", identifier) is not None, "task id must use T- followed by at least three digits")
        _require(identifier not in task_ids, "duplicate task id: {}".format(identifier))
        task_ids.add(identifier)
        by_id[identifier] = task
        for field in ("phase", "story", "closure"):
            _require(_nonempty_string(task.get(field)), "task {} requires nonempty {}".format(identifier, field))
        _require(re.fullmatch(r"PH-[0-9]{2,}", task["phase"]) is not None, "task {} phase must use PH- followed by at least two digits".format(identifier))
        _require(re.fullmatch(r"US-[0-9]{3,}", task["story"]) is not None, "task {} story must use US- followed by at least three digits".format(identifier))
        refs = task.get("acceptance")
        _require(isinstance(refs, list) and bool(refs) and all(_nonempty_string(ref) for ref in refs),
                 "task {} requires acceptance criterion IDs".format(identifier))
        _require(all(re.fullmatch(r"AC-[0-9]{3,}", ref) is not None for ref in refs),
                 "task {} acceptance refs must use AC- followed by at least three digits".format(identifier))
        files = task.get("files")
        _require(isinstance(files, list) and bool(files) and all(_nonempty_string(name) for name in files),
                 "task {} requires nonempty files".format(identifier))
        for filename in files:
            file_path = Path(filename)
            _require(not file_path.is_absolute() and ".." not in file_path.parts,
                     "task {} file paths must be relative and contained".format(identifier))
            _require(not file_path.parts or file_path.parts[0] not in {".specs", ".spec-flow", ".git"},
                     "task {} cannot target protected metadata paths".format(identifier))
            resolved_file = safe_path(root, file_path)
            _require(not resolved_file.is_dir(), "task {} file scope must name individual files, not directories: {}".format(identifier, filename))
        _require(isinstance(task.get("depends_on"), list), "task {} depends_on must be a list".format(identifier))
        steps = task.get("steps")
        _require(isinstance(steps, list) and bool(steps), "task {} requires nonempty steps".format(identifier))
        for step in steps:
            _require(isinstance(step, dict), "each task step must be an object")
            step_id = step.get("id")
            _require(_nonempty_string(step_id), "step id must be nonempty")
            _require(re.fullmatch(re.escape(identifier) + r"\.[0-9]{3,}", step_id) is not None,
                     "step {} must use its task ID and a numeric step suffix".format(step_id))
            _require(step_id not in step_ids, "duplicate step id: {}".format(step_id))
            step_ids.add(step_id)
            _require(_nonempty_string(step.get("action")), "step {} requires an action".format(step_id))
            verification = step.get("verification")
            _require(isinstance(verification, dict), "step {} requires verification".format(step_id))
            command = verification.get("command")
            inspection = verification.get("inspection")
            _require(("command" in verification) != ("inspection" in verification),
                     "step {} verification must define exactly one of command or inspection".format(step_id))
            if "command" in verification:
                _require(isinstance(command, list) and bool(command) and all(_nonempty_string(arg) for arg in command),
                         "step {} verification command must be a nonempty string list".format(step_id))
            else:
                _require(_nonempty_string(inspection), "step {} inspection must be specific and nonempty".format(step_id))
            _require(_nonempty_string(verification.get("expected")), "step {} requires expected result".format(step_id))
    for identifier, task in by_id.items():
        for dependency in task["depends_on"]:
            _require(_nonempty_string(dependency), "task {} has an invalid dependency".format(identifier))
            _require(dependency in task_ids, "task {} depends on missing task {}".format(identifier, dependency))
    visiting: Set[str] = set()
    visited: Set[str] = set()

    def visit(identifier: str) -> None:
        if identifier in visiting:
            raise ContractError("task dependency graph contains a cycle at {}".format(identifier))
        if identifier in visited:
            return
        visiting.add(identifier)
        for dependency in by_id[identifier]["depends_on"]:
            visit(dependency)
        visiting.remove(identifier)
        visited.add(identifier)

    for identifier in task_ids:
        visit(identifier)


def _validate_plan(contract: Mapping[str, Any]) -> None:
    phases: Any = contract.get("phases")
    _require(isinstance(phases, list) and bool(phases), "plan must declare a nonempty phases array")
    phase_ids: Set[str] = set()
    dependencies: Dict[str, List[str]] = {}
    for phase in phases:
        _require(isinstance(phase, dict), "each plan phase must be an object")
        identifier = phase.get("id")
        _require(isinstance(identifier, str) and re.fullmatch(r"PH-[0-9]{2,}", identifier) is not None,
                 "plan phase ID must use PH- followed by at least two digits")
        _require(identifier not in phase_ids, "duplicate plan phase id: {}".format(identifier))
        _require(_nonempty_string(phase.get("description")), "plan phase {} requires a description".format(identifier))
        refs = phase.get("depends_on")
        _require(isinstance(refs, list) and all(isinstance(item, str) and item for item in refs),
                 "plan phase {} depends_on must be a list of phase IDs".format(identifier))
        _require(len(refs) == len(set(refs)), "plan phase {} has duplicate dependencies".format(identifier))
        phase_ids.add(identifier)
        dependencies[identifier] = refs
    for identifier, refs in dependencies.items():
        _require(all(ref in phase_ids for ref in refs), "plan phase {} depends on an unknown phase".format(identifier))
    visiting: Set[str] = set()
    visited: Set[str] = set()

    def visit(identifier: str) -> None:
        _require(identifier not in visiting, "plan phase dependency graph contains a cycle at {}".format(identifier))
        if identifier in visited:
            return
        visiting.add(identifier)
        for dependency in dependencies[identifier]:
            visit(dependency)
        visiting.remove(identifier)
        visited.add(identifier)

    for identifier in phase_ids:
        visit(identifier)


def _validate_roadmap(contract: Mapping[str, Any]) -> None:
    releases: Any = contract.get("releases")
    _require(isinstance(releases, list) and bool(releases), "roadmap must declare a nonempty releases array")
    seen: Set[str] = set()
    for release in releases:
        _require(isinstance(release, dict), "each roadmap release must be an object")
        version = release.get("version")
        try:
            normalized = normalize_release(version)
        except ContractError as exc:
            raise ContractError("roadmap release version must be strict numeric semver") from exc
        _require(normalized == version, "roadmap release version must use canonical vX.Y.Z form")
        _require(version not in seen, "duplicate roadmap release version: {}".format(version))
        seen.add(version)
        _require(_nonempty_string(release.get("objective")), "roadmap release {} requires an objective".format(version))
        _require(release.get("status") in {"planned", "active", "completed", "deferred", "cancelled"},
                 "roadmap release {} has an unknown status".format(version))


def validate_document(root: Union[str, Path], path: Union[str, Path], check_dependencies: bool = True) -> Dict[str, Any]:
    """Validate one document and, by default, its referenced document digests."""
    root_path = Path(root).resolve()
    document_path = Path(path)
    if not document_path.is_absolute():
        document_path = safe_path(root_path, document_path)
    else:
        try:
            document_path = document_path.resolve()
            document_path.relative_to(root_path)
        except ValueError as exc:
            raise ContractError("document path resolves outside the project root") from exc
    document = read_document(document_path)
    contract = document["contract"]
    _require(contract.get("schema_version") == 1, "schema_version must be 1")
    kind = contract.get("kind")
    _require(isinstance(kind, str) and kind in KINDS,
             "kind must be one of {}".format(", ".join(sorted(KINDS))))
    _require(isinstance(contract.get("revision"), str) and re.fullmatch(r"R[0-9]{2,}", contract["revision"]) is not None,
             "revision must use R followed by at least two digits")
    _require(_nonempty_string(contract.get("id")), "document id must be nonempty")
    _require(isinstance(contract.get("depends_on"), list), "depends_on must be a list")
    if "status" in contract:
        _require(isinstance(contract["status"], str) and contract["status"] in {"draft", "approved", "converged"},
                 "status must be draft, approved, or converged")
    _require(_nonempty_string(document["prose"]), "document prose must not be empty")
    _require(not PLACEHOLDER_RE.search(document["prose"]), "document prose contains a placeholder")
    if contract["kind"] == "spec":
        _validate_spec(contract)
    if contract["kind"] == "plan":
        _validate_plan(contract)
    if contract["kind"] == "roadmap":
        _validate_roadmap(contract)
    if contract["kind"] == "tasks":
        _validate_tasks(contract, root_path)
    if check_dependencies:
        _validate_dependency_refs(root_path, contract)
    return document


def _dependency_kinds(root: Path, document_path: Path, contract: Mapping[str, Any]) -> Set[str]:
    kinds: Set[str] = set()
    for reference in contract.get("depends_on", []):
        target = safe_path(root, reference["path"])
        try:
            kinds.add(read_document(target)["contract"].get("kind"))
        except ContractError:
            raise
    return kinds


def _has_dependency(root: Path, source_path: Path, contract: Mapping[str, Any], target_path: Path) -> bool:
    expected = target_path.resolve()
    for reference in contract.get("depends_on", []):
        if safe_path(root, reference["path"]) == expected:
            return True
    return False


def _validate_dependency_graph(
    root: Path,
    document_path: Path,
    visiting: Optional[Set[Path]] = None,
    visited: Optional[Set[Path]] = None,
) -> None:
    """Validate every referenced document and reject dependency cycles."""
    visiting = set() if visiting is None else visiting
    visited = set() if visited is None else visited
    resolved = document_path.resolve()
    if resolved in visiting:
        raise ContractError("document dependency graph contains a cycle at {}".format(resolved))
    if resolved in visited:
        return
    document = validate_document(root, resolved, check_dependencies=True)
    visiting.add(resolved)
    for reference in document["contract"]["depends_on"]:
        dependency_path = safe_path(root, reference["path"])
        _validate_dependency_graph(root, dependency_path, visiting, visited)
    visiting.remove(resolved)
    visited.add(resolved)


def validate_release(root: Union[str, Path], release: str) -> Dict[str, Any]:
    """Validate a release's spec, plan, tasks, canonical chain, and acceptance coverage."""
    root_path = Path(root).resolve()
    version = normalize_release(release)
    release_dir = safe_path(root_path, Path(".specs") / ("release-" + version))
    spec_path = safe_path(release_dir, "spec.md")
    plan_path = safe_path(release_dir, "plan.md")
    tasks_path = safe_path(release_dir, "tasks.md")
    spec = validate_document(root_path, spec_path)
    plan = validate_document(root_path, plan_path)
    tasks = validate_document(root_path, tasks_path)
    for document_path in (spec_path, plan_path, tasks_path):
        _validate_dependency_graph(root_path, document_path)
    spec_contract = spec["contract"]
    plan_contract = plan["contract"]
    tasks_contract = tasks["contract"]
    _require(spec_contract["kind"] == "spec", "release spec.md must have kind spec")
    _require(plan_contract["kind"] == "plan", "release plan.md must have kind plan")
    _require(tasks_contract["kind"] == "tasks", "release tasks.md must have kind tasks")
    _require(bool(_dependency_kinds(root_path, spec_path, spec_contract) & {"roadmap"}),
             "release spec must depend on a roadmap document")
    roadmap_path = next(
        safe_path(root_path, reference["path"])
        for reference in spec_contract["depends_on"]
        if read_document(safe_path(root_path, reference["path"]))["contract"].get("kind") == "roadmap"
    )
    roadmap_contract = read_document(roadmap_path)["contract"]
    roadmap_releases = roadmap_contract.get("releases")
    _require(isinstance(roadmap_releases, list), "roadmap must declare a releases array")
    selected = [item for item in roadmap_releases if isinstance(item, dict) and item.get("version") == version and item.get("status") == "planned"]
    _require(bool(selected), "roadmap must select this release as planned: {}".format(version))
    _require(bool(_dependency_kinds(root_path, roadmap_path, roadmap_contract) & {"constitution"}),
             "roadmap must depend on a constitution document")
    _require(_has_dependency(root_path, plan_path, plan_contract, spec_path), "release plan must depend on spec.md")
    _require(_has_dependency(root_path, tasks_path, tasks_contract, plan_path), "release tasks must depend on plan.md")
    phases = plan_contract.get("phases")
    _require(isinstance(phases, list) and bool(phases), "plan must declare a nonempty phases array")
    phase_ids: Set[str] = set()
    phase_dependencies: Dict[str, List[str]] = {}
    for phase in phases:
        _require(isinstance(phase, dict), "each plan phase must be an object")
        phase_id = phase.get("id")
        _require(isinstance(phase_id, str) and bool(phase_id.strip()), "plan phase id must be nonempty")
        _require(re.fullmatch(r"PH-[0-9]{2,}", phase_id) is not None, "plan phase ID must use PH- followed by at least two digits")
        _require(phase_id not in phase_ids, "duplicate plan phase id: {}".format(phase_id))
        _require(isinstance(phase.get("description"), str) and bool(phase["description"].strip()), "plan phase description must be nonempty")
        deps = phase.get("depends_on")
        _require(isinstance(deps, list), "plan phase depends_on must be a list")
        phase_ids.add(phase_id)
        phase_dependencies[phase_id] = deps
    for phase_id, deps in phase_dependencies.items():
        _require(all(isinstance(dependency, str) and dependency in phase_ids for dependency in deps),
                 "plan phase {} depends on an unknown phase".format(phase_id))
    visiting_phases: Set[str] = set()
    visited_phases: Set[str] = set()

    def visit_phase(phase_id: str) -> None:
        _require(phase_id not in visiting_phases, "plan phase dependency graph contains a cycle")
        if phase_id in visited_phases:
            return
        visiting_phases.add(phase_id)
        for dependency in phase_dependencies[phase_id]:
            visit_phase(dependency)
        visiting_phases.remove(phase_id)
        visited_phases.add(phase_id)

    for phase_id in phase_ids:
        visit_phase(phase_id)
    _require(all(task_item.get("phase") in phase_ids for task_item in tasks_contract["tasks"]),
             "each task phase must be declared in plan.md")
    acceptance_ids = {criterion["id"] for criterion in spec_contract["acceptance"]}
    story_acceptance: Dict[str, Set[str]] = {story["id"]: set() for story in spec_contract["stories"]}
    for criterion in spec_contract["acceptance"]:
        story_acceptance[criterion["story"]].add(criterion["id"])
    covered: Set[str] = set()
    for task_item in tasks_contract["tasks"]:
        _require(task_item["story"] in story_acceptance, "task {} references unknown story {}".format(task_item["id"], task_item["story"]))
        _require(all(ref in story_acceptance[task_item["story"]] for ref in task_item["acceptance"]),
                 "task {} acceptance criteria must belong to its story".format(task_item["id"]))
        covered.update(task_item["acceptance"])
    missing = acceptance_ids - covered
    _require(not missing, "tasks do not cover acceptance criteria: {}".format(", ".join(sorted(missing))))
    extra = covered - acceptance_ids
    _require(not extra, "tasks reference unknown acceptance criteria: {}".format(", ".join(sorted(extra))))
    return {"release": version, "spec": spec, "plan": plan, "tasks": tasks}
