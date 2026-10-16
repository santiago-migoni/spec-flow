# Evidencia E7 — 34d8909

**NO APROBADA: F-03 HIGH.** La corrección F-02 y la recuperación de los tres runs anteriores están verificadas. Dos nuevos escenarios positivos cerraron; el negativo retiene propiedad tras agotar tres intentos.

- Informe: [e7-34d8909.md](../../e7-34d8909.md).
- `source-and-scope.json`: candidato, autorización e inventario SHA-256 del paquete exportado.
- `deterministic-tests.*`, `hook-tests.*`: 123 + 9 pruebas aprobadas.
- `recovery/`: recuperación por controlador, comparación independiente, snapshots y tres bundles.
- `native/`: operaciones CLI completas, informes, snapshots y tres bundles de la nueva ejecución.
- `native-independent-check.json`: atestación de nueve sesiones, dos cierres, tres fallos nativos y verificación independiente de las suites fijas.
- `preservation-summary.json`, `recovery/preservation-summary.json`: inventarios de preservación.
- `reproduction/`: preparación, comprobaciones complementarias, verificación final y preservación. Los scripts que crean fixtures no deben repetirse sobre los mismos destinos.
- `final-artifact-validation.json`: integridad final del paquete, formatos, snapshots, propiedad y bundles.
- `SHA256SUMS`: hashes de todos los archivos de este directorio salvo el propio inventario.

Los snapshots y registros de propiedad son históricos. No restauran autoridad ni justifican liberar un run manualmente. El negativo conserva su propiedad activa para recuperación mediante el controlador. Los logs del host se referencian mediante atestaciones compactas, sin copiar sesiones privadas completas.
