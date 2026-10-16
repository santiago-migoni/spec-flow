"""Complementary production queries and literal-template checks; not native implementation."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys

parser = argparse.ArgumentParser()
parser.add_argument("context", type=Path)
args = parser.parse_args()
c = json.loads(args.context.read_text())
pkg = Path(c["source_package_root"])
evidence = Path(c["evidence_directory"])
base = Path(c["disposable_base"]) / "consultation-fixtures-repeat"
sys.path.insert(0, str(pkg))
from harness.runtime.contracts import read_document
from harness.runtime.phases import PhaseController

def snapshot(root):
    return {p.relative_to(root).as_posix(): {"sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
                "mode": stat.S_IMODE(p.stat().st_mode), "mtime_ns": p.stat().st_mtime_ns}
            for p in sorted(root.rglob("*")) if p.is_file()}

def call(root, operation, payload):
    argv = [sys.executable, "-B", str(pkg / "scripts/spec-flow.py"), "--root", str(root), operation, "--input", "/dev/stdin"]
    p = subprocess.run(argv, input=json.dumps(payload), text=True, capture_output=True,
                       env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "GIT_OPTIONAL_LOCKS": "0"})
    return {"argv": argv, "input": payload, "exit_code": p.returncode,
            "stdout": json.loads(p.stdout), "stderr": p.stderr}

fixtures = {}
for label in ("new", "legacy", "adopted"):
    root = base / label
    root.mkdir(parents=True, exist_ok=False)
    fixtures[label] = root
legacy = fixtures["legacy"] / ".specs/001-probe/spec.md"
legacy.parent.mkdir(parents=True)
legacy.write_text("# Legacy probe\n\nStatus: Approved\n\n- [x] Historical task\n")
adopted = fixtures["adopted"]
path = adopted / ".specs/constitution.md"
path.parent.mkdir()
path.write_text('# Query fixture\n\n```spec-flow\n{"schema_version":1,"kind":"constitution","revision":"R00","id":"CONST-QUERY","depends_on":[]}\n```\n\nObserve queries only; no execution authority.\n')
setup = call(adopted, "initialize", {})
assert setup["exit_code"] == 0
queries, unsupported = [], []
for label, root in fixtures.items():
    before = snapshot(root)
    for op, payload in (("status", {}), ("gate", {"kind": "constitution"}),
                        ("validate", {"path": ".specs/constitution.md"}),
                        ("digest", {"path": ".specs/constitution.md"})):
        result = call(root, op, payload)
        assert snapshot(root) == before, (label, op)
        queries.append({"fixture": label, "no_file_or_metadata_changes": True, **result})
for kind in ("design", "backlog", "using-spec-flow"):
    before = snapshot(adopted)
    result = call(adopted, "gate", {"kind": kind})
    assert result["exit_code"] == 2
    assert snapshot(adopted) == before
    unsupported.append({"kind": kind, "no_file_or_metadata_changes": True, **result})
query_result = {"at": datetime.now(timezone.utc).isoformat(), "category": "real strict production CLI queries, no native implementation",
                "setup_before_snapshot": setup, "strict_query_operations": queries,
                "unsupported_gate_kinds": unsupported, "final_snapshots": {k: snapshot(v) for k, v in fixtures.items()},
                "complete_excluded": True, "no_mutation_observed": True}
(evidence / "consultation-tests.json").write_text(json.dumps(query_result, ensure_ascii=False, indent=2) + "\n")

literal = []
for rel in ("skills/specify/assets/spec-template.md", "skills/roadmap/assets/roadmap-template.md"):
    path = pkg / rel
    read_document(path)
    value = PhaseController._generated_record(path.read_text(), path)
    assert value is None, rel
    literal.append({"source": rel, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                    "document_reader_accepts": True, "closure_reader": None,
                    "meaning": "Valid initial progress; no persisted closure authority"})
(evidence / "F-01-literal-template-check.json").write_text(json.dumps({"at": datetime.now(timezone.utc).isoformat(),
    "category": "independent read-only literal-template check, not native closure", "observed": literal}, indent=2) + "\n")

hashes = {p.relative_to(pkg).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(pkg.rglob("*")) if p.is_file()}
generated = sorted(set(hashes) - set(c["package_files"]))
assert all("/__pycache__/" in "/" + rel and rel.endswith(".pyc") for rel in generated), generated
assert {k: hashes[k] for k in c["package_files"]} == c["package_files"]
hashes = {k: hashes[k] for k in c["package_files"]}
manifest = json.loads((pkg / "plugin.json").read_text())
assert manifest == json.loads((pkg / ".codex-plugin/plugin.json").read_text())
skills = sorted(p.parent.name for p in (pkg / "skills").glob("*/SKILL.md"))
templates = sorted(p.relative_to(pkg).as_posix() for p in (pkg / "skills").glob("*/assets/*template.md"))
assert len(skills) == len(templates) == 14
package_result = {"evaluated_commit": c["evaluated_commit"], "files_exact": len(hashes),
                  "source_export_matches": True, "manifest_mirror_matches": True, "version": manifest["version"],
                  "skills": skills, "templates": templates, "generated_bytecode_excluded": generated, "discovery_limit": "Source package inspection, not installed discovery or E8"}
(evidence / "package-checks.json").write_text(json.dumps(package_result, indent=2) + "\n")
print(json.dumps({"strict_queries": len(queries), "no_mutation": True, "unsupported_gates_rejected": len(unsupported),
                  "literal_templates_accept_initial_progress": len(literal), "source_files": len(hashes)}))
