---
name: implement
description: "Execute an authorized release phase through native Sol-Luna delegation, verified tasks, independent phase review, and a validated commit."
---

# Spec-Flow: Implement

<HARD-GATE>
Require a migrated/adopted project, current registry approvals for the exact release spec, plan, tasks, and their strategic dependencies, and explicit execution authorization covering the selected phase. Run the controller gate and release validator; Markdown status and generated checkboxes are not authority. Production execution requires an isolated linked Git worktree, a persistent controller owner, available native Codex delegation, and attested Sol high orchestration. If any check fails, stop with its cause. Do not implement against legacy .specs/NNN-feature-name artifacts.
</HARD-GATE>

## Scope and roles

Build verifiable increments for the authorized release in `.specs/release-vX.Y.Z/`. The approved tasks contract is the executable source. Sol high owns the run and reviews every task; one Luna high implementer works on one scoped task at a time; a distinct Sol high session reviews the integrated phase. Python does not spawn models. Never substitute profiles silently; if this chat is not Sol high, hand actual orchestration to an attested Sol high child.

Use the [native adapter](../../harness/adapters/codex/README.md), [execution contract](../../harness/contracts/execution.md), and [implementer](../../harness/roles/implementer.md), [orchestrator](../../harness/roles/orchestrator.md), and [reviewer](../../harness/roles/reviewer.md) instructions. Keep one persistent owner and the common-directory ownership registration. Default to one authorized phase; wider explicit authorization is reusable within its scope, with independent review and validated commit between phases. Do not ask again for each task.

## Execution readiness

Before invoking `spec-flow.py`, read [shared controller operations](../../harness/contracts/operations.md) for CLI/query and completion-check boundaries; follow the adapter's concrete execution payloads. Inspect status, approved source digests, authorized scope, phase dependencies, host capabilities, actual Git/worktree state, and relevant current checks before start/resume. Reconcile possible prior attempts or commits first. Preserve unrelated edits; stop if they cannot be separated.

Review the plan/task maps and coverage against their canonical records, including partial/final intent and NFR targets. A mismatch returns to `$plan` or `$tasks`; do not patch missing requirements into a delegation prompt. These semantic/coherence checks are agent review, not automatic Markdown validation by the controller. Reuse current baseline evidence; run additional baseline checks when needed to establish the actual starting state.

## Task selection and retained context

Select the first ready task in the first unfinished authorized phase. Use `prepare` for one immutable, bounded packet with its canonical task/ordered steps, relevant ACs, governing decisions, source digests, checks, and explicit files. Task prose/tables are omitted; confirm all operative constraints and quality definitions survive in canonical fields or retained approved sources. Dependency files in context do not expand the current task's write permission. Missing or oversized essential context blocks delegation.

Provide the packet and implementer role with isolated history (`fork_turns: "none"`), the exact Luna high profile, returned `native_task_name`, and `SPEC_FLOW_PACKET_SHA256=<packet_sha256>` marker. Bind the real child/session identity using `bind-agent` and adapter attestation before accepting its result. A claimed profile or PASS is not evidence.

## Incremental construction and quality

Luna inspects current scoped code, follows ordered steps, and makes small changes with relevant tests/checks during construction. Use TDD/ATDD where appropriate to the change; an initial failing development test is distinct from passing formal closure verification against the resulting state. Include relevant error, quality, integration, and regression behavior from approved sources. Documentation/configuration work uses proportionate executable checks and specific inspections where applicable. Do not add unrelated cleanup or widen scope to solve a new decision.

## Verification and acceptance

Record the real result with the existing `summary`, `files_modified`, `checks`, `evidence`, and `blockers` fields. Retain task/attempt identity through the existing packet/controller context; do not add result or operation fields or acceptance states. Have the controller run canonical commands or capture concrete inspections on the actual worktree, with outputs and code fingerprint. Verification commands must leave project code unchanged. Missing evidence, recognized empty suites, failures, and unresolved blockers cannot close a task.

Sol compares expected and observed behavior, actual diff, scope, AC/NFR conditions, and applicable constitution rules. Exit zero and nominal AC membership do not establish semantic acceptance; check what cases ran and what they prove. Distinguish partial contribution from final verification according to plan/tasks. T-001 may close its verified enabling contribution while AC-001 remains pending T-002's final check. Record that distinction in existing summary/review evidence. A constitution MUST conflict blocks closure. Only `verify` → passing `review` → `close` establishes task completion; generated checkboxes are views.

## Integration and current evidence

Check that successive changes work together, including relevant acceptance flows and regressions within authorized scope. If later work changes files relevant to completed tasks, inspect evidence freshness and use `refresh-evidence` for affected completed tasks before relying on it at dependencies or phase review. Inspect refreshed expected/observed results. This reruns checks, not implementation; it neither reopens work nor grants new task credit or bypasses phase review/commit. A failed refresh blocks advancement until correction follows an authorized route; do not edit closed work ad hoc or relabel stale evidence.

