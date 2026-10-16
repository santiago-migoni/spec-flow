import json,subprocess,sys
from pathlib import Path
E=Path('/Users/santiago_migoni/Documents/Projects/spec-flow/docs/implementation/evidence/e7-f8fa91d/native')
name=sys.argv[1]
owner='01a1451c-0ecd-7c93-9d51-8650fdaf887f'
report={'inventory_reference':'collaboration.list_agents owner tree snapshot in E7 Sol turn 2026-10-16','operations':{x:True for x in ['spawn_agent','wait_agent','interrupt_agent','list_agents']},'probe_evidence':{'spawn_agent':'native collaboration.spawn_agent schema exposed; actual delegated spawn follows prepare','wait_agent':'native collaboration.wait_agent schema exposed; actual wait follows spawn','interrupt_agent':'native collaboration.interrupt_agent schema exposed; actual use is pending in fresh scenario','list_agents':'live collaboration.list_agents result showed /root/e7_owner_f8fa91d running'}}
def call(op,x):
 p=subprocess.run(['python3','-B',str(E/'run_control.py'),name,op],input=json.dumps(x),text=True,capture_output=True);print(op,p.stdout);assert p.returncode==0,p.stderr;return json.loads(p.stdout)['output']
call('capabilities',{'owner':owner,'report':report})
a=call('start',{'release':'v1.2.3','owner':owner,'phases':['PH-01'],'authorization':{'actor':'User','statement':'Me parece bien. Corrige F-01 conservando los controles actuales y repite E7 sobre el nuevo commit, usando proyectos desechables y registrando las pruebas, los resultados y las evidencias. Synthetic E7 fixture execution of PH-01 only.','source':'evaluation-context.json human_authorization'},'capabilities':report})
(E/name/'run-id.txt').write_text(a['run_id'])
call('prepare',{'run_id':a['run_id'],'owner':owner,'task_id':'T-001'})
