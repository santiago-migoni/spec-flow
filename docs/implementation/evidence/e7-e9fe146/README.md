# Evidencias E7 — e9fe146

[Informe y matriz EV-01–EV-15](../../e7-e9fe146.md) · [Hallazgos/observaciones](findings.json) · [Verificación nativa independiente](native-independent-check.json) · [Integridad](final-integrity.json) · [Checksums](SHA256SUMS)

- `source-and-scope.json`, `candidate-package.tar`: candidato, autorización, hashes e identidad de fuente.
- `deterministic/`: 152 pruebas del controlador y 10 de hooks, comandos/salidas/códigos/duración.
- `native/{fresh,legacy,negative}/operations.jsonl`: entradas y salidas exactas del controlador.
- `native/legacy-initial/`: intento inicial conservado, bloqueado correctamente y abandonado mediante controlador.
- `native/*/snapshot`, `repository.bundle`, `preservation.json`: cuatro proyectos históricos preservados; no restauran autoridad activa.
- `native/session-context.json`, `native-independent-check.json`: atestaciones compactas de sesiones reales; no se copian logs privados completos.
- `native/profile-snapshot.json`, `native/EV11-pressure-assessment.json`: snapshot de perfiles y evaluación hipotética de instrucciones, categorías separadas.
- `consultation-tests.json`, `migration-independent-check.json`, `completion-staleness-negative-probes.json`, `native-prerequisite-negative-probes.json`: comprobaciones complementarias de producción.
- `reproduction/`: preparación y verificadores. Las rutas/UUID son de esta ejecución; nuevos runs requieren sus propias decisiones, sesiones y autoridad.

Los scripts de preparación conservan los comandos realmente usados, con rutas históricas de fixtures previos como origen de contenido sintético. No importan su evidencia como resultados actuales. No ejecutar scripts históricos sin revisar el alcance y adaptar rutas. El script de informe vuelve a insertar punteros; preservado como evidencia, no como operación idempotente.
