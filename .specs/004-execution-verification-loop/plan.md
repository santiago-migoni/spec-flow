# Plan: Execution-Driven Verification Loop

| Name                        | Code     | Version | Date       | Status |
| --------------------------- | -------- | ------- | ---------- | ------ |
| execution-verification-loop | PLAN-004 | R00     | 2026-07-17 | Approved |

## Approach

Editar prosa en dos `SKILL.md` existentes, sin agregar archivos, scripts, assets ni abstracciones. En `implement/SKILL.md` se reescribe el Verification Step para verificar ejecutando el flujo afectado y observando comportamiento (con degradación a revisión cuando no hay superficie ejecutable). En `converge/SKILL.md` se convierte el handoff en un re-check dentro de la misma invocación cuando los fixes se aplican en la misma conversación, reusando los dos caminos de escritura que converge ya tiene (append de una fase nueva, o `Status: Converged`) para no romper el append-only.

## Constitution Check

- **Tech Stack**: Alineado — solo se editan `SKILL.md` en Markdown, sin nuevo scripting ni dependencias.
- **Code Principles**: `MUST` "un skill = un archivo `SKILL.md`" — se respeta: se edita prosa dentro de los `SKILL.md` existentes, sin orquestación multi-archivo. `MUST` hard gates intactos (no se tocan los `<HARD-GATE>`). `MUST` "sin framework de extensions/hooks" — se respeta: converge **no** auto-invoca `implement` ni introduce un runner; el re-check es prosa que corre solo si el usuario aplicó los fixes en la conversación. `SHOULD` minimalismo Ponytail — el plan toca 2 archivos y cero abstracciones nuevas.
- **Security**: `MUST` ninguna operación destructiva sin confirmación puntual — relevante para US1: "ejecutar el flujo" en un proyecto consumidor no debe correr acciones destructivas o irreversibles sin la confirmación que la constitución ya exige. Se documenta como guardarraíl en el Verification Step.
- **Operational Principles**: N/A — esta feature no corta release ni bumpea versión (eso ocurre en `finishing-branch`, fuera de alcance).
- **Observability**: `MUST` findings de converge con severidad + recomendación — se preserva; el re-check reusa la tabla de findings existente, no la degrada.
- **Performance**: `MUST`/`SHOULD` model/effort por fase — **no se cambian** el `model`/`effort` de `implement` (sonnet/medium) ni de `converge` (opus/high), así que no hay que sincronizar la tabla de `CLAUDE.md`. N/A.
- **Dependency Policy**: `MUST` sin dependencia dura de otros plugins — se cumple: se eliminó toda referencia a una skill `verify` externa (decisión de spec R00). `SHOULD` helpers bash de propósito único — N/A, no se agrega script.
- **Constraints**: Plugin autocontenido, sin red — se cumple; solo edición de prosa.

## NFR Compliance

- **MUST converge sigue append-only/read-mostly**: El re-check dentro de la misma invocación no agrega ninguna acción de escritura nueva — si queda limpio setea `Status: Converged` (camino de cero findings que converge ya tiene), si quedan gaps residuales appendea una `## Phase N+1: Convergence` (otro append). Converge nunca aplica fixes ni auto-invoca `implement`. Satisfecho.
- **MUST cambio limitado a implement/converge**: La File Structure de abajo confirma que solo se tocan esos dos `SKILL.md`. Satisfecho.

## Architecture

Dos ediciones de prosa independientes, sin interacción entre sí (no hay diagrama que aporte):

**`implement/SKILL.md` — Verification Step (líneas ~40-48):**
- Reemplazar el paso "trace it explicitly: … → satisfied by [file:line]" por: ejecutar el flujo afectado por cada acceptance scenario y confirmar el comportamiento observado.
- Agregar el caso de degradación: si el cambio no tiene superficie ejecutable (prompt-only/docs), revisar el comportamiento esperado del artefacto y anotar explícitamente por qué no se ejecutó nada.
- Agregar el guardarraíl de Security: no correr acciones destructivas/irreversibles al ejecutar el flujo sin confirmación.
- Ajustar "What Counts as Done" (línea 53): "traced and confirmed" → "ejecutados y confirmados por comportamiento observado (o revisados, para cambios sin runtime)".

**`converge/SKILL.md` — sección 6 Handoff (líneas ~104-108):**
- Cuando hay findings y se appendearon tasks: ofrecer re-verificar en la misma invocación una vez que los fixes se aplicaron en la misma conversación (por el usuario o por `implement`), en vez de exigir una segunda corrida de `spec-flow:converge`.
- El re-check reusa el flujo de assess existente (secciones 2-5): limpio → `Status: Converged`; con gaps residuales → append de una fase de convergencia nueva.
- Fallback explícito: si el usuario no aplica los fixes en la misma conversación, converge reporta las tasks appendeadas y queda como hoy — el single-pass es camino feliz, no obligación.
- Reforzar en la sección "Core Constraint: Append-Only" que el re-check no introduce escrituras fuera de los dos appends ya permitidos, y que converge sigue sin aplicar fixes ni orquestar `implement`.

## File Structure

```text
skills/
├── implement/SKILL.md    ← modified: Verification Step reescrito a ejecutar-y-observar + degradación sin runtime + guardarraíl de acciones destructivas; wording de "What Counts as Done"
└── converge/SKILL.md      ← modified: handoff convertido en re-check de una sola invocación (append-only, sin auto-orquestar implement); nota en "Core Constraint"
```

## Data Model

N/A.

## API / Interface Contracts

N/A — los skills son prosa; no hay firma de función ni contrato de endpoint. El único "contrato" observable es la salida de cada skill, cuyo formato (tabla de findings, `Status`) no cambia.

## Dependencies

None — existing dependencies suffice. Se elimina, no se agrega, la referencia a `verify`.

## Risks & Unknowns

- **El re-check de US2 depende de que los fixes se apliquen en la misma conversación.** Si no ocurre, el comportamiento degrada exactamente al de hoy (dos invocaciones) — documentado como edge case en el spec, no es una falla.
- **"Ejecutar el flujo" (US1) puede tener efectos colaterales en un proyecto consumidor.** Mitigación: observar comportamiento y exigir confirmación para acciones destructivas (guardarraíl de Security ya incorporado al Verification Step).
- **Riesgo de regresión en la redacción**: al reescribir el Verification Step no debe perderse el chequeo contra constitución (paso 4 actual) ni el loop "si un scenario falla, agregar task y re-ejecutar". Se conservan, solo cambia trazar→ejecutar.
