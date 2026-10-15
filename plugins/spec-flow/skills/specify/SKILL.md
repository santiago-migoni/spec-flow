---
name: specify
description: "Specify a selected SemVer release with bounded user value, canonical stories and acceptance, quality requirements, and traceability ready for planning."
---

# Spec-Flow: specify

<HARD-GATE>
Require an approved roadmap selecting the explicit vX.Y.Z release and current registry approval of its exact digest. Run gate for specify and the release. If a legacy feature directory or unadopted configuration exists, migrate first. Do not write on the repository default branch.
</HARD-GATE>

Read constitution, the selected roadmap entry and OUT IDs, applicable approved shared design, existing backlog, and relevant current evidence. Ask one high-impact question at a time, collaborating with the product decision-maker, relevant users, and development/test perspectives. Resolve the exact release version from the user and roadmap; do not infer selection from a projected/planned status, array position, or directory number. Write `.specs/release-vX.Y.Z/spec.md` using [the spec template](assets/spec-template.md). Create or switch to a release branch before writing; preserve unrelated work.

## Drafting the spec

The spec owns release behavior, user stories, acceptance, scope/exclusions, quality requirements, edge cases/compatibility obligations, and outcome measurement. Use all eleven template sections:

1. **Purpose and selected release:** explicit version, approved roadmap entry, and delivery purpose.
2. **Users, context, and expected outcome:** real actors, needs, situations, existing OUT references, and release contribution; one release need not achieve the entire outcome.
3. **Scope and exclusions:** included capabilities, boundaries, coherent value, and work deferred elsewhere.
4. **Approved bases and constraints:** constitution and applicable shared design, referenced rather than copied; pin only approved sources actually used.
5. **User stories:** canonical stories plus a reference table linking US IDs, roadmap OUT IDs, owned AC IDs, and relevant dependencies.
6. **Rules, acceptance, and examples:** verifiable behavior/conditions and concrete situation-action-result examples linked to AC IDs. Given/When/Then is optional.
7. **Quality and conditions of done:** measurable release NFRs with conditions, targets, verification approaches, and AC links; reference shared quality conditions and explain N/A when appropriate.
8. **Edge cases, errors, and compatibility:** observable alternative/failure responses and applicable compatibility/data-transition obligations linked to AC IDs. Implementation procedures belong in plan.
9. **Post-delivery measurement:** roadmap metric references and release evaluation source, method, timing, and owner. Separate technical acceptance, delivery, and observed/pending impact.
10. **Assumptions, dependencies, and open questions:** consequences/validation, material blockers, and technical choices that can remain for plan.
11. **Readiness for planning, approval, and amendments:** readiness/coherence review, sources, actual approval scope, and revision reasons/affected documents.

Keep releases small enough to define coherently under the current full-release coverage requirement; do not speculate on future releases to finish this spec. Split oversized stories by independently testable user value, using INVEST as a review aid rather than an automatic certification. Do not invent user stories merely to relabel technical tasks. Explain real story dependencies. Use cases, examples, or light models may clarify context without forcing tooling or premature implementation choices. Leave unknown human decisions, baselines, and commitments explicit.

## Canonical records and table coherence

Keep `stories` with US IDs, titles, and descriptions and `acceptance` with AC IDs, exactly one owning story, and falsifiable descriptions as the sole canonical definitions. Use US-/AC- followed by at least three digits for compatibility with tasks. Retain the current contract: kind spec, id SPEC-X.Y.Z, revision R00 initially, nonempty arrays, and an exact-digest roadmap dependency. Add no new required schema fields for OUT/NFR mappings or tables; include other approved strategic sources only when directly used.

Maintain the story traceability table as a reference view: every canonical story once in the same order, only known roadmap OUT IDs, and every owned AC listed under its actual story. Give each story meaningful acceptance coverage; cross-story dependencies do not allow transferring criterion ownership. Keep examples and NFR rows linked to existing AC IDs and local NFR IDs. They explain or illustrate acceptance without becoming an independent criterion list. If any table, error case, or compatibility statement introduces required behavior, update/add canonical acceptance and synchronize references in the same revision.

