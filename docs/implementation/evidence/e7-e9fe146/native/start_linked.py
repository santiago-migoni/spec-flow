import json
import subprocess
import sys
from pathlib import Path

E = Path('/Users/santiago_migoni/Documents/Projects/spec-flow/docs/implementation/evidence/e7-e9fe146/native')
OWNER = '01a14601-755e-7623-8d98-bbdcf02b03e6'
label = sys.argv[1]
report = {
    'inventory_reference': 'collaboration.list_agents: e9fe146 capability probe completed; interrupt probe observed running then interrupted; no active fixture child at start',
    'operations': {key: True for key in ['spawn_agent', 'wait_agent', 'interrupt_agent', 'list_agents']},
    'probe_evidence': {
        'spawn_agent': 'native spawn_agent created isolated Luna/high e7_capability_probe_e9fe146 and e7_capability_interrupt_e9fe146, unrelated to implementation',
        'wait_agent': 'native wait_agent returned after capability probe ready and terminal message',
        'interrupt_agent': 'native interrupt_agent returned previous_status running for e7_capability_interrupt_e9fe146; later list_agents showed interrupted',
        'list_agents': 'native list_agents showed capability probe running, then interrupted, while no implementation child was active',
    },
}

report['model_catalog_reference'] = str(E.parent / 'host-model-inventory.json')
report['model_catalog'] = json.loads((E.parent / 'host-model-inventory.json').read_text())['models']

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
        'statement': 'Perfecto. Ejecuta E7 sobre el commit e9fe146, usando proyectos desechables y los perfiles configurados, conservando los controles y registrando pruebas, resultados y evidencias. Sin publicar ni actualizar mi instalación. Synthetic E7 execution of PH-01 only.',
        'source': 'evaluation-context.json human_authorization',
    },
    'capabilities': report,
})
(E / label / 'run-id.txt').write_text(run['run_id'] + '\n')
call('prepare', {'run_id': run['run_id'], 'owner': OWNER, 'task_id': 'T-001'})
