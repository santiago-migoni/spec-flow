"""Git-pinned phase review and release closure operations for the harness."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Set

from .contracts import ContractError, read_document
from .engine import EngineError
from .store import Store


COMMIT_SUBJECT = re.compile(r"^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\([a-zA-Z0-9._/-]+\))?!?: .+$")


class PhaseController:
    def __init__(self, engine: Any):
        self.e = engine

    def _git(self, *args: str, check: bool = True) -> str:
        try:
            result = subprocess.run(["git", *args], cwd=self.e.root, check=check, capture_output=True, text=True)
        except (OSError, subprocess.CalledProcessError) as exc:
            output = getattr(exc, "stderr", "") or str(exc)
            raise EngineError("git_operation_failed", "Git operation failed: {}".format(output.strip())) from exc
        return result.stdout.strip()

    def _phase(self, state: Mapping[str, Any], phase_id: str) -> Mapping[str, Any]:
        phase = next((item for item in state["phase_contracts"] if item["id"] == phase_id), None)
        if phase is None:
            raise EngineError("phase_unknown", "phase is not declared in the approved plan")
        return phase

    def _require_approved_phase(self, state: Mapping[str, Any], phase_id: str) -> Mapping[str, Any]:
        phase = self._phase(state, phase_id)
        if phase_id not in state["authorized_phases"]:
            raise EngineError("phase_not_authorized", "phase is outside the current explicit execution authorization")
        for dependency in phase["depends_on"]:
            dep = state.get("phases", {}).get(dependency, {})
            if dep.get("status") != "committed":
                raise EngineError("phase_dependency_not_committed", "commit the dependent phase first: {}".format(dependency), details={"phase_id": phase_id, "dependency": dependency})
            self._validate_recorded_commit(state, dependency, dep)
        return phase

    def _source_digests(self, state: Mapping[str, Any]) -> Dict[str, str]:
        self.e._ensure_approvals_current(state)
        return dict(sorted(state["documents"].items()))

    def _assert_task_evidence(self, state: Mapping[str, Any], phase_id: str) -> None:
        missing = []
        stale = []
        for task in state["task_contracts"]:
            if task["phase"] != phase_id:
                continue
            task_id = task["id"]
            task_state = state.get("tasks", {}).get(task_id, {})
            if task_state.get("status") != "completed":
                missing.append(task_id)
                continue
            try:
                self.e._ensure_evidence_current(state, task_id, task_state, enforce_snapshot=False)
            except EngineError as exc:
                stale.append({"task_id": task_id, "code": exc.code, "message": str(exc)})
        if missing:
            raise EngineError("phase_tasks_incomplete", "all phase tasks must be completed", details={"tasks": missing})
        if stale:
            raise EngineError("completed_evidence_stale", "refresh completed task checks before phase review", details={"tasks": stale})

    @staticmethod
    def _sha(value: bytes) -> str:
        return hashlib.sha256(value).hexdigest()

    def _allowed_paths(self, state: Mapping[str, Any], phase_id: str) -> Set[str]:
        allowed: Set[str] = set(state["documents"])
        for task in state["task_contracts"]:
            if task["phase"] == phase_id:
                allowed.update(self.e._task_scope_files(state, task))
        allowed.add(self.e._release_path(state["release"], "tasks.md").relative_to(self.e.root).as_posix())
        allowed.update({".spec-flow/.gitignore", ".spec-flow/config.json", ".spec-flow/approvals.jsonl",
                        ".spec-flow/runs/{}/events.jsonl".format(state["run_id"])})
        evidence = self.e.store.run_dir(state["run_id"]) / "evidence"
        if evidence.is_dir():
            allowed.update(path.relative_to(self.e.root).as_posix() for path in evidence.glob("*.json") if path.is_file())
        for prior in self.e.store.run_ids():
            prior_dir = self.e.store.run_dir(prior)
            prior_evidence = prior_dir / "evidence"
            if prior_evidence.is_dir():
                allowed.update(path.relative_to(self.e.root).as_posix() for path in prior_evidence.glob("*phase*-commit.json") if path.is_file())
        return allowed

    def _changed_paths(self) -> Set[str]:
        # Compare the index and worktree together against HEAD so staged changes
        # cannot disappear from the technical-completion or phase-scope checks.
        tracked = self._git("diff", "HEAD", "--name-only", "-z").split("\0")
        untracked = self._git("ls-files", "--others", "--exclude-standard", "-z").split("\0")
        return {Path(path).as_posix() for path in tracked + untracked if path}

    def _stage_exact(self, allowed: Set[str]) -> List[str]:
        cached = {item for item in self._git("diff", "--cached", "--name-only", "-z").split("\0") if item}
        staged_outside = sorted(cached - allowed)
        if staged_outside:
            raise EngineError("staged_changes_present", "staged changes include files outside this phase", details={"paths": staged_outside})
        changed = self._changed_paths()
        outside = sorted(changed - allowed)
        if outside:
            raise EngineError("phase_scope_changed", "worktree contains changes outside this phase and its canonical audit sources", details={"paths": outside})
        paths = sorted((changed | cached) & allowed)
        if not paths:
            raise EngineError("phase_diff_empty", "phase has no changed phase or audit files to review")
        self._git("add", "--", *paths)
        staged = {item for item in self._git("diff", "--cached", "--name-only", "-z").split("\0") if item}
        if staged != set(paths):
            raise EngineError("phase_stage_mismatch", "Git staged paths differ from the selected phase path set", details={"expected": paths, "actual": sorted(staged)})
        return paths

    def _snapshot_review_tree(self) -> Dict[str, str]:
        return {"parent": self._git("rev-parse", "HEAD"),
                "tree": self._git("write-tree"),
                "diff_sha256": self._sha(self._git("diff", "--cached", "--binary", "HEAD").encode("utf-8"))}

    def _verify_review_tree(self, state: Mapping[str, Any], phase_id: str) -> Mapping[str, Any]:
        phase = state.get("phases", {}).get(phase_id)
        if not isinstance(phase, dict) or phase.get("status") not in {"ready", "reviewed"}:
            raise EngineError("phase_not_ready", "phase-ready must pin this phase before review or commit")
        current = self._snapshot_review_tree()
        expected = {key: phase.get(key) for key in ("parent", "tree", "diff_sha256")}
        if current != expected:
            raise EngineError("phase_review_stale", "HEAD or staged tree changed after phase readiness/review", details={"expected": expected, "actual": current})
        # Expected reviewed paths remain staged relative to HEAD. Only detect
        # edits made in the worktree after readiness here; staged edits already
        # alter the pinned tree and are caught by the snapshot comparison above.
        unstaged = self._git("diff", "--name-only", "-z").split("\0")
        untracked = self._git("ls-files", "--others", "--exclude-standard", "-z").split("\0")
        post_ready = {path for path in unstaged + untracked if path and not path.startswith(".spec-flow/")}
        if post_ready:
            raise EngineError("phase_review_stale", "worktree changed after phase readiness/review", details={"paths": sorted(post_ready)})
        self._assert_task_evidence(state, phase_id)
        self._source_digests(state)
        return phase

    def ready(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        self.e._fields(payload, ("run_id", "owner", "phase_id"))
        state = self.e._owned_state(payload)
        if state.get("status") != "active" or state.get("active_task"):
            raise EngineError("phase_not_idle", "phase readiness requires an active idle run")
        phase_id = self.e._nonempty(payload["phase_id"], "phase_id")
        self._require_approved_phase(state, phase_id)
        self._assert_task_evidence(state, phase_id)
        digests = self._source_digests(state)
        prior = state.get("phases", {}).get(phase_id, {})
        if prior.get("status") in {"reviewed", "committed"}:
            raise EngineError("phase_already_reviewed", "a reviewed or committed phase cannot be prepared again")
        allowed = self._allowed_paths(state, phase_id)
        staged_paths = self._stage_exact(allowed)
        pin = self._snapshot_review_tree()
        marker = "SPEC_FLOW_PHASE_REVIEW={}/{}/{}".format(state["run_id"], phase_id, pin["tree"])
        packet = {"schema": "spec-flow-phase-review.v1", "run_id": state["run_id"], "release": state["release"],
                  "phase_id": phase_id, **pin, "staged_paths": staged_paths,
                  "task_ids": sorted(task["id"] for task in state["task_contracts"] if task["phase"] == phase_id),
                  "source_digests": digests, "marker": marker, "created_at": self.e._now()}
        packet["packet_sha256"] = self._sha(json.dumps(packet, sort_keys=True, separators=(",", ":")).encode("utf-8"))
        packet_path = self.e.store.run_dir(state["run_id"]) / "packets" / "phase-{}-{}.json".format(phase_id, pin["tree"])
        packet = self._write_packet(packet_path, packet)
        self.e._append(state["run_id"], "phase_ready", {"phase_id": phase_id, **pin,
                       "staged_paths": staged_paths, "source_digests": digests,
                       "packet_path": packet_path.relative_to(self.e.root).as_posix(),
                       "packet_sha256": packet["packet_sha256"], "marker": marker})
        return {"run_id": state["run_id"], "phase_id": phase_id, "phase_status": "ready", **pin,
                "staged_paths": staged_paths, "packet_path": str(packet_path), "packet_sha256": packet["packet_sha256"], "phase_marker": marker}

    def _write_packet(self, path: Path, packet: Mapping[str, Any]) -> Dict[str, Any]:
        if path.exists():
            try:
                old = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, json.JSONDecodeError) as exc:
                raise EngineError("phase_packet_corrupt", "existing phase review packet is unreadable") from exc
            stable = ("schema", "run_id", "release", "phase_id", "parent", "tree", "diff_sha256", "staged_paths", "task_ids", "source_digests", "marker")
            unhashed = {key: value for key, value in old.items() if key != "packet_sha256"} if isinstance(old, dict) else {}
            digest = self._sha(json.dumps(unhashed, sort_keys=True, separators=(",", ":")).encode("utf-8"))
            if not isinstance(old, dict) or any(old.get(key) != packet.get(key) for key in stable) or old.get("packet_sha256") != digest:
                raise EngineError("phase_packet_exists", "a different immutable review packet already exists")
            return old
        try:
            with path.open("x", encoding="utf-8") as stream:
                json.dump(packet, stream, ensure_ascii=False, sort_keys=True, indent=2)
                stream.write("\n")
                stream.flush()
                import os
                os.fsync(stream.fileno())
            Store._fsync_directory(path.parent)
            return dict(packet)
        except FileExistsError as exc:
            raise EngineError("phase_packet_exists", "review packet already exists") from exc
        except OSError as exc:
            raise EngineError("phase_packet_write_failed", "could not persist immutable phase packet") from exc

    def review(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        self.e._fields(payload, ("run_id", "owner", "phase_id", "reviewer_session", "reviewer_agent_id", "verdict", "evidence"))
        state = self.e._owned_state(payload)
        phase_id = self.e._nonempty(payload["phase_id"], "phase_id")
        phase = self._require_approved_phase(state, phase_id)
        ready = self._verify_review_tree(state, phase_id)
        reviewer_session = self.e._nonempty(payload["reviewer_session"], "reviewer_session")
        reviewer_agent_id = self.e._nonempty(payload["reviewer_agent_id"], "reviewer_agent_id")
        known_sessions = {state["owner"]}
        known_sessions.update(task.get("agent", {}).get("session_id") for task in state.get("tasks", {}).values() if isinstance(task.get("agent"), dict))
        if reviewer_session in known_sessions:
            raise EngineError("reviewer_not_independent", "phase reviewer must be distinct from the run owner and every implementer")
        verdict = payload["verdict"]
        if verdict not in {"pass", "changes"}:
            raise EngineError("invalid_input", "phase review verdict must be pass or changes")
        evidence = self.e._nonempty(payload["evidence"], "evidence")
        packet = json.loads(self.e._project_path(ready["packet_path"]).read_text(encoding="utf-8"))
        native = self.e._adapter_call("attest_session", reviewer_session, "reviewer", parent_session=state["owner"],
                                      agent_path=reviewer_agent_id, task_marker=ready["marker"], require_finished=True)
        if native.get("agent_lifecycle") != "completed":
            raise EngineError("reviewer_not_completed", "independent phase reviewer must have a completed native session")
        if native.get("session_id") in known_sessions:
            raise EngineError("reviewer_not_independent", "phase reviewer session is not distinct")
        self.e._append(state["run_id"], "phase_reviewed", {"phase_id": phase_id, "verdict": verdict,
                       "reviewer_session": reviewer_session, "reviewer_agent_id": reviewer_agent_id,
                       "evidence": evidence, "review_packet_sha256": packet["packet_sha256"],
                       "host_attestation": native, "reviewed_at": self.e._now()})
        return {"run_id": state["run_id"], "phase_id": phase_id,
                "phase_status": "reviewed" if verdict == "pass" else "ready", "verdict": verdict}

    def _commit_candidates(self, run_id: str, phase_id: str) -> List[Dict[str, Any]]:
        output = self._git("log", "HEAD", "-n", "1000", "--format=%H%x00%P%x00%T%x00%s%x00%B%x00")
        parts = output.split("\0")
        rows = []
        index = 0
        while index + 4 < len(parts):
            sha, parents, tree, subject, body = (item.strip() for item in parts[index:index+5])
            index += 5
            if not sha:
                continue
            run_trailer = "Spec-Flow-Run: {}".format(run_id)
            phase_trailer = "Spec-Flow-Phase: {}".format(phase_id)
            if run_trailer in body and phase_trailer in body:
                rows.append({"sha": sha, "parent": parents.split()[0] if parents else "", "tree": tree,
                             "subject": subject, "body": body})
        return rows

    def _audit_candidates(self, run_id: str) -> List[Dict[str, Any]]:
        output = self._git("log", "HEAD", "-n", "1000", "--format=%H%x00%P%x00%T%x00%s%x00%B%x00")
        parts = output.split("\0")
        rows = []
        for index in range(0, len(parts) - 4, 5):
            sha, parents, tree, subject, body = (item.strip() for item in parts[index:index + 5])
            if sha and "Spec-Flow-Audit: {}".format(run_id) in body:
                rows.append({"sha": sha, "parent": parents.split()[0] if parents else "", "tree": tree,
                             "subject": subject, "body": body})
        return rows

    def _validate_recorded_commit(self, state: Mapping[str, Any], phase_id: str, phase: Mapping[str, Any]) -> None:
        commit = phase.get("commit")
        if not isinstance(commit, dict) or not isinstance(commit.get("sha"), str):
            raise EngineError("phase_commit_invalid", "phase commit receipt is missing")
        ancestor = subprocess.run(["git", "merge-base", "--is-ancestor", commit["sha"], "HEAD"], cwd=self.e.root,
                                  capture_output=True, text=True)
        if ancestor.returncode != 0:
            raise EngineError("phase_commit_not_ancestor", "phase commit is not in the current branch history", details={"phase_id": phase_id, "sha": commit["sha"]})
        matching = [item for item in self._commit_candidates(state["run_id"], phase_id) if item["sha"] == commit["sha"]]
        if len(matching) != 1 or matching[0]["parent"] != commit.get("parent") or matching[0]["tree"] != commit.get("tree"):
            raise EngineError("phase_commit_invalid", "phase receipt does not match the commit's parent, tree, and trailers", details={"phase_id": phase_id})

    def commit(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        self.e._fields(payload, ("run_id", "owner", "phase_id", "subject"))
        state = self.e._owned_state(payload)
        phase_id = self.e._nonempty(payload["phase_id"], "phase_id")
        subject = self.e._nonempty(payload["subject"], "subject")
        if not COMMIT_SUBJECT.fullmatch(subject):
            raise EngineError("invalid_commit_subject", "phase commit subject must follow Conventional Commits")
        phase_state = state.get("phases", {}).get(phase_id, {})
        if phase_state.get("status") == "committed":
            self._validate_recorded_commit(state, phase_id, phase_state)
            return {"run_id": state["run_id"], "phase_id": phase_id, "phase_status": "committed", "commit_sha": phase_state["commit"]["sha"], "already_committed": True}
        if phase_state.get("status") != "reviewed" or phase_state.get("review", {}).get("verdict") != "pass":
            raise EngineError("phase_review_required", "a passing independent Sol phase review is required before commit")
        # Recover a commit that Git created before the receipt event was durable.
        candidates = self._commit_candidates(state["run_id"], phase_id)
        exact = [row for row in candidates if row["parent"] == phase_state["parent"] and row["tree"] == phase_state["tree"] and row["subject"] == subject]
        if candidates:
            self._assert_task_evidence(state, phase_id)
            self._source_digests(state)
            if len(candidates) != 1 or len(exact) != 1:
                raise EngineError("phase_commit_ambiguous", "matching run/phase trailers exist but do not identify one exact reviewed commit", details={"candidates": [row["sha"] for row in candidates]})
            commit = exact[0]
            adopted = True
        else:
            self._verify_review_tree(state, phase_id)
            self._require_approved_phase(state, phase_id)
            message_body = "Spec-Flow-Run: {}\nSpec-Flow-Phase: {}".format(state["run_id"], phase_id)
            try:
                self._git("commit", "-m", subject, "-m", message_body)
            except EngineError:
                # Git may have committed despite a lost response. Reconcile from history before failing.
                rows = self._commit_candidates(state["run_id"], phase_id)
                exact = [row for row in rows if row["parent"] == phase_state["parent"] and row["tree"] == phase_state["tree"] and row["subject"] == subject]
                if len(exact) != 1 or len(rows) != 1:
                    raise
                commit = exact[0]
                adopted = True
            else:
                commit = self._commit_candidates(state["run_id"], phase_id)[0]
                if commit["parent"] != phase_state["parent"] or commit["tree"] != phase_state["tree"] or commit["subject"] != subject:
                    raise EngineError("phase_commit_mismatch", "Git commit does not match the reviewed parent, tree, or subject")
                adopted = False
        receipt = {"schema": "spec-flow-phase-receipt.v1", "run_id": state["run_id"], "release": state["release"],
                   "phase_id": phase_id, "sha": commit["sha"], "parent": commit["parent"], "tree": commit["tree"],
                   "subject": subject, "review_packet_sha256": phase_state["review"]["review_packet_sha256"],
                   "evidence": phase_state["review"]["evidence"], "adopted_after_crash": adopted,
                   "committed_at": self.e._now()}
        receipt_path = self.e.store.run_dir(state["run_id"]) / "evidence" / "{}-phase-commit.json".format(phase_id)
        self.e.store.write_json_atomic(receipt_path, receipt)
        self.e._append(state["run_id"], "phase_committed", {"phase_id": phase_id, "commit": receipt,
                       "receipt_path": receipt_path.relative_to(self.e.root).as_posix()})
        return {"run_id": state["run_id"], "phase_id": phase_id, "phase_status": "committed",
                "commit_sha": commit["sha"], "receipt_path": str(receipt_path), "adopted_after_crash": adopted}

    def refresh_evidence(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        self.e._fields(payload, ("run_id", "owner", "task_id"), ("inspection_evidence", "timeout_seconds"))
        state = self.e._owned_state(payload)
        task_id = self.e._nonempty(payload["task_id"], "task_id")
        task_state = state.get("tasks", {}).get(task_id, {})
        if task_state.get("status") != "completed":
            raise EngineError("task_not_completed", "only completed task evidence can be refreshed")
        task = self.e._task_contract(state, task_id)
        digests = self._source_digests(state)
        current_snapshot = self.e._snapshot_code()
        fingerprint = self.e._scope_fingerprint(current_snapshot, self.e._task_scope_files(state, task))
        if task_state.get("code_fingerprint") == fingerprint and task_state.get("source_digests", state["documents"]) == digests:
            return {"run_id": state["run_id"], "task_id": task_id, "refreshed": False, "already_current": True}
        timeout = payload.get("timeout_seconds", 60)
        if not isinstance(timeout, (int, float)) or timeout <= 0 or timeout > 300:
            raise EngineError("invalid_input", "timeout_seconds must be between 0 and 300")
        inspections = payload.get("inspection_evidence", {})
        if not isinstance(inspections, dict):
            raise EngineError("invalid_input", "inspection_evidence must be an object")
        before = self.e._snapshot_code()
        outputs = []
        for step in task["steps"]:
            verification = step["verification"]
            if "command" in verification:
                try:
                    proc = subprocess.run(verification["command"], cwd=str(self.e.root), shell=False, check=False,
                                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                                          encoding="utf-8", errors="replace", timeout=timeout)
                except (OSError, subprocess.TimeoutExpired) as exc:
                    raise EngineError("verification_failed", "could not refresh task check {}: {}".format(step["id"], exc)) from exc
                output = proc.stdout or ""
                if proc.returncode != 0 or not output.strip() or any(pattern in output.lower() for pattern in ("ran 0 tests", "no tests ran", "no tests to run")):
                    raise EngineError("verification_failed", "refreshed task check did not produce a passing nonempty result", details={"step_id": step["id"], "exit_code": proc.returncode, "output": output[-2000:]})
                exit_code = proc.returncode
            else:
                output = inspections.get(step["id"], "")
                if not isinstance(output, str) or not output.strip():
                    raise EngineError("inspection_evidence_required", "refresh requires current inspection evidence for {}".format(step["id"]))
                exit_code = None
            outputs.append({"step_id": step["id"], "command": verification.get("command"), "inspection": verification.get("inspection"),
                            "expected": verification["expected"], "observed": output[-4000:], "output": output[-4000:],
                            "output_sha256": self._sha(output.encode("utf-8")), "exit_code": exit_code, "source_digests": digests,
                            "code_fingerprint": fingerprint})
        after = self.e._snapshot_code()
        changes = self.e._changed_paths(before, after)
        if changes:
            raise EngineError("verification_mutated_code", "refresh checks changed project files", details={"paths": sorted(changes)})
        evidence_path = self.e.store.run_dir(state["run_id"]) / "evidence" / "{}-refresh-{}.json".format(task_id, self.e._now().replace(":", ""))
        self.e.store.write_json_atomic(evidence_path, {"task_id": task_id, "steps": outputs, "code_fingerprint": fingerprint})
        self.e._append(state["run_id"], "task_evidence_refreshed", {"task_id": task_id, "steps": outputs,
                       "code_fingerprint": fingerprint, "verified_snapshot": after,
                       "source_digests": digests, "evidence_path": evidence_path.relative_to(self.e.root).as_posix()})
        return {"run_id": state["run_id"], "task_id": task_id, "refreshed": True, "evidence_path": str(evidence_path)}

    def complete(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        self.e._fields(payload, ("release",), ("run_id",))
        release = self.e._release_version(payload["release"])
        if "run_id" in payload:
            run_ids = [self.e._nonempty(payload["run_id"], "run_id")]
        else:
            run_ids = self.e.store.run_ids()
        state = None
        for run_id in reversed(run_ids):
            try:
                candidate = self.e._state(run_id)
            except EngineError:
                continue
            if candidate.get("release") == release:
                state = candidate
                break
        if state is None:
            return {"release": release, "complete": False, "reasons": ["no execution run exists for this release"]}
        reasons: List[str] = []
        try:
            self._source_digests(state)
        except EngineError as exc:
            reasons.append("approved sources are not current: {}".format(exc))
        for task in state["task_contracts"]:
            task_id = task["id"]
            task_state = state.get("tasks", {}).get(task_id, {})
            if task_state.get("status") != "completed":
                reasons.append("task {} is not completed".format(task_id))
                continue
            try:
                self.e._ensure_evidence_current(state, task_id, task_state, enforce_snapshot=False)
            except EngineError as exc:
                reasons.append("task {} evidence is stale: {}".format(task_id, exc.code))
        for phase in state["phase_contracts"]:
            phase_id = phase["id"]
            record = state.get("phases", {}).get(phase_id, {})
            if record.get("status") != "committed":
                reasons.append("phase {} is not committed".format(phase_id))
                continue
            receipt = record.get("commit", {})
            try:
                self._validate_recorded_commit(state, phase_id, record)
            except EngineError:
                reasons.append("phase {} commit receipt does not match current branch history".format(phase_id))
        # Task evidence may be refreshed after code changes. That refresh
        # confirms the checks, but it must not silently replace the code that
        # an independent phase review committed. Compare all declared task
        # files with the last reviewed phase tree even when later clean commits
        # have moved HEAD forward.
        if state["phase_contracts"]:
            last_phase_id = state["phase_contracts"][-1]["id"]
            reviewed = state.get("phases", {}).get(last_phase_id, {}).get("commit", {})
            reviewed_sha = reviewed.get("sha") if isinstance(reviewed, dict) else None
            scope = sorted({path for task in state["task_contracts"] for path in self.e._task_scope_files(state, task)})
            if reviewed_sha and scope:
                compared = subprocess.run(["git", "diff", "--quiet", reviewed_sha, "--", *scope], cwd=self.e.root)
                if compared.returncode == 1:
                    reasons.append("task files differ from the reviewed phase tree")
                elif compared.returncode != 0:
                    reasons.append("could not compare current task files with the reviewed phase tree")
        review = state.get("release_review")
        closure_reasons: List[str] = []
        if not isinstance(review, dict):
            closure_reasons.append("release-review has not been recorded")
        else:
            audits = self._audit_candidates(state["run_id"])
            if len(audits) != 1 or audits[0]["subject"] != "docs(spec-flow): record release review":
                closure_reasons.append("final audit commit is missing or ambiguous")
            elif self._git("rev-parse", "HEAD") != audits[0]["sha"]:
                closure_reasons.append("final audit commit is not the current branch tip")
            elif state["phase_contracts"] and audits[0]["parent"] != state.get("phases", {}).get(state["phase_contracts"][-1]["id"], {}).get("commit", {}).get("sha"):
                closure_reasons.append("final audit commit does not directly follow the last reviewed phase commit")
            elif self._git("status", "--porcelain"):
                closure_reasons.append("worktree changed after the final audit commit")
        changed_implementation = sorted(path for path in self._changed_paths() if not path.startswith(".spec-flow/"))
        if changed_implementation:
            reasons.append("worktree changed after the reviewed phase commit: {}".format(", ".join(changed_implementation)))
        technical_complete = not reasons
        return {"release": release, "run_id": state["run_id"], "technical_complete": technical_complete,
                "complete": technical_complete, "reasons": reasons,
                "release_review_pending": not isinstance(review, dict), "audit_pending": bool(closure_reasons),
                "release_closure_reasons": closure_reasons,
                "phase_commits": {phase_id: phase.get("commit", {}).get("sha") for phase_id, phase in state.get("phases", {}).items() if phase.get("status") == "committed"}}

    def release_review(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        self.e._fields(payload, ("run_id", "owner", "impact_status"), ("impact_evidence", "delivery_status"))
        state = self.e._state(self.e._nonempty(payload["run_id"], "run_id"))
        owner = self.e._nonempty(payload["owner"], "owner")
        self.e._require_owner(state, owner)
        if state.get("status") != "completed" or any(state.get("phases", {}).get(p["id"], {}).get("status") != "committed" for p in state["phase_contracts"]):
            raise EngineError("phase_commits_required", "release review requires all declared phase commits")
        self.e._adapter_call("attest_session", owner, "orchestrator")
        self.e._adapter_call("assert_lease", state)
        impact_status = payload["impact_status"]
        if impact_status not in {"observed", "pending", "unavailable"}:
            raise EngineError("invalid_input", "impact_status must be observed, pending, or unavailable")
        evidence = payload.get("impact_evidence", [])
        if not isinstance(evidence, list) or not all(isinstance(item, str) and item.strip() for item in evidence):
            raise EngineError("invalid_input", "impact_evidence must be a list of nonempty durable references")
        if impact_status == "observed" and not evidence:
            raise EngineError("impact_evidence_required", "observed impact requires at least one evidence reference")
        delivery = payload.get("delivery_status", "branch_committed")
        if delivery not in {"branch_committed", "branch_retained", "not_integrated"}:
            raise EngineError("invalid_input", "delivery_status is not recognized")
        existing = state.get("release_review")
        if existing:
            record = existing["record"]
            reference = existing["roadmap_reference"]
            if (record.get("impact_status"), record.get("impact_evidence"), record.get("delivery_status")) != (impact_status, evidence, delivery):
                raise EngineError("release_review_already_recorded", "a different release-review record is already durable")
        else:
            commits = [{"phase_id": item["id"], "sha": state["phases"][item["id"]]["commit"]["sha"]} for item in state["phase_contracts"]]
            record = {"schema": "spec-flow.derived-release.v1", "kind": "release-review", "release": state["release"],
                      "run_id": state["run_id"], "technical_status": "complete", "phase_commits": commits,
                      "impact_status": impact_status, "impact_evidence": evidence, "delivery_status": delivery,
                      "publication": False, "external_side_effects": False}
            spec_path = self.e._release_path(state["release"], "spec.md")
            roadmap_path = self._roadmap_path(state)
            reference = {"schema": "spec-flow.derived-reference.v1", "kind": "roadmap-reference",
                         "release": state["release"], "run_id": state["run_id"],
                         "spec_path": spec_path.relative_to(self.e.root).as_posix(), "impact_status": impact_status}
            self._write_generated(spec_path, record, status="converged")
            self._write_generated(roadmap_path, reference)
            self.e._append(state["run_id"], "release_reviewed", {"record": record, "roadmap_reference": reference,
                           "reviewed_at": self.e._now()})

        # The final audit commit captures the last phase receipt, derived docs,
        # and release_reviewed event in one reviewable tree. It has no receipt,
        # avoiding a circular commit/receipt loop.
        audits = self._audit_candidates(state["run_id"])
        audit_subject = "docs(spec-flow): record release review"
        if audits:
            if len(audits) != 1 or audits[0]["subject"] != audit_subject or self._git("rev-parse", "HEAD") != audits[0]["sha"]:
                raise EngineError("audit_commit_ambiguous", "final audit commit is ambiguous or no longer the branch tip")
            if self._git("status", "--porcelain"):
                raise EngineError("audit_commit_stale", "worktree changed after the final audit commit")
            commit_sha = audits[0]["sha"]
            adopted = True
        else:
            allowed = {self.e._release_path(state["release"], "spec.md").relative_to(self.e.root).as_posix(),
                       reference["spec_path"], self._roadmap_path(state).relative_to(self.e.root).as_posix(),
                       ".spec-flow/runs/{}/events.jsonl".format(state["run_id"])}
            for phase in state["phase_contracts"]:
                allowed.add(".spec-flow/runs/{}/evidence/{}-phase-commit.json".format(state["run_id"], phase["id"]))
            staged = {item for item in self._git("diff", "--cached", "--name-only", "-z").split("\0") if item}
            outside_staged = sorted(staged - allowed)
            if outside_staged:
                raise EngineError("staged_changes_present", "final audit contains staged files outside its exact record set", details={"paths": outside_staged})
            changed = self._changed_paths()
            outside = sorted(changed - allowed)
            if outside:
                raise EngineError("phase_scope_changed", "final audit found unrelated worktree changes", details={"paths": outside})
            paths = sorted((changed | staged) & allowed)
            if not paths:
                raise EngineError("audit_diff_empty", "final audit has no derived records or receipts to capture")
            self._git("add", "--", *paths)
            commit_parent = self._git("rev-parse", "HEAD")
            try:
                self._git("commit", "-m", audit_subject, "-m", "Spec-Flow-Audit: {}".format(state["run_id"]))
            except EngineError:
                audits = self._audit_candidates(state["run_id"])
                if len(audits) != 1 or audits[0]["subject"] != audit_subject or audits[0]["parent"] != commit_parent:
                    raise
                commit_sha, adopted = audits[0]["sha"], True
            else:
                audits = self._audit_candidates(state["run_id"])
                if len(audits) != 1 or audits[0]["subject"] != audit_subject or audits[0]["parent"] != commit_parent:
                    raise EngineError("audit_commit_mismatch", "final audit commit does not match expected parent and subject")
                commit_sha, adopted = audits[0]["sha"], False
        current = self.e._state(state["run_id"])
        self.e._adapter_call("release", current)
        return {"run_id": state["run_id"], "release_review": record, "roadmap_reference": reference,
                "audit_commit_sha": commit_sha, "adopted_after_crash": adopted}

    def _write_generated(self, path: Path, record: Mapping[str, Any], *, status: Optional[str] = None) -> None:
        document = read_document(path)
        text = path.read_text(encoding="utf-8")
        # Remove any prior strictly-shaped generated tail; malformed blocks fail closed in read_document.
        from .contracts import _strip_generated_tail, CONTRACT_BLOCK_RE
        match = CONTRACT_BLOCK_RE.search(text)
        if not match:
            raise EngineError("contract_invalid", "derived release record requires a canonical contract block")
        suffix = text[match.end():]
        base_suffix = _strip_generated_tail(suffix).rstrip("\r\n")
        prefix = text[:match.end()]
        contract = document["contract"]
        if status is not None:
            contract["status"] = status
            encoded = json.dumps(contract, ensure_ascii=False, indent=2)
            prefix = text[:match.start()] + "```spec-flow\n" + encoded + "\n```"
        canonical_record = json.dumps(dict(record), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        generated = "\n\n<!-- spec-flow:generated:start -->\nSpec-Flow derived record:\n" + canonical_record + "\n<!-- spec-flow:generated:end -->\n"
        path.write_text(prefix + base_suffix + generated, encoding="utf-8")

    def _roadmap_path(self, state: Mapping[str, Any]) -> Path:
        spec_path = self.e._release_path(state["release"], "spec.md")
        spec = read_document(spec_path)["contract"]
        for reference in spec["depends_on"]:
            path = self.e._project_path(reference["path"])
            if read_document(path)["contract"].get("kind") == "roadmap":
                return path
        raise EngineError("roadmap_reference_missing", "approved release spec has no canonical roadmap dependency")
