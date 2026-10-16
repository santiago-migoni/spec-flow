from pathlib import Path
import datetime,hashlib,json,subprocess,tomllib
R=Path.cwd();E=R/'docs/implementation/evidence/publication-v3.0.0';assert not subprocess.check_output(['git','status','--porcelain']);assert subprocess.check_output(['git','branch','--show-current'],text=True).strip()=='main';E.mkdir(parents=True);(E/'reproduction').mkdir()
sha=lambda b:hashlib.sha256(b).hexdigest();canonical=lambda x:sha(json.dumps(x,sort_keys=True,default=str).encode())
remote=subprocess.check_output(['git','ls-remote','origin','refs/heads/main','refs/tags/v3.0.0'],text=True);assert 'refs/tags/v3.0.0' not in remote;remote_sha=remote.split()[0];subprocess.run(['git','merge-base','--is-ancestor',remote_sha,'HEAD'],check=True)
config=Path.home()/'.codex/config.toml';cfg=tomllib.loads(config.read_text());stable=Path.home()/'.codex/plugins/cache/spec-flow/spec-flow';protected={p.relative_to(stable).as_posix():{'sha256':sha(p.read_bytes()),'mode':p.stat().st_mode,'mtime_ns':p.stat().st_mtime_ns} for p in stable.rglob('*') if p.is_file()}
(E/'protected-before.json').write_text(json.dumps({'root':str(stable),'files':protected,'config_bytes_sha256':sha(config.read_bytes()),'config_semantic_sha256':canonical(cfg),'hook_trust_sha256':canonical(cfg.get('hooks')),'stable_setting':cfg['plugins']['spec-flow@spec-flow']},indent=2)+'\n')
base=json.loads((R/'docs/implementation/evidence/e8-d19d6e0/source-and-scope.json').read_text());P=R/'plugins/spec-flow';actual={p.relative_to(P).as_posix():sha(p.read_bytes()) for p in P.rglob('*') if p.is_file()};assert actual==base['candidate_files'];assert json.loads((P/'plugin.json').read_text())['version']=='3.0.0';assert (P/'plugin.json').read_bytes()==(P/'.codex-plugin/plugin.json').read_bytes()
for name in ('e7-ef7897d','e8-ef7897d','release-v3.0.0','e8-d19d6e0'):
    d=E.parent/name
    for line in (d/'SHA256SUMS').read_text().splitlines():
        h,rel=line.split('  ',1);assert sha((d/rel).read_bytes())==h,(name,rel)
    for p in d.rglob('*'):
        if p.is_file():assert p.read_bytes()==subprocess.check_output(['git','show','HEAD:'+str(p.relative_to(R))]),str(p)
market=json.loads((R/'.agents/plugins/marketplace.json').read_text());assert market['plugins'][0]['source']['ref']=='main'
archive=R/'docs/implementation/evidence/release-v3.0.0/spec-flow-v3.0.0.tar.gz';expected=json.loads((archive.parent/'archive.json').read_text());assert sha(archive.read_bytes())==expected['sha256']
context={'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'authorization':'Me parece bien. Publica v3.0.0, haciendo push, creando el tag y la release de GitHub, conservando la trazabilidad de E7/E8 y sin actualizar mi instalación ni migrar proyectos todavía.','repository':'santiago-migoni/spec-flow','remote_main_before':remote_sha,'local_head_before':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'functional_E7_source':'ef7897d83dedf9fe20c8bf82fb9e311f4cff8107','final_installed_E8_source':base['candidate'],'package_files':actual,'package_archive':str(archive),'package_archive_sha256':expected['sha256'],'stable_files_protected':len(protected),'no_plugin_or_migration_operations_authorized':True}
(E/'preflight.json').write_text(json.dumps(context,indent=2)+'\n')
p=R/'CHANGELOG.md';s=p.read_text();old='Status: Prepared locally on 2026-10-16; not published. Publication date pending.';assert old in s;p.write_text(s.replace(old,'Release date: 2026-10-16.\nPrepared locally and verified before publication; E7/E8 source commits are recorded below.',1))
p=R/'docs/releases/v3.0.0.md';s=p.read_text();old='Status: local release cut prepared on 2026-10-16. Not yet published; publication date pending. These notes are ready for review before a separately authorized tag, push, and GitHub release.';assert old in s;s=s.replace(old,'Release date: 2026-10-16. Local preparation and final isolated installation are complete. Publication of this version through main, the v3.0.0 tag, and GitHub release is explicitly authorized; installation of the user copy and project migration remain separate.',1);s=s.replace('Publication remains pending.','Publication authorization covers the verified package; installation/update and migration remain separate.',1);old="The isolated test installation has been removed and the user's stable installation remains unchanged. This release has not been tagged, pushed, or published, and no existing project was migrated. The stable marketplace source remains `main`. Publication, installation/update, and project migration require their own applicable authorization and checks.";new="The isolated test installation has been removed and the user's stable installation remains unchanged. Publication uses the stable marketplace source on `main` and the `v3.0.0` tag, preserving the original evaluation commits and reports. Installation/update and project migration remain separately authorized actions; publication does not perform them. The post-publication receipt records the actual GitHub release, tag target and asset verification.";assert old in s;p.write_text(s.replace(old,new,1))
p=R/'README.md';s=p.read_text().replace('Local release cut **v3.0.0** is prepared;','**v3.0.0** release notes are ready;',1).replace('Publication is pending.','Publication is authorized; installation/update and project migration remain separate actions.',1);p.write_text(s)
p=R/'AGENTS.md';s=p.read_text();old='The local package version is `3.0.0`, prepared as a local release cut; publication is a separate authorized step.';new='The current package version is `3.0.0`. Publication, user installation/update, and project migration remain separately authorized steps.';assert old in s;p.write_text(s.replace(old,new,1))
(E/'README.md').write_text('''# Publication v3.0.0

The user explicitly authorized push, tag and GitHub release, preserving E7/E8 traceability and excluding user installation/update or project migration.

- preflight.json: authority, starting refs, exact package hashes and validated archive.
- protected-before.json: original installation/cache and configuration fingerprints; no private config copied.
- operations.jsonl: actual tag/push/release operations and outcomes, once executed.
- publication-receipt.json: verified remote tag target, release, downloaded assets and installation preservation, once available.
- SHA256SUMS: local evidence integrity.

The package remains byte-identical to d19d6e0. Native E7 remains tied to ef7897d and final isolated v3.0.0 installation to d19d6e0. No installation or migration operation is part of this publication.
''')
print(json.dumps({'remote_main':remote_sha,'package_files_verified':len(actual),'protected_stable_files':len(protected),'archive_sha256':expected['sha256']}))
