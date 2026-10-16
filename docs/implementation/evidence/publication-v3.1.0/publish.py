"""Historical authorized publication script. Do not rerun on an existing release/tag."""
from pathlib import Path
from datetime import datetime,timezone
import json,subprocess,hashlib,tarfile,tempfile
R=Path('/Users/santiago_migoni/Documents/Projects/spec-flow');E=R/'docs/implementation/evidence/publication-v3.1.0';repo='santiago-migoni/spec-flow';tag='v3.1.0';commit='fad239f6f280bc35c0f7f5b2236ca2abd37d7814';sha=lambda b:hashlib.sha256(b).hexdigest()
def g(*a):return subprocess.check_output(['git',*a],cwd=R,text=True).strip()
head=g('rev-parse','HEAD');assert head.startswith('7ea31fe');assert g('branch','--show-current')=='main';assert g('status','--porcelain')=='?? docs/implementation/evidence/publication-v3.1.0/'
assert g('remote','get-url','origin')=='https://github.com/santiago-migoni/spec-flow.git'
refs=g('ls-remote','origin','refs/heads/main','refs/tags/'+tag);assert refs=='3cb96fe43a5615b716ebf98ce63208e90ce2f953\trefs/heads/main',refs
subprocess.run(['git','merge-base','--is-ancestor','3cb96fe43a5615b716ebf98ce63208e90ce2f953',head],cwd=R,check=True)
c=json.loads((R/'docs/implementation/evidence/e8-v3.1.0/source-and-scope.json').read_text());v=json.loads((R/'docs/implementation/evidence/e8-v3.1.0/final-artifact-validation.json').read_text());assert v['result']=='PASS' and c['candidate']==commit
for label in ['e7-e9fe146','e8-e9fe146','e8-v3.1.0']:
 D=R/'docs/implementation/evidence'/label
 for line in (D/'SHA256SUMS').read_text().splitlines():
  h,rel=line.split('  ',1);f=D/rel;assert sha(f.read_bytes())==h;assert sha(subprocess.check_output(['git','show',head+':'+str(f.relative_to(R))],cwd=R))==h
for rel,h in c['candidate_files'].items():assert sha((R/'plugins/spec-flow'/rel).read_bytes())==h
B=Path(tempfile.mkdtemp(prefix='spec-flow-v310-publish-',dir='/private/tmp'));archive=B/'spec-flow-v3.1.0.tar.gz';subprocess.run(['git','archive','--format=tar.gz','--prefix=spec-flow/','-o',str(archive),commit+':plugins/spec-flow'],cwd=R,check=True)
with tarfile.open(archive) as t:assert {m.name[len('spec-flow/'):]:sha(t.extractfile(m).read()) for m in t if m.isfile()}==c['candidate_files']
digest=sha(archive.read_bytes());(B/'SHA256SUMS').write_text(digest+'  '+archive.name+'\n')
notes=f'''# Spec-Flow v3.1.0

Generate canonical documents with YAML frontmatter and choose model/effort profiles for native orchestration, implementation and independent review.

- Eight templates now begin with YAML metadata. Existing fenced JSON documents retain read compatibility and historical digests; generated status preserves encoding. No automatic conversion or project migration.
- Validated atomic `configure-profiles`, host inventory checks, exact session attestation and immutable run/packet profile snapshots. New defaults: `gpt-6.1-sol/low`, `gpt-6-luna/high`, `gpt-6.1-sol/medium`. Existing configs and old runs remain compatible.
- Approval receipts, exact dependencies, worktree ownership, one implementer, three attempts, independent phase review and evidence-based closure remain enforced.
- E7 and E8 passed on functional commit `e9fe146`. Final isolated v3.1.0 installation passed: 139 exact files, 14 skills, 152 controller tests, 10 hook tests, eight YAML templates and 75 local references. Evaluator observations and category limits remain recorded.
- User installation/configuration unchanged; no projects migrated and no hook trust granted. No claim of live UI/catalog refresh or token/cost savings.

[Detailed release notes](https://github.com/{repo}/blob/{commit}/docs/releases/v3.1.0.md) · [E7](https://github.com/{repo}/blob/{head}/docs/implementation/e7-e9fe146.md) · [E8](https://github.com/{repo}/blob/{head}/docs/implementation/e8-e9fe146.md) · [Final isolated installation](https://github.com/{repo}/blob/{head}/docs/implementation/e8-v3.1.0.md)

Release commit: `{commit}`. Only manifest version fields differ from the functional candidate. Evidence commit: `{head}`. Download `spec-flow-v3.1.0.tar.gz` and `SHA256SUMS` below; archive SHA-256: `{digest}`.
'''
(E/'github-release-notes.md').write_text(notes);(E/'target.json').write_text(json.dumps({'repository':repo,'tag':tag,'release_commit':commit,'evidence_commit':head,'archive_sha256':digest,'package_files':c['candidate_files'],'authorization':'Me parece bien. Publica v3.1.0 siguiendo esos pasos, incluyendo los commits, la verificación aislada final, el tag, el push y la release de GitHub, conservando la trazabilidad de E7/E8 y sin actualizar mi instalación ni migrar proyectos.'},indent=2)+'\n')
def run(step,args):
 p=subprocess.run(args,cwd=R,text=True,capture_output=True)
 with (E/'operations.jsonl').open('a') as f:f.write(json.dumps({'at':datetime.now(timezone.utc).isoformat(),'step':step,'argv':args,'exit':p.returncode,'stdout':p.stdout,'stderr':p.stderr})+'\n')
 print(step,p.returncode,flush=True);assert p.returncode==0,p.stderr;return p
