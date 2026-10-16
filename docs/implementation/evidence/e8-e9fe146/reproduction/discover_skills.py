import json,subprocess,selectors,time,sys
from pathlib import Path
c=json.loads(Path(sys.argv[1]).read_text());E=Path(c['evidence']);B=Path(c['base']);scratch=B/'fresh-client-project';scratch.mkdir(exist_ok=True);subprocess.run(['git','init','-q',str(scratch)],check=True)
logs=(E/'discovery-server.stderr').open('w');p=subprocess.Popen(['codex','app-server','--listen','stdio://'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=logs,text=True,bufsize=1);sel=selectors.DefaultSelector();sel.register(p.stdout,selectors.EVENT_READ)
def request(n,method,params):
    p.stdin.write(json.dumps({'id':n,'method':method,'params':params})+'\n');p.stdin.flush();end=time.monotonic()+40
    while time.monotonic()<end:
        if not sel.select(1):continue
        line=p.stdout.readline()
        if not line:raise RuntimeError('app-server closed')
        row=json.loads(line)
        if row.get('id')==n:return row
    raise TimeoutError(method)
try:
    init=request(1,'initialize',{'clientInfo':{'name':'spec-flow-e8-e9fe146','version':'1.0.0'}});assert 'result' in init
    p.stdin.write(json.dumps({'method':'initialized','params':{}})+'\n');p.stdin.flush()
    result=request(2,'skills/list',{'cwds':[str(scratch)],'forceReload':True});assert 'error' not in result,result
    rows=result['result']['data'];selected=[s for row in rows for s in row['skills'] if s['name'].startswith(c['name']+':')];assert all(not row.get('errors') for row in rows),rows
    expected=sorted(x.parent.name for x in (Path(c['package'])/'skills').glob('*/SKILL.md'));assert sorted(s['name'].split(':',1)[1] for s in selected)==expected,selected;assert all(s['enabled'] for s in selected)
    P=Path(json.loads((E/'installed-package.json').read_text())['path']);assert all(Path(s['path']).is_relative_to(P) for s in selected)
    (E/'discovered-skills.json').write_text(json.dumps({'server_initialize':init,'request':{'method':'skills/list','params':{'cwds':[str(scratch)],'forceReload':True}},'selected_skills':selected,'response_error':None,'cwd_errors':[row.get('errors') for row in rows],'expected_count':14,'enabled_count':len(selected),'result':'PASS','boundary':'Fresh app-server client discovery, not a claim that an already-open Desktop chat refreshed its injected catalog.'},indent=2)+'\n')
    print(json.dumps({'fresh_client_enabled_skills':len(selected),'installed_root':str(P),'scratch':str(scratch)}))
finally:
    p.terminate();p.wait(timeout=10);logs.close()
