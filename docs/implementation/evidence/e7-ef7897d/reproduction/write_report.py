"""Write the evaluation report only after independent native checks pass."""
import json
from pathlib import Path
R=Path(__file__).resolve().parents[5];E=Path(__file__).resolve().parents[1];c=json.loads((E/'source-and-scope.json').read_text());n=json.loads((E/'native-independent-check.json').read_text());recovery=json.loads((E/'recovery/independent-check.json').read_text())
assert n['positive_native_closures_verified']==2 and n['negative_lease_released'] and recovery['result']=='PASS'
fixtures=n['fixtures'];negative=fixtures['negative'];assert negative['status']=='abandoned' and negative['attempt']==3 and negative['task_status']=='verification_failed'
rows=[];commits=[]
for label,title in [('fresh','Nuevo'),('legacy','Migrado'),('negative','Negativo')]:
    f=fixtures[label];phase=f['phases'].get('PH-01',{}).get('commit',{}).get('sha','—');audit=(f.get('audit') or {}).get('sha','—')
    rows.append(f"| {title} | {f['run_id']} | {f['attempt']} | {f['status']} | {f['task_status']} | {'Sí' if f['completion']['technical_complete'] else 'No'} | Liberada |")
    if label!='negative':commits.append(f"| {title} | {phase} | {audit} |")
