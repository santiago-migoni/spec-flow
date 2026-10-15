---
name: finishing-branch
description: "Finish a reviewed Spec-Flow release branch through final checks, audit checkpoint, and an explicitly authorized integration choice."
---

# Spec-Flow: Finishing Branch

<HARD-GATE>
Require evidence-based task completion, independently reviewed and committed implementation phases, technical convergence, and the release review recorded in the spec's derived section. Verify current source digests, task evidence, phase receipts, and the closed run's final audit checkpoint. `release-review` already releases controller ownership after recording that checkpoint. A generated checkbox or status label is insufficient. Production execution and phase commits require the isolated linked Git worktree. If a required condition fails, stop with the owning phase to resolve it.
</HARD-GATE>

## Purpose and distinct actions

Verify the original release closure, prepare the requested branch action, and assess its actual result. Use [the report template](assets/finishing-report-template.md) for conversation output, with references to existing Git/PR/CI and release evidence rather than a new editable closure report or progress registry.

| Action | What completion demonstrates |
| --- | --- |
| Release closure | Current reviewed implementation, confirmed convergence, recorded release review, and valid original audit checkpoint. |
| Integration | Changes incorporated into the authorized destination and the resulting state verified. |
| Publication | The authorized version/artifact is available in its intended channel, with actual evidence. |
| Deployment | The authorized solution is installed/activated in the intended environment and its operation checked. |

Keeping a branch or opening a PR may fulfill the chosen action, but neither proves integration, publication, or deployment. A planned identifier such as v2.0.0 proves none of them. Technical closure also does not establish measured user/business impact; retain review-release's separate measurement follow-up.

## Verify the original closing state

Identify the consuming repository, release/run, source branch/worktree and SHA, approved bases, task evidence, reviewed phase commits, confirmed `$converge` result, and actual `$review-release` record/audit SHA. Read its AGENTS.md and release conventions. Inspect the index, worktree, branch diff, unrelated edits, and secrets without exposing sensitive content. Preserve other work and stop if it cannot be separated.

On the clean source closing state, run the read-only gate for finishing-branch and `complete` for the exact release/run following [the execution contract](../../harness/contracts/execution.md). Require `gate.ready=true`, `complete.technical_complete=true`, `release_review_pending=false`, and `audit_pending=false`. Missing results do not pass. `complete=true` alone checks technical completion, not final audit closure. Confirm the actual generated records and receipts, unique audit commit at source HEAD directly after the last reviewed phase, and the phase commits' original SHA/parent/tree/history. Any unresolved convergence finding blocks entry.

Run the consuming project's required test suite on that final source state and record checks, conditions, actual results, and the SHA tested; zero executed cases do not count as a passing suite. Checks must leave the reviewed state intact. New gaps or required source changes return to their canonical owner and authorized execution/recovery before integration.

`release-review` already captured the last receipt, generated records, and event in one final audit-only commit and released controller ownership. Keep compact events, receipts, and durable evidence tracked; generated state/bounded packets may remain local. Do not start another implementation run just to integrate, reopen closed phases, create a second housekeeping/audit commit or receipt, or manually rewrite the closure.

## Prepare the destination and authorization

Identify the actual destination repository/branch/current SHA, relevant divergence and changed files, intended integration method, and applicable branch protections, reviews, required checks, and merge-queue rules. Do not assume main, ignore destination policies, or bypass checks. A passed source suite does not demonstrate compatibility with a changed destination.

Prepare the concrete diff/range, source checkpoint, destination, method, checks, and proposed action before asking for missing authority. Reuse explicit authorization for this exact branch/destination and action within its scope; do not ask again unnecessarily. If absent, ask for the choice on the prepared result: keep the branch, merge locally, or push and create a PR. One clear authorization may cover multiple actions; authority for one does not imply authority for the others. PR creation/push does not imply permission to merge it or publish/deploy.

Keep the source closing branch/checkpoint unchanged. Where candidate preparation or integration testing needs changes, use a separate suitable context respecting repository/host worktree ownership and managed-worktree tools. Do not overwrite another worktree or append destination updates to the frozen source. If the destination advances, recheck the candidate, applicable review/check requirements, and affected tests before continuing within authorization.

## History-compatible integration

