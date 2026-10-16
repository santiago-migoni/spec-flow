# Corte v3.1.0

Publicación autorizada de v3.1.0 con commits separados, comprobación final aislada, tag, push y release de GitHub. No actualizar la instalación del usuario ni migrar proyectos.

Base funcional: `e9fe1461727e7b508143646132e2b9bc9ba5c16c`, con [E7](e7-e9fe146.md) y [E8](e8-e9fe146.md) aprobadas. Sus evidencias completas, incluidos logs y snapshots sintéticos excluidos normalmente por gitignore, quedaron en el commit documental `6ec7f1d`. Se verificaron desde Git contra sus checksums.

El corte cambia únicamente el campo version de ambos manifiestos dentro del paquete, de 3.0.1 a 3.1.0; actualiza AGENTS, changelog y notas fuera del paquete. [Correspondencia exacta](evidence/release-v3.1.0/verification.json). No se reinterpreta la evaluación de e9fe146 como una evaluación de código nuevo.

La publicación queda condicionada a la [comprobación instalada final](e8-v3.1.0.md) del commit de corte, con identidad temporal distinta, suites 152 + 10, descubrimiento fresco y conservación de instalación/configuración del usuario. Tag y release apuntarán al commit exacto verificado; la evidencia y el comprobante se agregan en commits documentales posteriores sin alterar su paquete.
