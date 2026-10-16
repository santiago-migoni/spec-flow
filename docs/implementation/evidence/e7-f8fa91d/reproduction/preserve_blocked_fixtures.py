"""Preserve blocked E7 projects without changing runs, leases or host logs."""
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
summary = json.loads((E / "native/native-result-summary.json").read_text())
result = {"preserved_at": datetime.now(timezone.utc).isoformat(), "fixtures": {},
          "warning": "Historical blocked state with active ownership, not an approved closure or executable restored authorization"}
for label, fixture in summary["fixtures"].items():
    root = Path(fixture["worktree"])
    dest = E / "native" / label
    bundle = dest / "repository.bundle"
    subprocess.run(["git", "bundle", "create", str(bundle), "--all"], cwd=root, check=True, capture_output=True)
    verify = subprocess.run(["git", "bundle", "verify", str(bundle)], cwd=root, check=True, capture_output=True, text=True)
    sources = []
    for rel in (".specs", ".spec-flow", ".gitignore", "release.py", "test_release.py"):
        path = root / rel
        sources.extend([path] if path.is_file() else [p for p in path.rglob("*") if p.is_file()])
    files = {}
    for source in sorted(sources):
        assert not source.is_symlink()
        rel = source.relative_to(root)
        target = dest / "snapshot" / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        assert source.read_bytes() == target.read_bytes()
        files[rel.as_posix()] = {"bytes": target.stat().st_size, "sha256": hashlib.sha256(target.read_bytes()).hexdigest()}
    registry = Path(checks["fixtures"][label]["ownership_registry"])
    shutil.copy2(registry, dest / "ownership-registration.json")
    assert json.loads((dest / "ownership-registration.json").read_text()) == checks["fixtures"][label]["lease"]
    record = {"original_worktree": str(root), "head": checks["fixtures"][label]["head"],
              "bundle_sha256": hashlib.sha256(bundle.read_bytes()).hexdigest(), "bundle_verified": True,
              "bundle_verify_stdout": verify.stdout, "bundle_verify_stderr": verify.stderr,
              "snapshot_files": files, "snapshot_bytes": sum(f["bytes"] for f in files.values()),
              "ownership_registry_retained_active": True,
              "ownership_copy_is_historical_evidence_only": True,
              "restoration_limit": "Do not restore leases or execute using this historical state. Recovery requires a supported corrected controller and current native inspection/authorization; no files were manually cleared."}
    (dest / "preservation.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
    result["fixtures"][label] = {"snapshot_files": len(files), "snapshot_bytes": record["snapshot_bytes"],
                                  "bundle_sha256": record["bundle_sha256"], "bundle_verified": True,
                                  "lease_retained_active": True}
(E / "preservation-summary.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
print(json.dumps(result["fixtures"], ensure_ascii=False))
