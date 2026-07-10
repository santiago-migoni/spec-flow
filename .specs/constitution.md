---
name: spec-flow
version: R01
date: 2026-07-09
---

# Constitución del Proyecto

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

- Un skill = un archivo `SKILL.md`: frontmatter (`name`, `description`) + `<HARD-GATE>` + pasos de `Process` + `Quality Check` + `After Writing`. Sin orquestación multi-archivo por skill.
- Los hard gates se aplican indicándole a Claude que verifique la existencia del artefacto previo antes de continuar — nunca mediante un script de validación externo ni un archivo de configuración.
- Sin sistema de extensions/hooks (sin etapas `before_*`/`after_*`, sin config estilo `extensions.yml`). Se consideró y se rechazó explícitamente — en spec-kit agregaba boilerplate a cada comando sin una necesidad equivalente acá. Si en el futuro aparece una necesidad real de personalización por proyecto, se reconsidera en ese momento.
- Cada fase escribe exactamente un artefacto, reporta un resumen (máximo 150 palabras, nunca el documento completo) y pide aprobación antes de avanzar.
- La implementación del propio plugin sigue el minimalismo estilo Ponytail: ninguna dependencia, script o abstracción más allá de lo que las instrucciones de un skill requieran.

## Convenciones de Nombres

- Carpetas de skills: `skills/<nombre-skill>/SKILL.md`, en kebab-case, coincidiendo con el nombre de invocación `spec-flow:<nombre-skill>`.
- Directorios de artefactos de feature: `.specs/NNN-descripcion-corta/` — `NNN` es un número de 3 dígitos con ceros a la izquierda desde `next-feature-number.sh`, `descripcion-corta` en kebab-case.
- Artefactos globales del proyecto: `.specs/constitution.md`, `.specs/backlog.md`.

## Restricciones

- Debe funcionar como un plugin de Claude Code portable y autocontenido — sin llamadas de red ni servicios externos en runtime.
- Las integraciones opcionales del ecosistema (Ponytail, RTK) siguen siendo opcionales: se detectan si están presentes, nunca son obligatorias, nunca una dependencia dura.
- La raíz de artefactos es `.specs/` (con punto, oculta). Esto es un cambio limpio respecto a la convención anterior `specs/` — sin detección dual de rutas, sin migración automática de carpetas `specs/` existentes.

## Fuera de Alcance

- Sin framework de hooks/extensions (etapas `before_*`/`after_*`, comandos pre/post configurados por YAML).
- Sin capa de retrocompatibilidad para el nombre de carpeta `specs/` antiguo.
- Sin framework de automatización personalizado más allá de pequeños helpers bash de propósito único.

## Registro de Enmiendas

<!-- Append-only. Una línea por revisión posterior a la primera aprobación. Formato: - RNN (YYYY-MM-DD): <qué cambió y por qué> -->
- R01 (2026-07-09): La tabla de control documental (Nombre/Código/Versión/Fecha) de constitution/spec/plan/tasks pasa de tabla markdown a frontmatter YAML — más simple de editar mecánicamente por los skills, consistente con el frontmatter que ya usan los propios SKILL.md.
