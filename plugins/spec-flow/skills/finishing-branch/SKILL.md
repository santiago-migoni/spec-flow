---
name: finishing-branch
description: "Finish a reviewed release branch: verify it is clean and passing, then carry out the integration the user explicitly chooses."
---

# Spec-Flow: Finishing Branch

<HARD-GATE>
Require a release review with a ready verdict in this conversation, or the user's explicit statement that the review is done. Require that the release's approvals are current, by running `gate` with `{"phase":"implement","release":"vX.Y.Z"}`. Do not run any integration action (merge, push, pull request, publication, or deployment) without the user's explicit choice of that action in this conversation.
</HARD-GATE>

## Steps

1. **Check the branch.** Identify the branch, its current commit, and the base it will integrate into. Run `git status` and confirm that the only changes are the release's intended ones. If there are unrelated changes, stop and ask the user how to handle them; do not commit or discard them yourself.
2. **Run the checks.** Run the test or verification commands the release's tasks define, and the project's own test command if it has one. Report each command and its outcome. Any failure blocks finishing.
3. **Offer the options.** Present the choices the user can take, with the consequence of each:
   - Keep the branch as it is.
   - Merge into the base locally, preserving commits (fast-forward when possible).
   - Push the branch and open a pull request.
   - Discard the branch. This deletes work and needs a separate, explicit confirmation.
4. **Do the chosen action only.** Run only the option the user picked. Recheck the base's current commit first; if it moved since step 1, rerun step 2 before integrating.
5. **Verify the result.** After integrating, confirm the base contains the release's commits and that the checks still pass on the result.

## Output

A short report: the branch and base, the check results, the option chosen, the commit or pull request that resulted, and anything left undone.

## Boundaries

Publishing a package version and deploying are separate actions with their own instructions. Never force-push, rewrite published history, or skip hooks.
