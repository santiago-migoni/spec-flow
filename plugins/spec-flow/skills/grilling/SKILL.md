---
name: grilling
description: "Grill an idea, plan, or decision with one question at a time, or brainstorm options first, in conversation only, at any point of the flow."
---

# Spec-Flow: grilling

<HARD-GATE>
Conversation only. Write no file, run no controller operation, record no approval, and create no document. Nothing said here is a decision of any Spec-Flow document until its owning skill records it under its own gate.
</HARD-GATE>

Use this optional side channel when the user wants to stress-test an idea, plan, or decision, or to explore options before committing. It gates nothing and can run before, between, or during any phase.

## Prepare

Read what already exists before asking: approved `.specs/` documents, the backlog, and the relevant code. Never ask what a read can answer. Cite the document when an idea conflicts with an approved decision. When no `.specs/` documents exist yet, the plugin's own contracts and the repository are the context.

## Grill

- Ask exactly one question per message, ordered by consequence: settle the decision that other decisions depend on first. Do not announce the questions you are holding back.
- Give two or more options and your recommended one with every question, so the user can accept it or push back. Number the questions across the session (Q1, Q2, ...) and use this format:

```txt
Q1 - <question>

* <option 1>
* <option 2>
* <option 3>

Recommended option: <the option, and why in one sentence>
```

- Challenge assumptions, contradictions, missing edge cases, hidden costs, and unstated alternatives. Fold the strongest objection into the current question as its context; it is not a second question. Be direct and keep going until the weak points are named.
- Label what you hear as fact, hypothesis, proposal, or decision. Do not turn a hypothesis into a decision.
- If the user has no options yet, first offer three to five distinct ones with their trade-offs, then grill the one they lean toward.
- Leave unknown owners, dates, budgets, and commitments as open questions. Never invent them.

## Close

Stop when the user says so or the consequential questions are settled. Summarize in the conversation: decisions made, assumptions, open questions, and rejected options with their reasons.

Then name where each result belongs: the `constitution`, `design`, `roadmap`, `specify`, `plan`, or `tasks` skill for decisions, or the `backlog` skill for ideas to defer. Use those skills only when the user asks; this skill does not hand work off by itself.
