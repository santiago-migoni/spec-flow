import json
import subprocess
import sys
from pathlib import Path

E = Path('/Users/santiago_migoni/Documents/Projects/spec-flow/docs/implementation/evidence/e7-e9fe146/native')
BASE = Path('/private/tmp/spec-flow-e7-e9fe146-ob54eg0e')
label = sys.argv[1]
root = BASE / (label + '-linked')
if label == 'legacy': root = BASE / 'legacy-final-linked'
paths = [
    '.specs/constitution.md', '.specs/architecture.md', '.specs/structure.md',
    '.specs/roadmap.md', '.specs/release-v1.2.3/spec.md',
    '.specs/release-v1.2.3/plan.md', '.specs/release-v1.2.3/tasks.md',
]

def call(operation, payload, expected_exit=0):
    process = subprocess.run(
        ['python3', '-B', str(E / 'native_call.py'), label, 'linked', operation],
        input=json.dumps(payload), text=True, capture_output=True,
    )
    if process.returncode:
        raise RuntimeError(process.stderr)
    result = json.loads(process.stdout)
    if result['exit'] != expected_exit:
        raise RuntimeError((operation, result))
    print(operation, result['exit'], str(result['output'])[:180])
    return result['output']

for rel in ('roadmap.md', 'release-v1.2.3/spec.md'):
    path = root / '.specs' / rel
    text = path.read_text()
    assert '<!-- spec-flow:generated:start -->\nProgress is maintained by the Spec-Flow harness.\n<!-- spec-flow:generated:end -->' in text, rel
(E / label / 'generated-before-release-review.json').write_text(json.dumps({'initial_generated_blocks_exact': True, 'paths': ['.specs/roadmap.md', '.specs/release-v1.2.3/spec.md']}, indent=2) + '\n')

call('initialize', {})
for path in paths:
    call('validate', {'path': path})
call('validate', {'release': 'v1.2.3'})
before = call('gate', {'kind': 'implement', 'release': 'v1.2.3'})
assert before.get('ready') is False, before
statement = ('Synthetic E7-only approval of this exact disposable fixture decision for immutable e9fe146; '
             'no human reviewed generated fixture contents and no real-product authority is implied.')
for path in paths:
    call('approve', {'path': path, 'actor': 'E7 Evaluator', 'statement': statement,
                     'source': 'evaluation-context.json human_authorization and E7 synthetic fixture protocol'})
after = call('gate', {'kind': 'implement', 'release': 'v1.2.3'})
assert after.get('ready') is True, after
print('GATES', before.get('ready'), after.get('ready'))
