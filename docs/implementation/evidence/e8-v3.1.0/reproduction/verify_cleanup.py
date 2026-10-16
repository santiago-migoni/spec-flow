import json,hashlib,tomllib,sys,gzip
from pathlib import Path
c=json.loads(Path(sys.argv[1]).read_text());E=Path(c['evidence']);b=json.loads((E/'protected-before.json').read_text());home=Path.home()/'.codex';conf=tomllib.loads((home/'config.toml').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();canonical=lambda x:hashlib.sha256(json.dumps(x,sort_keys=True,default=str).encode()).hexdigest()
assert canonical(conf)==b['config_semantic_sha256'];assert canonical(conf.get('hooks'))==b['hook_trust_sha256'];assert conf['plugins']['spec-flow@spec-flow']==b['stable_setting'];assert c['selector'] not in conf['plugins'] and c['marketplace_name'] not in conf['marketplaces'];assert not (home/'plugins/cache'/c['marketplace_name']/c['name']).exists()
stable=Path(b['stable_root']);now={p.relative_to(stable).as_posix():{'sha256':sha(p),'mode':p.stat().st_mode,'mtime_ns':p.stat().st_mtime_ns} for p in sorted(stable.rglob('*')) if p.is_file()};assert now==b['stable_files']
for name in ('plugins','marketplaces'):
    read=lambda path:path.read_text() if path.exists() else gzip.decompress(Path(str(path)+'.gz').read_bytes()).decode()
    before=read(E/(name+'-before.txt'));after=read(E/(name+'-after.txt'));assert ' '.join(before.split())==' '.join(after.split());assert c['marketplace_name'] not in after
record={'original_installation':b['stable_root'],'original_files_unchanged':len(now),'original_file_modes_and_mtimes_unchanged':True,'original_plugin_setting_unchanged':True,'configuration_semantically_identical':True,'configuration_bytes_identical':sha(home/'config.toml')==b['config_bytes_sha256'],'hook_trust_unchanged':True,'plugins_list_identical_normalized':True,'marketplaces_list_identical_normalized':True,'temporary_plugin_and_marketplace_removed':True,'temporary_installed_cache_removed':True,'result':'PASS'}
(E/'cleanup-check.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record))
