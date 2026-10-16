import json,pathlib,subprocess,sys
E=pathlib.Path('/Users/santiago_migoni/Documents/Projects/spec-flow/docs/implementation/evidence/e7-e9fe146/native');label=sys.argv[1];needle=sys.argv[2];run=(E/label/'run-id.txt').read_text().strip();b={'run_id':run,'owner':'01a14601-755e-7623-8d98-bbdcf02b03e6','task_id':'T-001'}
def call(op,p,ok=True):
 r=subprocess.run(['python3','-B',str(E/'native_call.py'),label,'linked',op],input=json.dumps(p),text=True,capture_output=True);v=json.loads(r.stdout);print(op,json.dumps(v)[:1600]);assert not ok or v['exit']==0;return v['output']
for p in pathlib.Path('/Users/santiago_migoni/.codex/sessions/2026/10/16').glob('*'):
 try:
  m=json.loads(p.open().readline())['payload'];a=m.get('source',{}).get('subagent',{}).get('thread_spawn',{})
  if needle in a.get('agent_path',''):break
 except:pass
call('bind-agent',{**b,'agent_id':a['agent_path'],'agent_path':a['agent_path'],'session_id':m['id']})
r={'summary':('Fault injection requested: '+needle) if label=='negative' else 'Implemented strict normalization; inspected actual code and fixed test integrity.','files_modified':['release.py'],'checks':[{'step_id':'T-001.001','check':'python3 -B -m unittest -v test_release.py','result':'Failed as expected' if label=='negative' else '4 tests pass'}],'evidence':[{'kind':'inspection','reference':'release.py','description':'Actual code and diff inspected; fixed test SHA256 unchanged 7bb24f05e31ffe3fdb53c96895e3462a5823fe7ac9ad4bdbe0e612d206cd0577.'}],'blockers':[]}
call('result',{**b,'result':r});v=call('verify',b,ok=label!='negative')
if label=='negative':
 assert v['error']['code']=='verification_failed';call('retry',{**b,'reason':'Fixed suite failed injected fault','hypothesis':'Next isolated fault tests enforce unchanged three-attempt budget.'});call('prepare',b)
else:
 call('review',{**b,'verdict':'pass','evidence':'Actual whole-string ASCII optional-v normalization, strict zero/error classes inspected; controller fixed four-method suite passes; test bytes unchanged and final ACs/NFR demonstrated.'});call('close',b);call('phase-ready',{'run_id':run,'owner':b['owner'],'phase_id':'PH-01'})
