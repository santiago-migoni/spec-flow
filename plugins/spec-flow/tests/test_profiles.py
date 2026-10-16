"""Configurable role profiles are validated and frozen per run."""
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from harness.runtime.engine import Engine, EngineError
from harness.runtime.codex_adapter import NativeCodexAdapter, AdapterError
from helpers import FakeAdapter, make_project, approve_release, start_run

DEFAULTS = {'orchestrator': {'id': 'gpt-6.1-sol', 'effort': 'low'},
            'implementer': {'id': 'gpt-6-luna', 'effort': 'high'},
            'reviewer': {'id': 'gpt-6.1-sol', 'effort': 'medium'}}

class ProfileTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.docs = make_project(self.root)
        self.engine = Engine(self.root, adapter=FakeAdapter())
        self.engine.dispatch('initialize', {})
        self.config = self.root / '.spec-flow/config.json'

    def change(self, profiles):
        config = json.loads(self.config.read_text())
        config['profiles'] = profiles
        self.config.write_text(json.dumps(config))

    def test_new_defaults_and_custom_profile_validation(self):
        self.assertEqual(json.loads(self.config.read_text())['profiles'], DEFAULTS)
        custom = json.loads(json.dumps(DEFAULTS))
        custom['implementer'] = {'id': 'custom-model', 'effort': 'medium'}
        self.change(custom)
        self.engine.dispatch('initialize', {})
        self.assertEqual(json.loads(self.config.read_text())['profiles'], custom)
        for invalid in ({}, {**custom, 'reviewer': {'id': ' ', 'effort': 'medium'}},
                        {**custom, 'reviewer': {'id': 'custom-model', 'effort': 'automatic'}},
                        {**custom, 'reviewer': {'id': 'custom-model', 'effort': 'medium', 'fallback': True}}):
            self.change(invalid)
            with self.assertRaises(EngineError):
                self.engine.dispatch('initialize', {})

    def test_run_profiles_survive_config_edits_and_state_rebuild(self):
        approve_release(self.engine, self.docs)
        run = start_run(self.engine)
        state = self.engine._state(run)
        self.assertEqual(state['profiles'], DEFAULTS)
        changed = json.loads(json.dumps(DEFAULTS));changed['reviewer']['effort'] = 'high'
        self.change(changed)
        (self.root / '.spec-flow/runs' / run / 'state.json').unlink()
        self.assertEqual(Engine(self.root, adapter=FakeAdapter())._state(run)['profiles'], DEFAULTS)
        prepared = self.engine.dispatch('prepare', {'run_id': run, 'owner': 'sol-session-1', 'task_id': 'T-001'})
        packet = json.loads(Path(prepared['packet_path']).read_text())
        self.assertEqual(packet['profiles'], DEFAULTS)

    def test_legacy_run_uses_historical_profiles_not_current_defaults(self):
        approve_release(self.engine, self.docs)
        run = start_run(self.engine)
        log = self.root / '.spec-flow/runs' / run / 'events.jsonl'
        rows = [json.loads(line) for line in log.read_text().splitlines()]
        rows[0]['data'].pop('profiles', None)
        log.write_text(''.join(json.dumps(row)+'\n' for row in rows))
        state = self.engine._state(run)
        self.assertEqual(state['profiles']['orchestrator'], {'id': 'gpt-6-sol', 'effort': 'high'})
        self.assertFalse(state['profile_snapshot'])

    def test_native_adapter_uses_exact_configured_role_and_catalog(self):
        adapter = NativeCodexAdapter(self.root)
        adapter.configure_profiles(DEFAULTS, require_catalog=True)
        sessions = self.root / 'host/sessions';sessions.mkdir(parents=True)
        path = sessions/'rollout-owner.jsonl'
        rows = [{'type': 'session_meta', 'payload': {'id': 'owner', 'source': {}}},
                {'type': 'turn_context', 'payload': {'model': 'gpt-6.1-sol', 'collaboration_mode': {'settings': {'reasoning_effort': 'low'}}}}]
        path.write_text(''.join(json.dumps(row)+'\n' for row in rows))
        report = {'inventory_reference': 'native-probes', 'operations': {x: True for x in adapter.OPERATIONS},
                  'probe_evidence': {x: 'native-result' for x in adapter.OPERATIONS},
                  'model_catalog_reference': 'host model inventory',
                  'model_catalog': [{'id': 'gpt-6.1-sol', 'reasoning_efforts': ['low', 'medium']},
                                    {'id': 'gpt-6-luna', 'reasoning_efforts': ['high']}]}
        with patch.dict(os.environ, {'CODEX_HOME': str(self.root/'host')}):
            self.assertEqual(adapter.capabilities(report, 'owner')['owner_session']['effort'], 'low')
            report['model_catalog'][0]['reasoning_efforts'] = ['high']
            with self.assertRaises(AdapterError):adapter.capabilities(report, 'owner')
            rows[1]['payload']['model'] = 'gpt-6-sol'
            path.write_text(''.join(json.dumps(row)+'\n' for row in rows))
            with self.assertRaises(AdapterError):adapter.attest_session('owner', 'orchestrator')

    def test_initialize_preserves_old_config_and_rejects_retry_budget_edit(self):
        from harness.runtime.profiles import LEGACY_PROFILES
        self.change(LEGACY_PROFILES)
        before = self.config.read_bytes()
        self.engine.dispatch('initialize', {})
        self.assertEqual(self.config.read_bytes(), before)
        config = json.loads(before);config['retry_limit'] = 4
        self.config.write_text(json.dumps(config))
        with self.assertRaises(EngineError):self.engine.dispatch('initialize', {})

    def test_native_actions_use_pinned_profile_after_new_config(self):
        class SpyAdapter(FakeAdapter):
            production = True
            def attest_session(self, session_id, role, **kwargs):
                return {'session_id': session_id, 'role': role, **self.profiles[role], 'agent_lifecycle': 'completed'}
        adapter = SpyAdapter()
        engine = Engine(self.root, adapter=adapter)
        approve_release(engine, self.docs)
        run = start_run(engine)
        changed = json.loads(json.dumps(DEFAULTS));changed['orchestrator'] = {'id': 'another-model', 'effort': 'high'}
        self.change(changed)
        engine.dispatch('prepare', {'run_id': run, 'owner': 'sol-session-1', 'task_id': 'T-001'})
        self.assertEqual(adapter.profiles, DEFAULTS)
        # A repeated start attests and acquires against the same snapshot.
        self.assertEqual(start_run(engine), run)
        self.assertEqual(adapter.profiles, DEFAULTS)

    def test_corrupt_run_snapshot_fails_instead_of_using_defaults(self):
        approve_release(self.engine, self.docs)
        run = start_run(self.engine)
        log = self.root / '.spec-flow/runs' / run / 'events.jsonl'
        rows = [json.loads(line) for line in log.read_text().splitlines()]
        rows[0]['data']['profiles'] = None
        log.write_text(''.join(json.dumps(row)+'\n' for row in rows))
        with self.assertRaises(EngineError) as ctx:self.engine._state(run)
        self.assertEqual(ctx.exception.code, 'corrupt_log')

    def test_new_run_uses_edited_profile_and_packets_have_exact_hash(self):
        import hashlib
        chosen = json.loads(json.dumps(DEFAULTS));chosen['implementer'] = {'id': 'custom-model', 'effort': 'low'}
        self.change(chosen)
        approve_release(self.engine, self.docs)
        run = start_run(self.engine)
        packet = self.engine.dispatch('prepare', {'run_id': run, 'owner': 'sol-session-1', 'task_id': 'T-001'})
        data = json.loads(Path(packet['packet_path']).read_text())
        self.assertEqual(data['profiles'], chosen)
        recorded = data.pop('packet_sha256')
        self.assertEqual(hashlib.sha256(json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest(), recorded)

    def test_legacy_packets_restore_without_new_fields(self):
        approve_release(self.engine, self.docs)
        run = start_run(self.engine)
        log = self.root / '.spec-flow/runs' / run / 'events.jsonl'
        rows = [json.loads(line) for line in log.read_text().splitlines()]
        rows[0]['data'].pop('profiles')
        log.write_text(''.join(json.dumps(row)+'\n' for row in rows))
        packet = self.engine.dispatch('prepare', {'run_id': run, 'owner': 'sol-session-1', 'task_id': 'T-001'})
        path = Path(packet['packet_path']);before = path.read_bytes()
        self.assertNotIn('profiles', json.loads(before))
        path.unlink()
        self.engine.dispatch('restore-packet', {'run_id': run, 'owner': 'sol-session-1', 'kind': 'task', 'task_id': 'T-001'})
        self.assertEqual(path.read_bytes(), before)

    def test_configure_profiles_is_atomic_idempotent_and_does_not_rewrite_runs(self):
        approve_release(self.engine, self.docs)
        run = start_run(self.engine)
        log = self.root / '.spec-flow/runs' / run / 'events.jsonl'
        before = log.read_bytes()
        chosen = json.loads(json.dumps(DEFAULTS));chosen['reviewer']['effort'] = 'high'
        result = self.engine.dispatch('configure-profiles', {'profiles': chosen})
        self.assertTrue(result['changed'])
        self.assertEqual(result['applies_to'], 'new_runs_only')
        mtime = self.config.stat().st_mtime_ns
        self.assertFalse(self.engine.dispatch('configure-profiles', {'profiles': chosen})['changed'])
        self.assertEqual(self.config.stat().st_mtime_ns, mtime)
        self.assertEqual(log.read_bytes(), before)
        self.assertEqual(self.engine._state(run)['profiles'], DEFAULTS)
        with self.assertRaises(EngineError):self.engine.dispatch('configure-profiles', {'profiles': {}})
        self.assertEqual(json.loads(self.config.read_text())['profiles'], chosen)

    def test_missing_model_inventory_and_unavailable_model_fail_before_run_creation(self):
        adapter = NativeCodexAdapter(self.root)
        adapter.configure_profiles(DEFAULTS, require_catalog=True)
        report = {'inventory_reference': 'probes', 'operations': {x: True for x in adapter.OPERATIONS},
                  'probe_evidence': {x: 'evidence' for x in adapter.OPERATIONS}}
        with self.assertRaises(AdapterError) as ctx:adapter.capabilities(report, 'owner')
        self.assertEqual(ctx.exception.code, 'model_catalog_required')
        report.update(model_catalog_reference='current-host', model_catalog=[{'id': 'unavailable-alternative', 'reasoning_efforts': ['low']}])
        with self.assertRaises(AdapterError) as ctx:adapter.capabilities(report, 'owner')
        self.assertEqual(ctx.exception.code, 'model_unavailable')
        engine = Engine(self.root)
        approve_release(engine, self.docs)
        with self.assertRaises(EngineError) as ctx:
            engine.dispatch('start', {'release': 'v1.2.3', 'owner': 'owner', 'phases': ['PH-01'],
                                     'authorization': {'actor': 'user', 'statement': 'Execute PH-01.', 'source': 'test'},
                                     'capabilities': report})
        self.assertEqual(ctx.exception.code, 'model_unavailable')
        self.assertEqual(engine.store.run_ids(), [])

    def test_duplicate_catalog_and_snapshot_values_are_rejected(self):
        adapter = NativeCodexAdapter(self.root);adapter.configure_profiles(DEFAULTS, require_catalog=True)
        report = {'model_catalog_reference': 'host', 'model_catalog': [
            {'id': 'gpt-6.1-sol', 'reasoning_efforts': ['low']},
            {'id': 'gpt-6.1-sol', 'reasoning_efforts': ['medium']}]}
        with self.assertRaises(AdapterError) as ctx:adapter._check_model_catalog(report)
        self.assertEqual(ctx.exception.code, 'model_catalog_invalid')
