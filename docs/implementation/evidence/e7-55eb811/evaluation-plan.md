# E7 — Plan de evaluación del commit 55eb811

Objetivo: evaluar el candidato exacto `55eb811bd05043966b9763e7270ed678444896c5` en proyectos desechables, conservando los controles y separando las clases de evidencia. La autorización es la solicitud del usuario registrada en source-and-scope.json.

## Alcance

- Fuente exportada e inmutable, comprobada byte a byte contra Git; versión 2.0.0 sin cambios.
- Ejecución de producción con NativeCodexAdapter, orquestador gpt-6-sol/high atestado, Luna/high por tarea, revisor Sol/high distinto por fase y worktrees enlazados aislados.
- Decisiones y aprobaciones sintéticas explícitas solo para fixtures E7, sin presentarlas como aprobación de un producto real.
- No alterar el paquete para resolver fallos del candidato; preservar el diagnóstico y la evidencia.

## Escenarios y resultados esperados

| Escenario | Resultado esperado | Evidencia requerida |
| --- | --- | --- |
| Proyecto nuevo | Gate rechaza aprobaciones ausentes; documentos y tablas actuales coherentes; implementación real verificada; revisión de tarea y fase; commit de fase y auditoría; impacto pendiente | Contratos/pins, operaciones, pruebas conductuales, atestaciones, diff y commits |
| Interrupción tras escritura | Conciliar agente y archivos existentes sin repetir una escritura por pérdida de respuesta | Estado nativo terminal, interrupt/resume/reconcile y hashes antes/después |
| Proyecto legacy | Gate exige migración; preview/revisión/apply preservan originales; etiquetas/checkboxes no importan autoridad | Manifest/digest, fuentes/archivo, resultados de importación y recibos E7 nuevos |
| Corrección deliberadamente insuficiente | Pruebas reales fallan; review(pass)/close rechazados; límite e historial preservados; cierre no concedido | Resultado/verificación/rechazos por intento, conciliación y abandono autorizado si corresponde |
| Consulta estricta | Consultas sin archivos/cachés/actualización de evidencias; complete excluido de ese modo | Entradas/salidas y comparación de contenido/permisos/mtime |

## Categorías

La suite determinista del plugin y hook complementa E7; los fixtures de adaptador de esas suites no cuentan como delegación nativa. Las simulaciones o inspecciones de instrucciones no prueban ejecución. La instalación aislada/discovery E8 queda fuera de esta evaluación. No se atribuyen ahorros de costo/tiempo ni efectos de negocio sin medición comparable.

## Criterio de conclusión

Informar cada escenario como aprobado, fallido, bloqueado o no ejecutado con alcance y causas observadas. Confirmar el flujo nativo solamente con identidad/linaje atestados, comportamiento comprobado y estado real del controlador. No derivar aprobación de una release del plugin de esta evaluación. Preservar evidencias compactas, hashes y repositorios desechables hasta su verificación independiente.
