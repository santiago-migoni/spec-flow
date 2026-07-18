# Tasks: Execution-Driven Verification Loop

| Name                        | Code      | Version | Date       | Status |
| --------------------------- | --------- | ------- | ---------- | ------ |
| execution-verification-loop | TASKS-004 | R00     | 2026-07-17 | Approved |

<!-- No Setup phase: ambos archivos ya existen; esto es edición de prosa. Sin tasks [TEST]: la constitución marca Testing N/A (los skills se validan por dogfooding). -->

## Phase 1: US1 — `implement` verifica ejecutando el flujo (P1)

- [x] T001 [US1] En `skills/implement/SKILL.md`, Verification Step (paso 2, ~línea 45): reemplazar "trace it explicitly: … → satisfied by [file:line]" por ejecutar el flujo afectado por cada acceptance scenario y confirmar el comportamiento observado (no una traza estática).
- [x] T002 [US1] En `skills/implement/SKILL.md`, Verification Step: agregar el caso de degradación — si el cambio no tiene superficie ejecutable (prompt-only/docs), revisar el comportamiento esperado del artefacto y anotar explícitamente por qué no se ejecutó nada.
- [x] T003 [US1] En `skills/implement/SKILL.md`, Verification Step: agregar el guardarraíl de Security — al ejecutar el flujo, no correr acciones destructivas/irreversibles sin la confirmación puntual que exige la constitución.
- [x] T004 [US1] En `skills/implement/SKILL.md`, "What Counts as Done" (~línea 53): cambiar "All acceptance scenarios in spec.md are traced and confirmed" por "ejecutados y confirmados por comportamiento observado (o revisados, para cambios sin runtime)".
- [x] T005 [US1] En `skills/implement/SKILL.md`, verificar que se conservan intactos el chequeo contra constitución (paso 4 actual) y el loop "si un scenario falla → agregar task, ejecutar, re-ejecutar" (paso 3 actual, ajustado a re-ejecutar en vez de re-trazar).

## Phase 2: US2 — `converge` cierra en una sola invocación (P1)

- [x] T006 [US2] En `skills/converge/SKILL.md`, sección "6. Handoff" (~líneas 104-108): cuando se appendearon tasks, ofrecer re-verificar en la misma invocación una vez que los fixes se aplicaron en la misma conversación (por el usuario o por `implement`), en vez de exigir una segunda corrida de `spec-flow:converge`.
- [x] T007 [US2] En `skills/converge/SKILL.md`, sección 6: especificar que el re-check reusa el flujo de assess (secciones 2-5) — limpio → `Status: Converged`; con gaps residuales → append de una `## Phase N+1: Convergence` — sin agregar ninguna acción de escritura nueva.
- [x] T008 [US2] En `skills/converge/SKILL.md`, sección 6: agregar el fallback explícito — si el usuario no aplica los fixes en la misma conversación, converge reporta las tasks appendeadas y queda como hoy (el single-pass es camino feliz, no obligación).
- [x] T009 [US2] En `skills/converge/SKILL.md`, "Core Constraint: Append-Only" (~líneas 19-28): reforzar que el re-check en una sola invocación no introduce escrituras fuera de los dos appends ya permitidos, y que converge sigue sin aplicar fixes ni auto-invocar `implement`.

## Verification

- [x] VERIFY All acceptance scenarios in spec.md pass — US1/AC1-3 (ejecutar + degradar), US2/AC1-3 (re-check en una invocación, `Converged`, append-only)
- [x] VERIFY All Non-Functional Requirements in spec.md are met — converge sigue append-only/read-mostly; el cambio se limitó a implement/converge SKILL.md
- [x] VERIFY No constitution MUST principle relevant to this feature is violated — un skill=un SKILL.md, hard gates intactos, sin framework de extensions (converge no orquesta), sin dependencia dura externa
- [x] VERIFY No files were created that are not listed in plan.md's file structure — solo `implement/SKILL.md` y `converge/SKILL.md` modificados, cero archivos nuevos
- [x] VERIFY No new dependencies were added beyond those listed in plan.md — ninguna (la referencia a `verify` se eliminó, no se agregó)
- [x] VERIFY `model`/`effort` de implement y converge sin cambios — no requiere sincronizar la tabla de `CLAUDE.md`
