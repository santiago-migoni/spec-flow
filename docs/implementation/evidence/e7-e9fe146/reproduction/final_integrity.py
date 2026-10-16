"""Verify the candidate bytes and the authorized no-publication boundary."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,subprocess,sys
c=json.loads(Path(sys.argv[1]).read_text());P=Path(c['source_package_root']);E=Path(c['evidence_directory']);R=Path('/Users/santiago_migoni/Documents/Projects/spec-flow')
def git(*args):return subprocess.check_output(['git',*args],cwd=R,text=True)
sha=lambda b:hashlib.sha256(b).hexdigest()
expected=c['package_files'];actual={p.relative_to(P).as_posix():sha(p.read_bytes()) for p in P.rglob('*') if p.is_file()};assert {k:actual[k] for k in expected}==expected
extra=sorted(set(actual)-set(expected));assert all('/__pycache__/' in '/'+k and k.endswith('.pyc') for k in extra)
for rel,digest in expected.items():assert sha((R/'plugins/spec-flow'/rel).read_bytes())==digest,rel
assert git('rev-parse','HEAD').strip()==c['evaluated_commit'];assert git('branch','--show-current').strip()==c['original_branch'];assert git('show-ref','--tags')==c['original_tags'];assert sha((E/'candidate-package.tar').read_bytes())==c['source_archive_sha256']
assert (P/'plugin.json').read_bytes()==(P/'.codex-plugin/plugin.json').read_bytes();assert json.loads((P/'plugin.json').read_text())['version']=='3.0.1'
status=git('status','--porcelain');assert all(('docs/implementation/' in row) for row in status.splitlines()),status
r={'checked_at':datetime.now(timezone.utc).isoformat(),'candidate':c['evaluated_commit'],'source_files_checked':len(expected),'export_source_bytes_unchanged':True,'working_checkout_package_bytes_unchanged':True,'archive_sha256':c['source_archive_sha256'],'generated_pyc_excluded':extra,'bytecode_note':'Test subprocesses created Python bytecode; excluded only generated __pycache__/*.pyc. No tracked package bytes changed.','head_branch_and_tags_unchanged':True,'version':'3.0.1','mirror_equal':True,'worktree_changes':status,'publication_or_install_commands_executed':False,'boundary_basis':'Local HEAD/branch/tags and package hashes verified; evaluator tool actions perform no push/tag/release/install. This is not a remote-publication API query.','result':'PASS'};(E/'final-integrity.json').write_text(json.dumps(r,indent=2)+'\n');print('PASS:139sourcefiles,archive,mirrormanifests,HEAD,branch,tags unchanged; only E7 documentation/evidence changes')
