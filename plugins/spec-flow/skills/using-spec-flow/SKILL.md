---
name: using-spec-flow
description: "Use when entering or resuming Spec-Flow, asking for project status, or choosing the next authorized document or delivery step."
---

# Spec-Flow: using-spec-flow

<HARD-GATE>
Inspect project configuration and `.specs` first. If legacy `.specs/NNN-name/` folders exist, stop before writing and follow the actual `migrate-preview` → human review → `migrate-apply` flow in [the migration contract](../../harness/contracts/migration.md); resume an interrupted apply with `migrate-resume`. There is no `migrate` CLI operation. For a new unadopted project, run `initialize` with empty JSON input `{}` first. Run the runtime gate for the intended document or execution phase and obey it; using-spec-flow itself is not a gate kind. Urgency never waives a failed gate.
</HARD-GATE>

## Purpose and entry mode

Coordinate intent, observed project state, and the next authorized owner/action. Preserve this path: `constitution → design (applicable shared system design) → roadmap → specify → plan → tasks → implement → converge → review-release → finishing-branch`. Clarify/analyze are optional side channels; backlog is independent. Iteration returns changed decisions to their owner while retaining dependencies and gates. The owning skill drafts/applies/records approval; the controller enforces its supported gates and execution protocol. Bootstrap itself does not rewrite or approve canonical artifacts.

Classify the request before setup, migration, or phase operations. The hard gate's initialization/migration requirements apply before authorized writing; its phase gate requirement applies to the intended gated document or execution phase. Consultation remains read-only even in an unadopted or legacy project.

| Mode | Intent | Operational boundary |
| --- | --- | --- |
| Consultation and diagnosis | Explain, inspect, review, or recommend what comes next. | Read/query only; no file creation, setup, migration (including preview), repairs, evidence refresh, task execution, or saved report. |
| Documentary editing | Create/revise an identified document within the request. | Check adoption and the owner's applicable gate; route the authorized edit to that skill. Document approval and execution authorization remain separate. |
| Execution | Implement an approved release/phase. | Check current sources, full-release coverage, explicit execution scope, and native prerequisites; use `$implement` and its contract. |
| Resumption | Continue existing documentary work, execution, or closure. | Recover the actual draft/run/checkpoint and authority first; use the matching owner/recovery path without restarting or replaying by assumption. |

For a mixed request, keep each action in its actual mode and scope. A status question grants no repair or execution authority. Reuse valid prior decisions and authorization without another interview or permission request; a generic continuation does not expand their scope. Ask one consequential question when an essential root, release, choice, or authority cannot be recovered. Do not invent missing human decisions, metrics, participants, dates, or commitments.

## Inspect the relevant current state

Inspect only what the requested mode needs. Basic consultation or backlog capture does not require all strategic/release documents. Establish the actual project root before mutations; preserve unrelated work. Recover as applicable:

- Requested purpose/outcome and scoped action; project adoption, legacy folders, or interrupted migration.
- Relevant `.specs/{constitution,architecture,infrastructure,structure,roadmap}.md` and `.specs/release-vX.Y.Z/{spec,plan,tasks}.md`; strict numeric SemVer and actual document revisions.
- Explicit roadmap selection and outcome references; projected/planned status, array order, version number, or folder existence does not select a release. Reuse an existing current human selection; ask if none is determined.
- Current decision digests, exact dependency pins, and latest approval receipts across the relevant closure, not only the leaf document. File validation, displayed status, checked boxes, and urgency do not establish approval or execution authority.
- Existing run/owner, authorized phases, active task/agent, results, checks, reviewed phase commits, and pending closure; branch/worktree/changes when relevant to the action.

Report unavailable/failed/mixed evidence and the resulting limits. A failed prerequisite blocks dependent work, not unrelated authorized reading. Do not manufacture future documents to make a query pass, restart strategy for unchanged valid bases, or silently repin approved descendants. Structural/nominal controller validation is distinct from semantic sufficiency, coherent Markdown tables, planned coverage, and demonstrated behavior; owner skills retain those reviews.

## Route from observed conditions

Use the row matching the request and actual evidence. In consultation, destinations below are recommendations only; do not perform the described writes.

