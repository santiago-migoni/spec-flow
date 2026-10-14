# Implementación del harness de Spec-Flow

Base: `935de5d:docs/designs/2026-10-14-harness-orchestration.md`.
Autorización: el usuario solicitó explícitamente implementar el plan E0–E8 en esta conversación el 2026-10-14. Migración obligatoria, una feature activa por release, conservación de evidencia vigente; sin bump, push ni publicación.

## Etapas

| Etapa | Resultado | Estado |
| --- | --- | --- |
| E0 | Viabilidad nativa Codex | Verificado en esta sesión |
| E1 | Contratos y validación | Verificado: 17 pruebas + 5 hooks |
| E2 | Skills y plantillas por release | Skills y plantillas verificadas; integración pendiente de E3/E4 |
| E3 | Aprobaciones, eventos y recuperación | En curso |
| E4 | Migración obligatoria | Pendiente |
| E5 | Orquestación Sol–Luna | Pendiente |
| E6 | Hook, convergencia y cierre | Pendiente |
| E7 | Evaluación integral | Pendiente |
| E8 | Preparación del paquete | Pendiente |

## E0 — Evidencia

- Delegación mediante `collaboration.spawn_agent`, contexto aislado (`fork_turns: none`), `gpt-6-luna`, esfuerzo `medium`.
- Registro del host: sesión `01a13b01-04c9-7653-ba40-1f257980ea46`, `turn_context.model=gpt-6-luna`, esfuerzo `medium`. No se utilizó autodeclaración del agente.
- Revisión independiente: sesión `01a13b01-65f1-7881-8485-85b759681bd9`, registro del host `gpt-6-sol`, esfuerzo `high`.
- Prueba desechable en `/private/tmp/e0-capability-probe`: normalización de releases, 3 pruebas con `python3 -B -m unittest -v test_release.py`, aprobadas por implementador y revisor.
- Interrupción controlada de Luna: `interrupt_agent` devolvió estado anterior `running`; `followup_task` reanudó sin reescribir archivos y las 3 pruebas volvieron a pasar.
- SHA256 `release.py`: `4cce23d654ddb63893a54650d21529e6f65f98e7663c5fe49c7b64ce5b263234`.
- SHA256 `test_release.py`: `be183fb467132dacdab07a906184e839a787823f3550b8bb2a9ba90653df9a80`.
- Worktree gestionado por Codex, creado desde el commit de diseño. Suite inicial del hook: 5 pruebas aprobadas.

Límites: demuestra estas capacidades en este host/sesión; no acredita todas las instalaciones de Codex. El hook actual intercepta ciertos parches, no todas las escrituras. El adaptador requerirá comprobar capacidades por ejecución y no sustituirá modelos silenciosamente.

## Decisiones de implementación

- Runtime Python con biblioteca estándar. Contratos estructurados en un bloque JSON `spec-flow` dentro del Markdown canónico; no se crea una segunda copia editable de requisitos.
- Progreso generado fuera del contenido decisorio. Las aprobaciones fijan digest de decisiones y declaración humana; no son una frontera de seguridad frente a un actor con permisos de escritura.
- Un solo implementador activo. Scripts locales nunca invocan modelos; el controlador Codex usa herramientas nativas.

## E1 — Verificación

Validadores y contrato JSON canónico en Markdown. Pruebas: 17 de contratos y 5 del hook existente. Revisión independiente Sol detectó y motivó correcciones de digest, entradas malformadas y validación transitiva. Sin dependencias externas.

## E2 — Verificación

Cuatro pruebas estructurales aprobadas. Revisión independiente Sol: conserva decisiones y referencias aprobadas, documentación técnica condicional y múltiples historias por release. La migración citada por las skills depende de E4; el flujo completo todavía no está activado. Se corrigió el bootstrap para consultar la fase destino, no su propio nombre.
