# Evidencia E8 — ef7897d

APROBADA en el alcance de instalación aislada, descubrimiento fresco y arranque instalado. La instalación estable está intacta; plugin y marketplace temporales retirados. Sin publicación.

- [Informe](../../e8-ef7897d.md).
- source-and-scope.json: commit exacto, autorización e inventarios del candidato y copia con identidad separada.
- protected-before.json, protected-during.json, cleanup-check.json: instalación estable y configuración protegidas antes/durante/después.
- installation-operations.jsonl y listados before/after (tablas CLI en .txt.gz, bytes originales conservados y verificables en cli-output-preservation.json): registro/instalación y limpieza por CLI soportado.
- installed-package.json: igualdad de 115 archivos con la copia de prueba; 113 recursos sin cambio respecto al candidato.
- installed-runtime.* y installed-hooks.*: suites 127 + 9 desde el cache instalado.
- discovered-skills.json: 14 skills habilitadas en cliente nuevo app-server; no acredita refresco de chats abiertos.
- installed-bootstrap-check.json, installed-bootstrap-operations.*: smoke real del runtime instalado y límites de autoridad.
- installed-references-check.json: 54 referencias locales y recursos resueltos.
- evaluator-notes.json: aserciones del evaluador corregidas, sin modificar el candidato.
- candidate-package.tar, tested-package.tar, preservation.json y scratch/: archivos portables y snapshots; procedencia explícita de la copia byte-idéntica al cache.
- reproduction/: scripts usados. No repetir preparación, instalación o smoke sobre los mismos destinos ya existentes; verificar identidades y estado antes de cualquier nueva instalación.
- final-artifact-validation.json y SHA256SUMS: integridad de los archivos preservados, salvo el propio inventario de hashes.

Los archivos portables no instalan plugins ni otorgan confianza o autorización. No se copiaron credenciales ni la configuración privada completa del usuario.
