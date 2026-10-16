from pathlib import Path
from datetime import datetime,timezone
import json
R=Path('/Users/santiago_migoni/Documents/Projects/spec-flow');E=R/'docs/implementation/evidence/e7-e9fe146';n=json.loads((E/'native-independent-check.json').read_text());s=json.loads((E/'native/native-summary.json').read_text())
observations=[{'id':'OBS-01','classification':'procedimiento del evaluador','description':'Texto histórico F03 copiado en los primeros payloads de autorización. La autorización humana actual cubre esos proyectos y PH-01; se conservan recibos y eventos originales, sin reescritura.','evidence':'native/authorization-provenance-discrepancy.json'},{'id':'OBS-02','classification':'preparación del fixture','description':'Faltó el checkpoint Git de la primera migración. phase-ready rechazó phase_scope_changed. Run abandonado por controlador, preservado, repetido en otro fixture con checkpoint. No se modificó el candidato.','evidence':'native/fixture-recovery.json'},{'id':'OBS-03','classification':'procedimiento del revisor','description':'El revisor ejecutó git write-tree y obtuvo el árbol ya fijado. Se verifican árbol y padre exactos; no cambió índice, código ni commits.','evidence':'native/reviewer-procedure-limitation.json'},{'id':'OBS-04','classification':'invocación del evaluador','description':'Primer bind-agent omitió dos campos; invalid_input rechazó la solicitud. Se corrigió usando la identidad nativa real, sin editar registro.','evidence':'native/fresh/operations.jsonl'},{'id':'OBS-05','classification':'límite de medición','description':'Las baselines de fallo se reprodujeron después desde el árbol Git inicial inmutable. No se atribuyen a una ejecución previa a la implementación.','evidence':'native/native-summary.json'}]
(E/'findings.json').write_text(json.dumps({'evaluated_commit':s['candidate'],'result':'PASS within documented E7 scope','candidate_blocking_findings':[],'evaluator_observations':observations,'no_candidate_fix_applied':True,'E8_pending_for_this_candidate':True},ensure_ascii=False,indent=2)+'\n')
report='''# E7 — YAML y perfiles configurables sobre e9fe146

Resultado: **APROBADA dentro del alcance E7 evaluado**, el 2026-10-16. Candidato inmutable: `e9fe1461727e7b508143646132e2b9bc9ba5c16c`; versión de paquete conservada: `3.0.1`. Sin hallazgos bloqueantes del candidato en estas pruebas. Se registran cinco observaciones del evaluador, con límites y recuperación explícitos. **No establece distribución instalada ni autorización de publicación:** E8 debe repetirse sobre este candidato antes de declarar que está listo para una nueva release.

[Plan](evidence/e7-e9fe146/evaluation-plan.md) · [Fuente y autorización](evidence/e7-e9fe146/source-and-scope.json) · [Hallazgos y observaciones](evidence/e7-e9fe146/findings.json) · [Verificación independiente nativa](evidence/e7-e9fe146/native-independent-check.json) · [Checksums](evidence/e7-e9fe146/SHA256SUMS)

## Fuente, host y perfiles

La evaluación usa `git archive` del commit solicitado, 139 archivos del paquete con hashes exactos, en una ruta temporal; no usa la instalación del usuario. [Inventario de disponibilidad del host](evidence/e7-e9fe146/host-model-inventory.json). El catálogo declarado solo demuestra disponibilidad informada; el adaptador comprobó además perfiles reales, filiación padre/hijo, marcadores de delegación y ciclo de vida de las sesiones.

| Rol | Modelo | Esfuerzo | Evidencia |
| --- | --- | --- | --- |
| Orquestador persistente | `gpt-6.1-sol` | `low` | Sesión real `01a14601-755e-7623-8d98-bbdcf02b03e6` |
| Implementadores, uno activo por run | `gpt-6-luna` | `high` | Hijos nativos, con packet y tarea/attempt vinculados |
| Revisores de fase distintos | `gpt-6.1-sol` | `medium` | Dos sesiones independientes, árboles y padres exactos |

Se atestaron nueve sesiones de orquestación/tareas/revisión, contando el primer fixture legacy retirado, y dos probes nativos de capacidad separados. Los probes no confieren crédito de implementación. La comprobación de snapshots confirmó que cambiar temporalmente el esfuerzo del revisor en config a `low` conserva `medium` en el run existente; se restauró config. Los packets de tarea y fase contienen los perfiles fijados y conservan sus hashes. [Prueba de snapshot](evidence/e7-e9fe146/native/profile-snapshot.json).

## Ejecución nativa

La conducta real evaluada es `normalize_release`: SemVer numérico ASCII estricto, prefijo `v` opcional, ceros canónicos, componentes grandes conservados, y errores distintos para tipo o formato inválidos. Solo `release.py` era editable. La suite fija de cuatro métodos se conservó con SHA256 `7bb24f05e31ffe3fdb53c96895e3462a5823fe7ac9ad4bdbe0e612d206cd0577`. Las decisiones y aprobaciones son sintéticas y solo autorizan estos repositorios desechables.

| Proyecto | Run | Resultado observable |
| --- | --- | --- |
| Nuevo, documentos YAML | `8a974b4c-ef05-4e2c-b323-6a8899b93552` | Bloqueo sin aprobaciones; siete recibos nuevos; Luna escribió y fue interrumpida; reconciliación del resultado sin repetir intento; recuperación del packet con hash idéntico; cuatro pruebas pasan; close duplicado produce un solo cierre; revisión independiente, commit de fase y auditoría |
| Legacy, documentos JSON existentes | `b9ec36e0-76a6-47af-9ffa-46182ff826c1` | Migración explícita conserva tres originales; no importa aprobación/evidencia histórica; siete recibos nuevos; cuatro pruebas pasan; revisión independiente, commit de fase y auditoría |
| Fallos deliberados | `ef85c65c-d92d-4034-8f5b-ce35243519d6` | Tres hijos nativos reales, cada implementación incorrecta rechazada por la suite fija; prepare adicional devuelve `task_already_active`; retry devuelve `retry_limit`; abandono con hijo terminal conserva historial y libera propiedad; técnico incompleto |

Los fallos negativos son inyección del evaluador, no una medición de calidad de Luna. Las baselines rojas se reprodujeron después desde el árbol Git inicial; no se presentan como comandos anteriores a la implementación.

| Proyecto | Commit de fase | Auditoría final |
| --- | --- | --- |
| YAML | `48a248943c3e0c12bccb9fa88cb303476e6c95d3` | `17c8a288408ae36c455530f37b0030e4731fc416` |
| Legacy JSON | `a6cb35569033157c74010640d1298f206cdddf08` | `7c964e11626d6a2927285ae4b59bdcb98dfd1da9` |

En los dos flujos positivos, `technical_complete=true`, revisión y auditoría pendientes en falso, impacto `pending`, publicación y efectos externos en falso; ramas conservadas. Ninguno de los cuatro runs, incluido el primer legacy retirado, conserva una reserva activa. El negativo sigue incompleto y abandonado: no se convirtió en una release exitosa. [Resumen nativo](evidence/e7-e9fe146/native/native-summary.json) · [Consultas y reservas finales](evidence/e7-e9fe146/native/ownership-final.json).

## Cobertura y controles

| Escenario | Categoría actual | Evidencia y resultado |
| --- | --- | --- |
| EV-01, aprobaciones faltantes | Nativa + determinista | Gate impide implementación sin recibos vigentes |
| EV-02, comportamiento real | Nativa | YAML y JSON: implementación, suite fija, revisión, cierre y commit |
| EV-03, legacy | Nativa + determinista | Migración y tres originales verificados contra Git; cero imports; nuevos recibos |
| EV-04, evidencia obsoleta | Producción complementaria + determinista | Clones separados: cambio de código o prosa YAML aprobada invalida complete; originales intactos |
| EV-05, interrupción | Nativa + determinista | Escritura real, interrupción nativa, reconciliación del mismo intento |
| EV-06, close duplicado | Nativa + determinista | Un único evento closed |
| EV-07, límite | Nativa + determinista | Tres intentos fallidos; cuarto bloqueado sin crear otro hijo |
| EV-08, alcance | Producción + determinista | Primer legacy bloqueado por cambios de migración ajenos; suite comprueba cambios fuera de scope |
| EV-09, cero casos | Determinista | Suite del controlador rechaza resultados vacíos/cero casos |
| EV-10, capacidad e identidad | Nativa + probes de producción + determinista | Identidades reales y cuatro precondiciones inválidas rechazadas; sin sustitución |
| EV-11, decisión compartida | Evaluación de instrucciones de revisor nativo | Hipótesis de API/arquitectura: detener y volver a design/aprobaciones/plan/tasks; no se ejecutó una migración de arquitectura real |
| EV-12, impacto pendiente | Nativa + determinista | Separación técnica/impacto/publicación; retención de rama |
| EV-13, dos propietarios | Determinista | Suite del adaptador comprueba lease compartido; no es prueba de dos orquestadores nativos simultáneos |
| EV-14, journal corrupto | Determinista | Rechazo de cola corrupta, reconstrucción solo de eventos válidos |
| EV-15, fuentes alteradas | Producción complementaria + determinista | Cambio de fuente YAML tras aprobación invalida completion; suite valida frescura transitiva |

[Suite del controlador: 152 aprobadas](evidence/e7-e9fe146/deterministic/controller.log), [hooks: 10 aprobadas](evidence/e7-e9fe146/deterministic/hooks.log). Fixtures de atestación en tests deterministas no sustituyen las sesiones reales. Además: [12 consultas sin cambios de archivos/metadatos](evidence/e7-e9fe146/consultation-tests.json), tres gates inexistentes rechazados, [21 documentos con secciones/tablas/tree válidos](evidence/e7-e9fe146/fixture-shape-independent-check.json), [migración comprobada independientemente](evidence/e7-e9fe146/migration-independent-check.json), [dos probes de obsolescencia](evidence/e7-e9fe146/completion-staleness-negative-probes.json) y [cuatro precondiciones negativas](evidence/e7-e9fe146/native-prerequisite-negative-probes.json).

Los HARD-GATE son idénticos al commit padre, salvo el reemplazo autorizado de Sol high fijo por atestación del perfil fijado en implement; el resto de ese bloque permanece idéntico. El handler del hook no cambió. [Comparación](evidence/e7-e9fe146/control-invariants.json). No se deshabilitaron controles, importaron recibos ficticios como históricos ni editaron registros para forzar éxito.

## Incidencias del evaluador y trazabilidad

1. Un helper conservó texto histórico F03 en los primeros start. La autorización humana actual cubre esos alcances; se deja constancia y no se reescriben recibos/eventos. Helper corregido para los siguientes starts.
2. El primer legacy omitió el checkpoint Git de la migración. `phase_scope_changed` detuvo el cierre. Run `0120653b-a9de-4be8-b45d-bb933fca0c6e` abandonado mediante controlador y preservado; otro fixture migró y registró el checkpoint antes de ejecutar. Se conserva la distinción entre ambos.
3. El revisor final ejecutó `git write-tree` al inspeccionar el árbol. Devolvió el árbol fijado; no cambió índice, fuentes ni commits. Se registra como desviación de la inspección pretendida.
4. Un primer bind-agent omitió campos; el controlador lo rechazó y luego se vinculó la identidad real.
5. Las baselines iniciales se reprodujeron desde Git después, sin atribuirles orden temporal previo.

[Observaciones completas](evidence/e7-e9fe146/findings.json). Un checker auxiliar inicial también detectó bytecode generado por subprocess de tests: se excluyen únicamente `__pycache__/*.pyc` y se verifican los 139 archivos originales por hash. Esto no es un cambio del código candidato.

## Preservación, reproducción y límites

[Cuatro Git bundles verificados y snapshots](evidence/e7-e9fe146/preservation-summary.json), incluidos el run retirado y el negativo abandonado. Cada proyecto conserva `.specs`, registros/packets/evidencias `.spec-flow`, implementación y prueba fija. Los snapshots sirven para inspección histórica; no restauran autoridad de sesión, aprobación ni propiedad activa. Los comandos exactos y códigos de salida están en cada `native/*/operations.jsonl`; los scripts de preparación y comprobación están en `reproduction/`. Las rutas temporales y UUID identifican esta ejecución y deben adaptarse al reproducirla, sin importar sus recibos como autoridad nueva.

[Integridad final](evidence/e7-e9fe146/final-integrity.json): fuente exportada y checkout sin cambios, HEAD/branch/tags conservados y manifiestos 3.0.1 idénticos. Solo se agregaron/actualizaron documentos y evidencias de esta evaluación. No se hizo commit, push, tag, publicación, integración ni actualización de instalación. No se migraron proyectos del usuario.

Alcance: una ejecución por escenario en este host, conducta pequeña y decisiones sintéticas. No demuestra coherencia semántica universal, rendimiento de otros modelos/hosts, confianza del hook instalado, despliegue, distribución ni ahorro de tokens/costo. E8 de candidatos anteriores conserva su alcance histórico; no acredita la instalación de e9fe146.
'''
(R/'docs/implementation/e7-e9fe146.md').write_text(report)
for name in ['harness-progress.md','harness-distribution.md']:
 p=R/'docs/implementation'/name;old=p.read_text();heading,rest=old.split('\n',1)
 entry='\nComprobación de desarrollo más reciente: [E7 sobre e9fe146, 2026-10-16](e7-e9fe146.md), **aprobada dentro de su alcance** con YAML, compatibilidad JSON y perfiles `gpt-6.1-sol/low` → `gpt-6-luna/high` → `gpt-6.1-sol/medium`. 152 + 10 pruebas deterministas; ejecución nativa y controles registrados. E8 sobre este candidato sigue pendiente. No hubo publicación ni actualización de instalación; los estados siguientes conservan su alcance histórico.\n'
 p.write_text(heading+'\n'+entry+rest)
print('Report, findings and current E7 pointers written')
