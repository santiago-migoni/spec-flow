# Preparación local — Spec-Flow v3.0.0

Actualización posterior, 2026-10-16: la [instalación aislada final de v3.0.0 sobre d19d6e0](e8-d19d6e0.md) quedó aprobada, con identidad separada y conservación exacta de la instalación estable/configuración. Este pendiente está resuelto; push, tag y publicación siguen pendientes. El registro siguiente conserva el alcance histórico del corte de metadatos previo a esa comprobación.


Fecha de preparación: 2026-10-16. Estado: **corte local preparado y verificado; publicación pendiente**. Autorización: actualizar ambos manifiestos, changelog y notas de release conservando E7/E8, sin push, tag ni publicación.

## Alcance del corte

- Ambos manifiestos equivalentes pasan de 2.0.0 a 3.0.0; no se cambia la identidad spec-flow ni la configuración OpenAI.
- CHANGELOG conserva Unreleased y agrega Release v3.0.0, con cambios incompatibles, mejoras, F-01/F-02/F-03 y validación. La fecha de publicación queda pendiente; la historia desde v2.0.0 permanece idéntica.
- [Notas de release y actualización](../releases/v3.0.0.md): reemplazo de architecture/infrastructure/structure por design, conservación de los tres documentos/contratos/aprobaciones y límites de evaluación.
- README y la guía AGENTS distinguen la versión preparada de su publicación. El marketplace estable conserva main.

El commit de preparación anterior es `238de52c923a271d584213bf122569b7ecdaf505`; las funcionalidades ya estaban implementadas en commits anteriores. Este corte se registra en un commit separado de los cambios funcionales.

## Trazabilidad de evaluación

| Elemento | Fuente y alcance |
| --- | --- |
| Base funcional | ef7897d83dedf9fe20c8bf82fb9e311f4cff8107 |
| E7 | [Informe](e7-ef7897d.md), registrado en 44b2685df26f094bfe29857b11fa59343a83f499; ejecución nativa aprobada en los escenarios documentados. |
| E8 | [Informe](e8-ef7897d.md), registrado en 238de52c923a271d584213bf122569b7ecdaf505; instalación aislada/cliente nuevo/arranque instalado aprobados en el alcance documentado. |
| Diferencia del paquete | 115 archivos: 113 idénticos a ef7897d, solo version cambia en los dos manifiestos. |
| Preservación | Informes, archivos de evidencia y sus SHA256SUMS originales comprobados íntegros y sin modificaciones. |

E7/E8 evaluaron ef7897d con manifiestos 2.0.0. Este corte conserva esos hechos y demuestra igualdad de su contenido funcional; no los renombra como ejecuciones del paquete v3.0.0. No se repitió E7 nativa ni se instaló v3.0.0. Una comprobación final de instalación aislada con la nueva versión queda pendiente antes de publicar.

## Verificación del corte local

| Comprobación | Resultado |
| --- | --- |
| Comparación exacta con candidato | PASS: 113 recursos idénticos, solo campo version de dos manifiestos distinto. |
| Manifiestos y marketplace | PASS: ambos 3.0.0 y equivalentes; marketplace main sin cambios. |
| Suite en copia congelada v3.0.0, ruta con espacios | 127 pruebas del plugin PASS. |
| Hook desde esa copia | 9 pruebas PASS; no demuestra activación confiable/interceptación en vivo. |
| Paquete tras suites | Sin cambios, 115 hashes conservados. |
| Artefacto local | spec-flow-v3.0.0.tar.gz: una raíz de plugin, 115 archivos idénticos a la copia verificada. |
| Referencias Git protegidas | Tags y referencias remotas sin cambios; v3.0.0 no creado como tag. |

[Comparación y autorización](evidence/release-v3.0.0/package-comparison.json), [suite](evidence/release-v3.0.0/runtime.json), [hook](evidence/release-v3.0.0/hooks.json), [artefacto y hash](evidence/release-v3.0.0/archive.json) e [integridad final](evidence/release-v3.0.0/final-check.json).

## Pendiente de publicación

El repositorio contiene un corte local reviewable. Antes de una publicación autorizada: confirmar la instalación final de v3.0.0 con identidad separada, fijar el commit verificado y la fecha/estado de publicación aplicables, y publicar por el flujo autorizado. Si cambia contenido funcional, reevaluar lo afectado antes de reutilizar la evidencia. Push, tag y release permanecen pendientes; instalación de usuario y migración de proyectos son hitos separados.
