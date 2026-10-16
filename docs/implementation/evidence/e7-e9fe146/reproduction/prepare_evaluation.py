from pathlib import Path
import subprocess,tempfile,json,hashlib,tarfile,io,datetime,os
R=Path('/Users/santiago_migoni/Documents/Projects/spec-flow');sha=lambda b:hashlib.sha256(b).hexdigest();commit=subprocess.check_output(['git','rev-parse','e9fe146^{commit}'],cwd=R,text=True).strip();assert commit=='e9fe1461727e7b508143646132e2b9bc9ba5c16c'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()==commit
assert not subprocess.check_output(['git','status','--porcelain'],cwd=R)
B=Path(tempfile.mkdtemp(prefix='spec-flow-e7-e9fe146-',dir='/private/tmp'));P=B/'source/plugins/spec-flow';P.mkdir(parents=True);E=R/'docs/implementation/evidence/e7-e9fe146';E.mkdir(parents=True);(E/'reproduction').mkdir();(E/'native').mkdir()
raw=subprocess.check_output(['git','archive',commit,'plugins/spec-flow'],cwd=R);archive=E/'candidate-package.tar';archive.write_bytes(raw)
with tarfile.open(fileobj=io.BytesIO(raw)) as t:
 for m in t:
  if m.isfile():
   dest=B/'source'/m.name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(t.extractfile(m).read());dest.chmod(m.mode)
