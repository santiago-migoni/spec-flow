"""Verify the remote release/tag and downloaded package; never install or migrate."""
import datetime,hashlib,json,subprocess,tarfile,tempfile,tomllib
from pathlib import Path
R=Path(__file__).resolve().parents[5];E=Path(__file__).resolve().parents[1];p=json.loads((E/'preflight.json').read_text());target=json.loads((E/'publication-target.json').read_text());repo=p['repository'];release_sha=target['release_commit']
def api(path):return json.loads(subprocess.check_output(['gh','api','repos/'+repo+'/'+path],cwd=R,text=True))
release=api('releases/tags/v3.0.0');assert release['tag_name']=='v3.0.0' and not release['draft'] and not release['prerelease'] and release['published_at'];assert api('releases/latest')['id']==release['id']
ref=api('git/ref/tags/v3.0.0');assert ref['object']['type']=='tag';tag=api('git/tags/'+ref['object']['sha']);assert tag['object']['type']=='commit' and tag['object']['sha']==release_sha
assert subprocess.check_output(['git','rev-parse','v3.0.0^{}'],cwd=R,text=True).strip()==release_sha
refs=subprocess.check_output(['git','ls-remote','origin','refs/heads/main','refs/tags/v3.0.0','refs/tags/v3.0.0^{}'],cwd=R,text=True);remote={line.split()[1]:line.split()[0] for line in refs.splitlines()};assert remote['refs/tags/v3.0.0^{}']==release_sha and remote['refs/tags/v3.0.0']==ref['object']['sha'];assert remote['refs/heads/main']==release_sha
B=Path(tempfile.mkdtemp(prefix='spec-flow-v3-published-download-',dir='/private/tmp'));subprocess.run(['gh','release','download','v3.0.0','--repo',repo,'--pattern','spec-flow-v3.0.0.tar.gz','--pattern','SHA256SUMS','--dir',str(B)],cwd=R,check=True,capture_output=True)
archive=B/'spec-flow-v3.0.0.tar.gz';digest=hashlib.sha256(archive.read_bytes()).hexdigest();assert digest==p['package_archive_sha256'];assert (B/'SHA256SUMS').read_text()==digest+'  '+archive.name+'\n'
with tarfile.open(archive) as t:
    members=t.getmembers();assert all(m.isfile() and m.name.startswith('spec-flow/') and '..' not in Path(m.name).parts for m in members)
    files={m.name[len('spec-flow/'):]:hashlib.sha256(t.extractfile(m).read()).hexdigest() for m in members};assert files==p['package_files']
assets=[]
for asset in release['assets']:
    assert asset['name'] in {'spec-flow-v3.0.0.tar.gz','SHA256SUMS'}
    local=B/asset['name'];assert asset['size']==local.stat().st_size
    server_digest=asset.get('digest')
    if server_digest:assert server_digest=='sha256:'+hashlib.sha256(local.read_bytes()).hexdigest()
    assets.append({k:asset.get(k) for k in ('id','name','size','digest','browser_download_url','state')})
assert len(assets)==2 and all(a['state']=='uploaded' for a in assets)
base=json.loads((E/'protected-before.json').read_text());root=Path(base['root']);sha=lambda raw:hashlib.sha256(raw).hexdigest();actual={f.relative_to(root).as_posix():{'sha256':sha(f.read_bytes()),'mode':f.stat().st_mode,'mtime_ns':f.stat().st_mtime_ns} for f in root.rglob('*') if f.is_file()};assert actual==base['files']
conf=Path.home()/'.codex/config.toml';cfg=tomllib.loads(conf.read_text());assert sha(conf.read_bytes())==base['config_bytes_sha256'];assert sha(json.dumps(cfg,sort_keys=True,default=str).encode())==base['config_semantic_sha256'];assert cfg['plugins']['spec-flow@spec-flow']==base['stable_setting']
for rel,h in p['package_files'].items():assert sha(subprocess.check_output(['git','show',release_sha+':plugins/spec-flow/'+rel],cwd=R))==h
for history in ('e7-ef7897d','e8-ef7897d','release-v3.0.0','e8-d19d6e0'):
    d=E.parent/history
    for line in (d/'SHA256SUMS').read_text().splitlines():
        h,rel=line.split('  ',1);assert sha((d/rel).read_bytes())==h,(history,rel)
    for f in d.rglob('*'):
        if f.is_file():assert f.read_bytes()==subprocess.check_output(['git','show',release_sha+':'+str(f.relative_to(R))],cwd=R)
receipt={'verified_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'repository':repo,'release_commit':release_sha,'tag':'v3.0.0','annotated_tag_object':ref['object']['sha'],'tag_target_verified':True,'remote_main_at_publication':remote['refs/heads/main'],'url':release['html_url'],'release_id':release['id'],'published_at':release['published_at'],'draft':release['draft'],'prerelease':release['prerelease'],'latest':True,'assets':assets,'download_directory':str(B),'downloaded_package_sha256':digest,'downloaded_files_verified':len(files),'downloaded_checksum_verified':True,'package_identical_to_final_installed_E8_source':p['final_installed_E8_source'],'E7_source':p['functional_E7_source'],'original_reports_and_evidence_preserved_in_release_commit':True,'user_installation_files_unchanged':len(actual),'user_installation_modes_and_mtimes_unchanged':True,'configuration_bytes_and_semantics_unchanged':True,'hook_trust_unchanged':True,'installation_or_migration_performed':False,'result':'PASS'}
(E/'publication-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
(E/'github-release-notes.md').write_text(release['body']);(E/'downloaded-SHA256SUMS').write_bytes((B/'SHA256SUMS').read_bytes())
print(json.dumps({'release':release['html_url'],'release_commit':release_sha,'latest':True,'downloaded_files_verified':len(files),'stable_files_unchanged':len(actual),'configuration_unchanged':True,'result':'PASS'}))