| Observed condition or requested decision | Owner / next action | Required evidence and transition boundary |
| --- | --- | --- |
| First authorized write in a new project | Adoption, then the relevant owner | `initialize` with {} before writing. Missing strategy alone does not prevent consultation or independent backlog capture. |
| Legacy project or interrupted migration needs writing | Migration workflow | Follow [the migration contract](../../harness/contracts/migration.md): exact committed originals, explicit mapping, reviewed candidates, `migrate-preview` → human review → `migrate-apply`; `migrate-resume` for interrupted apply. Never infer mapping or import old checkboxes as authority. |
| Purpose/principles/boundaries need a decision | `$constitution` | Recover human direction and existing valid bases; gain current approval before dependent writing. |
| Applicable shared system decisions need work | `$design` | Choose architecture/infrastructure/structure scope and its existing gate; approve actually used sources first. Recommended architecture → infrastructure → structure is flexible, with no reciprocal dependency cycles. |
| Priorities/outcomes/release grouping or selection need work | `$roadmap` | Current approved strategic bases; canonical releases/version table coherent; human selection distinct from projection and runtime active status. Distant opportunities may stay unversioned. |
| Selected-release behavior or an unapproved amendment needs work | `$specify` | Approved roadmap selecting the explicit version and current specify gate; bounded scope, canonical stories/ACs, quality, and coherent references before plan. Keep draft refinement here. |
| Consequential ambiguity in an approved spec | `$clarify` | Current approval of spec and dependency closure at entry; up to five questions per round, one at a time; blockers stay visible. Final amendment approval and downstream adoption remain separate. |
| Approved spec needs a delivery solution / approved plan needs executable decomposition | `$plan`, then `$tasks` | Each owner's gate/current approved bases. Plan owns solution/phases/verification strategy; tasks owns actions, files, steps/checks. Complete meaningful release AC/quality coverage remains required. |
| Optional documentary coherence assessment | `$analyze` | Read-only. Current approved spec/plan/tasks and closure, full-release validation and analyze gate. Failed entry is diagnostic-only; failed controls or CRITICAL findings block recommending implementation. Zero findings does not prove implementation or authorize execution. |
| Deferred opportunity to capture/refine/maintain | `$backlog` | No approved strategy/release prerequisite. Preserve BNNN IDs/provenance and explicit destinations. It has no document contract, approval receipt, or gate; no selection, scope waiver, or execution authority. |
| Approved release ready for authorized implementation | `$implement` | Adopted project, current approvals/pins, full-release validation, phase scope, native readiness and adequate retained context. Existing active work takes the resumption path first. |
| Active/interrupted execution or incomplete handoff | Existing owner via `$implement` recovery | Inspect status/native agent/worktree and actual result persistence. Reconcile before retry; a lost final message does not justify replay. |
| Reviewed phases technically complete | `$converge` | Current gate and `complete.technical_complete=true` enable assessment. Confirm only when every applicable obligation is demonstrated and zero findings remain, including LOW; missing evidence is Not verifiable. |
| Corresponding convergence confirmed, release review pending | `$review-release` | Current evidence and confirmed assessment. Keep rich report, supported persisted closure fields, and later follow-up distinct; pending/unavailable impact alone need not block technical closure. One final audit commit releases ownership. |
| Valid reviewed source closure and branch action requested | `$finishing-branch` | Current source eligibility, destination/action authority, and verified resulting SHA. Retained branch, open PR, integration, publication, and deployment are distinct outcomes. |

Shared design retains three canonical documents, templates in design/assets, per-document approvals, and existing controller kinds. Use only applicable design and approved sources actually used; omitting a pin does not make a document N/A. Record genuine N/A in roadmap. Preserve scoped revisions, verified versus proposed trees, and unchanged bases when design consolidation alone changes nothing.

## Resume the existing work

| Recovered work | Resume path | Preserve |
| --- | --- | --- |
| Initial or amendment documentary draft | Its owner; initial/unapproved spec amendments use `$specify`, not clarify on an old receipt | Existing content and pending decisions; R00 until first approval, existing amendment RNN while still in review. Do not increment again for each preapproval round. |
| Active/interrupted implementation | Existing authorized run and attested owner through `$implement` and [the execution contract](../../harness/contracts/execution.md) | Agent/attempt identity, actual worktree changes, current evidence, phase scope and prior commits. Inspect liveness/results before continuing. |
| Reviewed release with audit/integration/follow-up pending | `$review-release` or `$finishing-branch` at its actual checkpoint | Original reviewed phase/audit commits and closure history. Record later measurement at its planned source; do not rewrite or reclose the historical checkpoint. |

