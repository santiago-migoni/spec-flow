# Diseño del harness de Spec-Flow y orquestación entre GPT Sol y GPT Luna

| Campo | Valor |
| --- | --- |
| Fecha | 2026-10-14 |
| Revisión documental | R00 |
| Estado conceptual | Aprobado por el usuario en la conversación de origen |
| Estado de esta transcripción | Primera presentación escrita del diseño aprobado |
| Implementación | Pendiente; no autorizada por este documento |
| Plataforma | Exclusivamente Codex, como parte del plugin Spec-Flow |

## Propósito y aprobación

Spec-Flow evolucionará hacia un sistema de dirección, planificación y ejecución que avance de lo general a lo específico. La estrategia establece propósito, decisiones compartidas y prioridades; la operación convierte cada release en comportamiento, solución técnica, tareas y pasos verificables.

El usuario aprobó el diseño presentado en esta conversación con la declaración: «Perfecto. Aprobado. Crea un documento con toda esta información.» La aprobación comprende el diseño conceptual y su documentación. Este archivo conserva esa decisión sin atribuir aprobación previa a bytes todavía no presentados. No constituye una especificación de release ni un plan de implementación, y no autoriza implementación, instalación, publicación o despliegue. No se asigna una versión de producto.

Los nombres de componentes internos son orientativos. Los límites de reintentos, granularidad de revisión y mecanismos concretos de integración con Codex son decisiones de diseño sujetas a validación técnica y evaluaciones.

## Responsabilidades generales

- El usuario aprueba dirección, alcance y cambios de decisiones.
- GPT Sol transforma la dirección en trabajo ejecutable, orquesta y revisa.
- GPT Luna implementa tareas acotadas y aporta evidencia.
- El harness comprueba prerrequisitos, registra estados y controla las transiciones.

Los documentos son la fuente de intención. El harness es el mecanismo para ejecutar y comprobar esa intención sin depender únicamente de la memoria conversacional del modelo.

## Estructura del proyecto consumidor

```text
proyecto/
├── .specs/
│   ├── constitution.md
│   ├── architecture.md
│   ├── structure.md
│   ├── infrastructure.md
│   ├── roadmap.md
│   ├── backlog.md                       # Opcional
│   └── release-vX.Y.Z/
│       ├── spec.md
│       ├── plan.md
│       └── tasks.md
└── .spec-flow/
    ├── config.json                      # Política del proyecto
    ├── approvals.jsonl                  # Registro de aprobaciones
    └── runs/
        └── <run-id>/
            ├── events.jsonl             # Historial de ejecución
            ├── state.json               # Estado reconstruible
            ├── packets/                 # Contexto generado para agentes
            └── evidence/                # Resultados y revisiones
```

`.specs/` define qué se quiere construir, por qué y bajo qué decisiones. `.spec-flow/` registra qué se autorizó ejecutar, qué ocurrió y con qué evidencia.

Los paquetes de contexto y `state.json` son derivados y regenerables. Los registros de aprobación y ejecución son persistentes. Los logs voluminosos se guardan localmente bajo una política de retención; la evidencia necesaria para acreditar una entrega mantiene referencias duraderas. La política concreta de versionado y retención debe definirse antes de implementar; persistencia no implica incorporar indiscriminadamente todos los logs a Git.

No habrá dos listas de progreso editables. `tasks.md` define el trabajo; los eventos registran su ejecución. Sus casillas son una vista sincronizada por el harness. Una casilla marcada manualmente no acredita por sí sola una tarea.

## De lo general a lo específico

```text
ESTRATEGIA
Propósito y objetivos → Decisiones del sistema → Prioridades y releases

OPERACIÓN
Release → Historias y aceptación → Solución técnica y fases
        → Tareas → Pasos verificables → Implementación y evidencia
```

