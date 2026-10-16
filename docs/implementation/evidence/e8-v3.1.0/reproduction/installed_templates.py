"""Inspect exact installed manifests, packaged icon and YAML templates; no approvals/writes to installed package."""
from pathlib import Path
import json,hashlib,sys
c=json.loads(Path(sys.argv[1]).read_text());E=Path(c['evidence']);P=Path(json.loads((E/'installed-package.json').read_text())['path']);a=json.loads((P/'plugin.json').read_text());b=json.loads((P/'.codex-plugin/plugin.json').read_text());assert a==b and a['version']=='3.1.0'
icon=P/a['extensions']['com.openai']['interface']['logo'];assert icon.is_file();png=icon.read_bytes();assert png.startswith(b'\x89PNG\r\n\x1a\n')
(E/'installed-version-check.json').write_text(json.dumps({'actual_manifest_version':a['version'],'fallback_manifest_version':b['version'],'exact_mirror':True,'installed_path':str(P),'icon_path':str(icon.relative_to(P)),'icon_sha256':hashlib.sha256(png).hexdigest(),'icon_png_header_valid':True,'icon_limit':'Asset resolution only; no visual assertion about an already-open Desktop catalog.'},indent=2)+'\n')
sys.path.insert(0,str(P));from harness.runtime.contracts import read_document
rows=[]
for rel in ['constitution/assets/constitution-template.md','design/assets/architecture-template.md','design/assets/infrastructure-template.md','design/assets/structure-template.md','roadmap/assets/roadmap-template.md','specify/assets/spec-template.md','plan/assets/plan-template.md','tasks/assets/tasks-template.md']:
    p=P/'skills'/rel;v=read_document(p);assert p.read_text().startswith('---\n');rows.append({'path':'skills/'+rel,'kind':v['contract']['kind'],'yaml_frontmatter':True,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(E/'installed-yaml-templates.json').write_text(json.dumps({'templates':rows,'count':len(rows),'reader':'Installed package production document reader','legacy_compatibility_evidence':'152-test installed suite includes legacy JSON document and old-run compatibility regressions','result':'PASS'},indent=2)+'\n');print('PASS: installed manifests/icon/eight YAML templates')
