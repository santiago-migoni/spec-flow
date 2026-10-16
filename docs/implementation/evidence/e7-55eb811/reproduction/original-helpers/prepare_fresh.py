import json, os, shutil, subprocess, sys
from pathlib import Path
P=Path('/private/tmp/spec-flow-e7-55eb811-nh63aagh/source/plugins/spec-flow')
B=Path('/private/tmp/spec-flow-e7-55eb811-nh63aagh')
E=Path('/Users/santiago_migoni/Documents/Projects/spec-flow/docs/implementation/evidence/e7-55eb811/native')
E.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(P))
from harness.runtime.contracts import document_digest
root=B/'fresh-main'
if root.exists(): raise SystemExit('fixture already exists')
root.mkdir()
def git(*a):
 p=subprocess.run(['git',*a],cwd=root,text=True,capture_output=True); assert p.returncode==0,(a,p.stdout,p.stderr);return p.stdout.strip()
git('init','-b','main')
git('config','user.name','E7 Fixture Evaluator');git('config','user.email','e7-fixture@example.invalid')
def doc(rel, kind, id, deps, fields, sections):
 path=root/rel;path.parent.mkdir(parents=True,exist_ok=True)
 obj={'schema_version':1,'kind':kind,'revision':'R00','id':id,'depends_on':[{'path':p,'digest':document_digest(root/p)} for p in deps],**fields}
 path.write_text('# '+kind.title()+' — E7-only disposable fixture\n\n```spec-flow\n'+json.dumps(obj,indent=2)+'\n```\n\n'+sections+'\n\n<!-- spec-flow:generated:start -->\nProgress is maintained by the Spec-Flow harness.\n<!-- spec-flow:generated:end -->\n')
 return rel
