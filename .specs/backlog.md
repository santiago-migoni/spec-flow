# Backlog

Ideas, trabajo diferido y futuras features aún no convertidas en spec. Ordenado por prioridad — los ítems se eliminan automáticamente cuando `spec-flow:specify` los convierte en un spec.

## P0 — Crítica

## P1 — Alta

- [ ] B005 Aplicar el gate de aprobación entre fases con un hook (settings.json `Stop`/`PreToolUse`) en vez de prosa — hoy el `<HARD-GATE>` solo bloquea por existencia de artefacto, no por aprobación explícita del usuario, y el modelo puede encadenar fases (tasks→implement) sin OK; en el dogfooding esto falló de verdad y la regla terminó en la memoria de usuario en vez de en el plugin. Implica decidir si el plugin pasa de "solo prompts" a "prompts + hooks aplicados" (anotado 2026-07-12, de la sesión de dogfooding en odoo-infrastructure)
- [ ] B006 Agregar `rules/` con `paths:` que carguen recordatorios contextuales ligados a principios de la constitución durante `implement` (ej. `paths: ["docker-compose*.yml"]` → "cambio de sizing = actualizar presupuesto de RAM + reconciliar con la constitución") — anticipa findings recurrentes en vez de detectarlos tarde en converge; en el dogfooding el mismo finding de RAM apareció en dos features seguidas (anotado 2026-07-12, de la sesión de dogfooding en odoo-infrastructure)
- [ ] B007 Cambiar el Verification Step de `implement` de "trazar cada acceptance scenario a file:line" a "ejecutar el flujo afectado y observar el comportamiento" (integrar con la skill `verify` del ecosistema) — en el dogfooding todos los bugs reales (restic --no-lock, chown de filestore, locks huérfanos, versión sin pinear) aparecieron solo corriendo el código, nunca trazándolo (anotado 2026-07-12, de la sesión de dogfooding en odoo-infrastructure)

## P2 — Media

- [ ] B001 Agregar IDs numerados de requisitos FR-NNN/SC-NNN a spec-template.md para que spec-flow:analyze pueda mapear la cobertura de tareas de forma exacta en vez de por inferencia de palabras clave (anotado 2026-07-04, de la sesión de brainstorming)
- [ ] B003 Agregar un skill de solo lectura spec-flow:status que liste cada .specs/NNN-*/spec.md y su campo Estado en una tabla, para dar visibilidad cuando hay múltiples features en curso (anotado 2026-07-04, de la sesión de brainstorming)
- [ ] B004 Agregar spec-flow:reviewer, skill opcional (mismo estilo que clarify/analyze, sin subagentes) que corre después de implement y antes de converge, revisando el código escrito contra spec/plan/constitution, sin tocar los gates de la cadena principal (anotado 2026-07-04, de discusión sobre roles en el flujo)
- [ ] B008 Centralizar el toil repetitivo en scripts: `bump-version.sh` (R00→R01 post-aprobación, hoy manual y duplicado en 6 skills) y `cut-release.sh <version>` (cortar `[Unreleased]`→`[X.Y.Z]` en CHANGELOG + emitir solo esa sección para `gh release`) — ambos patrones se repitieron idénticos a mano en cada release del dogfooding (anotado 2026-07-12, de la sesión de dogfooding en odoo-infrastructure)
- [ ] B009 Reducir `converge` a una sola pasada cuando hay findings: tras aprobar y aplicar los fixes, re-verificar en la misma invocación en vez de exigir re-correr converge para el "Converged" limpio (preservando el append-only con append + re-check) — en el dogfooding cada feature con findings obligó a dos invocaciones de converge (anotado 2026-07-12, de la sesión de dogfooding en odoo-infrastructure)
- [ ] B010 Agregar un hook de validación de frontmatter al escribir en `.specs/` (campos `status`/`version`/`code` bien formados, transiciones de estado válidas) — hoy son convención y un valor mal tipeado o un gate salteado pasan en silencio (anotado 2026-07-12, de la sesión de dogfooding en odoo-infrastructure)
- [ ] B011 Extraer la tabla de las 7 fases a una fuente única referenciada en vez de re-tipeada en README + using-spec-flow + cada SKILL + CLAUDE.md — el propio CLAUDE.md admite que un cambio debe aterrizar en las tres copias; es deuda de mantenimiento (anotado 2026-07-12, de la sesión de dogfooding en odoo-infrastructure)

## P3 — Baja

- [ ] B012 Ofrecer un "carril liviano" para cambios triviales (fases colapsadas, o `specify` estima el tamaño y sugiere saltear fases) — hoy model/effort es fijo por fase y una feature de una línea corre el mismo `opus/high` en `plan` que un stack completo (anotado 2026-07-12, de la sesión de dogfooding en odoo-infrastructure)

## Considerado y descartado (no es cola de trabajo — ayuda memoria)

Ideas evaluadas y NO adoptadas a propósito. No llevan ID ni entran en el flujo de `specify`; viven acá para no re-proponerlas sin una justificación nueva. Reconsiderar solo si aparece una necesidad concreta que rompa el motivo del descarte.

- **`agents/` (subagentes con `tools:` restringidas) para `analyze`/`converge`** — haría cumplible su naturaleza read-only por permiso en vez de por prosa. Descartado: choca con el "no subagent overhead" que es identidad del plugin (está en su propia `description`); la simplicidad y predecibilidad valieron más que la garantía extra en todo el dogfooding. Reconsiderar solo si el read-only por prosa llegara a fallar de verdad. (evaluado 2026-07-12)
- **`workflows/` para orquestar la cadena o el loop `analyze→fix→re-analyze`** — descartado: el flujo lineal manual es una *feature*, no un límite; automatizar el camino feliz re-introduce la complejidad que el plugin evita a propósito. (evaluado 2026-07-12)
- **`output-styles/` para un estilo de reporte de findings** — descartado por marginal: bajo impacto frente al costo de mantener otro módulo. (evaluado 2026-07-12)
