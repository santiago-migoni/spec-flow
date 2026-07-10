---
name: finishing-branch
description: "Use when a feature is converged and ready to integrate. Verifies tests, updates CHANGELOG.md, then presents structured options: merge locally, push + PR, keep as-is, or discard. Use this when the user says the feature is done, wants to merge, or asks what to do with the branch."
model: sonnet
effort: medium
---

# Spec-Flow: Finishing Branch

Guide the integration of a completed feature branch — tests, changelog, then a clear choice about where the work goes.

<HARD-GATE>
Before proceeding:
1. `.specs/NNN-feature-name/tasks.md` must exist — run `scripts/check-complete.sh .specs/NNN-feature-name/tasks.md` to confirm all tasks are `[x]`
2. Converge must have run — either the spec's `Status` is `Converged`, or the user explicitly confirms they want to finish without converging
</HARD-GATE>

## Step 1: Converge Check

Read `.specs/NNN-feature-name/spec.md`. If `Status` is not `Converged`, surface this:

```
Converge has not been run for this feature.
Run spec-flow:converge first, or confirm you want to finish without it.
```

Wait for explicit user confirmation before continuing.

## Step 2: Verify Tests

Run the project's test suite:

```bash
npm test / cargo test / pytest / go test ./... / <project-specific command>
```

**If tests fail** — stop completely:

```
Tests failing (N failures). Fix before finishing:

[Show failures]

Cannot proceed until tests pass.
```

Do not proceed to Step 3.

**If tests pass** — continue.

## Step 3: Update CHANGELOG.md

Read `.specs/NNN-feature-name/spec.md` to extract:
- Feature name and summary
- User stories delivered (and their priorities)

Check the branch's commit history for its [Conventional Commits](https://www.conventionalcommits.org/) types:

```bash
git log <base-branch>..HEAD --oneline
```

Use the heading driven by the commit types found (fall back to judgment from the spec summary if commits aren't typed):
- `Added` — branch contains `feat` commits
- `Fixed` — branch contains `fix` commits (and no `feat`)
- `Changed` — everything else (`refactor`, `perf`, `style`, etc.)

If any commit has a `!` after its type/scope or a `BREAKING CHANGE:` footer, call that out explicitly in the entry.

The same scan gives the [SemVer](https://semver.org/) bump this branch calls for — carry it to Step 5, don't act on it here:
- **MAJOR** — any `!` or `BREAKING CHANGE:` footer
- **MINOR** — no breaking change, but at least one `feat`
- **PATCH** — no breaking change or `feat`, but at least one `fix` or `refactor`
- **none** — only `chore`/`docs`/`style`/etc., no user-facing change

Read the root `CHANGELOG.md` and add an entry under `## [Unreleased]` (create the section if it does not exist):

```markdown
### Added / Changed / Fixed
- [Feature name] — [one-line summary of what was delivered, derived from spec summary]
```

Write the updated `CHANGELOG.md`. Do not modify any other section.

## Step 4: Stage and Commit Spec Artifacts

Before presenting integration options, provide the commands to commit all spec artifacts and the changelog. Use a [Conventional Commits](https://www.conventionalcommits.org/) message — this commit only touches documentation, so type `docs`, scoped to the feature:

```bash
git add .specs/NNN-feature-name/ CHANGELOG.md
git commit -m "docs(NNN-feature-name): update changelog and spec artifacts"
```

This keeps the spec artifacts and changelog separate from the implementation commits.

## Step 5: Present Integration Options

```
Feature NNN-feature-name is complete. Tests pass. CHANGELOG updated.
Recommended version bump: <MAJOR|MINOR|PATCH|none> — <reason, e.g. "feat commits present">

1. Merge into <base-branch> locally
2. Push and create a Pull Request
3. Keep the branch as-is (handle later)
4. Discard this work

Which option?
```

Don't edit any version file (`package.json`, `Cargo.toml`, `.claude-plugin/plugin.json`, etc.) — its location and format vary per project. The bump is a recommendation for whoever cuts the release.

Detect base branch:
```bash
git merge-base HEAD main 2>/dev/null || git merge-base HEAD master 2>/dev/null
```

If base branch is ambiguous, ask: "Which branch should this merge into?"

## Step 6: Execute Choice

### Option 1 — Merge locally

Provide the commands:
```bash
git checkout <base-branch>
git pull
git merge <feature-branch>
```

Run tests again on the merged result. If they pass, provide:
```bash
git branch -d <feature-branch>
```

Report: "Merged and branch deleted. Feature complete."

### Option 2 — Push and create PR

Provide the commands:
```bash
git push -u origin <feature-branch>
gh pr create --title "<feature name>" --body "Closes spec: .specs/NNN-feature-name/"
```

Do not delete the branch — the user needs it alive for PR feedback.

Report: "Branch pushed and PR created. Branch preserved for iteration."

### Option 3 — Keep as-is

Report: "Branch kept as-is. Run spec-flow:finishing-branch again when ready."

### Option 4 — Discard

**Require explicit confirmation first:**

```
This will permanently delete:
- Branch <feature-branch>
- All commits since <base-branch>: <commit-list>

Type 'discard' to confirm.
```

Wait for exact input `discard`. On confirmation, provide:

```bash
git checkout <base-branch>
git branch -D <feature-branch>
```

Report: "Branch discarded."

## Red Flags

| Never | Because |
|---|---|
| Proceed with failing tests | Merges broken code |
| Force-push without explicit user request | Rewrites shared history |
| Delete the branch on Option 2 | User needs it for PR iteration |
| Skip the discard confirmation | Permanent data loss |
| Modify CHANGELOG sections other than Unreleased | Breaks release history |
