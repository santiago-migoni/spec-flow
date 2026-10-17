---
name: plan
description: "Plan an approved release as verifiable technical increments with canonical phases, acceptance coverage, realistic resources, risks, and readiness for tasks."
---

# Spec-Flow: plan

<HARD-GATE>
Require current registry approval of release spec and its roadmap and strategic dependencies. Run gate for plan; unresolved material spec questions block planning.
</HARD-GATE>

Read the approved spec, its roadmap/constitution bases, applicable architecture, infrastructure and structure, and relevant current evidence. Inspect the repository. Write `.specs/release-vX.Y.Z/plan.md` using [the plan template](assets/plan-template.md). Work with those who know or will perform the work. Ask for unknown human decisions and leave missing facts, commitments, capacity evidence, or estimates explicit rather than inventing them.

## Drafting the implementation plan

The plan owns release-specific solution choices, phase goals/deliverables, sequencing, change scope, risk response, and verification strategy. Use all eleven template sections:

1. **Purpose, scope, and approved bases:** selected release, approved spec, implementation objective/boundaries, and applicable approved sources actually used.
2. **Technical approach and implementation decisions:** solution, significant alternatives, choice/rationale/consequences, facts versus assumptions; refer to shared design without copying it.
3. **Phases, deliverables, and dependencies:** canonical phases plus synchronized reading table, US/AC links, and partial versus final contributions.
4. **Components, files, and change scope:** intended changes, paths/component references, phases, and restrictions; distinguish existing/proposed locations.
5. **Capacity, resources, and forecasts:** availability, tools, environments, access, constraints, estimate basis, uncertainty, and forecasts versus commitments.
6. **Risks, assumptions, and validation:** consequence, response, timing/phase, and expected evidence; prioritize important uncertainty early.
7. **Compliance and verification strategy:** intended delivery/final verification of every AC, applicable NFRs and constitution MUSTs, appropriate methods, and expected evidence.
8. **Operational delivery preparation:** applicable packaging/installation/configuration/compatibility/migration/rollback, referencing infrastructure procedures, or justified N/A.
9. **Review, learning, and adaptation:** review points, evidence/triggers, change routing, preserved progress, revisions and affected dependencies.
10. **Open questions and readiness for tasks:** unresolved decisions, blockers, and the concrete readiness review.
11. **References, approval, and amendments:** sources, actual approval scope, revisions/reasons, and affected documents.

Organize verifiable increments and explain value, dependencies, risks, and learning behind their order. Justify enabling technical phases by what they unlock; avoid making all testing a final activity. A phase need not equal a sprint or one story, and an AC may need several phases: distinguish partial contribution from final verification. Do not redefine spec behavior/acceptance or roadmap priorities. Route changes to shared decisions to their owner before relying on them.

Use estimates only with an explicit basis and assumptions. Do not infer concurrent execution from logical independence; sequence the phases and tasks as they will actually be done. Plan approval grants no authority to publish or deploy.

## Canonical phases and table coherence

Keep the existing nonempty `phases` array with stable PH IDs, descriptions, and depends_on IDs as the sole phase sequence. Use PH- followed by at least two digits. The contract stays kind plan, id PLAN-X.Y.Z, revision R00 initially, and an exact-digest dependency on this release's spec. Include other approved sources only when their decisions directly shape the plan. Do not add schema fields for tables or introduce new phase statuses.

Every canonical phase appears once in the reading table, in identical order, with its exact description and dependency IDs/order; render an empty list as None. Story/criterion links add planning context without redefining them. Check unique IDs, known dependencies, acyclic graph and intended ordering, and that table references exist in spec and preserve AC story ownership. Never maintain an independent table sequence. A row can reference several stories; it must not reassign an AC to another story.

The task context may include the full plan prose/table even when canonical phases are scoped to the task and its predecessors. Treat future-phase rows as context; the task's own scope is what permits work. Technical enabling phases still need tasks with honest story/AC contributions under the existing contract, not fabricated stories to satisfy validation.

Review file/risk/coverage tables for valid phase references, source links, consistent change scope, and explicit partial versus final verification. Each canonical AC needs intended delivery and final verification; quality and constitution obligations must have a planned check. Use existing AC/NFR/rule definitions and targets rather than copying/redefining them. Return an uncovered prose-only spec quality obligation to `specify`; do not silently amend the spec. Flag conflicts; a constitution MUST violation blocks tasks.

Before presentation, approval, or handoff, compare phase table/array count/order/IDs/descriptions/dependencies and reconcile all cross-table references and coverage. Update canonical phase decisions first, then synchronize views in the same revision. Stop dependent task drafting on a mismatch. Keep all decision tables outside generated progress: their context participates in the digest. The controller checks structural phase IDs/dependencies and later release task coverage, not Markdown table coherence, planned semantic coverage, or feasibility. Perform this review explicitly without claiming automatic enforcement.

## Handoff and maintenance

Readiness for tasks requires current approved bases, no unresolved conflicts, a sufficiently defined technical approach, coherent acyclic phases, intended AC/quality/MUST coverage, understood file scope/resources, risk responses, and resolved blocking decisions. Do not create tasks or another document to conceal missing plan decisions or prove readiness. Spec owns behavior/acceptance; this plan owns approach/phases/dependencies/verification strategy; tasks owns concrete actions, files, commands, ordered steps, and inspections. Keep those executable details out of this plan.

Preserve completed work and historical evidence when feedback changes the plan. Route changed behavior/acceptance to specify, priorities to roadmap, and shared decisions to their owner. A substantive postapproval revision requires new approval and explicit adoption of changed downstream pins; reconcile active execution before retrying. Full-release spec/plan/tasks and complete AC coverage remain required before execution; these edits do not allow undefined future-phase tasks.

This is a Spec-Flow adaptation informed by [PMI's planning guidance](https://www.pmi.org/microsites/disciplined-agile/agile/agileplanningtips) and [risk practices](https://www.pmi.org/microsites/disciplined-agile/agile/agilerisk), [IIBA/Agile Alliance's Planning Workshops](https://www.agilealliance.org/wp-content/uploads/2017/08/AgileExtension_V2-Member-Copy.pdf#page=80), [Agile Alliance's incremental design](https://agilealliance.org/glossary/xp/), and [DORA's testing](https://dora.dev/capabilities/test-automation/). It is not an official template from those sources.

Validate the plan path alone at this phase; full-release validation waits until spec, plan, and tasks exist. Present the concrete plan for approval before dependent task preparation.

## Runtime discipline

Before invoking `spec-flow.py`, read [shared controller operations](../../harness/contracts/operations.md). Follow its adoption, query/input, validation/digest, and approval/revision mechanics under this skill's own gate and authorized scope.

## Document encoding

Create new documents from the YAML-frontmatter templates. Preserve existing fenced JSON documents unless conversion is explicitly authorized. Apply [shared encoding and conversion rules](../../harness/contracts/operations.md#document-encoding); retain this skill's gates and canonical records, with no duplicate metadata source.
