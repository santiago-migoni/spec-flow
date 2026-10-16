import hashlib,json,shutil,subprocess
from pathlib import Path
B=Path('/private/tmp/spec-flow-e7-f8fa91d-1fyed3ur')
E=Path('/Users/santiago_migoni/Documents/Projects/spec-flow/docs/implementation/evidence/e7-f8fa91d/native')
P=B/'source/plugins/spec-flow'
root=B/'legacy-main'; candidates=B/'legacy-candidates'
if root.exists() or candidates.exists(): raise SystemExit('already prepared')
root.mkdir(); candidates.mkdir()
def git(*a):
 p=subprocess.run(['git',*a],cwd=root,text=True,capture_output=True);assert p.returncode==0,(a,p.stdout,p.stderr);return p.stdout.strip()
git('init','-b','main');git('config','user.name','E7 Evaluator');git('config','user.email','e7-fixture@example.invalid')
src=root/'.specs/001-normalize-release';src.mkdir(parents=True)
(src/'spec.md').write_text('# Legacy normalization feature\n\nStatus: Approved\n\nAs an evaluator, I want strict numeric release normalization. This historical prose is an E7 synthetic legacy fixture, not a registry approval.\n')
(src/'plan.md').write_text('# Legacy plan\n\nStatus: Approved\n\nImplement strict normalization in release.py and run the fixed unittest suite. E7 synthetic historical fixture.\n')
(src/'tasks.md').write_text('# Legacy tasks\n\nStatus: Approved\n\n- [x] T-001 Implement normalization\n- [x] T-002 Verify tests\n\nThese checkboxes are historical fixture prose, not evidence.\n')
shutil.copyfile(P/'evals/reference/test_release.py',root/'test_release.py')
(root/'release.py').write_text('def normalize_release(value):\n    raise NotImplementedError("E7 legacy baseline")\n')
(root/'.gitignore').write_text('__pycache__/\n')
git('add','.');git('commit','-m','chore(e7): record original synthetic legacy feature')
source_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in src.iterdir()}
shutil.copytree(B/'fresh-main/.specs',candidates/'.specs')
(E/'legacy').mkdir(parents=True,exist_ok=True)
(E/'legacy'/'original-snapshot.json').write_text(json.dumps({'git_head':git('rev-parse','HEAD'),'source_hashes':source_hashes,'test_hash':hashlib.sha256((root/'test_release.py').read_bytes()).hexdigest()},indent=2))
print(json.dumps({'root':str(root),'candidate_dir':str(candidates),'head':git('rev-parse','HEAD'),'source_hashes':source_hashes},indent=2))