Local integration checks and phase commits do not alone establish continuous integration into main. Main-branch integration remains with `$finishing-branch` under its own authorization.

## Failures, blockers, and decision changes

| Finding | Required response |
| --- | --- |
| Defect within approved scope | Use observed failure, a concrete hypothesis, and a targeted check; follow the controller transition for the current verification/review state. |
| Environment or dependency problem | Diagnose and repair only within authorized scope; retain the blocker if a required check cannot run. Do not substitute an inspection to conceal it. |
| Missing context or incoherent decomposition/checks | Return to `$tasks` or the owning source; restore sufficient approved context before affected execution. |
| Changed behavior, solution, or shared decision | Return to `$specify`, `$plan`, or the shared owner respectively, with affected approval pins inspected/adopted explicitly. |
| Exhausted correction limit | Stop and escalate the unresolved issue with evidence. |

A failed verification uses `retry` with reason/hypothesis before `prepare`; a task review of `changes` already sets needs_changes, so prepare its next attempt without an invalid retry call. Correction edits require the newly prepared packet and proper binding, not more edits to a verified/reviewed attempt. The first attempt plus at most two corrections are allowed. At the limit, an active `verification_failed` task can use explicitly authorized `abandon` after the controller attests its bound child as terminal; this records the unresolved failure and releases ownership without completion credit. Earlier failures and other active states retain their reconciliation requirements. Do not reset limits through a new agent/session, interruption, or abandonment. Stop affected work on a decision conflict; a failed gate never permits bypass. If approved sources change during an open run, reconcile active execution and use the recorded, authorized `abandon` flow before a new run with approved/adopted bases and applicable execution authorization. Preserve history; reconsider only affected dependent decisions, without continuing a stale run.

## Independent phase review and commit

When phase tasks are closed, inspect integrated deliverables, applicable quality/constitution checks, current evidence, and the contributions/final checks scheduled for this phase. Do not require future-phase AC completion or claim it prematurely. Use `phase-ready` to stage exact phase/generated-progress/audit paths and pin the stable parent/tree/diff. Preserve the controller's compact audit rules and unrelated changes.

Send the phase packet, actual diff, criteria, and current evidence to a distinct attested Sol high reviewer with isolated history, returned `native_task_name`, and exact phase marker. Record its passing verdict with `review-phase`. An implementation/tree change invalidates that review and requires current affected evidence and a new review through a valid controller transition. If the phase is already reviewed/committed and the controller blocks new preparation, stop and reconcile the authorized recovery/restart path; refresh cannot reset phase state or repair commit validity. Use `commit-phase` to commit exactly the reviewed tree with a Conventional Commit and run/phase identity; record the verified SHA/receipt. A receipt may remain the sole pending audit change for the next phase or final checkpoint. The next phase requires the reviewed prior commit, not closed tasks alone.

## Recovery and continuity

Before replaying interrupted work, inspect native agent status, actual files, controller state, and possible side effects. Use resume/reconcile; a missing final message is not proof no work occurred. An unbound possible child requires native inventory/log inspection under the adapter rules before a no-spawn claim. Restore a missing task/phase packet with `restore-packet` only when current pins reproduce its recorded hash; restoration does not reset attempts/bindings. Corrupt, ambiguous, or unrecoverable state blocks advancement.

If a commit succeeded before its receipt, use controller recovery to identify and adopt the unique matching run/phase commit once. Do not repeat commits, remove audit history, or regenerate decision context manually. Stop when ownership, authorization, or a gate is unresolved.

## Communication and handoff

Report observable capability, task/phase IDs, partial/final acceptance demonstrated or still pending, actual verification/evidence, limitations/blockers, independent reviewer outcome, verified commit SHA, and next authorized action. Demonstrate approved executable flows where applicable, without unapproved external effects. Reports derive from actual work and controller evidence; do not create a second editable progress registry or claim measured impact from task counts.

Stop at the authorized boundary. After the final phase, query `complete`: hand off to `$converge` only when `technical_complete` is true, reporting any release-review/audit items for their later stages. The subsequent path remains `$converge` → `$review-release` → `$finishing-branch`; implement does not perform their closure or infer publication. Push, merge, publication, and deployment retain separate authorization. Never run destructive or irreversible verification without its required authorization.

This adapts [PMI's incremental construction](https://www.pmi.org/microsites/disciplined-agile/construction-goals/produce-a-potentially-consumable-solution), [PMI/Agile Alliance execution practices](https://www.agilealliance.org/wp-content/uploads/2021/02/AgilePracticeGuide.pdf#page=71), and [DORA's integration](https://dora.dev/capabilities/continuous-integration/) and [peer review](https://dora.dev/capabilities/streamlining-change-approval/) to Spec-Flow's existing controls; those sources do not prescribe its model profiles or attempt limits.
