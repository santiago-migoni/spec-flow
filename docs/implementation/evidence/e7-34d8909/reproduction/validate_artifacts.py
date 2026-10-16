"""Check portable E7 artifacts against immutable source and retained originals."""
import ast, hashlib, json, re, subprocess
from datetime import datetime, timezone
from pathlib import Path
R=Path(__file__).resolve().parents[5]
E=Path(__file__).resolve().parents[1]
s=json.loads((E/'source-and-scope.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for rel,digest in s['package_files'].items():
    assert sha(Path(s['source_package_root'])/rel)==digest,rel
    assert sha(R/'plugins/spec-flow'/rel)==digest,rel
    raw=subprocess.check_output(['git','show',s['evaluated_commit']+':plugins/spec-flow/'+rel],cwd=R)
    assert hashlib.sha256(raw).hexdigest()==digest,rel
counts={'json':0,'jsonl_records':0,'python':0,'snapshot_files':0,'bundles':0}
for p in E.rglob('*'):
    if not p.is_file():continue
    if p.suffix=='.json':json.loads(p.read_text());counts['json']+=1
    elif p.suffix=='.jsonl':
        for line in p.read_text().splitlines():
            if line.strip():json.loads(line);counts['jsonl_records']+=1
    elif p.suffix=='.py':ast.parse(p.read_text());counts['python']+=1
for prefix in ('native','recovery'):
    for label in ('fresh','legacy','negative'):
        dest=E/prefix/label
        m=json.loads((dest/'preservation.json').read_text())
        root=Path(m['original_worktree'])
        for rel,info in m['snapshot_files'].items():
            p=dest/'snapshot'/rel
            assert sha(p)==info['sha256'] and p.stat().st_size==info['bytes'],str(p)
            assert p.read_bytes()==(root/rel).read_bytes(),str(p)
            counts['snapshot_files']+=1
        bundle=dest/'repository.bundle'
        assert sha(bundle)==m['bundle_sha256']
        subprocess.run(['git','bundle','verify',str(bundle)],cwd=root,check=True,capture_output=True)
        counts['bundles']+=1
        common=subprocess.check_output(['git','rev-parse','--git-common-dir'],cwd=root,text=True).strip()
        registry=(root/common).resolve()/'spec-flow-active-controller.json'
        expected=prefix=='native' and label=='negative'
        assert registry.exists()==expected
        if expected:assert registry.read_bytes()==(dest/'ownership-registration.json').read_bytes()
for doc in (R/'docs/implementation/e7-34d8909.md',E/'README.md'):
    for target in re.findall(r'\]\(([^)]+)\)',doc.read_text()):
        if '://' not in target:assert (doc.parent/target.split('#')[0]).exists(),target
record={'checked_at':datetime.now(timezone.utc).isoformat(),'candidate':s['evaluated_commit'],'package_files_unchanged':len(s['package_files']),**counts,'snapshot_originals_equal':True,'ownership_expected_only_new_negative':True,'report_links_valid':True,'result':'PASS'}
(E/'final-artifact-validation.json').write_text(json.dumps(record,indent=2)+'\n')
files=sorted(p for p in E.rglob('*') if p.is_file() and p.name!='SHA256SUMS')
(E/'SHA256SUMS').write_text(''.join(sha(p)+'  '+p.relative_to(E).as_posix()+'\n' for p in files))
print(json.dumps({**record,'checksum_files':len(files)}))
