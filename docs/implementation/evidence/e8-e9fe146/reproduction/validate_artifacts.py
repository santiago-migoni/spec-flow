"""Validate E8 evidence, immutable candidate, archives and untouched installation."""
import ast,gzip,hashlib,io,json,re,subprocess,sys,tarfile,tomllib
from pathlib import Path
R=Path(__file__).resolve().parents[5];E=Path(__file__).resolve().parents[1];c=json.loads((E/'source-and-scope.json').read_text());sha=lambda b:hashlib.sha256(b).hexdigest();P=Path(c['source']);T=Path(c['package'])
for rel,h in c['candidate_files'].items():
    assert sha((P/rel).read_bytes())==sha((R/'plugins/spec-flow'/rel).read_bytes())==h,rel
    assert sha(subprocess.check_output(['git','show',c['candidate']+':plugins/spec-flow/'+rel],cwd=R))==h,rel
assert sha((E/'candidate-package.tar').read_bytes())==c['archive_sha256']
for archive,prefix,expected in [('candidate-package.tar','plugins/spec-flow/',c['candidate_files']),('tested-package.tar',c['name']+'/',c['test_package_files'])]:
    with tarfile.open(E/archive) as t:
        actual={m.name[len(prefix):]:sha(t.extractfile(m).read()) for m in t.getmembers() if m.isfile()}
    assert actual==expected,archive
assert c['test_package_files']==json.loads((E/'installed-package.json').read_text())['files']
version_check=json.loads((E/'installed-version-check.json').read_text());assert version_check['actual_manifest_version']==version_check['fallback_manifest_version']=='3.0.1'
assert json.loads((P/'plugin.json').read_text())['version']=='3.0.1'
assert subprocess.check_output(['git','for-each-ref','--format=%(refname) %(objectname)','refs/tags','refs/remotes'],cwd=R,text=True)==(E/'refs-before.txt').read_text()
for history in ('e7-ef7897d','e8-ef7897d','release-v3.0.0'):
    historic=E.parent/history
    for line in (historic/'SHA256SUMS').read_text().splitlines():
        h,rel=line.split('  ',1);assert sha((historic/rel).read_bytes())==h,(history,rel)
    for file in historic.rglob('*'):
        if file.is_file():assert file.read_bytes()==subprocess.check_output(['git','show','HEAD:'+str(file.relative_to(R))],cwd=R)

current_e7=E.parent/'e7-e9fe146'
for line in (current_e7/'SHA256SUMS').read_text().splitlines():
    h,rel=line.split('  ',1);assert sha((current_e7/rel).read_bytes())==h,('e7-e9fe146',rel)
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()==c['candidate']
assert json.loads((E/'installed-yaml-templates.json').read_text())['count']==8
changes=[]
for rel,h in c['candidate_files'].items():
    if h!=c['test_package_files'][rel]:
        changes.append(rel);old=json.loads((P/rel).read_text());new=json.loads((T/rel).read_text());new['name']=old['name'];new['extensions']['com.openai']['interface']['displayName']=old['extensions']['com.openai']['interface']['displayName'];assert new==old
assert set(changes)=={'plugin.json','.codex-plugin/plugin.json'}
for name,count in [('runtime',152),('hooks',10)]:
    x=json.loads((E/('installed-'+name+'.json')).read_text());assert x['exit']==0 and x['tests']==count and x['package_unchanged'];assert sha((E/('installed-'+name+'.txt')).read_bytes())==x['output_sha256']
discovery=json.loads((E/'discovered-skills.json').read_text());assert discovery['enabled_count']==14 and all(s['enabled'] for s in discovery['selected_skills'])
assert json.loads((E/'installed-bootstrap-check.json').read_text())['result']=='PASS'
assert json.loads((E/'installed-references-check.json').read_text())['references_checked']==75
ops=[json.loads(s) for s in (E/'installation-operations.jsonl').read_text().splitlines()];assert len(ops)==7 and all(row['exit']==0 for row in ops)
subprocess.run([sys.executable,'-B',str(E/'reproduction/verify_cleanup.py'),str(Path(c['base'])/'context.json')],check=True,capture_output=True)
preserved=json.loads((E/'preservation.json').read_text());snapshot_files=0
for label,record in preserved['scratch_snapshots'].items():
    for rel,h in record['files'].items():
        p=E/'scratch'/label/rel;assert sha(p.read_bytes())==h==sha((Path(record['original'])/rel).read_bytes());snapshot_files+=1
raw_tables=json.loads((E/'cli-output-preservation.json').read_text())
for row in raw_tables['records']:
    raw=(E/row['file']).read_bytes();assert sha(raw)==row['compressed_sha256']
    restored=gzip.decompress(raw);assert sha(restored)==row['uncompressed_sha256'] and len(restored)==row['uncompressed_bytes']
counts={'json':0,'jsonl_records':0,'python':0}
for p in E.rglob('*'):
    if not p.is_file():continue
    if p.suffix=='.json':json.loads(p.read_text());counts['json']+=1
    elif p.suffix=='.jsonl':
        for line in p.read_text().splitlines():
            if line.strip():json.loads(line);counts['jsonl_records']+=1
    elif p.suffix=='.py':ast.parse(p.read_text());counts['python']+=1
for doc in (R/'docs/implementation/e8-e9fe146.md',E/'README.md'):
    for target in re.findall(r'\]\(([^)]+)\)',doc.read_text()):
        if '://' in target:continue
        dest=(doc.parent/target.split('#')[0]).resolve();assert dest.exists() or dest in {(E/'final-artifact-validation.json').resolve(),(E/'SHA256SUMS').resolve()},target
record={'candidate':c['candidate'],'actual_installed_version':'3.0.1','tag_and_remote_refs_unchanged':True,'earlier_E7_E8_and_cut_evidence_preserved':True,'candidate_files_verified_against_git':139,'unchanged_resources':137,'identity_only_manifest_changes':changes,'installed_package_exact':True,'runtime_tests':152,'hook_tests':10,'fresh_client_skills':14,'references_resolved':75,'supported_install_cleanup_operations':7,'archives_verified':2,'scratch_snapshot_files':snapshot_files,**counts,'stable_installation_and_config_unchanged':True,'result':'PASS'}
(E/'final-artifact-validation.json').write_text(json.dumps(record,indent=2)+'\n');files=sorted(p for p in E.rglob('*') if p.is_file() and p.name!='SHA256SUMS');(E/'SHA256SUMS').write_text(''.join(sha(p.read_bytes())+'  '+p.relative_to(E).as_posix()+'\n' for p in files));print(json.dumps({**record,'checksum_files':len(files)}))
