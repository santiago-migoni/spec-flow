# Constitución del Proyecto

<!-- Principios de Código, Security, Operational Principles, Observability, Performance y Dependency Policy etiquetan cada bullet con una keyword RFC 2119:
MUST — no negociable; plan/analyze/converge tratan una violación como CRITICAL.
SHOULD — default fuerte; una desviación necesita una razón explícita en plan.md.
MAY — opcional, a criterio del implementador.
Si una sección entera no aplica a este proyecto, reemplazar sus bullets con una línea: N/A — <por qué>. -->

| Nombre    | Versión | Fecha      | Estado   |
| --------- | ------- | ---------- | -------- |
| spec-flow | R03     | 2026-07-17 | Approved |

## Propósito

Un plugin de Claude Code para Desarrollo Guiado por Especificaciones (SDD). Obliga a que la planificación de features ocurra en artefactos versionados de texto plano — constitution, spec, plan, tasks — antes de escribir código, para que la implementación asistida por IA tenga una verdad de referencia contra la cual chequear, en lugar de depender de la memoria conversacional.

## Stack Técnico

- **Lenguaje**: Markdown (definiciones de skills con frontmatter YAML)
- **Runtime / Framework**: sistema de plugins/skills de Claude Code — los skills se descubren desde `skills/<nombre>/SKILL.md`, empaquetados vía `.claude-plugin/plugin.json` y `.claude-plugin/marketplace.json`
- **Scripting**: Bash, solo donde las instrucciones en markdown no alcanzan (ej. `skills/specify/scripts/next-feature-number.sh`)
- **Base de datos**: N/A
- **Testing**: N/A — los skills se validan por dogfooding directo, no por una suite automatizada
- **Linting / Formato**: N/A

## Principios de Código

- **MUST**: Un skill = un archivo `SKILL.md`: frontmatter (`name`, `description`) + `<HARD-GATE>` + pasos de `Process` + `Quality Check` + `After Writing`. Sin orquestación multi-archivo por skill.
- **MUST**: Los hard gates se aplican indicándole a Claude que verifique la existencia del artefacto previo antes de continuar — prosa, no script de validación externo ni archivo de configuración. Excepción angosta (R02, ver abajo): el gate de *aprobación* específicamente puede reforzarse con un hook nativo de Claude Code.
- **MUST**: Sin framework general de extensions/hooks configurable por proyecto (sin etapas `before_*`/`after_*`, sin config estilo `extensions.yml`) — se rechaza por agregar boilerplate a cada comando sin una necesidad equivalente acá. Excepción angosta (R02): el propio plugin puede usar hooks nativos de Claude Code (`settings.json` `Stop`/`PreToolUse`) para hacer cumplir su propio gate de aprobación entre fases — no es personalización por proyecto, es enforcement de una regla que ya existe en prosa (`<HARD-GATE>`) y que el dogfooding real demostró insuficiente por sí sola.
- **MUST**: Cada fase escribe exactamente un artefacto, reporta un resumen (máximo 150 palabras, nunca el documento completo) y pide aprobación antes de avanzar.
- **SHOULD**: La implementación del propio plugin sigue el minimalismo estilo Ponytail: ninguna dependencia, script o abstracción más allá de lo que las instrucciones de un skill requieran.

## Security

<!-- Reglas de trust-boundary que este repo siempre sigue — no es un threat model completo. -->

- **MUST**: Ninguna operación git destructiva (force-push, hard reset, borrado de rama, discard) corre sin confirmación explícita del usuario para esa acción puntual — ver la tabla de Red Flags de `finishing-branch/SKILL.md`.
- **MUST**: Los artefactos de `.specs/` (versionados en git) nunca contienen secretos, credenciales o tokens reales, ni siquiera como ejemplo ilustrativo — usar placeholders (`<TOKEN>`).

## Operational Principles

<!-- Cómo se despliega y revierte este sistema — acá "deploy" es cortar una release del plugin. -->

- **MUST**: El commit que bumpea la versión (`plugin.json` + el heading `## Release vX.Y.Z` en `CHANGELOG.md`) es un commit separado del/los commit(s) que contienen el cambio real — nunca se mezclan.
- **SHOULD**: Las entradas de `CHANGELOG.md` se acumulan bajo un heading de trabajo-en-curso durante una sesión y se finalizan como `## Release vX.Y.Z` recién en el commit de bump.

## Observability

<!-- No hay runtime que loguear — esto es sobre cómo el propio proceso de SDD reporta sus hallazgos. -->