(R/'docs/implementation/e7-ef7897d.md').write_text(f'''# E7 — reevaluación de ef7897d y recuperación de F-03

Fecha: 2026-10-16. **Resultado: APROBADA para los escenarios E7 ejercitados en este host.** F-03 quedó corregido; el run anterior se recuperó mediante el controlador. Los proyectos nuevo y migrado cerraron con revisión y auditoría. El escenario negativo ejecutó tres fallos reales controlados y pudo abandonarse sin aceptar código fallido ni reiniciar su presupuesto.

## Candidato y autoridad

- Commit evaluado: `{c['evaluated_commit']}`. Exportación inmutable; archivo SHA-256 `{c['source_archive_sha256']}`. Los 115 archivos del paquete se contrastaron con Git y la exportación.
- Pedido: corregir F-03 conservando controles, recuperar el run bloqueado por el controlador y repetir E7 con proyectos desechables y evidencia. La declaración literal está en [source-and-scope.json](evidence/e7-ef7897d/source-and-scope.json).
- Versión 2.0.0 conservada. Sin E8, instalación, integración, push, tag, publicación ni despliegue. Se retuvieron las ramas de evaluación.
- Orquestador Sol/high real `01a1451c-0ecd-7c93-9d51-8650fdaf887f`, propietario original del run bloqueado. Nueve sesiones distintas atestadas independientemente para E7: propietario, una prueba de capacidades Luna/high, cinco intentos Luna/high y dos revisores Sol/high independientes. La prueba de capacidades no acredita implementación.
- Aprobaciones sintéticas del evaluador exclusivamente para fixtures. No se atribuyen al usuario aprobaciones de un producto real. Cada implementación se ejecutó en un worktree enlazado, con propiedad común y un solo implementador activo.

## F-03: corrección y recuperación

El tercer fallo dejaba una tarea activa: retry rechazaba por límite, abandon exigía conciliación y resume mantenía verification_failed, incompatible con reconcile. El cambio acotado permite el abandono explícito de esa tarea **solo con verificación fallida y presupuesto agotado**, autorización válida, propietario/propiedad comprobados y atestación del hijo exacto como terminal. El evento abandoned registra unresolved_task y la atestación antes de liberar propiedad; retira la reserva activa sin cambiar la tarea fallida ni sus intentos. Otras tareas activas mantienen sus requisitos de reconciliación.

Se observaron cuatro regresiones RED antes del cambio. Después pasaron **127 pruebas del plugin + 9 del hook**, también desde la exportación exacta evaluada; revisión independiente sin bloqueos en el alcance corregido. Se comprobó rechazo con hijo vivo/inaccesible, autorización vacía, propietario o propiedad inválidos; conservación de código/historia, presupuesto entre runs e idempotencia ante caída después del evento. [Corrección y regresiones](evidence/f03-fix/README.md), [revisión independiente](evidence/f03-fix/independent-review.json).

El propietario original ejecutó el nuevo CLI sobre el run anterior `ca3bad74-90c2-4d4d-8d6c-3f08b3d0180e`. Quedó abandoned, active_task=null, T-001=verification_failed con intento3, sin propiedad activa. Los 17 eventos anteriores permanecen como prefijo byte por byte; el evento18 es el abandono autorizado con la atestación terminal. Código, pruebas, siete decisiones, recibos, paquetes y todo el estado de tareas permanecen idénticos. No se editó estado ni se borró propiedad manualmente. Esta recuperación no acredita implementación exitosa.

[Verificación independiente de recuperación](evidence/e7-ef7897d/recovery/independent-check.json), [operaciones reales](evidence/e7-ef7897d/recovery/operations.jsonl) y [snapshot/bundle](evidence/e7-ef7897d/recovery/preservation.json). El [hallazgo original F-03](evidence/e7-34d8909/native/F-03-recovery-after-retry-limit.md) y el [resultado anterior no aprobado](e7-34d8909.md) se conservan como historia del candidato anterior.

## Nuevas ejecuciones nativas

Los tres proyectos son nuevos y desechables. Antes de aprobar/iniciar se comprobaron 21 documentos: todas las secciones y tablas actuales, contratos/pins válidos, tree anotado y verificable en structure. Infraestructura N/A justificada para una función local; la aplicabilidad mantiene flexibles las dependencias de diseño. Solo release.py era editable y test_release.py se mantuvo fijo, SHA-256 `7bb24f05e31ffe3fdb53c96895e3462a5823fe7ac9ad4bdbe0e612d206cd0577`.

| Proyecto | Run | Intentos | Estado del run | Estado de la tarea | Finalización técnica | Propiedad |
| --- | --- | --- | --- | --- | --- | --- |
'''+ '\n'.join(rows)+'''

| Proyecto | Commit de fase revisada | Checkpoint de auditoría, hijo directo |
| --- | --- | --- |
'''+ '\n'.join(commits)+'''

En el proyecto nuevo, Luna fue interrumpido tras escribir el código. Se inspeccionaron sus archivos y su estado terminal, se restauró el paquete perdido con bytes/digest idénticos y se concilió el resultado sin repetir implementación ni gastar otro intento. Las cuatro pruebas pasaron en el controlador. Un Sol distinto revisó el árbol exacto de fase antes del commit. [Interrupción](evidence/e7-ef7897d/native/fresh/interruption-recovery-check.json), [paquete](evidence/e7-ef7897d/fresh-packet-independent-check.json).

En el migrado, preview y apply explícitos conservaron los tres originales y su correspondencia con Git; se importaron cero aprobaciones y cero evidencias desde etiquetas/casillas. Se emitieron siete recibos nuevos. Luna implementó la función; cuatro pruebas pasaron y un Sol distinto revisó la fase. [Comprobación independiente de migración](evidence/e7-ef7897d/migration-independent-check.json).

Ambos positivos completaron convergencia semántica, primer review-release desde los bloques iniciales (regresión nativa de F-01), auditoría única y finishing con rama conservada y limpia. complete devuelve technical_complete=true, release_review_pending=false, audit_pending=false. La entrega queda branch_retained y el impacto pendiente; ninguna de esas evidencias acredita publicación o despliegue.

## Negativo: presupuesto y recuperación sin aceptación indebida

Tres hijos Luna/high reales produjeron implementaciones deliberadamente insuficientes, con tres verificaciones fallidas del controlador sobre la suite fija. Son fallos inyectados para evaluar controles, no una evaluación de calidad de modelos. review(pass), close y phase-ready fueron rechazados; retry devolvió retry_limit y prepare4 fue rechazado sin lanzar otro hijo.

Después, abandon autorizado atestó el tercer hijo terminal, registró el fallo no resuelto y liberó la propiedad. Conservó intento3 y verification_failed, sin fase aprobada, commit de implementación ni release-review. complete sigue technical_complete=false. La verificación independiente volvió a ejecutar la suite: falla como debe, conservando los bytes del código y de la prueba. Así se verifica la salida de F-03 sin maquillar el fallo ni resetear intentos.

[Operaciones del negativo](evidence/e7-ef7897d/native/negative/operations.jsonl), [resumen nativo](evidence/e7-ef7897d/native/native-result-summary.json) y [atestaciones y comprobaciones independientes](evidence/e7-ef7897d/native-independent-check.json). El límite entre runs también tiene regresión determinista: después del abandono, un nuevo run no obtiene un cuarto intento.

## Comprobaciones complementarias

| Comprobación | Resultado y evidencia |
| --- | --- |
| Suite del candidato exportado | [127 pruebas PASS](evidence/e7-ef7897d/deterministic-tests.txt) y [9 hooks PASS](evidence/e7-ef7897d/hook-tests.txt) |
| Controles conservados | [14 HARD-GATE idénticos; solo _abandon y el reducer cambiaron en Engine; verificación, límites, aprobaciones, perfiles, fases y hook preservados](evidence/e7-ef7897d/control-invariants-independent-check.json) |
| Formato y paquete | [115 archivos, 14 skills, 14 templates, manifiestos idénticos 2.0.0](evidence/e7-ef7897d/package-checks.json) |
| Consulta estricta | [12 consultas reales sin alterar bytes/modos/fechas; tres gates no soportados rechazados](evidence/e7-ef7897d/consultation-tests.json) |
| Prerrequisitos nativos | [Perfil incorrecto y capacidad ausente rechazados](evidence/e7-ef7897d/native-prerequisite-negative-probes.json) |
| Bases de los fixtures | [Secciones, tablas, tree y contratos antes de aprobar](evidence/e7-ef7897d/fixture-shape-independent-check.json) |
| Vigencia posterior al cierre | [Dos clones independientes: cambiar código o especificación invalida complete; original cerrado conservado](evidence/e7-ef7897d/completion-staleness-negative-probes.json) |

Las pruebas deterministas y las consultas complementan la evidencia nativa, sin sustituirla. complete se prueba separadamente de las consultas estrictas porque puede refrescar metadatos Git. El alcance se limita a estos escenarios en este host/candidato; no se evaluó exhaustivamente cada comportamiento de las 14 skills ni se repitió E8. Esta aprobación E7 no declara una nueva versión lista para publicación.

## Preservación y procedencia

Cuatro repositorios preservados: el negativo recuperado y tres escenarios nuevos. Cuatro bundles Git verificados, snapshots con hashes y operaciones CLI; las cuatro propiedades están liberadas. Los archivos temporales se conservan, junto con copias portables que permiten inspeccionar el estado aunque desaparezcan los originales. No se copiaron logs privados completos del host; las atestaciones registran referencias y hashes compactos.

[Índice de evidencia](evidence/e7-ef7897d/README.md), [preservación nueva](evidence/e7-ef7897d/preservation-summary.json), [integridad final](evidence/e7-ef7897d/final-artifact-validation.json) y [SHA256SUMS](evidence/e7-ef7897d/SHA256SUMS). Los scripts de reproducción necesitan las sesiones/host originales para repetir atestaciones; restaurar snapshots o bundles no restablece autorización ni identidad nativa.
''')
(E/'README.md').write_text('''# Evidencia E7 — ef7897d

**APROBADA en los escenarios nativos ejercitados.** F-03 corregido; run anterior recuperado mediante el controlador, dos positivos cerrados y negativo abandonado preservando sus tres fallos. Cuatro propiedades liberadas. Sin E8 ni publicación.

- [Informe completo](../../e7-ef7897d.md).
- [Hallazgo original F-03](../e7-34d8909/native/F-03-recovery-after-retry-limit.md); [corrección y regresiones](../f03-fix/README.md).
- source-and-scope.json: candidato, autorización literal e inventario de la exportación.
- recovery/: operaciones del run anterior, comparaciones independientes y copia portable.
- native/: operaciones de cada fixture, atestaciones, interrupción/restauración, convergencia, cierres y copias portables.
- native-independent-check.json: nueve sesiones reales, árboles/commits/auditorías, estado final y pruebas independientes.
- control-invariants-independent-check.json: controles conservados y métodos afectados.
- deterministic-tests.*, hook-tests.*: 127 + 9 pruebas desde el candidato exportado.
- reproduction/: preparación y comprobaciones; no repetir scripts que crean fixtures sobre destinos existentes.
- preservation-summary.json y recovery/preservation.json: tres repositorios nuevos y uno recuperado.
- final-artifact-validation.json y SHA256SUMS: integridad y hashes de todos los archivos, salvo el propio SHA256SUMS.

Los snapshots y bundles son evidencia histórica. No restauran autorización, propiedad o identidad nativa. Las atestaciones conservan referencias/hashes del host, sin copiar logs privados completos.
''')
print('Report and evidence index written from independently verified native results')
