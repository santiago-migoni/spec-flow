# F-03 — corrección y regresiones

Base: 6650a194f7ea1c448ffc75d4d21e273fb7d2021e. Hallazgo nativo en la evaluación E7 de 34d8909: tarea verification_failed activa tras agotar tres intentos; retry bloquea y abandon exige una reconciliación no aplicable.

La excepción acotada de abandon requiere fracaso de verificación y presupuesto agotado, autorización explícita, propiedad y propietario válidos, y atestación del hijo nativo ligado como terminal. El evento persiste el fallo no resuelto y su intento; el reducer retira la reserva activa sin alterar la tarea fallida ni sus intentos. Repetir tras una caída completa la liberación sin duplicar el evento. Un nuevo run conserva el presupuesto y no permite un cuarto intento.

- red.txt: cuatro tests, dos errores y tres aserciones fallidas antes de modificar producción; todos por el rechazo anterior active_task_requires_reconciliation.
- runtime.txt: 127 pruebas aprobadas después del cambio; incluye conservación de historia/código, presupuesto entre runs, autorización, propietario, lease, hijo activo/inaccesible e idempotencia ante caída.
- hooks.txt: nueve pruebas aprobadas.
- independent-review.json: revisión independiente y suites 127 + 9 aprobadas; no certifica por sí sola recuperación ni E7 nativa.

Los adaptadores simulados de las regresiones deterministas no acreditan sesiones reales. La recuperación real y la siguiente evaluación se registran separadamente por el commit exacto evaluado. No se alteraron límites, hard gates, perfiles, aprobaciones ni requisitos de cierre. Versión 2.0.0 conservada.
