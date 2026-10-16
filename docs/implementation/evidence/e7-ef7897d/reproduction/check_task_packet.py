import json,hashlib,sys
from pathlib import Path
from datetime import datetime,timezone
c=json.loads(Path(sys.argv[1]).read_text());E=Path(c['evidence_directory']);root=Path(c['disposable_base'])/'fresh-linked';run=(E/'native/fresh/run-id.txt').read_text().strip();state=json.loads((root/'.spec-flow/runs'/run/'state.json').read_text());task=state['tasks']['T-001'];path=root/task['packet_path'];p=json.loads(path.read_text());popped=p.pop('packet_sha256');canonical=hashlib.sha256(json.dumps(p,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest();assert canonical==popped==task['packet_sha256']
assert p['task']['files']==['release.py'];sources={s['path']:s for s in p['sources']};spec=sources['.specs/release-v1.2.3/spec.md'];prose=spec['prose'];assert 'NFR-001' in prose and '01.2.3' in prose and 'ValueError' in prose
assert not sources['.specs/release-v1.2.3/tasks.md']['prose']
assert set(p['selected_acceptance'])=={'AC-001','AC-002'}
result={'checked_at':datetime.now(timezone.utc).isoformat(),'category':'Independent actual native task packet check; no mutations','run_id':run,'packet_sha256':canonical,'packet_file_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'scope_only_release_py':True,'task_prose_omitted':True,'NFR_edge_cases_and_ACs_retained':True,'source_count':len(sources),'result':'PASS'}
(E/'fresh-packet-independent-check.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
