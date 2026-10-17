---
schema_version: 1
kind: architecture
revision: R00
id: ARCH-PROJECT
depends_on:
- path: .specs/constitution.md
  digest: '0000000000000000000000000000000000000000000000000000000000000000'
---

# System Architecture

Replace the example constitution digest with its approved digest. Add exact-digest dependencies only for approved strategic documents whose decisions are actually used. Recommended elaboration order: architecture → infrastructure → structure; this is not a mandatory dependency chain. If a whole document is inapplicable, record N/A with a reason in the roadmap under its own gate. Omitting a dependency alone does not make its document N/A. Do not create filler or future dependent documents to complete this one; keep dependency pins acyclic and navigational links separate.

## Purpose, audience, and scope

[Identify readers, the questions this document answers, and the scope of shared design. Explain N/A for sections that do not apply.]

## System context and boundaries

[Describe users, external systems, integrations, and responsibilities outside the system. Add a context diagram when useful.]

## Current evidence and intended design

[Separate verified components and behavior from proposed changes. Cite code, tests, or other evidence; approval of a design does not establish implementation.]

## Quality goals and constraints

[Link constitution objectives and relevant restrictions without copying them. Use measurable scenarios rather than unsupported quality claims.]

| Attribute | Scenario | Expected result | Verification approach |
| --- | --- | --- | --- |
| [Quality attribute] | [Conditions and stimulus] | [Observable response] | [Evidence or planned check] |

## Solution strategy

[Explain the overall approach and why it fits the goals and constraints. Decide enough for upcoming work; leave speculative detail pending.]

## Components, responsibilities, and contracts

| ID | Component | Responsibility | Interfaces | Dependencies |
| --- | --- | --- | --- | --- |
| ARC-01 | [Name] | [Owned behavior] | [Contract] | [Related IDs or external systems] |

## Data and runtime scenarios

[Describe data ownership, exchanges, and important execution paths, including relevant failures. Add interaction diagrams when useful; choose only views that answer readers' questions.]

## Crosscutting concepts

[Record applicable shared approaches such as authentication, error handling, consistency, or compatibility. Reference operational detail in infrastructure rather than duplicating it.]

## Decisions and consequences

[For each significant decision record ID, context, alternatives, choice, rationale, positive and negative consequences, and review conditions. Distinguish proposed from approved decisions. Link existing ADRs when available; separate ADR files are optional. Preserve superseded decisions through history and replacement references.]

## Risks, technical debt, and open questions

[Identify impact, needed validation, and pending human decisions. Record assumptions explicitly. Keep release-specific implementation tasks in release documents.]

## References and amendment history

[Link approved sources and evidence with their scope. Record approved revisions and why decisions changed. Revisit when boundaries, contracts, quality goals, or significant decisions change.]

<!-- spec-flow:generated:start -->
Progress is maintained by the Spec-Flow harness.
<!-- spec-flow:generated:end -->
