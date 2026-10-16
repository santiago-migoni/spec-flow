import json
import subprocess
import sys
from pathlib import Path

E = Path('/Users/santiago_migoni/Documents/Projects/spec-flow/docs/implementation/evidence/e7-ef7897d/native')
OWNER = '01a1451c-0ecd-7c93-9d51-8650fdaf887f'
label = sys.argv[1]
report = {
    'inventory_reference': 'collaboration.list_agents: ef7897d capability probe completed; interrupt probe observed running then interrupted; no active fixture child at start',
    'operations': {key: True for key in ['spawn_agent', 'wait_agent', 'interrupt_agent', 'list_agents']},
    'probe_evidence': {
        'spawn_agent': 'native spawn_agent created isolated Luna/high e7_capability_probe_ef7897d and e7_capability_interrupt_ef7897d, unrelated to implementation',
        'wait_agent': 'native wait_agent returned after capability probe ready and terminal message',
        'interrupt_agent': 'native interrupt_agent returned previous_status running for e7_capability_interrupt_ef7897d; later list_agents showed interrupted',
        'list_agents': 'native list_agents showed capability probe running, then interrupted, while no implementation child was active',
    },
}

def call(operation, payload):
    process = subprocess.run(['python3', '-B', str(E / 'native_call.py'), label, 'linked', operation],
                             input=json.dumps(payload), text=True, capture_output=True)
    if process.returncode:
        raise RuntimeError(process.stderr)
    result = json.loads(process.stdout)
    if result['exit']:
        raise RuntimeError((operation, result))
    print(operation, json.dumps(result['output'])[:1500])
    return result['output']

call('capabilities', {'owner': OWNER, 'report': report})
run = call('start', {
    'release': 'v1.2.3', 'owner': OWNER, 'phases': ['PH-01'],
    'authorization': {
        'actor': 'User',
        'statement': 'Me parece bien. Corrige F-03 conservando los controles actuales, recupera el run bloqueado mediante el controlador y repite E7 sobre el nuevo commit, usando proyectos desechables y registrando las pruebas, los resultados y las evidencias. Synthetic E7 execution of PH-01 only.',
        'source': 'evaluation-context.json human_authorization',
    },
    'capabilities': report,
})
(E / label / 'run-id.txt').write_text(run['run_id'] + '\n')
call('prepare', {'run_id': run['run_id'], 'owner': OWNER, 'task_id': 'T-001'})