Represent quality obligations that need task verification in canonical acceptance, directly or by explicit reference to NFR conditions/targets in this document. A prose-only NFR is not checked by the controller's AC coverage. Keep each target defined once and all examples/references consistent; do not invent a second story owner for a shared AC. Detailed commands, files, and executable steps belong in tasks, not the spec.

Before presentation, approval, or handoff to plan, review story row count/order/uniqueness, known US/OUT/AC/NFR references, complete correct AC membership, consistent examples/quality thresholds, and absence of prose-only acceptance obligations. Update canonical decisions first, then reconcile their views before dependent work. Keep these tables outside generated progress; their context is decision prose included in the digest. Controller validation checks structural contracts/references, not Markdown table coherence, INVEST, or semantic completeness; perform that review explicitly.

## Handoff and refinement

Resolve questions material to scope, acceptance, or feasibility before plan. For an initial unapproved spec or an existing amendment draft, resolve them here under the specify gate; `$clarify` requires the spec itself and its dependency closure to have current approval. Use `$clarify` for consequential ambiguity in that approved base. Do not approve an ambiguous draft merely to enter clarify, or reuse an old receipt for changed content. Resume an interrupted amendment at its existing RNN; initial drafts retain R00 and further rounds before approval do not increment revision. Use clarify's [dated session template](../clarify/assets/clarifications-template.md) when recording consequential draft decisions, keeping canonical stories/acceptance and their views coherent. A confirmed answer covers only its actual scope; final decision content still requires explicit approval.

Plan-owned technical choices may remain open when they do not prevent understanding or accepting behavior. Spec readiness requires the selected release/current approved bases, coherent scope, bounded stories, verifiable acceptance/quality, and reconciled references. Do not create plan/tasks or another document to fill missing spec decisions. Spec owns what/acceptance; plan owns solution choices, phases/dependencies and verification strategy; tasks owns actions, files, steps and concrete checks. Do not restate roadmap priorities or shared architectural decisions.

Keep one active release at a time, with multiple stories/features allowed. The controller requires spec, plan, tasks and full AC coverage for release validation; these edits do not enable incomplete future-phase tasks. A substantive refinement after approval needs new revision/approval and explicit adoption of changed downstream pins. Approval of this document does not itself authorize implementation, integration, or publication, and accepted delivery does not prove impact.

This Spec-Flow adaptation draws on [PMI's functional requirements](https://www.pmi.org/disciplined-agile/product-owner/practice-capturing-functional-requirements) and [quality guidance](https://www.pmi.org/disciplined-agile/agile/qualityrequirements), [Agile Alliance's story splitting](https://agilealliance.org/glossary/story-splitting/), [IIBA/Agile Alliance's story elaboration](https://www.agilealliance.org/wp-content/uploads/2017/08/AgileExtension_V2-Member-Copy.pdf#page=104), and [Cucumber's Example Mapping](https://cucumber.io/docs/bdd/example-mapping/); it is not an official template from those sources.

Run validate with {"release":"vX.Y.Z"} only after spec, plan, and tasks all exist; for this phase validate the spec path alone. Backlog items become linked or removed only after a valid spec draft is written; never claim a release from an unchecked idea.

## Runtime discipline

Resolve <plugin-root> from this installed SKILL.md. Run python3 <plugin-root>/scripts/spec-flow.py --root <project> OP --input <json-file>. Use validate with {"path":"..."} or {"release":"vX.Y.Z"}, digest with {"path":"..."}, gate with {"kind":"<phase>","release":"vX.Y.Z"}, and status with {}. Registry approval of the exact decision digest controls gates; a Markdown status is only a view. If legacy `.specs/NNN-name/` folders exist, stop before writing and follow the `migrate-preview` → review → `migrate-apply` flow in `$using-spec-flow`; use `migrate-resume` after an interrupted apply. For a new unadopted project, run initialize with empty JSON input {} first. Do not silently convert historical approvals or checked boxes.

Validate the resulting document. Present its concrete draft for human approval. On explicit approval call approve with {"path":"<project-relative path>","actor":"<human>","statement":"<their approval>","source":"<conversation reference>"}. A substantive edit after approval increments RNN and requires new approval; inspect affected downstream pins and adopt a new base only with explicit approval. Do not approve on behalf of the user.