A request to resume permits only its recovered scope. A consultation about an interrupted run does not itself authorize mutable recovery. `resume`/`reconcile` rebuild/reconcile state; they are not status queries. Use the contract's actual payloads and preconditions, not invented operations:

- Missing task/phase packet: `restore-packet` with the same run/owner and task/phase ID requires current approved pins and the event-recorded hash. It preserves attempts/bindings; corrupt caches are not replaced and unavailable original timestamps remain diagnostic.
- Possibly running/lost child: inspect native inventory, host logs/markers, persisted results, and actual files before retry or another delegation. No-spawn reconciliation requires its fresh owner-scoped inventory/marker/baseline proof. Keep one persistent owner; ambiguous ownership blocks another controller.
- Changed approved source during an open run: reconcile the active attempt first, then use `abandon` only with recorded reason and explicit authorization before a new run on current approved bases. Reuse completed-task evidence only when exact task contract, pins, checks, and code fingerprint match; attempt limits carry across abandonment.
- Ownership transfer: `takeover` applies only to an interrupted run under its terminal-owner/child evidence and human reconciliation requirements; it does not expand authorized phases. Interrupted migration uses `migrate-resume`, not execution resume.

If the next phase exceeds authorization, report that scope boundary and obtain the missing decision before starting it. Existing authorization covering several phases stays reusable, with independent review and validated commit between phases.

## Changed decisions and learning

| Discovery or change | Canonical owner | Coordination consequence |
| --- | --- | --- |
| Purpose, principles, or boundaries | `$constitution` | Reassess affected strategy/release decisions. |
| Shared component, operational, or repository decisions | `$design` | Revise only affected perspectives and their actual dependents. |
| Priorities, outcomes, or release scope/selection | `$roadmap` | Keep canonical releases, projections and explicit selection coherent. |
| Behavior or acceptance | `$specify`; `$clarify` only at its eligible approved entry | Reconcile stories/ACs, examples/quality and affected downstream bases. |
| Solution, phases, or planned verification | `$plan` | Reconcile canonical phases, coverage and affected tasks. |
| Actions, files, checks, or retained execution instructions | `$tasks` | Reconcile executable contracts and evidence implications before implementation. |
| Optional future opportunity | `$backlog` | Preserve provenance and projection/selection/draft-incorporation distinctions; approved obligations require an approved scope change before deferral. |

Identify evidence, owning decision, affected descendants, and actual approval/adoption needs. Accepting exact proposed wording may supply scoped approval; record/validate through the owner rather than asking redundantly or approving unseen changes. Historical receipts do not approve changed content. Preserve unchanged sources and closure evidence; do not automatically regenerate the chain, widen an active run, or select another release.

Use feedback during implementation, release review, and later operation to inform the next authorized decision. Separate planned work, verified capability, delivery, observed/pending outcomes, and achieved targets. Refer to existing measurement sources and actual observations; do not invent metrics or schedule follow-up. Workflow policies may improve through authorized decisions while current controls remain in force.

## Conversation handoff

Return this compact checkpoint, proportional to the request. Label pending/unavailable evidence and proposed versus performed actions. In consultation, recommendations remain recommendations; report what the queries actually established. Keep it in conversation, without another status/approval registry, document, or controller schema.

| Field | Required content |
| --- | --- |
| Intent | Consultation, editing, execution, or resumption; identify mixed scope when needed. |
| Context | Actual project and selected release/run/revision only where applicable. |
| Observed state | Sources and query results actually examined; distinguish validation, approval, readiness, and technical completion. |
| Blockers / limits | Exact unmet condition, affected scope, missing/unavailable material; no fabricated readiness. |
| Next step | Concrete action and owning skill; distinguish proposed, authorized, performed, and waiting. |
| Authority | Existing applicable permission or the specific human choice still needed; separate edit, approval, execution, and integration authority. |

