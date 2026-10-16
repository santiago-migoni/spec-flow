# Publicación — Spec-Flow v3.0.0

**Publicada y verificada:** [https://github.com/santiago-migoni/spec-flow/releases/tag/v3.0.0](https://github.com/santiago-migoni/spec-flow/releases/tag/v3.0.0). Fecha real GitHub: `2026-10-16T16:38:45Z`. Release estable, no draft ni prerelease, marcada Latest.

El usuario autorizó push, tag y release, conservando E7/E8 y excluyendo actualización de su instalación y migración de proyectos. [Autorización y preflight](evidence/publication-v3.0.0/preflight.json).

| Elemento | Resultado verificado |
| --- | --- |
| Repositorio | santiago-migoni/spec-flow |
| Commit de release | 1c92505584f789b2e20b4e10538678aa2275dfa2 |
| Tag anotado | v3.0.0 |
| Objeto de tag | d8ee41697512e96121cd90f6c493724356627a80 |
| Main al publicar | 1c92505584f789b2e20b4e10538678aa2275dfa2 |
| Release | [415169925](https://github.com/santiago-migoni/spec-flow/releases/tag/v3.0.0) |
| Artefacto | spec-flow-v3.0.0.tar.gz y SHA256SUMS |
| SHA-256 del paquete descargado | e91768238461a8159fb0588364636c7925771da666d487c5d0e54f6857d01ecc |
| Archivos descargados cotejados | 115, idénticos al paquete de d19d6e0 |

Se verificó avance fast-forward desde el main remoto anterior y se enviaron main y tag en una operación atómica, sin force ni reescritura. La release se creó sobre el tag remoto verificado, con notas que fijan los enlaces de evidencia al commit de release. Se descargaron ambos assets desde GitHub y se comprobaron hash, tamaños, contenido del checksum y los 115 archivos del paquete. Los digests informados por GitHub también coincidieron cuando estaban presentes.

## Trazabilidad conservada

- [E7 nativa](e7-ef7897d.md): ef7897d83dedf9fe20c8bf82fb9e311f4cff8107, escenarios documentados y correcciones F-01/F-02/F-03.
- [E8 previa](e8-ef7897d.md): mismo candidato funcional, manifiestos 2.0.0, sin reinterpretar su alcance.
- [Corte local](release-v3.0.0.md): d19d6e0be75702907442412f9227688cbc835fba, solo version de ambos manifiestos frente a la base funcional.
- [Instalación final v3.0.0](e8-d19d6e0.md): d19d6e0, 14 skills, 127 tests del plugin y 9 del hook desde el cache instalado; smoke y protección de instalación/configuración.

El commit de release conserva esos informes y sus archivos de evidencia originales íntegros. Los 115 archivos del paquete son byte-idénticos a d19d6e0, por lo que esta publicación reutiliza las verificaciones ya registradas sin atribuirles una ejecución nueva. Los cambios de publicación son documentación/metadatos externos al paquete. El comprobante posterior se registra en un commit documental adicional en main; el tag conserva permanentemente el commit de release indicado arriba.

## Instalación y proyectos

Se volvieron a comprobar los 114 archivos de la instalación estable existente, con bytes, permisos y mtime idénticos; setting del plugin, configuración completa y confianza de hooks sin cambios. No se ejecutaron operaciones de instalación/actualización, inicialización ni migración de proyectos en esta publicación. La disponibilidad de v3.0.0 en el marketplace no implica haberla instalado en la copia del usuario.

## Evidencias y límites

[Comprobante estructurado](evidence/publication-v3.0.0/publication-receipt.json), [operaciones](evidence/publication-v3.0.0/operations.jsonl), [destino](evidence/publication-v3.0.0/publication-target.json) e [inventario de integridad](evidence/publication-v3.0.0/SHA256SUMS).

Las pruebas conservan los límites de sus informes: host/escenarios observados, sin promesas de ahorro, refresco automático de chats ni interceptación universal/confiable del hook. Publicación, instalación del usuario y migración permanecen como hechos separados.
