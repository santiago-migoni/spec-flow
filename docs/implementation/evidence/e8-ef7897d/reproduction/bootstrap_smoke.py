"""Exercise only discovery-derived installed bootstrap paths in a fresh scratch repo."""
import json,subprocess,sys,hashlib,os,re
from pathlib import Path
c=json.loads(Path(sys.argv[1]).read_text());E=Path(c['evidence']);B=Path(c['base']);discovery=json.loads((E/'discovered-skills.json').read_text());entry=next(s for s in discovery['selected_skills'] if s['name']==c['name']+':using-spec-flow');skill=Path(entry['path']);P=skill.parents[2];root=B/'bootstrap-smoke-project';verify_only=len(sys.argv)>2 and sys.argv[2]=='verify-only'
if not verify_only:
    root.mkdir();subprocess.run(['git','init','-q',str(root)],check=True);assert {p.name for p in root.iterdir()}=={'.git'}
text=skill.read_text();operations=P/'harness/contracts/operations.md';assert operations.is_file();assert 'initialize' in text and operations.read_text()
rows=[]
def call(op,payload,exit=0):
    argv=[sys.executable,'-B',str(P/'scripts/spec-flow.py'),'--root',str(root),op,'--input','/dev/stdin'];p=subprocess.run(argv,input=json.dumps(payload),capture_output=True,text=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','GIT_OPTIONAL_LOCKS':'0'});output=json.loads(p.stdout);row={'argv':argv,'input':payload,'exit':p.returncode,'output':output,'stderr':p.stderr};rows.append(row);
    with (E/'installed-bootstrap-operations.jsonl').open('a') as stream:stream.write(json.dumps(row)+'\n')
    assert p.returncode==exit,output;return output
if not verify_only:
    assert call('status',{})['status']=='uninitialized';assert not (root/'.spec-flow').exists()
    assert call('initialize',{})['already_initialized'] is False
    assert call('initialize',{})['already_initialized'] is True
    assert call('status',{})['runs']==[]
    assert call('gate',{'kind':'constitution'})['ready'] is True
    for kind in ('using-spec-flow','design','backlog'):
        out=call('gate',{'kind':kind},exit=2);assert out['error']['code']=='invalid_input',out
else:
    rows=[json.loads(line) for line in (E/'installed-bootstrap-operations.jsonl').read_text().splitlines()]
    assert len(rows)==8
assert not (root/'.specs').exists() and not (root/'.spec-flow/approvals.jsonl').exists() and not any((root/'.spec-flow/runs').iterdir())
config=json.loads((root/'.spec-flow/config.json').read_text());assert config['retry_limit']==3;assert config['profiles']=={'orchestrator':{'id':'gpt-6-sol','effort':'high'},'implementer':{'id':'gpt-6-luna','effort':'high'},'reviewer':{'id':'gpt-6-sol','effort':'high'}}
(E/'installed-bootstrap-operations.json').write_text(json.dumps(rows,indent=2)+'\n')
(E/'installed-bootstrap-check.json').write_text(json.dumps({'discovered_skill':entry['name'],'skill_path':str(skill),'skill_sha256':hashlib.sha256(skill.read_bytes()).hexdigest(),'installed_root':str(P),'scratch':str(root),'initial_only_git':True,'initialize_idempotent':True,'constitution_gate_ready':True,'unsupported_gate_kinds_rejected':['using-spec-flow','design','backlog'],'no_decisions_approvals_or_runs_created':True,'profiles_and_retry_limit_preserved':True,'classification':'Explicit E8 scratch initialization, not strict consultation or production execution','next_decision':'Project constitution needs human purpose/outcomes and subsequent approval; no product decisions invented.','result':'PASS'},indent=2)+'\n')
# Resolve real local Markdown references in installed skills and harness; external URLs and in-document anchors are outside this check.
references=[]
for p in sorted(list((P/'skills').rglob('*.md'))+list((P/'harness').rglob('*.md'))):
    for target in re.findall(r'\]\(([^)\n]+)\)',p.read_text()):
        if '://' in target or target.startswith('#'):continue
        target=target.strip('<>').split('#')[0]
        if not target:continue
        resolved=(p.parent/target).resolve();assert resolved.is_relative_to(P) and resolved.exists(),(p,target)
        references.append({'source':str(p.relative_to(P)),'target':target,'resolved':str(resolved.relative_to(P))})
for rel in ('scripts/spec-flow.py','scripts/check-complete.sh','hooks/hooks.json','hooks/check-phase-approval.py','harness/runtime/engine.py','harness/contracts/canonical-contract.md','harness/contracts/execution.md'):
    assert (P/rel).is_file(),rel
hooks=json.loads((P/'hooks/hooks.json').read_text());assert 'PreToolUse' in hooks['hooks'];assert json.loads((P/'plugin.json').read_text())['extensions']['com.openai']['hooks']=='./hooks/hooks.json'
(E/'installed-references-check.json').write_text(json.dumps({'references_checked':len(references),'references':references,'hook_manifest_path_resolves':True,'hook_trust_changed':False,'boundary':'Deterministic hook suite and path resolution only; no live hook trust or interception claimed.','result':'PASS'},indent=2)+'\n');print(json.dumps({'bootstrap_operations':len(rows),'local_references':len(references),'result':'PASS'}))
