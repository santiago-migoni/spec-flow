# Evidencia E7 — ef7897d

**APROBADA en los escenarios nativos ejercitados.** F-03 corregido; run anterior recuperado mediante el controlador, dos positivos cerrados y negativo abandonado preservando sus tres fallos. Cuatro propiedades liberadas. Sin E8 ni publicación.

- [Informe completo](../../e7-ef7897d.md).
- [Hallazgo original F-03](../e7-34d8909/native/F-03-recovery-after-retry-limit.md); [corrección y regresiones](../f03-fix/README.md).
- source-and-scope.json: candidato, autorización literal e inventario de la exportación.
- recovery/: operaciones del run anterior, comparaciones independientes y copia portable.
- native/: operaciones de cada fixture, atestaciones, interrupción/restauración, convergencia, cierres y copias portables.
- native-independent-check.json: nueve sesiones reales, árboles/commits/auditorías, estado final y pruebas independientes.
- control-invariants-independent-check.json: controles conservados y métodos afectados.
- deterministic-tests.*, hook-tests.*: 127 + 9 pruebas desde el candidato exportado.
- reproduction/: preparación y comprobaciones; no repetir scripts que crean fixtures sobre destinos existentes.
- preservation-summary.json y recovery/preservation.json: tres repositorios nuevos y uno recuperado.
- final-artifact-validation.json y SHA256SUMS: integridad y hashes de todos los archivos, salvo el propio SHA256SUMS.

Los snapshots y bundles son evidencia histórica. No restauran autorización, propiedad o identidad nativa. Las atestaciones conservan referencias/hashes del host, sin copiar logs privados completos.
