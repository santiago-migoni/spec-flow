from pathlib import Path
import gzip,hashlib,io,json,tarfile,shutil
R=Path.cwd();E=R/'docs/implementation/evidence/release-v3.0.0';c=json.loads((E/'package-comparison.json').read_text());P=Path(c['frozen_test_package'])
for name,count in [('runtime',127),('hooks',9)]:
    x=json.loads((E/(name+'.json')).read_text());assert x['exit']==0 and x['tests']==count and x['frozen_package_unchanged']
buffer=io.BytesIO()
with tarfile.open(fileobj=buffer,mode='w') as t:
    for p in sorted(P.rglob('*')):
        if p.is_file():t.add(p,arcname='spec-flow/'+p.relative_to(P).as_posix(),recursive=False)
archive=E/'spec-flow-v3.0.0.tar.gz';archive.write_bytes(gzip.compress(buffer.getvalue(),mtime=0))
with tarfile.open(archive) as t:
    files={m.name.removeprefix('spec-flow/'):hashlib.sha256(t.extractfile(m).read()).hexdigest() for m in t.getmembers() if m.isfile()}
assert files==c['package_files']
(E/'archive.json').write_text(json.dumps({'file':archive.name,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'files':len(files),'single_plugin_root':'spec-flow/','exact_frozen_package_match':True,'version':'3.0.0','status':'Local verified artifact; not published or installed'},indent=2)+'\n')
(R/'docs/implementation/release-v3.0.0.md').write_text('''# Preparación local — Spec-Flow v3.0.0

Fecha de preparación: 2026-10-16. Estado: **corte local preparado y verificado; publicación pendiente**. Autorización: actualizar ambos manifiestos, changelog y notas de release conservando E7/E8, sin push, tag ni publicación.

## Alcance del corte

- Ambos manifiestos equivalentes pasan de 2.0.0 a 3.0.0; no se cambia la identidad spec-flow ni la configuración OpenAI.
- CHANGELOG conserva Unreleased y agrega Release v3.0.0, con cambios incompatibles, mejoras, F-01/F-02/F-03 y validación. La fecha de publicación queda pendiente; la historia desde v2.0.0 permanece idéntica.
- [Notas de release y actualización](../releases/v3.0.0.md): reemplazo de architecture/infrastructure/structure por design, conservación de los tres documentos/contratos/aprobaciones y límites de evaluación.
- README y la guía AGENTS distinguen la versión preparada de su publicación. El marketplace estable conserva main.

El commit de preparación anterior es `238de52c923a271d584213bf122569b7ecdaf505`; las funcionalidades ya estaban implementadas en commits anteriores. Este corte se registra en un commit separado de los cambios funcionales.

## Trazabilidad de evaluación

| Elemento | Fuente y alcance |
| --- | --- |
| Base funcional | ef7897d83dedf9fe20c8bf82fb9e311f4cff8107 |
| E7 | [Informe](e7-ef7897d.md), registrado en 44b2685df26f094bfe29857b11fa59343a83f499; ejecución nativa aprobada en los escenarios documentados. |
| E8 | [Informe](e8-ef7897d.md), registrado en 238de52c923a271d584213bf122569b7ecdaf505; instalación aislada/cliente nuevo/arranque instalado aprobados en el alcance documentado. |
| Diferencia del paquete | 115 archivos: 113 idénticos a ef7897d, solo version cambia en los dos manifiestos. |
| Preservación | Informes, archivos de evidencia y sus SHA256SUMS originales comprobados íntegros y sin modificaciones. |

E7/E8 evaluaron ef7897d con manifiestos 2.0.0. Este corte conserva esos hechos y demuestra igualdad de su contenido funcional; no los renombra como ejecuciones del paquete v3.0.0. No se repitió E7 nativa ni se instaló v3.0.0. Una comprobación final de instalación aislada con la nueva versión queda pendiente antes de publicar.

## Verificación del corte local

| Comprobación | Resultado |
| --- | --- |
| Comparación exacta con candidato | PASS: 113 recursos idénticos, solo campo version de dos manifiestos distinto. |
| Manifiestos y marketplace | PASS: ambos 3.0.0 y equivalentes; marketplace main sin cambios. |
| Suite en copia congelada v3.0.0, ruta con espacios | 127 pruebas del plugin PASS. |
| Hook desde esa copia | 9 pruebas PASS; no demuestra activación confiable/interceptación en vivo. |
| Paquete tras suites | Sin cambios, 115 hashes conservados. |
| Artefacto local | spec-flow-v3.0.0.tar.gz: una raíz de plugin, 115 archivos idénticos a la copia verificada. |
| Referencias Git protegidas | Tags y referencias remotas sin cambios; v3.0.0 no creado como tag. |

[Comparación y autorización](evidence/release-v3.0.0/package-comparison.json), [suite](evidence/release-v3.0.0/runtime.json), [hook](evidence/release-v3.0.0/hooks.json), [artefacto y hash](evidence/release-v3.0.0/archive.json) e [integridad final](evidence/release-v3.0.0/final-check.json).

## Pendiente de publicación

El repositorio contiene un corte local reviewable. Antes de una publicación autorizada: confirmar la instalación final de v3.0.0 con identidad separada, fijar el commit verificado y la fecha/estado de publicación aplicables, y publicar por el flujo autorizado. Si cambia contenido funcional, reevaluar lo afectado antes de reutilizar la evidencia. Push, tag y release permanecen pendientes; instalación de usuario y migración de proyectos son hitos separados.
''')
(E/'README.md').write_text('''# Corte local v3.0.0 — evidencia

Corte de metadatos y documentación, separado de cambios funcionales. Base funcional ef7897d; E7/E8 originales preservados. Sin push/tag/publicación ni instalación de v3.0.0.

- [Registro de preparación](../../release-v3.0.0.md) y [notas](../../../releases/v3.0.0.md).
- package-comparison.json: 115 hashes, dos cambios exclusivos de version, 113 archivos idénticos; autorización y referencias originales.
- runtime.* y hooks.*: suites 127 + 9 en una copia congelada v3.0.0; no confundir con E7 nativa ni E8 instalada.
- spec-flow-v3.0.0.tar.gz y archive.json: artefacto local verificado, no publicado.
- refs-before.txt: referencias de tags/remotos al inicio.
- final-check.json y SHA256SUMS: integridad final.
- reproduction/: comprobaciones usadas; necesitan un checkout limpio de origen para repetir preparación y no deben sobrescribir la evidencia comprometida.

Una instalación aislada de la versión final queda pendiente antes de publicación. Los informes/evidencias de E7 y E8 continúan referidos a ef7897d, con manifiestos 2.0.0.
''')
print('Release notes, provenance record and verified local 3.0.0 package ready')
