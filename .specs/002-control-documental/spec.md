# Spec: Tabla de Control Documental

| Nombre | Código | Versión | Fecha |
|---|---|---|---|
| control-documental | SPEC-002 | R00 | 2026-07-04 |

**Estado**: Converged (2026-07-04)

## Clarifications

### Sesión 2026-07-04

- Q: ¿Los cambios previos a la aprobación (borrador inicial, iteraciones de "On revision request" antes de que el usuario confirme, respuestas de `clarify`) suben la Versión, o solo lo hacen los cambios posteriores a la aprobación? → A: Antes de la aprobación, ningún cambio sube la Versión — el documento permanece en `R00`. Solo un cambio pedido **después** de que el usuario ya aprobó el documento sube la Versión.
- Q: Los templates (`skills/*/assets/*-template.md`) están en inglés, como el resto del plugin — ¿los encabezados de la tabla (Nombre/Código/Versión/Fecha) van en inglés en el template, traducidos a español solo en los documentos de este proyecto, o van en español directamente en el template? → A: En inglés en el template (`Name / Code / Version / Date`), igual que el resto del contenido del template; se traducen a español al escribir los documentos de este proyecto, como ya se hace con el resto.
- Q: ¿Qué hacemos con las líneas de referencia cruzada `**Spec**:`/`**Plan**:` que hoy tienen `plan.md`/`tasks.md`, al agregar la tabla? → A: Se eliminan — el Código compartido (mismo `NNN` en `SPEC-NNN`/`PLAN-NNN`/`TASKS-NNN`) ya vincula los documentos entre sí, sin necesidad de duplicar la ruta completa.
- Q: En la tabla, ¿qué valor exacto lleva el campo "Nombre" de `spec.md`/`plan.md`/`tasks.md`? → A: El `short-description` en kebab-case de la carpeta de la feature (ej. `control-documental`) — el único identificador ya normalizado que existe hoy.

## Resumen

Agregar una tabla de control documental (Nombre / Código / Versión / Fecha) al inicio de los templates de `constitution`, `spec`, `plan` y `tasks`, para dar trazabilidad formal de identidad y revisión a cada artefacto de spec-flow — aplicando una técnica estándar de gestión documental. Los templates en sí (`skills/*/assets/*-template.md`) llevan los encabezados en inglés (`Name / Code / Version / Date`), igual que el resto del plugin; se traducen a español solo al escribir los documentos concretos de este proyecto.

## Historias de Usuario

### US1 — `spec.md`/`plan.md`/`tasks.md` incluyen tabla con código único por documento (P1)

Como usuario de spec-flow, cada documento de una feature tiene al inicio una tabla con: Nombre (el `short-description` en kebab-case de la carpeta de la feature, ej. `control-documental`), Código (identificador único: `SPEC-NNN`/`PLAN-NNN`/`TASKS-NNN`, mismo `NNN` que la carpeta de la feature), Versión (revisión, arranca en `R00`) y Fecha (ISO `YYYY-MM-DD`). Esta tabla reemplaza los campos sueltos `**ID**`/`**Creado**` que hoy encabezan cada documento.

**Escenarios de Aceptación**:
- **Dado** que se genera un `spec.md` nuevo, **Cuando** `specify` lo escribe, **Entonces** incluye la tabla con Código `SPEC-NNN` (mismo `NNN` de la carpeta) y Versión `R00`.
- **Dado** que se generan `plan.md` y `tasks.md` para la misma feature, **Cuando** se escriben, **Entonces** usan `PLAN-NNN`/`TASKS-NNN` respectivamente (mismo `NNN`), cada uno con su propia Versión arrancando en `R00`.
- **Dado** que el campo `**Estado**` (Draft/Converged) ya existe en `spec.md`, **Cuando** se aplica la tabla, **Entonces** `**Estado**` se mantiene como línea separada debajo de la tabla — no se fusiona con Versión, porque son conceptos distintos (estado del flujo de fases vs. número de revisión del documento).
- **Dado** que `converge` y `finishing-branch` leen el campo `**Estado**` para sus gates, **Cuando** se aplica este cambio, **Entonces** siguen funcionando sin modificación, porque `**Estado**` no cambia de nombre ni de posición semántica.
- **Dado** que `plan.md`/`tasks.md` hoy tienen líneas `**Spec**:`/`**Plan**:` de referencia cruzada, **Cuando** se aplica la tabla, **Entonces** esas líneas se eliminan — el Código compartido (mismo `NNN`) ya vincula los documentos sin duplicar la ruta completa.

