import hashlib,json,subprocess,sys
from pathlib import Path
c=json.loads(Path(sys.argv[1]).read_text());B=Path(c['disposable_base']);E=Path(c['evidence_directory']);root=Path(c['legacy_worktree']);sys.path.insert(0,c['source_package_root'])
from harness.runtime.contracts import document_digest
ops=[json.loads(s) for s in (E/'native/legacy/operations.jsonl').read_text().splitlines()];preview=next(r for r in ops if r['op']=='migrate-preview');apply=next(r for r in ops if r['op']=='migrate-apply');assert preview['exit']==apply['exit']==0
out=apply['output'];m=preview['output']['manifest'];assert m['imports']=={'approvals':[],'evidence':[]};assert out['approval_imports']['imported']==out['evidence_imports']['imported']==0
archive=root/out['archive'];originals=json.loads((E/'native/legacy/original-snapshot.json').read_text())
for row in m['sources']:
    rel=row['path'];matches=list(archive.rglob(Path(rel).name));assert len(matches)==1
    actual=matches[0].read_bytes();assert hashlib.sha256(actual).hexdigest()==row['sha256']==originals['source_hashes'][Path(rel).name]
    assert subprocess.check_output(['git','show',m['git_head']+':'+rel],cwd=root)==actual
assert not (root/'.specs/001-normalize-release').exists()
approvals=[json.loads(s) for s in (root/'.spec-flow/approvals.jsonl').read_text().splitlines()];assert len(approvals)==7
for row in approvals:
    assert document_digest(root/row['path'])==row['digest']
for p in (B/'legacy-candidates/.specs').rglob('*.md'):
    assert document_digest(p)==document_digest(root/'.specs'/p.relative_to(B/'legacy-candidates/.specs'))
record={'migration_id':out['migration_id'],'preview_digest':preview['output']['digest'],'source_git_head':m['git_head'],'source_files_preserved_and_equal_git':len(m['sources']),'approval_imports':0,'evidence_imports':0,'new_approval_receipts':7,'all_decision_digests_equal_candidates':True,'result':'PASS'}
(E/'migration-independent-check.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record))
