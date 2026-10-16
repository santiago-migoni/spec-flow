import datetime,glob,hashlib,json,subprocess,sys
from pathlib import Path
OLD=Path('/private/tmp/spec-flow-e7-f8fa91d-1fyed3ur')
NEW=Path('/private/tmp/spec-flow-e7-34d8909-od5uaw4f/source/plugins/spec-flow')
E=Path('/Users/santiago_migoni/Documents/Projects/spec-flow/docs/implementation/evidence/e7-34d8909/recovery')
OWNER='01a1451c-0ecd-7c93-9d51-8650fdaf887f'
DOCS=['.specs/constitution.md','.specs/architecture.md','.specs/structure.md','.specs/roadmap.md','.specs/release-v1.2.3/spec.md','.specs/release-v1.2.3/plan.md','.specs/release-v1.2.3/tasks.md']
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(path):
 p=Path(path)
 return hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None
def git(root,*args):
 p=subprocess.run(['git',*args],cwd=root,text=True,capture_output=True)
 if p.returncode:raise RuntimeError(p.stderr)
 return p.stdout.strip()
def snap(root,run):
 state_path=root/'.spec-flow/runs'/run/'state.json'
 state=json.loads(state_path.read_text()) if state_path.is_file() else {}
 common=Path(git(root,'rev-parse','--git-common-dir'))
 if not common.is_absolute():common=(root/common).resolve()
 lease=common/'spec-flow-active-controller.json'
 return {'at':now(),'git_head':git(root,'rev-parse','HEAD'),'git_status':git(root,'status','--porcelain=v1').splitlines(),'code_sha256':sha(root/'release.py'),'test_sha256':sha(root/'test_release.py'),'decision_sha256':{d:sha(root/d) for d in DOCS},'approval_receipts_sha256':sha(root/'.spec-flow/approvals.jsonl'),'run_status':state.get('status'),'active_task':state.get('active_task'),'attempt':state.get('tasks',{}).get('T-001',{}).get('attempt'),'task_status':state.get('tasks',{}).get('T-001',{}).get('status'),'lease':json.loads(lease.read_text()) if lease.is_file() else None,'lease_path':str(lease)}
def call(name,root,run,op,payload):
 folder=E/name;folder.mkdir(parents=True,exist_ok=True)
 before=snap(root,run)
 p=subprocess.run(['python3','-B',str(NEW/'scripts/spec-flow.py'),'--root',str(root),op,'--input','/dev/stdin'],input=json.dumps(payload),text=True,capture_output=True)
 after=snap(root,run)
 try:out=json.loads(p.stdout)
 except json.JSONDecodeError:out=p.stdout
 row={'time':now(),'root':str(root),'op':op,'input':payload,'exit':p.returncode,'output':out,'stderr':p.stderr,'before':before,'after':after}
 with (folder/'operations.jsonl').open('a') as f:f.write(json.dumps(row,ensure_ascii=False)+'\n')
 print(name,op,p.returncode, out if p.returncode else 'ok')
 return row
if __name__=='__main__':
 children=[]
 for p in glob.glob('/Users/santiago_migoni/.codex/sessions/2026/10/16/*.jsonl'):
  try:
   with open(p) as f:m=json.loads(f.readline())['payload']
   source=m.get('source')
   sub=source.get('subagent') if isinstance(source,dict) else None
   lineage=sub.get('thread_spawn') if isinstance(sub,dict) else None
   if isinstance(lineage,dict) and lineage.get('parent_thread_id')==OWNER:children.append({'session_id':m.get('id'),'agent_path':lineage.get('agent_path')})
  except (OSError,UnicodeError,json.JSONDecodeError):pass
 if children:raise SystemExit('owner has native children: '+json.dumps(children))
 inventory={'owner_session':OWNER,'inventory_reference':'collaboration.list_agents current followup: owner running with zero descendants; previous 55eb811 children terminal. Local session_meta lineage scan zero owner descendants.','checked_at':datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),'agents':[]}
 E.mkdir(parents=True,exist_ok=True)
 (E/'native-inventory.json').write_text(json.dumps({'inventory':inventory,'local_child_sessions':children},indent=2)+'\n')
 summary={'candidate_commit':'34d89095ba75d6ae2707c3ed331ab4bda56573b6','cli':str(NEW/'scripts/spec-flow.py'),'owner':OWNER,'inventory':inventory,'fixtures':{}}
 for name,run in [('fresh','ea84dc87-11c2-46ef-b0d8-d2f0665fb824'),('legacy','8d1d0189-840d-4749-b4d8-f54718fe8c0c'),('negative','db79a022-629d-4243-8445-dc801d1b2be6')]:
  root=OLD/(name+'-linked')
  initial=snap(root,run)
  assert initial['run_status']=='active' and initial['active_task']=='T-001' and initial['attempt']==1 and initial['task_status']=='reconciliation_required',initial
  assert initial['test_sha256']=='7bb24f05e31ffe3fdb53c96895e3462a5823fe7ac9ad4bdbe0e612d206cd0577'
  assert initial['lease'] and initial['lease']['owner']==OWNER and initial['lease']['run_id']==run
  assert initial['code_sha256']==('08d838d6fd27b91eca3929c96833ba09596c3fd66de9bad027085c9eb746fdf0' if name=='legacy' else 'a804abcd14f65126a7ada66bb6a9bb4554595ddd31cdc485df545beb28e42aa9')
  call(name,root,run,'status',{})
  rec=call(name,root,run,'reconcile',{'run_id':run,'owner':OWNER,'task_id':'T-001','disposition':'no_spawn','evidence':'Native inventory and host parent lineage contain no owner child; first spawn was rejected at host thread limit; fixture release.py and fixed test bytes are unchanged since attempt preparation.','native_inspection':inventory})
  if rec['exit']!=0:summary['fixtures'][name]={'blocked_at':'reconcile','before':initial,'result':rec['output']};break
  if rec['after']['active_task'] is not None:summary['fixtures'][name]={'blocked_at':'active_task_not_cleared','after':rec['after']};break
  call(name,root,run,'status',{})
  ab=call(name,root,run,'abandon',{'run_id':run,'owner':OWNER,'reason':'Recover the f8fa91d E7 synthetic fixture after failed native spawn and F-02 no_spawn attestation crash. No implementation was delegated; preserve original attempt and history before evaluating corrected 34d8909 in new projects.','authorization':{'actor':'User','statement':'Me parece bien. Corrige F-02 conservando los controles actuales, recupera los runs bloqueados mediante el controlador y repite E7 sobre el nuevo commit, usando proyectos desechables y registrando las pruebas, los resultados y las evidencias.','source':'Parent task relay of explicit user authorization for F-02 and E7 recovery, 2026-10-16'}})
  if ab['exit']!=0:summary['fixtures'][name]={'blocked_at':'abandon','before':initial,'result':ab['output']};break
  call(name,root,run,'status',{})
  final=snap(root,run)
  assert final['run_status']=='abandoned' and final['active_task'] is None and final['attempt']==1 and final['lease'] is None
  assert final['code_sha256']==initial['code_sha256'] and final['test_sha256']==initial['test_sha256'] and final['decision_sha256']==initial['decision_sha256'] and final['approval_receipts_sha256']==initial['approval_receipts_sha256']
  summary['fixtures'][name]={'status':'recovered_abandoned','run_id':run,'before':initial,'after':final,'operations_log':str(E/name/'operations.jsonl')}
 (E/'result-summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n')
 print('summary',E/'result-summary.json')
