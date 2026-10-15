---
name: using-spec-flow
description: "Start or resume the release-centered Spec-Flow workflow and find the next authorized phase."
---

# Spec-Flow: using-spec-flow

<HARD-GATE>
Inspect project configuration and `.specs` first. If legacy `.specs/NNN-name/` folders exist, stop before writing and follow the actual `migrate-preview` → human review → `migrate-apply` flow in [the migration contract](../../harness/contracts/migration.md); resume an interrupted apply with `migrate-resume`. There is no `migrate` CLI operation. For a new unadopted project, run `initialize` with empty JSON input `{}` first. Run the runtime gate for the intended document or execution phase and obey it; using-spec-flow itself is not a gate kind. Urgency never waives a failed gate.
</HARD-GATE>

Strategy: `constitution → applicable shared system design → roadmap`. Delivery: `specify → clarify (optional) → plan → tasks → analyze (optional) → implement (verified phases and commits) → converge → review-release → finishing-branch`. Create architecture, infrastructure, and structure documents only when applicable to planned releases; record N/A with a reason in the roadmap when inapplicable. Strategy files are `.specs/{constitution,architecture,infrastructure,structure,roadmap}.md`. An active release uses `.specs/release-vX.Y.Z/{spec,plan,tasks}.md` and may contain multiple stories. Release identifiers use strict numeric SemVer such as `v2.0.0`.

Recommended design elaboration order: architecture → infrastructure → structure. This is not a mandatory dependency chain. Inspect existing repository organization and operational constraints early; revise earlier decisions when findings require it. Each document pins the approved constitution and only approved design sources actually used; do not introduce reciprocal pins. Infrastructure does not require structure by default; structure can proceed without infrastructure when it does not rely on it. Navigational links alone do not imply dependencies, and omitting a dependency does not make its source document N/A. Do not create future dependent documents to complete an earlier one.

Architecture owns context, quality scenarios, components/contracts, data/runtime behavior, and significant design decisions. Infrastructure owns execution resources, delivery/operations, and recovery, including local host needs when applicable. Structure maps responsibilities to paths and placement/dependency rules, with an annotated verified tree and a separate proposed tree when needed. Keep proposals, approved design, and implementation evidence distinct; approval does not prove deployment or implementation.

At session start inspect configuration and `.specs`, then call `status --input <json-file>` using `{}` and `gate --input <json-file>` for the intended phase. For release gates pass `{"kind":"<phase>","release":"vX.Y.Z"}`. Do not infer authorization from file existence, legacy `Status: Approved` tables, checked boxes, or urgency. Existing approved sources can be reused only while content digest and scope remain current. If approved sources change during an open run, reconcile any active native agent and use `abandon` with a recorded reason and authorization before starting a new run; unchanged completed-task evidence is reused only when its exact task contract, source pins, checks, and code fingerprint still match. Attempt limits carry across abandoned runs. Legacy projects use the documented preview/apply/resume operations before new writes; new projects run `initialize` with empty JSON input `{}`.

The constitution establishes product direction and the agile project framework: purpose, beneficiaries, measurable outcomes, boundaries, principles, authority, resources, risks, delivery/learning, and completion criteria. Its approval does not itself authorize implementation. Roadmap owns release priorities, and detailed team working agreements are linked rather than duplicated.

Draft the next required document, gain its approval, then proceed to dependent phases. Explicit user execution authorization may cover multiple phases; each phase still needs current task evidence, an independent Sol review, and a validated commit before the next phase. Approval to execute does not authorize push, merge, publication, or deployment. `$backlog` remains independent.

CLI shape: `python3 <plugin-root>/scripts/spec-flow.py --root <project> OP --input <json-file>`. Operations include `initialize`, `validate`, `digest`, `approve`, `gate`, `capabilities`, `start`, `authorize`, `prepare`, `restore-packet`, `bind-agent`, `result`, `verify`, `review`, `close`, `resume`, `reconcile`, `takeover`, `interrupt`, `phase-ready`, `review-phase`, `commit-phase`, `refresh-evidence`, `release-review`, `complete`, `status`, and the three migration operations. Resolve plugin root from the installed skill location. Follow the selected phase skill's own hard gate and stop on any failed gate.

## Runtime and approval

Resolve the plugin root from this installed skill. Run `python3 <plugin-root>/scripts/spec-flow.py --root <project> validate --input <json-file>` with `{"path":"<project-relative path>"}` after writing. Use `digest` with the same input to capture exact dependency digests. One fenced `spec-flow` JSON block holds `schema_version: 1`, `kind`, stable `id`, `revision: "R00"` initially, and `depends_on` references. Decision prose remains outside the block. Only generated progress and optional lowercase `status` may be updated as views.

The relevant document skill owns drafting and approval. Bootstrap does not itself approve or rewrite artifacts.

## Execution closure

The controller starts one explicitly authorized phase by default. Close tasks only after current checks and review; task closure does not commit or complete the run. At each phase boundary use `phase-ready`, obtain an independent Sol high review of the exact pinned tree with `review-phase`, then call `commit-phase`. The next dependent phase cannot start before the prior phase commit is in the current branch history. After every declared phase commit, call `release-review`; it writes the derived technical outcome and roadmap reference and creates the final audit-only commit. `complete` and `scripts/check-complete.sh <tasks.md>` are read-only evidence-and-commit checks; task checkboxes alone do not prove completion. If a bounded task or phase packet cache is missing, use `restore-packet` with the same run/owner and task or phase ID before resume/review; it only restores when approved source pins reproduce the event hash. Corrupt caches are not replaced, and older events without the original timestamp may be unrecoverable. Use the concrete payloads in [the execution contract](../../harness/contracts/execution.md).
