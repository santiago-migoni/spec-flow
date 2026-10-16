"""Read-only independent checks of the original E7 disposable native fixtures.

Uses the pinned production adapter. Does not refresh controller verification,
repair state, acquire a lease, or copy private host session logs.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("evidence", type=Path)
    args = parser.parse_args()
    evidence = args.evidence.resolve()
    summary = json.loads((evidence / "native/native-result-summary.json").read_text())
    sys.path.insert(0, summary["source_package_root"])
    from harness.runtime.engine import Engine
    from harness.runtime.codex_adapter import NativeCodexAdapter

    def git(root, *argv):
        return subprocess.check_output(["git", *argv], cwd=root, text=True).strip()

    out = {"evaluated_commit": summary["evaluated_commit"],
           "checked_at": datetime.now(timezone.utc).isoformat(),
           "scope": "Original fixtures; status and host attestation read-only. Independent unittest runs confer no controller credit.",
           "owner": None, "fixtures": {}}
    owner = summary["owner"]
    first_root = Path(summary["fixture_runs"]["fresh"]["linked_worktree"])
    out["owner"] = NativeCodexAdapter(first_root).attest_session(
        owner["session_id"], "orchestrator", parent_session="01a13f8c-b50f-7db0-b28d-162f4914e043",
        agent_path=owner["agent_path"], require_finished=True)
    sessions = {owner["session_id"]}
    for label, fixture in summary["fixture_runs"].items():
        root = Path(fixture["linked_worktree"])
        state = Engine(root).dispatch("status", {"run_id": fixture["run_id"]})
        events_path = root / ".spec-flow/runs" / fixture["run_id"] / "events.jsonl"
        events = [json.loads(line) for line in events_path.read_text().splitlines()]
        assert [e["seq"] for e in events] == list(range(1, len(events) + 1))
        adapter = NativeCodexAdapter(root)
        attempts = {}
        attestations = []
        for event in events:
            data = event["data"]
            if event["event"] == "prepared":
                attempts[(data["task_id"], data["attempt"])] = data
            if event["event"] == "agent_bound":
                prepared = attempts[(data["task_id"], data["attempt"])]
                actual = adapter.attest_session(data["session_id"], "implementer",
                    parent_session=owner["session_id"], agent_path=data["agent_path"], require_finished=True,
                    task_marker="SPEC_FLOW_PACKET_SHA256=" + prepared["packet_sha256"], after=prepared["prepared_at"])
                attestations.append({"task_id": data["task_id"], "attempt": data["attempt"], "attestation": actual})
                assert data["session_id"] not in sessions
                sessions.add(data["session_id"])
        phases = {}
        for phase_id, phase in state["phases"].items():
            review = phase["review"]
            actual = adapter.attest_session(review["reviewer_session"], "reviewer",
                parent_session=owner["session_id"], agent_path=review["reviewer_agent_id"], require_finished=True,
                task_marker=phase["marker"], after=phase["ready_at"])
            assert review["reviewer_session"] not in sessions
            sessions.add(review["reviewer_session"])
            commit = phase["commit"]
            assert git(root, "rev-parse", "HEAD") == commit["sha"] == fixture["phase_commit_sha"]
            assert git(root, "rev-parse", commit["sha"] + "^{tree}") == commit["tree"] == phase["tree"]
            assert git(root, "rev-parse", commit["sha"] + "^") == commit["parent"] == phase["parent"]
            phases[phase_id] = {"status": phase["status"], "commit": commit,
                                "review_attestation": actual, "exact_commit_tree_parent": True}
        common = Path(git(root, "rev-parse", "--git-common-dir"))
        if not common.is_absolute():
            common = (root / common).resolve()
        lease = common / "spec-flow-active-controller.json"
        assert state["status"] == "abandoned" and state["active_task"] is None
        assert not lease.exists()
        assert not state.get("release_review")
        assert "docs(spec-flow): record release review" not in git(root, "log", "--format=%s").splitlines()
        test_hash = hashlib.sha256((root / "test_release.py").read_bytes()).hexdigest()
        assert test_hash == fixture["test_file_sha256"]
        before_code = hashlib.sha256((root / "release.py").read_bytes()).hexdigest()
        started = datetime.now(timezone.utc).isoformat()
        test = subprocess.run(["python3", "-B", "-m", "unittest", "-v", "test_release.py"], cwd=root,
                              env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}, text=True, capture_output=True)
        assert test.returncode == (1 if label == "negative" else 0)
        assert hashlib.sha256((root / "release.py").read_bytes()).hexdigest() == before_code
        assert hashlib.sha256((root / "test_release.py").read_bytes()).hexdigest() == test_hash
        row = {"root": str(root), "run_id": fixture["run_id"], "status": state["status"],
               "active_task": state["active_task"], "release_review": None, "audit_commit_absent": True,
               "ownership_registry": str(lease), "lease_absent": True,
               "head": git(root, "rev-parse", "HEAD"), "events": len(events),
               "events_sha256": hashlib.sha256(events_path.read_bytes()).hexdigest(),
               "task_attempts": attestations, "phases": phases,
               "independent_test": {"argv": ["python3", "-B", "-m", "unittest", "-v", "test_release.py"],
                                    "started_at": started, "exit_code": test.returncode,
                                    "stdout": test.stdout, "stderr": test.stderr,
                                    "test_sha256": test_hash, "code_sha256": before_code, "code_unchanged": True},
               "retained_worktree_status": git(root, "status", "--short")}
        if label == "legacy":
            row["migration_checkpoint"] = git(root, "rev-parse", fixture["migration_checkpoint"])
            row["legacy_source_commit"] = git(root, "rev-parse", fixture["legacy_source_head"])
        out["fixtures"][label] = row
    assert len(sessions) == 9
    out["distinct_attested_sessions"] = len(sessions)
    out["result"] = "PASS: identities, markers, terminal lifecycles, commits, tests and teardown match recorded native outcomes"
    (evidence / "native-independent-check.json").write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"result": out["result"], "sessions": len(sessions), "fixtures": len(out["fixtures"])}, ensure_ascii=False))


if __name__ == "__main__":
    main()
