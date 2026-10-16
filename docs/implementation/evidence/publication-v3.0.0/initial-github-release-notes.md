# Spec-Flow v3.0.0

Release date: 2026-10-16. Local preparation and final isolated installation are complete. Publication of this version through main, the v3.0.0 tag, and GitHub release is explicitly authorized; installation of the user copy and project migration remain separate.

## Breaking change and upgrade guidance

The three independently invocable design skills are replaced by one design skill. This changes the public skill interface and is the reason for the major version increment.

| Previous invocation | v3.0.0 invocation and requested scope |
| --- | --- |
| `$architecture` / `spec-flow:architecture` | `$design` / `spec-flow:design`, architecture perspective |
| `$infrastructure` / `spec-flow:infrastructure` | `$design` / `spec-flow:design`, infrastructure perspective |
| `$structure` / `spec-flow:structure` | `$design` / `spec-flow:design`, structure perspective |

Update saved prompts, scripts, or instructions that invoke the old skill names or reference their old template paths. The three templates now live under `plugins/spec-flow/skills/design/assets/`.

The canonical `.specs/architecture.md`, `.specs/infrastructure.md`, and `.specs/structure.md` documents, their existing controller kinds, and per-document approval receipts remain separate. Consolidating skills alone does not migrate documents or invalidate unchanged approvals. Keep exact approved dependency pins; explicitly approve/adopt affected revisions when decisions actually change. Existing v2 release projects do not need automatic document rewriting for this update. Legacy numbered feature projects still require the existing reviewed migration before new writes.

## Main improvements

- Expanded strategy and release templates with outcomes, quality, risks, readiness, and synchronized canonical story, acceptance, phase, task, and projected-version tables.
- Unified design with architecture → infrastructure → structure as a flexible elaboration order, scoped perspective changes, and annotated current/proposed repository trees.
- Clearer implementation, technical convergence, release review, and finishing responsibilities; technical completion, integration, publication, and deployment remain separate outcomes.
- Explicit consultation, documentary editing, execution, and resumption modes. Analyze and backlog retain their respective read-only and independent-channel boundaries; clarify distinguishes drafts from approved specifications.
- Shared controller operations reduce repeated instructions while preserving hard gates, approval/evidence authority, native profiles, and execution scope.

## Reliability fixes

| Finding | Correction |
| --- | --- |
| F-01 | Permit the first release review from valid initial generated progress blocks while retaining closure and audit checks. |
| F-02 | Handle unrelated non-object native subagent metadata without bypassing parent, marker, inventory, profile, or ownership attestation. |
| F-03 | Permit explicit abandonment of an exhausted failed task only after attesting the exact bound child as terminal; preserve failures, attempt budget, history, and recoverable ownership release. |

Production execution continues to require an isolated linked Git worktree, attested Sol/high orchestration, one Luna/high implementer, and an independent Sol/high phase reviewer. Three total attempts, exact approval pins, nonmutating verification, phase commits, and final audit controls remain in force.

## Validation and provenance

| Evidence | Actual evaluated source | Demonstrated scope |
| --- | --- | --- |
| [E7](https://github.com/santiago-migoni/spec-flow/blob/1c92505584f789b2e20b4e10538678aa2275dfa2/docs/implementation/e7-ef7897d.md) | ef7897d83dedf9fe20c8bf82fb9e311f4cff8107, manifests 2.0.0 | Fresh/migrated native closure, interruption/restoration, failed-attempt limit and supported abandonment. |
| [E8](https://github.com/santiago-migoni/spec-flow/blob/1c92505584f789b2e20b4e10538678aa2275dfa2/docs/implementation/e8-ef7897d.md) | Same ef7897d candidate, isolated test identity | 14 enabled skills, installed runtime/bootstrap, 127 plugin tests + 9 hook tests; stable installation/configuration unchanged after cleanup. |
| [Local v3.0.0 preparation](https://github.com/santiago-migoni/spec-flow/blob/1c92505584f789b2e20b4e10538678aa2275dfa2/docs/implementation/release-v3.0.0.md) | This cut, version-only manifest changes | Package comparison, current suites and metadata/document consistency, with original evidence links preserved. |
| [Final v3.0.0 isolated installation](https://github.com/santiago-migoni/spec-flow/blob/1c92505584f789b2e20b4e10538678aa2275dfa2/docs/implementation/e8-d19d6e0.md) | d19d6e0be75702907442412f9227688cbc835fba, manifests 3.0.0 | Installed 3.0.0, 14 skills, 127 + 9 tests and bootstrap; separate identity removed, stable installation/configuration intact. |

The 113 files outside the two manifests remain byte-identical to ef7897d. Both manifests retain all fields except version, now 3.0.0. E7/E8 are retained as evidence of that functional base, not rewritten or described as executions against the new version. A separate [final isolated v3.0.0 installation check](https://github.com/santiago-migoni/spec-flow/blob/1c92505584f789b2e20b4e10538678aa2275dfa2/docs/implementation/e8-d19d6e0.md) subsequently passed on d19d6e0be75702907442412f9227688cbc835fba: 14 skills, 127 plugin tests and 9 hook tests from the installed cache, bootstrap checks, and stable installation/configuration preserved. Publication authorization covers the verified package; installation/update and migration remain separate.

Limits remain: the evaluations apply to their host and exercised scenarios. E8 did not demonstrate automatic refresh of existing Desktop chats or live trusted-hook interception. There is no demonstrated time/cost reduction. Real product impact remains separate from technical completion.

## Publication and installation status

The isolated test installation has been removed and the user's stable installation remains unchanged. Publication uses the stable marketplace source on `main` and the `v3.0.0` tag, preserving the original evaluation commits and reports. Installation/update and project migration remain separately authorized actions; publication does not perform them. The post-publication receipt records the actual GitHub release, tag target and asset verification.


## Release provenance

- Release commit: [`1c92505584f789b2e20b4e10538678aa2275dfa2`](https://github.com/santiago-migoni/spec-flow/commit/1c92505584f789b2e20b4e10538678aa2275dfa2).
- Native E7 functional source: `ef7897d83dedf9fe20c8bf82fb9e311f4cff8107`.
- Final isolated installed v3.0.0 source: `d19d6e0be75702907442412f9227688cbc835fba`.
- All 115 package files match that installed source.
- Package SHA-256: `e91768238461a8159fb0588364636c7925771da666d487c5d0e54f6857d01ecc`.
- User installation/update and consuming-project migration are outside this publication.
