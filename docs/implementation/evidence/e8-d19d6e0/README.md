# Evidencia — instalación aislada v3.0.0 / d19d6e0

APROBADA en instalación, descubrimiento fresco y arranque instalado. Instalación estable intacta; temporales retirados. Sin push/tag/publicación.

- [Informe](../../e8-d19d6e0.md).
- source-and-scope.json y refs-before.txt: fuente, autorización, identidades, 115 hashes y referencias protegidas.
- installed-version-check.json e installed-package.json: manifiestos reales 3.0.0, 115 archivos instalados iguales a la copia, 113 recursos iguales al candidato.
- installed-runtime.* e installed-hooks.*: 127 + 9 tests desde el cache instalado.
- discovered-skills.json: 14 skills habilitadas, cliente nuevo app-server.
- installed-bootstrap-* e installed-references-check.json: ocho operaciones, alcance y 54 referencias resueltas.
- protected-before.json, protected-during.json y cleanup-check.json: protección y limpieza verificadas.
- installation-operations.jsonl: siete operaciones CLI soportadas con entradas/salidas/exits.
- Tablas CLI .txt.gz y cli-output-preservation.json: salidas originales preservadas sin pérdida.
- candidate-package.tar, tested-package.tar, preservation.json y scratch/: archivos portables y snapshots. El archivo probado proviene de la copia temporal previamente comprobada idéntica al cache, que luego se retiró.
- reproduction/: scripts usados; no repetir instalación/preparación sobre destinos existentes ni sobrescribir evidencia comprometida.
- final-artifact-validation.json y SHA256SUMS: integridad final de todos los archivos salvo el propio inventario de hashes.

Los archivos históricos no otorgan confianza ni autorización. No se copiaron credenciales o configuración privada completa.
