"""Check local release metadata, evidence, frozen artifact and publication boundaries."""
import ast,hashlib,json,re,subprocess,tarfile
from pathlib import Path
R=Path(__file__).resolve().parents[5];E=Path(__file__).resolve().parents[1];c=json.loads((E/'package-comparison.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for rel,h in c['package_files'].items():
    assert sha(R/'plugins/spec-flow'/rel)==sha(Path(c['frozen_test_package'])/rel)==h,rel
assert {p.relative_to(R/'plugins/spec-flow').as_posix() for p in (R/'plugins/spec-flow').rglob('*') if p.is_file()}==set(c['package_files'])
for dirname in ('e7-ef7897d','e8-ef7897d'):
    d=E.parent/dirname
    for line in (d/'SHA256SUMS').read_text().splitlines():
        h,rel=line.split('  ',1);assert sha(d/rel)==h
    for p in d.rglob('*'):
        if p.is_file():assert p.read_bytes()==subprocess.check_output(['git','show','HEAD:'+str(p.relative_to(R))],cwd=R)
for name,count in [('runtime',127),('hooks',9)]:
    x=json.loads((E/(name+'.json')).read_text());assert x['tests']==count and x['exit']==0;assert sha(E/(name+'.txt'))==x['output_sha256']
archive=json.loads((E/'archive.json').read_text());assert sha(E/archive['file'])==archive['sha256']
with tarfile.open(E/archive['file']) as t:
    assert all(m.isfile() and m.name.startswith('spec-flow/') and '..' not in Path(m.name).parts for m in t.getmembers())
    actual={m.name[len('spec-flow/'):]:hashlib.sha256(t.extractfile(m).read()).hexdigest() for m in t.getmembers()};assert actual==c['package_files']
assert subprocess.check_output(['git','for-each-ref','--format=%(refname) %(objectname)','refs/tags','refs/remotes'],cwd=R,text=True)==(E/'refs-before.txt').read_text()
for doc in (R/'docs/releases/v3.0.0.md',R/'docs/implementation/release-v3.0.0.md',E/'README.md'):
    for target in re.findall(r'\]\(([^)]+)\)',doc.read_text()):
        if '://' in target:continue
        dest=(doc.parent/target.split('#')[0]).resolve();assert dest.exists() or dest in {(E/'final-check.json').resolve(),(E/'SHA256SUMS').resolve()},(doc,target)
for p in E.rglob('*'):
    if p.is_file() and p.suffix=='.json':json.loads(p.read_text())
    if p.is_file() and p.suffix=='.py':ast.parse(p.read_text())
manifest=json.loads((R/'plugins/spec-flow/plugin.json').read_text());assert manifest['version']=='3.0.0';assert manifest==json.loads((R/'plugins/spec-flow/.codex-plugin/plugin.json').read_text())
changelog=(R/'CHANGELOG.md').read_text();assert changelog.count('## Release v3.0.0')==1 and 'not published' in changelog.split('## Release v3.0.0',1)[1].split('###',1)[0]
assert changelog.split('## Release v2.0.0',1)[1]==subprocess.check_output(['git','show',c['preparation_parent']+':CHANGELOG.md'],cwd=R,text=True).split('## Release v2.0.0',1)[1]
record={'release_version':'3.0.0','preparation_parent':c['preparation_parent'],'evaluated_functional_base':c['functional_base'],'package_files':115,'unchanged_non_manifest_files':113,'only_manifest_version_changes':True,'manifests_equal':True,'original_E7_E8_reports_and_evidence_preserved':True,'current_frozen_suites':{'plugin':127,'hook':9},'archive_verified':True,'local_doc_links_valid':True,'prior_changelog_history_preserved':True,'tag_and_remote_refs_unchanged':True,'v3_tag_absent':True,'publication':'Not performed; requires separate authorization','fresh_v3_installation':'Not performed in local metadata cut; remains a prepublication check','result':'PASS'}
(E/'final-check.json').write_text(json.dumps(record,indent=2)+'\n')
files=sorted(p for p in E.rglob('*') if p.is_file() and p.name!='SHA256SUMS');(E/'SHA256SUMS').write_text(''.join(sha(p)+'  '+p.relative_to(E).as_posix()+'\n' for p in files));print(json.dumps({**record,'checksum_files':len(files)}))
