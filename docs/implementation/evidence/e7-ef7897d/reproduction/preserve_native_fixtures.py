"""Preserve closed and blocked native E7 fixtures without changing their state."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument("context", type=Path)
args = parser.parse_args()
c = json.loads(args.context.read_text())
E = Path(c["evidence_directory"])
checks = json.loads((E / "native-independent-check.json").read_text())
summary = {"preserved_at": datetime.now(timezone.utc).isoformat(), "fixtures": {}}
for label, check in checks["fixtures"].items():
    root = Path(check["root"])
    dest = E / "native" / label
    bundle = dest / "repository.bundle"
    subprocess.run(["git", "bundle", "create", str(bundle), "--all"], cwd=root, check=True, capture_output=True)
    verified = subprocess.run(["git", "bundle", "verify", str(bundle)], cwd=root, check=True, capture_output=True, text=True)
    sources = []
    for rel in (".specs", ".spec-flow", ".gitignore", "release.py", "test_release.py"):
        source = root / rel
        sources.extend([source] if source.is_file() else [p for p in source.rglob("*") if p.is_file()])
    manifest = {}
    for source in sorted(sources):
        assert not source.is_symlink()
        rel = source.relative_to(root)
        target = dest / "snapshot" / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        assert target.read_bytes() == source.read_bytes()
        manifest[rel.as_posix()] = {"sha256": hashlib.sha256(target.read_bytes()).hexdigest(), "bytes": target.stat().st_size}
    registry = Path(check["ownership_registry"])
    assert registry.exists() == check["lease_present"]
    if registry.exists():
        shutil.copy2(registry, dest / "ownership-registration.json")
        assert json.loads((dest / "ownership-registration.json").read_text()) == check["lease"]
    record = {"original_worktree": str(root), "head": check["head"], "run_id": check["run_id"],
              "status": check["status"], "task_status": check["task_status"], "lease_present": check["lease_present"],
              "snapshot_files": manifest, "snapshot_bytes": sum(v["bytes"] for v in manifest.values()),
              "bundle_sha256": hashlib.sha256(bundle.read_bytes()).hexdigest(), "bundle_verified": True,
              "bundle_verify_stdout": verified.stdout, "bundle_verify_stderr": verified.stderr,
              "restoration_limit": "Historical inspection only. Bundles/snapshots do not restore live worktree/session/approval authority. Do not restore or manually clear ownership registrations."}
    (dest / "preservation.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
    summary["fixtures"][label] = {"files": len(manifest), "bytes": record["snapshot_bytes"],
                                  "bundle_verified": True, "lease_present": check["lease_present"]}
(E / "preservation-summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
print(json.dumps(summary["fixtures"], ensure_ascii=False))
