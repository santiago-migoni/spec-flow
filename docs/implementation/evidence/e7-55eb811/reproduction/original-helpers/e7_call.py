import datetime,json,subprocess,sys
from pathlib import Path
root=Path(sys.argv[1]);op=sys.argv[2];payload=json.load(sys.stdin)
P=Path('/private/tmp/spec-flow-e7-55eb811-nh63aagh/source/plugins/spec-flow')
E=Path('/Users/santiago_migoni/Documents/Projects/spec-flow/docs/implementation/evidence/e7-55eb811/native')
label=sys.argv[3] if len(sys.argv)>3 else root.name
p=subprocess.run(['python3','-B',str(P/'scripts/spec-flow.py'),'--root',str(root),op,'--input','/dev/stdin'],input=json.dumps(payload),text=True,capture_output=True)
try:out=json.loads(p.stdout)
except:out=p.stdout
record={'time':datetime.datetime.now(datetime.timezone.utc).isoformat(),'fixture':label,'root':str(root),'op':op,'input':payload,'exit':p.returncode,'output':out,'stderr':p.stderr}
f=E/label/'operations.jsonl';f.parent.mkdir(parents=True,exist_ok=True)
with f.open('a') as h:h.write(json.dumps(record,ensure_ascii=False)+'\n')
print(json.dumps({'exit':p.returncode,'output':out,'stderr':p.stderr},indent=2,ensure_ascii=False))