| Method | Treatment with the current controller |
| --- | --- |
| Fast-forward | Use when possible and permitted; retains original reviewed commits and audit checkpoint. |
| Merge retaining the original commits | Use when permitted; identify/review the resulting combination and run relevant integration/regression checks. |
| Squash or rebase | Do not automatically rewrite the reviewed history or treat replacement commits as satisfying the original receipts. |

Preserve the exact original phase commits and audit checkpoint as reachable history. A SHA correspondence note does not replace the controller's original ancestry/parent/tree checks. If destination policy permits only an incompatible method, preserve the branch and report the concrete blocker; a supported preservation/equivalence protocol requires separately approved work. Do not change protections, fabricate receipts, or force-push as a workaround. Never force-push without an explicit request.

## Verify integration and recover interruptions

Execute only the selected authorized action. Record the destination before/after SHAs, method, actual push/PR results, and relationship to the original phase/audit commits. After merging, inspect the resulting diff and run relevant tests and destination-required checks on the integrated SHA. Preserve evidence that the original commits remain in history. An open PR, pending CI, successful Git command, or passing source tests alone cannot establish verified integration.

Review conflict resolutions and their effects before claiming the combined result passed. Resolve conflicts only within authorized scope; obtain the repository-required review and current checks for the resulting candidate. Passing post-merge tests do not automatically renew the original semantic convergence for changed behavior. New behavior, solution decisions, or implementation beyond integration scope return to `$specify`, `$plan`, `$tasks`, or the appropriate shared owner and authorized implementation; do not patch the closed release ad hoc.

If integration/checks fail, report the exact state and unresolved checks, preserve evidence, and use only an authorized recovery path. Do not silently reset/revert shared work or continue into publication/deployment on a failed result. After interruption, inspect local/remote refs, pending merge/conflicts, actual destination SHA, existing PR/action results, and worktrees before retrying. A missing final response does not prove no side effect occurred; uncertainty or mismatches block replay until reconciled.

Validate the source closure in its original context and the integrated result separately. A legitimate merge can have a different destination HEAD; the controller's audit-at-HEAD condition may then report pending on that destination. Do not interpret that alone as erased historical closure or use the old run to certify the new tree. Keep the actual source-check result tied to its checkpoint and report the separate integration evidence; never rerun `release-review` or add another audit to make the new HEAD appear closed.

## Version, publication, and deployment

Distinguish release identifier, package version, tag, published artifact/channel, and deployed environment. Follow the consuming repository's metadata/commit rules. Update a changelog only when those conventions call for it; do not create or edit a forbidden changelog. Version changes require explicit authorization. Metadata belonging to the reviewed release state must be prepared through the owning approved work before its closure/audit; do not append it to an already closed source branch. If such changes are discovered here, route them before advancing against revised bases.

Metadata belonging to a later authorized publication follows that separate repository procedure, commits, and checks while retaining the original closure as history. Creating a tag, publishing, or deploying requires its own explicit scope, which may already be included in a broader authorization. Use actual repository procedures rather than inventing publication/deployment skills. If authorized, verify version/artifact/source identity and actual channel or environment results; report each action independently. Otherwise leave it unperformed/pending without implying that integration authorized it.

## Report and preserve traceability

Report release/run, source branch/worktree and tested SHA, original phase commits/audit checkpoint, destination before integration, selected method and authority, resulting SHA/PR, checks tied to the state tested, blockers, and each action's actual outcome. The controller persists the original closure only; integration/publication/deployment evidence remains in its actual Git/platform/repository records and the conversational report. Do not invent controller fields or change the closed review's impact/delivery flags to describe later actions.

Separate source closure verified, branch retained, PR open, integration performed but checks pending/failed, integration verified, publication verified, and deployment verified as conversational descriptions rather than new controller statuses. Report uncertainties and retained resources, and identify the next authorized action without claiming an unperformed step complete. A correct final integration does not itself establish frequent integration throughout development.

## Cleanup and discard

Clean up branches/worktrees only within authorized scope after checking actual integration/PR state and preserving work/evidence. Inventory tracked, untracked, and relevant ignored/local files; preserve needed content before any removal. Verify original phase/audit commits remain durably reachable and compact evidence is retained. Use the host's managed-worktree mechanism where applicable and leave unrelated/owned-by-others work untouched.

Keep required resources when a PR/check is pending, local changes remain, or preservation is uncertain; report what is retained and why. Cleanup is distinct from discarding unintegrated work. For discard, show the exact branch/commit range and require explicit confirmation before deletion; integration authority does not supply that confirmation.
