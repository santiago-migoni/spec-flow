# E7 — Reevaluación del candidato f8fa91d

Commit: `f8fa91d2c98927eeaba3af0643e9973e9a1e506f`. Objetivo: comprobar la corrección de F-01 con ejecución nativa nueva y preservar los controles actuales. Fuente exportada exacta, sin modificaciones durante E7. La solicitud del usuario y los hashes están en `source-and-scope.json`.

| Escenario | Comprobación requerida |
| --- | --- |
| Proyecto nuevo | Documentos actuales aplicables, tablas coherentes y tree verificado; gates antes/después de recibos sintéticos; tarea Luna, verificación, revisión Sol distinta, commit; converge, release-review desde bloques iniciales y una única auditoría; finishing con rama conservada |
| Interrupción y paquetes | Interrumpir después de la escritura, conciliar archivos/resultado sin repetir; pérdida y restauración exacta de paquete sin nuevo intento |
| Legacy | Preview/apply revisados; conservar originales y hashes; cero autoridad/evidencia importada de etiquetas/casillas; nuevos recibos E7; completar fase y cierre |
| Correcciones insuficientes | Tres intentos deliberados con pruebas reales fallidas; review/close rechazados; preparación de cuarto intento rechazada sin delegarlo; abandono reconciliado preserva historial/presupuesto |
| Controles complementarios | Suites completas del paquete exportado y hook; consultas estrictas sin archivos/mtime; perfiles/capacidades incorrectos rechazados; cambios posteriores de código/spec invalidan estado en clones separados |

Las decisiones/recibos de fixture y autorización de ejecución son sintéticos y exclusivos de estos proyectos desechables bajo el pedido E7. No sustituyen aprobación de un producto real. Orquestador Sol high atestado; un Luna high activo por vez; revisor Sol high distinto por fase; Git worktrees enlazados y registro común de propiedad. Sin adaptadores simulados en los runs nativos.

Separar suite determinista, consultas reales, fallos deliberados y delegación nativa. Conservar operaciones/entradas/salidas, hashes, atestaciones compactas, paquetes, fuentes, eventos, pruebas y Git bundles. No copiar logs privados completos del host. Positivos deben terminar limpios con cierre/auditoría y lease liberado; negativo debe abandonar por operación soportada conservando sus archivos e historial. Si aparece otro bloqueo, registrarlo sin modificar el candidato.

E7 no ejecuta E8, instalación, integración del plugin, bump, push, tag, publicación ni despliegue. Los resultados anteriores permanecen históricos. Una aprobación E7 queda limitada al alcance realmente ejecutado y no acredita todos los casos de las skills ni preparación completa de publicación.
