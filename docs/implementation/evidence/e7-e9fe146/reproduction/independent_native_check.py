"""Independent production attestation, event, test and ownership verification.
No registry edits or imported task credit. Fixed behavioral reruns confer no execution credit.
"""
import json,os,sys,hashlib,subprocess
from pathlib import Path
from datetime import datetime,timezone
c=json.loads(Path(sys.argv[1]).read_text());P=Path(c['source_package_root']);E=Path(c['evidence_directory']);sys.path.insert(0,str(P))
from harness.runtime.engine import Engine
from harness.runtime.codex_adapter import NativeCodexAdapter
from harness.runtime.phases import PhaseController
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def git(root,*args):return subprocess.check_output(['git','--no-optional-locks',*args],cwd=root,text=True).strip()
sessions=json.loads((E/'native/session-context.json').read_text());owner=next(s for s in sessions if s['agent_path']=='/root/e7_native_owner')
adapter=NativeCodexAdapter(Path(c['disposable_base']));adapter.configure_profiles(c['profiles'],require_catalog=True)
owner_att=adapter.attest_session(owner['session_id'],'orchestrator',parent_session=owner['parent_session'],agent_path=owner['agent_path'],require_finished=True)
out={'checked_at':datetime.now(timezone.utc).isoformat(),'candidate':c['evaluated_commit'],'category':'Independent real native attestations, canonical state/events, fixed test reruns and Git/lease checks','owner':owner_att,'fixtures':{}}
seen={owner['session_id']}
for label in ('fresh','legacy','negative'):
 root=Path(c[label+'_worktree']);ops=[json.loads(x) for x in (E/'native'/label/'operations.jsonl').read_text().splitlines()];started=next(r for r in ops if r['op']=='start' and r['exit']==0);run=started['output'].get('run_id') or started['output']['state']['run_id'];engine=Engine(root);state=engine.dispatch('status',{'run_id':run});journal=root/'.spec-flow/runs'/run/'events.jsonl';events=[json.loads(x) for x in journal.read_text().splitlines()];assert [e['seq'] for e in events]==list(range(1,len(events)+1));assert state['profiles']==c['profiles'];attempts={};atts=[]
 for event in events:
  data=event['data']
  if event['event']=='prepared':
   attempts[(data['task_id'],data['attempt'])]=data
   packet=json.loads((root/data['packet_path']).read_text());assert packet['profiles']==c['profiles'];unhashed={k:v for k,v in packet.items() if k!='packet_sha256'};digest=hashlib.sha256(json.dumps(unhashed,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest();assert digest==packet['packet_sha256']==data['packet_sha256']
  if event['event']=='agent_bound':
   prepared=attempts[(data['task_id'],data['attempt'])];actual=adapter.attest_session(data['session_id'],'implementer',parent_session=owner['session_id'],agent_path=data['agent_path'],require_finished=True,task_marker='SPEC_FLOW_PACKET_SHA256='+prepared['packet_sha256'],after=prepared['prepared_at']);assert data['session_id'] not in seen;seen.add(data['session_id']);atts.append({'attempt':data['attempt'],'attestation':actual})
 phases={}
 for phase_id,phase in state['phases'].items():
  packet=json.loads((root/phase['packet_path']).read_text());assert packet['profiles']==c['profiles'];unhashed={k:v for k,v in packet.items() if k!='packet_sha256'};assert hashlib.sha256(json.dumps(unhashed,sort_keys=True,separators=(',',':')).encode()).hexdigest()==packet['packet_sha256']==phase['packet_sha256']
  review=phase['review'];actual=adapter.attest_session(review['reviewer_session'],'reviewer',parent_session=owner['session_id'],agent_path=review['reviewer_agent_id'],require_finished=True,task_marker=phase['marker'],after=phase['ready_at']);assert review['reviewer_session'] not in seen;seen.add(review['reviewer_session']);commit=phase['commit'];assert git(root,'rev-parse',commit['sha']+'^{tree}')==commit['tree']==phase['tree'];assert git(root,'rev-parse',commit['sha']+'^')==commit['parent']==phase['parent'];phases[phase_id]={'commit':commit,'reviewer_attestation':actual,'exact_tree_and_parent':True}
 common=Path(git(root,'rev-parse','--git-common-dir'));common=common if common.is_absolute() else (root/common).resolve();lease=common/'spec-flow-active-controller.json';assert not lease.exists();assert state['active_task'] is None;complete=engine.dispatch('complete',{'release':'v1.2.3','run_id':run})
 if label!='negative':
  assert state['status']=='completed';assert complete['technical_complete'] and not complete['release_review_pending'] and not complete['audit_pending'];assert not git(root,'status','--porcelain');assert len(atts)==len(phases)==1;rr=state['release_review'];assert rr['record']['impact_status']=='pending' and rr['record']['publication'] is False and rr['record']['external_side_effects'] is False
  for rel,record in [('.specs/release-v1.2.3/spec.md',rr['record']),('.specs/roadmap.md',rr['roadmap_reference'])]:
   path=root/rel;assert PhaseController._generated_record(path.read_text(),path)==record
  assert sum(e['event']=='closed' for e in events)==1
 else:
  assert state['status']=='abandoned' and state['tasks']['T-001']['attempt']==3;assert len(atts)==3 and not phases and not state.get('release_review');assert not complete['technical_complete'];assert sum(e['event']=='verification_failed' for e in events)==3;assert sum(e['event']=='abandoned' for e in events)==1
 testsha=sha(root/'test_release.py');codesha=sha(root/'release.py');assert testsha=='7bb24f05e31ffe3fdb53c96895e3462a5823fe7ac9ad4bdbe0e612d206cd0577';cmd=['python3','-B','-m','unittest','-v','test_release.py'];p=subprocess.run(cmd,cwd=root,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},capture_output=True,text=True);assert p.returncode==(1 if label=='negative' else 0);assert sha(root/'test_release.py')==testsha and sha(root/'release.py')==codesha
 out['fixtures'][label]={'root':str(root),'run_id':run,'status':state['status'],'task_status':state['tasks']['T-001']['status'],'attempt':state['tasks']['T-001']['attempt'],'profiles':state['profiles'],'head':git(root,'rev-parse','HEAD'),'worktree_status':git(root,'status','--short'),'attestations':atts,'phases':phases,'completion':complete,'ownership_registry':str(lease),'lease_present':False,'event_count':len(events),'events_sha256':sha(journal),'test_sha256':testsha,'code_sha256':codesha,'independent_test':{'argv':cmd,'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'source_unchanged':True}}
recovery=json.loads((E/'native/fixture-recovery.json').read_text());root=Path(recovery['old']);engine=Engine(root);state=engine.dispatch('status',{'run_id':recovery['initial_run']});assert state['status']=='abandoned' and state['active_task'] is None
common=Path(git(root,'rev-parse','--git-common-dir'));common=common if common.is_absolute() else (root/common).resolve();lease=common/'spec-flow-active-controller.json';assert not lease.exists()
ops=[json.loads(x) for x in (E/'native/legacy-initial/operations.jsonl').read_text().splitlines()];assert any(r['op']=='phase-ready' and r['exit']==2 and r['output']['error']['code']=='phase_scope_changed' for r in ops)
journal=root/'.spec-flow/runs'/recovery['initial_run']/'events.jsonl';events=[json.loads(x) for x in journal.read_text().splitlines()];prepared=next(e['data'] for e in events if e['event']=='prepared');bound=next(e['data'] for e in events if e['event']=='agent_bound');att=adapter.attest_session(bound['session_id'],'implementer',parent_session=owner['session_id'],agent_path=bound['agent_path'],require_finished=True,task_marker='SPEC_FLOW_PACKET_SHA256='+prepared['packet_sha256'],after=prepared['prepared_at']);assert bound['session_id'] not in seen;seen.add(bound['session_id'])
out['initial_fixture_recovery']={'root':str(root),'run_id':recovery['initial_run'],'status':state['status'],'lease_present':False,'ownership_registry':str(lease),'head':git(root,'rev-parse','HEAD'),'event_count':len(events),'events_sha256':sha(journal),'attestation':att,'task_status':state['tasks']['T-001']['status'],'expected_scope_guard_observed':True,'replacement_root':recovery['new']}
out['capability_probe_attestations']=[adapter.attest_session(v['session_id'],'implementer',parent_session=owner['session_id'],agent_path=v['agent_path'],require_finished=True) for v in sessions if v['session_id'] not in seen and 'e7_capability_' in v['agent_path']]
out['distinct_task_and_review_sessions']=len(seen)-1;out['result']='PASS';(E/'native-independent-check.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'result':'PASS','fixtures':{k:{'status':v['status'],'attempt':v['attempt'],'lease_present':v['lease_present']} for k,v in out['fixtures'].items()},'sessions':len(seen)}))