- **MUST**: Los findings de `analyze`/`converge` siempre llevan severidad y una recomendación concreta — nunca un "algo está mal" sin más contexto.
- **MUST**: Un conflicto de constitución es siempre `CRITICAL` en `analyze`/`converge`, nunca se degrada en silencio.

## Performance

<!-- No hay latencia de runtime que presupuestar — esto es el presupuesto de costo/capacidad del propio plugin. -->

- **MUST**: La asignación de `model`/`effort` por fase sigue la razón capacidad-vs-minuciosidad documentada en `CLAUDE.md` — un modelo capaz para juicio ambiguo/arquitectónico, effort alto en un modelo más barato para fases mecánicas donde el riesgo es saltear un paso.
- **SHOULD**: Cambiar el `model`/`effort` de una fase implica actualizar la tabla de razones en `CLAUDE.md`, no solo el frontmatter del skill, para que las dos no diverjan.

## Dependency Policy

<!-- Cuándo el propio plugin puede sumar una dependencia o un módulo nuevo. -->

- **MUST**: Sin dependencia dura de otros plugins del ecosistema (Ponytail, RTK) — las integraciones se detectan si están presentes, nunca son obligatorias.
- **SHOULD**: Preferir helpers bash chicos y de propósito único (ej. `next-feature-number.sh`) antes que agregar un framework general de automatización.

## Convenciones de Nombres

- Carpetas de skills: `skills/<nombre-skill>/SKILL.md`, en kebab-case, coincidiendo con el nombre de invocación `spec-flow:<nombre-skill>`.
- Directorios de artefactos de feature: `.specs/NNN-descripcion-corta/` — `NNN` es un número de 3 dígitos con ceros a la izquierda desde `next-feature-number.sh`, `descripcion-corta` en kebab-case.
- Artefactos globales del proyecto: `.specs/constitution.md`, `.specs/backlog.md`.

## Restricciones

- Debe funcionar como un plugin de Claude Code portable y autocontenido — sin llamadas de red ni servicios externos en runtime.
- La raíz de artefactos es `.specs/` (con punto, oculta). Esto es un cambio limpio respecto a la convención anterior `specs/` — sin detección dual de rutas, sin migración automática de carpetas `specs/` existentes.

## Fuera de Alcance

- Sin framework general de hooks/extensions configurable por proyecto (etapas `before_*`/`after_*`, comandos pre/post configurados por YAML) — sigue fuera de alcance. Excepción: hooks nativos de Claude Code usados por el propio plugin para hacer cumplir su gate de aprobación (ver R02 en el Registro de Enmiendas).
- Sin capa de retrocompatibilidad para el nombre de carpeta `specs/` antiguo.
- Sin framework de automatización personalizado más allá de pequeños helpers bash de propósito único.

## Registro de Enmiendas

<!-- Append-only. Una línea por revisión posterior a la primera aprobación. Formato: - RNN (YYYY-MM-DD): <qué cambió y por qué> -->
- R01 (2026-07-09): La tabla de control documental (Nombre/Código/Versión/Fecha) de constitution/spec/plan/tasks pasa de tabla markdown a frontmatter YAML — más simple de editar mecánicamente por los skills, consistente con el frontmatter que ya usan los propios SKILL.md.
- R02 (2026-07-17): Excepción angosta al rechazo de hooks/extensions ("Principios de Código" y "Fuera de Alcance") — el propio plugin puede usar hooks nativos de Claude Code (`settings.json` `Stop`/`PreToolUse`) para hacer cumplir su gate de aprobación entre fases. El rechazo original (R01, vía spec-kit) era sobre un framework general de personalización por proyecto; ese rechazo se mantiene. Motivo: backlog item B005 — en dogfooding real (proyecto odoo-infrastructure) el modelo encadenó fases sin aprobación explícita del usuario, y el `<HARD-GATE>` en prosa no fue suficiente para evitarlo.
- R03 (2026-07-17): Migración completa a la estructura nueva de `constitution-template.md` — se agregan las secciones `Security`, `Operational Principles`, `Observability`, `Performance` y `Dependency Policy`, y cada bullet de una sección de principios queda etiquetado `MUST`/`SHOULD`/`MAY`. Todo el contenido nuevo proviene de convenciones ya practicadas en este repo (Red Flags de `finishing-branch`, reglas de severidad de `analyze`/`converge`, tabla de model/effort de `CLAUDE.md`, proceso de release de esta misma sesión) — ninguna reubicación inventa un principio no practicado. De paso se corrige el bullet de hard gates en "Principios de Código", que había quedado inconsistente con la excepción de hooks de R02.
