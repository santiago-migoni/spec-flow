from pathlib import Path
import json
R=Path.cwd();E=R/'docs/implementation/evidence/e8-d19d6e0';c=json.loads((E/'source-and-scope.json').read_text());assert json.loads((E/'cleanup-check.json').read_text())['configuration_bytes_identical']
(R/'docs/implementation/e8-d19d6e0.md').write_text(f'''# Instalación aislada final — Spec-Flow v3.0.0

Fecha: 2026-10-16. **APROBADA en el alcance de instalación aislada, descubrimiento fresco y arranque instalado.** Fuente exacta: `{c['candidate']}`. La instalación actual se conservó intacta y el entorno temporal se retiró. Sin push, tag, publicación ni migración de proyectos existentes.

## Fuente y aislamiento

El usuario autorizó comprobar v3.0.0 sobre d19d6e0 con identidad de marketplace separada y registro de evidencias. [Autorización e inventarios](evidence/e8-d19d6e0/source-and-scope.json).

Se exportaron 115 archivos directamente desde Git, archivo SHA-256 `{c['archive_sha256']}`. La copia de prueba cambió únicamente name y extensions.com.openai.interface.displayName de ambos manifiestos. Su versión siguió siendo **3.0.0**. Los otros **113 recursos** permanecieron idénticos a d19d6e0; los 115 archivos instalados coincidieron exactamente con la copia de prueba.

| Elemento | Identidad |
| --- | --- |
| Plugin estable protegido | spec-flow@spec-flow; cache existente 2.0.0 |
| Plugin temporal | {c['name']} |
| Marketplace temporal | {c['marketplace_name']} |
| Cache instalado y verificado | ~/.codex/plugins/cache/{c['marketplace_name']}/{c['name']}/3.0.0 |
| Fuente del marketplace | Copia local del commit exacto, ruta con espacios |

[Manifiestos instalados verificados](evidence/e8-d19d6e0/installed-version-check.json) e [inventario instalado](evidence/e8-d19d6e0/installed-package.json). La comprobación protege todos los archivos/versiones bajo el cache estable, sin sustituirlo.

## Pruebas y resultados

| Prueba | Resultado | Evidencia |
| --- | --- | --- |
| Registro e instalación | Marketplace/plugin temporales instalados y listados por CLI soportado; exit0 | [Operaciones](evidence/e8-d19d6e0/installation-operations.jsonl) |
| Suite desde el cache 3.0.0 instalado | 127 pruebas PASS; archivos del paquete sin cambios | [Runtime](evidence/e8-d19d6e0/installed-runtime.json), [salida](evidence/e8-d19d6e0/installed-runtime.txt) |
| Hook desde ese cache | 9 pruebas PASS; archivos del paquete sin cambios | [Hook](evidence/e8-d19d6e0/installed-hooks.json), [salida](evidence/e8-d19d6e0/installed-hooks.txt) |
| Cliente nuevo app-server | 14 skills habilitadas, sin errores; todos los paths pertenecen al cache temporal 3.0.0 | [Descubrimiento](evidence/e8-d19d6e0/discovered-skills.json) |
| Arranque desde bootstrap descubierto | Ocho operaciones: status inicial, initialize idempotente, status sin runs, gate constitution ready; tres kinds inexistentes rechazados | [Smoke](evidence/e8-d19d6e0/installed-bootstrap-check.json), [operaciones](evidence/e8-d19d6e0/installed-bootstrap-operations.json) |
| Recursos y referencias | 54 referencias locales resuelven dentro del paquete; scripts/contratos/ruta de hook presentes | [Referencias](evidence/e8-d19d6e0/installed-references-check.json) |
| Protección intermedia | 114 archivos estables y configuración ajena a las dos identidades de prueba sin cambios | [Durante](evidence/e8-d19d6e0/protected-during.json) |
| Retirada y conservación final | Plugin, marketplace y cache temporal retirados; listados originales equivalentes; configuración idéntica byte por byte | [Limpieza](evidence/e8-d19d6e0/cleanup-check.json) |

Se conservaron también permisos y mtime de los 114 archivos estables, el enabled original y la confianza de hooks. No se restauró config.toml manualmente. El archivo de evidencia contiene hashes y campos acotados, sin copiar configuración privada completa.

El smoke creó solamente configuración, gitignore y lock del harness en un repositorio desechable. Runs quedó vacío; no se crearon decisiones, aprobaciones ni ejecución de producto. Los perfiles Sol/high–Luna/high–Sol/high y el límite3 se conservaron. El otro repositorio usado para descubrimiento permaneció sin inicializar. El host informó Codex Desktop/0.135.0, macOS arm64; el CLI local es 0.135.0.

## Trazabilidad y límites

Esta comprobación cierra el pendiente de instalación de la versión final señalado en el [corte local v3.0.0](release-v3.0.0.md). Se añade a la [E7 de ef7897d](e7-ef7897d.md) y la [E8 previa de ef7897d](e8-ef7897d.md), que permanecen intactas y referidas a su fuente original. El paquete de d19d6e0 es idéntico a ef7897d salvo el campo version de sus dos manifiestos; esta prueba nueva sí verificó la instalación 3.0.0 de d19d6e0.

Los resultados se limitan al host y a los escenarios ejercitados. Cliente nuevo app-server no demuestra refresco automático de chats abiertos ni catálogo inicial de un nuevo chat visible; no se creó un chat adicional del usuario. El smoke usa el runtime instalado y no equivale a una nueva implementación nativa Sol–Luna ni a evaluar todas las instrucciones de las 14 skills. Los nueve tests del hook y resolución de rutas no demuestran activación confiable/interceptación en vivo. No se atribuyen ahorros de tiempo/costo.

La comprobación fue una instalación local de prueba, no una descarga del marketplace estable publicado. El marketplace estable continúa en main y la versión sigue preparada localmente. Publicación, actualización de la instalación del usuario y migración de proyectos conservan sus límites de autorización.

## Preservación

[Índice](evidence/e8-d19d6e0/README.md), [archivos y snapshots](evidence/e8-d19d6e0/preservation.json), [integridad final](evidence/e8-d19d6e0/final-artifact-validation.json) y [SHA256SUMS](evidence/e8-d19d6e0/SHA256SUMS).

Se conservaron dos archivos del paquete: exportación Git y copia de marketplace comprobada byte-idéntica al cache instalado antes de retirarlo. También se conservaron operaciones/salidas, hashes y snapshots del proyecto de smoke. Las tablas CLI con relleno se preservan en gzip, con descompresión exacta comprobada. Esos archivos no restauran instalación, confianza, aprobación ni autoridad de ejecución. Tags y referencias remotas permanecen iguales a los capturados antes de la prueba.
''')
(E/'README.md').write_text('''# Evidencia — instalación aislada v3.0.0 / d19d6e0

APROBADA en instalación, descubrimiento fresco y arranque instalado. Instalación estable intacta; temporales retirados. Sin push/tag/publicación.

- [Informe](../../e8-d19d6e0.md).
- source-and-scope.json y refs-before.txt: fuente, autorización, identidades, 115 hashes y referencias protegidas.
- installed-version-check.json e installed-package.json: manifiestos reales 3.0.0, 115 archivos instalados iguales a la copia, 113 recursos iguales al candidato.
- installed-runtime.* e installed-hooks.*: 127 + 9 tests desde el cache instalado.
- discovered-skills.json: 14 skills habilitadas, cliente nuevo app-server.
- installed-bootstrap-* e installed-references-check.json: ocho operaciones, alcance y 54 referencias resueltas.
- protected-before.json, protected-during.json y cleanup-check.json: protección y limpieza verificadas.
- installation-operations.jsonl: siete operaciones CLI soportadas con entradas/salidas/exits.
- Tablas CLI .txt.gz y cli-output-preservation.json: salidas originales preservadas sin pérdida.
- candidate-package.tar, tested-package.tar, preservation.json y scratch/: archivos portables y snapshots. El archivo probado proviene de la copia temporal previamente comprobada idéntica al cache, que luego se retiró.
- reproduction/: scripts usados; no repetir instalación/preparación sobre destinos existentes ni sobrescribir evidencia comprometida.
- final-artifact-validation.json y SHA256SUMS: integridad final de todos los archivos salvo el propio inventario de hashes.

Los archivos históricos no otorgan confianza ni autorización. No se copiaron credenciales o configuración privada completa.
''')
p=R/'docs/releases/v3.0.0.md';s=p.read_text();old='A fresh installed v3.0.0 package evaluation has not been performed as part of this local metadata cut; confirm final distribution separately before publication.';new='A separate [final isolated v3.0.0 installation check](../implementation/e8-d19d6e0.md) subsequently passed on d19d6e0be75702907442412f9227688cbc835fba: 14 skills, 127 plugin tests and 9 hook tests from the installed cache, bootstrap checks, and stable installation/configuration preserved. Publication remains pending.';assert old in s;s=s.replace(old,new,1);needle='| [Local v3.0.0 preparation]';idx=s.index('\n',s.index(needle));s=s[:idx]+ '\n| [Final v3.0.0 isolated installation](../implementation/e8-d19d6e0.md) | d19d6e0be75702907442412f9227688cbc835fba, manifests 3.0.0 | Installed 3.0.0, 14 skills, 127 + 9 tests and bootstrap; separate identity removed, stable installation/configuration intact. |'+s[idx:];p.write_text(s)
p=R/'docs/implementation/release-v3.0.0.md';s=p.read_text();first=s.index('\n');s=s[:first]+ '\n\nActualización posterior, 2026-10-16: la [instalación aislada final de v3.0.0 sobre d19d6e0](e8-d19d6e0.md) quedó aprobada, con identidad separada y conservación exacta de la instalación estable/configuración. Este pendiente está resuelto; push, tag y publicación siguen pendientes. El registro siguiente conserva el alcance histórico del corte de metadatos previo a esa comprobación.\n'+s[first:];p.write_text(s)
p=R/'README.md';s=p.read_text();needle='Publication is pending.';assert needle in s;s=s.replace(needle,'The [final isolated v3.0.0 installation check](docs/implementation/e8-d19d6e0.md) passed on `d19d6e0`, preserving the stable installation and configuration. Publication is pending.',1);p.write_text(s)
p=R/'CHANGELOG.md';s=p.read_text();needle='### Validation\n';idx=s.index(needle,s.index('## Release v3.0.0'))+len(needle);s=s[:idx]+'\n- Final v3.0.0 isolated installation passed on d19d6e0: 14 enabled skills, 127 plugin tests + 9 hook tests from the installed cache, bootstrap checks, and stable installation/configuration unchanged after removal of the test identities. See [final installation evidence](docs/implementation/e8-d19d6e0.md).\n'+s[idx:];p.write_text(s)
p=R/'docs/implementation/harness-distribution.md';s=p.read_text();first=s.index('\n');s=s[:first]+'\n\nComprobación final actual: [v3.0.0 sobre d19d6e0, 2026-10-16](e8-d19d6e0.md), **aprobada** para instalación aislada, descubrimiento fresco y arranque instalado. 14 skills, 127 + 9 tests; instalación estable y configuración intactas; temporales retirados, sin push/tag/publicación. Las evaluaciones siguientes se conservan como historia de sus respectivos candidatos.\n'+s[first:];p.write_text(s)
p=R/'docs/implementation/harness-progress.md';s=p.read_text();first=s.index('\n');s=s[:first]+'\n\nComprobación final de distribución: [v3.0.0 instalada aisladamente desde d19d6e0](e8-d19d6e0.md), **aprobada** el 2026-10-16. 14 skills, 127 + 9 tests, smoke instalado y configuración/instalación estable conservadas. Corte local y comprobación final completos; push, tag y publicación pendientes. El historial E7/E8 conserva sus commits y alcances originales.\n'+s[first:];p.write_text(s)
print('Recorded final v3.0.0 installation and resolved its documented pending check; publication remains pending')