| Documento | Contenido canónico |
| --- | --- |
| `constitution.md` | Propósito, usuarios, objetivos, principios y límites. |
| `architecture.md` | Componentes, responsabilidades, contratos y decisiones compartidas. |
| `structure.md` | Organización del código y convenciones de ubicación. |
| `infrastructure.md` | Entornos, recursos, despliegue, observabilidad y recuperación. |
| `roadmap.md` | Resultados esperados, prioridades, secuencia y agrupación de releases. |
| `spec.md` | Comportamiento y aceptación de una release. |
| `plan.md` | Solución técnica, fases, entregables y dependencias. |
| `tasks.md` | Acciones ejecutables, pasos, verificaciones y condiciones de cierre. |

Cada decisión tiene una fuente canónica. El roadmap selecciona entregas; la spec detalla su comportamiento. El plan no repite las instrucciones detalladas de `tasks.md`. Los documentos operativos referencian las decisiones estratégicas mediante identificadores y revisiones exactas.

Arquitectura, estructura e infraestructura se desarrollan hasta el nivel necesario para las releases previstas. No se exige decidir anticipadamente todo el futuro del producto ni llenar documentos con decisiones inventadas.

La unidad organizadora objetivo es la release, que puede contener varias historias o funcionalidades. No se mantienen en paralelo una spec o un plan de Superpowered y otra copia de Spec-Flow. Superpowered aporta referencias metodológicas; Spec-Flow será dueño del flujo integrado.

## Estructura objetivo del plugin

```text
plugins/spec-flow/
├── plugin.json
├── .codex-plugin/
│   └── plugin.json
├── skills/
│   ├── using-spec-flow/
│   ├── constitution/
│   ├── architecture/
│   ├── structure/
│   ├── infrastructure/
│   ├── roadmap/
│   ├── specify/
│   ├── clarify/
│   ├── plan/
│   ├── tasks/
│   ├── analyze/
│   ├── implement/
│   ├── converge/
│   ├── review-release/
│   ├── finishing-branch/
│   └── backlog/
├── harness/
│   ├── contracts/                       # Estados, autoridad y transiciones
│   ├── schemas/                         # Formatos validables
│   ├── roles/                           # Instrucciones de Sol y Luna
│   ├── runtime/                         # Lógica local determinista
│   └── adapters/
│       └── codex/                       # Adaptación al entorno disponible
├── hooks/
├── scripts/
├── tests/
└── evals/
```

Las plantillas permanecen junto a sus skills. No toda operación interna se convierte en una skill pública.

| Componente | Responsabilidad |
| --- | --- |
| Skills | Conducir la interacción y las fases. |
| Runtime | Validar documentos, resolver dependencias y registrar transiciones. |
| Roles | Delimitar lo que recibe y devuelve cada agente. |
| Adaptador de Codex | Identificar capacidades disponibles y preparar la delegación. |
| Hooks | Reforzar controles en las herramientas que puedan interceptar. |
| Evaluaciones | Comprobar el comportamiento del conjunto. |

El plugin utiliza la ejecución nativa de Codex. No incorpora un servicio externo ni un segundo sistema de agentes mediante API. El adaptador no presupone que un script local pueda invocar directamente herramientas de delegación del modelo: el enlace concreto con las capacidades del host queda por validar.

## Roles y modelos

| Actor | Responsabilidades | Límites |
| --- | --- | --- |
| Sol, orquestador | Recuperar contexto, preparar documentos, seleccionar tareas habilitadas, delegar, interpretar resultados y gestionar excepciones. | No aprobar decisiones en nombre del usuario ni ampliar el alcance. |
| Luna, implementador | Inspeccionar el código pertinente, implementar, verificar y devolver resultados. | No cambiar requisitos, aprobar su trabajo ni iniciar otras tareas. |
| Sol, revisor | Revisar el diff y su cumplimiento con las fuentes aprobadas. | No sustituir pruebas por una opinión favorable. |
| Runtime | Validar formatos, dependencias, revisiones, evidencias y estados. | No decidir valor de producto ni interpretar objetivos ambiguos. |
| Usuario | Aprobar decisiones, autorizar ejecución e integración. | No necesita intervenir en cada detalle local ya autorizado. |

