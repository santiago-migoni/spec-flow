---
name: constitution
description: "Create or revise an agile project constitution covering purpose, beneficiaries, outcomes, boundaries, principles, authority, resources, risks, and completion criteria."
---

# Spec-Flow: constitution

<HARD-GATE>
Inspect project configuration and .specs first. If legacy `.specs/NNN-name/` folders exist, stop before writing and follow the `migrate-preview` → review → `migrate-apply` flow in `using-spec-flow`; use `migrate-resume` after an interrupted apply. For a new unadopted project, run initialize with empty JSON input {} first. Run the runtime gate for this phase and obey it. Urgency never waives a failed gate. This first decision document must be approved in the registry before dependent work.
</HARD-GATE>

Read the repository, README, AGENTS.md, and root configuration for current facts. Write `.specs/constitution.md` using [the constitution template](assets/constitution-template.md). It combines enduring product direction with the agile project's authorization framework. Ask the user for unknown human decisions; purpose, commitments, authority, and acceptance cannot be inferred from code. Distinguish verified facts, hypotheses, proposals, and approved commitments. Leave unanswered items as explicit questions or pending values; explain N/A instead of inventing budgets, dates, baselines, or role assignments.

## Drafting the constitution

Use all eleven template sections, keeping answers concise and sufficient for decisions:

1. **Purpose and justification:** problem or opportunity, reason to act, strategic contribution, and diagnostic evidence.
2. **Vision and beneficiaries:** desired future state, users, customers, stakeholders, needs, and expected value.
3. **Objectives and success criteria:** measurable outcomes with indicator, baseline, target, and evaluation point; distinguish benefits from deliverables.
4. **Scope and boundaries:** included results, exclusions, discovery areas, and conditions for reconsidering the project.
5. **Principles:** enduring, testable MUST rules and SHOULD defaults with explicit deviation conditions.
6. **Responsibilities and authority:** sponsor/initiator, accountable lead, product priority decision-maker, decision limits, approvals, and escalation; explicitly identify combined roles.
7. **Resources, constraints, and assumptions:** budget, capacity, mandatory dates, restrictions, and how/when assumptions will be validated; separate authorized resources from estimates and pending needs.
8. **Principal risks and uncertainties:** strategic risks to value, viability, or objectives, with consequence, initial response/validation, and owner.
9. **Delivery and learning approach:** incremental delivery, user involvement, feedback, and general criteria for prioritizing value and reviewing direction.
10. **Completion and continuation criteria:** evidence, accepting authority, and conditions to continue, redirect, suspend, or cancel; distinguish project completion, release acceptance, and team definition of done.
11. **Approval, references, and amendments:** authorization scope, decision sources, and approved revision history including reasons and affected documents.

Component design belongs in architecture, paths in structure, environments in infrastructure, and release priorities in roadmap. Functional detail belongs in release specs; release-specific risks belong in their release documents. Link detailed team working agreements from the delivery approach. Do not require or create downstream documents to finish the constitution; add references when those documents exist under their own gates.

Constitution approval establishes the project framework. It does not itself authorize implementation, integration, or publication. Follow the separate downstream gates even when the user asks to start immediately.

This is a Spec-Flow adaptation informed by PMI and Agile Alliance's [Agile Practice Guide, sections 5.1–5.2](https://www.agilealliance.org/wp-content/uploads/2021/02/AgilePracticeGuide.pdf#page=63), not an official PMI template. Its agile focus is purpose, beneficiary value, completion criteria, and collaboration, with requirements elaborated progressively.

Use `kind: "constitution"` and `depends_on: []`. Make MUST statements testable and leave unknowns as questions. An approved amendment requires a new revision and approval; downstream dependency digests may become stale.

## Runtime and approval

Before invoking `spec-flow.py`, read [shared controller operations](../../harness/contracts/operations.md). Follow its adoption, query/input, validation/digest, and approval/revision mechanics under this skill's own gate and authorized scope.

## Document encoding

Create new documents from the YAML-frontmatter templates. Preserve existing fenced JSON documents unless conversion is explicitly authorized. Apply [shared encoding and conversion rules](../../harness/contracts/operations.md#document-encoding); retain this skill's gates and canonical records, with no duplicate metadata source.
