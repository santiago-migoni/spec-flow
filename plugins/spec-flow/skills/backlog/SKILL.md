---
name: backlog
description: "Manage deferred project opportunities when capturing, consulting, refining, reviewing, or recording backlog decisions."
---

# Spec-Flow: backlog

<HARD-GATE>
No phase prerequisite. Inspect adoption and legacy status before writing; migration is mandatory for legacy projects.
</HARD-GATE>

## Purpose and requested operation

Manage optional `.specs/backlog.md` as a side channel for deferred opportunities, needs, and ideas, including product, quality, infrastructure, and learning improvements. No approved constitution, design, roadmap, or release is required to capture an idea. Read existing strategy or release material only when relevant and available; missing documents do not require another interview or phase.

| Operation | Result |
| --- | --- |
| Consult | Answer from existing information without writing. |
| Capture | Check for a matching opportunity, then add or enrich the appropriate item. |
| Refine | Clarify the problem/value, evidence, uncertainties, and relevant dependencies progressively. |
| Review | Assess relevance, duplicates, priorities, and next decisions; report proposed changes. |
| Record a decision | Apply an authorized deferral, reprioritization, incorporation, discard, merge, or reopening with its reason and source. |

Consultation and a read-only review write nothing: do not create the backlog, initialize, migrate (including preview), create input/scratch files, or generate Python caches. If absent, report that no backlog exists. For maintenance, apply only changes covered by the requested action or existing authority; accepting exact proposed changes is sufficient without redundant approval. Unaccepted choices remain proposals. Do not silently start another skill's writing or execution workflow.

## Capture and progressive refinement

For an authorized first write, create the file from [the backlog template](assets/backlog-template.md) after adoption/migration checks. Use its five sections: purpose/rules, opportunity register, refinement notes, decision history, and review/references. Adapt older bullet/priority layouts only within the requested maintenance scope; preserve existing content, IDs, source dates, references, and relative priority order. Historical checked boxes are not delivery evidence.

Search existing items, notes, and history for the same need before adding one. Enrich a clear match with the new dated source; when distinct intent matters and cannot be inferred, ask one consequential question. Allocate a new BNNN ID above the highest existing numeric ID, including retired or historical references; never renumber or reuse IDs. Preserve unresolved old ID collisions and request their scoped resolution rather than silently assigning new identities.

Capture a concise recognizable opportunity with its noted date and source. Record the problem, beneficiary, and expected value when known; unknown value, ownership, effort, or outcome alignment stays unknown. Do not require a complete story, acceptance criteria, estimate, technical design, or full interview to capture an idea. Keep original provenance when later evidence is added. Refinement notes use the existing ID and add only useful context: evidence, relevant OUT links, assumptions, dependencies, questions, or a reconsideration condition. Canonical priority and disposition remain in the register.

Keep P0 Critical, P1 High, P2 Medium, and P3 Low and preserve their existing relative order. Insert new items within the appropriate priority group; move an existing item only with explicit reprioritization. Default to **P2 provisional** only when priority is genuinely unspecified. Do not reinterpret existing P2 entries as evaluated or provisional without evidence. An evaluated or changed priority records a brief rationale/source in notes or history. Consider known value, urgency, risk, dependencies, and effort with the product decision-maker and relevant technical/stakeholder input; do not invent participants, scores, estimates, commitments, or a mandatory scoring method. Backlog ordering does not change approved roadmap priorities.

## Disposition and traceability

Keep one current register row per ID, including items no longer under consideration. Notes and history reference that ID; they do not become competing current definitions.

| Disposition | Meaning |
| --- | --- |
| Pending | Captured and still being considered or evaluated. |
| Deferred | Explicitly postponed; keep the reason and any known reconsideration condition. |
| Incorporated | A valid spec draft records the idea with a verified destination reference. |
| Discarded | Explicitly removed from consideration; retain the reason. |
| Merged | Its content is consolidated into an identified existing item. |

These are documentary descriptions, not controller statuses or gates. Preserve the item instead of deleting it. Significant priority/disposition/destination changes append date, ID, actual decision, rationale/evidence, and destination/source to history; editorial corrections need no event. Mark superseded notes clearly and reconcile the current row. A scoped reopening reuses the same ID and records why. If a destination later changes or drops the idea, review the affected mapping and record any authorized reopening or residual work rather than treating the old link as proof of coverage.

