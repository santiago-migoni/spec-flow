from pathlib import Path
import json
R=Path.cwd();E=R/'docs/implementation/evidence/e8-ef7897d';c=json.loads((E/'source-and-scope.json').read_text());clean=json.loads((E/'cleanup-check.json').read_text());assert clean['result']=='PASS'
(R/'docs/implementation/e8-ef7897d.md').write_text(f'''# E8 — instalación aislada de ef7897d

Fecha: 2026-10-16. **APROBADA para instalación aislada, descubrimiento en cliente nuevo y arranque del runtime instalado en este host.** Se verificó el candidato `{c['candidate']}`, sin reemplazar la instalación estable. El plugin y marketplace temporales fueron retirados y la configuración original quedó idéntica byte por byte.

## Candidato, autorización e identidad

El usuario autorizó E8 sobre ef7897d con identidad de marketplace separada, conservación de su instalación y registro de pruebas/resultados/evidencias. [Declaración literal e inventario](evidence/e8-ef7897d/source-and-scope.json).

Se exportó el paquete directamente desde Git: 115 archivos, archivo SHA-256 `{c['archive_sha256']}`, igual al candidato evaluado en [E7](e7-ef7897d.md). El checkout actual no fue usado como sustituto del commit solicitado.

| Elemento | Identidad |
| --- | --- |
| Instalación estable protegida | spec-flow@spec-flow, versión 2.0.0 |
| Marketplace temporal | {c['marketplace_name']} |
| Plugin temporal | {c['name']} |
| Selector temporal | {c['selector']} |
| Versión del candidato | 2.0.0, conservada |

La copia temporal vive en una ruta con espacios. Solo cambiaron `name` y `extensions.com.openai.interface.displayName` en ambos manifiestos, manteniendo su equivalencia. Los otros **113 recursos** conservaron sus hashes exactos del candidato. La instalación real tuvo los 115 archivos idénticos a esa copia de prueba. [Inventario instalado](evidence/e8-ef7897d/installed-package.json).

## Pruebas y resultados

| Prueba | Resultado observado | Evidencia |
| --- | --- | --- |
| Instalación CLI soportada | marketplace add, plugin add y listado temporal: exit0 | [Operaciones](evidence/e8-ef7897d/installation-operations.jsonl) |
| Suite desde el cache instalado | 127 pruebas PASS; sin cambiar archivos del paquete | [Runtime](evidence/e8-ef7897d/installed-runtime.json), [salida](evidence/e8-ef7897d/installed-runtime.txt) |
| Hook desde el cache instalado | 9 pruebas PASS; sin cambiar archivos del paquete | [Hook](evidence/e8-ef7897d/installed-hooks.json), [salida](evidence/e8-ef7897d/installed-hooks.txt) |
| Cliente nuevo app-server | skills/list con forceReload devolvió exactamente 14 skills habilitadas del namespace temporal, sin errores, todas desde el cache instalado | [Descubrimiento](evidence/e8-ef7897d/discovered-skills.json) |
| Arranque en repositorio nuevo | status uninitialized; initialize inicial y repetido idempotente; status sin runs; constitution gate ready | [Smoke](evidence/e8-ef7897d/installed-bootstrap-check.json), [8 operaciones](evidence/e8-ef7897d/installed-bootstrap-operations.json) |
| Gates inexistentes | using-spec-flow, design y backlog rechazados con invalid_input/exit2 | [Operaciones](evidence/e8-ef7897d/installed-bootstrap-operations.jsonl) |
| Referencias instaladas | 54 enlaces Markdown locales de skills/harness resuelven dentro del paquete; scripts, contratos y ruta del hook presentes | [Referencias](evidence/e8-ef7897d/installed-references-check.json) |
| Protección durante instalación | 114 archivos estables sin cambios; configuración fuera de las dos identidades temporales idéntica | [Comprobación intermedia](evidence/e8-ef7897d/protected-during.json) |
| Limpieza final | Plugin/marketplace/cache temporales retirados; listados iniciales y finales equivalentes; configuración original idéntica byte por byte | [Limpieza](evidence/e8-ef7897d/cleanup-check.json) |

Las 14 skills incluyen design y sus tres templates; architecture, infrastructure y structure permanecen como documentos/perspectivas, sin volver a registrarse como skills independientes. El host initialize informó Codex Desktop/0.135.0, macOS arm64; CLI local 0.135.0.

El smoke resolvió el runtime a partir del bootstrap devuelto por descubrimiento y usó únicamente ese paquete instalado. Se leyeron using-spec-flow y el contrato de operaciones instalado. El proyecto solo recibió configuración del harness, su gitignore y lock; runs quedó vacío. No se crearon decisiones, aprobaciones, tareas ni ejecución de producto. Se conservaron perfiles Sol/high–Luna/high–Sol/high y límite3. La siguiente decisión real sería definir propósito/resultados para una constitución, fuera de este smoke.

Se corrigieron dos aserciones del evaluador: el rechazo de un gate inexistente usa invalid_input, y initialize crea el directorio runs vacío. El primer sondeo quedó preservado; el smoke completo registró sus ocho operaciones en otro repositorio nuevo y se verificó su estado. El candidato permaneció intacto. [Notas del evaluador](evidence/e8-ef7897d/evaluator-notes.json).

## Conservación de la instalación actual

Los 114 archivos de la instalación estable mantuvieron bytes, permisos y mtime. Su setting enabled permaneció igual; la configuración completa y el contenido de confianza de hooks resultaron idénticos a los valores previos. Se usaron las operaciones soportadas de registro/retirada sobre las identidades temporales; no se restauró config.toml manualmente. [Estado previo](evidence/e8-ef7897d/protected-before.json) y [comprobación final](evidence/e8-ef7897d/cleanup-check.json). La evidencia almacena hashes y datos acotados, sin copiar la configuración privada completa.

## Límites

- El descubrimiento se verificó en un cliente app-server nuevo. No se probó refresco automático del catálogo inyectado en este chat ni el catálogo inicial de un nuevo chat visible de Desktop; no se creó un chat adicional del usuario.
- El smoke fue ejecutado mediante el runtime instalado. No es una nueva implementación nativa Sol–Luna ni una prueba de obediencia de un modelo a todas las skills; esa ejecución funcional está separada en E7.
- Los hooks conservaron su confianza previa. Nueve tests y resolución de rutas no demuestran que el usuario haya confiado el hook de prueba, que se haya ejecutado en vivo ni interceptación universal.
- Esta es instalación local desde un marketplace de prueba, no una descarga de ef7897d desde el marketplace estable ni una publicación. No hubo bump, push, tag, release, despliegue o migración de proyectos existentes. E7/E8 no prueban ahorro de tiempo o costo.

El formato de marketplace y manifiestos se contrastó con la [documentación oficial de plugins de OpenAI](https://developers.openai.com/plugins/build/plugins); el comportamiento concreto se contrastó con la ayuda del CLI local y la instalación observada. Las diferencias de la versión evaluada frente a documentación actual no se sustituyeron por supuestos.

## Preservación

[Índice de evidencias](evidence/e8-ef7897d/README.md), [preservación](evidence/e8-ef7897d/preservation.json), [integridad final](evidence/e8-ef7897d/final-artifact-validation.json) y [SHA256SUMS](evidence/e8-ef7897d/SHA256SUMS).

Se conservan el archivo exacto del candidato y el archivo de la copia de marketplace verificada como idéntica al cache instalado, además de operaciones/salidas, hashes y dos snapshots de proyectos vacíos inicializados. El archivo de prueba proviene de la copia temporal byte-idéntica; no se presenta como un snapshot copiado del cache ya retirado. Los originales temporales siguen disponibles. Los archivos preservados no restablecen instalación, confianza de hooks, aprobaciones o autorización de ejecución.
''')
(E/'README.md').write_text('''# Evidencia E8 — ef7897d

APROBADA en el alcance de instalación aislada, descubrimiento fresco y arranque instalado. La instalación estable está intacta; plugin y marketplace temporales retirados. Sin publicación.

- [Informe](../../e8-ef7897d.md).
- source-and-scope.json: commit exacto, autorización e inventarios del candidato y copia con identidad separada.
- protected-before.json, protected-during.json, cleanup-check.json: instalación estable y configuración protegidas antes/durante/después.
- installation-operations.jsonl y listados before/after: registro/instalación y limpieza por CLI soportado.
- installed-package.json: igualdad de 115 archivos con la copia de prueba; 113 recursos sin cambio respecto al candidato.
- installed-runtime.* y installed-hooks.*: suites 127 + 9 desde el cache instalado.
- discovered-skills.json: 14 skills habilitadas en cliente nuevo app-server; no acredita refresco de chats abiertos.
- installed-bootstrap-check.json, installed-bootstrap-operations.*: smoke real del runtime instalado y límites de autoridad.
- installed-references-check.json: 54 referencias locales y recursos resueltos.
- evaluator-notes.json: aserciones del evaluador corregidas, sin modificar el candidato.
- candidate-package.tar, tested-package.tar, preservation.json y scratch/: archivos portables y snapshots; procedencia explícita de la copia byte-idéntica al cache.
- reproduction/: scripts usados. No repetir preparación, instalación o smoke sobre los mismos destinos ya existentes; verificar identidades y estado antes de cualquier nueva instalación.
- final-artifact-validation.json y SHA256SUMS: integridad de los archivos preservados, salvo el propio inventario de hashes.

Los archivos portables no instalan plugins ni otorgan confianza o autorización. No se copiaron credenciales ni la configuración privada completa del usuario.
''')
p=R/'docs/implementation/harness-progress.md';s=p.read_text();old='E8 no se repitió sobre este candidato y no se declara una nueva versión lista para publicación.';new='La [E8 de ef7897d](e8-ef7897d.md) también quedó aprobada en instalación aislada, descubrimiento fresco y arranque instalado: 14 skills, 113 recursos conservados y suites 127 + 9. La instalación estable y la configuración permanecen intactas; no hubo publicación ni cambio de versión.';assert old in s;s=s.replace(old,new,1);s+='''\n## E8 2026-10-16 — candidato ef7897d, identidad separada\n\nInstalación temporal spec-flow-e8-ef7897d@spec-flow-e8-ef7897d-01a13f8c desde copia exacta de ef7897d en ruta con espacios. Solo name/displayName de ambos manifiestos cambiaron; 113 recursos idénticos, 115 archivos instalados comprobados. Suites del cache instalado: 127 pruebas del plugin + 9 del hook PASS. Cliente app-server nuevo descubrió 14 skills habilitadas; smoke instalado verificó inicialización idempotente, estado sin runs, gate de constitución y rechazo de tres kinds inexistentes, sin decisiones/aprobaciones/ejecución de producto. 54 referencias locales resuelven.\n\nPlugin y marketplace temporales retirados por CLI; listados previos/finales equivalentes. Los 114 archivos estables conservan bytes/permisos/fechas; configuración completa idéntica byte por byte, confianza de hooks intacta. **E8 aprobada en este alcance**; no se creó un nuevo chat visible ni se probó refresco automático de chats existentes o activación confiable del hook. Archivos del candidato/test y snapshots preservados. Sin publicación, bump, push, tag, despliegue ni migración de proyectos existentes. [Informe actual y evidencias](e8-ef7897d.md).\n''';p.write_text(s)
p=R/'docs/implementation/harness-distribution.md';s=p.read_text();heading='# E8 — Preparación de distribución\n';assert s.startswith(heading);s=s.replace(heading,heading+'\nResultado actual: [E8 de ef7897d, 2026-10-16](e8-ef7897d.md), **aprobada** para instalación aislada, cliente nuevo y arranque del paquete instalado. Suites 127 + 9; 14 skills; instalación estable y configuración intactas; sin publicación. El registro siguiente conserva la evaluación histórica del 2026-10-14.\n',1);p.write_text(s)
p=R/'README.md';s=p.read_text();old='The development candidate passed native fresh-project and migration evaluations, interruption and failed-correction checks, and a separate installed-package test. See the [evaluation record](docs/implementation/harness-progress.md) and [distribution evidence](docs/implementation/harness-distribution.md). **2.0.0** includes the final review fixes (114 plugin tests and 9 hook tests). The native and installed-package evaluations predate those fixes. The measurements do not establish time or cost savings.';new='Development candidate `ef7897d` passed [E7 native evaluation](docs/implementation/e7-ef7897d.md) and [E8 isolated installation](docs/implementation/e8-ef7897d.md) on the evaluated host. E8 used a separate marketplace/plugin identity, preserved 113 package resources, discovered 14 enabled skills in a fresh app-server client, and passed 127 plugin tests plus 9 hook tests from the installed cache. The existing stable installation and configuration were unchanged after cleanup. These results apply to the tested candidate and stated scenarios; they do not publish a new release, prove automatic catalog refresh in existing chats or live hook activation, or establish time or cost savings. See the [evaluation history](docs/implementation/harness-progress.md) for earlier candidates.';assert old in s;p.write_text(s.replace(old,new,1))
