# E8 — Preparación de distribución

Estado actual: **[v3.1.0 publicada](publication-v3.1.0.md)** como estable y Latest, tag sobre `fad239f`, descarga de 139 archivos verificada. E7/E8 y prueba instalada final mantienen su trazabilidad; instalación/configuración del usuario intactas, sin migración. Los pendientes y estados siguientes se conservan como historia de preparación.

Corte final v3.1.0: [instalación aislada sobre fad239f](e8-v3.1.0.md), **aprobada** (139 archivos, 14 skills, 152 + 10 tests). Solo version de manifiestos difiere de e9fe146, cuya E7/E8 permanece vigente para el código; instalación estable/configuración intactas y temporales retirados. Publicación autorizada pendiente de completar y verificar.

Comprobación de distribución más reciente: [E8 sobre e9fe146, 2026-10-16](e8-e9fe146.md), **aprobada dentro de instalación aislada, descubrimiento fresco y arranque instalado**. 139 archivos instalados, 14 skills, suites 152 + 10, ocho templates YAML y 75 referencias válidas. Identidades temporales retiradas; instalación estable y configuración intactas; sin publicación. Junto con E7 del mismo commit, resuelve el pendiente E8 señalado en el registro siguiente, cuyo texto se conserva como historia.

Comprobación de desarrollo más reciente: [E7 sobre e9fe146, 2026-10-16](e7-e9fe146.md), **aprobada dentro de su alcance** con YAML, compatibilidad JSON y perfiles `gpt-6.1-sol/low` → `gpt-6-luna/high` → `gpt-6.1-sol/medium`. 152 + 10 pruebas deterministas; ejecución nativa y controles registrados. E8 sobre este candidato sigue pendiente. No hubo publicación ni actualización de instalación; los estados siguientes conservan su alcance histórico.

Estado actual: **[v3.0.0 publicada](https://github.com/santiago-migoni/spec-flow/releases/tag/v3.0.0)**, verificada el 2026-10-16; tag en `1c92505`. [Comprobante de publicación](publication-v3.0.0.md), con E7/E8 originales preservados y paquete descargado verificado. Instalación del usuario y configuración intactas; no se migraron proyectos. Los registros siguientes conservan los estados históricos de preparación y evaluación anteriores a la publicación.


Comprobación final actual: [v3.0.0 sobre d19d6e0, 2026-10-16](e8-d19d6e0.md), **aprobada** para instalación aislada, descubrimiento fresco y arranque instalado. 14 skills, 127 + 9 tests; instalación estable y configuración intactas; temporales retirados, sin push/tag/publicación. Las evaluaciones siguientes se conservan como historia de sus respectivos candidatos.


Resultado actual: [E8 de ef7897d, 2026-10-16](e8-ef7897d.md), **aprobada** para instalación aislada, cliente nuevo y arranque del paquete instalado. Suites 127 + 9; 14 skills; instalación estable y configuración intactas; sin publicación. El registro siguiente conserva la evaluación histórica del 2026-10-14.

Fecha: 2026-10-14. Candidato de desarrollo en `codex/spec-flow-harness`; versión conservada: 1.1.0. Propuesta incompatible: **2.0.0**, pendiente de autorización y commit separado.

## Evidencia

- Copia del paquete en una ruta temporal con espacios, marketplace `spec-flow-e8-market-01a13adc` y plugin `spec-flow-e8-01a13adc`. Solo cambiaron nombre/displayName de los manifiestos de prueba. Los 112 recursos restantes coincidieron por SHA256 con el checkout y la instalación: [hashes](evidence/distribution/package-resources.json), [operaciones](evidence/distribution/installation-results.json).
- Suites desde el paquete reubicado: [107 pruebas](evidence/distribution/relocated-runtime.txt), [9 hooks](evidence/distribution/relocated-hooks.txt).
- Cliente local nuevo de Codex app-server, `skills/list(forceReload=true)`: [16 skills habilitadas](evidence/distribution/discovered-skills.json). Sol leyó el bootstrap instalado y ejecutó initialize/status/gate constitution en un repositorio temporal vacío: [reporte](evidence/distribution/native-installed-flow.md).
- Chat nuevo autorizado `01a13b83-af74-75c2-b539-995a6380520b`: catálogo inicial con las 16 skills; dos contratos y dos scripts referenciados presentes. Modelo comprobado en turn_context del host: [registro compacto](evidence/distribution/fresh-chat.json). No se usó su autodeclaración como evidencia del modelo.
- Plugin y marketplace temporales retirados tras la comprobación. Listados previos y posteriores iguales al normalizar espacios: [limpieza](evidence/distribution/cleanup.json). No se reemplazaron instalaciones existentes.

## Límites observados

El CLI independiente rechazó `gpt-6-sol` con HTTP 400 por modelo no soportado para esa cuenta/ruta. No hubo sustitución de modelo: las comprobaciones con Sol usaron Codex Desktop. Un subagente previo conservaba el catálogo inyectado anterior; el app-server recargado y el chat nuevo sí descubrieron el paquete. No se promete refresco automático de chats existentes.

El host evaluado fue Codex Desktop 0.135.0, macOS arm64. El runtime requiere POSIX, Git, delegación nativa y registros del host accesibles. Los hooks no se habilitaron como confiables durante esta instalación; sus nueve pruebas son deterministas y no demuestran interceptación universal. La evaluación funcional nativa está en [E7](../../plugins/spec-flow/evals/native/evaluation-report.md), y no demuestra ahorro de tiempo o costo.

El formato y la instalación se contrastaron con la [documentación oficial de plugins](https://developers.openai.com/plugins/build/plugins) y el protocolo local generado por Codex. No hubo publicación, tag ni cambio de versión. La evidencia de esta carpeta se añadió después de probar el paquete y no altera sus recursos ejecutables.
