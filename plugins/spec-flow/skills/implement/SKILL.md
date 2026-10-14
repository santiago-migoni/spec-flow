---
name: implement
description: "Execute an authorized release phase through native Sol-Luna delegation, verified tasks, independent phase review, and a validated commit."
---

# Spec-Flow: Implement

<HARD-GATE>
Require a migrated/adopted project, current registry approvals for the exact release spec, plan, tasks, and their strategic dependencies, and explicit execution authorization covering the selected phase. Run the controller gate and release validator; Markdown status and generated checkboxes are not authority. Production execution requires an isolated linked Git worktree, a persistent controller owner, available native Codex delegation, and attested Sol high orchestration. If any check fails, stop with its cause. Do not implement against legacy .specs/NNN-feature-name artifacts.
</HARD-GATE>

## Scope and roles

The release lives in `.specs/release-vX.Y.Z/`. The approved tasks contract is the executable source. Sol high owns the run and reviews each task; one Luna high implementer works on one scoped task at a time; a distinct Sol high reviewer assesses the integrated phase before its commit. Use the native adapter in `harness/adapters/codex/README.md` and the role files. Python does not spawn models. Never substitute a model silently. If the calling chat is not Sol high, hand actual orchestration to an attested Sol high child.

Default to one authorized phase per invocation. An explicit user authorization may cover several phases, but every phase must still close with its own independent review and validated commit before the next phase begins. Reuse authorization within its exact scope; do not ask again for each task.

## Process

1. Read controller status, approved source digests, plan phase dependencies, and actual Git state. Select the first ready task in the first unfinished authorized phase. If a prior attempt or commit may have happened during an interruption, reconcile it before doing new work. Preserve unrelated edits; stop if they cannot be separated.
2. Ask the controller to prepare one immutable, bounded task packet. It contains the selected task and steps, selected acceptance criteria, applicable shared decisions, exact source digests, expected checks, and allowed paths. A packet that cannot fit without losing a governing rule blocks delegation.
3. Spawn one Luna high child with isolated history. Bind its native agent identity and real host session attestation to this attempt. The child edits only authorized files and returns changed paths, actual work, test observations, and unresolved questions. Do not trust a claimed PASS or model string.
4. Record the result. Have the controller verify specified commands or concrete inspections on the actual code and capture outputs and code fingerprint. Sol reviews the diff against approved criteria. Close the task only with current verification and a passing review; the controller updates generated progress. Do not manually mark checkboxes.
5. On failure, give Luna the observed failure, a new hypothesis, and a targeted check. The first attempt plus at most two corrections are allowed. Stop and escalate when the limit is reached or a decision change is needed. A decision change returns to the owning canonical document; only affected downstream approval pins are reconsidered.
6. When all tasks in the phase are closed, confirm the phase's acceptance and constitution checks. Stage only phase files, generated task progress, and any prior pending compact audit receipt. Inspect the staged diff. Ask a distinct attested Sol high reviewer to assess that stable diff and controller evidence. If the staged tree changes, obtain a new review.
7. Commit exactly the independently reviewed staged tree with a Conventional Commit and the controller's run/phase identity. Record the verified SHA as a compact phase receipt. That receipt may remain the sole pending audit change until the next phase or final audit checkpoint. Never start the next phase on closed tasks alone; it requires the prior phase's reviewed commit.
8. Report task IDs, observed verification, reviewer outcome, commit SHA, and next authorized phase. After the final phase, query evidence-based completion and hand off to `$converge`.

## Recovery and limits

Before replaying an interrupted attempt, inspect the native agent status and worktree. Use controller resume/reconcile: accept an actual completed result with evidence or retry with reason and hypothesis. If a Git commit succeeded before its receipt was recorded, identify the unique matching run/phase commit and adopt its SHA once; do not commit twice. Ambiguous or changed state stops for reconciliation.

Use observed acceptance flows where executable. For prompt or documentation work with no executable surface, provide a specific inspection against expected behavior; run any partial executable surface. Never run destructive or irreversible verification actions without the authorization already required for them. Push, merge, publication, and deployment remain separate decisions.
