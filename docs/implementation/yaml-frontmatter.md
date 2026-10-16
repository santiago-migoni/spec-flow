# Encabezado YAML — implementación local

**Verificación determinista aprobada.** Sin corte de versión, commit, tag, push, publicación, actualización de instalación ni migración de proyectos. Los manifiestos permanecen en **3.0.1**. Base: `3cb96fe43a5615b716ebf98ce63208e90ce2f953`.

## Cambios

Los ocho templates canónicos usan frontmatter YAML antes del título. Conservan campos, registros, prosa y bloques generados; solo se normalizan líneas en blanco junto al contrato trasladado. Skills, contratos compartidos, README y AGENTS explican la creación, compatibilidad y conversión explícita. Backlog e informes no reciben un contrato o aprobación nuevos.

El lector admite YAML y el bloque JSON existente. Los digests JSON conservan el algoritmo anterior. YAML utiliza el dominio `spec-flow-yaml-v1`, el contrato normalizado sin status superior y el cuerpo sin el bloque generado estrictamente validado. No se equiparan automáticamente digests entre formatos. Cambios de decisiones, incluidos estados anidados de releases, invalidan pins.

La escritura de estados/cierre preserva el formato. Convertir una fuente aprobada requiere autorización, revisión/aprobación, adopción downstream y reconciliación de ejecución según los controles existentes. No hay conversión implícita al consultar, aprobar o reanudar. CLI, manifiestos, eventos, paquetes y registros derivados siguen en JSON/JSONL.

PyYAML 6.0.3 puro Python está incluido con fuentes originales, licencia MIT y procedencia/hash del wheel. No se instala una dependencia global. El lector restringe tipos a datos compatibles con JSON y rechaza duplicados, claves no textuales, tags, anchors, aliases, merges y números no finitos. Limita tamaño, profundidad y nodos. El emisor evita aliases y cita cadenas ambiguas.

## Pruebas y controles

| Comprobación | Resultado |
| --- | --- |
| Suite con fixtures YAML, formatos y cadenas mixtas | 138 pruebas PASS |
| Misma suite con fixtures JSON | 138 pruebas PASS |
| Hook con YAML y controles de aprobación | 10 pruebas PASS |
| Ocho templates frente a HEAD | Mismos contratos, prosa y bloques generados, salvo líneas en blanco |
| HARD-GATE de 14 skills | Bloques literales intactos |
| Manifiestos, esquema, engine, migration, adapter, store y handler del hook | Bytes iguales a HEAD |
| Paquete antes/después de cada suite | Fuentes sin mutación |
| Dependencia vendorizada | 16 fuentes Python idénticas al wheel; licencia conservada |

Se reprodujeron fallos antes de implementar el lector y un caso del emisor que producía aliases; están cubiertos por pruebas. Se usan proyectos Git desechables y adaptadores de prueba explícitos. Las suites cubren cierre, auditoría, recuperación, permisos, fuentes obsoletas y cobertura. No equivalen a ejecución nativa con modelos.

[Evidencia estructurada](evidence/yaml-frontmatter/verification.json), [suite YAML](evidence/yaml-frontmatter/yaml-suite.txt), [compatibilidad JSON](evidence/yaml-frontmatter/legacy-json-suite.txt), [hook](evidence/yaml-frontmatter/hook-suite.txt), [reproductor](evidence/yaml-frontmatter/verify.py) e [integridad](evidence/yaml-frontmatter/SHA256SUMS).

## Trazabilidad y límites

E7/E8 y las evidencias publicadas conservan sus fuentes y resultados históricos. No se repitieron E7/E8 ni una instalación del candidato. No se declara listo para publicación: una eventual release requiere autorización y verificaciones aplicables. El cambio permanece local para revisión.
