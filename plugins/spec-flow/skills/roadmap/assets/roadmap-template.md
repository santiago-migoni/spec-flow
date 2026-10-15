# Product Roadmap

```spec-flow
{
  "schema_version": 1,
  "kind": "roadmap",
  "revision": "R00",
  "id": "ROADMAP-PROJECT",
  "depends_on": [
    {
      "path": ".specs/constitution.md",
      "digest": "0000000000000000000000000000000000000000000000000000000000000000"
    }
  ],
  "releases": [
    {
      "version": "v2.0.0",
      "objective": "[Measurable contribution to OUT-001.]",
      "status": "planned"
    },
    {
      "version": "v2.1.0",
      "objective": "[Further contribution to OUT-001.]",
      "status": "planned"
    },
    {
      "version": "v3.0.0",
      "objective": "[Contribution to OUT-002, subject to validation.]",
      "status": "planned"
    }
  ]
}
```

The example versions and row count are illustrative, unrelated to this plugin's version, and must be replaced with projections explicitly agreed with the user (for example v0.1.0 onward for a new product). Keep one canonical releases array and synchronize its reading table below. Example entries do not select a release or authorize creating release directories.

## Purpose, audience, and scope

[Identify who uses this roadmap, what decisions it supports, the product or initiative covered, and an appropriate planning horizon.]

## Direction and approved bases

[Reference constitution goals, beneficiaries, and boundaries. Identify architecture, infrastructure, or structure decisions that constrain priorities. Pin only approved sources actually used; record N/A with a reason for genuinely inapplicable design documents. A document omitted from depends_on is not automatically N/A.]

## Desired outcomes and measurement

[Give each outcome a stable ID and explain the problem or opportunity. Distinguish expected benefits from capabilities and deliverables. Leave unknown data, targets, or commitments explicitly pending.]

| ID | Desired outcome | Beneficiaries | Indicator | Baseline | Target | Evaluation |
| --- | --- | --- | --- | --- | --- | --- |
| OUT-001 | [Desired improvement] | [Users or stakeholders] | [Measure] | [Known value or pending] | [Target or pending] | [When and how] |
| OUT-002 | [Later improvement] | [Users or stakeholders] | [Measure] | [Known value or pending] | [Target or pending] | [When and how] |

## Prioritization criteria and rationale

[Explain why some outcomes precede others, considering value, urgency, effort, capacity, risk, dependencies, learning, and external constraints where relevant. Record meaningful alternatives and consequences; use scoring only when it helps decisions.]

## Horizons and uncertainty

[Define Now / Next / Later or agreed alternatives, with more detail nearby and less farther out. State hypotheses, validations, and conditions for advancing. Keep release membership/order in the canonical array and projection table rather than a second sequence here. Distinguish mandatory dates, approved commitments, and forecasts; omit dates without adequate basis.]

## Release projections and sequence

The canonical releases array owns versions, order, objectives, and statuses. This table is its synchronized reading view, with horizon, capabilities, and selection as additional decision context. Each canonical release appears exactly once in the same order, including deferred or cancelled entries retained in the record. Copy objective and status exactly; explain contributions through OUT IDs rather than inventing a different objective in the table.

| Version | Horizon | Expected contribution | General capabilities | Canonical status | Selection |
| --- | --- | --- | --- | --- | --- |
| v2.0.0 | Now | [Measurable contribution to OUT-001.] | [Minimum capabilities] | planned | Projected |
| v2.1.0 | Next | [Further contribution to OUT-001.] | [Expected capabilities] | planned | Projected |
| v3.0.0 | Later | [Contribution to OUT-002, subject to validation.] | [Capabilities to validate] | planned | Projected |

[Replace these rows together with the canonical examples. Explain grouping rationale, ordering constraints, and relevant dependencies keyed to versions without creating another release list. For retained releases no longer projected or selected, say Not selected and explain the context without adding controller states. Optional dates must identify forecast versus commitment.]

A desired outcome may need several releases, and a release may contribute to more than one outcome. General capabilities can group multiple stories; behavior and detailed acceptance belong in release specs. Revisit projected grouping, scope, or order through review and approval. Unversioned opportunities belong in deferred opportunities below, not invented releases.

Before presenting or approving, check table/array row count, unique versions, order, exact objective/status matches, known OUT IDs, and consistency of Selection with the next selected release below. Projected and Selected are contextual labels, not new canonical statuses or execution permissions; planned alone does not mean selected. Keep this table outside generated progress: its context and selection are decision prose included in the digest.

## Next selected release

[State None selected yet, or identify exactly one canonical version explicitly selected with the user, why it is next, and its pending questions before specification. Match the table's Selected label; do not infer selection from Now, planned, or the first array position. Keep one active release at a time under the existing workflow.]

Selection allows proceeding only through the applicable document gates. It does not authorize implementation, integration, or publication. Do not set status to active merely to indicate selection; follow the current controller lifecycle.

## Capacity, dependencies, and risks

[Record availability, resources, external decisions, and important uncertainties affecting feasibility or order. Link outcomes/releases and distinguish confirmed constraints from assumptions. Keep execution detail in release plans.]

## Deferred opportunities and exclusions

[Link existing backlog items or describe opportunities not yet versioned; explain deferral and conditions for reconsideration. Distinguish these from constitution exclusions. Do not create a backlog document just to complete this section; use its own workflow when authorized.]

## Review, evidence, and learning

[Identify owner, participants, agreed review cadence, and triggers. Reference release review evidence and outcome measurements, distinguishing verified delivery, observed impact, and pending impact. Explain learning that warrants retaining, reordering, reformulating, or abandoning priorities; do not mark an outcome achieved from release delivery alone. Link closure reports instead of copying them.]

## References, approval, and amendments

[Keep sources and approved revisions, reasons, and affected documents. State what is approved and what remains subject to discovery: an approved future intention does not fix its detailed scope. Approval authority remains in the controller registry. Substantive changes need a new revision/approval and review of downstream pins.]

<!-- spec-flow:generated:start -->
Progress is maintained by the Spec-Flow harness.
<!-- spec-flow:generated:end -->
