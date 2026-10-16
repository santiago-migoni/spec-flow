import json,sys,hashlib
from pathlib import Path
from datetime import datetime,timezone
c=json.loads(Path(sys.argv[1]).read_text());sys.path.insert(0,c['source_package_root'])
from harness.runtime.codex_adapter import NativeCodexAdapter,AdapterError
B=Path(c['disposable_base']);E=Path(c['evidence_directory']);owner=c['recovery_owner'];a=NativeCodexAdapter(B)
att=a.attest_session(owner,'orchestrator',parent_session=c['parent_session'],agent_path='/root/e7_owner_f8fa91d')
(E/'owner-preflight-independent.json').write_text(json.dumps(att,indent=2)+'\n')
probes=[]
for label,call,expected in [('owner-as-implementer',lambda:a.attest_session(owner,'implementer'),'host_profile_mismatch'),('missing-interrupt-capability',lambda:a.capabilities({'inventory_reference':'negative capability fixture; interrupt deliberately omitted','operations':{'spawn_agent':True,'wait_agent':True,'interrupt_agent':False,'list_agents':True},'probe_evidence':{'spawn_agent':'negative fixture','wait_agent':'negative fixture','list_agents':'negative fixture'}},owner),'native_capability_unavailable')]:
    try:call();raise AssertionError('Negative probe unexpectedly passed')
    except AdapterError as exc:
        assert exc.code==expected,(label,exc.code)
        probes.append({'probe':label,'expected':expected,'observed':exc.code,'message':str(exc)})
(E/'native-prerequisite-negative-probes.json').write_text(json.dumps({'checked_at':datetime.now(timezone.utc).isoformat(),'category':'Production adapter probes; no controller mutations or task credit','probes':probes,'result':'PASS'},indent=2)+'\n')
print('PASS: native owner profile and both negative prerequisite checks')
