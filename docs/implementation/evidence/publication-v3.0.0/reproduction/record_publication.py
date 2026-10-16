from pathlib import Path
import datetime,hashlib,json,re,subprocess
R=Path.cwd();E=R/'docs/implementation/evidence/publication-v3.0.0';receipt=json.loads((E/'publication-receipt.json').read_text());assert receipt['result']=='PASS';url=receipt['url'];release_sha=receipt['release_commit'];day=receipt['published_at'][:10]
p=R/'docs/releases/v3.0.0.md';s=p.read_text();old='Release date: 2026-10-16. Local preparation and final isolated installation are complete. Publication of this version through main, the v3.0.0 tag, and GitHub release is explicitly authorized; installation of the user copy and project migration remain separate.';new=f'Release date: {day}. **[Published on GitHub]({url})**, tag v3.0.0 at `{release_sha}`. Original E7/E8 sources and final installed-package verification remain recorded below; user installation/update and project migration are separate actions.';assert old in s;s=s.replace(old,new,1);s=s.replace('Publication authorization covers the verified package; installation/update and migration remain separate.','The verified package is published; installation/update and migration remain separate.',1);s=s.replace('The post-publication receipt records the actual GitHub release, tag target and asset verification.','The [post-publication receipt](../implementation/publication-v3.0.0.md) records the actual GitHub release, tag target, downloaded-asset verification and unchanged user installation.',1);p.write_text(s)
p=R/'README.md';s=p.read_text().replace('**v3.0.0** release notes are ready;',f'**[v3.0.0]({url}) is published**;',1).replace('Publication is authorized; installation/update and project migration remain separate actions.','The [publication receipt](docs/implementation/publication-v3.0.0.md) verifies the tag and downloaded package. Installation/update and project migration remain separate actions.',1);p.write_text(s)
(R/'docs/implementation/publication-v3.0.0.md').write_text(f'''# Publicación — Spec-Flow v3.0.0

**Publicada y verificada:** [{url}]({url}). Fecha real GitHub: `{receipt['published_at']}`. Release estable, no draft ni prerelease, marcada Latest.

El usuario autorizó push, tag y release, conservando E7/E8 y excluyendo actualización de su instalación y migración de proyectos. [Autorización y preflight](evidence/publication-v3.0.0/preflight.json).

| Elemento | Resultado verificado |
| --- | --- |
| Repositorio | santiago-migoni/spec-flow |
| Commit de release | {release_sha} |
| Tag anotado | v3.0.0 |
| Objeto de tag | {receipt['annotated_tag_object']} |
| Main al publicar | {receipt['remote_main_at_publication']} |
| Release | [{receipt['release_id']}]({url}) |
| Artefacto | spec-flow-v3.0.0.tar.gz y SHA256SUMS |
| SHA-256 del paquete descargado | {receipt['downloaded_package_sha256']} |
| Archivos descargados cotejados | 115, idénticos al paquete de d19d6e0 |

Se verificó avance fast-forward desde el main remoto anterior y se enviaron main y tag en una operación atómica, sin force ni reescritura. La release se creó sobre el tag remoto verificado, con notas que fijan los enlaces de evidencia al commit de release. Se descargaron ambos assets desde GitHub y se comprobaron hash, tamaños, contenido del checksum y los 115 archivos del paquete. Los digests informados por GitHub también coincidieron cuando estaban presentes.

## Trazabilidad conservada

- [E7 nativa](e7-ef7897d.md): ef7897d83dedf9fe20c8bf82fb9e311f4cff8107, escenarios documentados y correcciones F-01/F-02/F-03.
- [E8 previa](e8-ef7897d.md): mismo candidato funcional, manifiestos 2.0.0, sin reinterpretar su alcance.
- [Corte local](release-v3.0.0.md): d19d6e0be75702907442412f9227688cbc835fba, solo version de ambos manifiestos frente a la base funcional.
- [Instalación final v3.0.0](e8-d19d6e0.md): d19d6e0, 14 skills, 127 tests del plugin y 9 del hook desde el cache instalado; smoke y protección de instalación/configuración.

El commit de release conserva esos informes y sus archivos de evidencia originales íntegros. Los 115 archivos del paquete son byte-idénticos a d19d6e0, por lo que esta publicación reutiliza las verificaciones ya registradas sin atribuirles una ejecución nueva. Los cambios de publicación son documentación/metadatos externos al paquete. El comprobante posterior se registra en un commit documental adicional en main; el tag conserva permanentemente el commit de release indicado arriba.

## Instalación y proyectos

Se volvieron a comprobar los 114 archivos de la instalación estable existente, con bytes, permisos y mtime idénticos; setting del plugin, configuración completa y confianza de hooks sin cambios. No se ejecutaron operaciones de instalación/actualización, inicialización ni migración de proyectos en esta publicación. La disponibilidad de v3.0.0 en el marketplace no implica haberla instalado en la copia del usuario.

## Evidencias y límites

[Comprobante estructurado](evidence/publication-v3.0.0/publication-receipt.json), [operaciones](evidence/publication-v3.0.0/operations.jsonl), [destino](evidence/publication-v3.0.0/publication-target.json) e [inventario de integridad](evidence/publication-v3.0.0/SHA256SUMS).

Las pruebas conservan los límites de sus informes: host/escenarios observados, sin promesas de ahorro, refresco automático de chats ni interceptación universal/confiable del hook. Publicación, instalación del usuario y migración permanecen como hechos separados.
''')
for name in ('harness-progress.md','harness-distribution.md'):
    p=R/'docs/implementation'/name;s=p.read_text();i=s.index('\n');s=s[:i]+f'\n\nEstado actual: **[v3.0.0 publicada]({url})**, verificada el {day}; tag en `{release_sha[:7]}`. [Comprobante de publicación](publication-v3.0.0.md), con E7/E8 originales preservados y paquete descargado verificado. Instalación del usuario y configuración intactas; no se migraron proyectos. Los registros siguientes conservan los estados históricos de preparación y evaluación anteriores a la publicación.\n'+s[i:];p.write_text(s)
