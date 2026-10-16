# Evidencias E7 — f8fa91d

Resultado: **E7 no aprobada, bloqueada por HIGH F-02 antes de delegar una implementación**. F-01 está corregida en el candidato y validada por regresiones; su cierre nativo integral no se alcanzó. Ver el [informe](../../e7-f8fa91d.md).

| Material | Contenido |
| --- | --- |
| `source-and-scope.json`, `package-checks.json` | Commit, exportación exacta, archivos/hashes y autorización literal |
| `evaluation-plan.md` | Objetivos previos, separados de resultados observados |
| `deterministic-tests.{txt,json}`, `hook-tests.{txt,json}` | Salidas completas, argv, tiempos y exit: 120 + 9 |
| `F-01-literal-template-check.json` | Ambos bloques iniciales válidos aceptados como ausencia de cierre |
| `owner-preflight-independent.json` | Sesión Sol/high y linaje contrastados por el padre |
| `consultation-tests.json` | 12 consultas reales, tres gate kinds inválidos y snapshots de archivos/metadatos |
| `native-prerequisite-negative-probes.json` | Rechazos de perfil y capacidad |
| `host-inventory-recovery.json` | Estado pending_init histórico, cleanup sin trabajo nuevo y slots liberados |
| `native/*/operations.jsonl` | Operaciones reales con entradas, salidas, exits y traceback de F-02 |
| `native/*/baseline.json` | Tests sobre stubs, sin implementación nueva |
| `native/legacy/` | Originales, preview/revisión/migración y corrección explícita de referencia inexacta de capability |
| `native/native-result-summary.json` | Resumen del propietario, no una aprobación |
| `native-independent-check.json` | Perfil terminal, cero hijos propios, baselines intactos, leases activos y F-02 reproducido sin mutación |
| `native/*/repository.bundle` | Historia/refs de repos desechables, bundles verificados |
| `native/*/snapshot/` | Fuentes y registro final, incluidos archivos sin commit e ignorados |
| `native/*/ownership-registration.json` | Copia histórica del lease, fuera del snapshot ejecutable; no restaurar como autoridad |
| `native/*/preservation.json`, `preservation-summary.json` | Hashes e inventario de conservación |
| `reproduction/`, `native/*.py` | Comprobaciones independientes y helpers realmente usados, con sus rutas originales |
| `patch-whitespace-check.json` | Avisos de espacios solo en logs verbatim de tests fallidos de la corrección |
| `SHA256SUMS` | Hashes de todos los archivos de este directorio salvo el propio manifiesto |

Los bundles retienen commits; los snapshots retienen decisiones/recibos y eventos que aún no se habían comprometido. Son material de inspección offline. Los registros tienen rutas/sesiones históricas y requieren recuperación soportada; copiar el snapshot no crea autoridad ni worktree enlazado. Los leases originales siguen activos porque la conciliación está bloqueada; no se borraron manualmente. No se copiaron logs privados completos del host.

La evidencia de red/green, suite y revisión del parche F-01 está en [f01-fix](../f01-fix/README.md), fijada en el commit del candidato. Esta carpeta registra la nueva evaluación y mantiene sus resultados separados de esa prueba determinista y de la E7 anterior.
