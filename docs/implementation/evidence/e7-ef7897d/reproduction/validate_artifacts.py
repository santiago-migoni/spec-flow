"""Verify the candidate and four preserved disposable repositories; build checksums."""
import ast,hashlib,json,re,subprocess
from datetime import datetime,timezone
from pathlib import Path
R=Path(__file__).resolve().parents[5];E=Path(__file__).resolve().parents[1];c=json.loads((E/'source-and-scope.json').read_text());P=Path(c['source_package_root'])
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert {p.relative_to(P).as_posix() for p in P.rglob('*') if p.is_file()}==set(c['package_files'])
for rel,h in c['package_files'].items():
    assert sha(P/rel)==sha(R/'plugins/spec-flow'/rel)==h,rel
    assert hashlib.sha256(subprocess.check_output(['git','show',c['evaluated_commit']+':plugins/spec-flow/'+rel],cwd=R)).hexdigest()==h,rel
counts={'json':0,'jsonl_records':0,'python':0,'snapshot_files':0,'bundles':0}
for p in E.rglob('*'):
    if not p.is_file():continue
    if p.suffix=='.json':json.loads(p.read_text());counts['json']+=1
    elif p.suffix=='.jsonl':
        for line in p.read_text().splitlines():
            if line.strip():json.loads(line);counts['jsonl_records']+=1
    elif p.suffix=='.py':ast.parse(p.read_text());counts['python']+=1
for dest in [E/'recovery']+[E/'native'/label for label in ('fresh','legacy','negative')]:
    m=json.loads((dest/'preservation.json').read_text());root=Path(m['original_worktree'])
    for rel,info in m['snapshot_files'].items():
        p=dest/'snapshot'/rel;assert sha(p)==info['sha256'] and p.stat().st_size==info['bytes'];assert p.read_bytes()==(root/rel).read_bytes();counts['snapshot_files']+=1
    bundle=dest/'repository.bundle';assert sha(bundle)==m['bundle_sha256'];subprocess.run(['git','bundle','verify',str(bundle)],cwd=root,check=True,capture_output=True);counts['bundles']+=1
    common=Path(subprocess.check_output(['git','rev-parse','--git-common-dir'],cwd=root,text=True).strip());common=common if common.is_absolute() else (root/common).resolve();assert not (common/'spec-flow-active-controller.json').exists()
for doc in (R/'docs/implementation/e7-ef7897d.md',E/'README.md'):
    for target in re.findall(r'\]\(([^)]+)\)',doc.read_text()):
        if '://' not in target:
            resolved=(doc.parent/target.split('#')[0]).resolve()
            assert resolved.exists() or resolved in {(E/'final-artifact-validation.json').resolve(),(E/'SHA256SUMS').resolve()},target
record={'checked_at':datetime.now(timezone.utc).isoformat(),'candidate':c['evaluated_commit'],'package_files_unchanged':len(c['package_files']),**counts,'all_snapshot_originals_equal':True,'all_four_ownership_leases_absent':True,'report_links_valid':True,'result':'PASS'}
(E/'final-artifact-validation.json').write_text(json.dumps(record,indent=2)+'\n')
files=sorted(p for p in E.rglob('*') if p.is_file() and p.name!='SHA256SUMS');(E/'SHA256SUMS').write_text(''.join(sha(p)+'  '+p.relative_to(E).as_posix()+'\n' for p in files));print(json.dumps({**record,'checksum_files':len(files)}))
