# E8 — Preparación de distribución

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
