---
name: finishing-branch
description: "Finish a reviewed Spec-Flow release branch through final checks, audit checkpoint, and an explicitly authorized integration choice."
---

# Spec-Flow: Finishing Branch

<HARD-GATE>
Require evidence-based task completion, independently reviewed and committed implementation phases, technical convergence, and the release review recorded in the spec's derived section. Verify current source digests, task evidence, phase receipts, and the closed run's final audit checkpoint. `release-review` already releases controller ownership after recording that checkpoint. A generated checkbox or status label is insufficient. Production execution and phase commits require the isolated linked Git worktree. If a required condition fails, stop with the owning phase to resolve it.
</HARD-GATE>

## Prepare a reviewable result

Run the consuming project's required test suite on the final release state and record actual results; zero executed cases do not count as a passing suite. Check the branch diff and worktree for unrelated edits or secrets. Read the consuming repository's AGENTS.md and release conventions before touching version or release notes. Update its changelog only when those conventions call for it; do not create or edit a forbidden changelog. Change a package version or publish only when that action is explicitly authorized. Keep any release metadata changes in the commits required by the consuming repository's process.

Verify the final audit checkpoint created by `release-review`. That operation captures the last phase receipt, derived spec/roadmap records, and release-review event in exactly one audit-only commit, then releases controller ownership. Do not create a second housekeeping commit or receipt for that audit commit. Generated state and bounded packets may remain local; compact events, receipts, and evidence needed to assess the release stay tracked. The code-phase commits must still match their independently reviewed staged trees.

Present the resulting release version, passed checks, phase commit SHAs, audit checkpoint, and proposed integration action. Reuse any explicit integration authorization the user already gave for this exact branch and destination. If that authority is absent, ask for a choice after the concrete result is ready: keep the branch, merge locally, or push and create a PR. Execute only the chosen action. For discard, show the exact branch/commit range and require explicit confirmation before deletion. Re-run relevant tests after a merge. Never force-push without an explicit request.

A planned release identifier such as `v2.0.0` does not by itself authorize a package version change, publication, or deployment. Report which of those actions, if any, were actually authorized and completed.
