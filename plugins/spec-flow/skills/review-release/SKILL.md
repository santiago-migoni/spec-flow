---
name: review-release
description: "Review a technically converged release's acceptance, observed impact, delivery state, and lessons before branch integration."
---

# Spec-Flow: Review Release

<HARD-GATE>
Require a release spec whose technical convergence is backed by current controller evidence and reviewed phase commits. Run the release-review gate. If tasks, verification, or convergence are incomplete, stop and direct the remaining work to the owning phase. Do not treat publication or deployment as implied by technical completion.
</HARD-GATE>

Read the approved roadmap outcome, the spec's AC IDs and measurement plan, current task/phase evidence, and the `complete.technical_complete` result reported by `$converge`. There is no separate technical-closure write; `release-review` records the combined derived technical and impact outcome. Distinguish three states: technical acceptance (verified behavior), delivery/integration (branch and artifact state), and real-world impact (measured result, pending measurement, or unavailable evidence). A technically complete release can retain pending impact measurement.

Call `release-review` to record the concise derived outcome in the spec's trailing generated section with evidence references, technical status, impact status, delivery state, limitations, lessons, and pending decisions. The controller also writes a roadmap reference and final audit-only commit. Do not make another generated-doc or audit commit afterward. Update the roadmap's release status as a reference to that closure when appropriate; do not copy the report into the roadmap or create a separate release review file. If a new priority, scope, architecture, or principle is proposed, route it to its canonical owner for human approval. A lesson is a proposal, not an automatic new task.

Report accepted behavior, impact status, and remaining action. Then hand branch integration to `$finishing-branch`. This skill does not push, merge, publish, deploy, or bump a package version.
