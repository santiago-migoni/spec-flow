import datetime,json,subprocess,sys
from pathlib import Path
P=Path('/private/tmp/spec-flow-e7-34d8909-od5uaw4f/source/plugins/spec-flow')
B=Path('/private/tmp/spec-flow-e7-34d8909-od5uaw4f')
# Explicit evidence directory stays outside disposable worktrees.
E=Path('/Users/santiago_migoni/Documents/Projects/spec-flow/docs/implementation/evidence/e7-34d8909/native')
name,variant,op=sys.argv[1:4]
root=B/(name+'-'+variant)
payload=json.load(sys.stdin)
p=subprocess.run(['python3','-B',str(P/'scripts/spec-flow.py'),'--root',str(root),op,'--input','/dev/stdin'],input=json.dumps(payload),text=True,capture_output=True)
try:out=json.loads(p.stdout)
except json.JSONDecodeError:out=p.stdout
record={'time':datetime.datetime.now(datetime.timezone.utc).isoformat(),'root':str(root),'op':op,'input':payload,'exit':p.returncode,'output':out,'stderr':p.stderr}
folder=E/name;folder.mkdir(parents=True,exist_ok=True)
with (folder/'operations.jsonl').open('a') as f:f.write(json.dumps(record,ensure_ascii=False)+'\n')
print(json.dumps({'exit':p.returncode,'output':out,'stderr':p.stderr},ensure_ascii=False))
