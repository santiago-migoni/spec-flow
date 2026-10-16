import hashlib,json,os,re,subprocess,sys,datetime
from pathlib import Path
R=Path('/Users/santiago_migoni/Documents/Projects/spec-flow');E=R/'docs/implementation/evidence/yaml-frontmatter';sys.path.insert(0,str(R/'plugins/spec-flow'))
from harness.runtime.contracts import read_document
sha=lambda b:hashlib.sha256(b).hexdigest()
package=lambda:{f.relative_to(R/'plugins/spec-flow').as_posix():sha(f.read_bytes()) for f in (R/'plugins/spec-flow').rglob('*') if f.is_file() and '__pycache__' not in f.parts}
before=package()
env=dict(os.environ,PYTHONPATH=str(R/'plugins/spec-flow'),PYTHONDONTWRITEBYTECODE='1')
ops=[]
for name,args in [('yaml-suite',['python3','-B','-m','unittest','discover','-s','plugins/spec-flow/tests','-q']),('hook-suite',['python3','-B','-m','unittest','discover','-s','plugins/spec-flow/hooks','-p','test_*.py','-q'])]:
 p=subprocess.run(args,cwd=R,env=env,text=True,capture_output=True);(E/(name+'.txt')).write_text(p.stdout+p.stderr);ops.append({'name':name,'argv':args,'exit':p.returncode});print(name,p.returncode,flush=True);assert p.returncode==0,p.stderr;assert package()==before
# Exercise the same release/approval/recovery suites with JSON fixtures as well.
legacy_code="""import sys, unittest
sys.path.insert(0,'plugins/spec-flow/tests')
import helpers
original=helpers.write_document
def legacy(*args,**kwargs):
 kwargs.setdefault('encoding','json')
 return original(*args,**kwargs)
helpers.write_document=legacy
suite=unittest.defaultTestLoader.discover('plugins/spec-flow/tests')
result=unittest.TextTestRunner(verbosity=1).run(suite)
sys.exit(not result.wasSuccessful())
"""
p=subprocess.run(['python3','-B','-c',legacy_code],cwd=R,env=env,text=True,capture_output=True);(E/'legacy-json-suite.txt').write_text(p.stdout+p.stderr);ops.append({'name':'legacy-json-suite','exit':p.returncode,'fixture_override':legacy_code});print('legacy-json-suite',p.returncode,flush=True);assert p.returncode==0,p.stderr;assert package()==before
checks={}
for rel in ('plugin.json','.codex-plugin/plugin.json','harness/schemas/document.schema.json','hooks/check-phase-approval.py','harness/runtime/engine.py','harness/runtime/migration.py','harness/runtime/codex_adapter.py','harness/runtime/store.py'):
 old=subprocess.check_output(['git','show','HEAD:plugins/spec-flow/'+rel],cwd=R);assert old==(R/'plugins/spec-flow'/rel).read_bytes();checks[rel]=sha(old)
gates={}
for f in (R/'plugins/spec-flow/skills').glob('*/SKILL.md'):
 rel=f.relative_to(R).as_posix();old=subprocess.check_output(['git','show','HEAD:'+rel],cwd=R,text=True)
 assert re.findall(r'<HARD-GATE>.*?</HARD-GATE>',old,re.S)==re.findall(r'<HARD-GATE>.*?</HARD-GATE>',f.read_text(),re.S)
 gates[rel]=True
for kind,rel in {'constitution':'constitution/assets/constitution-template.md','architecture':'design/assets/architecture-template.md','infrastructure':'design/assets/infrastructure-template.md','structure':'design/assets/structure-template.md','roadmap':'roadmap/assets/roadmap-template.md','spec':'specify/assets/spec-template.md','plan':'plan/assets/plan-template.md','tasks':'tasks/assets/tasks-template.md'}.items():
 f=R/'plugins/spec-flow/skills'/rel;assert f.read_text().startswith('---\n');assert read_document(f)['contract']['kind']==kind
subprocess.run(['git','diff','--check'],cwd=R,check=True)
result={'result':'PASS','verified_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'base_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),'operations':ops,'version_unchanged':'3.0.1','templates':8,'gated_skills_unchanged':gates,'protected_runtime_and_manifests':checks,'package_before_and_after_tests_identical':True,'package_sha256':before,'published':False,'installed_or_migrated_user_projects':False,'native_E7_E8_rerun':False,'scope':'Local deterministic suites, JSON/YAML fixtures, closure/recovery, approvals, hooks and template controls; no publication or host installation.'}
(E/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print('all verification PASS',flush=True)