Orquestación y revisión son roles distintos aunque usen Sol. Se propone una revisión con contexto independiente al cierre de cada fase, además de la revisión de resultados de cada tarea por el orquestador.

La configuración utiliza perfiles lógicos `orchestrator`, `implementer` y `reviewer`, vinculados a identificadores concretos disponibles. No habrá sustitución silenciosa de Luna por Sol. El esfuerzo de razonamiento y la selección exacta de modelos se fijarán según las capacidades expuestas por la instalación.

Codex documenta delegación a subagentes y configuración de roles. El mecanismo concreto debe adaptarse al host. En la sesión de diseño había herramientas de delegación con selección explícita de modelo; no se ejecutó ni validó el flujo Sol–Luna propuesto.

## Contrato de una tarea

| Campo | Contenido |
| --- | --- |
| Identidad | ID estable, fase e historia o criterio de aceptación relacionado. |
| Objetivo | Resultado concreto que debe producir. |
| Dependencias | Tareas y condiciones necesarias antes de empezar. |
| Alcance | Archivos, símbolos y contratos relevantes. |
| Reutilización | Componentes existentes que debe usar o respetar. |
| Pasos | Acciones ordenadas con IDs estables. |
| Verificación | Comandos o inspecciones, resultado esperado y condición de cierre. |
| Excepciones | Qué puede resolver localmente y qué debe escalar. |

```text
Release vX.Y.Z
└── US-003
    └── Fase PH-02
        └── T-012
            ├── T-012.001
            ├── T-012.002
            └── T-012.003
```

La tarea es la unidad de delegación; el paso, la unidad mínima de evidencia; la fase, la unidad habitual de revisión integral y commit. No se crea un agente ni un commit por cada paso.

El paquete enviado a Luna se genera desde fuentes canónicas, incluye únicamente contexto pertinente y fija su revisión. Si cambia la base, el resultado no se acepta sin evaluar el impacto. El paquete no es una segunda fuente editable de requisitos.

## Ciclo de ejecución

```text
pending → ready → running → verifying → reviewing → completed
                    │           │           │
                    └───────────┴───────────┴──→ needs_changes
                                                    │
                                                    └→ running

Estados adicionales: blocked, interrupted, cancelled
```

1. **Preparar:** comprobar aprobaciones, dependencias, entorno y alcance autorizado.
2. **Reservar:** asignar la tarea a un único ejecutor.
3. **Delegar:** Sol envía a Luna el paquete con contexto y límites.
4. **Implementar:** Luna realiza el trabajo y devuelve diff, comprobaciones y dudas.
5. **Verificar:** ejecutar o contrastar comprobaciones sobre el estado real del código.
6. **Revisar:** Sol evalúa cumplimiento, regresiones y cambios fuera de alcance.
7. **Cerrar:** registrar evidencia y actualizar la vista de progreso.
8. **Continuar:** seleccionar otra tarea solo dentro de la autorización vigente.

Un resultado PASS sin pruebas ejecutadas, una salida vacía o un resultado de otra revisión no permiten cerrar una tarea. Para documentación y skills, la verificación combina controles estructurales y evaluaciones de comportamiento cuando corresponda; no se inventan pruebas de aplicación.

La evidencia debe identificar tarea/paso, intento, fuentes y código probado, comando o inspección, entorno relevante, resultado esperado y observado, y revisión asociada. Un commit por sí solo no identifica cambios locales todavía no incluidos en él.

## Reintentos y escalamiento

La política inicial propuesta permite un intento inicial y hasta dos rondas de corrección por tarea. El límite es configurable y debe validarse mediante evaluaciones.

Cada corrección identifica qué falló, la hipótesis explicativa, el cambio previsto y la comprobación específica que demostrará la corrección. No se repiten ensayos idénticos sin nueva hipótesis o evidencia.

