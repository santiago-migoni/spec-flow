# Constitución del Proyecto

<!-- Principios de Código, Security, Operational Principles, Observability, Performance y Dependency Policy etiquetan cada bullet con una keyword RFC 2119:
MUST — no negociable; plan/analyze/converge tratan una violación como CRITICAL.
SHOULD — default fuerte; una desviación necesita una razón explícita en plan.md.
MAY — opcional, a criterio del implementador.
Si una sección entera no aplica a este proyecto, reemplazar sus bullets con una línea: N/A — <por qué>. -->

| Nombre    | Versión | Fecha      | Estado   |
| --------- | ------- | ---------- | -------- |
| spec-flow | R04     | 2026-09-12 | Approved |

## Propósito

Un plugin de Codex para Desarrollo Guiado por Especificaciones (SDD). Obliga a que la planificación de features ocurra en artefactos versionados de texto plano — constitution, spec, plan, tasks — antes de escribir código, para que la implementación asistida por IA tenga una verdad de referencia contra la cual chequear, en lugar de depender de la memoria conversacional.

## Stack Técnico

- **Lenguaje**: Markdown (definiciones de skills con frontmatter YAML)
- **Runtime / Framework**: formato portable Agent Plugins de Codex — el paquete vive en `plugins/spec-flow/`, con `plugin.json` en su raíz y skills en `plugins/spec-flow/skills/<nombre>/SKILL.md`; el marketplace del repositorio se declara en `.agents/plugins/marketplace.json` y obtiene el paquete desde GitHub
- **Scripting**: Bash para helpers pequeños y Python 3 estándar para procesar eventos del hook cuando las instrucciones en Markdown no alcanzan
- **Base de datos**: N/A
- **Testing**: N/A — los skills se validan por dogfooding directo, no por una suite automatizada
- **Linting / Formato**: N/A

## Principios de Código

- **MUST**: Un skill = un archivo `SKILL.md`: frontmatter (`name`, `description`) + `<HARD-GATE>` + pasos de `Process` + `Quality Check` + `After Writing`. Sin orquestación multi-archivo por skill.
- **MUST**: Los hard gates se aplican indicando al agente Codex que verifique la existencia y aprobación del artefacto previo antes de continuar — prosa en cada `SKILL.md`, no una herramienta externa requerida para elegir o ejecutar una skill. La excepción angosta de abajo puede reforzar el gate de aprobación para escrituras locales cubiertas por el hook.
- **MUST**: Sin framework general de extensiones/hooks configurable por proyecto (sin etapas `before_*`/`after_*`, sin config estilo `extensions.yml`). Excepción angosta: el propio plugin puede usar un hook nativo de Codex `PreToolUse` para hacer cumplir su gate de aprobación entre fases en rutas de escritura local que el hook soporte. No intercepta selección de skills ni reemplaza los hard gates en prosa; sus definiciones deben ser confiadas por el usuario para que se ejecuten.
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

- **MUST**: El frontmatter de cada skill usa los campos que Codex admite para descubrirla; no depende de metadatos exclusivos de Claude Code como `model` o `effort`.
- **SHOULD**: La elección del modelo y del esfuerzo debe corresponder a la ambigüedad y profundidad de la tarea y mantenerse en la configuración soportada por Codex, sin una tabla paralela ligada a un runtime de otro proveedor.

## Dependency Policy

<!-- Cuándo el propio plugin puede sumar una dependencia o un módulo nuevo. -->

- **MUST**: Sin dependencia dura de otros plugins del ecosistema (Ponytail, RTK) — las integraciones se detectan si están presentes, nunca son obligatorias. GitHub se usa para obtener o actualizar el marketplace y el paquete durante la instalación; el plugin no requiere red ni servicios externos en runtime.
- **SHOULD**: Preferir helpers bash chicos y de propósito único (ej. `next-feature-number.sh`) antes que agregar un framework general de automatización.

## Convenciones de Nombres

