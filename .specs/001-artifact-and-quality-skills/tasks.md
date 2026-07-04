# Tasks: Renombre de Raíz de Artefactos + Skills de Calidad

**ID**: 001-artifact-and-quality-skills
**Creado**: 2026-07-04
**Spec**: .specs/001-artifact-and-quality-skills/spec.md
**Plan**: .specs/001-artifact-and-quality-skills/plan.md

## Phase 1: User Story 1 — La raíz de artefactos pasa a ser `.specs/` (P1)

- [x] T001 [P][US1] Reemplazar toda referencia `specs/` → `.specs/` en skills/constitution/SKILL.md
- [x] T002 [P][US1] Reemplazar toda referencia `specs/` → `.specs/` en skills/plan/SKILL.md
- [x] T003 [P][US1] Reemplazar toda referencia `specs/` → `.specs/` en skills/plan/assets/plan-template.md
- [x] T004 [P][US1] Reemplazar toda referencia `specs/` → `.specs/` en skills/implement/SKILL.md
- [x] T005 [P][US1] Reemplazar toda referencia `specs/` → `.specs/` en skills/converge/SKILL.md
- [x] T006 [P][US1] Reemplazar toda referencia `specs/` → `.specs/` en skills/finishing-branch/SKILL.md
- [x] T007 [P][US1] Reemplazar toda referencia `specs/` → `.specs/` en skills/backlog/SKILL.md
- [x] T008 [P][US1] Cambiar el argumento por defecto (y el comentario) de "specs" a ".specs" en skills/specify/scripts/next-feature-number.sh
- [x] T009 [P][US1] Reemplazar toda referencia `specs/` → `.specs/` en skills/tasks/assets/tasks-template.md
- [x] T010 [US1] Reemplazar toda referencia `specs/` → `.specs/` en README.md (tabla de fases + bloque de artifact layout)

## Phase 2: User Story 2 — `spec-flow:clarify` (P1)

- [x] T011 [US2] Crear skills/clarify/SKILL.md nuevo, siguiendo el formato de plan.md (Architecture): frontmatter `name`/`description`; `<HARD-GATE>` exige `spec.md` de la feature actual (si no existe, invocar `spec-flow:specify` primero); Process: leer `.specs/constitution.md` y `spec.md`, escanear 5 dimensiones (alcance funcional/casos borde, modelo de datos, calidad no-funcional, integraciones/dependencias, terminología/completitud), generar hasta 5 preguntas priorizadas, hacer una a la vez (multiple-choice con opción recomendada + razón, o respuesta corta sugerida), y tras cada respuesta aceptada crear/actualizar `## Clarifications` (con `### Sesión YYYY-MM-DD`) y editar la sección del spec afectada; Quality Check (máx. 5 preguntas, una línea por respuesta, sin texto contradictorio, gate de plan sin cambios); After Writing recomendando `spec-flow:plan`
- [x] T012 [US1][US2] Reemplazar `specs/` → `.specs/` en skills/specify/SKILL.md y actualizar su mensaje "After Writing" para mencionar `spec-flow:clarify` como paso recomendado (no obligatorio) antes de `plan` — depende de T011

## Phase 3: User Story 3 — `spec-flow:analyze` (P2)

- [x] T013 [US3] Crear skills/analyze/SKILL.md nuevo, siguiendo el formato de plan.md (Architecture): frontmatter `name`/`description`; `<HARD-GATE>` exige `spec.md` + `plan.md` + `tasks.md` de la feature actual (si falta `tasks.md`, invocar `spec-flow:tasks` primero); declarar explícitamente la restricción "estrictamente de solo lectura, nunca escribe archivos"; Process: cargar spec/plan/tasks/constitution, construir inventario interno, detectar duplicación/ambigüedad/subespecificación/conflictos con constitution/huecos de cobertura/inconsistencia terminológica, asignar severidad (`CRITICAL`/`HIGH`/`MEDIUM`/`LOW`, conflicto con constitution siempre `CRITICAL`), reportar tabla de hallazgos + resumen de cobertura + métricas (tope ~30 hallazgos con nota de overflow), y un bloque de próximas acciones; reglas de comportamiento (nunca modificar archivos, reportar cero hallazgos limpiamente)
- [x] T014 [US1][US3] Reemplazar `specs/` → `.specs/` en skills/tasks/SKILL.md y actualizar su mensaje "After Writing" para mencionar `spec-flow:analyze` como paso recomendado (no obligatorio) antes de `implement` — depende de T013

## Phase 4: Integración y Documentación

- [x] T015 [US1][US2][US3] Reemplazar `specs/` → `.specs/` en skills/using-spec-flow/SKILL.md (tabla de fases + diagrama de artifact layout) y agregar una sección nueva `## Skills de Calidad (Side-Channel)` documentando `spec-flow:clarify` y `spec-flow:analyze` (cuándo invocarlos, sin gate, recomendados no obligatorios), con el mismo estilo que la sección existente de Backlog — depende de T011, T013
- [x] T016 [US2][US3] Agregar en README.md una sección "Comandos Opcionales" con una tabla listando `spec-flow:clarify` y `spec-flow:analyze` (mismo estilo que la tabla de las siete fases), ubicada después de la tabla principal de fases — depende de T011, T013

## Verification

- [x] VERIFY Los escenarios de aceptación de US1 pasan: `.specs/` se crea/lee en vez de `specs/`, constitution escribe en `.specs/constitution.md`, `next-feature-number.sh` sin argumentos escanea `.specs/`
- [x] VERIFY `grep -rn "specs/" skills scripts README.md` no devuelve ninguna coincidencia fuera de `.specs/` (edge case de US1)
- [x] VERIFY Los escenarios de aceptación de US2 pasan: `clarify` sin ambigüedades reporta limpio sin preguntar nada; con ambigüedades pregunta de a una (máx. 5) y escribe en `## Clarifications`; el hard-gate de `plan` sigue sin exigir `clarify`
- [x] VERIFY Los escenarios de aceptación de US3 pasan: `analyze` con los tres artefactos genera tabla de hallazgos sin escribir archivos; sin `tasks.md` se detiene pidiendo correr `tasks` primero; conflicto con constitution siempre `CRITICAL`
- [x] VERIFY `skills/clarify/SKILL.md` y `skills/analyze/SKILL.md` respetan la misma forma frontmatter + `<HARD-GATE>` + `Process` + verificación de calidad + mensaje final que el resto de los skills, sin ningún sistema de hooks/`extensions.yml`
- [x] VERIFY No se agregó ninguna dependencia ni script nuevo más allá del cambio de argumento por defecto en `next-feature-number.sh`
