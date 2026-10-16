import json,subprocess,sys
from pathlib import Path
E=Path('/Users/santiago_migoni/Documents/Projects/spec-flow/docs/implementation/evidence/e7-f8fa91d/native')
B=Path('/private/tmp/spec-flow-e7-f8fa91d-1fyed3ur')
name,op=sys.argv[1:3]
root=B/(name+'-linked')
payload=json.load(sys.stdin)
p=subprocess.run(['python3','-B',str(E/'e7_call.py'),str(root),op,name],input=json.dumps(payload),text=True,capture_output=True)
if p.returncode: print(p.stderr,file=sys.stderr);raise SystemExit(p.returncode)
r=json.loads(p.stdout)
(E/name/('last-'+op+'.json')).write_text(json.dumps(r,indent=2,ensure_ascii=False))
print(json.dumps(r,indent=2,ensure_ascii=False))
