"""Independently inspect blocked original E7 fixtures and reproduce F-02 read-only."""
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
summary = json.loads((E / "native/native-result-summary.json").read_text())
sys.path.insert(0, c["source_package_root"])
from harness.runtime.codex_adapter import NativeCodexAdapter
from harness.runtime.engine import Engine

def files(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for folder in (".specs", ".spec-flow") for p in (root / folder).rglob("*") if p.is_file()}

def git(root, *argv):
    return subprocess.check_output(["git", "--no-optional-locks", *argv], cwd=root, text=True).strip()

owner = summary["owner_session"]
adapter = NativeCodexAdapter(Path(c["disposable_base"]))
attestation = adapter.attest_session(owner, "orchestrator", parent_session=c["parent_session"],
                                   agent_path="/root/e7_owner_f8fa91d", require_finished=True)
session_base = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))) / "sessions"
foreign_shapes, own_children = [], []
for path in session_base.rglob("rollout-*.jsonl"):
    try:
        with path.open() as stream:
            first = json.loads(stream.readline())
    except (OSError, UnicodeError, json.JSONDecodeError):
        continue
    if not isinstance(first, dict) or first.get("type") != "session_meta":
        continue
    meta = first.get("payload")
    source = meta.get("source") if isinstance(meta, dict) else None
    subagent = source.get("subagent") if isinstance(source, dict) else None
    if isinstance(subagent, str):
        foreign_shapes.append({"session_id": meta.get("id"), "subagent_type": "str",
                               "metadata_record_utf8_canonical_sha256": adapter._record_hash(first),
                               "metadata_record_ascii_escaped_sha256": hashlib.sha256(json.dumps(
                                   first, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest()})
    lineage = subagent.get("thread_spawn") if isinstance(subagent, dict) else None
    if isinstance(lineage, dict) and lineage.get("parent_thread_id") == owner:
        own_children.append({"session_id": meta.get("id"), "agent_path": lineage.get("agent_path")})
assert not own_children
assert any(x["metadata_record_ascii_escaped_sha256"] == summary["blocker"]["host_session_metadata_sha256"] for x in foreign_shapes)
inventory = json.loads((E / "native/no-spawn-inventory-followup.json").read_text())
out = {"checked_at": datetime.now(timezone.utc).isoformat(), "evaluated_commit": c["evaluated_commit"],
       "category": "Read-only inspection and production adapter reproduction on actual host; no forged metadata or registry changes",
       "owner_attestation": attestation, "owner_children_found": own_children,
       "foreign_metadata_shapes": foreign_shapes, "fixtures": {}}
for label, f in summary["fixtures"].items():
    root = Path(f["worktree"])
    before = files(root)
    state = Engine(root).dispatch("status", {"run_id": f["run_id"]})
    task = state["tasks"]["T-001"]
    assert state["status"] == "active" and state["active_task"] == "T-001"
    assert task["status"] == "reconciliation_required" and task["attempt"] == 1
    assert not task.get("agent") and not task.get("result") and not state.get("phases") and not state.get("release_review")
    assert hashlib.sha256((root / "release.py").read_bytes()).hexdigest() == f["release_sha256"]
    assert hashlib.sha256((root / "test_release.py").read_bytes()).hexdigest() == f["test_sha256"]
    common = Path(git(root, "rev-parse", "--git-common-dir"))
    if not common.is_absolute():
        common = (root / common).resolve()
    registry = common / "spec-flow-active-controller.json"
    registry_bytes = registry.read_bytes()
    lease = json.loads(registry_bytes)
    assert lease == f["lease"]
    try:
        NativeCodexAdapter(root).attest_no_spawn(owner, task, inventory)
    except AttributeError as error:
        assert "'str' object has no attribute 'get'" in str(error)
        failure = {"exception": type(error).__name__, "message": str(error)}
    else:
        raise AssertionError("F-02 did not reproduce")
    assert files(root) == before and registry.read_bytes() == registry_bytes
    operations = [json.loads(line) for line in (E / "native" / label / "operations.jsonl").read_text().splitlines()]
    reconcile = [row for row in operations if row["op"] == "reconcile"][-1]
    assert reconcile["exit"] == 1 and "AttributeError" in reconcile["stderr"]
    out["fixtures"][label] = {"worktree": str(root), "run_id": f["run_id"], "head": git(root, "rev-parse", "HEAD"),
        "status": state["status"], "active_task": state["active_task"], "task_status": task["status"],
        "attempt": task["attempt"], "native_child_bound": False, "phase_commit": None, "release_review": None,
        "code_and_tests_equal_baseline": True, "ownership_registry": str(registry), "lease_present": True,
        "lease": lease, "read_only_reproduction": failure, "operation_count": len(operations),
        "files_and_registry_unchanged": True, "worktree_status": git(root, "status", "--short")}
out["result"] = "F-02 reproduced independently in all three fixtures; no native child implementation or closure credited"
(E / "native-independent-check.json").write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
print(json.dumps({"result": out["result"], "fixtures": len(out["fixtures"]),
                  "owner_profile": attestation["model"] + "/" + attestation["effort"]}))
