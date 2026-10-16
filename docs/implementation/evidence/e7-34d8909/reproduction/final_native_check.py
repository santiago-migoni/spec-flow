"""Independent read-only attestation/state checks and final nonmutating tests.

Does not refresh execution credit, acquire/release ownership or repair records.
Actual incomplete/blocked negative state is preserved, not coerced into success.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

parser = argparse.ArgumentParser()
parser.add_argument("context", type=Path)
args = parser.parse_args()
c = json.loads(args.context.read_text())
E = Path(c["evidence_directory"])
B = Path(c["disposable_base"])
sys.path.insert(0, c["source_package_root"])
from harness.runtime.engine import Engine
from harness.runtime.codex_adapter import NativeCodexAdapter
from harness.runtime.phases import PhaseController

def git(root, *argv):
    return subprocess.check_output(["git", "--no-optional-locks", *argv], cwd=root, text=True).strip()

owner = c["recovery_owner"]
adapter = NativeCodexAdapter(B)
owner_att = adapter.attest_session(owner, "orchestrator", parent_session=c["parent_session"],
                                   agent_path="/root/e7_owner_f8fa91d", require_finished=True)
out = {"checked_at": datetime.now(timezone.utc).isoformat(), "evaluated_commit": c["evaluated_commit"],
       "category": "Independent actual host attestation and production state checks; independent test reruns confer no controller task credit",
       "owner_attestation": owner_att, "fixtures": {}}
sessions = {owner}
for label in ("fresh", "legacy", "negative"):
    root = B / (label + "-linked")
    run_id = (E / "native" / label / "run-id.txt").read_text().strip()
    engine = Engine(root)
    state = engine.dispatch("status", {"run_id": run_id})
    journal = root / ".spec-flow/runs" / run_id / "events.jsonl"
    events = [json.loads(line) for line in journal.read_text().splitlines()]
    assert [event["seq"] for event in events] == list(range(1, len(events) + 1))
    attempts = {}
    attestations = []
    for event in events:
        data = event["data"]
        if event["event"] == "prepared":
            attempts[(data["task_id"], data["attempt"])] = data
        if event["event"] == "agent_bound":
            prepared = attempts[(data["task_id"], data["attempt"])]
            actual = NativeCodexAdapter(root).attest_session(data["session_id"], "implementer",
                parent_session=owner, agent_path=data["agent_path"], require_finished=True,
                task_marker="SPEC_FLOW_PACKET_SHA256=" + prepared["packet_sha256"], after=prepared["prepared_at"])
            assert data["session_id"] not in sessions
            sessions.add(data["session_id"])
            attestations.append({"task_id": data["task_id"], "attempt": data["attempt"], "attestation": actual})
    phases = {}
    for phase_id, phase in state["phases"].items():
        review = phase["review"]
        actual = NativeCodexAdapter(root).attest_session(review["reviewer_session"], "reviewer",
            parent_session=owner, agent_path=review["reviewer_agent_id"], require_finished=True,
            task_marker=phase["marker"], after=phase["ready_at"])
        assert review["reviewer_session"] not in sessions
        sessions.add(review["reviewer_session"])
        commit = phase["commit"]
        assert git(root, "rev-parse", commit["sha"] + "^{tree}") == commit["tree"] == phase["tree"]
        assert git(root, "rev-parse", commit["sha"] + "^") == commit["parent"] == phase["parent"]
        phases[phase_id] = {"commit": commit, "exact_tree_parent": True, "review_attestation": actual}
    common = Path(git(root, "rev-parse", "--git-common-dir"))
    if not common.is_absolute():
        common = (root / common).resolve()
    registry = common / "spec-flow-active-controller.json"
    completion = engine.dispatch("complete", {"release": "v1.2.3", "run_id": run_id})
    audit = None
    if label != "negative":
        assert state["status"] == "completed" and state["active_task"] is None
        assert completion["technical_complete"] and not completion["release_review_pending"] and not completion["audit_pending"]
        assert not registry.exists() and not git(root, "status", "--porcelain")
        candidates = engine._phase_controller()._audit_candidates(run_id)
        assert len(candidates) == 1
        audit = candidates[0]
        assert audit["sha"] == git(root, "rev-parse", "HEAD")
        assert audit["subject"] == "docs(spec-flow): record release review"
        assert audit["parent"] == state["phases"]["PH-01"]["commit"]["sha"]
        recorded = state["release_review"]
        assert PhaseController._generated_record((root / ".specs/release-v1.2.3/spec.md").read_text(), root / ".specs/release-v1.2.3/spec.md") == recorded["record"]
        assert PhaseController._generated_record((root / ".specs/roadmap.md").read_text(), root / ".specs/roadmap.md") == recorded["roadmap_reference"]
        assert recorded["record"]["impact_status"] == "pending" and recorded["record"]["publication"] is False
        assert recorded["record"]["external_side_effects"] is False
        assert engine.dispatch("validate", {"release": "v1.2.3"})["valid"]
    else:
        assert state["tasks"]["T-001"]["attempt"] == 3
        assert len(attestations) == 3 and not state["phases"] and not state.get("release_review")
        assert not completion["technical_complete"]
        assert sum(event["event"] == "verification_failed" for event in events) == 3
    test_sha = hashlib.sha256((root / "test_release.py").read_bytes()).hexdigest()
    assert test_sha == "7bb24f05e31ffe3fdb53c96895e3462a5823fe7ac9ad4bdbe0e612d206cd0577"
    code_sha = hashlib.sha256((root / "release.py").read_bytes()).hexdigest()
    test = subprocess.run(["python3", "-B", "-m", "unittest", "-v", "test_release.py"], cwd=root,
                          env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}, text=True, capture_output=True)
    assert test.returncode == (1 if label == "negative" else 0)
    assert hashlib.sha256((root / "release.py").read_bytes()).hexdigest() == code_sha
    assert hashlib.sha256((root / "test_release.py").read_bytes()).hexdigest() == test_sha
    out["fixtures"][label] = {"root": str(root), "run_id": run_id, "status": state["status"],
        "active_task": state["active_task"], "attempt": state["tasks"]["T-001"]["attempt"],
        "task_status": state["tasks"]["T-001"]["status"], "head": git(root, "rev-parse", "HEAD"),
        "attempt_attestations": attestations, "phases": phases, "audit": audit, "completion": completion,
        "ownership_registry": str(registry), "lease_present": registry.exists(),
        "lease": json.loads(registry.read_text()) if registry.exists() else None,
        "event_count": len(events), "events_sha256": hashlib.sha256(journal.read_bytes()).hexdigest(),
        "worktree_status": git(root, "status", "--short"),
        "independent_test": {"argv": ["python3", "-B", "-m", "unittest", "-v", "test_release.py"],
            "exit_code": test.returncode, "stdout": test.stdout, "stderr": test.stderr,
            "test_sha256": test_sha, "code_sha256": code_sha, "code_unchanged": True}}

# Capability probe is separate from bound task credit. Resolve its actual host
# session by first-record lineage, never by assistant self-description.
probe_path = "/root/e7_owner_f8fa91d/e7_capability_probe_34d8909"
probe_id = None
home = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
for path in (home / "sessions").rglob("rollout-*.jsonl"):
    try:
        with path.open() as stream:
            row = json.loads(stream.readline())
    except (OSError, UnicodeError, json.JSONDecodeError):
        continue
    meta = row.get("payload") if isinstance(row, dict) else None
    source = meta.get("source") if isinstance(meta, dict) else None
    subagent = source.get("subagent") if isinstance(source, dict) else None
    lineage = subagent.get("thread_spawn") if isinstance(subagent, dict) else None
    if isinstance(lineage, dict) and lineage.get("parent_thread_id") == owner and lineage.get("agent_path") == probe_path:
        assert probe_id is None
        probe_id = meta["id"]
assert probe_id and probe_id not in sessions
probe = adapter.attest_session(probe_id, "implementer", parent_session=owner, agent_path=probe_path, require_finished=True)
out["capability_probe_attestation"] = probe
out["capability_probe_limit"] = "Tool capability exercise only; not a prepared/bound implementation task"
sessions.add(probe_id)
assert len(sessions) == 9, len(sessions)
out["distinct_attested_sessions"] = len(sessions)
out["positive_native_closures_verified"] = 2
out["negative_lease_released"] = not out["fixtures"]["negative"]["lease_present"]
out["result"] = "Evidence/identity checks passed; inspect negative state and evaluation report for overall E7 verdict"
(E / "native-independent-check.json").write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"sessions": len(sessions), "positive_closures": 2,
                  "negative_status": out["fixtures"]["negative"]["task_status"],
                  "negative_lease_present": out["fixtures"]["negative"]["lease_present"]}))
