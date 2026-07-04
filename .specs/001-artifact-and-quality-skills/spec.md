# Spec: Renombre de Raíz de Artefactos + Skills de Calidad

**ID**: 001-artifact-and-quality-skills
**Creado**: 2026-07-04
**Estado**: Converged (2026-07-04)

## Resumen

Renombrar la raíz de artefactos de spec-flow de `specs/` a `.specs/`, y agregar dos skills opcionales de calidad portados de spec-kit (`clarify` y `analyze`) adaptados al estilo terso y sin hooks de spec-flow.

## Historias de Usuario

### US1 — La raíz de artefactos pasa a ser `.specs/` (P1)

Como usuario de spec-flow, todos los artefactos (constitution, backlog, specs/plans/tasks de features) viven en el directorio oculto `.specs/` en vez del visible `specs/`, para no ensuciar el nivel superior de un proyecto.

**Escenarios de Aceptación**:
- **Dado** un proyecto sin directorio `.specs/`, **Cuando** corre cualquier skill de spec-flow por primera vez, **Entonces** crea y lee desde `.specs/` (nunca `specs/`).
- **Dado** que corre el skill de constitution, **Cuando** escribe la constitución, **Entonces** la escribe en `.specs/constitution.md`.
- **Dado** que `next-feature-number.sh` corre sin argumentos, **Cuando** se invoca, **Entonces** por defecto escanea `.specs/` en vez de `specs/`.
- **Dado** que el renombre está completo, **Cuando** se busca en todos los archivos de skills, templates de assets, scripts y el README, **Entonces** no queda ninguna referencia a la ruta `specs/` sin el punto.

### US2 — `spec-flow:clarify` saca a la luz ambigüedades antes de planificar (P1)

Como usuario que acaba de escribir un spec, puedo correr `spec-flow:clarify` para que Claude haga hasta 5 preguntas dirigidas sobre áreas subespecificadas, con las respuestas escritas directamente en `spec.md`, antes de correr `plan`.

**Escenarios de Aceptación**:
- **Dado** un `spec.md` sin áreas vagas o subespecificadas, **Cuando** corre `clarify`, **Entonces** reporta "sin ambigüedades críticas" y sugiere avanzar a `plan`, sin hacer ninguna pregunta.
- **Dado** un `spec.md` con varias áreas subespecificadas, **Cuando** corre `clarify`, **Entonces** hace una pregunta a la vez (máximo 5 en total), y después de cada respuesta aceptada agrega una línea bajo una sección `## Clarifications` en `spec.md` y actualiza la sección correspondiente directamente.
- **Dado** que `clarify` corrió o no corrió, **Cuando** corre `plan` después, **Entonces** el hard-gate de plan no se ve afectado — `clarify` es recomendado, nunca obligatorio.
- **Dado** que no existe `spec.md` todavía para la feature actual, **Cuando** se invoca `clarify`, **Entonces** se detiene e indica al usuario correr `spec-flow:specify` primero.

### US3 — `spec-flow:analyze` cruza consistencia entre spec/plan/tasks (P2)

Como usuario que acaba de terminar `tasks.md`, puedo correr `spec-flow:analyze` para obtener un reporte de consistencia de solo lectura entre `spec.md`, `plan.md` y `tasks.md` antes de implementar.

**Escenarios de Aceptación**:
- **Dado** que existen `spec.md`, `plan.md` y `tasks.md`, **Cuando** corre `analyze`, **Entonces** genera una tabla de hallazgos (duplicación, ambigüedad, huecos de cobertura, conflictos con la constitution) con severidades, y no escribe ningún archivo.
- **Dado** que `tasks.md` todavía no existe, **Cuando** se invoca `analyze`, **Entonces** se detiene e indica al usuario correr `spec-flow:tasks` primero.
- **Dado** que un hallazgo entra en conflicto con un principio `MUST` de la constitution, **Cuando** `analyze` lo reporta, **Entonces** ese hallazgo siempre se marca `CRITICAL`.
- **Dado** que los artefactos tienen cero hallazgos, **Cuando** corre `analyze`, **Entonces** reporta un resumen limpio con estadísticas de cobertura en vez de inventar problemas.

## Casos Borde

- Un proyecto con una carpeta `specs/` preexistente (de una versión anterior del plugin) no se migra automáticamente — los skills operan solo sobre `.specs/`, según la decisión de cambio limpio de la constitution.
- `clarify` invocado cuando todas las categorías ya están `Clear`: cero preguntas, se reporta explícitamente, no se agrega sección `## Clarifications`.
- `analyze` invocado a mitad de camino (existen spec + plan, no tasks): se detiene con la instrucción de correr `tasks` primero, igual que cualquier otro caso de prerrequisito faltante en spec-flow.

## No-Objetivos Explícitos

- Sin sistema de hooks `extensions.yml` / `before_*` / `after_*` (rechazado en la constitution).
- Sin herramienta de migración automática para directorios `specs/` preexistentes.
- Sin gates nuevos agregados a la cadena existente de siete fases — `clarify` y `analyze` son aditivos y opcionales, nunca bloqueantes.
- No se agrega ningún skill de generación de checklists de calidad de requisitos — se evaluó portar `checklist` de spec-kit y se descartó deliberadamente.
- Sin orquestación multi-agente/subagente para estos skills — mismo estilo conversacional de un solo paso que los skills existentes.
- Sin cambios a los nombres, orden o formatos de archivo de las siete fases principales, más allá de la ruta `specs/` → `.specs/`.

## Preguntas Abiertas

Ninguna — las ambigüedades se resolvieron con el usuario antes de redactar (nivel de gate: solo recomendado; artefacto de `analyze`: solo reporte, sin archivo).
