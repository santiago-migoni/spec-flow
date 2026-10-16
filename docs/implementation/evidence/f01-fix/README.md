# F-01 — Corrección y regresiones

Base: `4154db084d55ed7de4e9a14a11ec7beebd785237`; hallazgo y evaluación anterior en [E7 de 55eb811](../../e7-55eb811.md). Autorización: «Corrige F-01 conservando los controles actuales y repite E7 sobre el nuevo commit, usando proyectos desechables y registrando las pruebas, los resultados y las evidencias».

El lector de cierre trataba todo marcador generado sin un registro derivado como inválido. Ahora, para ese caso, usa el validador compartido estricto de progreso generado. El bloque inicial válido significa ausencia de registro de cierre; no representa autoridad para cerrar. Permanecen la comparación del registro persistido, aprobaciones/digests, evidencia vigente, árbol revisado, HEAD y recuperación. No se modificaron HARD-GATE, roles, perfiles, hook, esquemas, templates ni versión 2.0.0.

Regresiones nuevas: primer cierre/auditoría e idempotencia desde los bloques iniciales literales de spec/roadmap; rechazo de reemplazar un cierre persistido por progreso inicial; rechazo de bloques incompletos, duplicados, fuera de posición, prosa arbitraria y JSON inválido. Las pruebas existentes de recuperación tras escritura parcial y evento previo a auditoría ahora parten también de los bloques de los templates.

| Evidencia | Resultado |
| --- | --- |
| `red.txt`, `red.json` | Primer ensayo previo al cambio; reproduce F-01 y detecta además un error de contexto en una aserción de test |
| `red-confirmed.txt`, `red-confirmed.json` | Aserción corregida antes de tocar producción; los cuatro casos seleccionados siguen fallando por F-01 o rechazo faltante del marcador final aislado |
| `green-phases.txt`, `green-phases.json` | 22 tests de fase/cierre aprobados tras la corrección |
| `runtime.txt`, `runtime.json` | 120 tests del plugin aprobados |
| `hooks.txt`, `hooks.json` | 9 tests del hook aprobados |

Son pruebas deterministas con fixtures de controlador. No cuentan como delegación nativa ni reemplazan la nueva E7, cuyo candidato se fija en un commit posterior a estos resultados.

La revisión independiente (`independent-review.json`) no detectó hallazgos bloqueantes y repitió 120 + 9 tests. Los hashes de los tres archivos revisados se contrastaron con los bytes que se guardan en el commit de corrección. Sus probes adicionales se describen como revisión complementaria, no como ejecución E7.
