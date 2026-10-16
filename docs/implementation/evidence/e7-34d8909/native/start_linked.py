import json,subprocess,sys
from pathlib import Path
E=Path('/Users/santiago_migoni/Documents/Projects/spec-flow/docs/implementation/evidence/e7-34d8909/native')
name=sys.argv[1];OWNER='01a1451c-0ecd-7c93-9d51-8650fdaf887f'
report={'inventory_reference':'collaboration.list_agents: capability probe interrupted; fresh Luna aborted; fresh Sol reviewer completed; no active child at new fixture start','operations':{x:True for x in ['spawn_agent','wait_agent','interrupt_agent','list_agents']},'probe_evidence':{'spawn_agent':'native spawn_agent created Luna/high capability probe and fresh implementation and distinct Sol/high reviewer','wait_agent':'native wait_agent returned probe ready message and reviewer completion','interrupt_agent':'native interrupt_agent stopped running probe and running fresh Luna after its code write','list_agents':'native list_agents confirmed active/terminal child states in this owner session'}}
def call(op,payload):
 p=subprocess.run(['python3','-B',str(E/'native_call.py'),name,'linked',op],input=json.dumps(payload),text=True,capture_output=True)
 if p.returncode:raise RuntimeError(p.stderr)
 r=json.loads(p.stdout);print(op,json.dumps(r['output'],ensure_ascii=False)[:1300]);assert r['exit']==0,r
 return r['output']
call('capabilities',{'owner':OWNER,'report':report})
r=call('start',{'release':'v1.2.3','owner':OWNER,'phases':['PH-01'],'authorization':{'actor':'User','statement':'Me parece bien. Corrige F-02 conservando los controles actuales, recupera los runs bloqueados mediante el controlador y repite E7 sobre el nuevo commit, usando proyectos desechables y registrando las pruebas, los resultados y las evidencias. Synthetic E7 fixture execution of PH-01 only.','source':'evaluation-context.json human_authorization'},'capabilities':report})
(E/name/'run-id.txt').write_text(r['run_id'])
call('prepare',{'run_id':r['run_id'],'owner':OWNER,'task_id':'T-001'})
