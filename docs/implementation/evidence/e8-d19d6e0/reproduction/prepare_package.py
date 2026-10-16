from pathlib import Path
import datetime,hashlib,io,json,subprocess,tarfile,tempfile,shutil,tomllib
R=Path.cwd();commit=subprocess.check_output(['git','rev-parse','d19d6e0^{commit}'],text=True).strip();assert not subprocess.check_output(['git','status','--porcelain'])
B=Path(tempfile.mkdtemp(prefix='spec-flow-e8-d19d6e0-',dir='/private/tmp'));E=R/'docs/implementation/evidence/e8-d19d6e0';E.mkdir(parents=True);(E/'reproduction').mkdir()
(E/'refs-before.txt').write_text(subprocess.check_output(['git','for-each-ref','--format=%(refname) %(objectname)','refs/tags','refs/remotes'],text=True))
raw=subprocess.check_output(['git','archive',commit,'plugins/spec-flow']);(B/'candidate.tar').write_bytes(raw);(B/'source').mkdir()
with tarfile.open(fileobj=io.BytesIO(raw)) as t:t.extractall(B/'source',filter='data')
source=B/'source/plugins/spec-flow';assert json.loads((source/'plugin.json').read_text())['version']=='3.0.0';name='spec-flow-e8-d19d6e0';market_name='spec-flow-e8-d19d6e0-01a13f8c';market=B/'marketplace with spaces';target=market/'plugins'/name;shutil.copytree(source,target)
for rel in ('plugin.json','.codex-plugin/plugin.json'):
    p=target/rel;data=json.loads(p.read_text());data['name']=name;data['extensions']['com.openai']['interface']['displayName']='Spec Flow E8 d19d6e0 Temporary';p.write_text(json.dumps(data,indent=2)+'\n')
mp=market/'.agents/plugins/marketplace.json';mp.parent.mkdir(parents=True);mp.write_text(json.dumps({'name':market_name,'plugins':[{'name':name,'source':{'source':'local','path':'./plugins/'+name},'policy':{'installation':'AVAILABLE','authentication':'ON_INSTALL'},'category':'Productivity'}]},indent=2)+'\n');shutil.copyfile(mp,E/'test-marketplace.json')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();files={p.relative_to(source).as_posix():sha(p) for p in sorted(source.rglob('*')) if p.is_file()};modified={p.relative_to(target).as_posix():sha(p) for p in sorted(target.rglob('*')) if p.is_file()}
assert [rel for rel in files if files[rel]!=modified[rel]]==['.codex-plugin/plugin.json','plugin.json'];assert len(files)==115
home=Path.home()/'.codex';stable=home/'plugins/cache/spec-flow/spec-flow';assert stable.is_dir();protected={p.relative_to(stable).as_posix():{'sha256':sha(p),'mode':p.stat().st_mode,'mtime_ns':p.stat().st_mtime_ns} for p in sorted(stable.rglob('*')) if p.is_file()}
conf=tomllib.loads((home/'config.toml').read_text());canonical=lambda v:hashlib.sha256(json.dumps(v,sort_keys=True,default=str).encode()).hexdigest()
before={'stable_root':str(stable),'stable_files':protected,'stable_setting':conf['plugins']['spec-flow@spec-flow'],'config_bytes_sha256':sha(home/'config.toml'),'config_semantic_sha256':canonical(conf),'hook_trust_sha256':canonical(conf.get('hooks')),'config_keys':list(conf),'plugin_keys':list(conf.get('plugins',{})),'marketplace_keys':list(conf.get('marketplaces',{}))}
(E/'protected-before.json').write_text(json.dumps(before,indent=2)+'\n')
for label,args in [('plugins-before',['codex','plugin','list']),('marketplaces-before',['codex','plugin','marketplace','list'])]:
    p=subprocess.run(args,text=True,capture_output=True);assert p.returncode==0;(E/(label+'.txt')).write_text(p.stdout);(E/(label+'.stderr')).write_text(p.stderr);assert market_name not in p.stdout and name+'@' not in p.stdout
c={'candidate':commit,'archive_sha256':hashlib.sha256(raw).hexdigest(),'prepared_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source':str(source),'base':str(B),'evidence':str(E),'marketplace':str(market),'marketplace_name':market_name,'name':name,'package':str(target),'selector':name+'@'+market_name,'candidate_files':files,'test_package_files':modified,'identity_only_changes':['name','extensions.com.openai.interface.displayName'],'unchanged_resources':113,'human_authorization':'Me parece bien. Comprueba la instalación aislada de v3.0.0 sobre el commit d19d6e0, usando una identidad de marketplace separada, sin reemplazar mi instalación actual y registrando las evidencias. Sin push, tag ni publicación todavía.'}
(B/'context.json').write_text(json.dumps(c,indent=2)+'\n');(E/'source-and-scope.json').write_text(json.dumps(c,indent=2)+'\n')
print(json.dumps({'context':str(B/'context.json'),'candidate':commit,'resources_unchanged':113,'protected_files':len(protected),'selector':c['selector']}))
