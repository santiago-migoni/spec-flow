# Perfiles configurables — implementación local

Estado: **verificaciones deterministas aprobadas**, sin commit, cambio de versión, tag, push, publicación, instalación ni migración de proyectos del usuario. Los manifiestos siguen en **3.0.1**.

## Alcance aprobado

Elegir modelo y esfuerzo por rol en `.spec-flow/config.json`. Valores iniciales aprobados: orquestador gpt-6.1-sol/low, implementador gpt-6-luna/high y revisor independiente gpt-6.1-sol/medium. Las configuraciones existentes válidas no se sustituyen al inicializar.

El trabajo parte de HEAD `3cb96fe43a5615b716ebf98ce63208e90ce2f953` más los cambios YAML locales previos, conservados. [Snapshot anterior a esta funcionalidad](evidence/configurable-profiles/before.json) registra sus hashes; el HEAD no se presenta como commit de estos cambios locales.

## Implementación

- Validación central de tres roles con exactamente id y effort; IDs sin espacios y esfuerzos reconocidos. retry_limit permanece fijo en 3. No hay allowlist de familias ni sustitución silenciosa.
- `configure-profiles` valida y guarda preferencias atómicamente, de forma idempotente. Es una operación mutable, ajena a consulta estricta; no aprueba documentos ni autoriza ejecución. Agentes usan el controlador para respetar la protección de rutas del registro; el usuario puede editar el JSON manualmente.
- Nuevos runs guardan profiles en started. Estado reconstruido, recuperación, takeover, atestación, revisión/cierre y paquetes toman esa copia, aunque cambie config.json. Los cambios afectan únicamente runs nuevos.
- Runs históricos sin snapshot usan el perfil fijo histórico Sol/high–Luna/high–Sol/high. No se reescriben eventos/evidencias ni se agrega el campo a sus paquetes; la restauración conserva sus hashes. Un snapshot malformado bloquea, sin recurrir a valores por defecto.
- Nuevos preflights nativos exigen inventario de modelos/esfuerzos del host y una referencia de evidencia. El controlador comprueba y conserva la declaración, pero no enumera modelos ni autentica por sí mismo referencias externas. Modelos ausentes o esfuerzos no disponibles bloquean. Las sesiones y los spawns reales deben coincidir exactamente; el catálogo declarado no reemplaza la atestación.
- Un implementador activo, revisor en sesión separada, worktree aislado, ownership, aprobaciones, pins, tres intentos y controles de evidencia/recuperación permanecen. El HARD-GATE de implement conserva sus requisitos; solo su cláusula de perfil fijo se sustituye por atestación del perfil seleccionado y congelado. Los bloques de las otras skills permanecen literales.
- Instrucciones de roles, implement, bootstrap, review-release, contratos, README y AGENTS se alinearon con el perfil por rol. La selección de modelos no modifica la autoridad de ejecución, integración o publicación.

[Contrato de configuración y ejemplos](../../plugins/spec-flow/harness/contracts/profiles.md).

## Pruebas

| Comprobación | Resultado |
| --- | --- |
| Suite local con fixtures YAML, incluyendo perfiles y CLI | 152 pruebas PASS |
| Misma suite con fixtures JSON | 152 pruebas PASS |
| Hook y controles de aprobación | 10 pruebas PASS |
| CLI real: initialize y configure-profiles | PASS en proyecto desechable; sin runs creados |
| Configuración existente, edits durante run y reconstrucción de estado | PASS |
| Modelos/esfuerzos incorrectos, catálogo ausente/duplicado/no disponible y snapshots corruptos | Rechazo esperado |
| Spawns cifrados con revisor configurado y cambio de esfuerzo | Coincidencia exacta requerida |
| Paquetes, ownership, revisión independiente, cierre y recuperación | Suite PASS |
| Revisión independiente | Sin hallazgos accionables; core y delta CLI revisados |

La primera prueba pública detectó que faltaba la opción configure-profiles en argparse. Se reprodujo con una regresión CLI, se agregó a la entrada portable y la prueba pasó. La revisión independiente comprobó luego esa corrección. Las salidas finales y el smoke corresponden al código final, con fuentes sin cambios durante las comprobaciones JSON y CLI.

[Evidencia estructurada](evidence/configurable-profiles/verification.json), [suite YAML](evidence/configurable-profiles/yaml-suite.txt), [suite JSON](evidence/configurable-profiles/legacy-json-suite.txt), [hook](evidence/configurable-profiles/hook-suite.txt), [smoke CLI](evidence/configurable-profiles/cli-smoke.json), [revisión](evidence/configurable-profiles/independent-review.json), [reproductor](evidence/configurable-profiles/verify.py) e [integridad](evidence/configurable-profiles/SHA256SUMS).

## Límites y trazabilidad

No se ejecutaron modelos reales ni nuevas E7/E8, no se instaló el candidato y no se afirma eficacia/calidad de combinaciones nuevas. Las pruebas nativas del adaptador usan logs sintéticos etiquetados como fixtures. E7/E8 históricas y los informes previos conservan sus fuentes y perfiles evaluados. La verificación YAML previa es un snapshot anterior; las suites de este informe prueban el conjunto local posterior con perfiles configurables.

El usuario conserva su instalación y configuraciones de proyectos; los ejemplos y cambios de preferencias se probaron únicamente en proyectos desechables. Una futura publicación e instalación requieren su autorización y las verificaciones aplicables al candidato.
