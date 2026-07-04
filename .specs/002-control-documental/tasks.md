# Tasks: Tabla de Control Documental

| Name | Code | Version | Date |
|---|---|---|---|
| control-documental | TASKS-002 | R00 | 2026-07-04 |

**Spec**: .specs/002-control-documental/spec.md
**Plan**: .specs/002-control-documental/plan.md

## Phase 1: User Story 2 — Constitution incluye tabla sin Código (P1)

- [x] T001 [US2] Modificar skills/constitution/assets/constitution-template.md: reemplazar `**Project**`/`**Updated**` por la tabla `| Name | Version | Date |` con fila `[name] | R00 | [YYYY-MM-DD]`, y agregar una sección `## Amendments Log` al final (vacía, con el formato `- RNN (YYYY-MM-DD): <what changed and why>` como comentario)
- [x] T002 [US2][US3] Modificar skills/constitution/SKILL.md: la escritura inicial siempre usa Version `R00`; el paso "On revision request" solo incrementa Version y agrega una línea al Amendments Log cuando el documento ya fue aprobado antes (una edición post-aprobación); las iteraciones previas a la primera aprobación no incrementan nada — depende de T001

## Phase 2: User Story 1 — spec/plan/tasks templates con tabla Name/Code/Version/Date (P1)

- [x] T003 [P][US1] Modificar skills/specify/assets/spec-template.md: reemplazar `**ID**`/`**Creado**` por la tabla `| Name | Code | Version | Date |` con fila `[short-description] | SPEC-NNN | R00 | [YYYY-MM-DD]`; mantener `**Status**` como línea separada debajo de la tabla
- [x] T004 [US1][US3] Modificar skills/specify/SKILL.md: Código = `SPEC-NNN` (mismo `NNN` de `next-feature-number.sh`); misma regla de versión que T002 (`R00` hasta la primera aprobación, sube solo en ediciones posteriores) — depende de T003
- [x] T005 [P][US1] Modificar skills/plan/assets/plan-template.md: reemplazar `**ID**`/`**Created**`/`**Spec**` por la tabla `| Name | Code | Version | Date |` con fila `[short-description] | PLAN-NNN | R00 | [YYYY-MM-DD]`; eliminar la línea de referencia cruzada `**Spec**`
- [x] T006 [US1][US3] Modificar skills/plan/SKILL.md: Código = `PLAN-NNN`; misma regla de versión — depende de T005
- [x] T007 [P][US1] Modificar skills/tasks/assets/tasks-template.md: reemplazar `**ID**`/`**Created**`/`**Spec**`/`**Plan**` por la tabla `| Name | Code | Version | Date |` con fila `[short-description] | TASKS-NNN | R00 | [YYYY-MM-DD]`; eliminar las líneas de referencia cruzada `**Spec**`/`**Plan**`
- [x] T008 [US1][US3] Modificar skills/tasks/SKILL.md: Código = `TASKS-NNN`; misma regla de versión — depende de T007

## Phase 3: Retrofit de Documentos Vivos

- [x] T009 [US2] Reformatear .specs/constitution.md con la tabla `| Name | Version | Date |` → `| spec-flow | R00 | 2026-07-04 |`, sin agregar línea al Amendments Log (no hay enmienda de contenido, es solo el reformateo mecánico de este feature) — depende de T001
- [x] T010 [US1] Reformatear .specs/002-control-documental/spec.md con la tabla `| Name | Code | Version | Date |` → `| control-documental | SPEC-002 | R00 | 2026-07-04 |`, eliminando `**ID**`/`**Creado**`, manteniendo `**Estado**` — depende de T003
- [x] T011 [US1] Reformatear .specs/002-control-documental/plan.md con la tabla `| Name | Code | Version | Date |` → `| control-documental | PLAN-002 | R00 | 2026-07-04 |`, eliminando `**ID**`/`**Creado**`/`**Spec**` — depende de T005

## Verification

- [x] VERIFY Escenarios de aceptación de US1 pasan: Código con mismo `NNN` en spec/plan/tasks; `**Estado**` se mantiene separado en `spec.md`; `converge`/`finishing-branch` siguen leyendo `**Estado**` sin cambios; líneas `**Spec**:`/`**Plan**:` eliminadas de plan/tasks
- [x] VERIFY Escenarios de aceptación de US2 pasan: constitution sin columna Código; próxima revisión real sube Version `R00` → `R01`; Amendments Log es append-only
- [x] VERIFY Escenarios de aceptación de US3 pasan: varias ediciones antes de la primera aprobación no suben Version; una edición posterior a la aprobación sí la sube
- [x] VERIFY `grep -rn "\*\*ID\*\*:\|\*\*Created\*\*:\|\*\*Creado\*\*:" skills/*/assets/*.md` no devuelve coincidencias en los 4 templates modificados
- [x] VERIFY `.specs/001-artifact-and-quality-skills/` (ya `Converged`) queda intacto, sin retrofit — mismo criterio que la migración `specs/` → `.specs/`
