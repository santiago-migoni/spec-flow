---
name: clarify
description: "Resolve consequential ambiguity in a release spec before planning."
---

# Spec-Flow: clarify

<HARD-GATE>
Require an existing release spec and run gate for clarify. Read its current registry approval before editing; an approved spec must not be changed under the old digest.
</HARD-GATE>

## Entry and draft routing

Inspect the selected release, spec, registry approval history, and dependencies before writing. Run `gate` with {"kind":"clarify","release":"vX.Y.Z"}; this gate requires the spec itself and its dependency closure to have current approvals. A path-based spec gate checks prerequisites for drafting and does not replace this phase gate. A failed clarify gate stops clarify writes; report its reasons and use the applicable route:

| Observed state | Route |
| --- | --- |
| Initial spec draft without approval | Resolve its questions in `specify` under that skill's gate; retain R00 until approved. Do not approve an ambiguous spec merely to enter clarify. |
| Approved spec and current approved dependencies | Enter clarify against that exact base and prepare a coherent amendment if needed. |
| Previously approved spec now edited or an interrupted amendment draft | Continue the existing draft through `specify` under its own gate. Preserve revision/history; the old receipt does not approve the changed digest. |
| Missing/stale strategic approval or changed dependency pin | Resolve the owning source and explicitly approved adoption before affected work. |

Use approval history rather than revision labels or Markdown status to distinguish these states. Read constitution, selected roadmap scope, applicable approved design, canonical stories/acceptance, existing clarifications, and relevant evidence. Recover already answered questions before asking again. If no meaningful ambiguity exists, report clean and make no write, including no empty session or revision increment.

## Focused conversation

Identify missing decisions, competing interpretations, contradictions, and unverified assumptions. Prioritize consequences for user value, scope, acceptance, feasibility, data, quality, compatibility, and verification. Ask up to five consequential questions per round, one at a time; explain the uncertainty and material consequences, offer neutral alternatives when useful, and use concrete normal/edge/error examples. Draw on business, development, and testing perspectives without inventing participants or requiring a meeting.

Separate existing evidence, the agent's recommendation, and the user's confirmed answer. Leave unknown decisions or thresholds explicit. Five answers do not establish readiness: if material questions remain, report the blockers and continue another round when authorized by the ongoing task. Appropriate technical choices can remain for `plan` when behavior and feasibility are sufficiently clear.

During a valid clarify session, gather responses against the unchanged approved base, then consolidate an amendment. A response conflicting with approved release scope or strategic constraints requires the owning `roadmap`, `constitution`, or shared-design decision before adoption. Route deferred proposals to `backlog` within authorized scope, otherwise report the proposed destination; they do not automatically become release stories.

## Canonical amendment and session record

Use [the clarifications template](assets/clarifications-template.md) for a dated section inside `.specs/release-vX.Y.Z/spec.md`, outside generated progress. It records context, questions/confirmed answers and sources, affected references/application, pending questions and routing, and closure/approval state at preparation. Present current registry approval separately; adding its receipt to the approved decision prose changes the digest. Q references are session-local conversation references, not requirement IDs. Keep prior sessions as history; identify later superseding decisions without rewriting their original answers. Do not create a second editable requirements file, canonical contract, or approval registry.

Update canonical `stories` and `acceptance` first, preserving existing US/AC identifiers and each AC's actual story owner. Synchronize affected prose, story traceability, examples, NFR conditions/targets, and error/compatibility sections in the same revision. A new verifiable obligation needs canonical acceptance, directly or by explicit NFR reference; a Q/A row or example alone cannot define it. Reference each target in its defining section instead of copying another editable value into the session record. Apply `specify`'s table/ownership/coherence review; controller validation does not check semantic completeness or Markdown tables.

For a substantive amendment to an approved spec, increment RNN once and treat the new content as draft. Further rounds before its approval retain that revision. An edit invalidates coverage by the old receipt: do not claim the clarify gate still passes or continue dependent work under it. If interrupted, use the draft route above. Preserve the original approved base and approval history; do not replace downstream pins automatically.

## Closure and handoff

Validate with {"path":".specs/release-vX.Y.Z/spec.md"}; release-wide validation requires spec, plan, and tasks and is not required here. Review reference coherence and unresolved blockers explicitly. Present the concrete revision, decisions applied, remaining questions and their impact/owner/destination, validation results, and actual approval state. Unresolved acceptance/scope/feasibility blockers prevent handoff to plan even if a historical approval exists. Nonblocking plan-owned choices need an explicit reason and destination.

A confirmed answer approves only its actual scope. Get explicit approval of the final revision before dependent work. If the user approved exact proposed wording verbatim and that declaration covers all resulting decision content, it can approve the validated revision without asking again; unseen additions remain unapproved. Inspect affected plan/tasks/shared-source references and adopt changed bases only with explicit approval. Clarification approval does not authorize execution, integration, publication, or deployment.

If implementation is underway, reconcile the completed work with the changed bases before continuing. Route subsequent changes to a new revision and approval rather than rewriting completed history.

This adaptation draws on [PMI's progressive requirements elaboration](https://www.pmi.org/disciplined-agile/product-owner/practice-capturing-functional-requirements), [Agile Alliance's Three C's](https://agilealliance.org/glossary/three-cs/), and [Cucumber's Example Mapping](https://cucumber.io/docs/bdd/example-mapping/); it is not an official template from those sources.

## Runtime discipline

Before invoking `spec-flow.py`, read [shared controller operations](../../harness/contracts/operations.md). Follow its adoption, query/input, validation/digest, and approval/revision mechanics under this skill's own gate and authorized scope.

Clarification does not authorize format conversion. Preserve an existing JSON document's encoding unless separately authorized; apply [shared conversion controls](../../harness/contracts/operations.md#document-encoding) when converting approved sources.
