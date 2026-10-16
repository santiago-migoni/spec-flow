---
schema_version: 1
kind: plan
revision: R00
id: PLAN-X.Y.Z
depends_on:
- path: .specs/release-vX.Y.Z/spec.md
  digest: '0000000000000000000000000000000000000000000000000000000000000000'
phases:
- id: PH-01
  description: '[Phase goal and deliverable.]'
  depends_on: []
- id: PH-02
  description: '[Related increment and integration deliverable.]'
  depends_on:
  - PH-01
---

# Release Plan: vX.Y.Z

Replace the illustrative phases, table rows, references, and paths with this release's actual approved decisions. They prescribe neither phase count nor implementation scope. The phases array owns IDs, descriptions, and dependencies; keep its reading table synchronized. All decision tables stay outside generated progress and participate in the document digest.

## Purpose, scope, and approved bases

[Identify the release, approved spec, and implementation objective. Reference applicable constitution, architecture, infrastructure, and structure decisions; pin only approved sources actually used. Define this plan's boundaries without redefining spec behavior.]

## Technical approach and implementation decisions

[Explain the release-specific solution and significant decisions: context, alternatives, choice, rationale, and consequences. Reference shared design instead of copying it. Distinguish verified facts, assumptions, and proposed decisions. Route changes to shared decisions to their owning document before relying on them.]

## Phases, deliverables, and dependencies

This table is a reading view of phases, with story/criterion links as additional planning context. Include every phase exactly once in the same order; copy descriptions and dependency IDs exactly. Use None for an empty depends_on array; otherwise preserve its ID order. Never maintain a second independent phase sequence.

| Phase | Goal and deliverable | Dependencies | Related stories | Related criteria |
| --- | --- | --- | --- | --- |
| PH-01 | [Phase goal and deliverable.] | None | US-001 | AC-001, AC-002, AC-003 |
| PH-02 | [Related increment and integration deliverable.] | PH-01 | US-002 | AC-004 |

[Organize phases around verifiable increments. Justify technical enabling phases and explain what they unlock. A story/criterion may span phases; identify partial contributions versus final verification in the coverage table below. Each AC must retain its actual story owner from spec; phase membership does not change ownership. Explain dependency and ordering rationale without redefining canonical dependencies.]

Phase tables provide planning context, including future phases. Only the active task/phase scope and current execution authorization permit work; a visible row does not authorize executing it.

## Components, files, and change scope

| Component or path | Intended change | Phase | Restrictions or dependencies |
| --- | --- | --- | --- |
| [Component reference or relative/path] | [Create, modify, or other intervention] | PH-01 | [Relevant conditions] |

[Explain where changes are expected and their relationship to approved structure. Distinguish existing from proposed locations. Tasks will contain the executable per-task file list; this planning table does not authorize writes.]

## Capacity, resources, and forecasts

[Record availability, tools, environments, access, and constraints affecting feasibility. Estimates must state their basis, assumptions, and uncertainty; distinguish forecasts from approved commitments. Do not assume logically independent work can execute concurrently. Respect the current execution model, including one active implementer and independent phase review/commit requirements; reference the execution contract for detail. Leave missing capacity evidence explicit.]

## Risks, assumptions, and validation

| Risk or assumption | Consequence | Response or validation | Point or phase | Expected evidence |
| --- | --- | --- | --- | --- |
| [Description] | [Impact] | [Intended action] | PH-01 | [Observable result] |

[Prioritize validation that reduces important uncertainty. Resolve uncertainty blocking agreed scope, acceptance, or feasibility with its owning document before continuing. Record validations as planned until evidence exists; do not invent a technical-task story to bypass spec decisions.]

## Compliance and verification strategy

| Reference | Delivery or verification phase | Verification approach | Expected evidence |
| --- | --- | --- | --- |
| AC-001 | PH-01 (delivery and final verification) | [General method] | [Observable result] |
| AC-002 | PH-01 (delivery and final verification) | [Failure/alternative behavior check] | [Observable result] |
| NFR-001 → AC-003 | PH-01 (delivery and final verification) | [Quality check] | [Evidence against the spec target] |
| AC-004 | PH-02 (delivery and final verification) | [Related behavior/integration check] | [Observable result] |
| [Applicable constitution MUST reference] | [Phase] | [Review or check] | [Evidence] |

[Map every canonical AC to planned delivery and final verification; identify final verification explicitly and label partial contributions separately when relevant. Cover applicable quality requirements and constitution rules, linking their definitions instead of redefining thresholds or acceptance. Check that each phase/story/AC/NFR/rule reference exists and agrees with the spec and phase table. A prose-only quality obligation missing canonical AC coverage must return to specify for resolution. Flag conflicts; a MUST violation blocks tasks.]

Integrate verification throughout development, using checks appropriate to the change. Detailed commands, executable steps, and specific inspections belong in tasks. This is intended coverage, not evidence of completion; the controller does not assess Markdown matrix coherence or semantic adequacy.

## Operational delivery preparation

[Identify packaging, installation, configuration, compatibility, migration, and rollback needs when applicable. Reference infrastructure procedures and explain this release's application, or N/A with reason. Separate technical readiness from authorization to integrate, publish, or deploy.]

## Review, learning, and adaptation

[Define when to review the plan and what evidence may change it: verification results, feedback, discovered risks, or capacity changes. Distinguish adjustments within scope from changes to spec, roadmap, or shared design. Preserve completed work and historical evidence. Substantive revisions need approval and inspection/adoption of affected downstream pins; follow interruption/reconciliation rules for active runs.]

## Open questions and readiness for tasks

[List pending decisions and mark which block executable decomposition. Do not create tasks to hide decisions this plan still needs to resolve.]

Before handing off to tasks, review current approved bases/no conflicts, sufficiently defined technical approach, coherent phases and acyclic dependencies, intended acceptance/quality/rule coverage, understood change scope and constraints, treatment of important risks, resolution of blocking questions, and table/contract coherence. These are review requirements, not completion checkboxes. Do not require creating tasks to declare the plan ready for their preparation.

## References, approval, and amendments

[Keep sources and actual approved revisions, reasons, and affected documents. The registry remains approval authority. Plan approval allows proceeding through the tasks gate; it does not prove execution or itself authorize implementation, integration, or publication. Full-release task coverage and separate execution authorization still apply.]

<!-- spec-flow:generated:start -->
Progress is maintained by the Spec-Flow harness.
<!-- spec-flow:generated:end -->