### US2 — La constitution incluye la tabla sin columna Código (P1)

Como usuario, `constitution.md` tiene la tabla con Nombre (nombre del proyecto) / Versión / Fecha, sin columna Código — es un documento único a nivel proyecto, no repetible por feature, así que un código de identificación no aporta trazabilidad adicional.

**Escenarios de Aceptación**:
- **Dado** que se escribe o actualiza la constitution, **Cuando** se aplica la tabla, **Entonces** reemplaza los campos actuales `**Project**`/`**Updated**` y no incluye columna Código.
- **Dado** que la constitution se actualiza por segunda vez, **Cuando** se guarda la revisión, **Entonces** Versión pasa de `R00` a `R01`.
- **Dado** que la constitution incluye una sección `## Registro de Enmiendas` debajo de la tabla, **Cuando** se guarda cualquier revisión, **Entonces** se agrega una línea `- RNN (YYYY-MM-DD): <qué cambió y por qué>` — un log append-only, nunca se reordena ni se edita una línea ya escrita.

### US3 — La versión sube solo con cambios posteriores a la aprobación (P2)

Como usuario, un documento permanece en `R00` durante todo el ciclo previo a mi aprobación — borrador inicial, iteraciones de "On revision request" antes de confirmar, respuestas de `clarify` — sin importar cuántos ajustes tenga. Recién cuando pido un cambio **después** de haber aprobado el documento, la Versión sube en uno.

**Escenarios de Aceptación**:
- **Dado** un `spec.md` recién escrito y todavía no aprobado, **Cuando** pido dos o tres ajustes seguidos antes de aprobarlo, **Entonces** Versión se mantiene en `R00` durante todos esos ajustes.
- **Dado** un `spec.md` que ya aprobé (`R00`), **Cuando** pido una revisión después de esa aprobación y el skill la aplica, **Entonces** Versión pasa a `R01`.
- **Dado** que `converge` agrega tareas en un `## Phase N: Convergence` a `tasks.md`, **Cuando** lo hace, **Entonces** eso NO cuenta como revisión — no bumpea Versión de `tasks.md` (es una acción automática de cierre de brecha, no una revisión de intención pedida por el usuario).

## Casos Borde

- Un documento que nunca fue revisado después de su escritura inicial permanece en `R00` indefinidamente — no hay incremento automático por el paso del tiempo.
- La constitution nunca tiene columna Código, por diseño (US2) — no es un caso a resolver, es la regla.
- Si el usuario pide varias revisiones seguidas antes de aprobar, ninguna sube la Versión — todas ocurren mientras el documento sigue en `R00`, sin aprobar.

## No-Objetivos Explícitos

- El registro de enmiendas (`## Registro de Enmiendas`) aplica solo a `constitution.md` — `spec.md`/`plan.md`/`tasks.md` se quedan con el bump de Versión (US3) sin un log detallado propio, porque el historial de git y los resúmenes de "On revision request" ya dan esa trazabilidad para documentos de feature, que son mucho más frecuentes que cambios de constitution.
- No se unifica el formato de fecha a `dd-mmm-yyyy` — se mantiene ISO `YYYY-MM-DD` en la tabla, en el registro de enmiendas y en el resto del repo, tal como se usa hoy.
- No se agrega campo de ratificación/aprobación formal (sin "Ratified by" ni firma).
- Sin cambios a la lógica de gates existente — `**Estado**` sigue siendo exactamente lo que `converge`/`finishing-branch` ya leen y escriben.

## Preguntas Abiertas

Ninguna — la ambigüedad de versión pre/post aprobación se resolvió con el usuario (ver `## Clarifications`).
