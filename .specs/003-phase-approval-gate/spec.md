# Spec: Phase Approval Gate

<!-- Every claim in this document must be measurable or falsifiable — avoid vague adjectives ("fast", "robust", "intuitive", "seamless") without a concrete threshold or test. spec-flow:analyze flags unmeasurable language as an Ambiguity finding. -->

| Name                 | Code     | Version | Date       | Status   |
| -------------------- | -------- | ------- | ---------- | -------- |
| phase-approval-gate  | SPEC-003 | R01     | 2026-07-17 | Approved |

## Summary

Enforce, with a native Claude Code hook rather than prose, that a phase's artifact carries an explicit recorded approval before the next gated phase's skill can be invoked — closing the gap where the model could chain phases (e.g. `tasks`→`implement`) without real user sign-off. The signal is the existing document-control table's `Status` field (`Draft`/`Approved`/`Converged` on `spec.md`; `Draft`/`Approved` on `constitution.md`, `plan.md`, `tasks.md`) — no new field is introduced.

## Clarifications

### Session 2026-07-17

- Q: Does a missing `Status` column on a pre-existing artifact block the next phase, or count as already-approved? → A: Grandfathered — a missing `Status` column is treated as already-approved and does not block.
- Q: Does revising an already-`Approved` artifact reset its `Status` to `Draft`? → A: Yes — any post-approval edit (a requested revision, or an amendment) resets `Status` to `Draft` until the user approves again.

### Session 2026-07-17 (continued)

- Q: Does that reset-to-`Draft` step apply even when the user's edit request already constitutes approval of the exact resulting content (e.g., approving `spec-flow:analyze`'s suggested fixes, verbatim)? → A: No — if the user has already seen the specific proposed text and explicitly asks to apply it, that instruction is itself the approval. Skip the `Draft` interim state: bump `Version` and set `Status` straight to `Approved` in the same edit. The `Draft` interim state is only for edits where the model must draft content the user hasn't seen yet.

## Success Metrics

- Zero phase-chaining-without-approval incidents in dogfooding sessions after this ships (the class of bug reported from odoo-infrastructure, backlog `B005`) — measured by absence of such reports across at least the next 3 dogfooded features.
- When a call is blocked, the model asks the user for approval on its own, without the user needing to manually point out the gate — measured qualitatively during dogfooding.

## User Stories

<!-- One block per story, ordered by priority. P1 = must-ship, P2 = should-ship, P3 = nice-to-have. Repeat as US2, US3, ... for each additional story. -->

### US1 — Block invoking the next phase before approval (P1)

As a spec-flow user, I want the next phase's skill to refuse to run if the prior phase's artifact's `Status` is still `Draft`, so the model can't silently skip my sign-off.

**Acceptance Scenarios**:

- **Given** `tasks.md`'s document-control table has `Status: Draft`, **When** the model attempts to invoke `spec-flow:implement`, **Then** the tool call is blocked and the model receives a reason it can act on (the artifact is not yet approved).
- **Given** `spec.md`'s `Status` is `Approved` (or `Converged`), **When** the model invokes `spec-flow:plan`, **Then** the tool call proceeds normally.
- **Given** the user is invoking `spec-flow:clarify` or `spec-flow:analyze` (side-channel, non-gated skills), **When** the prior artifact's `Status` is `Draft`, **Then** the call is not blocked — this hook only applies to the four gated transitions (`constitution`→`specify`, `specify`→`plan`, `plan`→`tasks`, `tasks`→`implement`).

### US2 — Record approval as part of the existing confirm step (P1)

As a spec-flow user, when I approve a phase's executive summary (the existing "ask for approval or revisions" step every phase already has), I want `Status` set to `Approved` immediately, so the hook has a real signal to check instead of nothing.

**Acceptance Scenarios**:

