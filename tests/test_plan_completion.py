"""Observable closure, intake and migration behavior for schema 5."""

import copy
import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from test_project_os import PROJECT_OS, file_hashes, run_cli, strip_schema5_records, write_program_definition


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


class PlanCompletionTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        initialized = run_cli('init', '--target', str(self.root), '--packs', 'none')
        self.assertEqual(initialized.returncode, 0, initialized.stderr)
        self.index_path = self.root / '.agents/plans/index.json'
        self.requests_path = self.root / '.agents/requests.json'
        self.contract_path = self.root / '.agents/plans/001.json'
        self.checkpoint = self.root / 'checkpoint-draft.md'
        self.checkpoint.write_text('# Checkpoint\n\nExecution state: idle.\nActive plan: none.\n\nThe recorded outcome is verified. Next: review planned work.\n')
        self.plan = self.add_plan('001', 'active', verified=True)

    def add_plan(self, identifier, status, verified=False):
        md = f'.agents/plans/{identifier}.md'
        contract = f'.agents/plans/{identifier}.json'
        proof = f'.agents/evidence/{identifier}.md'
        (self.root / md).write_text(f'# Plan {identifier}\n\nOutcome: verify local behavior.\n')
        (self.root / proof).write_text('Synthetic test result: the target sample matches the expected behavior.\n')
        evidence = {'path': proof, 'sha256': 'sha256:' + hashlib.sha256((self.root / proof).read_bytes()).hexdigest(),
                    'checked_on': '2026-09-30', 'target': 'local', 'revision': 1}
        gate = {'id': 'sample', 'condition': 'The sample behaves as requested.', 'evidence_class': 'source',
                'target': 'local', 'status': 'verified' if verified else 'pending', 'evidence': [evidence] if verified else [],
                'next_action': '' if verified else 'Run the sample check.', 'reason': ''}
        write_json(self.root / contract, {'schema_version': 1, 'plan_id': identifier, 'revision': 1, 'gates': [gate]})
        plan = {'id': identifier, 'status': status, 'path': md, 'outcome': 'Verify local behavior.', 'contract_path': contract}
        index = json.loads(self.index_path.read_text())
        index['plans'].append(plan)
        index['next_id'] = max(index['next_id'], int(identifier) + 1)
        if status == 'active':
            index.update(execution_state='running', active_plan=identifier)
        write_json(self.index_path, index)
        return plan

    def complete(self, *extra):
        return run_cli('plan', 'complete', '--target', str(self.root), '--id', '001', '--checkpoint', str(self.checkpoint), *extra)

    def check(self):
        return run_cli('check', '--target', str(self.root))

    def request(self, status='captured', relation='same_outcome', target=None, gates=None, decision=''):
        value = {'id': 'R-001', 'recorded_on': '2026-09-30', 'source_text': 'Also verify the extra behavior.',
                 'interpretation': 'Include the new required behavior.', 'origin_plan': '001', 'target_plan': target,
                 'relation': relation, 'status': status, 'gate_ids': gates or [], 'decision': decision}
        write_json(self.requests_path, {'schema_version': 1, 'next_id': 2, 'requests': [value]})
        return value

    def test_pending_remote_migration_blocks_done_after_local_success(self):
        contract = json.loads(self.contract_path.read_text())
        contract['gates'].append({'id': 'migration', 'condition': 'The remote migration is applied.', 'evidence_class': 'production',
                                  'target': 'production', 'status': 'pending', 'evidence': [], 'next_action': 'Inspect the target schema.', 'reason': ''})
        write_json(self.contract_path, contract)
        before = file_hashes(self.root)
        self.assertEqual(self.check().returncode, 0)
        status = run_cli('plan', 'status', '--target', str(self.root), '--json')
        report = json.loads(status.stdout)
        self.assertFalse(report['can_complete'])
        self.assertIn('migration', ' '.join(report['blockers']))
        result = self.complete()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('migration', result.stderr)
        self.assertEqual(file_hashes(self.root), before)

    def test_require_ready_fails_with_pending_host_even_when_structural_check_passes(self):
        contract = json.loads(self.contract_path.read_text())
        contract['gates'].append({'id': 'host', 'condition': 'Fresh session recovery works.', 'evidence_class': 'host',
                                  'target': 'fresh Codex', 'status': 'pending', 'evidence': [],
                                  'next_action': 'Run fresh-session recovery before publication.', 'reason': 'No host acceptance yet.'})
        write_json(self.contract_path, contract)
        before = file_hashes(self.root)
        self.assertEqual(self.check().returncode, 0)
        result = run_cli('plan', 'status', '--target', str(self.root), '--require-ready', '--json')
        self.assertEqual(result.returncode, 1)
        report = json.loads(result.stdout)
        self.assertEqual(report['readiness'], 'NOT_READY')
        self.assertFalse(report['ready'])
        self.assertIn('Fresh session', ' '.join(report['readiness_blockers']))
        self.assertEqual(file_hashes(self.root), before)

    def test_ready_applies_to_named_active_and_valid_completed_outcome(self):
        result = run_cli('plan', 'status', '--target', str(self.root), '--require-ready', '--json')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(json.loads(result.stdout)['ready'])
        self.assertEqual(self.complete().returncode, 0)
        result = run_cli('plan', 'status', '--target', str(self.root), '--id', '001', '--require-ready', '--json')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(json.loads(result.stdout)['ready'])
        self.assertFalse(json.loads(result.stdout)['can_complete'])
        (self.root / '.agents/evidence/001.md').write_text('Changed proof.\n')
        result = run_cli('plan', 'status', '--target', str(self.root), '--id', '001', '--require-ready', '--json')
        self.assertEqual(result.returncode, 1)
        self.assertFalse(json.loads(result.stdout)['ready'])

    def test_unresolved_request_and_planned_status_are_not_ready(self):
        self.request('needs_clarification')
        result = run_cli('plan', 'status', '--target', str(self.root), '--require-ready', '--json')
        self.assertEqual(result.returncode, 1)
        self.assertIn('R-001', ' '.join(json.loads(result.stdout)['readiness_blockers']))
        self.add_plan('002', 'planned', verified=True)
        result = run_cli('plan', 'status', '--target', str(self.root), '--id', '002', '--require-ready', '--json')
        self.assertEqual(result.returncode, 1)
        self.assertFalse(json.loads(result.stdout)['ready'])

    def test_dry_run_then_close_records_proof_and_does_not_activate_successor(self):
        self.add_plan('002', 'planned')
        self.request('implemented', target='001', gates=['sample'])
        before = file_hashes(self.root)
        preview = self.complete('--dry-run')
        self.assertEqual(preview.returncode, 0, preview.stdout + preview.stderr)
        self.assertIn('"checkpoint"', preview.stdout)
        self.assertEqual(file_hashes(self.root), before)
        applied = self.complete()
        self.assertEqual(applied.returncode, 0, applied.stdout + applied.stderr)
        index = json.loads(self.index_path.read_text())
        self.assertEqual(index['execution_state'], 'idle')
        self.assertIsNone(index['active_plan'])
        self.assertEqual(index['plans'][0]['status'], 'done')
        self.assertEqual(index['plans'][0]['completion']['revision'], 1)
        self.assertEqual(index['plans'][0]['completion']['requests'][0]['id'], 'R-001')
        self.assertEqual(index['plans'][1]['status'], 'planned')
        self.assertEqual((self.root / '.agents/STATE.md').read_text(), self.checkpoint.read_text())
        self.assertEqual(self.check().returncode, 0)
        self.assertNotEqual(self.complete().returncode, 0)

    def test_manual_done_without_receipt_fails_check(self):
        index = json.loads(self.index_path.read_text())
        index['plans'][0]['status'] = 'done'
        index.update(execution_state='idle', active_plan=None)
        write_json(self.index_path, index)
        checked = self.check()
        self.assertEqual(checked.returncode, 1)
        self.assertIn('completion receipt', checked.stdout)

    def test_unrouted_conflicting_and_integrated_requests_block_closure(self):
        for status in ('captured', 'needs_clarification', 'integrated'):
            with self.subTest(status=status):
                self.request(status, target='001' if status == 'integrated' else None, gates=['sample'] if status == 'integrated' else [])
                self.assertEqual(self.check().returncode, 0)
                before = file_hashes(self.root)
                result = self.complete()
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('R-001', result.stderr)
                self.assertEqual(file_hashes(self.root), before)

    def test_required_dependency_cannot_be_routed_to_successor(self):
        self.add_plan('002', 'planned')
        for relation in ('same_outcome', 'prerequisite'):
            with self.subTest(relation=relation):
                self.request('integrated', relation, '002', ['sample'])
                result = self.check()
                self.assertEqual(result.returncode, 1)
                self.assertIn('required dependency', result.stdout)
                self.assertNotEqual(self.complete().returncode, 0)

    def test_independent_successor_does_not_invalidate_predecessor_receipt(self):
        self.add_plan('002', 'planned', verified=True)
        request = self.request('integrated', 'independent', '002', ['sample'], 'The new outcome is independent and follows plan 001.')
        result = self.complete()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        request['status'] = 'implemented'
        write_json(self.requests_path, {'schema_version': 1, 'next_id': 2, 'requests': [request]})
        self.assertEqual(self.check().returncode, 0)

    def test_implemented_requires_verified_linked_gates(self):
        self.add_plan('002', 'planned')
        self.request('implemented', 'independent', '002', ['sample'])
        checked = self.check()
        self.assertEqual(checked.returncode, 1)
        self.assertIn('implemented requires verified', checked.stdout)

    def test_withdrawal_requires_explicit_recorded_decision(self):
        self.request('withdrawn')
        self.assertEqual(self.check().returncode, 1)
        self.request('withdrawn', decision='The user explicitly cancelled this addition in the current message.')
        self.assertEqual(self.complete().returncode, 0)

    def test_evidence_missing_changed_stale_or_wrong_target_blocks_closure(self):
        original = json.loads(self.contract_path.read_text())
        for mode in ('missing', 'changed', 'revision', 'target', 'date'):
            with self.subTest(mode=mode):
                contract = copy.deepcopy(original)
                proof = contract['gates'][0]['evidence'][0]
                if mode == 'missing': proof['path'] = '.agents/evidence/absent.md'
                if mode == 'changed': proof['sha256'] = 'sha256:' + '0' * 64
                if mode == 'revision': proof['revision'] = 2
                if mode == 'target': proof['target'] = 'production'
                if mode == 'date': proof['checked_on'] = '2026-99-31'
                write_json(self.contract_path, contract)
                before = file_hashes(self.root)
                result = self.complete()
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(file_hashes(self.root), before)

    def test_pending_and_not_applicable_require_their_explanation_fields(self):
        original = json.loads(self.contract_path.read_text())
        for status in ('pending', 'not_applicable'):
            with self.subTest(status=status):
                contract = copy.deepcopy(original)
                gate = contract['gates'][0]
                gate.update(status=status, evidence=[], next_action='', reason='')
                write_json(self.contract_path, contract)
                self.assertEqual(self.check().returncode, 1)
                gate['next_action' if status == 'pending' else 'reason'] = 'This outcome is bounded to source preparation.'
                write_json(self.contract_path, contract)
                self.assertEqual(self.check().returncode, 0)

    def test_checkpoint_must_match_idle_transition(self):
        self.checkpoint.write_text('# Checkpoint\n\nExecution state: running.\nActive plan: 001.\n')
        before = file_hashes(self.root)
        self.assertNotEqual(self.complete().returncode, 0)
        self.assertEqual(file_hashes(self.root), before)

    def test_status_requires_id_without_single_active_plan(self):
        self.assertEqual(self.complete().returncode, 0)
        result = run_cli('plan', 'status', '--target', str(self.root), '--json')
        self.assertNotEqual(result.returncode, 0)
        explicit = run_cli('plan', 'status', '--target', str(self.root), '--id', '001', '--json')
        self.assertEqual(explicit.returncode, 0)
        self.assertEqual(json.loads(explicit.stdout)['status'], 'done')

    def test_unsafe_contract_or_evidence_path_and_symlink_are_rejected(self):
        for mode in ('outside', 'symlink', 'collision'):
            with self.subTest(mode=mode):
                index = json.loads(self.index_path.read_text())
                if mode == 'outside': index['plans'][0]['contract_path'] = '../outside.json'
                elif mode == 'collision': index['plans'][0]['contract_path'] = '.agents/requests.json'
                else:
                    link = self.root / '.agents/plans/link.json'
                    link.symlink_to(self.contract_path)
                    index['plans'][0]['contract_path'] = '.agents/plans/link.json'
                write_json(self.index_path, index)
                self.assertNotEqual(self.complete().returncode, 0)
                index['plans'][0]['contract_path'] = '.agents/plans/001.json'
                write_json(self.index_path, index)
        contract = json.loads(self.contract_path.read_text())
        contract['gates'][0]['evidence'][0]['path'] = '../outside.md'
        write_json(self.contract_path, contract)
        self.assertEqual(self.check().returncode, 1)

    def test_receipt_detects_later_contract_evidence_or_scoped_request_edits(self):
        self.request('implemented', target='001', gates=['sample'])
        self.assertEqual(self.complete().returncode, 0)
        request_registry = json.loads(self.requests_path.read_text())
        request_registry['requests'][0]['interpretation'] = 'A later edited requirement.'
        write_json(self.requests_path, request_registry)
        checked = self.check()
        self.assertEqual(checked.returncode, 1)
        self.assertIn('receipt no longer matches', checked.stdout)

    def test_preview_concurrent_change_aborts_without_overwriting_it(self):
        before = file_hashes(self.root)
        original = PROJECT_OS.print_transaction_preview
        def change_before_apply(*args):
            self.request('needs_clarification')
            return original(*args)
        with mock.patch.object(PROJECT_OS, 'print_transaction_preview', side_effect=change_before_apply):
            with self.assertRaisesRegex(PROJECT_OS.ProjectOSError, 'changed'):
                PROJECT_OS.complete_plan(self.root, '001', self.checkpoint, False)
        after = file_hashes(self.root)
        before.pop('.agents/requests.json')
        after.pop('.agents/requests.json')
        self.assertEqual(after, before)
        self.assertEqual(json.loads(self.requests_path.read_text())['requests'][0]['status'], 'needs_clarification')

    def test_write_and_final_validation_failures_roll_back(self):
        for boundary in ('atomic_write_text', 'require_passing_check'):
            with self.subTest(boundary=boundary):
                before = file_hashes(self.root)
                with mock.patch.object(PROJECT_OS, boundary, side_effect=PROJECT_OS.ProjectOSError('injected failure')):
                    with self.assertRaises(PROJECT_OS.ProjectOSError):
                        PROJECT_OS.complete_plan(self.root, '001', self.checkpoint, False)
                self.assertEqual(file_hashes(self.root), before)

    def test_post_validation_dependency_change_is_detected_and_preserved(self):
        before = file_hashes(self.root)
        original = PROJECT_OS.require_passing_check
        proof = self.root / '.agents/evidence/001.md'
        def check_then_change(*args):
            original(*args)
            proof.write_text('Concurrent proof replacement.\n')
        with mock.patch.object(PROJECT_OS, 'require_passing_check', side_effect=check_then_change):
            with self.assertRaises(PROJECT_OS.ProjectOSError):
                PROJECT_OS.complete_plan(self.root, '001', self.checkpoint, False)
        after = file_hashes(self.root)
        before.pop('.agents/evidence/001.md')
        after.pop('.agents/evidence/001.md')
        self.assertEqual(after, before)
        self.assertEqual(proof.read_text(), 'Concurrent proof replacement.\n')

    def test_checkpoint_change_before_write_or_after_validation_is_preserved(self):
        for boundary in ('print_transaction_preview', 'require_passing_check'):
            with self.subTest(boundary=boundary):
                before = file_hashes(self.root)
                original = getattr(PROJECT_OS, boundary)
                def change_draft(*args):
                    result = original(*args)
                    self.checkpoint.write_text('Concurrent checkpoint edit.\n')
                    return result
                with mock.patch.object(PROJECT_OS, boundary, side_effect=change_draft):
                    with self.assertRaisesRegex(PROJECT_OS.ProjectOSError, 'Checkpoint draft changed'):
                        PROJECT_OS.complete_plan(self.root, '001', self.checkpoint, False)
                after = file_hashes(self.root)
                before.pop('checkpoint-draft.md')
                after.pop('checkpoint-draft.md')
                self.assertEqual(after, before)
                self.assertEqual(self.checkpoint.read_text(), 'Concurrent checkpoint edit.\n')
                self.checkpoint.write_text('# Checkpoint\n\nExecution state: idle.\nActive plan: none.\n')

    def test_repeated_validation_cannot_replace_original_request_snapshot(self):
        self.request('implemented', target='001', gates=['sample'])
        before = file_hashes(self.root)
        original = PROJECT_OS.validate_plan_records
        calls = 0
        def modify_between_reads(*args, **kwargs):
            nonlocal calls
            result = original(*args, **kwargs)
            if kwargs.get('snapshots') is not None or len(args) > 3 and args[3] is not None:
                calls += 1
                if calls == 1:
                    self.request('implemented', target='001', gates=['sample'], decision='Concurrent accepted record edit.')
            return result
        with mock.patch.object(PROJECT_OS, 'validate_plan_records', side_effect=modify_between_reads):
            with self.assertRaisesRegex(PROJECT_OS.ProjectOSError, 'changed'):
                PROJECT_OS.complete_plan(self.root, '001', self.checkpoint, False)
        after = file_hashes(self.root)
        before.pop('.agents/requests.json')
        after.pop('.agents/requests.json')
        self.assertEqual(after, before)

    def test_contract_hardlink_alias_and_nonempty_independent_routing_are_enforced(self):
        alias = self.root / '.agents/plans/alias.json'
        os.link(self.requests_path, alias)
        index = json.loads(self.index_path.read_text())
        index['plans'][0]['contract_path'] = '.agents/plans/alias.json'
        write_json(self.index_path, index)
        result = self.check()
        self.assertEqual(result.returncode, 1)
        self.assertIn('aliases', result.stdout)
        index['plans'][0]['contract_path'] = '.agents/plans/001.json'
        write_json(self.index_path, index)
        self.add_plan('002', 'planned')
        self.request('integrated', 'independent', '002', ['sample'])
        self.assertEqual(self.check().returncode, 1)

    def test_partial_second_write_failure_restores_both_record_owners(self):
        before = file_hashes(self.root)
        original = PROJECT_OS.atomic_write_text
        calls = 0
        def fail_second(*args, **kwargs):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise PROJECT_OS.ProjectOSError('injected second write failure')
            return original(*args, **kwargs)
        with mock.patch.object(PROJECT_OS, 'atomic_write_text', side_effect=fail_second):
            with self.assertRaises(PROJECT_OS.ProjectOSError):
                PROJECT_OS.complete_plan(self.root, '001', self.checkpoint, False)
        self.assertEqual(file_hashes(self.root), before)

    def test_schema4_upgrade_preserves_history_and_requires_contract_on_resume(self):
        index = json.loads(self.index_path.read_text())
        index['plans'][0].pop('contract_path')
        old_closed = dict(self.plan, id='002', status='done', path='.agents/plans/002.md')
        old_closed.pop('contract_path')
        (self.root / old_closed['path']).write_text('# Historical closed plan\n\nUnverified old acceptance stays historical.\n')
        index['plans'].append(old_closed)
        write_json(self.index_path, index)
        system_path = self.root / '.agents/SYSTEM.json'
        system = json.loads(system_path.read_text())
        strip_schema5_records(self.root, system)
        system.update(schema_version=4, project_os_version='2.1.1')
        write_json(system_path, system)
        before = file_hashes(self.root)
        preview = run_cli('upgrade', '--target', str(self.root), '--dry-run')
        self.assertEqual(preview.returncode, 0, preview.stdout + preview.stderr)
        self.assertEqual(file_hashes(self.root), before)
        applied = run_cli('upgrade', '--target', str(self.root))
        self.assertEqual(applied.returncode, 0, applied.stdout + applied.stderr)
        self.assertEqual((self.root / old_closed['path']).read_text(), '# Historical closed plan\n\nUnverified old acceptance stays historical.\n')
        index = json.loads(self.index_path.read_text())
        self.assertEqual(index['legacy_closed'], {'002': 'done'})
        self.assertEqual(index['legacy_uncontracted'], ['001'])
        self.assertEqual(self.check().returncode, 0)
        self.assertNotEqual(self.complete().returncode, 0)
        repeated_before = file_hashes(self.root)
        repeated = run_cli('upgrade', '--target', str(self.root))
        self.assertEqual(repeated.returncode, 0)
        self.assertEqual(file_hashes(self.root), repeated_before)
        index['plans'][0]['contract_path'] = '.agents/plans/001.json'
        index['legacy_uncontracted'].remove('001')
        write_json(self.index_path, index)
        self.assertEqual(self.complete().returncode, 0)

    def test_schema4_upgrade_aborts_on_new_file_collision(self):
        for collision in ('requests.json', 'WORKFLOW.md'):
            with self.subTest(collision=collision):
                system_path = self.root / '.agents/SYSTEM.json'
                system = json.loads(system_path.read_text())
                strip_schema5_records(self.root, system)
                system.update(schema_version=4, project_os_version='2.1.1')
                write_json(system_path, system)
                (self.root / '.agents' / collision).write_text('Repository-owned existing file.\n')
                before = file_hashes(self.root)
                result = run_cli('upgrade', '--target', str(self.root))
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(file_hashes(self.root), before)

    def test_legacy_standard_and_program_migrations_preserve_custom_record_paths(self):
        for schema in (2, 3, 4):
            for mode in ('standard', 'program'):
                with self.subTest(schema=schema, mode=mode), tempfile.TemporaryDirectory() as temporary:
                    root = Path(temporary).resolve()
                    self.assertEqual(run_cli('init', '--target', str(root), '--packs', 'none').returncode, 0)
                    if mode == 'program':
                        definition = write_program_definition(root)
                        started = run_cli('program', 'start', '--target', str(root), '--definition', str(definition))
                        self.assertEqual(started.returncode, 0, started.stdout + started.stderr)
                    system_path = root / '.agents/SYSTEM.json'
                    system = json.loads(system_path.read_text())
                    strip_schema5_records(root, system)
                    system.update(schema_version=schema, project_os_version='2.1.1' if schema == 4 else '2.0.5')
                    if schema in (2, 3):
                        reusable = root / system['paths'].pop('reusable_knowledge')
                        reusable.unlink()
                        reusable.parent.rmdir()
                        shared = root / '.agents/knowledge/shared/failures.json'
                        shared.parent.mkdir()
                        write_json(shared, {'schema_version': 1, 'knowledge_version': system['project_os_version'], 'packs': ['core'], 'overlays': [], 'entries': []})
                        system['paths']['shared_knowledge'] = shared.relative_to(root).as_posix()
                        system['managed_knowledge'] = {}
                    arguments = []
                    if schema == 2:
                        system['mode'] = 'full' if mode == 'program' else 'lite'
                        system.pop('active_program')
                        system['paths'].pop('history_index')
                        if mode == 'program':
                            (root / '.agents/history').mkdir()
                            arguments = ['--legacy-program-state', 'active']
                    custom = root / '.agents/custom'
                    custom.mkdir()
                    agents = root / 'AGENTS.md'
                    guidance = agents.read_text()
                    preserved = {}
                    for key in ('context', 'state', 'plans'):
                        old = system['paths'][key]
                        new = f'.agents/custom/{key}.json' if key == 'plans' else f'.agents/custom/{key}.md'
                        (root / old).rename(root / new)
                        system['paths'][key] = new
                        guidance = guidance.replace(old, new)
                        if key != 'plans':
                            preserved[new] = (root / new).read_bytes()
                    agents.write_text(guidance)
                    if mode == 'program':
                        preserved[system['paths']['program']] = (root / system['paths']['program']).read_bytes()
                    write_json(system_path, system)
                    before = file_hashes(root)
                    preview = run_cli('upgrade', '--target', str(root), *arguments, '--dry-run')
                    self.assertEqual(preview.returncode, 0, preview.stdout + preview.stderr)
                    self.assertEqual(file_hashes(root), before)
                    applied = run_cli('upgrade', '--target', str(root), *arguments)
                    self.assertEqual(applied.returncode, 0, applied.stdout + applied.stderr)
                    updated = json.loads(system_path.read_text())
                    self.assertEqual(updated['mode'], mode)
                    self.assertEqual(updated['schema_version'], 5)
                    for key in ('context', 'state', 'plans'):
                        self.assertEqual(updated['paths'][key], system['paths'][key])
                    for relative, content in preserved.items():
                        self.assertEqual((root / relative).read_bytes(), content)
                    self.assertEqual(run_cli('check', '--target', str(root)).returncode, 0)
                    after = file_hashes(root)
                    repeated = run_cli('upgrade', '--target', str(root))
                    self.assertEqual(repeated.returncode, 0, repeated.stdout + repeated.stderr)
                    self.assertEqual(file_hashes(root), after)

    def test_malformed_records_report_errors_instead_of_tracebacks(self):
        original = json.loads(self.requests_path.read_text())
        for invalid in ('status', 'target_plan', 'gate_ids', 'relation'):
            with self.subTest(field=invalid):
                request = self.request('implemented', target='001', gates=['sample'])
                request[invalid] = {'invalid': 'object'}
                write_json(self.requests_path, {'schema_version': 1, 'next_id': 2, 'requests': [request]})
                checked = self.check()
                self.assertEqual(checked.returncode, 1, checked.stderr)
                self.assertNotIn('Traceback', checked.stderr)
                status = run_cli('plan', 'status', '--target', str(self.root), '--json')
                self.assertEqual(status.returncode, 1, status.stderr)
                self.assertTrue(json.loads(status.stdout)['errors'])
        write_json(self.requests_path, original)
