---
name: converge
description: "Assess a committed release against approved acceptance and shared decisions, then route residual work to its canonical source."
---

# Spec-Flow: Converge

<HARD-GATE>
Require an adopted release with valid spec, plan, and tasks; current registry approvals; at least one verified implementation pass; and reviewed phase commits for all phases claimed complete. Run the controller gate and evidence-based `complete` query; proceed to technical convergence only when `technical_complete` is true. The query also reports `release_review_pending` and `audit_pending` for the later closure steps. Checked boxes or a Markdown Converged label alone do not satisfy this gate.
</HARD-GATE>

## Assessment

Read the release's acceptance IDs, edge cases, non-goals, plan deliverables, task evidence and phase commits, and applicable constitution and technical decisions. Inspect only code and interfaces within the approved scope. Use the controller's real verification results and current code, not an agent's PASS claim. Classify gaps as missing, partial, contradictory, or unrequested. A constitution MUST violation is CRITICAL. A clean result has zero findings.

Report findings in the conversation using `assets/convergence-report-template.md`. Do not write application code, retry a task, or spawn Luna from this skill. For an implementation gap, propose a concrete task with stable ID, phase, AC references, steps, expected verification, closure, and file scope in the canonical `tasks.md` contract. Do not create a second editable gap list. If the gap changes behavior or acceptance, return to `$specify`; if it changes solution, return to `$plan`; if it changes shared design or priorities, return to that strategic document. Show the proposed decision change before applying it. An exact recommendation accepted verbatim can serve as the user's approval; open-ended wording needs review. Revision and approval changes affect only dependent decisions that actually adopt the new base.

When residual work is approved and added to its canonical source, hand execution back to `$implement` under the appropriate authorization. A subsequent convergence pass inspects the new code and evidence. This skill never fixes the gap itself.

## Clean outcome

If no gaps remain, leave `tasks.md` and approved decision content unchanged. Report the read-only controller result from `complete.technical_complete` in the conversation, citing the release, reviewed phase commits, and current evidence. Do not write a separate convergence document or generated closure note; `$review-release` records the combined derived release outcome after the technical review. Technical convergence does not prove impact or authorize publication.
