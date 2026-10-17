---
name: review-release
description: "Review a finished release against its acceptance criteria, its measurement plan, and the feedback received, before branch finishing."
---

# Spec-Flow: Review Release

<HARD-GATE>
Require that every task of the release is complete: each step's verification passed, as recorded in `tasks.md` and the implementation report. Require current approvals for the release spec, plan, and tasks by running `gate` with `{"phase":"implement","release":"vX.Y.Z"}`; it must report ready. If any task is incomplete or any approval is stale, stop and direct the remaining work to `implement`, `tasks`, or `plan`. Do not treat merging, publishing, or deploying as implied by a finished review.
</HARD-GATE>

## Purpose

Check what the release actually delivers, what users said about it, and what it changed. Keep three things apart: the acceptance criteria met, the code integrated, and the user or business results observed. Passing tests and finished tasks do not show measured impact.

## Steps

1. **Acceptance.** For each story in `spec.md`, check each acceptance criterion against the real behavior: run the relevant flow, or review the evidence from the implementation report. Mark each criterion met, not met, or not verifiable, with the evidence.
2. **Feedback.** Record who saw the release, what they said, and whether they accepted it. Do not invent acceptance or attendees. If feedback is missing and the spec requires it, say so and stop short of closing.
3. **Outcomes.** Read the measurement plan in `spec.md` and the outcomes it references in `roadmap.md`. Report what has been observed, the source, the period, and the limits. If the measurement has not run yet, say so; do not infer the result from delivery.
4. **Findings.** Sort each finding as one of: a criterion not met (return to `implement`), a changed need (route to `roadmap` or `backlog`), or an optional improvement (route to `backlog`). Do not change acceptance or scope here.

## Output

A conversation report, not a file. Use these sections, in this order:

- **Release and bases:** version, approved documents, and the implementation state.
- **Acceptance:** each story and criterion, its status, and its evidence.
- **Feedback:** who, when, what, and whether accepted.
- **Outcomes:** observed values against the plan, or "not yet measured".
- **Findings and routing:** each finding with its destination.
- **Verdict:** ready to finish, or blocked with the owning next step.

## Boundaries

This skill does not push, merge, publish, deploy, or change the package version. Those belong to `finishing-branch` and need the user's explicit instruction.
