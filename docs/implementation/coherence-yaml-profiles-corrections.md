# Cierre de coherencia documental — YAML y perfiles

Fecha: 2026-10-16. **COH-01, COH-02 y COH-03 resueltos; sin nuevos desajustes detectados en el alcance revisado.** Este informe continúa la [revisión anterior](coherence-yaml-profiles.md), cuyos hallazgos abiertos y evidencias se conservan como historia.

## Correcciones

| ID | Corrección y resultado |
| --- | --- |
| COH-01 | operations.md distingue encabezados YAML nuevos de documentos JSON existentes, sin cambiar kinds, IDs, revisión, pins, aprobación ni autorización. |
| COH-02 | execution.md incluye un ejemplo completo de capabilities con catálogo de modelos/esfuerzos y referencia; aclara que es ilustrativo y exige observaciones reales del host. Explica run_id para preflight de un run existente. |
| COH-03 | Se reemplazan referencias activas a Sol/Luna por orquestador/implementador/revisor y perfiles congelados en execution, roles, README, adaptador y converge. Se mantienen los perfiles históricos y los prefijos luna_/review_. |

No se modificaron código Python, pruebas, templates, manifiestos, bloques HARD-GATE ni controles del runtime en esta corrección. La prohibición de implementar desde converge queda expresada por rol, sin cambiar su límite funcional.

## Verificación

- 29 pruebas focalizadas de perfiles, CLI, YAML y estructura del paquete: PASS.
- Ejemplo extraído directamente de execution.md: aceptado por el adaptador con logs e inventario sintéticos coincidentes. Al omitir el catálogo sigue fallando model_catalog_required; con una sesión de otro modelo sigue fallando host_profile_mismatch.
- Las fuentes de runtime, pruebas, templates y controles coinciden con el snapshot de las suites completas previas: 152 YAML, 152 JSON y 10 hook. Se reutilizan esos resultados, sin afirmar otra ejecución completa.
- Revisión independiente: los tres hallazgos documentales están resueltos, sin nuevos hallazgos en el alcance revisado. No quedan instrucciones activas que fijen modelos por nombre en los documentos examinados.
- Comparación de inventarios: solo seis documentos del paquete y README cambiaron desde la revisión; bloques de gates intactos. La versión sigue en 3.0.1 y HEAD no cambió.
- Checksums de las evidencias YAML, perfiles y revisión original intactos; los registros originales no se reescribieron.

[Hallazgos resueltos](evidence/coherence-yaml-profiles-corrections/resolved-findings.json), [ejemplo y rechazos](evidence/coherence-yaml-profiles-corrections/documented-example-check.json), [29 pruebas](evidence/coherence-yaml-profiles-corrections/focused-tests.txt), [revisión independiente](evidence/coherence-yaml-profiles-corrections/independent-review.json), [inventario/verificación](evidence/coherence-yaml-profiles-corrections/verification.json) e [integridad](evidence/coherence-yaml-profiles-corrections/SHA256SUMS).

## Límites

Trabajo local sin commit, nueva versión, tag, push, publicación, instalación ni migración. No se ejecutaron modelos reales ni nuevas E7/E8; las evaluaciones históricas conservan sus fuentes/modelos y alcances. Cierre de coherencia documental no equivale a autorizar o demostrar una publicación ni disponibilidad/eficacia de modelos en un host real.
