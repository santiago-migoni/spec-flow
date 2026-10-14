# Implementación del harness de Spec-Flow

Base: `935de5d:docs/designs/2026-10-14-harness-orchestration.md`.
Autorización: el usuario solicitó explícitamente implementar el plan E0–E8 en esta conversación el 2026-10-14. Migración obligatoria, una feature activa por release, conservación de evidencia vigente; sin bump, push ni publicación.

## Etapas

| Etapa | Resultado | Estado |
| --- | --- | --- |
| E0 | Viabilidad nativa Codex | Verificado en esta sesión |
| E1 | Contratos y validación | Verificado: 17 pruebas + 5 hooks |
| E2 | Skills y plantillas por release | Skills y plantillas verificadas; integración pendiente de E3/E4 |
| E3 | Aprobaciones, eventos y recuperación | Verificado: 23 pruebas del motor; 44 del plugin y 5 hooks |
| E4 | Migración obligatoria | Verificada: 12 pruebas de migración; 56 del plugin |
| E5 | Orquestación Sol–Luna | Verificada con fixtures: 70 pruebas del plugin y 5 hooks; evaluación nativa integral en E7 |
| E6 | Hook, convergencia y cierre | Verificado: 97 pruebas del plugin y 9 hooks; revisión independiente Sol |
| E7 | Evaluación integral | Verificada: proyecto nuevo y migrado nativos, interrupción y corrección fallida; 107 pruebas del plugin + 9 hooks |
| E8 | Preparación del paquete | Verificada: instalación aislada, 16 skills en chat nuevo Sol, 112 recursos, 107 + 9 pruebas reubicadas |

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

## E3 — Verificación

Registro secuencial con bloqueo, snapshots atómicos reconstruibles, aprobaciones transitivas y CLI estructurada. La revisión independiente Sol detectó transiciones inválidas, cambios posteriores a verificación y recuperación incompleta; se corrigieron con pruebas de regresión. Una interrupción exige reconciliación explícita; no vuelve a ejecutar automáticamente. Se verificaron 44 pruebas del plugin y 5 del hook. La identidad nativa de agentes y el cierre de fase siguen reservados para E5/E6.

## E4 — Verificación

Previsualización de solo lectura, mapeo explícito, candidatos canónicos, originales fijados a Git, archivo con procedencia y diario recuperable. Se corrigieron por revisión Sol la recuperación de copia/promoción, repetición de importaciones, límites de destinos y equivalencia de decisiones. Las aprobaciones históricas requieren declaración identificable y equivalencia completa; las etiquetas aisladas quedan pendientes. Evidencia histórica con fuentes, pasos y código coincidentes se acredita sin ejecutar otra vez las comprobaciones; un cambio de aceptación la deja pendiente. La adopción se recupera tras una caída entre inicio y crédito sin duplicación. Las conversiones de prosa sin equivalencia demostrable conservan su historial y requieren resolver la evidencia faltante. Verificación: 56 pruebas del plugin y 5 del hook.

## E5 — Verificación

Adaptador nativo sin llamadas a modelos desde Python, identidad de Sol/Luna comprobada contra registros del host, propiedad persistente entre worktrees, paquetes acotados y resultados contrastados con archivos reales. La revisión independiente Sol detectó nombres de capacidades incorrectos, identidad opaca y ventanas de caída al transferir control; se corrigieron y añadieron regresiones. La huella del paquete se exige en el mensaje de delegación y la identidad del padre se conserva entre transferencias. Pruebas: 70 del plugin y 5 hooks; suite focalizada del adaptador: 9. Las pruebas con identidad simulada están etiquetadas como fixtures y no sustituyen la evaluación nativa E7. El cierre de fases y la adaptación del hook permanecen en E6.

## E6 — Verificación

Cierre de fases con árbol Git fijado, revisión Sol independiente, commits recuperables y un checkpoint final de auditoría. `complete` comprueba evidencia vigente y correspondencia con código revisado, incluso frente a cambios posteriores ya commiteados. El hook comparte validación y alcance con el runtime, sin bloquear proyectos ajenos. Abandono explícito conserva historial, evidencia aplicable y límites de intentos; la recuperación distingue un agente lanzado sin vínculo de una reserva que nunca llegó a delegarse. Las ventanas de caída al preparar, commitear y liberar propiedad tienen regresiones. Revisión independiente Sol sin bloqueos restantes en el alcance evaluado. Pruebas: 97 del plugin y 9 hooks. Estas pruebas de mecánica no sustituyen la evaluación nativa E7 ni la instalación E8.

## E7 — Verificación

Dos releases desechables completaron el flujo de producción con Sol high como propietario, Luna high como implementador y un Sol high independiente revisando cada fase. Ambas terminaron con commit de fase, auditoría final, evidencia vigente y worktree limpio; impacto pendiente y publicación falsa. Una interrupción posterior a escritura conservó el código y se reconcilió sin repetirlo. Un tercer escenario de corrección deliberadamente incompleta produjo una prueba fallida y el controlador rechazó revisión aprobatoria/cierre. Evidencia portable en `plugins/spec-flow/evals/native/evaluation-report.md`, junto con fuentes, resultados, procedencia, métricas y hashes.

La evaluación real detectó dos defectos que los fixtures anteriores no mostraban: el host cifra los prompts de delegación y el reducer conservaba el agente del intento previo. El adaptador ahora vincula la llamada nativa por hash del marcador, salida exacta y parentesco; el segundo intento limpia el vínculo anterior y conserva su tiempo original. Se añadió restauración explícita de paquetes ignorados por Git: reconstrucción con el mismo hash y sin nuevo intento, con pruebas deterministas y revisión Sol independiente. La restauración de paquetes no se presenta como ensayo nativo. Suite final de esta etapa: 107 pruebas del plugin y 9 hooks.

La referencia Sol usa exactamente la misma suite de cuatro métodos. Se registraron duración y consumo disponible; la evaluación incluye preparación, fallos inyectados, reparación del harness y una interrupción por límite de uso. No demuestra ahorro de tiempo ni costo.

## E8 — Verificación

Paquete instalado con identidad temporal independiente y rutas con espacios; 112 recursos coinciden por hash. Las suites reubicadas pasaron 107 pruebas del plugin y 9 hooks. Un cliente nuevo de app-server descubrió las 16 skills; Sol inició un proyecto vacío desde el runtime instalado y obtuvo el gate de constitución habilitado. Un chat nuevo adicional, autorizado explícitamente, recibió las 16 skills en su catálogo inicial y verificó referencias. La prueba del CLI independiente rechazó el modelo Sol; no se sustituyó, y la evaluación se realizó mediante Codex Desktop. Se retiraron plugin y marketplace temporales y se verificaron listados previos idénticos. Detalles y límites en [harness-distribution.md](harness-distribution.md).

README, guía del repositorio, manifiestos, marketplace y Unreleased reflejan el alcance evaluado. Propuesta de versión incompatible: **2.0.0**, pendiente de autorización de corte; ambos manifiestos conservan **1.1.0**. Sin tag, publicación ni integración en main.
