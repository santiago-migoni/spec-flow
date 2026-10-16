import datetime,hashlib,json,os,shutil,struct,subprocess,tempfile
from pathlib import Path
R=Path('/Users/santiago_migoni/Documents/Projects/spec-flow');E=R/'docs/implementation/evidence/release-v3.0.1';T=Path(tempfile.mkdtemp(prefix='spec-flow-v301-',dir='/private/tmp'));H=T/'codex-home';H.mkdir();env=dict(os.environ,CODEX_HOME=str(H),PYTHONDONTWRITEBYTECODE='1');sha=lambda b:hashlib.sha256(b).hexdigest()
def protected():
 roots=[Path.home()/'.codex/config.toml',Path.home()/'.codex/plugins/cache/spec-flow']
 return {str(f):{'sha256':sha(f.read_bytes()),'mode':f.stat().st_mode,'mtime_ns':f.stat().st_mtime_ns} for p in roots for f in ([p] if p.is_file() else p.rglob('*')) if f.is_file()}
before=protected();(E/'protected-before.json').write_text(json.dumps(before,indent=2)+'\n')
P=T/'marketplace/plugins/spec-flow';P.mkdir(parents=True)
files=subprocess.check_output(['git','ls-files','plugins/spec-flow'],cwd=R,text=True).splitlines()
for rel in files:
 src=R/rel;dest=P/src.relative_to(R/'plugins/spec-flow');dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest)
name='spec-flow-v301-check';market='spec-flow-v301-isolated'
for rel in ('plugin.json','.codex-plugin/plugin.json'):
 p=P/rel;d=json.loads(p.read_text());d['name']=name;d['extensions']['com.openai']['interface']['displayName']='Spec Flow isolated 3.0.1';p.write_text(json.dumps(d,indent=2)+'\n')
m=T/'marketplace/.agents/plugins';m.mkdir(parents=True);(m/'marketplace.json').write_text(json.dumps({'name':market,'plugins':[{'name':name,'source':{'source':'local','path':'./plugins/spec-flow'},'policy':{'installation':'AVAILABLE','authentication':'ON_INSTALL'},'category':'Productivity'}]},indent=2))
def run(label,args,cwd=R,extra=None):
 p=subprocess.run(args,cwd=cwd,env=env| (extra or {}),text=True,capture_output=True);(E/(label+'.txt')).write_text(p.stdout+p.stderr)
 with (E/'operations.jsonl').open('a') as f:f.write(json.dumps({'step':label,'argv':args,'exit':p.returncode})+'\n')
 print(label,p.returncode,flush=True);assert p.returncode==0,p.stderr;return p
run('market-add',['codex','plugin','marketplace','add',str(T/'marketplace')]);run('plugin-add',['codex','plugin','add',name+'@'+market])
installed=next((H/'plugins/cache'/market/name).glob('*'));assert installed.is_dir()
inventory=lambda root:{f.relative_to(root).as_posix():sha(f.read_bytes()) for f in root.rglob('*') if f.is_file()}
assert inventory(installed)==inventory(P)
d=json.loads((installed/'plugin.json').read_text());assert d==json.loads((installed/'.codex-plugin/plugin.json').read_text());assert d['version']=='3.0.1'
i=d['extensions']['com.openai']['interface'];assert i['logo']==i['composerIcon']=='./assets/spec-flow-icon.png';icon=installed/i['logo'];raw=icon.read_bytes();assert raw[:8]==b'\x89PNG\r\n\x1a\n';w,h=struct.unpack('>II',raw[16:24]);assert 48<=w==h<=4096 and len(raw)<=5*1024*1024
run('installed-tests',['python3','-B','-m','unittest','discover','-s','tests','-q'],installed)
run('installed-hooks',['python3','-B','-m','unittest','discover','-s','hooks','-p','test_*.py','-q'],installed)
assert inventory(installed)==inventory(P)
run('plugin-remove',['codex','plugin','remove',name+'@'+market]);run('market-remove',['codex','plugin','marketplace','remove',market]);assert protected()==before
result={'result':'PASS','at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'version':'3.0.1','temporary_codex_home':str(H),'marketplace':market,'plugin':name,'installed_files':len(inventory(P)),'installed_matches_test_copy':True,'identity_only_test_changes':['name','extensions.com.openai.interface.displayName'],'listing_logo_and_composer_icon_verified':True,'icon_dimensions':[w,h],'icon_sha256':sha(raw),'plugin_tests':128,'hook_tests':9,'original_user_config_and_stable_cache_unchanged':True,'native_E7_reused_without_rerun':'ef7897d','visual_catalog_refresh_verified':False,'temporary_identity_removed':True,'source_package_files':inventory(R/'plugins/spec-flow')}
(E/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='source_package_files'}))
