"""Preserve original E7 fixtures after native agents and ownership have ended.

Git bundles retain commits; byte snapshots also retain pending controller events,
receipts, ignored packets/state, and the deliberately failing negative code.
This does not turn an abandoned fixture into a closed/reusable release.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("evidence", type=Path)
    args = parser.parse_args()
    evidence = args.evidence.resolve()
    summary = json.loads((evidence / "native/native-result-summary.json").read_text())
    checks = json.loads((evidence / "native-independent-check.json").read_text())
    records = {"created_at": datetime.now(timezone.utc).isoformat(), "fixtures": {}}
    for label, fixture in summary["fixture_runs"].items():
        assert checks["fixtures"][label]["lease_absent"]
        root = Path(fixture["linked_worktree"])
        dest = evidence / "native" / label
        bundle = dest / "repository.bundle"
        subprocess.run(["git", "bundle", "create", str(bundle), "--all"], cwd=root, check=True, capture_output=True)
        verified = subprocess.run(["git", "bundle", "verify", str(bundle)], cwd=root, check=True, capture_output=True, text=True)
        files = []
        for rel in (".specs", ".spec-flow", ".gitignore", "release.py", "test_release.py"):
            src = root / rel
            files.extend([src] if src.is_file() else [p for p in src.rglob("*") if p.is_file()])
        manifest = {}
        for src in sorted(files):
            assert not src.is_symlink()
            rel = src.relative_to(root)
            target = dest / "snapshot" / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, target)
            assert target.read_bytes() == src.read_bytes()
            manifest[rel.as_posix()] = {"sha256": hashlib.sha256(target.read_bytes()).hexdigest(), "bytes": target.stat().st_size}
        row = {"original_worktree": str(root), "head": checks["fixtures"][label]["head"],
               "snapshot_files": manifest, "snapshot_bytes": sum(v["bytes"] for v in manifest.values()),
               "bundle_sha256": hashlib.sha256(bundle.read_bytes()).hexdigest(),
               "bundle_verify_stdout": verified.stdout, "bundle_verify_stderr": verified.stderr,
               "retained_worktree_status": checks["fixtures"][label]["retained_worktree_status"],
               "restore_limit": "Inspect offline: absolute project paths, native sessions and expired authorization are historical; no active lease is copied."}
        (dest / "preservation.json").write_text(json.dumps(row, ensure_ascii=False, indent=2) + "\n")
        records["fixtures"][label] = {"snapshot_files": len(manifest), "snapshot_bytes": row["snapshot_bytes"],
                                      "bundle_sha256": row["bundle_sha256"], "bundle_verified": True}
    (evidence / "preservation-summary.json").write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(records["fixtures"], ensure_ascii=False))


if __name__ == "__main__":
    main()
