import ast,hashlib,json,re,subprocess,sys
from pathlib import Path
c=json.loads(Path(sys.argv[1]).read_text());E=Path(c['evidence_directory']);P=Path(c['source_package_root']);R=Path.cwd();base='6650a194f7ea1c448ffc75d4d21e273fb7d2021e'
def old(rel):return subprocess.check_output(['git','show',base+':plugins/spec-flow/'+rel],cwd=R,text=True)
def methods(s):
    t=ast.parse(s);return {n.name:ast.dump(n,include_attributes=False) for cl in t.body if isinstance(cl,ast.ClassDef) and cl.name=='Engine' for n in cl.body if isinstance(n,ast.FunctionDef)}
a=methods(old('harness/runtime/engine.py'));b=methods((P/'harness/runtime/engine.py').read_text());assert set(a)==set(b);changed=sorted(k for k in a if a[k]!=b[k]);assert changed==['_abandon','_reduce_event_rows'],changed
unchanged=['harness/runtime/codex_adapter.py','harness/runtime/contracts.py','harness/runtime/phases.py','harness/runtime/store.py','hooks/check-phase-approval.py']
for rel in unchanged:assert old(rel)==(P/rel).read_text(),rel
gates=[]
for p in sorted((P/'skills').glob('*/SKILL.md')):
    rel=p.relative_to(P).as_posix();old_gate=re.findall(r'<HARD-GATE>.*?</HARD-GATE>',old(rel),re.S);new_gate=re.findall(r'<HARD-GATE>.*?</HARD-GATE>',p.read_text(),re.S);assert old_gate==new_gate,rel
    if new_gate:gates.append(rel)
assert json.loads((P/'plugin.json').read_text())==json.loads((P/'.codex-plugin/plugin.json').read_text())
assert json.loads((P/'plugin.json').read_text())['version']=='2.0.0'
record={'base':base,'candidate':c['evaluated_commit'],'changed_engine_methods_only':changed,'unchanged_runtime_and_hook_files':unchanged,'hard_gate_blocks_unchanged':gates,'version':'2.0.0','manifest_mirror_equal':True,'preserved_by_unchanged_methods':['retry limit configuration','prepare budget across runs','verification and mutation rejection','task review and close','approval receipts and dependency freshness','native profiles and parent/marker attestation','phase review/audit closure'],'result':'PASS'}
review=json.loads((E.parent/'f03-fix/independent-review.json').read_text())
for rel,digest in review['files_sha256'].items():
    assert hashlib.sha256((R/rel).read_bytes()).hexdigest()==digest,rel
record['independent_fix_review_bytes_match_candidate']=True
record['reviewed_files_checked']=len(review['files_sha256'])
(E/'control-invariants-independent-check.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps({'changed_engine_methods':changed,'hard_gate_blocks_preserved':len(gates)}))