# GitHub release copy uses immutable commit-pinned local-document links.
notes_path=R/'docs/releases/v3.0.0.md';notes=notes_path.read_text()
def absolute(m):
    label,target=m[1],m[2]
    if '://' in target or target.startswith('#'):return m[0]
    resolved=(notes_path.parent/target.split('#')[0]).resolve().relative_to(R).as_posix()
    # Publication receipt is created after the release tag, so it will be pinned
    # to its own documentary commit after that commit has been pushed.
    if resolved=='docs/implementation/publication-v3.0.0.md':return '['+label+'](https://github.com/santiago-migoni/spec-flow/blob/main/'+resolved+')'
    return '['+label+'](https://github.com/santiago-migoni/spec-flow/blob/'+release_sha+'/'+resolved+')'
notes=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',absolute,notes)
notes+='\n\n## Download verification\n\nPackage SHA-256: `'+receipt['downloaded_package_sha256']+'`. All 115 downloaded package files match d19d6e0; the user installation/configuration remains unchanged.\n'
(E/'initial-github-release-notes.md').write_bytes((E/'github-release-notes.md').read_bytes());(E/'github-release-notes.md').write_text(notes)
result=subprocess.run(['gh','release','edit','v3.0.0','--repo','santiago-migoni/spec-flow','--notes-file',str(E/'github-release-notes.md')],capture_output=True,text=True)
with (E/'operations.jsonl').open('a') as f:f.write(json.dumps({'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'step':'finalize-release-notes','argv':['gh','release','edit','v3.0.0','--repo','santiago-migoni/spec-flow','--notes-file',str(E/'github-release-notes.md')],'exit':result.returncode,'stdout':result.stdout,'stderr':result.stderr})+'\n')
assert result.returncode==0,result.stderr
actual=json.loads(subprocess.check_output(['gh','api','repos/santiago-migoni/spec-flow/releases/tags/v3.0.0'],text=True));assert actual['body']==notes and actual['id']==receipt['release_id'];receipt['final_notes_sha256']=hashlib.sha256(notes.encode()).hexdigest();receipt['final_notes_verified_on_github']=True;(E/'publication-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'publication_record':str(R/'docs/implementation/publication-v3.0.0.md'),'notes_verified':True,'published_release':url}))
