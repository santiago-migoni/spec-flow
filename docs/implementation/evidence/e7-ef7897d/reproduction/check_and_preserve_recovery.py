import json,hashlib,shutil,subprocess,sys
from pathlib import Path
from datetime import datetime,timezone
c=json.loads(Path(sys.argv[1]).read_text());E=Path(c['evidence_directory']);D=E/'recovery';before=json.loads((D/'before-independent.json').read_text());root=Path(before['root']);run=before['run_id'];sys.path.insert(0,c['source_package_root'])
from harness.runtime.engine import Engine
from harness.runtime.codex_adapter import NativeCodexAdapter
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
state=Engine(root).dispatch('status',{'run_id':run});events_path=root/'.spec-flow/runs'/run/'events.jsonl';raw=events_path.read_bytes();events=[json.loads(s) for s in raw.splitlines()]
assert state['status']=='abandoned' and state['active_task'] is None
assert state['tasks']['T-001']['status']=='verification_failed' and state['tasks']['T-001']['attempt']==3
assert not Path(before['registry']).exists()
for rel,digest in before['file_hashes'].items():
    if rel.endswith('/state.json') or rel.endswith('/events.jsonl'):continue
    assert sha(root/rel)==digest,rel
assert hashlib.sha256(raw[:before['events_bytes']]).hexdigest()==before['file_hashes'][str(events_path.relative_to(root))]
assert len(events)==18 and events[-1]['event']=='abandoned'
assert [e['seq'] for e in events]==list(range(1,19))
prior_snapshot=E.parent/'e7-34d8909/native/negative/snapshot/.spec-flow/runs'/run/'state.json';prior=json.loads(prior_snapshot.read_text());assert state['tasks']==prior['tasks']
unresolved=events[-1]['data']['unresolved_task'];native=unresolved['host_attestation'];assert unresolved['attempt']==3 and unresolved['status']=='verification_failed'
actual=NativeCodexAdapter(root).attest_session(native['session_id'],'implementer',parent_session=c['recovery_owner'],agent_path=state['tasks']['T-001']['agent']['agent_path'],task_marker='SPEC_FLOW_PACKET_SHA256='+state['tasks']['T-001']['packet_sha256'],after=state['tasks']['T-001']['prepared_at'],require_finished=True)
ops=[json.loads(line) for line in (D/'operations.jsonl').read_text().splitlines()];assert all(row['exit']==0 for row in ops)
record={'checked_at':datetime.now(timezone.utc).isoformat(),'candidate':c['evaluated_commit'],'run_id':run,'status':state['status'],'active_task':None,'attempt':3,'task_status':'verification_failed','original_17_events_byte_prefix_preserved':True,'all_task_state_unchanged':True,'code_tests_decisions_receipts_and_packets_unchanged':True,'lease_absent':True,'terminal_child_independent_attestation':actual,'operations':[row['op'] for row in ops],'result':'PASS'}
(D/'independent-check.json').write_text(json.dumps(record,indent=2)+'\n')
files=[]
for rel in ('.specs','.spec-flow','.gitignore','release.py','test_release.py'):
    p=root/rel;files.extend([p] if p.is_file() else [x for x in p.rglob('*') if x.is_file()])
manifest={}
for p in sorted(files):
    rel=p.relative_to(root);target=D/'snapshot'/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target);assert target.read_bytes()==p.read_bytes();manifest[rel.as_posix()]={'sha256':sha(p),'bytes':p.stat().st_size}
bundle=D/'repository.bundle';subprocess.run(['git','bundle','create',str(bundle),'--all'],cwd=root,check=True,capture_output=True);p=subprocess.run(['git','bundle','verify',str(bundle)],cwd=root,check=True,capture_output=True,text=True)
(D/'preservation.json').write_text(json.dumps({'original_worktree':str(root),'run_id':run,'snapshot_files':manifest,'bundle_sha256':sha(bundle),'bundle_verified':True,'verify_stdout':p.stdout,'verify_stderr':p.stderr,'restoration_limit':'Historical inspection only; does not restore host identity, approvals or execution authority.'},indent=2)+'\n')
print(json.dumps({'recovered_run':run,'status':'abandoned','task_status':'verification_failed','attempt':3,'lease_released':True,'snapshot_files':len(files),'bundle_verified':True}))
