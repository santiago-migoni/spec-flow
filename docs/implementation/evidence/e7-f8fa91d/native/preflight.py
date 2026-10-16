import datetime,hashlib,json,subprocess,sys
from pathlib import Path
B=Path('/private/tmp/spec-flow-e7-f8fa91d-1fyed3ur')
E=Path('/Users/santiago_migoni/Documents/Projects/spec-flow/docs/implementation/evidence/e7-f8fa91d/native')
CALL=E/'e7_call.py'
DOCS=['.specs/constitution.md','.specs/architecture.md','.specs/structure.md','.specs/roadmap.md','.specs/release-v1.2.3/spec.md','.specs/release-v1.2.3/plan.md','.specs/release-v1.2.3/tasks.md']
for name in sys.argv[1:]:
 root=B/(name+'-linked');folder=E/name;folder.mkdir(parents=True,exist_ok=True)
 p=subprocess.run(['python3','-B','-m','unittest','-v','test_release.py'],cwd=root,text=True,capture_output=True)
 (folder/'baseline.json').write_text(json.dumps({'time':datetime.datetime.now(datetime.timezone.utc).isoformat(),'command':['python3','-B','-m','unittest','-v','test_release.py'],'exit':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'test_sha256':hashlib.sha256((root/'test_release.py').read_bytes()).hexdigest(),'code_sha256':hashlib.sha256((root/'release.py').read_bytes()).hexdigest()},indent=2))
 assert p.returncode!=0
 def call(op,payload):
  p=subprocess.run(['python3','-B',str(CALL),str(root),op,name],input=json.dumps(payload),text=True,capture_output=True)
  assert p.returncode==0,p.stderr
  r=json.loads(p.stdout)
  return r
 for d in DOCS:
  x=call('validate',{'path':d});assert x['exit']==0,(d,x)
 x=call('validate',{'release':'v1.2.3'});assert x['exit']==0,x
 x=call('gate',{'kind':'implement','release':'v1.2.3'});assert x['exit']==0 and not x['output']['ready'],x
 for d in DOCS:
  x=call('approve',{'path':d,'actor':'E7 Evaluator','statement':'Synthetic E7-only approval of this exact disposable fixture decision for commit f8fa91d; no human reviewed these generated contents and no real-product authority is implied.','source':'evaluation-context.json human_authorization and E7 synthetic fixture protocol'})
  assert x['exit']==0,(d,x)
 x=call('gate',{'kind':'implement','release':'v1.2.3'});assert x['exit']==0 and x['output']['ready'],x
 print(name,'preflight ready',hashlib.sha256((root/'test_release.py').read_bytes()).hexdigest())
