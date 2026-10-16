# Spec-Flow v3.0.1 — corrección del logo

Corrección autorizada: declarar el icono existente como `logo` además de `composerIcon`, preparar v3.0.1 y realizar commit, tag, push y release. No se actualiza la instalación del usuario ni se migran proyectos.

## Cambio y validación

- Ambos manifiestos conservan identidad y opciones; agregan `extensions.com.openai.interface.logo` apuntando al PNG existente. Versión final 3.0.1.
- Prueba de paquete adicional: manifiestos idénticos, campos `logo` y `composerIcon`, rutas contenidas, archivos incluidos y límite de tamaño.
- Suite local: 128 pruebas del plugin y 9 del hook aprobadas. La primera invocación desde la raíz no resolvió el módulo `harness`; se corrigió el directorio de ejecución, sin cambios al código por ese error.
- Instalación nueva en `CODEX_HOME` desechable con marketplace `spec-flow-v301-isolated` y plugin `spec-flow-v301-check`; solo name y displayName difieren en la copia de prueba. El paquete instalado coincide con la copia íntegra.
- Desde ese cache instalado: 128 pruebas del plugin y 9 del hook aprobadas; manifiestos 3.0.1 iguales, logo presente, PNG cuadrado 1254 × 1254 y bytes originales conservados. Identidad temporal retirada.
- Configuración y cache estable del usuario cotejados antes/después, sin cambios. No se otorgó confianza a hooks.

[Evidencia estructurada](evidence/release-v3.0.1/verification.json), [operaciones](evidence/release-v3.0.1/operations.jsonl), [suite instalada](evidence/release-v3.0.1/installed-tests.txt), [hook instalado](evidence/release-v3.0.1/installed-hooks.txt).

## Trazabilidad y límites

El commit de corrección se separa del corte de versión. Controller, hook, perfiles, gates, skills y templates no cambian. [E7 ef7897d](e7-ef7897d.md), [E8 ef7897d](e8-ef7897d.md), [E8 d19d6e0](e8-d19d6e0.md) y [publicación v3.0.0](publication-v3.0.0.md) mantienen sus commits y alcances originales. No se afirma haber repetido E7 para esta corrección de presentación.

Se verificó la instalación del paquete y la declaración del logo, sin demostrar un refresco visual del catálogo en una sesión abierta. La captura anterior también mostraba el nombre interno y el botón Agregar; por tanto, la falta de `logo` explica la omisión declarativa confirmada, pero no permite atribuir todos los detalles visuales al mismo motivo. La publicación no equivale a actualizar la copia del usuario.
