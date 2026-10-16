# E7 — e9fe146: plan y límites

Candidato inmutable: `e9fe1461727e7b508143646132e2b9bc9ba5c16c`, paquete 3.0.1. Autorización: ejecutar E7 con proyectos desechables y perfiles configurados; sin publicación ni actualización de instalación.

| Categoría | Prueba prevista | Evidencia exigida |
| --- | --- | --- |
| Native Codex | Proyecto nuevo YAML; interrupción y reanudación; reconstrucción de packet; cierre idempotente y revisión independiente | Sesiones y perfiles reales, comandos del controlador, diferencias, pruebas, eventos, commits y auditoría |
| Native Codex | Proyecto legacy JSON; migración explícita y nueva implementación | Originales conservados, sin importar aprobación/checkmarks, nuevas decisiones y evidencia nativa |
| Native Codex | Tres implementaciones con fallos deliberados y rechazo del cuarto intento | Fallos observados, presupuesto conservado, abandono autorizado por controlador y agentes terminales |
| Determinista | Suite completa del controlador y hooks | Comandos, salidas completas, códigos de salida y duración |
| Complementaria | Consulta estricta, templates literales, invariantes y fuentes | Hashes, tiempos/modos antes/después, validación y consultas de producción |

Los fixtures contienen decisiones y aprobaciones sintéticas limitadas a una función de normalización SemVer. No son decisiones de proyectos reales. Los fallos negativos se inyectan deliberadamente: no evalúan la calidad comparativa de modelos. Las pruebas unitarias de identidad usan fixtures declarados; no sustituyen la atestación de sesiones nativas. E8, distribución instalada, confianza real en el hook, métricas de costo y rendimiento comparativo quedan fuera de esta evaluación.

Perfiles exigidos: orquestador `gpt-6.1-sol/low`, implementador `gpt-6-luna/high`, revisor distinto `gpt-6.1-sol/medium`. La evaluación no cambia perfiles para eludir controles. Una falla del candidato se registra sin corregir código durante E7. Infraestructura N/A justificada; los demás documentos y dependencias se conservan. El cierre técnico conserva impacto pendiente y no autoriza integración, publicación ni despliegue.