constitution=doc('.specs/constitution.md','constitution','CONST-E7',[],{},'''## Purpose and justification
Evaluate the pinned Spec-Flow package on a bounded local Python library. The baseline intentionally lacks the desired implementation; evidence is the fixed four-method suite.
## Vision and beneficiaries
The evaluator needs an exact normalization function and attributable controller evidence. This fixture has no external users.
## Objectives and success criteria
| Objective | Indicator | Baseline | Target | Evaluation point |
| --- | --- | --- | --- | --- |
| OUT-001 strict normalization | Four fixed unittest methods | Failing baseline | All pass | Before release review |
## Scope and boundaries
Only release.py may be implemented. test_release.py is fixed. Installation, delivery, and real-product approval are excluded.
## Principles
- MUST: Preserve the fixed test file and exact errors.
- MUST: Verification must leave implementation bytes unchanged.
## Responsibilities and authority
The E7 evaluator owns synthetic fixture decisions and bounded execution under the user's E7 authorization. These approvals apply solely to disposable fixtures.
## Resources, constraints, and assumptions
Use the pinned package, stdlib Python, native agents, and local linked worktrees. No external capacity or date commitments.
## Principal risks and uncertainties
| Risk or uncertainty | Possible consequence | Initial validation or response | Owner |
| --- | --- | --- | --- |
| Host attestation unavailable | Native run blocked | Validate session log before start | Evaluator |
## Delivery and learning approach
One small reviewed phase with explicit evidence and a retained branch.
## Completion and continuation criteria
Technical completion requires all tests, task closure, independent phase review, and phase commit. Impact measurement remains pending; no publication follows.
## Approval, references, and amendments
This is a synthetic E7-only decision. Controller receipts, not this prose, establish fixture authority.''')
architecture=doc('.specs/architecture.md','architecture','ARCH-E7',[constitution],{},'''## Purpose and approved basis
The approved E7 constitution selects a single local function and fixed test boundary.
## Responsibilities and interfaces
release.py exports normalize_release(value). It returns a canonical v-prefixed strict numeric triple or raises TypeError for nonstrings and ValueError for malformed strings. test_release.py is the immutable verification client.
## Components and interactions
Input → normalize_release → canonical string or typed exception. No storage, network, or service interface.
## Decisions and rationale
Keep implementation in one Python module and use stdlib only; this makes the contract observable through the fixed suite.
## Quality and risks
No Unicode numeric acceptance; ASCII digits only. Whole-string matching prevents whitespace and suffix acceptance.
## Verification and changes
The four fixed tests and review of actual diff establish behavior. Any changed interface needs a new approved source.''')
structure=doc('.specs/structure.md','structure','STRUCT-E7',[constitution,architecture],{},'''## Purpose and approved bases
This structure records the verified starting tree and intended single-file change.
## Verified current tree
- release.py — existing stub; only implementation file.
- test_release.py — fixed four-method suite; read-only.
- .specs/ — controller-governed decisions.
## Proposed tree
Same paths; release.py becomes a working implementation. Generated .spec-flow records are owned by the controller.
## Placement rules
Function and helper constants stay in release.py. Tests remain byte-for-byte fixed.
## Validation and exceptions
Git diff and file hashes verify placement; no exception or path expansion is approved.''')
obj='Evaluate strict release normalization in disposable code.'
roadmap=doc('.specs/roadmap.md','roadmap','ROADMAP-E7',[constitution,architecture,structure],{'releases':[{'version':'v1.2.3','objective':obj,'status':'planned'}]},f'''## Purpose, audience, and scope
One E7-only local release projection for evaluators.
## Direction and approved bases
OUT-001 is governed by the constitution, architecture, and structure. Infrastructure is N/A because this is a local pure function with no deployed environment.
## Desired outcomes and measurement
| ID | Desired outcome | Beneficiaries | Indicator | Baseline | Target | Evaluation |
| --- | --- | --- | --- | --- | --- | --- |
| OUT-001 | Strict normalization | Evaluator | Fixed unittest methods | Failing | Four pass | At technical review |
## Prioritization criteria and rationale
The sole release is first because it is the complete bounded evaluation behavior.
## Horizons and uncertainty
Now means this fixture run; no future release commitments.
## Release projections and sequence
| Version | Horizon | Expected contribution | General capabilities | Canonical status | Selection |
| --- | --- | --- | --- | --- | --- |
| v1.2.3 | Now | {obj} | Strict normalization | planned | Selected |
## Next selected release
v1.2.3 is explicitly selected for this E7-only fixture under the user's evaluation authorization. Selection does not authorize real product delivery.
## Capacity, dependencies, and risks
Python stdlib and native host attestation are required; host failure blocks execution.
## Deferred opportunities and exclusions
No further behavior selected.
## Review, evidence, and learning
Review fixed tests and source-linked controller evidence after execution; impact is pending.
## References, approval, and amendments
Synthetic fixture decision; receipts apply only to E7.''')
accept=[{'id':'AC-001','story':'US-001','description':'A bare or v-prefixed ASCII numeric triple normalizes to one v-prefixed triple, preserving component digits including zero and arbitrarily large components.'},{'id':'AC-002','story':'US-001','description':'Malformed strings, leading zeros, Unicode digits, whitespace, suffixes and incorrect segment counts raise ValueError; non-string inputs raise TypeError.'}]
spec=doc('.specs/release-v1.2.3/spec.md','spec','SPEC-1.2.3',[roadmap,architecture,structure],{'stories':[{'id':'US-001','title':'Strict release normalization','description':'As an E7 evaluator, I need a deterministic strict normalizer so that release identifiers have one canonical form.'}],'acceptance':accept},'''## Purpose and selected release
The approved roadmap explicitly selects v1.2.3 for the E7 fixture.
## Users, context, and expected outcome
The evaluator calls normalize_release from local Python; OUT-001 is demonstrated by four fixed tests.
## Scope and exclusions
Implement release.py only. No CLI, packaging, deployment, or test editing.
## Approved bases and constraints
Constitution MUST rules, architecture interface, and structure paths apply. Infrastructure is N/A for this local function.
## User stories
| Story | Related outcomes | Acceptance criteria | Relevant dependencies |
| --- | --- | --- | --- |
| US-001 | OUT-001 | AC-001, AC-002 | Fixed suite |
## Rules, acceptance, and examples
| Criterion | Situation or input | Action or event | Expected result |
| --- | --- | --- | --- |
| AC-001 | `1.2.3`, `v1.2.3`, `0.0.0`, huge ASCII integers | normalize_release | Exact v-prefixed triple |
| AC-002 | `01.2.3`, `1.2.٣`, whitespace, suffix, None | normalize_release | ValueError for strings; TypeError for nonstrings |
## Quality and conditions of done
| ID | Attribute | Conditions | Result or threshold | Verification approach | Related criteria |
| --- | --- | --- | --- | --- | --- |
| NFR-001 | Deterministic strictness | All fixed samples | Four unittest methods pass; test file unchanged | `python3 -B -m unittest -v test_release.py` | AC-001, AC-002 |
## Edge cases, errors, and compatibility
AC-002 includes Python bool as nonstring despite its int subclass. No permissive whitespace stripping.
## Post-delivery measurement
Run evidence shows technical behavior. Real-world impact is pending and out of scope.
## Assumptions, dependencies, and open questions
No blocking question; stdlib Python and fixed test file are present.
## Readiness for planning, approval, and amendments
All observable behavior and error classes are in canonical ACs; this is an E7-only fixture approval.''')
plan=doc('.specs/release-v1.2.3/plan.md','plan','PLAN-1.2.3',[spec,structure],{'phases':[{'id':'PH-01','description':'Implement and verify strict normalization in release.py.','depends_on':[]}]},'''## Purpose, scope, and approved bases
One phase delivers US-001 under the approved E7 fixture spec and structure.
## Technical approach and implementation decisions
Use whole-string ASCII numeric matching or equivalent logic. Keep the fixed test file unchanged.
## Phases, deliverables, and dependencies
| Phase | Goal and deliverable | Dependencies | Related stories | Related criteria |
| --- | --- | --- | --- | --- |
| PH-01 | Implement and verify strict normalization in release.py. | None | US-001 | AC-001, AC-002 |
## Components, files, and change scope
| Component or path | Intended change | Phase | Restrictions or dependencies |
| --- | --- | --- | --- |
| release.py | Implement function | PH-01 | Only implementation file |
## Capacity, resources, and forecasts
One bounded native task and one independent phase review; no schedule commitment.
## Risks, assumptions, and validation
| Risk or assumption | Consequence | Response or validation | Point or phase | Expected evidence |
| --- | --- | --- | --- | --- |
| Test suite is fixed | False positives if modified | Hash comparison | PH-01 | Identical test bytes |
## Compliance and verification strategy
| Reference | Delivery or verification phase | Verification approach | Expected evidence |
| --- | --- | --- | --- |
| AC-001 | PH-01 final | Four-method suite, valid cases | Exact normalized strings |
| AC-002 | PH-01 final | Four-method suite, invalid cases | Exact exception types |
| NFR-001 → AC-001, AC-002 | PH-01 final | All four tests | Four executed tests pass |
| Constitution MUST | PH-01 | Git diff and hashes | Tests unchanged; verification nonmutating |
## Operational delivery preparation
Local Python only; no deployment.
## Review, learning, and adaptation
Sol task review and distinct Sol phase review assess actual cases, diff, and evidence.
## Open questions and readiness for tasks
No blocking question. Task scope is one file and one fixed command.
## References, approval, and amendments
Fixture-only approval; implementation remains separately authorized.''')
cmd=['python3','-B','-m','unittest','-v','test_release.py']
task={'id':'T-001','phase':'PH-01','story':'US-001','acceptance':['AC-001','AC-002'],'depends_on':[],'files':['release.py'],'steps':[{'id':'T-001.001','action':'Implement normalize_release to satisfy valid ASCII triples and exact error classes; run the fixed four-method suite without editing tests.','verification':{'command':cmd,'expected':'All four fixed tests execute and pass with exact outputs and exception types.'}}],'closure':'Final AC-001 and AC-002 behavior passes all four fixed tests; test_release.py remains unchanged.'}
tasks=doc('.specs/release-v1.2.3/tasks.md','tasks','TASKS-1.2.3',[plan],{'tasks':[task]},'''## Purpose and approved bases
The single task realizes the approved E7 spec and plan.
## Decomposition criteria
One bounded implementation file; fixed tests are existing verification, not writable scope.
## Task map
| Task | Phase | Story | Related criteria | Dependencies | Closure condition |
| --- | --- | --- | --- | --- | --- |
| T-001 | PH-01 | US-001 | AC-001, AC-002 | None | Final behavior and four fixed tests pass |
## Sequence and dependencies
T-001 is first and only task in PH-01.
## File scope and restrictions
release.py alone is writable. test_release.py and all decision files are read-only to Luna.
## Acceptance and quality coverage
| Criterion | Owning story | Contributing tasks | Final verification step | Quality reference |
| --- | --- | --- | --- | --- |
| AC-001 | US-001 | T-001 | T-001.001 | NFR-001 |
| AC-002 | US-001 | T-001 | T-001.001 | NFR-001 |
## Verification and evidence
Run python3 -B -m unittest -v test_release.py; retain four-case output, code fingerprint, and unchanged test hash.
## Risks, blockers, and readiness
No context omitted; strict whole-string and exception requirements survive canonical ACs and action.
## Closure and progress
Controller verify, Sol review, close, distinct phase review, then commit.
## Refinement, references, and approval
Synthetic E7-only decisions, with controller receipts and exact digests.''')
shutil.copyfile(P/'evals/reference/test_release.py',root/'test_release.py')
(root/'release.py').write_text('def normalize_release(value):\n    raise NotImplementedError("E7 baseline")\n')
(root/'.gitignore').write_text('__pycache__/\n')
git('add','.');git('commit','-m','chore(e7): establish disposable strict-normalization fixture')
print(json.dumps({'root':str(root),'head':git('rev-parse','HEAD'),'docs':[constitution,architecture,structure,roadmap,spec,plan,tasks],'test_sha256':__import__('hashlib').sha256((root/'test_release.py').read_bytes()).hexdigest()},indent=2))
