# Revisión final — YAML y perfiles configurables

Fecha: 2026-10-16. **Revisión completada con tres desajustes documentales abiertos. No se confirma todavía coherencia completa.** No se modificaron instrucciones, templates ni runtime durante esta revisión; solo se agregan este informe y sus evidencias. Sin commit, nueva versión, tag, push, publicación, instalación ni migración.

## Hallazgos

| ID | Prioridad | Ubicación | Evidencia e impacto | Corrección propuesta |
| --- | --- | --- | --- | --- |
| COH-01 | P2, media | [operations.md:35](../../plugins/spec-flow/harness/contracts/operations.md#governed-documents-and-gates) | Exige conservar un bloque JSON para los ocho kinds; contradice su sección de encoding y los ocho templates YAML. Todas las skills escritoras consultan estas instrucciones. | Distinguir nuevos encabezados YAML de fuentes JSON existentes, conservando los demás controles. |
| COH-02 | P2, media | [execution.md:49](../../plugins/spec-flow/harness/contracts/execution.md#target-controller-operations) | El ejemplo de capabilities no incluye model_catalog_reference/model_catalog. Reproducido: model_catalog_required antes de atestar la sesión. | Completar el ejemplo con inventario actual del host y evidencia; explicar run_id para perfiles congelados. No relajar validaciones. |
| COH-03 | P3, baja | [execution.md:63](../../plugins/spec-flow/harness/contracts/execution.md#evidence-and-stopping-rules) y ubicaciones relacionadas | Persisten instrucciones activas que fijan/nominan roles como Sol y Luna, pese a admitir modelos arbitrarios. Puede orientar una delegación incorrecta o dejar ambigua la prohibición de implementar desde converge. | Usar orquestador/implementador/revisor y sus perfiles congelados. Conservar nombres históricos y prefijos de compatibilidad. |

COH-03 también abarca execution.md:49,51,71; roles/implementer.md:13; roles/orchestrator.md:5; README.md:46,74; skills/converge/SKILL.md:16. El listado estructurado contiene archivos y líneas. Los IDs de este informe son locales y no sustituyen F-01/F-02/F-03 históricos de E7.

## Comprobaciones

- Dos revisiones independientes: parser/digests/templates y perfiles/flujo/instrucciones. Ambas detectaron COH-01; la segunda confirmó los otros dos hallazgos. No identificaron nuevos fallos concretos del runtime en el alcance revisado.
- Los archivos actuales del paquete coinciden exactamente con el snapshot probado en [perfiles configurables](configurable-profiles.md): 152 pruebas con fixtures YAML, 152 con JSON y 10 del hook. Se reutilizan esos resultados con comprobación fresca de hashes; no se presentan como suites completas reejecutadas hoy en esta revisión.
- Pruebas focalizadas nuevas: 16 de perfiles/CLI aprobadas. El revisor YAML ejecutó siete pruebas de formato aprobadas.
- Los ocho templates tienen frontmatter YAML y sus kinds canónicos correctos. Las revisiones confirmaron conservación de los contratos frente a sus fuentes JSON previas.
- Se comprobaron hashes de ambos manifiestos, esquema, hook handler, store/migration y componentes YAML preservados; se mantiene 3.0.1. El HEAD sigue en `3cb96fe43a5615b716ebf98ce63208e90ce2f953`; el conjunto YAML/perfiles es trabajo local sin commit.
- Las evidencias locales anteriores conservan sus checksums. Se mantienen las distinciones entre documentos, configuración JSON, registros internos, aprobaciones, ejecución y publicación.

No se detectaron alteraciones a atestación exacta, snapshots por run, perfiles históricos, restauración de paquetes, separación de sesiones, tres intentos, worktree/ownership ni gates de decisiones. El HARD-GATE de implement conserva la adaptación de perfil aprobada; esta revisión no lo modifica ni concede excepciones.

## Evidencias y siguiente paso

[Hallazgos estructurados](evidence/coherence-yaml-profiles/findings.json), [reproducción del ejemplo](evidence/coherence-yaml-profiles/example-reproduction.json), [pruebas focalizadas](evidence/coherence-yaml-profiles/focused-tests.txt), [revisiones independientes](evidence/coherence-yaml-profiles/independent-reviews.json), [verificación e inventario](evidence/coherence-yaml-profiles/verification.json) e [integridad](evidence/coherence-yaml-profiles/SHA256SUMS).

Corresponde corregir los tres textos y volver a verificar su coherencia antes de declarar cerrado el trabajo. Los hallazgos no justifican cambiar el runtime o flexibilizar sus controles. E7/E8 originales conservan fuentes/modelos/resultados históricos; no se ejecutó una nueva evaluación nativa ni se comprobó una instalación. Esta revisión no demuestra eficacia de modelos nuevos, seguridad exhaustiva ni disponibilidad real de un catálogo de host.
