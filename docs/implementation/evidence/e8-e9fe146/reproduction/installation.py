"""Use supported CLI operations on the uniquely identified E8 marketplace only."""
import datetime,json,subprocess,sys,hashlib
from pathlib import Path
c=json.loads(Path(sys.argv[1]).read_text());E=Path(c['evidence']);assert c['selector']=='spec-flow-e8-e9fe146@spec-flow-e8-e9fe146-01a13f8c'
mode=sys.argv[2]
operations={'install':[('market-add',['codex','plugin','marketplace','add',c['marketplace']]),('plugin-add',['codex','plugin','add',c['selector']]),('installed-list',['codex','plugin','list','--marketplace',c['marketplace_name']])],'cleanup':[('plugin-remove',['codex','plugin','remove',c['selector']]),('market-remove',['codex','plugin','marketplace','remove',c['marketplace_name']]),('plugins-after',['codex','plugin','list']),('marketplaces-after',['codex','plugin','marketplace','list'])]}[mode]
for label,argv in operations:
    p=subprocess.run(argv,text=True,capture_output=True);(E/(label+'.txt')).write_text(p.stdout);(E/(label+'.stderr')).write_text(p.stderr)
    row={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'step':label,'argv':argv,'exit':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
    with (E/'installation-operations.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
    print(label,p.returncode,flush=True)
    if p.returncode:raise SystemExit(p.returncode)
if mode=='install':
    matches=list((Path.home()/'.codex/plugins/cache'/c['marketplace_name']/c['name']).glob('*'))
    matches=[p for p in matches if (p/'plugin.json').is_file()];assert len(matches)==1,matches
    installed=matches[0];files={p.relative_to(installed).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in installed.rglob('*') if p.is_file()}
    assert files==c['test_package_files']
    (E/'installed-package.json').write_text(json.dumps({'path':str(installed),'files':files,'count':len(files),'exact_test_package_match':True,'unchanged_candidate_resources':137},indent=2)+'\n')
    print('Installed exact test package:',installed,flush=True)
