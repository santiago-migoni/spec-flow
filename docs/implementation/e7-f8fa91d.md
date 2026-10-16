# F-01 y reevaluación E7 — f8fa91d

Fecha: 2026-10-16. **F-01 corregida y validada mediante regresiones; E7 NO APROBADA por un nuevo bloqueo HIGH F-02.** La nueva evaluación llegó a preparar tres proyectos y runs nativos, pero no pudo delegar la primera implementación ni completar la conciliación. No se atribuyen a este commit los éxitos nativos de candidatos anteriores.

## Corrección de F-01

Commit de corrección: `f8fa91d2c98927eeaba3af0643e9973e9a1e506f`, sobre `4154db084d55ed7de4e9a14a11ec7beebd785237`. Cambios funcionales limitados a [phases.py](../../plugins/spec-flow/harness/runtime/phases.py#L571), sus regresiones y Unreleased; versión 2.0.0 sin cambios.

El lector de cierre ahora usa el validador compartido estricto cuando un bloque generado no es un registro derivado. El progreso inicial válido significa ausencia de registro de cierre; no confiere autoridad. Conserva el rechazo de bloques incompletos, duplicados, fuera de posición, prosa arbitraria y registros derivados inválidos. Las comprobaciones de aprobación/digests, evidencia vigente, código/árbol revisados, HEAD, correspondencia con registros persistidos y recuperación permanecen vigentes.

| Prueba de la corrección | Resultado y evidencia |
| --- | --- |
| Regresión previa al cambio | F-01 reproducida con bloques literales de spec/roadmap; [red confirmado](evidence/f01-fix/red-confirmed.txt) |
| Primer cierre y auditoría | Pasa desde esos bloques, con idempotencia, flags de cierre y padre del audit comprobados |
| Recuperación | Pasan escritura parcial y evento previo a auditoría partiendo de bloques iniciales |
| Controles de registros | Rechazados reemplazo de cierre persistido por progreso y colas malformadas |
| Suite de fase/cierre | 22 pruebas aprobadas; [salida](evidence/f01-fix/green-phases.txt) |
| Suite completa antes del commit | 120 del plugin + 9 del hook aprobadas; [evidencias de corrección](evidence/f01-fix/README.md) |
| Revisión independiente | Sin hallazgos bloqueantes; repitió 120 + 9; [informe y hashes revisados](evidence/f01-fix/independent-review.json) |
| Exportación del nuevo commit | 120 + 9 aprobadas de nuevo; [plugin](evidence/e7-f8fa91d/deterministic-tests.txt), [hook](evidence/e7-f8fa91d/hook-tests.txt) |
| Ambos templates literales | Lector de cierre acepta progreso como `None`, no como cierre; [comprobación independiente](evidence/e7-f8fa91d/F-01-literal-template-check.json) |

Las pruebas del controlador usan adaptadores de fixture cuando corresponde. Acreditan esas regresiones, no una nueva implementación nativa, instalación ni preparación para publicar. El primer ensayo de test tenía además una aserción de contexto incorrecta; se corrigió antes de tocar producción y se conservaron ambas salidas. Los dos avisos de espacios finales en el diff del commit están solo en salidas unittest verbatim; el diff de código/tests/changelog pasa sin avisos. [Registro del chequeo](evidence/e7-f8fa91d/patch-whitespace-check.json).

## Identidad y autoridad de la nueva E7

| Elemento | Valor |
| --- | --- |
| Commit evaluado | `f8fa91d2c98927eeaba3af0643e9973e9a1e506f` |
| Paquete exportado | 115 archivos exactos; 14 skills y 14 templates; manifiestos espejo; versión 2.0.0 |
| Directorio desechable | `/private/tmp/spec-flow-e7-f8fa91d-1fyed3ur` |
| Orquestador real | `gpt-6-sol/high`, sesión `01a1451c-0ecd-7c93-9d51-8650fdaf887f` |
| Linaje | Hijo `/root/e7_owner_f8fa91d` de `01a13f8c-b50f-7db0-b28d-162f4914e043` |
| Implementadores/revisores nuevos | Ninguno llegó a crearse para las tareas/fases de esta E7 |
| Autoridad | Pedido literal del usuario; decisiones/recibos E7 Evaluator sintéticos exclusivos de los fixtures |

[Fuente, archivo exportado y hashes](evidence/e7-f8fa91d/source-and-scope.json), [plan previo](evidence/e7-f8fa91d/evaluation-plan.md), [paquete](evidence/e7-f8fa91d/package-checks.json), [preflight independiente](evidence/e7-f8fa91d/owner-preflight-independent.json). Se atestaron perfil, parentesco y turnos reales del propietario. No hubo FakeAdapter en los runs nativos, sustitución de perfiles ni APIs externas.

## Escenarios y resultado observado

| Fixture / run | Realizado | Estado final |
| --- | --- | --- |
| fresh / `ea84dc87-11c2-46ef-b0d8-d2f0665fb824` | Suite fija falla sobre stub; documentos validados; gate rechaza siete recibos ausentes y acepta siete nuevos; capabilities/start/prepare | Primer spawn rechazado por límite del host; luego conciliación bloqueada por F-02 |
| legacy / `8d1d0189-840d-4749-b4d8-f54718fe8c0c` | Originales comprometidos, preview/revisión/apply, importación de autoridad cero, recibos nuevos, start/prepare | Sin hijo lanzado; conciliación bloqueada por F-02 |
| negative / `db79a022-629d-4243-8445-dc801d1b2be6` | Proyecto y recibos propios, baseline fallida, start/prepare | No llegó a los fallos/correcciones inyectados; conciliación bloqueada por F-02 |

Los tres conservan intento 1, `active_task=T-001`, tarea `reconciliation_required`, sin agente vinculado, resultado, evidencia aprobatoria, fase ni cierre. No se cambiaron `release.py` ni `test_release.py` respecto de sus baselines. La suite fija retiene SHA256 `7bb24f05e31ffe3fdb53c96895e3462a5823fe7ac9ad4bdbe0e612d206cd0577`.

La migración legacy preservó el commit original `249e47ff5ba48fb3dc0967b40182450c46e896f0` y sus fuentes. ID `87f92dbb7045575e98080d00f6578817`; preview `852a016879aa3c5c6163290e6dc02b3f1069b284ba17e5d1c5d552bc50a35f41`. Etiquetas Approved y casillas importaron cero aprobaciones y cero evidencias. [Procedencia](evidence/e7-f8fa91d/native/legacy/original-snapshot.json), [revisión de candidatos](evidence/e7-f8fa91d/native/legacy/candidate-review.json) y operaciones efectivas en [legacy](evidence/e7-f8fa91d/native/legacy/operations.jsonl).

Se detectó una omisión de preparación: architecture tenía sus secciones y decisiones en prosa, pero faltaban las dos tablas aplicables. Structure sí incluyó tree anotado y tablas; las otras seis formas tenían sus tablas. Se conservan las fuentes aprobadas originales. La revisión R01 y adopción de dependencias quedaron pendientes porque la conciliación y el abandono no pudieron completarse. Es una limitación del fixture, no un defecto atribuido al plugin. Una referencia de capability en legacy anticipó indebidamente una interrupción aún no realizada; se preservó y corrigió explícitamente en [capability-reference-correction.json](evidence/e7-f8fa91d/native/legacy/capability-reference-correction.json); no se cuenta como prueba de interrupción nativa.

## Incidentes de host y recuperación

El primer spawn falló con `agent thread limit reached`: dos hijos históricos figuraban `pending_init`. Interrumpirlos no liberó por sí solo el estado. Un followup limitado a finalizar, sin herramientas ni trabajo nuevo, hizo que ambos confirmaran `completed`; el inventario mostró los slots liberados. No se reutilizaron sus sesiones para las nuevas tareas. [Registro del inventario y conciliación](evidence/e7-f8fa91d/host-inventory-recovery.json).

Antes de cambiar fuentes aprobadas se intentó `interrupt → resume → reconcile(no_spawn)` sobre los tres runs. El primer intento de conciliación rechazó `host_agent_reused` porque exigía un turno del propietario posterior a `prepare`. Un followup real al mismo Sol/high produjo ese turno; no se editaron timestamps ni logs. Superado ese control, apareció F-02 durante el barrido de metadatos.

## F-02 — Metadato ajeno válido bloquea la conciliación sin hijo

**Severidad: HIGH. Reproducido en los tres runs y de forma independiente, sin mutación.**

En [codex_adapter.py:249](../../plugins/spec-flow/harness/runtime/codex_adapter.py#L249), `attest_no_spawn` recorre sesiones del host y evalúa `source.get("subagent", {}).get("thread_spawn", {})`. Un registro ajeno al propietario tiene `source.subagent` de tipo string. El código intenta llamar `.get()` sobre ese texto **antes de filtrar el parentesco** y lanza `AttributeError: 'str' object has no attribute 'get'`.

El CLI termina con exit 1 y traceback, sin devolver el rechazo estructurado habitual ni conciliar la reserva. El inventario y la inspección independiente encuentran cero hijos de este propietario y los archivos de tarea intactos; el defecto impide demostrarlo mediante la ruta soportada. No se observó aceptación indebida ni liberación de propiedad sin control.

Evidencia primaria: entradas, salidas y traceback completos en [fresh](evidence/e7-f8fa91d/native/fresh/operations.jsonl), [legacy](evidence/e7-f8fa91d/native/legacy/operations.jsonl) y [negative](evidence/e7-f8fa91d/native/negative/operations.jsonl). La [comprobación independiente](evidence/e7-f8fa91d/native-independent-check.json) volvió a atestar al propietario, verificó cero hijos, estado/lease/baselines y reprodujo la excepción con el adapter de producción sin cambiar archivos ni registro de propiedad.

Se retienen solo identificador/tipo/hashes del metadato, sin copiar contenido privado. Hash canónico UTF-8 del primer `session_meta`: `e5dcb28e59645366a2d91781d3b67166ac84101608628ea289fb30d53c2b57bd`. El resumen del propietario usa serialización ASCII escapada y da `d7dcb1e1b823f564ffc931deb59a610cfd15020a57d89c674066e4f5ea3d7f49`; ambos dominios se verificaron y explicitan en la comprobación independiente.

Corrección propuesta para el siguiente trabajo: reconocer tipos legítimos de metadatos antes de acceder al linaje, preservar la selección por padre y mantener los rechazos de hijos activos, omitidos, reutilizados, no atribuibles o vinculados al paquete. Añadir regresión con metadato ajeno `subagent` string y controles negativos de hijos propios. No filtrar `CODEX_HOME`, esconder logs, inventar inventarios, limpiar leases ni cambiar perfiles para superar el ensayo. El candidato evaluado permanece intacto.

## Controles complementarios y cobertura pendiente

| Comprobación | Resultado |
| --- | --- |
| Suites del paquete exportado | 120 + 9 aprobadas; evidencia determinista separada |
| Consulta estricta real | 12 consultas status/gate/validate/digest sin cambios de bytes, permisos ni mtime; [registro](evidence/e7-f8fa91d/consultation-tests.json) |
| Kinds inexistentes | design/backlog/using-spec-flow rechazados; sin mutaciones |
| Prerrequisitos nativos | Perfil de implementador Sol y capacidad faltante rechazados; [probes](evidence/e7-f8fa91d/native-prerequisite-negative-probes.json) |
| F-01 literal | Ambos templates aceptados como progreso sin cierre |
| EV-01 / EV-03 | Gates sin/con recibos y migración real observados en preparación |
| EV-05 / EV-10 | Recuperación y controles de identidad efectivamente ejercitados; conciliación falla por F-02 |
| EV-02 / EV-12 | Implementación nativa, convergencia, revisión, auditoría y finishing no alcanzados |
| EV-06 / EV-07 / EV-08 / EV-09 / EV-13 / EV-14 / EV-15 | Suite determinista aprobada; sin acreditar casos nativos nuevos no realizados |
| EV-04 / EV-11 | Probes sobre historia nativa nueva revisada y enrutamiento semántico no realizados; no había esa historia |

No se ejecutaron las tres correcciones deliberadas, interrupción después de escritura de Luna ni restauración de su paquete: eran objetivos del plan, no resultados. Tampoco se ejecutó E8, instalación, integración, bump, push, tag, publicación ni despliegue. Los tests del hook no prueban confianza/instalación en el host. No se atribuyen impactos de negocio ni ahorros de tiempo/costo.

## Preservación y estado para continuidad

Los tres proyectos permanecen bajo `/private/tmp/spec-flow-e7-f8fa91d-1fyed3ur`. **Sus registros de propiedad siguen activos** en los directorios Git comunes desechables. No se afirmó abandono: el controlador requiere la conciliación que F-02 bloquea. No hay hijos propios activos, pero sí reservas de tarea que necesitan recuperación soportada. No se borró ni liberó nada manualmente.

Se preservaron bundles Git verificados, snapshots byte a byte de fuentes/recibos/eventos/estado/paquetes, registros históricos de propiedad y baselines. Las copias son evidencia forense, no autorización ejecutable; no restaurar leases ni reanudar runs por copiar archivos. [Inventario de conservación](evidence/e7-f8fa91d/preservation-summary.json), [guía](evidence/e7-f8fa91d/README.md) y [SHA256SUMS](evidence/e7-f8fa91d/SHA256SUMS).

La continuidad requiere corregir F-02 en un commit separado conservando controles, conciliar/abandonar estos runs por operaciones soportadas y repetir E7 con proyectos nuevos y fixtures completos. F-01 cuenta con regresiones aprobadas; la validación nativa integral sigue pendiente.
