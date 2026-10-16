from pathlib import Path
import json,subprocess
R=Path.cwd();E=R/'docs/implementation/evidence/release-v3.0.0';E.mkdir(parents=True);(E/'reproduction').mkdir()
assert not subprocess.check_output(['git','status','--porcelain'])
refs=subprocess.check_output(['git','for-each-ref','--format=%(refname) %(objectname)','refs/tags','refs/remotes'],text=True)
(E/'refs-before.txt').write_text(refs)
for rel in ('plugins/spec-flow/plugin.json','plugins/spec-flow/.codex-plugin/plugin.json'):
    p=R/rel;x=json.loads(p.read_text());assert x['version']=='2.0.0';x['version']='3.0.0';p.write_text(json.dumps(x,indent=2)+'\n')
p=R/'CHANGELOG.md';s=p.read_text();head,old=s.split('## Release v2.0.0',1);body=head.split('## Unreleased',1)[1].strip()
f03='- Fix F-03: explicitly abandon an exhausted failed task only after terminal native-child attestation, preserving failure history, retry budget, and ownership-release recovery.'
assert body.startswith(f03);body=body[len(f03):].lstrip();body=body.replace('### Fixed\n','### Fixed\n\n'+f03+'\n',1)
body=body.replace('gate conditions, or version 2.0.0.','or gate conditions.').replace('without adding a runtime design kind or changing version 2.0.0.','without adding a runtime design kind.')
intro='''# Changelog

## Unreleased

## Release v3.0.0

Status: Prepared locally on 2026-10-16; not published. Publication date pending.
Release notes: [v3.0.0](docs/releases/v3.0.0.md).

### Breaking changes

- Replace the independently invocable architecture, infrastructure, and structure skills with design. Update saved prompts and automation to invoke design and state the intended perspective. The three canonical documents, templates, controller kinds, and per-document approvals remain distinct; existing v2 projects do not require automatic document rewriting because of this consolidation.

'''
validation='''

### Validation

- E7 native evaluation passed on candidate ef7897d: fresh and migrated release closure, interruption recovery, three failed attempts with rejection of a fourth attempt, and authorized abandonment preserving failure history and releasing ownership.
- E8 isolated installation passed on ef7897d: 14 enabled skills discovered in a fresh app-server client, 113 resources unchanged, 127 plugin tests and 9 hook tests from the installed cache, and stable installation/configuration preserved after cleanup.
- The v3.0.0 cut changes only the version field of both package manifests relative to ef7897d. The release-preparation record links the original E7/E8 evidence and records current package checks; it does not relabel those evaluations as runs against v3.0.0.
- No demonstrated cost or duration savings, automatic refresh of existing chat catalogs, or live trusted-hook interception. Local preparation does not publish or install v3.0.0.
'''
p.write_text(intro+body+validation+'\n## Release v2.0.0'+old)
p=R/'AGENTS.md';s=p.read_text();old='The current release is `2.0.0`; retain it unless a release version bump is explicitly part of the work.';new='The local package version is `3.0.0`, prepared as a local release cut; publication is a separate authorized step. Retain this version unless a release version bump is explicitly part of the work.';assert old in s;p.write_text(s.replace(old,new,1))
p=R/'README.md';s=p.read_text();needle='## Install from GitHub marketplace';assert needle in s;s=s.replace(needle,'Local release cut **v3.0.0** is prepared; see [release notes and upgrade guidance](docs/releases/v3.0.0.md). The package version changed after the candidate evaluations; their original commit references and the [release-preparation checks](docs/implementation/release-v3.0.0.md) remain explicit. Publication is pending.\n\n'+needle,1);p.write_text(s)
(R/'docs/releases').mkdir(exist_ok=True)
(R/'docs/releases/v3.0.0.md').write_text('''# Spec-Flow v3.0.0

Status: local release cut prepared on 2026-10-16. Not yet published; publication date pending. These notes are ready for review before a separately authorized tag, push, and GitHub release.

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
| [E7](../implementation/e7-ef7897d.md) | ef7897d83dedf9fe20c8bf82fb9e311f4cff8107, manifests 2.0.0 | Fresh/migrated native closure, interruption/restoration, failed-attempt limit and supported abandonment. |
| [E8](../implementation/e8-ef7897d.md) | Same ef7897d candidate, isolated test identity | 14 enabled skills, installed runtime/bootstrap, 127 plugin tests + 9 hook tests; stable installation/configuration unchanged after cleanup. |
| [Local v3.0.0 preparation](../implementation/release-v3.0.0.md) | This cut, version-only manifest changes | Package comparison, current suites and metadata/document consistency, with original evidence links preserved. |

The 113 files outside the two manifests remain byte-identical to ef7897d. Both manifests retain all fields except version, now 3.0.0. E7/E8 are retained as evidence of that functional base, not rewritten or described as executions against the new version. A fresh installed v3.0.0 package evaluation has not been performed as part of this local metadata cut; confirm final distribution separately before publication.

Limits remain: the evaluations apply to their host and exercised scenarios. E8 did not demonstrate automatic refresh of existing Desktop chats or live trusted-hook interception. There is no demonstrated time/cost reduction. Real product impact remains separate from technical completion.

## Publication and installation status

This local cut does not create a tag, push commits, publish a GitHub release, install the new version, or migrate an existing project. The stable marketplace source remains `main`. Publication, installation/update, and project migration require their own applicable authorization and checks.
''')
print('Prepared manifests 3.0.0, changelog section, release notes and coherent local-cut guidance')