run('annotated-tag',['git','tag','-a',tag,commit,'-m','Spec-Flow v3.1.0: YAML and configurable profiles; native E7, E8 and final isolated 152 + 10 tests passed.'])
run('atomic-push',['git','push','--atomic','origin',head+':refs/heads/main','refs/tags/'+tag])
run('github-release',['gh','release','create',tag,'--repo',repo,'--verify-tag','--target',commit,'--title','Spec-Flow v3.1.0','--latest','--notes-file',str(E/'github-release-notes.md'),str(archive),str(B/'SHA256SUMS')])
def api(path):return json.loads(subprocess.check_output(['gh','api','repos/'+repo+'/'+path],cwd=R))
a=api('releases/tags/'+tag);assert not a['draft'] and not a['prerelease'] and a['body']==notes;assert api('releases/latest')['id']==a['id'];ref=api('git/ref/tags/'+tag);assert ref['object']['type']=='tag';assert api('git/tags/'+ref['object']['sha'])['object']['sha']==commit
D=B/'downloaded';D.mkdir();run('download-published-assets',['gh','release','download',tag,'--repo',repo,'--dir',str(D)]);assert sha((D/archive.name).read_bytes())==digest;assert (D/'SHA256SUMS').read_bytes()==(B/'SHA256SUMS').read_bytes()
with tarfile.open(D/archive.name) as t:assert {m.name[len('spec-flow/'):]:sha(t.extractfile(m).read()) for m in t if m.isfile()}==c['candidate_files']
assert {x['name'] for x in a['assets']}=={archive.name,'SHA256SUMS'}
for x in a['assets']:
 assert x['state']=='uploaded' and x['size']==(D/x['name']).stat().st_size
 if x.get('digest'):assert x['digest']=='sha256:'+sha((D/x['name']).read_bytes())
subprocess.run(['python3','-B',str(R/'docs/implementation/evidence/e8-v3.1.0/reproduction/verify_cleanup.py'),str(Path(c['base'])/'context.json')],cwd=R,check=True,capture_output=True)
receipt={'result':'PASS','verified_at':datetime.now(timezone.utc).isoformat(),'url':a['html_url'],'release_commit':commit,'evidence_commit':head,'tag_object':ref['object']['sha'],'stable_latest':True,'published_at':a['published_at'],'release_id':a['id'],'downloaded_package_files_verified':139,'archive_sha256':digest,'assets':[{k:x.get(k) for k in ('name','size','digest','browser_download_url')} for x in a['assets']],'user_installation_and_config_unchanged':True,'project_migrations':False,'hook_trust_changed':False};(E/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');(E/'downloaded-SHA256SUMS').write_bytes((D/'SHA256SUMS').read_bytes());print(json.dumps(receipt),flush=True)
