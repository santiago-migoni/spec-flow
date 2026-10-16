"""Publish the explicitly authorized, exact package to its existing GitHub repository."""
import datetime,hashlib,json,re,shutil,subprocess,sys,tempfile
from pathlib import Path
R=Path(__file__).resolve().parents[5];E=Path(__file__).resolve().parents[1];p=json.loads((E/'preflight.json').read_text())
def run(label,argv):
    result=subprocess.run(argv,cwd=R,text=True,capture_output=True)
    row={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'step':label,'argv':argv,'exit':result.returncode,'stdout':result.stdout,'stderr':result.stderr}
    with (E/'operations.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
    if result.returncode:raise RuntimeError(label+': '+result.stderr+result.stdout)
    return result.stdout.strip()
assert not subprocess.check_output(['git','status','--porcelain'],cwd=R)
release_sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()
for rel,digest in p['package_files'].items():assert hashlib.sha256((R/'plugins/spec-flow'/rel).read_bytes()).hexdigest()==digest
remote=subprocess.check_output(['git','ls-remote','origin','refs/heads/main','refs/tags/v3.0.0'],cwd=R,text=True);assert 'refs/tags/v3.0.0' not in remote and remote.split()[0]==p['remote_main_before']
subprocess.run(['git','merge-base','--is-ancestor',p['remote_main_before'],release_sha],cwd=R,check=True)
assert subprocess.run(['git','show-ref','--verify','--quiet','refs/tags/v3.0.0'],cwd=R).returncode==1
B=Path(tempfile.mkdtemp(prefix='spec-flow-publication-v3-',dir='/private/tmp'));asset=B/'spec-flow-v3.0.0.tar.gz';shutil.copyfile(p['package_archive'],asset);assert hashlib.sha256(asset.read_bytes()).hexdigest()==p['package_archive_sha256']
checksum=B/'SHA256SUMS';checksum.write_text(p['package_archive_sha256']+'  '+asset.name+'\n')
notes_path=R/'docs/releases/v3.0.0.md';notes=notes_path.read_text()
def absolute(match):
    label,target=match.group(1),match.group(2)
    if '://' in target or target.startswith('#'):return match.group(0)
    rel=(notes_path.parent/target.split('#')[0]).resolve().relative_to(R).as_posix();anchor=('#'+target.split('#',1)[1]) if '#' in target else ''
    return '['+label+'](https://github.com/'+p['repository']+'/blob/'+release_sha+'/'+rel+anchor+')'
notes=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',absolute,notes)
notes+='\n\n## Release provenance\n\n- Release commit: [`'+release_sha+'`](https://github.com/'+p['repository']+'/commit/'+release_sha+').\n- Native E7 functional source: `'+p['functional_E7_source']+'`.\n- Final isolated installed v3.0.0 source: `'+p['final_installed_E8_source']+'`.\n- All 115 package files match that installed source.\n- Package SHA-256: `'+p['package_archive_sha256']+'`.\n- User installation/update and consuming-project migration are outside this publication.\n'
(B/'release-notes.md').write_text(notes)
tag_message='Spec-Flow v3.0.0\n\nRelease commit: '+release_sha+'\nNative E7 source: '+p['functional_E7_source']+'\nFinal installed v3.0.0 E8 source: '+p['final_installed_E8_source']+'\nPackage unchanged from the tested installed source; reports preserved in this commit.'
(E/'publication-target.json').write_text(json.dumps({'release_commit':release_sha,'tag':'v3.0.0','repository':p['repository'],'asset':str(asset),'asset_sha256':p['package_archive_sha256'],'checksum_asset':str(checksum),'notes_file':str(B/'release-notes.md'),'notes_sha256':hashlib.sha256(notes.encode()).hexdigest(),'package_files':p['package_files']},indent=2)+'\n')
run('create-annotated-tag',['git','tag','-a','v3.0.0',release_sha,'-m',tag_message])
run('atomic-push-main-and-tag',['git','push','--atomic','origin',release_sha+':refs/heads/main','refs/tags/v3.0.0'])
url=run('create-github-release',['gh','release','create','v3.0.0','--repo',p['repository'],'--verify-tag','--target',release_sha,'--title','Spec-Flow v3.0.0','--latest','--notes-file',str(B/'release-notes.md'),str(asset),str(checksum)])
print(json.dumps({'release_commit':release_sha,'release_url':url,'asset_sha256':p['package_archive_sha256']}))