- Carpetas de skills: `plugins/spec-flow/skills/<nombre-skill>/SKILL.md`, en kebab-case y con `name` coincidente en el frontmatter; las instrucciones públicas usan el selector que Codex expone para la skill.
- Directorios de artefactos de feature: `.specs/NNN-descripcion-corta/` — `NNN` es un número de 3 dígitos con ceros a la izquierda desde `next-feature-number.sh`, `descripcion-corta` en kebab-case.
- Artefactos globales del proyecto: `.specs/constitution.md`, `.specs/backlog.md`.

## Restricciones

- Debe funcionar como un plugin portable de Codex, distribuido desde el marketplace versionado en GitHub. El acceso a GitHub sirve para recuperar o actualizar el paquete; las skills funcionan sin llamadas de red ni servicios externos en runtime.
- La raíz de artefactos es `.specs/` (con punto, oculta). Esto es un cambio limpio respecto a la convención anterior `specs/` — sin detección dual de rutas, sin migración automática de carpetas `specs/` existentes.

## Fuera de Alcance

- Sin framework general de hooks/extensiones configurable por proyecto (etapas `before_*`/`after_*`, comandos pre/post configurados por YAML) — sigue fuera de alcance. Excepción: el hook nativo de Codex usado por el propio plugin para reforzar su gate de aprobación en escrituras cubiertas (ver R04 en el Registro de Enmiendas).
- Sin capa de retrocompatibilidad para el nombre de carpeta `specs/` antiguo.
- Sin framework de automatización personalizado más allá de pequeños helpers bash de propósito único.

## Registro de Enmiendas

<!-- Append-only. Una línea por revisión posterior a la primera aprobación. Formato: - RNN (YYYY-MM-DD): <qué cambió y por qué> -->
- R01 (2026-07-09): La tabla de control documental (Nombre/Código/Versión/Fecha) de constitution/spec/plan/tasks pasa de tabla markdown a frontmatter YAML — más simple de editar mecánicamente por los skills, consistente con el frontmatter que ya usan los propios SKILL.md.
- R02 (2026-07-17): Excepción angosta al rechazo de hooks/extensions ("Principios de Código" y "Fuera de Alcance") — el propio plugin puede usar hooks nativos de Claude Code (`settings.json` `Stop`/`PreToolUse`) para hacer cumplir su gate de aprobación entre fases. El rechazo original (R01, vía spec-kit) era sobre un framework general de personalización por proyecto; ese rechazo se mantiene. Motivo: backlog item B005 — en dogfooding real (proyecto odoo-infrastructure) el modelo encadenó fases sin aprobación explícita del usuario, y el `<HARD-GATE>` en prosa no fue suficiente para evitarlo.
- R03 (2026-07-17): Migración completa a la estructura nueva de `constitution-template.md` — se agregan las secciones `Security`, `Operational Principles`, `Observability`, `Performance` y `Dependency Policy`, y cada bullet de una sección de principios queda etiquetado `MUST`/`SHOULD`/`MAY`. Todo el contenido nuevo proviene de convenciones ya practicadas en este repo (Red Flags de `finishing-branch`, reglas de severidad de `analyze`/`converge`, tabla de model/effort de `CLAUDE.md`, proceso de release de esta misma sesión) — ninguna reubicación inventa un principio no practicado. De paso se corrige el bullet de hard gates en "Principios de Código", que había quedado inconsistente con la excepción de hooks de R02.
- R04 (2026-09-12): Migración del host de Claude Code a Codex y del paquete a Agent Plugins portable: skills bajo `plugins/spec-flow/`, marketplace GitHub con fuente `git-subdir` en `main`, eliminación de reglas de modelo ligadas a `CLAUDE.md` y actualización del hook angosto de aprobación a Codex `PreToolUse`. Los hard gates en prosa siguen siendo obligatorios; el hook complementa solo las escrituras locales cubiertas y depende de la confianza explícita del usuario. GitHub es requisito de distribución, no de runtime.
