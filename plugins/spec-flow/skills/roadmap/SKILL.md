---
name: roadmap
description: "Prioritize measurable outcomes and project explicit SemVer releases, horizons, and human selection from approved strategy."
---

# Spec-Flow: roadmap

<HARD-GATE>
Inspect project configuration and .specs first. If legacy `.specs/NNN-name/` folders exist, stop before writing and follow the `migrate-preview` → review → `migrate-apply` flow in `using-spec-flow`; use `migrate-resume` after an interrupted apply. For a new unadopted project, run initialize with empty JSON input {} first. Run the runtime gate for this phase and obey it. Urgency never waives a failed gate. Require current registry approval of constitution and applicable shared design. Do not start a release spec until the roadmap selects its vX.Y.Z release and is approved.
</HARD-GATE>

Read approved constitution, applicable design, existing backlog, and scoped release/outcome evidence. Write `.specs/roadmap.md` using [the roadmap template](assets/roadmap-template.md). It owns priorities, horizons, outcome targets, release grouping, and explicit next-release selection. Work with the product decision-maker and relevant stakeholders; ask for unknown human choices and leave assumptions, missing metrics, and commitments pending rather than inventing them.

## Drafting the roadmap

Use all eleven template sections, with concise decision-oriented content:

1. **Purpose, audience, and scope:** readers, decisions supported, initiative, and planning horizon.
2. **Direction and approved bases:** constitution objectives, beneficiaries, boundaries, and applicable approved design. Record N/A with reasons for inapplicable design documents; dependency omission alone is not N/A.
3. **Desired outcomes and measurement:** stable OUT IDs, problems/opportunities, beneficiaries, indicators, baselines, targets, and evaluation timing/method.
4. **Prioritization criteria and rationale:** value, urgency, effort, capacity, risk, dependencies, learning, constraints, alternatives, and consequences. Scoring is optional.
5. **Horizons and uncertainty:** Now / Next / Later or agreed alternatives, progressive detail, hypotheses, validation, and advancement conditions. Separate mandatory dates, approved commitments, and forecasts.
6. **Release projections and sequence:** canonical releases plus the synchronized version table, expected contributions, high-level capabilities, and dependencies/grouping rationale.
7. **Next selected release:** explicit human choice from the canonical versions, rationale, and pending questions, or no selection yet. Never infer it from array position, horizon, or planned status.
8. **Capacity, dependencies, and risks:** conditions affecting feasibility/order, linked to outcomes/releases.
9. **Deferred opportunities and exclusions:** existing backlog links or unversioned opportunities, deferral/reconsideration reasons, and constitution exclusions. Do not require creating another document to finish the roadmap.
10. **Review, evidence, and learning:** owner, participants, agreed cadence/triggers, evidence, and resulting priority decisions. Separate verified delivery from observed/pending impact; reference release review instead of copying it.
11. **References, approval, and amendments:** sources, actual approval scope, revisions/reasons, affected documents, and remaining discovery.

Link outcomes to constitution goals without duplicating them. An outcome can span several releases and a release can support multiple outcomes; delivering a version does not prove its benefit. Keep spec behavior/acceptance, plan solution choices, and tasks executable detail in their owners. Preserve evidence provenance and distinguish proposed scope, approved direction, forecasts, and measured results.

## Canonical releases and readable projections

Keep the existing `releases` array with `version`, `objective`, and `status`; add no new required controller fields or statuses. Use strict numeric `vX.Y.Z` versions explicitly agreed with the user. Template numbers/rows are illustrative, not a version-selection rule or the installed plugin's release. Each entry states a measurable contribution to OUT IDs. If no release can yet be identified, keep the roadmap incomplete rather than fabricating one to satisfy the nonempty array requirement. Farther opportunities may remain unversioned in section 9 until sufficient definition and human choice exist.

Maintain the projection table as a reading view of that array, not an independent sequence. Include every canonical release once, in identical order; copy its objective and status exactly. Add horizon, general capabilities, and selection context in the table. Projected/Selected/Not selected are contextual labels only; canonical statuses remain planned, active, completed, deferred, or cancelled. Do not put unversioned opportunities in this table.

Before presentation, approval, or use for specification, compare table and array for row count, unique versions, order, exact objective/status values, known OUT references, and coherent selection. Update the canonical array first when its decisions change, then synchronize the table and related references in the same revision. Stop dependent drafting on a mismatch and reconcile it under the applicable approval rules. The controller validates contracts/digests; it does not check this Markdown table or establish human selection. Perform this consistency review explicitly, without claiming automatic enforcement.

Keep table and selection outside generated progress: their decision context is included in the document digest. A projection or planned status does not select the release. Confirm the user's exact version and make section 7 and the table agree; keep at most one selected next release and one active release under the existing flow. Do not change status to active merely for selection; specification uses the planned entry required by the controller. A projected version does not authorize creating its directory/spec or executing it. Selection still requires an approved roadmap and downstream gates; implementation, integration, and publication require their separate authorization.

This is a Spec-Flow adaptation informed by [PMI's product management practices](https://www.pmi.org/disciplined-agile/process/product-management/product-management-practices), [IIBA and Agile Alliance's Agile Extension, section 7.10](https://www.agilealliance.org/wp-content/uploads/2017/08/AgileExtension_V2-Member-Copy.pdf#page=86), [GO Product Roadmap](https://www.romanpichler.com/tools/the-go-product-roadmap), and [Scrum.org's customer outcomes](https://www.scrum.org/resources/customer-outcomes), not an official template from those sources.

Use `kind: "roadmap"` and an exact-digest constitution dependency; include other shared decisions it relies on. Validate and request approval. A later scope or priority change needs a new revision and approval; it does not automatically authorize execution.

## Runtime and approval

Before invoking `spec-flow.py`, read [shared controller operations](../../harness/contracts/operations.md). Follow its adoption, query/input, validation/digest, and approval/revision mechanics under this skill's own gate and authorized scope.

## Document encoding

Create new documents from the YAML-frontmatter templates. Preserve existing fenced JSON documents unless conversion is explicitly authorized. Apply [shared encoding and conversion rules](../../harness/contracts/operations.md#document-encoding); retain this skill's gates and canonical records, with no duplicate metadata source.
