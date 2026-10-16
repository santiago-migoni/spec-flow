"""Negative probes use the production adapter and a real owner; no task credit."""
import json,sys
from pathlib import Path
from datetime import datetime,timezone
c=json.loads(Path(sys.argv[1]).read_text());sys.path.insert(0,c['source_package_root'])
from harness.runtime.codex_adapter import NativeCodexAdapter,AdapterError
E=Path(c['evidence_directory']);sessions=json.loads((E/'native/session-context.json').read_text());owner=next(s for s in sessions if s['agent_path']=='/root/e7_native_owner');a=NativeCodexAdapter(Path(c['disposable_base']));a.configure_profiles(c['profiles'],require_catalog=True)
att=a.attest_session(owner['session_id'],'orchestrator',parent_session=owner['parent_session'],agent_path=owner['agent_path'])
(E/'owner-preflight-independent.json').write_text(json.dumps(att,indent=2)+'\n')
report={'inventory_reference':c['host_model_inventory_reference'],'operations':{n:True for n in a.OPERATIONS},'probe_evidence':{n:'deliberate production prerequisite probe; not task implementation' for n in a.OPERATIONS},'model_catalog_reference':c['host_model_inventory_reference'],'model_catalog':[{'id':'gpt-6.1-sol','reasoning_efforts':['low','medium']},{'id':'gpt-6-luna','reasoning_efforts':['high']}]}
probes=[]
def check(label,fn,code):
    try:fn();raise AssertionError('negative probe unexpectedly passed')
    except AdapterError as exc:
        assert exc.code==code,(label,exc.code)
        probes.append({'probe':label,'expected':code,'observed':exc.code,'message':str(exc)})
check('owner cannot act as implementer',lambda:a.attest_session(owner['session_id'],'implementer'),'host_profile_mismatch')
r=json.loads(json.dumps(report));r['operations']['interrupt_agent']=False
check('missing interrupt capability',lambda:a.capabilities(r,owner['session_id']),'native_capability_unavailable')
r=json.loads(json.dumps(report));r.pop('model_catalog_reference')
check('missing catalog reference',lambda:a.capabilities(r,owner['session_id']),'model_catalog_required')
r=json.loads(json.dumps(report));r['model_catalog'][1]['reasoning_efforts']=['low']
check('configured implementer effort unavailable',lambda:a.capabilities(r,owner['session_id']),'model_unavailable')
(E/'native-prerequisite-negative-probes.json').write_text(json.dumps({'checked_at':datetime.now(timezone.utc).isoformat(),'category':'Production read-only adapter probes; deliberately malformed inventories; no mutations or task credit','probes':probes,'result':'PASS'},indent=2)+'\n');print('PASS: real owner attested and four negative prerequisites rejected')
