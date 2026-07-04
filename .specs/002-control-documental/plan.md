# Plan: Tabla de Control Documental

| Nombre | Código | Versión | Fecha |
|---|---|---|---|
| control-documental | PLAN-002 | R00 | 2026-07-04 |

## Enfoque

Dos frentes: (1) modificar los 4 templates de `assets/` y las instrucciones de los `SKILL.md` correspondientes (`constitution`, `specify`, `plan`, `tasks`) para que escriban/lean la nueva tabla Name/Code/Version/Date en vez de los campos sueltos actuales; (2) aplicar retroactivamente la tabla a los documentos "vivos" — `.specs/constitution.md` y los propios `spec.md`/`plan.md`/`tasks.md` de esta feature (002) — dejando sin tocar los documentos de features ya `Converged` (001), igual que decidimos con el rename de `specs/` → `.specs/`: cambio limpio hacia adelante, sin migración retroactiva de lo ya archivado.

## Constitution Check

- **Tech stack**: sin cambios — markdown puro, coherente con la constitution.
- **Code principles**: la tabla es una convención de formato dentro de cada `SKILL.md`/template existente, no un mecanismo nuevo de scripts ni de validación externa — cumple "hard gates se verifican pidiéndole a Claude que chequee, no con scripts". No se agrega ningún hook ni `extensions.yml`.
- **Constraints**: los templates (`skills/*/assets/*-template.md`) llevan los encabezados en inglés, igual que el resto del plugin — decidido en `clarify`. El campo `**Estado**` no cambia de nombre ni posición semántica, así que `converge`/`finishing-branch` (que lo leen para sus gates) no requieren cambios.

## Architecture

**Esquema de Código** (spec/plan/tasks únicamente, la constitution no lleva Código — US2): `SPEC-NNN` / `PLAN-NNN` / `TASKS-NNN`, mismo `NNN` de 3 dígitos que ya usa la carpeta de la feature (reutiliza `next-feature-number.sh`, sin generar un contador nuevo).

**Esquema de Versión**: arranca en `R00` en la primera escritura. Sube en uno únicamente cuando se edita un documento **ya aprobado** por el usuario, fuera de su propio ciclo de borrador — es decir, el loop existente "draft → resumen → pedido de aprobación → (si pide cambios) editar → repetir resumen" de `constitution`/`specify`/`plan`/`tasks` nunca bumpea Versión mientras se repite (el documento sigue sin aprobar, se queda en `R00` sin importar cuántas vueltas dé). Solo una edición posterior a que el usuario ya dijo "aprobado" — típicamente en una sesión posterior, cuando el usuario pide modificar un documento que ya había confirmado — sube la Versión.

**Tabla por tipo de documento**:
- `constitution.md`: `| Name | Version | Date |` (sin columna Code)
- `spec.md` / `plan.md` / `tasks.md`: `| Name | Code | Version | Date |`, donde `Name` es el `short-description` en kebab-case de la carpeta de la feature (ej. `control-documental`)

**Registro de Enmiendas** (`## Amendments Log` en el template en inglés, `## Registro de Enmiendas` cuando se traduce): exclusivo de `constitution.md`. Se agrega una línea `- RNN (YYYY-MM-DD): <qué cambió y por qué>` solo cuando ocurre una edición post-aprobación real de los principios — no se agrega una línea por el simple hecho de reformatear la constitution ya existente con esta nueva tabla (eso no es una enmienda de contenido, es la aplicación mecánica de este mismo feature).

**Referencias cruzadas eliminadas**: las líneas `**Spec**:`/`**Plan**:` que hoy tienen `plan-template.md`/`tasks-template.md` se eliminan — el Código compartido (mismo `NNN`) ya vincula los documentos entre sí (decidido en `clarify`).

**Retroactividad acotada a documentos vivos**: `.specs/constitution.md` se reformatea ahora con `Name: spec-flow`, `Version: R00` (la aprobada hasta hoy, sin enmienda nueva) y `Date` = la fecha de su última aprobación real (2026-07-04, sin cambiar). Los propios `spec.md`/`plan.md` (este archivo) y luego `tasks.md` de la feature 002 también adoptan la tabla al escribirse/reescribirse durante `implement`, porque todavía no fueron `Converged`. La feature `001-artifact-and-quality-skills`, ya `Converged`, queda con su formato original — no se retrofitea, mismo criterio que ya aplicamos a `specs/` → `.specs/`.

## File Structure

```text
skills/constitution/assets/constitution-template.md   ← modificado: tabla Name/Version/Date + sección Amendments Log
skills/constitution/SKILL.md                           ← modificado: regla de versión (R00 hasta aprobación) + cuándo agregar línea al Amendments Log
skills/specify/assets/spec-template.md                 ← modificado: tabla Name/Code/Version/Date reemplaza **ID**/**Creado**; **Estado** se mantiene debajo
skills/specify/SKILL.md                                ← modificado: Código = SPEC-NNN, regla de versión
skills/plan/assets/plan-template.md                    ← modificado: tabla Name/Code/Version/Date reemplaza **ID**/**Created**/**Spec**
skills/plan/SKILL.md                                   ← modificado: Código = PLAN-NNN, regla de versión
skills/tasks/assets/tasks-template.md                  ← modificado: tabla Name/Code/Version/Date reemplaza **ID**/**Created**/**Spec**/**Plan**
skills/tasks/SKILL.md                                  ← modificado: Código = TASKS-NNN, regla de versión

.specs/constitution.md                                 ← modificado: aplicar la tabla ahora (retrofit, documento vivo)
.specs/002-control-documental/spec.md                  ← modificado: aplicar la tabla (retrofit, feature aún no Converged)
.specs/002-control-documental/plan.md                  ← este archivo, se reescribe con la tabla durante implement
.specs/002-control-documental/tasks.md                 ← se escribe directamente con la tabla (no existe todavía)
```

## Data Model

N/A — sin entidades estructuradas, solo formato de encabezado en archivos markdown.

## API / Interface Contracts

Forma genérica de la tabla nueva (en el template, en inglés):

```markdown
| Name | Code | Version | Date |
|---|---|---|---|
| [short-description] | [TYPE-NNN] | R00 | [YYYY-MM-DD] |
```

Para `constitution-template.md`, sin columna `Code`:

```markdown
| Name | Version | Date |
|---|---|---|
| [project-name] | R00 | [YYYY-MM-DD] |
```

## Dependencies

Ninguna — se reutiliza `next-feature-number.sh` (ya existente) para el `NNN` del Código; sin scripts ni parsers nuevos.

## Risks & Unknowns

- **Riesgo**: reformatear `.specs/constitution.md` ahora mismo, sin agregar una línea al Amendments Log, podría interpretarse como que el registro "empieza vacío" sin dejar constancia de que la constitution ya había sido aprobada una vez antes de este feature. Mitigación: el propio `Version: R00` en la tabla ya deja claro que es la primera versión aprobada; el Amendments Log queda vacío hasta la primera enmienda real de contenido, que es justamente lo que se decidió en `clarify`.
- **Riesgo**: si en el futuro se agrega un `spec-flow:status` (ver `B003` del backlog) que lea estos campos, debe parsear la tabla en vez de las líneas `**ID**:` actuales — no es parte de este feature, pero queda como nota para cuando se implemente `B003`.
- Sin `[NEEDS CLARIFICATION]` — todas las ambigüedades de esta feature se resolvieron con el usuario en `clarify`.
