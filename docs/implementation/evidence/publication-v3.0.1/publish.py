import datetime,hashlib,json,subprocess,tarfile,tempfile
from pathlib import Path
R=Path('/Users/santiago_migoni/Documents/Projects/spec-flow');repo='santiago-migoni/spec-flow';sha=lambda b:hashlib.sha256(b).hexdigest()
def g(*a):return subprocess.check_output(['git',*a],cwd=R,text=True).strip()
assert not g('status','--porcelain');commit=g('rev-parse','HEAD');assert commit.startswith('c8aee57');assert g('rev-parse','HEAD^').startswith('654b6b8');refs=g('ls-remote','origin','refs/heads/main','refs/tags/v3.0.1');assert refs=='8bf5e8d9d1a3c488d8b10b28827a678884afc3c3\trefs/heads/main'
E=R/'docs/implementation/evidence/publication-v3.0.1';E.mkdir();B=Path(tempfile.mkdtemp(prefix='spec-flow-v301-publish-',dir='/private/tmp'))
v=json.loads((R/'docs/implementation/evidence/release-v3.0.1/verification.json').read_text());assert v['result']=='PASS'
for rel,h in v['source_package_files'].items():assert sha((R/'plugins/spec-flow'/rel).read_bytes())==h
archive=B/'spec-flow-v3.0.1.tar.gz';subprocess.run(['git','archive','--format=tar.gz','--prefix=spec-flow/','-o',str(archive),commit+':plugins/spec-flow'],cwd=R,check=True)
with tarfile.open(archive) as t:
 files={m.name[len('spec-flow/'):]:sha(t.extractfile(m).read()) for m in t if m.isfile()};assert files==v['source_package_files']
digest=sha(archive.read_bytes());(B/'SHA256SUMS').write_text(digest+'  '+archive.name+'\n')
notes=f'''# Spec-Flow v3.0.1

Fix the missing listing logo declaration: both manifests now declare `logo` and `composerIcon` as `./assets/spec-flow-icon.png`. The designed image is unchanged.

- Added a packaging regression check for mirrored manifests and packaged listing/composer assets.
- Fresh isolated installation passed: 115 exact files, 128 plugin tests and 9 hook tests; PNG 1254 × 1254 verified.
- Workflow, controller, hook, profiles, gates, skills and templates are unchanged. E7/E8 reports keep their original source commits and scopes.
- User installation/configuration are unchanged; no projects were migrated.

[Release notes](https://github.com/{repo}/blob/{commit}/docs/releases/v3.0.1.md) · [Fresh verification and original E7/E8 traceability](https://github.com/{repo}/blob/{commit}/docs/implementation/release-v3.0.1.md)

The package declarations and assets were verified. A visible catalog refresh in an existing app session was not demonstrated. Installing/updating the user copy is a separate action.

Release commit: `{commit}`. Download `spec-flow-v3.0.1.tar.gz` and `SHA256SUMS` below; archive SHA-256: `{digest}`.
'''
(E/'github-release-notes.md').write_text(notes)
(E/'target.json').write_text(json.dumps({'authorization':'Si, corrige y prepara v3.0.1. Realiza el commit, tag, push y release.','repository':repo,'tag':'v3.0.1','release_commit':commit,'archive_sha256':digest,'source_files':files},indent=2)+'\n')
def run(label,args):
 p=subprocess.run(args,cwd=R,text=True,capture_output=True)
 with (E/'operations.jsonl').open('a') as f:f.write(json.dumps({'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'step':label,'argv':args,'exit':p.returncode,'stdout':p.stdout,'stderr':p.stderr})+'\n')
 print(label,p.returncode,flush=True);assert p.returncode==0,p.stderr;return p
run('tag',['git','tag','-a','v3.0.1',commit,'-m','Spec-Flow v3.0.1: declare listing logo; isolated installation and 128 + 9 tests passed. Original E7/E8 traceability preserved.'])
run('atomic-push',['git','push','--atomic','origin',commit+':refs/heads/main','refs/tags/v3.0.1'])
run('release',['gh','release','create','v3.0.1','--repo',repo,'--verify-tag','--target',commit,'--title','Spec-Flow v3.0.1','--latest','--notes-file',str(E/'github-release-notes.md'),str(archive),str(B/'SHA256SUMS')])
def api(p):return json.loads(subprocess.check_output(['gh','api','repos/'+repo+'/'+p],cwd=R))
a=api('releases/tags/v3.0.1');assert not a['draft'] and not a['prerelease'] and a['body']==notes;assert api('releases/latest')['id']==a['id'];ref=api('git/ref/tags/v3.0.1');assert ref['object']['type']=='tag';assert api('git/tags/'+ref['object']['sha'])['object']['sha']==commit
D=B/'downloaded';D.mkdir();run('download',['gh','release','download','v3.0.1','--repo',repo,'--dir',str(D)]);assert sha((D/archive.name).read_bytes())==digest;assert (D/'SHA256SUMS').read_bytes()==(B/'SHA256SUMS').read_bytes()
with tarfile.open(D/archive.name) as t:assert {m.name[len('spec-flow/'):]:sha(t.extractfile(m).read()) for m in t if m.isfile()}==files
assert {x['name'] for x in a['assets']}=={archive.name,'SHA256SUMS'}
for x in a['assets']:
 assert x['state']=='uploaded' and x['size']==(D/x['name']).stat().st_size
 if x.get('digest'):assert x['digest']=='sha256:'+sha((D/x['name']).read_bytes())
protected=json.loads((R/'docs/implementation/evidence/release-v3.0.1/protected-before.json').read_text())
for path,old in protected.items():
 p=Path(path);assert {'sha256':sha(p.read_bytes()),'mode':p.stat().st_mode,'mtime_ns':p.stat().st_mtime_ns}==old
receipt={'result':'PASS','verified_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'url':a['html_url'],'release_commit':commit,'tag_object':ref['object']['sha'],'stable_latest':True,'published_at':a['published_at'],'release_id':a['id'],'downloaded_files_verified':len(files),'archive_sha256':digest,'assets':[{k:x.get(k) for k in ('name','size','digest','browser_download_url')} for x in a['assets']],'user_installation_and_config_unchanged':True,'visual_catalog_refresh_verified':False}
(E/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');(E/'downloaded-SHA256SUMS').write_bytes((D/'SHA256SUMS').read_bytes());print(json.dumps(receipt),flush=True)
