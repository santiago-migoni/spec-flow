import ast,datetime,hashlib,json,os,re,subprocess,sys,tempfile
from pathlib import Path
R=Path('/Users/santiago_migoni/Documents/Projects/spec-flow');E=R/'docs/implementation/evidence/configurable-profiles';P=R/'plugins/spec-flow';sha=lambda b:hashlib.sha256(b).hexdigest()
package=lambda:{p.relative_to(P).as_posix():sha(p.read_bytes()) for p in P.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
before=package();scope=json.loads((E/'before.json').read_text());env=dict(os.environ,PYTHONPATH=str(P),PYTHONDONTWRITEBYTECODE='1')
for source,name,count in [('/private/tmp/profiles-final-tests.txt','yaml-suite.txt',152),('/private/tmp/profiles-final-hooks.txt','hook-suite.txt',10)]:
 text=Path(source).read_text();assert re.search(r'Ran '+str(count)+r' tests',text) and text.rstrip().endswith('OK');(E/name).write_text(text)
code="""import sys,unittest
sys.path.insert(0,'plugins/spec-flow/tests')
import helpers
original=helpers.write_document
def legacy(*args,**kwargs):
 kwargs.setdefault('encoding','json')
 return original(*args,**kwargs)
helpers.write_document=legacy
result=unittest.TextTestRunner().run(unittest.defaultTestLoader.discover('plugins/spec-flow/tests'))
sys.exit(not result.wasSuccessful())
"""
p=subprocess.run(['python3','-B','-c',code],cwd=R,env=env,text=True,capture_output=True);(E/'legacy-json-suite.txt').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr;assert package()==before
# Real CLI round trip, only configuration in an unrelated disposable directory.
with tempfile.TemporaryDirectory(prefix='spec-flow-profile-cli-') as td:
 root=Path(td);input_file=root/'input.json';input_file.write_text('{}');rows=[]
 for operation,data in [('initialize',{}),('configure-profiles',{'profiles':{
    'orchestrator':{'id':'custom-orchestrator','effort':'medium'},
    'implementer':{'id':'custom-implementer','effort':'low'},
    'reviewer':{'id':'custom-reviewer','effort':'high'}}})]:
  input_file.write_text(json.dumps(data));args=['python3','-B',str(P/'scripts/spec-flow.py'),'--root',str(root),operation,'--input',str(input_file)]
  p=subprocess.run(args,cwd=R,env=env,text=True,capture_output=True);assert p.returncode==0,p.stderr;rows.append({'operation':operation,'result':json.loads(p.stdout)})
 assert rows[-1]['result']['applies_to']=='new_runs_only'
 assert json.loads((root/'.spec-flow/config.json').read_text())['retry_limit']==3
 (E/'cli-smoke.json').write_text(json.dumps(rows,indent=2)+'\n')
checks={}
for rel in ['plugin.json','.codex-plugin/plugin.json','hooks/check-phase-approval.py','hooks/hooks.json','harness/runtime/contracts.py','harness/runtime/yaml_format.py','harness/runtime/store.py','harness/runtime/migration.py','harness/schemas/document.schema.json']:
 assert before[rel]==scope['package_files'][rel],rel;checks[rel]=before[rel]
for rel,h in scope['package_files'].items():
 if rel.startswith('harness/_vendor/') or ('/assets/' in rel and rel.startswith('skills/')):assert before[rel]==h,rel
for f in P.rglob('*.py'):ast.parse(f.read_text())
gates={}
for f in (P/'skills').glob('*/SKILL.md'):
 rel=f.relative_to(R).as_posix();original=subprocess.check_output(['git','show',scope['head']+':'+rel],cwd=R,text=True)
 old=re.findall(r'<HARD-GATE>.*?</HARD-GATE>',original,re.S);new=re.findall(r'<HARD-GATE>.*?</HARD-GATE>',f.read_text(),re.S)
 if f.parent.name=='implement':old=[x.replace('attested Sol high orchestration',"orchestration attested against the run's pinned model/effort") for x in old]
 assert old==new,rel;gates[rel]='same controls; configured-profile attestation clause only' if f.parent.name=='implement' else 'literal blocks unchanged'
assert package()==before
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()==scope['head']
subprocess.run(['git','diff','--check'],cwd=R,check=True)
result={'result':'PASS','verified_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'head_unchanged':scope['head'],'version_unchanged':'3.0.1','yaml_suite':152,'legacy_json_suite':152,'hook_suite':10,'cli_configuration_smoke':True,'package_unchanged_during_legacy_and_cli_checks':True,'package_files':before,'preserved_controls_and_yaml_files':checks,'skill_gate_checks':gates,'legacy_suite_fixture_override':code,'native_model_execution_performed':False,'E7_E8_rerun':False,'publication_or_installation_or_project_migration':False,'configuration_scope':'disposable projects only; actual user project configs untouched'}
(E/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in {'package_files','preserved_controls_and_yaml_files','skill_gate_checks','legacy_suite_fixture_override'}}))
