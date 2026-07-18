# Spec: Execution-Driven Verification Loop

<!-- Every claim in this document must be measurable or falsifiable — avoid vague adjectives ("fast", "robust", "intuitive", "seamless") without a concrete threshold or test. spec-flow:analyze flags unmeasurable language as an Ambiguity finding. -->

| Name                          | Code     | Version | Date       | Status |
| ----------------------------- | -------- | ------- | ---------- | ------ |
| execution-verification-loop   | SPEC-004 | R00     | 2026-07-18 | Converged |

## Summary

Refinar el loop `implement`↔`converge` con dos cambios que salieron del dogfooding en odoo-infrastructure: `implement` verifica ejecutando el flujo afectado y observando el comportamiento real (no trazando a `file:line`), y `converge` cierra en una sola invocación cuando hay findings (append de tasks → fixes aplicados en la misma conversación → re-check), sin exigir una segunda corrida.

## Success Metrics

- Bugs reales detectados en la fase `implement` en vez de escaparse a `converge` o a runtime: en los próximos ≥3 features dogfooded, cada bug con superficie ejecutable se detecta en el Verification Step de `implement`, no después.
- Invocaciones de `converge` por feature con findings: baja de 2 a 1 en los próximos ≥3 features dogfooded con findings.

## User Stories

<!-- One block per story, ordered by priority. P1 = must-ship, P2 = should-ship, P3 = nice-to-have. Repeat as US2, US3, ... for each additional story. -->

### US1 — `implement` verifica ejecutando el flujo, no trazando (P1)

Como usuario que corre `spec-flow:implement`, el Verification Step ejecuta el flujo afectado por los cambios y observa el comportamiento real, en vez de trazar cada acceptance scenario a un `file:line`. El origen del cambio: en el dogfooding todos los bugs reales (restic `--no-lock`, chown de filestore, locks huérfanos, versión sin pinear) aparecieron solo corriendo el código, nunca leyéndolo.

**Acceptance Scenarios**:

- **Given** un `tasks.md` con todas las tasks completas y un cambio con superficie ejecutable, **When** corre el Verification Step de `implement`, **Then** ejecuta el flujo afectado por cada acceptance scenario y confirma el comportamiento observado (no una traza estática a `file:line`).
- **Given** un acceptance scenario cuyo comportamiento observado NO coincide con el esperado, **When** el Verification Step lo ejecuta, **Then** agrega una task nueva a `tasks.md` para el gap, la ejecuta, y re-ejecuta el flujo (no re-traza).
- **Given** un cambio SIN superficie ejecutable (prompt-only / docs — ej. editar un `SKILL.md` de spec-flow), **When** corre el Verification Step, **Then** degrada a revisar el comportamiento esperado del artefacto y anota explícitamente por qué no se ejecutó nada, sin forzar un run inaplicable.

### US2 — `converge` cierra en una sola invocación cuando hay findings (P1)

Como usuario que corre `spec-flow:converge` sobre un feature con gaps, la misma invocación appendea las tasks de convergencia, espera a que se apliquen los fixes en la misma conversación, y re-verifica — sin obligarme a invocar `spec-flow:converge` una segunda vez para obtener el `Converged` limpio. En el dogfooding, cada feature con findings obligó a dos invocaciones.

**Acceptance Scenarios**:

- **Given** un `converge` que encuentra findings, **When** el usuario aprueba y los fixes se aplican en la misma conversación, **Then** `converge` re-verifica dentro de la misma invocación y reporta el resultado, sin pedir una segunda corrida de `spec-flow:converge`.
- **Given** que el re-check en la misma invocación da limpio, **When** `converge` cierra, **Then** setea `Status: Converged` sobre el `spec.md`, igual que hoy.
- **Given** que hay findings, **When** `converge` escribe, **Then** su única acción de escritura sobre `tasks.md` sigue siendo append (append de la sección `## Phase N: Convergence` + append del resultado del re-check) — nunca reescribe ni reordena contenido previo.

## Non-Functional Requirements

<!-- Feature-specific quality bar, additive to constitution.md's global MUSTs — don't repeat a constitution principle here, only what this feature specifically needs. Write "N/A" if the constitution's baseline already covers this feature with no exceptions. -->

- **MUST**: `converge` preserva su naturaleza append-only y read-mostly — no aplica fixes él mismo ni auto-invoca `implement`; el re-check en una sola pasada no puede introducir una acción de escritura que no sea un append a `tasks.md`.
- **MUST**: El cambio se limita a `skills/implement/SKILL.md` y `skills/converge/SKILL.md` (y sus `assets/` si aplica) — no toca los `<HARD-GATE>` de la cadena principal ni el hook de aprobación.

## Edge Cases

- Un cambio parcialmente ejecutable (parte con runtime, parte prompt-only): se ejecuta lo que tiene superficie y se degrada a revisión lo que no, en la misma corrida — no es todo-o-nada.
- El usuario NO aplica los fixes en la misma conversación (se va, o difiere): `converge` no puede re-checkear algo que no pasó — reporta las tasks appendeadas y queda igual que hoy (el `Converged` limpio requerirá una corrida futura). El single-pass es un camino feliz, no una obligación.
- Ejecutar el flujo tiene efectos colaterales (escribe datos, llama servicios): el Verification Step observa comportamiento, no debe correr acciones destructivas sin la confirmación que ya exige la constitución.

## Assumptions & Dependencies

<!-- External systems, prior specs, or data this feature assumes already exist. Write "None" if there are none. -->

- None — no depende de ningún otro spec en curso ni de ninguna skill externa al plugin.

## Explicit Non-Goals

- No automatiza la cadena `implement`→`converge` ni ninguna otra: `converge` sigue sin orquestar `implement`; el single-pass solo evita la *segunda invocación de converge*, no introduce un runner.
- No cambia el patrón de aprobación ni los `<HARD-GATE>` de ninguna fase.
- No agrega un framework de testing automatizado al plugin (la constitución marca `Testing: N/A`).
- No toca ningún skill fuera de `implement` y `converge`.

## Open Questions

<!-- Empty section is a valid, finished state — don't invent a question to fill it. -->
