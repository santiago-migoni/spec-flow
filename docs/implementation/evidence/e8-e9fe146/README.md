# Evidencias E8 — e9fe146

[Informe completo](../../e8-e9fe146.md) · [Hallazgos y observación](findings.json) · [Validación final](final-artifact-validation.json) · [Checksums](SHA256SUMS)

- `source-and-scope.json`: commit, autorización, nombres separados, hashes y estado Git inicial.
- `candidate-package.tar`: exportación exacta de Git.
- `tested-package.tar`, `installed-package.json`: copia temporal e inventario instalado con correspondencia exacta.
- `installation-operations.jsonl`: comandos soportados y resultados de instalación/retirada.
- `installed-runtime.*`, `installed-hooks.*`: suites 152 + 10 desde cache instalado.
- `discovered-skills.json`, `installed-bootstrap-*`, `installed-yaml-templates.json`, `installed-references-check.json`: cliente nuevo, arranque, ocho templates y 75 referencias.
- `protected-before.json`, `protected-during.json`, `cleanup-check.json`: conservación del plugin estable/configuración y retirada de las identidades temporales.
- `discovery-server-sandbox-attempt.stderr`: intento inicial rechazado por SQLite de solo lectura; el reintento autorizado sí descubrió las skills.
- `preservation.json`, `scratch/`, `reproduction/`: preservación y scripts con las rutas de esta evaluación. Adaptar rutas e identidades al reproducir; no importar snapshots como autoridad.

No se copian config privada completa ni credenciales. Los archivos son evidencia histórica, sin instalación, confianza de hooks, aprobaciones ni autoridad activa. La prueba no modifica el paquete candidato ni su versión y no publica.
