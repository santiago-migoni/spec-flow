"""Reproduce F-01 read-only on the literal templates of an exported candidate."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

parser = argparse.ArgumentParser()
parser.add_argument("package", type=Path)
args = parser.parse_args()
package = args.package.resolve()
sys.path.insert(0, str(package))
from harness.runtime.contracts import read_document
from harness.runtime.engine import EngineError
from harness.runtime.phases import PhaseController

results = []
for rel in ("skills/specify/assets/spec-template.md", "skills/roadmap/assets/roadmap-template.md"):
    path = package / rel
    text = path.read_text()
    read_document(path)  # The ordinary document reader accepts the generated tail.
    try:
        PhaseController._generated_record(text, path)
    except EngineError as error:
        assert error.code == "release_review_record_stale"
        results.append({"template": rel, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                        "document_reader_accepts": True, "closure_reader_error": error.code})
    else:
        raise AssertionError("Expected pinned candidate F-01 was not reproduced: " + rel)
print(json.dumps(results, ensure_ascii=False, indent=2))
