import json,subprocess
from pathlib import Path
E=Path('/Users/santiago_migoni/Documents/Projects/spec-flow/docs/implementation/evidence/e7-34d8909/native')
OWNER='01a1451c-0ecd-7c93-9d51-8650fdaf887f'
report={'inventory_reference':'collaboration.list_agents after capability probe: /root/e7_owner_f8fa91d/e7_capability_probe_34d8909 interrupted and no implementer active','operations':{x:True for x in ['spawn_agent','wait_agent','interrupt_agent','list_agents']},'probe_evidence':{'spawn_agent':'native spawn_agent created isolated Luna/high capability probe e7_capability_probe_34d8909; its ready message received','wait_agent':'native wait_agent returned after probe ready message','interrupt_agent':'native interrupt_agent returned previous_status running and list_agents then showed interrupted','list_agents':'native list_agents showed probe running then interrupted; owner path /root/e7_owner_f8fa91d running'}}
def call(op,payload):
 p=subprocess.run(['python3','-B',str(E/'native_call.py'),'fresh','linked',op],input=json.dumps(payload),text=True,capture_output=True)
 if p.returncode:raise RuntimeError(p.stderr)
 r=json.loads(p.stdout)
 assert r['exit']==0,r
 print(op,json.dumps(r['output'],ensure_ascii=False)[:1800])
 return r['output']
call('capabilities',{'owner':OWNER,'report':report})
r=call('start',{'release':'v1.2.3','owner':OWNER,'phases':['PH-01'],'authorization':{'actor':'User','statement':'Me parece bien. Corrige F-02 conservando los controles actuales, recupera los runs bloqueados mediante el controlador y repite E7 sobre el nuevo commit, usando proyectos desechables y registrando las pruebas, los resultados y las evidencias. Synthetic E7 fixture execution of PH-01 only.','source':'evaluation-context.json human_authorization'},'capabilities':report})
(E/'fresh'/'run-id.txt').write_text(r['run_id'])
call('prepare',{'run_id':r['run_id'],'owner':OWNER,'task_id':'T-001'})
