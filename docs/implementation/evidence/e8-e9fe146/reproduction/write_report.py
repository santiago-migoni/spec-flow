from pathlib import Path
import json
R=Path('/Users/santiago_migoni/Documents/Projects/spec-flow');E=R/'docs/implementation/evidence/e8-e9fe146';c=json.loads((E/'source-and-scope.json').read_text())
(E/'findings.json').write_text(json.dumps({'candidate':c['candidate'],'candidate_blocking_findings':[],'evaluator_observations':[{'id':'OBS-E8-01','description':'Primer arranque de app-server desde sandbox rechazó escritura de SQLite de estado del host. Se preserva stderr y se repite con ejecución autorizada fuera del sandbox; descubrimiento fresco correcto. No se modificó el candidato ni se cambió la instalación estable.','evidence':'discovery-server-sandbox-attempt.stderr'}],'result':'PASS within isolated installation, discovery and installed bootstrap scope'},ensure_ascii=False,indent=2)+'\n')
(R/'docs/implementation/e8-e9fe146.md').write_text('''# E8 — Instalación aislada de e9fe146

Fecha: 2026-10-16. **APROBADA dentro del alcance de instalación aislada, descubrimiento fresco y arranque instalado.** Candidato exacto: `e9fe1461727e7b508143646132e2b9bc9ba5c16c`; versión conservada **3.0.1**. La instalación del usuario quedó intacta; plugin y marketplace temporales retirados. Sin commit, push, tag, publicación ni migración de proyectos reales.

[Fuente y autorización](evidence/e8-e9fe146/source-and-scope.json) · [Hallazgos/observaciones](evidence/e8-e9fe146/findings.json) · [Índice de evidencias](evidence/e8-e9fe146/README.md) · [SHA256SUMS](evidence/e8-e9fe146/SHA256SUMS)

## Fuente e identidad separada

Exportación directa desde Git: 139 archivos, archivo SHA256 `518d9fbdc7c8b8753e40dba5d465fc3601bd1839a95b7e5b3410185c9d2726f5`. Solo se cambiaron `name` y `extensions.com.openai.interface.displayName` en los dos manifiestos de la copia temporal. Los otros **137 recursos** permanecieron idénticos al commit. Los 139 archivos instalados coincidieron con la copia preparada; versión 3.0.1 y manifiestos espejo verificados.

| Elemento | Identidad |
| --- | --- |
| Plugin estable protegido | `spec-flow@spec-flow` |
| Plugin temporal | `spec-flow-e8-e9fe146` |
| Marketplace temporal | `spec-flow-e8-e9fe146-01a13f8c` |
| Cache de prueba | `~/.codex/plugins/cache/spec-flow-e8-e9fe146-01a13f8c/spec-flow-e8-e9fe146/3.0.1` |
| Fuente de prueba | Copia local del commit exacto en una ruta con espacios |

La versión 3.0.1 también existe en la instalación estable: esta prueba acredita los **bytes de e9fe146**, no que una instalación estable con el mismo número contenga los cambios locales. [Hashes instalados](evidence/e8-e9fe146/installed-package.json) · [Versión e icono](evidence/e8-e9fe146/installed-version-check.json).

## Pruebas y resultados

| Prueba | Resultado | Evidencia |
| --- | --- | --- |
| Instalación separada | Registro e instalación por CLI soportado, identidad única, exit0 | [Operaciones exactas](evidence/e8-e9fe146/installation-operations.jsonl) |
| Controlador desde cache instalado | **152 pruebas aprobadas**, paquete sin cambios | [Resultado](evidence/e8-e9fe146/installed-runtime.json), [salida](evidence/e8-e9fe146/installed-runtime.txt) |
| Hooks desde cache instalado | **10 pruebas aprobadas**, paquete sin cambios | [Resultado](evidence/e8-e9fe146/installed-hooks.json), [salida](evidence/e8-e9fe146/installed-hooks.txt) |
| Cliente app-server nuevo | **14 skills habilitadas**, sin errores, todas desde cache temporal | [Descubrimiento](evidence/e8-e9fe146/discovered-skills.json) |
| Arranque desde bootstrap descubierto | Ocho operaciones: status inicial, initialize idempotente, status sin runs, gate constitution y tres kinds inexistentes rechazados | [Smoke](evidence/e8-e9fe146/installed-bootstrap-check.json), [operaciones](evidence/e8-e9fe146/installed-bootstrap-operations.json) |
| Encabezados YAML | Ocho templates canónicos leídos por el parser de producción instalado | [Templates](evidence/e8-e9fe146/installed-yaml-templates.json) |
| Recursos y referencias | **75 referencias locales** válidas; scripts, contratos y hook resuelven | [Referencias](evidence/e8-e9fe146/installed-references-check.json) |
| Protección durante la prueba | 115 archivos estables y configuración ajena a las dos identidades temporales intactos | [Durante](evidence/e8-e9fe146/protected-during.json) |
| Retirada y conservación final | Marketplace, plugin y cache temporal retirados; listados equivalentes; config idéntico byte por byte | [Limpieza](evidence/e8-e9fe146/cleanup-check.json) |

El smoke se ejecutó desde la ruta realmente descubierta en un repositorio desechable. Creó solamente config, gitignore y lock; no decisiones, aprobaciones ni runs. Los perfiles inicializados son `gpt-6.1-sol/low`, `gpt-6-luna/high`, `gpt-6.1-sol/medium`, con límite de tres intentos. El otro proyecto de descubrimiento permaneció sin inicializar. La suite instalada incluye las regresiones de documentos JSON y runs históricos; E8 no vuelve a implementar un producto ni reemplaza las atestaciones nativas de E7.

## Controles, observaciones y límites

Se conservaron contenido, permisos y mtime de los 115 archivos bajo el cache estable, enabled/configuración original y confianza de hooks. No se restauró ni reescribió manualmente `config.toml`: las operaciones soportadas de retirada devolvieron su contenido original. La evidencia registra hashes y campos acotados; no copia la configuración privada completa.

El primer app-server ejecutado dentro del sandbox no pudo escribir su estado SQLite y terminó antes de inicializar. Se preservó el stderr y se repitió con ejecución autorizada fuera del sandbox. El segundo cliente descubrió correctamente las skills. Es una incidencia del entorno de evaluación, sin cambio del candidato ni hallazgo bloqueante. [Observación](evidence/e8-e9fe146/findings.json).

El host reportó Codex Desktop/0.135.0, macOS arm64. Cliente app-server nuevo no prueba actualización automática del catálogo de chats abiertos; no se creó otro chat del usuario. Se comprobó la ruta del PNG y su cabecera, sin afirmar que el icono haya sido renderizado en la UI. Las diez pruebas de hooks y resolución de rutas no demuestran confianza/activación/interceptación en vivo. No se midieron ahorros ni eficacia de todas las instrucciones de skills.

Esta es una instalación local de prueba con identidad distinta; no una descarga del marketplace publicado. No hubo publicación, instalación/actualización del plugin estable ni migración de proyectos del usuario. E7 y E8 aprobadas sobre este commit no autorizan por sí mismas un corte de versión o publicación.

## Trazabilidad y preservación

La [E7 del mismo e9fe146](e7-e9fe146.md) conserva su resultado, sus cinco observaciones del evaluador y la separación de categorías. Las E7/E8 anteriores permanecen históricas. Se verificaron hashes de la evidencia actual E7 y de evaluaciones anteriores, paquete original contra Git, archivos instalados, referencias locales, HEAD y refs de tags/remotos.

[Preservación](evidence/e8-e9fe146/preservation.json): exportación Git y archivo del paquete temporal comprobado idéntico al cache antes de retirarlo; salidas completas, comandos, snapshots de los dos proyectos desechables y reproducción. Los archivos preservados no instalan el plugin ni restauran confianza, aprobación o autoridad de ejecución. Las tablas CLI con relleno se preservan mediante gzip con descompresión exacta comprobada.

[Validación final](evidence/e8-e9fe146/final-artifact-validation.json). Los cambios previos de evidencias E7 estaban presentes al comenzar y se conservaron; solo se añaden resultados E8 y punteros documentales. Todo queda local y sin commit.
''')
(E/'README.md').write_text('''# Evidencias E8 — e9fe146

[Informe completo](../../e8-e9fe146.md) · [Hallazgos y observación](findings.json) · [Validación final](final-artifact-validation.json) · [Checksums](SHA256SUMS)

- `source-and-scope.json`: commit, autorización, nombres separados, hashes y estado Git inicial.
- `candidate-package.tar`: exportación exacta de Git.
- `tested-package.tar`, `installed-package.json`: copia temporal e inventario instalado con correspondencia exacta.
- `installation-operations.jsonl`: comandos soportados y resultados de instalación/retirada.
- `installed-runtime.*`, `installed-hooks.*`: suites 152 + 10 desde cache instalado.
- `discovered-skills.json`, `installed-bootstrap-*`, `installed-yaml-templates.json`, `installed-references-check.json`: cliente nuevo, arranque, ocho templates y 75 referencias.
- `protected-before.json`, `protected-during.json`, `cleanup-check.json`: conservación del plugin estable/configuración y retirada de las identidades temporales.
- `discovery-server-sandbox-attempt.stderr`: intento inicial rechazado por SQLite de solo lectura; el reintento autorizado sí descubrió las skills.
- `preservation.json`, `scratch/`, `reproduction/`: preservación y scripts con las rutas de esta evaluación. Adaptar rutas e identidades al reproducir; no importar snapshots como autoridad.

No se copian config privada completa ni credenciales. Los archivos son evidencia histórica, sin instalación, confianza de hooks, aprobaciones ni autoridad activa. La prueba no modifica el paquete candidato ni su versión y no publica.
''')
for name in ['harness-progress.md','harness-distribution.md']:
 p=R/'docs/implementation'/name;s=p.read_text();title,rest=s.split('\n',1);p.write_text(title+'\n\nComprobación de distribución más reciente: [E8 sobre e9fe146, 2026-10-16](e8-e9fe146.md), **aprobada dentro de instalación aislada, descubrimiento fresco y arranque instalado**. 139 archivos instalados, 14 skills, suites 152 + 10, ocho templates YAML y 75 referencias válidas. Identidades temporales retiradas; instalación estable y configuración intactas; sin publicación. Junto con E7 del mismo commit, resuelve el pendiente E8 señalado en el registro siguiente, cuyo texto se conserva como historia.\n'+rest)
print('E8 report, index, findings and current pointers written')
