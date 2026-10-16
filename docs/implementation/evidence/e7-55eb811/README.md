# Evidencias E7 — 55eb811

Resultado: evaluación ejecutada, **no aprobada por HIGH F-01**. El [informe](../../e7-55eb811.md) distingue resultados nativos, pruebas deterministas, consultas reales, fallos deliberados y límites.

| Material | Contenido |
| --- | --- |
| `source-and-scope.json`, `package-checks.json` | Commit, fuente exportada, hashes, autorización y formato del paquete |
| `evaluation-plan.md` | Escenarios y criterio de conclusión establecidos antes del resultado |
| `deterministic-tests.{json,txt}`, `hook-tests.{json,txt}` | Comandos, tiempos, salidas y resultados completos: 117 + 9 |
| `consultation-tests.json` | Consultas reales y snapshots de bytes/permisos/mtime |
| `native-prerequisite-negative-probes.json` | Rechazos reales de perfil/capacidad antes de ejecución |
| `native/*/operations.jsonl` | Entrada, salida, exit, fecha y raíz de cada operación nativa |
| `native/native-result-summary.json` | Resumen del orquestador; contrastado independientemente |
| `native-independent-check.json` | Nueve sesiones reales, marcadores, hashes de registros del host, commits, pruebas repetidas y ausencia de leases |
| `native/*/repository.bundle` | Historia y refs de cada repositorio desechable; bundles verificados |
| `native/*/snapshot/` | Fuentes y registro final, incluidas modificaciones sin commit y paquetes ignorados |
| `native/*/preservation.json`, `preservation-summary.json` | Inventario y hashes de snapshots y bundles |
| `F-01-generated-tail-reproduction.json` | Rechazo de los dos templates literales por el lector de cierre |
| `completion-staleness-negative-probes.json` | Baselines y rechazos de complete tras editar código/spec en dos clones |
| `reproduction/` | Comprobadores independientes, entradas de probes y helpers originales de preparación |
| `SHA256SUMS` | Hashes de todos los archivos de este directorio salvo el propio manifiesto |

Los helpers originales conservan las rutas y condiciones de su ejecución. Son evidencia reproducible inspeccionable; no son una interfaz de producto ni deben ejecutarse sobre repositorios reales. Para repetir la prueba se necesita exportar de nuevo el commit, crear proyectos desechables nuevos y obtener identidades, aprobaciones y autorización vigentes. No se debe copiar autoridad histórica para ejecutar.

Los bundles permiten inspeccionar los commits sin depender de `/tmp`. Los snapshots preservan lo que Git no incluía después del abandono: eventos, recibos, estado, paquetes y código negativo. Para una reconstrucción forense offline, abrir una copia del bundle y comparar/superponer el snapshot con su manifiesto. No crea el worktree enlazado original, no restaura un lease y no habilita continuar el run. Las atestaciones contienen referencias y hashes de registros reales; los logs completos privados del host permanecen fuera de este repositorio.

Los cuatro repositorios originales se conservaron después de liberar propiedad con `abandon`. No hubo integración, push, tag, publicación, instalación, cambio de versión ni reparación del candidato.
