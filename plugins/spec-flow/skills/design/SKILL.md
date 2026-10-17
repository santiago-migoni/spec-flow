---
name: design
description: "Use when defining, reviewing, or updating shared architecture, infrastructure, or repository structure."
---

# Spec-Flow: design

<HARD-GATE>
Inspect project configuration and .specs first. For creation or revision, select each affected document kind and apply its preserved gate below before writing; require current registry approvals of the constitution and all source decisions actually used. Stop affected work on a failed gate or unapproved dependency. Design is a skill, not a runtime gate or document kind. A read-only review inspects and reports without initialization, writes, approval recording, or automatic execution. Approval of design never authorizes implementation, integration, publication, deployment, or recovery execution.
</HARD-GATE>

## Scope and routing

Recover the user's requested operation, existing documents, current approvals, and relevant code/configuration evidence. Distinguish creation, scoped revision, and read-only coherence review. A request about one perspective does not restart the others. Read-only findings stay in conversation; proposals remain unapproved. Load only the templates needed for the authorized work.

| Perspective | Canonical document | Runtime gate kind | Template |
| --- | --- | --- | --- |
| Architecture | `.specs/architecture.md` | `architecture` | [Architecture](assets/architecture-template.md) |
| Infrastructure | `.specs/infrastructure.md` | `infrastructure` | [Infrastructure](assets/infrastructure-template.md) |
| Structure | `.specs/structure.md` | `structure` | [Structure](assets/structure-template.md) |

Run `gate` with {"kind":"<selected document kind>"}, never kind design. The preserved blocks below apply only when creating/revising their corresponding document; “this phase” means that document kind. Gates check the constitution; also inspect registry approval of every source actually relied on and validate exact dependency digests. There is no combined design approval, `.specs/design.md`, or kind design.

Recommended elaboration order is architecture → infrastructure → structure, using only applicable perspectives. Inspect existing repository organization and operational constraints early; evidence can require revisiting source decisions. This is not a mandatory dependency chain. Infrastructure does not require structure by default, and structure can proceed without infrastructure when it does not rely on it. An absent or unpinned document is not automatically N/A.

For a genuinely inapplicable document, create no filler; report the reason and record N/A when drafting the roadmap under its own gate. Within an applicable document, explain inapplicable template sections. Do not create future dependent documents to complete an earlier one. If a requested document needs a new decision from another perspective, obtain approval of that source before writing the dependent document; otherwise continue only independent authorized work.

## Shared decisions and dependencies

Design enough for upcoming work. Reuse current approved sources without reopening unchanged interviews or approvals. Ask one consequential human question at a time; leave unknown choices, targets, owners, commitments, and assumptions explicit. Distinguish inspected implementation/configuration, proposed changes, approved design, tested behavior, and deployed resources; evidence identifies source and scope, and approval proves none of the implementation/operational outcomes.

Keep constitution principles, roadmap priorities, and release implementation details with their owners. Record significant decisions with ID, context, alternatives, choice, rationale, consequences, and review conditions; link existing ADRs rather than requiring additional files. Reference decisions across perspectives instead of duplicating editable definitions. Preserve superseded history and inspect affected dependents when decisions change.

Every document pins the constitution's exact decision digest plus only approved strategic sources actually used. Require their current registry approval before relying on them. Keep the dependency graph acyclic: feedback calls for source revision and explicitly approved adoption, not reciprocal pins. Navigational links alone do not create dependencies. Preserve each document's stable ID, kind, revision/history, generated tail, and approval receipt when its content is unchanged. Moving to this skill does not migrate project documents, change their digests, or require new approvals.

## Architecture

<HARD-GATE>
Inspect project configuration and .specs first. If legacy `.specs/NNN-name/` folders exist, stop before writing and follow the `migrate-preview` → review → `migrate-apply` flow in `using-spec-flow`; use `migrate-resume` after an interrupted apply. For a new unadopted project, run initialize with empty JSON input {} first. Run the runtime gate for this phase and obey it. Urgency never waives a failed gate. Require current registry approval for the exact constitution digest; a Markdown label is insufficient.
</HARD-GATE>

Read the approved constitution, current code, and relevant existing design evidence. Use the architecture template for system context/boundaries, shared components/responsibilities/contracts, data ownership/flow, quality goals, and cross-release technical decisions.

Use all eleven template sections: purpose/audience/scope; system context/boundaries; current evidence/intended design; quality goals/constraints; solution strategy; components/contracts; data/runtime scenarios; crosscutting concepts; decisions/consequences; risks/debt/questions; references/amendments.

Choose diagrams that answer a reader's question: context and application/data-store views may suffice; add components/interactions when useful. Give components stable IDs and quality goals observable scenarios and verification approaches. Cover important failure paths and data ownership. Revisit when boundaries, interfaces, quality goals, or significant decisions change. Repository placement belongs in structure and deployment/operations in infrastructure; reference their documents when available without making them prerequisites merely for navigation.

## Infrastructure

<HARD-GATE>
Inspect project configuration and .specs first. If legacy `.specs/NNN-name/` folders exist, stop before writing and follow the `migrate-preview` → review → `migrate-apply` flow in `using-spec-flow`; use `migrate-resume` after an interrupted apply. For a new unadopted project, run initialize with empty JSON input {} first. Run the runtime gate for this phase and obey it. Urgency never waives a failed gate. Require current registry approval of constitution and the applicable architecture or structure decisions this infrastructure relies on.
</HARD-GATE>