Example for a status question in an unadopted project: consultation; actual project; no adoption/documents found; no blocker to reading, adoption needed before future writing; propose `$constitution` after authorized initialization; consultation only, no setup or execution performed.

## Runtime and preserved controls

Before invoking `spec-flow.py`, read [shared controller operations](../../harness/contracts/operations.md) for strict consultation, adoption, phase queries, validation, and approval/revision mechanics. Bootstrap routes work; the owning skill retains its gate and permission boundary. Consultation uses only the shared query whitelist and creates no files. Exclude `complete`/check-complete from that mode; report recorded closure as historical and current technical completion, review/audit flags, and closure eligibility as not revalidated. Authorized owner workflows retain mandatory live completion checks.

Use the actual perspective kind for design; `using-spec-flow`, `design`, and `backlog` are not gate kinds. Bootstrap adds no contract fields, approval authority, release statuses, or canonical artifact. Preserve story/AC/phase/task ownership and coherent reference tables. Execution-critical instructions must survive in canonical task fields or retained approved context: tasks.md prose/tables alone do not reach implementer packets. Progressive planning does not waive full-release tasks/AC coverage.

Production execution requires an isolated linked Git worktree, writable common-directory ownership registry, native Codex delegation and readable host session logs: the attested orchestrator and single implementer match the run's pinned profiles, and a distinct session with the pinned reviewer profile reviews the integrated phase. Python never launches models; do not silently substitute profiles. Missing readiness yields a diagnostic, not fallback. Keep the three-attempt limit, native attestation, exact result fields, and source/evidence scope checks. Verification must not mutate code; stale completed-task checks use `refresh-evidence` under `$implement` without replaying implementation or task credit.

At each phase boundary, current closed-task evidence → `phase-ready` pinning the stable tree → independent configured-profile review via `review-phase` → matching `commit-phase`. A task `close` neither commits nor finishes the run. The next dependent phase requires its predecessor commit in current ancestry and its own scope authorization. After all phases commit and `complete.technical_complete=true`, assess through converge, then confirmed release review: converge writes no marker/generated closure; review-release persists only its supported fields/roadmap reference and one final audit commit, releasing ownership. `release_review_pending`/`audit_pending` describe remaining closure, not implementation permission.

Finishing-branch preserves original phase/audit commits, verifies source closure and destination/action authority, and checks the actual integrated SHA. Use permitted fast-forward or preservation merges; incompatible squash/rebase policy blocks integration pending a supported protocol. Preserve unrelated/ignored content, worktree ownership, and recovery checkpoints during cleanup. Execution authorization does not authorize push, merge, publication, or deployment; local phase commits do not establish CI into main or observed impact. Use [the execution contract](../../harness/contracts/execution.md) and [native adapter](../../harness/adapters/codex/README.md) for concrete operation payloads, role instructions, attestation, and recovery.

This coordination adaptation draws on [PMI's full delivery life cycles](https://www.pmi.org/disciplined-agile/lifecycle/) and [risk-based governance](https://www.pmi.org/microsites/disciplined-agile/agile/agilerisk), [Agile Alliance's iterative development](https://agilealliance.org/glossary/iterative-development/), [the Kanban Guide](https://kanbanguides.org/the-kanban-guide), and [Scrum.org's evidence-based management](https://www.scrum.org/resources/online-evidence-based-management-guide). Spec-Flow's release protocol remains its own governed workflow, not an official template or a replacement for those frameworks.

## Canonical document encoding

New source documents use YAML frontmatter; existing fenced JSON and mixed-format dependency chains remain supported. Consultation, initialization and resumption do not convert documents. Route an explicit conversion request to the document owner under [shared conversion controls](../../harness/contracts/operations.md#document-encoding-and-explicit-conversion), preserving approvals, revisions, downstream adoption, execution reconciliation and history. CLI input/output and internal records remain JSON.

Model/effort preferences belong to `.spec-flow/config.json`; follow [profiles](../../harness/contracts/profiles.md) and shared operations for authorized edits. New choices apply only to new runs. For resumption inspect stored profiles, not current defaults. Consultation does not call configure-profiles; profile changes do not authorize execution.
