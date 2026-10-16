import datetime
import json
import subprocess
import sys
from pathlib import Path

PACKAGE = Path('/private/tmp/spec-flow-e7-ef7897d-jn0glhbr/source/plugins/spec-flow')
BASE = Path('/private/tmp/spec-flow-e7-ef7897d-jn0glhbr')
EVIDENCE = Path('/Users/santiago_migoni/Documents/Projects/spec-flow/docs/implementation/evidence/e7-ef7897d/native')

label, variant, operation = sys.argv[1:4]
root = BASE / (label + '-' + variant)
payload = json.load(sys.stdin)
process = subprocess.run(
    ['python3', '-B', str(PACKAGE / 'scripts/spec-flow.py'), '--root', str(root), operation, '--input', '/dev/stdin'],
    input=json.dumps(payload), text=True, capture_output=True,
)
try:
    output = json.loads(process.stdout)
except json.JSONDecodeError:
    output = process.stdout
record = {
    'time': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'root': str(root), 'op': operation, 'input': payload,
    'exit': process.returncode, 'output': output, 'stderr': process.stderr,
}
folder = EVIDENCE / label
folder.mkdir(parents=True, exist_ok=True)
with (folder / 'operations.jsonl').open('a') as stream:
    stream.write(json.dumps(record, ensure_ascii=False) + '\n')
print(json.dumps({'exit': process.returncode, 'output': output, 'stderr': process.stderr}, ensure_ascii=False))
