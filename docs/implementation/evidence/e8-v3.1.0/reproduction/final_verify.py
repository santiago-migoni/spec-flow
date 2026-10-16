from pathlib import Path
import json,hashlib,subprocess,tarfile,sys,re,ast
R=Path(__file__).resolve().parents[5];E=Path(__file__).resolve().parents[1];c=json.loads((E/'source-and-scope.json').read_text());sha=lambda b:hashlib.sha256(b).hexdigest()
for rel,h in c['candidate_files'].items():
 assert sha(subprocess.check_output(['git','show',c['candidate']+':plugins/spec-flow/'+rel],cwd=R))==h
 assert sha((R/'plugins/spec-flow'/rel).read_bytes())==h
for archive,prefix,expected in [('candidate-package.tar','plugins/spec-flow/',c['candidate_files']),('tested-package.tar',c['name']+'/',c['test_package_files'])]:
 with tarfile.open(E/archive) as t:assert {m.name[len(prefix):]:sha(t.extractfile(m).read()) for m in t if m.isfile()}==expected
assert json.loads((E/'installed-package.json').read_text())['files']==c['test_package_files']
for name,count in [('runtime',152),('hooks',10)]:
 v=json.loads((E/('installed-'+name+'.json')).read_text());assert v['exit']==0 and v['tests']==count and v['package_unchanged'];assert sha((E/('installed-'+name+'.txt')).read_bytes())==v['output_sha256']
assert json.loads((E/'discovered-skills.json').read_text())['enabled_count']==14
assert json.loads((E/'installed-yaml-templates.json').read_text())['count']==8
assert json.loads((E/'installed-references-check.json').read_text())['references_checked']==75
assert json.loads((E/'installed-version-check.json').read_text())['actual_manifest_version']=='3.1.0'
subprocess.run([sys.executable,'-B',str(E/'reproduction/verify_cleanup.py'),str(Path(c['base'])/'context.json')],cwd=R,check=True,capture_output=True)
for label in ['e7-e9fe146','e8-e9fe146']:
 old=E.parent/label
 for row in (old/'SHA256SUMS').read_text().splitlines():
  h,rel=row.split('  ',1);f=old/rel;assert sha(f.read_bytes())==h;assert sha(subprocess.check_output(['git','show','HEAD:'+str(f.relative_to(R))],cwd=R))==h
changes=[]
for rel in c['candidate_files']:
 old=subprocess.check_output(['git','show','e9fe146:plugins/spec-flow/'+rel],cwd=R);new=(R/'plugins/spec-flow'/rel).read_bytes()
 if old!=new:
  a=json.loads(old);b=json.loads(new);assert a['version']=='3.0.1' and b['version']=='3.1.0';b['version']=a['version'];assert a==b;changes.append(rel)
assert set(changes)=={'plugin.json','.codex-plugin/plugin.json'}
ops=[json.loads(x) for x in (E/'installation-operations.jsonl').read_text().splitlines()];assert len(ops)==8 and ops[0]['exit']==1 and all(x['exit']==0 for x in ops[1:])
for doc in [R/'docs/implementation/e8-v3.1.0.md',E/'README.md']:
 for target in re.findall(r'\]\(([^)]+)\)',doc.read_text()):
  if '://' not in target:assert (doc.parent/target).exists() or target.endswith(('final-artifact-validation.json','SHA256SUMS')),target
for p in (E/'reproduction').glob('*.py'):ast.parse(p.read_text())
r={'result':'PASS','candidate':c['candidate'],'version':'3.1.0','source_files_against_git':139,'exact_installed_copy':True,'only_functional_base_changes':changes,'only_field':'version','runtime_tests':152,'hook_tests':10,'fresh_client_enabled_skills':14,'yaml_templates':8,'references':75,'E7_E8_evidence_unchanged_and_tracked':True,'stable_installation_and_config_unchanged':True,'temporary_plugin_marketplace_removed':True,'initial_identity_rejection_preserved':True};(E/'final-artifact-validation.json').write_text(json.dumps(r,indent=2)+'\n')
files=sorted(p for p in E.rglob('*') if p.is_file() and p.name!='SHA256SUMS');(E/'SHA256SUMS').write_text(''.join(sha(p.read_bytes())+'  '+p.relative_to(E).as_posix()+'\n' for p in files));print(json.dumps(r))
