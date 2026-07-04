# Plan: Renombre de Raíz de Artefactos + Skills de Calidad

**ID**: 001-artifact-and-quality-skills
**Creado**: 2026-07-04
**Spec**: .specs/001-artifact-and-quality-skills/spec.md

## Enfoque

Dos frentes sobre el mismo árbol de archivos, ejecutados como un solo plan porque comparten los mismos archivos tocados: (1) reemplazo disciplinado de toda referencia a `specs/` por `.specs/` en cada `SKILL.md`, template de `assets/` y script existente, sin tocar la lógica interna de ningún skill; (2) dos `SKILL.md` nuevos (`clarify`, `analyze`) escritos desde cero en el estilo terso de spec-flow — sin scripts de prerequisitos JSON, sin sistema de hooks — más ajustes puntuales de una línea en `plan`, `tasks`, `specify`, `using-spec-flow` y `README.md` para mencionarlos como pasos opcionales recomendados, nunca bloqueantes.

## Constitution Check

- **Tech stack**: sin cambios — markdown + bash, coherente con la constitution.
- **Code principles**: `clarify` y `analyze` siguen el mismo formato que los skills existentes (frontmatter + `<HARD-GATE>` + `Process` + verificación de calidad + mensaje final). Cero hooks, cero `extensions.yml`, tal como fija la constitution.
- **Constraints**: `analyze` es de solo lectura y no escribe ningún artefacto — excepción ya acordada explícitamente con el usuario al principio de `specify`, documentada también acá para que quede trazada. El resto de los skills mantiene "un artefacto por fase".
- **Constraints**: cambio limpio `specs/` → `.specs/`, sin shim de compatibilidad — cumple la restricción de la constitution.

## Architecture

**Rename (`US1`)**: pure find-and-replace de la ruta `specs/` → `.specs/` en cada ocurrencia listada en el árbol de archivos abajo, incluyendo el argumento por defecto de `next-feature-number.sh` (`specs` → `.specs`). No cambia ningún nombre de skill, ningún formato de artefacto, ningún gate.

**`spec-flow:clarify` (`US2`)**: mismo patrón que `specify`/`plan` — lee `.specs/constitution.md` y el `spec.md` de la feature actual, escanea 5 dimensiones (reducidas del catálogo de 9 de spec-kit, sin perder cobertura real):
1. Alcance funcional y casos borde
2. Modelo de datos / entidades
3. Calidad no-funcional (performance, seguridad, confiabilidad)
4. Integraciones y dependencias externas
5. Terminología y señales de completitud

Genera hasta 5 preguntas priorizadas, una a la vez (multiple-choice con opción recomendada + razón, o respuesta corta sugerida). Cada respuesta aceptada se escribe de inmediato: bullet en `## Clarifications` (creada bajo `Resumen` si no existe, con subtítulo `### Sesión YYYY-MM-DD`) y edición directa de la sección del spec que la ambigüedad afectaba.

**`spec-flow:analyze` (`US4` → ahora `US3`)**: única excepción de solo-lectura en todo el plugin. Lee `spec.md` + `plan.md` + `tasks.md` + `.specs/constitution.md`, construye un inventario interno (requisitos, tareas, principios `MUST`), detecta duplicación / ambigüedad / huecos de cobertura / conflictos de constitution / inconsistencia terminológica, asigna severidad (`CRITICAL`/`HIGH`/`MEDIUM`/`LOW` — conflicto con constitution siempre `CRITICAL`), y reporta una tabla de hallazgos + resumen de cobertura. Nunca escribe en disco.

**Menciones opcionales**: `specify` sugiere `clarify` como paso opcional antes de `plan`; `tasks` sugiere `analyze` como paso opcional antes de `implement`; `using-spec-flow` documenta ambos en una sección nueva "Skills de Calidad (Side-Channel)", igual que ya documenta `backlog`.

## File Structure

```text
.specs/
├── constitution.md                          ← ya escrito (fase constitution)
└── 001-artifact-and-quality-skills/
    ├── spec.md                              ← ya escrito (fase specify)
    └── plan.md                              ← este archivo

skills/
├── clarify/
│   └── SKILL.md                             ← nuevo — US2
├── analyze/
│   └── SKILL.md                             ← nuevo — US3
├── constitution/SKILL.md                    ← modificado — specs/ → .specs/
├── specify/
│   ├── SKILL.md                             ← modificado — specs/ → .specs/, menciona clarify
│   └── scripts/next-feature-number.sh       ← modificado — default arg "specs" → ".specs"
├── plan/
│   ├── SKILL.md                             ← modificado — specs/ → .specs/
│   └── assets/plan-template.md              ← modificado — specs/ → .specs/
├── tasks/
│   ├── SKILL.md                             ← modificado — specs/ → .specs/, menciona analyze
│   └── assets/tasks-template.md             ← modificado — specs/ → .specs/
├── implement/SKILL.md                       ← modificado — specs/ → .specs/
├── converge/SKILL.md                        ← modificado — specs/ → .specs/
├── finishing-branch/SKILL.md                ← modificado — specs/ → .specs/
├── backlog/SKILL.md                         ← modificado — specs/ → .specs/
└── using-spec-flow/SKILL.md                 ← modificado — specs/ → .specs/, nueva sección Skills de Calidad

README.md                                     ← modificado — specs/ → .specs/, tabla de comandos opcionales
```

## Data Model

N/A — no hay entidades estructuradas; todo son archivos markdown.

## API / Interface Contracts

Contrato de cada skill nuevo (frontmatter `SKILL.md`):

```yaml
---
name: clarify
description: "Ask up to 5 targeted questions to resolve ambiguity in the current feature's spec.md, writing answers directly into a Clarifications section. Recommended before spec-flow:plan, never required."
---
```

```yaml
---
name: analyze
description: "Read-only cross-check of spec.md, plan.md, and tasks.md for duplication, ambiguity, coverage gaps, and constitution conflicts. Run after spec-flow:tasks, before spec-flow:implement. Never writes files."
---
```

## Dependencies

Ninguna — se reutiliza exactamente el mismo mecanismo de lectura/escritura de markdown que ya usan `specify`, `plan` y `tasks`. Sin scripts nuevos, sin parsers YAML/JSON, sin subagentes.

## Risks & Unknowns

- **Riesgo**: cualquier proyecto que ya haya usado una versión previa del plugin con `specs/` va a ver que los skills empiezan a operar sobre un `.specs/` vacío. Aceptado y documentado como decisión de cambio limpio en la constitution y el spec — no es un bug, es el comportamiento esperado.
- **Riesgo**: reducir el catálogo de 9 categorías de spec-kit a 5 en `clarify` podría dejar afuera algún tipo de ambigüedad. Mitigación: si el uso real muestra huecos, se amplía en una iteración futura — no se sobre-diseña ahora (ponytail).
- Sin `[NEEDS CLARIFICATION]` — todas las ambigüedades de esta feature ya se resolvieron con el usuario en las fases de constitution y specify.
