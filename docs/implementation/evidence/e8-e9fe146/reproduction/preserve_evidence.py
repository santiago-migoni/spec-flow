import hashlib,json,shutil,sys,tarfile
from pathlib import Path
c=json.loads(Path(sys.argv[1]).read_text());E=Path(c['evidence']);B=Path(c['base']);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
shutil.copyfile(B/'candidate.tar',E/'candidate-package.tar');assert sha(E/'candidate-package.tar')==c['archive_sha256']
P=Path(c['package']);installed=json.loads((E/'installed-package.json').read_text());actual={p.relative_to(P).as_posix():sha(p) for p in P.rglob('*') if p.is_file()};assert actual==c['test_package_files']==installed['files']
with tarfile.open(E/'tested-package.tar','w') as t:t.add(P,arcname=c['name'])
snaps={}
for label in ('fresh-client-project','bootstrap-smoke-project'):
    root=B/label;files={}
    for p in (root/'.spec-flow').rglob('*'):
        if p.is_file():
            rel=p.relative_to(root);target=E/'scratch'/label/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target);assert target.read_bytes()==p.read_bytes();files[rel.as_posix()]=sha(p)
    assert len(files)==(3 if label=='bootstrap-smoke-project' else 0) and not (root/'.specs').exists() and (not (root/'.spec-flow/runs').exists() or not any((root/'.spec-flow/runs').iterdir()));snaps[label]={'original':str(root),'files':files,'runs_directory_exists':(root/'.spec-flow/runs').is_dir(),'no_run_entries':True,'no_decisions_or_approvals':True}
(E/'preservation.json').write_text(json.dumps({'candidate_archive_sha256':sha(E/'candidate-package.tar'),'tested_archive_sha256':sha(E/'tested-package.tar'),'tested_archive_provenance':'Archived temporary marketplace source after proving all 139 bytes/file hashes equal the installed cache before cleanup; not a copied snapshot of the subsequently removed cache.','exact_installed_test_files':len(actual),'scratch_snapshots':snaps,'restoration_limit':'Archives and snapshots are historical evidence; extracting them does not install a plugin or grant hook trust, approvals or execution authority.'},indent=2)+'\n')
print(json.dumps({'archives':2,'tested_files':len(actual),'scratch_snapshots':len(snaps)}))
