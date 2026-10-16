"""Verify a metadata-only local v3.0.0 cut against the exact E7/E8 candidate."""
import hashlib,json,re,shutil,subprocess,tempfile,sys
from pathlib import Path
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[5];E=Path(__file__).resolve().parents[1];P=R/'plugins/spec-flow';base='ef7897d83dedf9fe20c8bf82fb9e311f4cff8107';sha=lambda raw:hashlib.sha256(raw).hexdigest()
files={p.relative_to(P).as_posix():sha(p.read_bytes()) for p in sorted(P.rglob('*')) if p.is_file()};prior=json.loads((E.parent/'e7-ef7897d/source-and-scope.json').read_text())['package_files'];assert set(files)==set(prior) and len(files)==115
changed=sorted(rel for rel in files if files[rel]!=prior[rel]);assert changed==['.codex-plugin/plugin.json','plugin.json']
for rel in changed:
    old=json.loads(subprocess.check_output(['git','show',base+':plugins/spec-flow/'+rel],cwd=R));new=json.loads((P/rel).read_text());assert old['version']=='2.0.0' and new['version']=='3.0.0';restored=dict(new,version='2.0.0');assert restored==old
assert json.loads((P/'plugin.json').read_text())==json.loads((P/'.codex-plugin/plugin.json').read_text())
market=json.loads((R/'.agents/plugins/marketplace.json').read_text());assert market['name']=='spec-flow' and market['plugins'][0]['source']['ref']=='main'
assert subprocess.check_output(['git','show',base+':.agents/plugins/marketplace.json'],cwd=R)==(R/'.agents/plugins/marketplace.json').read_bytes()
for dirname in ('e7-ef7897d','e8-ef7897d'):
    dest=E.parent/dirname
    for line in (dest/'SHA256SUMS').read_text().splitlines():
        h,rel=line.split('  ',1);assert sha((dest/rel).read_bytes())==h,(dirname,rel)
    source=json.loads((dest/'source-and-scope.json').read_text());assert source.get('candidate',source.get('evaluated_commit'))==base
    for p in dest.rglob('*'):
        if p.is_file():assert p.read_bytes()==subprocess.check_output(['git','show','HEAD:'+str(p.relative_to(R))],cwd=R),str(p)
for name in ('e7-ef7897d.md','e8-ef7897d.md'):
    p=R/'docs/implementation'/name;assert p.read_bytes()==subprocess.check_output(['git','show','HEAD:'+str(p.relative_to(R))],cwd=R)
changelog=(R/'CHANGELOG.md').read_text();assert changelog.count('## Release v3.0.0')==1 and changelog.count('## Unreleased')==1;assert changelog.index('## Unreleased')<changelog.index('## Release v3.0.0')<changelog.index('## Release v2.0.0')
oldlog=subprocess.check_output(['git','show','HEAD:CHANGELOG.md'],cwd=R,text=True);assert changelog.split('## Release v2.0.0',1)[1]==oldlog.split('## Release v2.0.0',1)[1]
refs=subprocess.check_output(['git','for-each-ref','--format=%(refname) %(objectname)','refs/tags','refs/remotes'],cwd=R,text=True);assert refs==(E/'refs-before.txt').read_text();assert 'refs/tags/v3.0.0 ' not in refs
B=Path(tempfile.mkdtemp(prefix='spec-flow-release-v3.0.0-',dir='/private/tmp'));frozen=B/'package with spaces/spec-flow';frozen.parent.mkdir();shutil.copytree(P,frozen)
assert {p.relative_to(frozen).as_posix():sha(p.read_bytes()) for p in frozen.rglob('*') if p.is_file()}==files
record={'checked_at':datetime.now(timezone.utc).isoformat(),'release_version':'3.0.0','preparation_parent':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),'functional_base':base,'changed_package_files':changed,'only_version_field_changed':True,'unchanged_package_resources':113,'package_file_count':115,'package_files':files,'manifests_identical':True,'marketplace_main_unchanged':True,'original_E7_E8_reports_and_evidence_unchanged':True,'prior_release_history_unchanged':True,'tag_and_remote_refs_unchanged':True,'v3_tag_absent':True,'frozen_test_package':str(frozen),'test_workspace':str(B),'scope':'Local version/notes preparation; original E7/E8 remain pinned to ef7897d. No fresh installed v3.0.0 evaluation performed.','authorization':'Me parece bien. Prepara el corte local de v3.0.0, actualizando ambos manifiestos, changelog y notas de release, conservando la trazabilidad de E7/E8 y sin hacer push, tag ni publicación todavía.','result':'PASS'}
(E/'package-comparison.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps({'package_files':115,'unchanged_resources':113,'only_version_changed':True,'frozen_package':str(frozen),'E7_E8_preserved':True}))
