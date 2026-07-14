---
name: clarify
description: "Ask up to 5 targeted questions to resolve ambiguity in the current feature's spec.md, writing answers directly into a Clarifications section. Recommended before spec-flow:plan, never required. Use this right after specify when the spec has vague or underspecified areas."
model: opus
effort: high
---

# Spec-Flow: Clarify

Surface and resolve ambiguity in a spec before planning locks in the wrong assumptions.

<HARD-GATE>
A `spec.md` must exist for the current feature — if not, stop and invoke `spec-flow:specify` first.
</HARD-GATE>

## When to Run This Phase

- Right after `spec.md` is written, before `spec-flow:plan`
- Recommended, never required — `plan`'s hard-gate does not check whether `clarify` has run

## Process

1. **Read `.specs/constitution.md` and the current feature's `spec.md`**
2. **Scan for ambiguity** across five dimensions: functional scope & edge cases; data model / entities; non-functional quality (performance, security, reliability); integrations & external dependencies; terminology & completion signals. Mark each dimension Clear / Partial / Missing internally (don't print this map).
3. **Build a prioritized queue** of up to 5 questions — only where the answer would materially change architecture, data model, or test design. Skip anything already answered, or better deferred to `plan`.
4. **Ask one question at a time**:
   - Multiple-choice: show `**Recommended:** Option X — <1-sentence reasoning>`, then a table of options (max 5), then invite the user to reply with a letter, "yes", or their own answer.
   - Open-ended: show `**Suggested:** <answer> — <1-sentence reasoning>`, and invite "yes" or a short answer (≤5 words) of their own.
5. **After each accepted answer** — write immediately, never batch:
   - Create `## Clarifications` in `spec.md` if missing (place right after the summary section), with a `### Session YYYY-MM-DD` subheading for today
   - Append `- Q: <question> → A: <answer>`
   - Edit the directly affected section (User Stories, Edge Cases, or Non-Goals) to resolve the ambiguity — replace the vague text, don't just append a caveat next to it
6. **Stop** at 5 asked questions, or when the user signals "done"/"enough", or when no high-impact ambiguity remains
7. **If no meaningful ambiguity is found** — report "No critical ambiguities detected." and suggest proceeding to `plan`, asking nothing

## Quality Check Before Finishing

- [ ] No more than 5 questions were asked
- [ ] Every accepted answer has exactly one bullet under `## Clarifications` and is reflected in the relevant section
- [ ] No contradictory earlier statement remains in `spec.md`
- [ ] `plan`'s hard-gate is unaffected — `clarify` is a recommendation, never a requirement

## After Writing

Tell the user: "N clarifications recorded in `.specs/NNN-feature-name/spec.md`. Run `spec-flow:plan` when ready." If no questions were needed: "No critical ambiguities detected — proceed to `spec-flow:plan` whenever you're ready."
