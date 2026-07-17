# Backlog

Ideas, trabajo diferido y futuras features aún no convertidas en spec. Ordenado por prioridad — los ítems se eliminan automáticamente cuando `spec-flow:specify` los convierte en un spec.

## P0 — Crítica

## P1 — Alta

- [ ] B007 Cambiar el Verification Step de `implement` de "trazar cada acceptance scenario a file:line" a "ejecutar el flujo afectado y observar el comportamiento" (integrar con la skill `verify` del ecosistema) — en el dogfooding todos los bugs reales (restic --no-lock, chown de filestore, locks huérfanos, versión sin pinear) aparecieron solo corriendo el código, nunca trazándolo (anotado 2026-07-12, de la sesión de dogfooding en odoo-infrastructure)
- [ ] B013 Hacer commit de cada artefacto (`constitution.md`, `spec.md`, `plan.md`, `tasks.md`) inmediatamente después de que el usuario lo aprueba, no solo al cierre en `finishing-branch` — hoy ningún phase skill toca git tras la aprobación, así que no queda historial commiteado por etapa hasta el final de la feature; complementa al gate de aprobación ya entregado (ex-B005, feature 003, v0.8.0) — la señal `Status: Approved` que ese gate consume es el punto natural donde este commit dispararía (anotado 2026-07-17, pedido explícito del usuario)

## P2 — Media

- [ ] B003 Agregar un skill de solo lectura spec-flow:status que liste cada .specs/NNN-*/spec.md y su campo Estado en una tabla, para dar visibilidad cuando hay múltiples features en curso (anotado 2026-07-04, de la sesión de brainstorming)
- [ ] B008 Centralizar el toil repetitivo en scripts: `bump-version.sh` (R00→R01 post-aprobación, hoy manual y duplicado en 6 skills) y `cut-release.sh <version>` (cortar `[Unreleased]`→`[X.Y.Z]` en CHANGELOG + emitir solo esa sección para `gh release`) — ambos patrones se repitieron idénticos a mano en cada release del dogfooding. Nota: la derivación de heading de CHANGELOG y bump SemVer desde el historial de commits ya se entregó en `finishing-branch` (v0.6.0); lo que queda abierto acá es extraer esos dos scripts reutilizables (anotado 2026-07-12, de la sesión de dogfooding en odoo-infrastructure)
- [ ] B009 Reducir `converge` a una sola pasada cuando hay findings: tras aprobar y aplicar los fixes, re-verificar en la misma invocación en vez de exigir re-correr converge para el "Converged" limpio (preservando el append-only con append + re-check) — en el dogfooding cada feature con findings obligó a dos invocaciones de converge (anotado 2026-07-12, de la sesión de dogfooding en odoo-infrastructure)
- [ ] B010 Agregar un hook de validación de frontmatter al escribir en `.specs/` (campos `status`/`version`/`code` bien formados, transiciones de estado válidas) — hoy son convención y un valor mal tipeado o un gate salteado pasan en silencio (anotado 2026-07-12, de la sesión de dogfooding en odoo-infrastructure)
- [ ] B011 Extraer la tabla de las 7 fases a una fuente única referenciada en vez de re-tipeada en README + using-spec-flow + cada SKILL + CLAUDE.md — el propio CLAUDE.md admite que un cambio debe aterrizar en las tres copias; es deuda de mantenimiento (anotado 2026-07-12, de la sesión de dogfooding en odoo-infrastructure)

## P3 — Baja

- [ ] B012 Ofrecer un "carril liviano" para cambios triviales (fases colapsadas, o `specify` estima el tamaño y sugiere saltear fases) — hoy model/effort es fijo por fase y una feature de una línea corre el mismo `opus/high` en `plan` que un stack completo (anotado 2026-07-12, de la sesión de dogfooding en odoo-infrastructure)

## Considerado y descartado (no es cola de trabajo — ayuda memoria)

Ideas evaluadas y NO adoptadas a propósito. No llevan ID ni entran en el flujo de `specify`; viven acá para no re-proponerlas sin una justificación nueva. Reconsiderar solo si aparece una necesidad concreta que rompa el motivo del descarte.

- **`spec-flow:reviewer` — skill opcional (estilo clarify/analyze) que revisa el código entre `implement` y `converge`** contra spec/plan/constitution. Descartado: se pisa con tres revisores que ya existen — `analyze` (cross-check pre-implement), `converge` (código vs intención) y `/code-review` del ecosistema. Un cuarto revisor agrega superficie de mantenimiento sin cubrir un hueco real. Reconsiderar solo si aparece un tipo de revisión que ninguno de los tres hace. (evaluado 2026-07-17, era B004)
- **`rules/` con `paths:` que carguen recordatorios contextuales por proyecto durante `implement`** (ej. `paths: ["docker-compose*.yml"]` → recordar reconciliar el presupuesto de RAM con la constitución) — anticiparía findings recurrentes en vez de detectarlos tarde en converge. Descartado: es exactamente el "framework general de extensions/hooks configurable por proyecto" que la constitución rechaza (R01, y reafirmado en R02, que acota la excepción de hooks *solo* al gate de aprobación del propio plugin). Reconsiderar solo si se enmienda esa decisión de la constitución con una necesidad concreta. (evaluado 2026-07-17, era B006, de la sesión de dogfooding en odoo-infrastructure)
- **`agents/` (subagentes con `tools:` restringidas) para `analyze`/`converge`** — haría cumplible su naturaleza read-only por permiso en vez de por prosa. Descartado: choca con el "no subagent overhead" que es identidad del plugin (está en su propia `description`); la simplicidad y predecibilidad valieron más que la garantía extra en todo el dogfooding. Reconsiderar solo si el read-only por prosa llegara a fallar de verdad. (evaluado 2026-07-12)
- **`workflows/` para orquestar la cadena o el loop `analyze→fix→re-analyze`** — descartado: el flujo lineal manual es una *feature*, no un límite; automatizar el camino feliz re-introduce la complejidad que el plugin evita a propósito. (evaluado 2026-07-12)
- **`output-styles/` para un estilo de reporte de findings** — descartado por marginal: bajo impacto frente al costo de mantener otro módulo. (evaluado 2026-07-12)
- **IDs numerados de requisitos (`FR-NNN`/`SC-NNN`) en spec-template.md** — permitiría a `spec-flow:analyze` mapear cobertura de forma exacta en vez de por inferencia de palabras clave. Descartado: al rediseñar `spec-template.md`, `analyze`/`converge` ya tratan `USn/ACn` como el ID atómico del requisito — una segunda numeración fragmentaría la trazabilidad en vez de resolverla (ver CHANGELOG v0.7.0). Reconsiderar solo si `USn/ACn` demuestra ser insuficiente como ID en la práctica. (evaluado 2026-07-17, era B001)
