import datetime,hashlib,json,subprocess,sys
from pathlib import Path
B=Path('/private/tmp/spec-flow-e7-34d8909-od5uaw4f')
E=Path('/Users/santiago_migoni/Documents/Projects/spec-flow/docs/implementation/evidence/e7-34d8909/native')
name=sys.argv[1];root=B/(name+'-linked');folder=E/name;folder.mkdir(parents=True,exist_ok=True)
DOCS=['.specs/constitution.md','.specs/architecture.md','.specs/structure.md','.specs/roadmap.md','.specs/release-v1.2.3/spec.md','.specs/release-v1.2.3/plan.md','.specs/release-v1.2.3/tasks.md']
def call(op,payload):
 p=subprocess.run(['python3','-B',str(E/'native_call.py'),name,'linked',op],input=json.dumps(payload),text=True,capture_output=True)
 if p.returncode:raise RuntimeError(p.stderr)
 return json.loads(p.stdout)
p=subprocess.run(['python3','-B','-m','unittest','-v','test_release.py'],cwd=root,text=True,capture_output=True)
(folder/'baseline.json').write_text(json.dumps({'time':datetime.datetime.now(datetime.timezone.utc).isoformat(),'command':['python3','-B','-m','unittest','-v','test_release.py'],'exit':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'code_sha256':hashlib.sha256((root/'release.py').read_bytes()).hexdigest(),'test_sha256':hashlib.sha256((root/'test_release.py').read_bytes()).hexdigest()},indent=2))
assert p.returncode!=0 and 'Ran 4 tests' in p.stderr,p.stderr
assert hashlib.sha256((root/'test_release.py').read_bytes()).hexdigest()=='7bb24f05e31ffe3fdb53c96895e3462a5823fe7ac9ad4bdbe0e612d206cd0577'
for d in DOCS:
 r=call('validate',{'path':d});assert r['exit']==0,(d,r)
r=call('validate',{'release':'v1.2.3'});assert r['exit']==0,r
r=call('gate',{'kind':'implement','release':'v1.2.3'});assert r['exit']==0 and r['output']['ready'] is False,r
for d in DOCS:
 r=call('approve',{'path':d,'actor':'E7 Evaluator','statement':'Synthetic E7-only approval of this exact disposable fixture decision for commit 34d8909; no human reviewed generated fixture contents and no real-product authority is implied.','source':'evaluation-context.json human_authorization and E7 synthetic fixture protocol'})
 assert r['exit']==0,(d,r)
r=call('gate',{'kind':'implement','release':'v1.2.3'});assert r['exit']==0 and r['output']['ready'] is True,r
print(name,'ready; baseline 4 methods failing; 7 receipts')
