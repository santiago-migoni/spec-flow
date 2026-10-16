# F-02 — Corrección y regresiones

Base: `1766fc71b654547d72aa539bbfcdef5472be1a50`. Hallazgo y runs bloqueados: [E7 de f8fa91d](../../e7-f8fa91d.md). Autorización: «Corrige F-02 conservando los controles actuales, recupera los runs bloqueados mediante el controlador y repite E7 sobre el nuevo commit, usando proyectos desechables y registrando las pruebas, los resultados y las evidencias».

Ambas lecturas de linaje ahora comprueban que `source.subagent` sea un objeto antes de acceder a `thread_spawn`. Un registro ajeno de servicio/compactación con valor string no representa un hijo de thread. Tampoco puede satisfacer una atestación explícita de padre/ruta: esta sigue rechazándose con `host_parent_mismatch`. Los hijos con linaje de thread válido recorren los mismos controles previos.

Se conservan perfiles, parentesco/ruta, marcadores, timestamps, inventario vigente, rechazo de hijos activos/omitidos/no atribuibles, verificación, propiedad persistente y controles de cierre. No se modificaron logs del host, CODEX_HOME real, fuentes/recibos de los runs bloqueados, HARD-GATE, esquemas, hook, templates ni versión 2.0.0 para superar las pruebas.

| Evidencia | Resultado |
| --- | --- |
| `red.txt`, `red.json` | Tres regresiones antes del cambio: AttributeError reproducido con metadatos no objeto; 7 errores en subcasos |
| `runtime.txt`, `runtime.json` | 123 tests del plugin aprobados después del cambio |
| `hooks.txt`, `hooks.json` | 9 tests del hook aprobados |

Tres tests nuevos verifican barrido sin hijos con metadatos ajenos no objeto, rechazo de su uso como linaje requerido y conservación de rechazos cuando coexisten con un hijo propio. El caso previo de hijo no atribuible incorpora también ese metadato ajeno. Son pruebas deterministas con logs sintéticos de test; la recuperación de runs y E7 real se registran por separado usando el commit exportado, sesiones nativas y registros auténticos del host.

Revisión independiente sin hallazgos bloqueantes en `independent-review.json`; sus hashes se contrastaron con el parche. Repitió 123 + 9 tests. Se conserva su invocación inicial con import path incorrecto y la ejecución corregida, sin atribuir al primer comando pruebas no ejecutadas.