Al agotar el límite, Sol diagnostica y elige entre reformular la tarea dentro del alcance aprobado, registrar un bloqueo o presentar una decisión pendiente. No se convierte automáticamente en implementador.

| Hallazgo | Fuente que debe reconsiderarse |
| --- | --- |
| Implementación que incumple una decisión vigente | Tarea y su corrección. |
| Descomposición o secuencia inadecuada | Plan o tasks, según la decisión afectada. |
| Cambio de comportamiento o aceptación | Spec. |
| Cambio de contrato o arquitectura compartida | Documento técnico correspondiente. |
| Cambio de prioridad o composición de entregas | Roadmap. |
| Cambio de objetivos o límites | Constitución. |

Se detiene el trabajo dependiente de la decisión pendiente. Las partes independientes conservan su aprobación; una revisión nueva no invalida todo automáticamente.

## Recuperación y consistencia

Al retomar una ejecución:

1. Leer el registro persistente.
2. Inspeccionar cambios reales y agentes todavía activos.
3. Identificar intentos incompletos.
4. Revalidar evidencia afectada.
5. Retomar desde el primer paso pendiente.

No se repite una acción solo porque falta su mensaje final. Si un comando pudo producir efectos, primero se reconcilia su resultado.

El controlador es el único escritor del registro central. Las transiciones son atómicas y usan identificadores de intento para evitar cierres duplicados. Los agentes devuelven resultados; no editan directamente el historial central. `state.json` se reconstruye desde los eventos y no compite con ellos como fuente de autoridad.

## Aprobaciones y autorización

El registro identifica documento, revisión o hash de contenido, alcance y evidencia de aprobación humana. El estado visible del Markdown representa esa autoridad; no constituye otra aprobación independiente. Un hash identifica contenido, pero no demuestra que una persona lo aprobó.

```text
Constitución aprobada
    ↓
Diseño compartido aplicable aprobado
    ↓
Roadmap con release seleccionada aprobado
    ↓
Spec aprobada
    ↓
Plan aprobado
    ↓
Tasks aprobadas
    ↓
Ejecución autorizada
```

No se agrega un archivo ni una aprobación de release entre roadmap y spec. El roadmap selecciona la entrega y `spec.md` define su alcance detallado. Cada aprobación se reconoce una vez y se reutiliza mientras su contenido y alcance sigan vigentes.

La autorización puede cubrir una fase o varias. El modo inicial conserva la parada por fase de Spec-Flow. El avance automático entre fases requiere una autorización que abarque ese recorrido. Aprobar tareas y autorizar su ejecución puede ocurrir en la misma declaración explícita, sin una confirmación redundante.

Aprobar trabajo no autoriza automáticamente push, integración, publicación o despliegue. Las decisiones de producto, la ejecución y esas acciones mantienen alcances distinguibles.

## Aislamiento y controles

La primera versión objetivo utiliza un único Luna implementador activo por ejecución, con un entorno de trabajo aislado para la release. La revisión ocurre sobre una revisión estable, sin escrituras simultáneas. La concurrencia entre implementadores queda para una extensión posterior, condicionada a dependencias y aislamiento comprobables.

| Mecanismo | Garantía buscada |
| --- | --- |
| Instrucciones de roles | Comportamiento esperado del agente. |
| Validadores | Rechazar transiciones sin evidencia suficiente. |
| Inspección de diffs | Detectar modificaciones fuera del alcance. |
| Hooks compatibles | Bloquear determinadas operaciones antes de ejecutarlas. |
| Permisos y aislamiento de Codex | Limitar acciones disponibles según el entorno. |

Una lista de archivos permitidos en un prompt no es una barrera de permisos. Debe distinguirse lo prevenido de lo detectado después. El hook actual de Spec-Flow cubre determinados parches y no todas las escrituras; no garantiza por sí solo el ciclo completo. El registro tampoco debe presentarse como una prueba criptográfica de autoridad humana o una frontera de seguridad independiente de los permisos del host.