files={p.relative_to(P).as_posix():sha(p.read_bytes()) for p in P.rglob('*') if p.is_file()};assert len(files)==139
profiles={'orchestrator':{'id':'gpt-6.1-sol','effort':'low'},'implementer':{'id':'gpt-6-luna','effort':'high'},'reviewer':{'id':'gpt-6.1-sol','effort':'medium'}}
inventory={'source':'Current host collaboration.spawn_agent tool declaration exposed to this task; selected models and efforts explicitly present. This is host-provided availability evidence, not Python authentication or proof of implementation.','models':[{'id':'gpt-6.1-sol','reasoning_efforts':['low','medium','high','xhigh','max','ultra']},{'id':'gpt-6-luna','reasoning_efforts':['low','medium','high','xhigh','max']}],'selected_profiles':profiles,'actual_session_attestation_required':True}
(E/'host-model-inventory.json').write_text(json.dumps(inventory,indent=2)+'\n')
c={'evaluated_commit':commit,'version':'3.0.1','authorization':'Perfecto. Ejecuta E7 sobre el commit e9fe146, usando proyectos desechables y los perfiles configurados, conservando los controles y registrando pruebas, resultados y evidencias. Sin publicar ni actualizar mi instalación.','source_archive_sha256':sha(raw),'source_package_root':str(P),'disposable_base':str(B),'evidence_directory':str(E),'profiles':profiles,'package_files':files,'host_model_inventory_reference':str(E/'host-model-inventory.json'),'prepared_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'original_branch':subprocess.check_output(['git','branch','--show-current'],cwd=R,text=True).strip(),'original_tags':subprocess.check_output(['git','show-ref','--tags'],cwd=R,text=True)}
(E/'source-and-scope.json').write_text(json.dumps(c,indent=2)+'\n');Path('/private/tmp/spec-flow-e7-e9-context.json').write_text(json.dumps(c,indent=2)+'\n')
# Reuse only synthetic fixture content, adapting its serialization and role language.
s=(R/'docs/implementation/evidence/e7-ef7897d/reproduction/prepare_fixture.py').read_text();s=s.replace("P=Path('/private/tmp/spec-flow-e7-ef7897d-jn0glhbr/source/plugins/spec-flow')",'P=Path('+repr(str(P))+')').replace("B=Path('/private/tmp/spec-flow-e7-ef7897d-jn0glhbr')",'B=Path('+repr(str(B))+')').replace("E=Path('/Users/santiago_migoni/Documents/Projects/spec-flow/docs/implementation/evidence/e7-ef7897d/native')",'E=Path('+repr(str(E/'native'))+')').replace('from harness.runtime.contracts import document_digest','from harness.runtime.contracts import document_digest, render_document')
old='path.write_text(\'# \'+kind.title()+\' — E7-only disposable fixture\\n\\n```spec-flow\\n\'+json.dumps(obj,indent=2)+\'\\n```\\n\\n\'+sections+\'\\n\\n<!-- spec-flow:generated:start -->\\nProgress is maintained by the Spec-Flow harness.\\n<!-- spec-flow:generated:end -->\\n\')'
new='path.write_text(render_document(obj, "# " + kind.title() + " — E7-only disposable fixture\\n\\n" + sections + "\\n\\n<!-- spec-flow:generated:start -->\\nProgress is maintained by the Spec-Flow harness.\\n<!-- spec-flow:generated:end -->\\n"))'
assert old in s;s=s.replace(old,new).replace('Sol task review and distinct Sol phase review','Orchestrator task review and distinct configured reviewer phase review').replace('read-only to Luna','read-only to the implementer').replace('Controller verify, Sol review, close, distinct phase review','Controller verify, orchestrator review, close, distinct phase review');f=E/'reproduction/prepare_fixture.py';f.write_text(s)
for label in ['fresh','negative']:
 out=subprocess.check_output(['python3','-B',str(f),label],text=True);(E/(label+'-preparation.json')).write_text(out)
s=(R/'docs/implementation/evidence/e7-ef7897d/reproduction/prepare_legacy.py').read_text().replace("B=Path('/private/tmp/spec-flow-e7-ef7897d-jn0glhbr')",'B=Path('+repr(str(B))+')').replace("E=Path('/Users/santiago_migoni/Documents/Projects/spec-flow/docs/implementation/evidence/e7-ef7897d/native')",'E=Path('+repr(str(E/'native'))+')')
f=E/'reproduction/prepare_legacy.py';f.write_text(s);out=subprocess.check_output(['python3','-B',str(f)],text=True);(E/'legacy-preparation.json').write_text(out)
# Keep canonical legacy candidates as JSON to exercise the compatibility reader.
import sys;sys.path.insert(0,str(P));from harness.runtime.contracts import read_document,document_digest
candidates=B/'legacy-candidates/.specs';order=['constitution.md','architecture.md','structure.md','roadmap.md','release-v1.2.3/spec.md','release-v1.2.3/plan.md','release-v1.2.3/tasks.md']
for rel in order:
 p=candidates/rel;d=read_document(p);contract=d['contract']
 for dep in contract['depends_on']:dep['digest']=document_digest(candidates.parent/dep['path'])
 p.write_text('# E7 existing JSON candidate\\n'.replace('\\n','\n')+'\n```spec-flow\n'+json.dumps(contract,indent=2)+'\n```\n\n'+d['prose']+'\n\n<!-- spec-flow:generated:start -->\nProgress is maintained by the Spec-Flow harness.\n<!-- spec-flow:generated:end -->\n')
# Linked worktrees; separate repos keep ownership registries and scenarios isolated.
for label in ['fresh','legacy','negative']:
 root=B/(label+'-main');work=B/(label+'-linked');subprocess.run(['git','worktree','add','-b','codex/e7-e9fe146-'+label,str(work)],cwd=root,check=True,capture_output=True)
 c[label+'_worktree']=str(work)
(E/'source-and-scope.json').write_text(json.dumps(c,indent=2)+'\n');Path('/private/tmp/spec-flow-e7-e9-context.json').write_text(json.dumps(c,indent=2)+'\n')
print(json.dumps({'context':'/private/tmp/spec-flow-e7-e9-context.json','source':str(P),'base':str(B),'evidence':str(E),'worktrees':{label:c[label+'_worktree'] for label in ['fresh','legacy','negative']}}))