Read applicable approved design and actual deployment/configuration evidence. Use the infrastructure template for execution environments, resources, configuration/access, build/distribution/deployment, operations, capacity/costs, and recovery. Link component IDs and known repository paths instead of copying their decisions. Local plugins may need host/runtime, permissions, installation, distribution, and state recovery decisions even without servers.

Use all eleven template sections: purpose/audience/operational scope; current evidence; environments/resources; deployment mapping/connections; configuration/access/secrets; build/distribution/deployment/rollback; observability/operations; capacity/limits/costs; backup/restoration/recovery; decisions/risks/questions; references/amendments.

Map components to execution resources and explain environment differences. Identify permissions and secret management through secure references, never secret values. Link automation and detailed procedures. State applicable operational signals, objectives/thresholds, responses, and owners. Define recovery time (RTO) and tolerable data loss (RPO) only when justified by project needs. Separate capacity/cost estimates, intended procedures, and planned recovery checks from measurements and completed tests. Revisit when environments, resources, deployment, access, or recovery decisions change; component design stays in architecture and repository placement in structure.

## Structure

<HARD-GATE>
Inspect project configuration and .specs first. If legacy `.specs/NNN-name/` folders exist, stop before writing and follow the `migrate-preview` → review → `migrate-apply` flow in `using-spec-flow`; use `migrate-resume` after an interrupted apply. For a new unadopted project, run initialize with empty JSON input {} first. Run the runtime gate for this phase and obey it. Urgency never waives a failed gate. Require current registry approval of constitution and any architecture decision this structure relies on.
</HARD-GATE>

Inspect actual repository paths and applicable approved architecture/infrastructure. Use the structure template for repository organization, code module boundaries, directory purposes, placement/naming rules, dependency direction, entry points, and distribution boundaries. Incorporate approved operational decisions affecting packages, configuration, deployment files, or distribution; omit dependencies not actually needed, even if their documents exist.

Use all ten template sections: purpose/audience/scope; verified current organization; architecture-to-repository mapping; intended organization/placement; naming/public interfaces; dependencies/module boundaries; tests/configuration/documentation/resources; generated/third-party/distribution files; decisions/risks/pending changes; references/amendments.

Include an annotated verified tree in a fenced text block from inspected paths, at useful depth, describing omitted repetitive content or downloaded dependencies. State verified absence for an empty repository and do not impose the template's illustrative src/ layout. When proposing layout changes, provide a separate annotated proposed tree; otherwise state no layout change is needed and omit it. Never present future paths as verified current paths; the tree command is not required.

Map components or known responsibilities to paths, current/proposed state, and entry points. Explain where the next change belongs and the available checks. Distinguish editable sources, generated outputs, third-party content, and distributable artifacts; link operational procedures. Revisit when module layout, dependency rules, entry points, or distribution boundaries change. Approval does not create directories or establish implementation.

## Coherence, validation, and handoff

Review the affected perspectives together: component IDs/responsibilities must agree with execution resources and repository mappings; quality/failure/recovery constraints must be consistent; current/proposed states, references, and evidence must match. Inspect affected downstream pins and report blockers and proposed corrections within authorized scope. A read-only review writes no canonical document or additional report file.

Before invoking `spec-flow.py`, read [shared controller operations](../../harness/contracts/operations.md). A read-only design review uses only strict consultation queries with `GIT_OPTIONAL_LOCKS=0 python3 -B`, existing inputs or `/dev/stdin`, and Git reads without index refresh; no helper files, caches, setup, or approval recording. For authorized creation/revision use the affected document's preserved gate and the shared adoption/validation/approval mechanics. Keep separate per-document receipts; preserve unchanged perspectives and explicitly approve affected downstream adoption.

Report the perspectives inspected/changed, validation and coherence findings, actual approval state, pending decisions, and next authorized step. Changing an approved source invalidates the approvals that pinned it; re-approve those documents before dependent work. Do not automatically create roadmap or release documents, start implementation or operations, or advance through missing approvals.

This Spec-Flow adaptation draws on [PMI's agile documentation guidance](https://www.pmi.org/disciplined-agile/agile/documentation), [Agile Alliance's continuous design](https://agilealliance.org/glossary/simple-design/), [arc42](https://arc42.org/overview/), [C4](https://c4model.com/diagrams), [ADRs](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions), [deployment views](https://docs.arc42.org/section-7/), [Google SRE](https://sre.google/sre-book/evolving-sre-engagement-model/), [AWS recovery guidance](https://docs.aws.amazon.com/wellarchitected/latest/framework/rel-13.html), and [building-block/source mapping](https://faq.arc42.org/questions/C-5-6/); it is not an official template from those sources and requires no particular provider or hosted service.

## Document encoding

Create new documents from the YAML-frontmatter templates. Preserve existing fenced JSON documents unless conversion is explicitly authorized. Apply [shared encoding and conversion rules](../../harness/contracts/operations.md#document-encoding); retain this skill's gates and canonical records, with no duplicate metadata source.