Distinguish two handoffs:

1. **Roadmap selection:** when the approved roadmap explicitly selects the release containing the opportunity, link the item to that release and its actual selection evidence. A projected version is only a projection; label any such reference accordingly. Selection alone does not make the item Incorporated.
2. **Spec incorporation:** after an existing spec draft validates and its actual content records the idea, mark Incorporated and link the release, spec path, and real US/AC IDs as applicable. Identify the destination as draft or currently approved from evidence. This does not require approval of the draft and does not establish implementation, acceptance, delivery, publication, deployment, or observed impact. Those facts remain with their canonical records.

Map each destination's contribution explicitly if several stories/releases cover the idea. For partial incorporation, keep Pending or Deferred with the residual need and mapped portion explicit; use Incorporated only once the whole recorded opportunity is represented. Split an item only within authorized refinement, retain the original and history, and link any new stable IDs. Reference US/AC definitions by actual spec path and IDs rather than copying them; use anchors only when they exist in that document. A missing/invalid destination leaves incorporation pending; do not create a spec or infer coverage to complete the backlog entry.

Roadmap owns strategic priorities, horizons, outcomes, release grouping and explicit selection; specify owns behavior/stories/acceptance; plan and tasks own implementation planning/actions. Optional discoveries from clarify/analyze/converge/review-release or operations may be captured within authority. An approved obligation or regression returns to its canonical owner and correction workflow; a backlog note does not defer it, change approved scope, or allow release closure. Deferral of approved scope requires its owner's approved change and downstream reconciliation.

## Maintenance and handoff

Review relevance, duplication, evidence, known priority rationale, and next decisions at requested reviews or agreed triggers. Record only actual review dates, participants, decisions, and agreed cadence/conditions; do not invent a periodic schedule, automate follow-up, or discard items solely because of age. Keep distant options broad and refine near-term candidates enough for a roadmap/spec decision without predefining all future work.

Before handing off, check unique current IDs, provenance retention, supported priority/disposition labels, significant history, consistent notes/current rows, explicit partial coverage, and real target references with correct draft/approval/selection distinctions. Report the operation, changed IDs, priority/disposition, reason, verified links, and pending decisions. Consultation/review findings stay in conversation unless saving those results was authorized.

This adaptation draws on [PMI's backlog management strategies](https://www.pmi.org/microsites/disciplined-agile/agile/backlogmanagement), [Agile Alliance's product backlog](https://agilealliance.org/glossary/backlog/) and [refinement guidance](https://agilealliance.org/glossary/backlog-refinement/), and [the Scrum Guide](https://scrumguides.org/scrum-guide.html#product-backlog). It applies their principles to Spec-Flow's deferred-opportunity channel, not a duplicate product-work registry or an official template from those sources.

## Runtime discipline

Resolve <plugin-root> from this installed SKILL.md. Run `python3 -B <plugin-root>/scripts/spec-flow.py --root <project> OP --input <json-file>`. For read-only queries, use existing input files or stream JSON through `/dev/stdin` on the supported POSIX host; use Git reads such as `git --no-optional-locks status --short` without refreshing the index. Inspect adoption/legacy state without writing; optional `status` with {} reports state or a diagnostic without authorizing repair. For read-only requests, report missing adoption/required migration and keep the response diagnostic without setup or migration operations.

Before an authorized write in a legacy `.specs/NNN-name/` project, stop and follow the `migrate-preview` → human review → `migrate-apply` flow in `$using-spec-flow`; use `migrate-resume` after interrupted apply. For an authorized write in a new unadopted project, first run `initialize` with empty JSON input {}. Do not silently convert historical approvals or checked boxes.

Backlog is plain Markdown: it has no controller document kind, contract block, generated progress, revision/approval receipt, or gate. Do not run validate/digest/approve on backlog.md or invent a `backlog` gate. To check existing roadmap/spec destinations, use read-only `validate` and `digest` with their supported project-relative paths. When claiming current approval, inspect the actual latest exact-digest receipts for the document and its dependency closure; file validation alone does not establish approval. Missing/failed evidence limits the claim, not basic idea capture. Roadmap/spec writing and phase gates stay with their owner skills. Registry approval of exact decision content controls those gates; backlog rows, checked boxes, and displayed statuses do not.

The backlog is a side channel and gates nothing. It never bypasses migration or approval of release work.
