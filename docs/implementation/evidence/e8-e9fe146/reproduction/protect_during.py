import copy,hashlib,json,sys,tomllib
from pathlib import Path
c=json.loads(Path(sys.argv[1]).read_text());E=Path(c['evidence']);b=json.loads((E/'protected-before.json').read_text());cfg=tomllib.loads((Path.home()/'.codex/config.toml').read_text());h=lambda x:hashlib.sha256(json.dumps(x,sort_keys=True,default=str).encode()).hexdigest();normalized=copy.deepcopy(cfg);normalized['plugins'].pop(c['selector'],None);normalized['marketplaces'].pop(c['marketplace_name'],None)
assert h(normalized)==b['config_semantic_sha256'] and h(cfg.get('hooks'))==b['hook_trust_sha256']
stable=Path(b['stable_root']);now={p.relative_to(stable).as_posix():{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'mode':p.stat().st_mode,'mtime_ns':p.stat().st_mtime_ns} for p in stable.rglob('*') if p.is_file()};assert now==b['stable_files']
(E/'protected-during.json').write_text(json.dumps({'original_installation_files_unchanged':len(now),'all_other_config_semantics_unchanged':True,'only_added_entries':[c['selector'],c['marketplace_name']],'hook_trust_unchanged':True,'result':'PASS'},indent=2)+'\n');print('PASS: stable installation and all unrelated configuration unchanged')
