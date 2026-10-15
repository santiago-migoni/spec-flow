---
name: infrastructure
description: "Define execution environments, resources, distribution, operations, and recovery from the applicable approved project and architecture decisions."
---

# Spec-Flow: infrastructure

<HARD-GATE>
Inspect project configuration and .specs first. If legacy `.specs/NNN-name/` folders exist, stop before writing and follow the `migrate-preview` → review → `migrate-apply` flow in `$using-spec-flow`; use `migrate-resume` after an interrupted apply. For a new unadopted project, run initialize with empty JSON input {} first. Run the runtime gate for this phase and obey it. Urgency never waives a failed gate. Require current registry approval of constitution and the applicable architecture or structure decisions this infrastructure relies on.
</HARD-GATE>

Read the approved constitution, applicable design, and actual deployment/configuration evidence. Write `.specs/infrastructure.md` using [the infrastructure template](assets/infrastructure-template.md). It owns execution environments, resources, configuration/access, build/distribution/deployment, operations, capacity, costs, and recovery. Link component IDs and known repository locations instead of copying their decisions.

Recommended elaboration order is architecture → infrastructure → structure, with only applicable documents. Structure is not a default prerequisite: define execution/distribution constraints before their repository layout when useful. Read existing paths from the start; add links to later structure documentation when available. A local plugin may need host/runtime, permissions, installation, distribution, and state recovery decisions even without servers. If the document is inapplicable, create no filler; record N/A with a reason when drafting the roadmap under its own gate.

## Drafting and review

Use all eleven template sections: purpose/audience/operational scope; current evidence; environments/resources; deployment mapping/connections; configuration/access/secrets; build/distribution/deployment/rollback; observability/operations; capacity/limits/costs; backup/restoration/recovery; decisions/risks/questions; references/amendments. Explain N/A for inapplicable sections.

Map components to execution resources and describe environment differences. Identify permissions and secret management by secure references, never secret values. Link automation and detailed procedures. State relevant operational signals, objectives or thresholds, responses, and owners. Define recovery time (RTO) and tolerable data loss (RPO) only when applicable, based on project needs. Distinguish estimated capacity/costs, intended procedures, and planned recovery checks from measurements and completed tests.

Record significant decisions with ID, context, alternatives, choice, rationale, consequences, and review conditions, or link existing ADRs. Ask for missing commitments and leave unknown targets, owners, assumptions, and human decisions explicit. Separate declared configuration, tested behavior, deployed resources, and proposed design; approval proves none of those operational outcomes. Scope evidence to what was inspected or tested.

Revisit when environments, resources, deployment, access, or recovery decisions change; inspect affected dependents. Keep component design in architecture, placement in structure, priorities in roadmap, and release implementation in release plans. Do not require or create future dependent documents to finish this one. Documentation and approval do not authorize executing deployment, recovery, integration, or publication.

This Spec-Flow adaptation draws on [arc42's deployment view](https://docs.arc42.org/section-7/), [Google SRE](https://sre.google/sre-book/evolving-sre-engagement-model/), and [AWS recovery guidance](https://docs.aws.amazon.com/wellarchitected/latest/framework/rel-13.html). Adapt to the actual product; these sources do not require a hosted service or a particular provider.

Use `kind: "infrastructure"` with exact-digest dependencies on constitution and only the applicable approved architecture or structure decisions actually used. Require their current registry approval before relying on them. Keep the graph acyclic; feedback calls for reviewing source decisions, not reciprocal pins. Navigational path references alone do not create dependencies. Validate and request approval.

## Runtime and approval

Resolve the plugin root from this installed skill. Run `python3 <plugin-root>/scripts/spec-flow.py --root <project> validate --input <json-file>` with `{"path":"<project-relative path>"}` after writing. Use `digest` with the same input to capture exact dependency digests. One fenced `spec-flow` JSON block holds `schema_version: 1`, `kind`, stable `id`, `revision: "R00"` initially, and `depends_on` references. Decision prose remains outside the block. Only generated progress and optional lowercase `status` may be updated as views.

Present the draft for human approval. On explicit approval, call `approve --input <json-file>` with `{"path":"<path>","actor":"<human>","statement":"<their approval>","source":"<conversation reference>"}`. The registry binds exact decision content. A substantive postapproval edit increments `RNN` and needs new approval; inspect affected downstream pins and adopt a new base only with explicit approval. Neither a Markdown status nor old approval of different content is authority. Do not approve on the user's behalf.