## Cierre técnico y aprendizaje

`converge` comprueba que implementación, spec, plan y principios coinciden, y propone trabajo residual. `review-release` registra aceptación, entrega, resultados observados, aprendizajes y decisiones pendientes. `finishing-branch` conserva la responsabilidad de integración de la rama.

El cierre narrativo vive en `spec.md`, con referencias a la evidencia técnica. El roadmap refleja el estado de la release sin copiar su historial. No se requiere otro archivo de revisión o release.

Una release puede estar técnicamente convergida y conservar mediciones de impacto pendientes. El aprendizaje propone cambios estratégicos; no los aprueba ni inicia otra implementación automáticamente.

## Evaluación del harness

Los escenarios de aceptación deben cubrir al menos:

- Una tarea no comienza sin autorización o dependencias satisfechas.
- Luna modifica un archivo fuera del alcance y el cambio no se acepta silenciosamente.
- Una revisión relevante invalida la evidencia dependiente.
- Una sesión se interrumpe después de una escritura y se recupera sin repetirla a ciegas.
- Dos intentos de cierre no producen dos transiciones.
- Un fallo repetido alcanza el límite y escala.
- Una tarea descubre un cambio arquitectónico y vuelve al documento correcto.
- El modelo requerido no está disponible y se informa sin sustituirlo.
- Una suite sin casos ejecutados no acredita éxito.
- La finalización técnica no dispara una publicación.

Se medirán aceptación correcta, defectos detectados, retrabajo, intervenciones humanas, tiempo y uso de tokens cuando Codex exponga esos datos. El ahorro económico y la mejora de resultados de Sol + Luna deben demostrarse; no se dan por obtenidos.

## Diferencias respecto del plugin actual

El diseño amplía el flujo centrado en features hacia una organización por releases, incorpora documentos estratégicos y agrega un harness persistente con delegación Sol–Luna. Mantiene como principios las aprobaciones explícitas, los artefactos canónicos, la ejecución por fases y la convergencia.

Antes de implementar deberán resolverse la compatibilidad con artefactos históricos `NNN-feature-name`, el reconocimiento de ramas, la adaptación de hooks y scripts, el formato de metadatos y el registro de aprobaciones existente. Este diseño no ordena una migración automática ni cambia la versión 1.1.0 del plugin.

## Validaciones técnicas pendientes

- Mecanismo nativo disponible en Codex para selección de modelos, delegación y recuperación de agentes.
- Integración del adaptador con ese mecanismo sin crear un runtime externo de agentes.
- Alcance real de permisos, hooks y aislamiento en el entorno objetivo.
- Esquemas y atomicidad de registros, recuperación y sincronización de vistas.
- Política de conservación de evidencia y referencias duraderas.
- Compatibilidad y adopción por proyectos con artefactos previos.
- Evaluaciones para límites de reintento, granularidad de revisión y desempeño Sol–Luna.

Estos puntos concretan la implementación posterior; no autorizan modificar el alcance conceptual aprobado sin presentar el cambio correspondiente.

## Fuentes y referencias

- Conversación de diseño del 2026-10-14 y declaración de aprobación transcrita al inicio.
- [README actual de Spec-Flow](../../README.md).
- [Skill de implementación actual](../../plugins/spec-flow/skills/implement/SKILL.md).
- [Skill de convergencia actual](../../plugins/spec-flow/skills/converge/SKILL.md).
- [Hook actual de aprobación](../../plugins/spec-flow/hooks/check-phase-approval.py).
- [Documentación oficial de subagentes de Codex](https://learn.chatgpt.com/docs/agent-configuration/subagents).

Superpowered fue la referencia metodológica para separar dirección, diseño compartido, prioridades y revisión de resultados. Este documento especifica el objetivo propio de Spec-Flow, no una dependencia de ejecución de Superpowered.
