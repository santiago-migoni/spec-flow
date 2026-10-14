"""Fixtures shared by harness runtime tests."""

import json
from pathlib import Path

from harness.runtime.contracts import document_digest


class FakeAdapter:
    """Mechanics-only adapter for deterministic controller unit tests."""

    production = False

    def capabilities(self, report, owner):
        return {"mechanics_only": True, "report": report, "owner_session": owner}

    def acquire(self, run_id, release, owner):
        return {"mechanics_only": True, "run_id": run_id, "release": release, "owner": owner}

    def assert_lease(self, state):
        return None

    def attest_session(self, session_id, role, **kwargs):
        return {"session_id": session_id, "role": role, "agent_lifecycle": "completed"}

    def release(self, state):
        return None


class FixtureProductionAdapter(FakeAdapter):
    """Simulated attestation boundary; exercises production-only Engine checks."""

    production = True

    def __init__(self):
        self.leases = set()
        self.releases = 0

    def capabilities(self, report, owner):
        return {"fixture_attestation": True, "owner_session": {"session_id": owner, "model": "gpt-6-sol", "effort": "high"}}

    def acquire(self, run_id, release, owner):
        self.leases.add(run_id)
        return {"fixture_attestation": True, "run_id": run_id, "release": release, "owner": owner}

    def assert_lease(self, state):
        if state["status"] in {"completed", "abandoned"} and state["run_id"] not in self.leases:
            return None
        if state["run_id"] not in self.leases:
            from harness.runtime.codex_adapter import AdapterError
            raise AdapterError("ownership_lease_missing", "fixture lease is absent")

    def attest_no_spawn(self, owner_session, task_state, inventory):
        if not isinstance(inventory, dict) or inventory.get("owner_session") != owner_session or not inventory.get("inventory_reference") or inventory.get("agents") != []:
            from harness.runtime.codex_adapter import AdapterError
            raise AdapterError("native_inventory_invalid", "fixture inventory must be current, scoped, and empty")
        return {"owner_session": owner_session, "inventory_reference": inventory["inventory_reference"],
                "packet_marker": "SPEC_FLOW_PACKET_SHA256=" + task_state["packet_sha256"], "fixture_attestation": True}

    def attest_session(self, session_id, role, **kwargs):
        return {"session_id": session_id, "role": role, "model": "gpt-6-luna" if role == "implementer" else "gpt-6-sol",
                "effort": "high", "agent_lifecycle": "completed", "parent_session": kwargs.get("parent_session"),
                "agent_path": kwargs.get("agent_path"), "record_hashes": {"fixture": "sha256"}, "attestation_sha256": "fixture-hash"}

    def release(self, state):
        self.assert_lease(state)
        if state["run_id"] in self.leases:
            self.leases.discard(state["run_id"])
            self.releases += 1

    def takeover(self, state, new_owner):
        return {"previous_owner": {"session_id": state["owner"], "agent_lifecycle": "completed"},
                "new_owner": {"session_id": new_owner, "model": "gpt-6-sol", "effort": "high"},
                "native_agent": None}


def contract(kind, identifier, *, depends_on=None, **extra):
    return {
        "schema_version": 1,
        "kind": kind,
        "revision": "R00",
        "id": identifier,
        "depends_on": depends_on or [],
        **extra,
    }


def write_document(path, data, prose="Approved source decision."):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(prose + "\n\n```spec-flow\n" + json.dumps(data, indent=2) + "\n```\n", encoding="utf-8")
    return path


def task(identifier="T-001", *, phase="PH-01", story="US-001", dependencies=None, acceptance=None, command=None, inspection=None, files=None):
    verification = {"expected": "verification passed"}
    if inspection:
        verification["inspection"] = inspection
    else:
        verification["command"] = command or ["python3", "-c", "print('verification passed')"]
    return {
        "id": identifier,
        "phase": phase,
        "story": story,
        "acceptance": acceptance or ["AC-001"],
        "depends_on": dependencies or [],
        "files": files or ["src/example.py"],
        "steps": [{"id": identifier + ".001", "action": "Implement the behavior.", "verification": verification}],
        "closure": "The behavior and verification are complete.",
    }


def make_project(root, *, command=None, inspection=None, task_files=None, task_items=None):
    root = Path(root)
    task_items = task_items or [task(command=command, inspection=inspection, files=task_files)]
    phase_ids = list(dict.fromkeys(item["phase"] for item in task_items))
    phases = [
        {"id": phase_id, "description": "Deliver {}.".format(phase_id), "depends_on": phase_ids[index - 1:index]}
        for index, phase_id in enumerate(phase_ids)
    ]
    specs = root / ".specs"
    release = specs / "release-v1.2.3"
    constitution = write_document(specs / "constitution.md", contract("constitution", "CONSTITUTION"))
    roadmap = write_document(
        specs / "roadmap.md",
        contract("roadmap", "ROADMAP", depends_on=[{"path": ".specs/constitution.md", "digest": document_digest(constitution)}],
                 releases=[{"version": "v1.2.3", "objective": "Deliver the approved behavior.", "status": "planned"}]),
    )
    spec = write_document(
        release / "spec.md",
        contract("spec", "SPEC-1.2.3", depends_on=[{"path": ".specs/roadmap.md", "digest": document_digest(roadmap)}],
                 stories=[{"id": "US-001", "title": "Complete behavior", "description": "The user needs to complete the behavior."}],
                 acceptance=[{"id": "AC-001", "story": "US-001", "description": "The user can complete the behavior."}]),
    )
    plan = write_document(
        release / "plan.md",
        contract("plan", "PLAN-1.2.3", depends_on=[{"path": ".specs/release-v1.2.3/spec.md", "digest": document_digest(spec)}], phases=phases),
    )
    tasks = write_document(
        release / "tasks.md",
        contract("tasks", "TASKS-1.2.3", depends_on=[{"path": ".specs/release-v1.2.3/plan.md", "digest": document_digest(plan)}],
                 tasks=task_items),
    )
    (root / "src").mkdir(exist_ok=True)
    (root / "src" / "example.py").write_text("# initial\n", encoding="utf-8")
    return {
        "constitution": constitution,
        "roadmap": roadmap,
        "spec": spec,
        "plan": plan,
        "tasks": tasks,
        "release": release,
    }


def approve_release(engine, docs):
    for name in ("constitution", "roadmap", "spec", "plan", "tasks"):
        engine.dispatch("approve", {
            "path": docs[name].resolve().relative_to(engine.root).as_posix(),
            "actor": "user",
            "statement": "I approve this document for this release.",
            "source": "conversation",
        })


def start_run(engine):
    return engine.dispatch("start", {
        "release": "1.2.3",
        "owner": "sol-session-1",
        "phases": ["PH-01"],
        "authorization": {"actor": "user", "statement": "Execute the approved PH-01 tasks.", "source": "conversation"},
        "capabilities": {"models": ["gpt-6-sol", "gpt-6-luna"]},
    })["run_id"]
