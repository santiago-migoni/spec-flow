"""Query staleness in new clones of closed native history, never the original run."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

parser = argparse.ArgumentParser()
parser.add_argument("context", type=Path)
parser.add_argument("source", type=Path)
parser.add_argument("run_id")
args = parser.parse_args()
c = json.loads(args.context.read_text())
E = Path(c["evidence_directory"])
B = Path(c["disposable_base"])
P = Path(c["source_package_root"])
source = args.source.resolve()
head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=source, text=True).strip()

def query(root):
    argv = [sys.executable, "-B", str(P / "scripts/spec-flow.py"), "--root", str(root), "complete", "--input", "/dev/stdin"]
    payload = {"release": "v1.2.3", "run_id": args.run_id}
    p = subprocess.run(argv, input=json.dumps(payload), capture_output=True, text=True,
                       env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    assert p.returncode == 0, p.stderr + p.stdout
    return {"argv": argv, "input": payload, "exit_code": p.returncode,
            "stdout": json.loads(p.stdout), "stderr": p.stderr}

results = []
for label, rel in (("reviewed-code-change", "release.py"),
                   ("approved-source-change", ".specs/release-v1.2.3/spec.md")):
    root = B / label
    assert not root.exists()
    subprocess.run(["git", "clone", "--no-hardlinks", str(source), str(root)], check=True, capture_output=True)
    shutil.copytree(source / ".spec-flow", root / ".spec-flow", dirs_exist_ok=True)
    baseline = query(root)
    value = baseline["stdout"]
    assert value["technical_complete"] and not value["release_review_pending"] and not value["audit_pending"], value
    path = root / rel
    before = path.read_bytes()
    if rel == "release.py":
        path.write_bytes(before + b"\n# E7 deliberately changed after reviewed audit\n")
    else:
        path.write_text(path.read_text() + "\nUnapproved decision injected after native closure.\n")
    changed = path.read_bytes()
    rejected = query(root)
    assert not rejected["stdout"]["technical_complete"], rejected
    assert path.read_bytes() == changed
    dest = E / "reproduction/staleness-inputs" / label / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, dest)
    results.append({"case": label, "root": str(root), "source_native_audit_head": head,
                    "run_id": args.run_id, "baseline": baseline, "injected_path": rel,
                    "before_sha256": hashlib.sha256(before).hexdigest(),
                    "after_sha256": hashlib.sha256(changed).hexdigest(), "rejection": rejected})
(E / "completion-staleness-negative-probes.json").write_text(json.dumps({
    "at": datetime.now(timezone.utc).isoformat(),
    "category": "Production complete queries on independent clones of closed native history; not fresh native implementations or approval authority",
    "source_original_unchanged": True, "probes": results}, ensure_ascii=False, indent=2) + "\n")
assert subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=source, text=True).strip() == head
print(json.dumps({"clones": len(results), "post_review_changes_rejected": True, "source_audit": head}))
