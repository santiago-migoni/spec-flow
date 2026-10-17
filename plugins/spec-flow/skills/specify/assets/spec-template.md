---
schema_version: 1
kind: spec
revision: R00
id: SPEC-X.Y.Z
depends_on:
- path: .specs/roadmap.md
  digest: '0000000000000000000000000000000000000000000000000000000000000000'
stories:
- id: US-001
  title: '[Story title]'
  description: As a [user], I need [capability] so that [benefit].
- id: US-002
  title: '[Related story title]'
  description: As a [user], I need [related capability] so that [benefit].
acceptance:
- id: AC-001
  story: US-001
  description: '[Observable successful behavior under stated conditions.]'
- id: AC-002
  story: US-001
  description: '[Observable response to a relevant invalid input or failure.]'
- id: AC-003
  story: US-001
  description: '[Observable quality behavior satisfying NFR-001 under its documented conditions and target.]'
- id: AC-004
  story: US-002
  description: '[Observable behavior contributing the related story''s value.]'
---

# Release Spec: vX.Y.Z

Replace the illustrative stories, criteria, table rows, outcome references, and NFR with the selected release's actual decisions. They prescribe neither story count nor scope. Keep one canonical stories array and one acceptance array. All decision tables below stay outside generated progress and participate in the document digest.

## Purpose and selected release

[Identify the version explicitly chosen with the user, its entry in the approved roadmap, and the purpose of this delivery. A projected/planned entry alone does not establish human selection.]

## Users, context, and expected outcome

[Describe real actors, their needs and usage context. Reference existing roadmap OUT IDs and explain this release's contribution without assuming one delivery achieves the whole outcome. Do not invent upstream goals or copy their definitions.]

## Scope and exclusions

[State included capabilities, boundaries, and explicit exclusions. Describe the coherent increment of value; identify what belongs to other releases or the backlog without selecting or creating them.]

## Approved bases and constraints

[Reference constitution and applicable architecture, infrastructure, and structure decisions. Pin only approved sources actually used. Identify constraints on behavior without repeating shared design or prematurely choosing release implementation.]

## User stories

The stories array owns each story's ID, title, and description; acceptance owns each AC's ID, story owner, and verifiable description. Use this section for additional context and this reference view, not a second definition. Split oversized stories into independently valuable, testable increments. Explain actual dependencies rather than inventing technical-task stories.

| Story | Related outcomes | Acceptance criteria | Relevant dependencies |
| --- | --- | --- | --- |
| US-001 | OUT-001 | AC-001, AC-002, AC-003 | [References or none] |
| US-002 | OUT-001 | AC-004 | [References or none] |

[Include each canonical story exactly once, in canonical order. Reference only existing roadmap outcomes and all AC IDs belonging to that story. Dependencies between stories do not transfer criterion ownership.]

## Rules, acceptance, and examples

[Keep required observable behavior, including relevant conditions, in canonical acceptance descriptions. Use concrete examples where they remove ambiguity; Given/When/Then is optional and does not require a tool.]

| Criterion | Situation or input | Action or event | Expected result |
| --- | --- | --- | --- |
| AC-001 | [Concrete valid context] | [Action] | [Observable instance of AC-001] |
| AC-002 | [Relevant invalid input or failure] | [Action] | [Observable instance of AC-002] |
| AC-003 | [Conditions in NFR-001] | [Action] | [Observable satisfaction of the NFR-001 target] |

[Examples need not enumerate every possible case. Each row must reference an existing AC and illustrate it consistently. If an example reveals a new obligation, update/add the canonical criterion under the correct story in the same revision; do not leave new acceptance solely in prose.]

## Quality and conditions of done

[Define release-specific quality requirements and reference applicable shared conditions of done. Explain N/A when appropriate. Distinguish functional acceptance, increment quality, and any additional delivery conditions.]

| ID | Attribute | Conditions | Result or threshold | Verification approach | Related criteria |
| --- | --- | --- | --- | --- | --- |
| NFR-001 | [Quality attribute] | [Relevant context/load] | [Measurable target] | [General method] | AC-003 |

[Link each quality obligation requiring task verification to canonical AC descriptions, directly or through an explicit NFR reference such as AC-003 above. Keep conditions/targets consistent and defined once. For a cross-story requirement, provide the needed canonical criteria under their actual story owners rather than sharing an AC across owners. A prose-only NFR is not covered by the controller's AC coverage check. Detailed verification commands belong in tasks.]

## Edge cases, errors, and compatibility

[Describe expected responses to relevant invalid inputs, failures, and alternative situations, referencing their AC IDs. Identify compatibility or data-transition obligations when applicable; technical procedures belong in plan. Update canonical acceptance whenever this section introduces required behavior.]

## Post-delivery measurement

[Reference roadmap indicators and targets, then specify this release's evaluation source, method, timing, and owner. Distinguish technical acceptance, actual delivery, and observed impact. Accepted releases can retain pending impact measurement. Leave unknowns explicit and explain any N/A.]

## Assumptions, dependencies, and open questions

[Record uncertainties, consequences, and needed validation. Mark questions that block scope, acceptance, or feasibility and resolve them before plan. Technical choices owned by plan can remain open if behavior and acceptance are sufficiently clear; do not require creating plan/tasks to complete this spec.]

## Readiness for planning, approval, and amendments

Before presenting the spec as ready for planning, review explicit release selection/current approved bases, coherent scope, bounded valuable stories, verifiable criteria, relevant quality/exceptions/constraints, and resolution of material questions. Check story-table count/order/IDs, complete AC membership under the correct owner, known OUT references, valid example/NFR links, and semantic consistency with canonical acceptance. Reconcile any mismatch before dependent planning. These are review requirements, not completion checkboxes.

[Keep decision sources and approved revisions, reasons, and affected documents. Record actual approval scope; authority remains in the controller registry. A substantive change needs revision/approval and inspection of affected downstream pins. Spec approval permits progression through the plan gate, not implementation, integration, or publication.]

<!-- spec-flow:generated:start -->
Progress is maintained by the Spec-Flow harness.
<!-- spec-flow:generated:end -->