- **Given** the model just presented a phase's executive summary and asked for approval, **When** the user replies with approval, **Then** the model sets `Status` to `Approved` in that artifact's document-control table before the turn ends.
- **Given** the user asks for a revision instead of approving, **When** the model applies the revision and re-asks for approval, **Then** `Status` stays `Draft` until the user actually approves.
- **Given** an artifact's `Status` is already `Approved` (or `Converged`), **When** the user requests a further edit whose exact content the model must still draft (the user hasn't seen the resulting text yet), **Then** the model resets `Status` to `Draft`, applies the edit, and asks for approval again before setting `Status` back to `Approved`.
- **Given** an artifact's `Status` is already `Approved` (or `Converged`), **When** the user explicitly approves applying a specific, already-shown edit (e.g., a `spec-flow:analyze` finding's exact recommendation) and the model applies exactly that, **Then** the model skips the `Draft` interim state — it bumps `Version` and sets `Status` straight to `Approved` in the same edit, without asking for a second confirmation.

## Non-Functional Requirements

<!-- Feature-specific quality bar, additive to constitution.md's global MUSTs — don't repeat a constitution principle here, only what this feature specifically needs. Write "N/A" if the constitution's baseline already covers this feature with no exceptions. -->

- **MUST**: The enforcement mechanism is a native Claude Code hook (`settings.json` `PreToolUse`) — no external service, no network call, per the constitution's portability constraint and its narrow R02 hooks exception.
- **MUST**: A blocked call returns a human-readable reason the model can act on (ask the user for approval) — never a silent or opaque failure.
- **SHOULD**: The hook's check stays fast — it reads one table cell, it does not perform any semantic judgment of the conversation.

## Edge Cases

- An artifact predates this feature and has no `Status` column at all (e.g., this repo's own `.specs/001-*` and `.specs/002-*`) — grandfathered: treated as already-approved, does not block the next phase.
- The user approves via free text that doesn't match any fixed phrase (e.g. "sure, go ahead", "dale") — the hook never parses conversation text; recognizing approval and writing `Status: Approved` is the model's responsibility, same as it already is for the existing prose-based "ask for approval" step.
- A phase is re-run to revise an artifact that was already `Approved` (e.g. `spec-flow:plan` invoked again to make a change) — the edit resets `Status` to `Draft`; the next gated phase is blocked again until the user re-approves. Exception: if the user already approved the exact resulting text (e.g., a `spec-flow:analyze` finding's specific recommendation), the model skips `Draft` and sets `Status` straight to `Approved`.
- `spec.md` reaches `Converged` (set only by `spec-flow:converge`) — a `Converged` status must count as approved for gating purposes, same as `Approved`; `constitution.md`/`plan.md`/`tasks.md` never reach `Converged` at all (2-state enum: `Draft`/`Approved` only).

## Assumptions & Dependencies

- Assumes a Claude Code `PreToolUse` hook can identify which skill is about to run (e.g. by matching the invoking tool call's arguments) and can read a table cell from a `.specs/` markdown file before allowing or blocking the call.
- Assumes every gated artifact's document-control table already has a `Status` column — `constitution.md`, `plan.md`, and `tasks.md`'s templates gained one alongside this feature; `spec.md` already had one and just gained the `Approved` middle value.
- Depends on `.specs/constitution.md`'s narrow hooks exception (introduced in `R02`, carried unchanged through `R03`'s section reorganization), approved earlier this session.

## Explicit Non-Goals

- Does not build a general-purpose hooks/extensions framework for arbitrary per-project customization — the constitution's `R02` exception is narrow, scoped to this one enforcement mechanism, and the general rejection stays in force.
- Does not attempt to semantically verify that an approval was genuine or informed — the hook only ever checks one table cell; writing that cell honestly remains the model's responsibility, same as today's prose-based gate already relies on.
- Does not change any artifact template's content beyond the `Status` column already added to `constitution.md`/`plan.md`/`tasks.md` and the `Approved` value added to `spec.md`'s existing `Status` enum — no other section of any template changes.

## Open Questions

<!-- Empty section is a valid, finished state — don't invent a question to fill it. -->

None — both open questions were resolved via `spec-flow:clarify` (see Clarifications above).
