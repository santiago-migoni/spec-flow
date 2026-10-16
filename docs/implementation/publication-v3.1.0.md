# Publicación de Spec-Flow v3.1.0

**Publicada como estable y Latest** el `2026-10-16T19:06:33Z`: [Spec-Flow v3.1.0](https://github.com/santiago-migoni/spec-flow/releases/tag/v3.1.0).

| Hito | Commit / resultado |
| --- | --- |
| YAML y perfiles configurables | `e9fe1461727e7b508143646132e2b9bc9ba5c16c` |
| E7/E8 y evidencias completas | `6ec7f1d` |
| Corte, tag y paquete publicado | `fad239f6f280bc35c0f7f5b2236ca2abd37d7814` |
| Instalación final y evidencias | `7ea31fe19f6f7a87d77b53e49a54691a946c89fe` |
| Tag anotado | `v3.1.0`, objeto `327d30e40a7085779fde1daf052dfa0c9350e95a` |
| Publicación GitHub | Release `415292012`, estable y Latest |

Main con las evidencias y tag fueron enviados mediante push atómico sin force. Tag permanece en el commit de corte, cuyos 139 archivos fueron instalados y comprobados; el commit documental posterior no cambia el paquete. Este comprobante se registra después de publicar, sin mover el tag.

[Notas](../releases/v3.1.0.md) · [Corte](release-v3.1.0.md) · [E7](e7-e9fe146.md) · [E8 funcional](e8-e9fe146.md) · [Instalación final](e8-v3.1.0.md).

La descarga desde GitHub contiene **139 archivos idénticos** al corte verificado. SHA256 del asset `spec-flow-v3.1.0.tar.gz`: `9dcac10dd94b2ea8baf563b79438893cdb7c269b83813deee41f749602557e9d`. El archivo SHA256SUMS descargado coincide con el generado y los digests de assets informados por GitHub coinciden. [Comprobante estructurado](evidence/publication-v3.1.0/receipt.json), [operaciones](evidence/publication-v3.1.0/operations.jsonl), [destino y hashes de archivos](evidence/publication-v3.1.0/target.json), [notas efectivas](evidence/publication-v3.1.0/github-release-notes.md) y [SHA256SUMS](evidence/publication-v3.1.0/SHA256SUMS).

E7 nativa y E8 sobre e9fe146 conservan sus alcances y observaciones. El corte cambia solamente version en dos manifiestos; instalación final 3.1.0 aprobó 152 pruebas del controlador y 10 de hooks, 14 skills, ocho templates YAML y 75 referencias. No se atribuye una nueva ejecución nativa a la modificación de versión ni se reescriben evaluaciones históricas.

Se cotejaron nuevamente configuración y cache estable tras publicar: bytes, permisos y mtime de 115 archivos estables conservados; configuración byte-idéntica, confianza de hooks intacta. No se actualizó la instalación ni se migraron proyectos del usuario. Los marketplaces temporales fueron retirados. Publicación no demuestra refresco visual de chats abiertos ni ahorro de tokens/costo.

El script de publicación preservado es histórico y realiza operaciones externas; no debe repetirse sobre destinos ya completados. Los siguientes cambios requieren su propia autorización.
