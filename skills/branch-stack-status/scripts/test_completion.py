"""Accepted fulfillment uses Complete while preserving review qualification."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

import serve_branch_report as report
import validate_operational_records as records
import test_serve_branch_report as fixtures


class CompletionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.slice = fixtures.slice_record('one', 'fulfilled')
        self.slice['current'] = None
        self.completion = {'status':'accepted', 'kind':'code', 'accepted_by':'Operator',
            'accepted_at':'2026-10-20T09:00:00Z', 'evidence':'plans/audits/acceptance/receipt.json',
            'source':'feature/one', 'tip_sha':fixtures.A,
            'parent':{'branch':'master', 'sha':fixtures.C}, 'release_id':'release'}
        self.slice['completion'] = self.completion
        self.release = {'schema_version':2, 'kind':'release', 'release_id':'release',
            'lifecycle':'released', 'state':'merged', 'base':{'branch':'master', 'sha':fixtures.C},
            'integration_branch':'release/release', 'candidate':{'sha':fixtures.A, 'tree_sha':None},
            'changes':[{'slice_slug':'one', 'build_id':None, 'source':'feature/one',
                        'head_sha':fixtures.A, 'original_parent':copy.deepcopy(self.completion['parent']),
                        'state':'merged', 'pr':fixtures.pr(), 'extensions':{}}],
            'final_pr':fixtures.pr(), 'acceptance':{'status':'accepted', 'evidence':self.completion['evidence']},
            'staging_receipt':None, 'unresolved':[], 'extensions':{}}
        self.write_release()
        self.write_acceptance()
        self.write_slice()

    def write(self, path, value):
        dest = self.root / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(value))
        return dest

    def write_slice(self):
        self.write('plans/slices/fulfilled/one/record.json', self.slice)

    def write_release(self):
        self.write('plans/releases/released/release/preparation.json', self.release)

    def write_acceptance(self):
        self.write(self.completion['evidence'], {'status':'accepted',
            'accepted_by':self.completion['accepted_by'], 'accepted_at':self.completion['accepted_at'],
            'accepted_slices':[{'slice_slug':'one', **{k:self.completion[k] for k in
                ('kind', 'source', 'tip_sha', 'parent', 'release_id')}}]})

    def errors(self):
        return records.validate_record(self.slice, root=self.root)

    def row(self):
        return report.Report(self.root).snapshot()['groups'][0]['rows'][0]

    def select_build(self, counts=False):
        self.slice['current'] = fixtures.slice_record('one')['current']
        branch = fixtures.branch('one')
        for field, count in [('trim_review', 4), ('review_progress', 3)]:
            phase = branch[field]
            phase.update(status='unknown', reason='Review qualification unavailable.',
                         accounting='receipts' if counts else 'unknown',
                         completed_passes=count if counts else None,
                         historical_completed_passes=0 if counts else None,
                         passes=[fixtures.receipt(pass_id=f'{field}-{i}') for i in range(count)] if counts else [])
        self.build = fixtures.build([branch])
        self.write_build()
        self.write_slice()
        return branch

    def write_build(self):
        return self.write('plans/builds/build/manifest.json', self.build)

    def test_code_without_build_is_complete_with_exact_delivery_links(self):
        self.assertFalse(self.errors())
        row = self.row()
        self.assertEqual(row['status'], 'Complete')
        self.assertEqual((row['trim_loops'], row['code_loops']), ('Not recorded', 'Not recorded'))
        self.assertEqual((row['source'], row['tip_sha'], row['target']), ('feature/one', fixtures.A, 'master'))
        self.assertFalse(row['builds'])
        self.assertEqual(row['review_sha'], '')
        self.write('plans/deployments/prod/manifest.json', {'schema_version':2, 'kind':'deployment',
            'deployment_id':'prod', 'environment':'production', 'release_id':'release',
            'candidate':{'sha':fixtures.A, 'tree_sha':None}, 'outcome':'verified',
            'included_slices':[{'slice_slug':'one', 'source':'feature/one', 'tip_sha':fixtures.A}],
            'evidence':self.completion['evidence'], 'unresolved':[], 'extensions':{}})
        self.assertEqual(self.row()['deployments'][0]['name'], 'prod')

    def test_existing_build_and_known_review_counts_remain_intact(self):
        self.select_build(counts=True)
        self.assertFalse(self.errors())
        path = self.root / 'plans/builds/build/manifest.json'
        original = path.read_bytes()
        row = self.row()
        self.assertEqual((row['status'], row['trim_loops'], row['code_loops']), ('Complete', 4, 3))
        self.assertEqual(row['builds'][0]['name'], 'build')
        self.assertEqual(row['build_history'][0]['review_progress']['status'], 'unknown')
        self.assertEqual(path.read_bytes(), original)
        self.assertIsNotNone(row['plan_record']['current'])

    def test_unknown_selected_build_counts_are_not_invented(self):
        self.select_build()
        self.assertFalse(self.errors())
        row = self.row()
        self.assertEqual((row['trim_loops'], row['code_loops']), ('Not recorded', 'Not recorded'))
        self.assertEqual(row['status'], 'Complete')

    def test_known_zero_counts_and_exhausted_review_history_are_preserved(self):
        self.select_build()
        self.build['branches'][0] = fixtures.branch('one')
        self.write_build()
        row = self.row()
        self.assertEqual((row['status'], row['trim_loops'], row['code_loops']), ('Complete', 0, 0))
        phase = self.build['branches'][0]['review_progress']
        phase.update(status='review_cap_reached', sha=fixtures.A, evidence=self.completion['evidence'],
            completed_passes=5, passes=[fixtures.receipt(pass_id=str(i)) for i in range(5)])
        self.write_build()
        self.assertFalse(self.errors())
        row = self.row()
        self.assertEqual((row['status'], row['code_loops']), ('Complete', 5))
        self.assertEqual(row['build_history'][0]['review_progress']['status'], 'review_cap_reached')
        self.assertIn('Recorded review status: Exhausted.', '\n'.join(row['notes']))

    def test_each_non_code_kind_uses_complete_and_na(self):
        for kind in ('no_change_audit', 'operation', 'workflow'):
            with self.subTest(kind=kind):
                self.completion.update(kind=kind, source=None, tip_sha=None, parent=None, release_id=None)
                self.write_acceptance()
                self.write_slice()
                self.assertFalse(self.errors())
                row = self.row()
                self.assertEqual((row['status'], row['trim_loops'], row['code_loops']), ('Complete', 'N/A', 'N/A'))
                self.assertEqual((row['source'], row['tip_sha']), ('', ''))
                self.assertFalse(row['builds'])

    def test_fulfilled_stage_alone_does_not_establish_completion(self):
        self.slice.pop('completion')
        self.write_slice()
        self.assertEqual(self.row()['status'], 'Unclear')

    def test_acceptance_cannot_follow_reopened_stage_or_different_source(self):
        for stage in ('hold', 'review', 'superseded'):
            self.slice['stage'] = stage
            self.assertTrue(self.errors())
        self.slice['stage'] = 'fulfilled'
        self.select_build()
        self.slice['current']['tip_sha'] = fixtures.B
        self.assertTrue(self.errors())

    def test_unaccepted_unmerged_or_wrong_release_member_is_rejected(self):
        for mutate in [lambda d:d['acceptance'].update(status='pending'),
                       lambda d:d.update(state='ready'),
                       lambda d:d['changes'][0].update(state='open'),
                       lambda d:d['changes'][0].update(head_sha=fixtures.B),
                       lambda d:d['changes'][0]['original_parent'].update(sha=fixtures.B),
                       lambda d:d['acceptance'].update(evidence=None)]:
            original = copy.deepcopy(self.release)
            mutate(self.release)
            self.write_release()
            self.assertTrue(self.errors())
            self.release = original

    def test_acceptance_binds_actor_time_and_exact_scope(self):
        for field, value in [('accepted_by','Other'), ('accepted_at','2026-10-21T09:00:00Z'),
                             ('tip_sha',fixtures.B)]:
            original = self.completion[field]
            self.completion[field] = value
            self.assertTrue(self.errors())
            self.completion[field] = original

    def test_missing_empty_unsafe_or_duplicate_acceptance_is_rejected(self):
        path = self.root / self.completion['evidence']
        for action in (lambda:path.unlink(), lambda:path.write_text(''), lambda:path.write_text('{invalid')):
            self.write_acceptance()
            action()
            self.assertTrue(self.errors())
        self.write_acceptance()
        evidence = json.loads(path.read_text())
        evidence['accepted_slices'] *= 2
        path.write_text(json.dumps(evidence))
        self.assertTrue(self.errors())
        self.completion['evidence'] = 'plans/../../outside.json'
        self.assertTrue(self.errors())

    def test_missing_duplicate_or_unsafe_release_is_rejected(self):
        path = self.root / 'plans/releases/released/release/preparation.json'
        path.unlink()
        self.assertTrue(self.errors())
        self.write_release()
        outside = self.root.parent / (self.root.name + '-outside.json')
        self.addCleanup(lambda:outside.unlink(missing_ok=True))
        outside.write_text(path.read_text())
        path.unlink()
        path.symlink_to(outside)
        self.assertTrue(self.errors())
        path.unlink()
        self.write_release()
        self.write('plans/releases/active/release/preparation.json', self.release)
        self.assertTrue(self.errors())

    def test_selected_build_pin_parent_and_validity_are_required(self):
        for field, value in [('tip_sha',fixtures.B), ('parent',{'branch':'master', 'sha':fixtures.B}),
                             ('tree_sha','short')]:
            branch = self.select_build()
            branch[field] = value
            self.write_build()
            self.assertTrue(self.errors())
            self.assertEqual(self.row()['status'], 'Unclear')
        self.select_build()
        (self.root / 'plans/builds/build/manifest.json').unlink()
        self.assertTrue(self.errors())

    def test_non_code_cannot_invent_code_provenance(self):
        self.completion['kind'] = 'operation'
        self.assertTrue(self.errors())

    def test_invalid_waiver_evidence_remains_visible_after_acceptance(self):
        branch = self.select_build()
        branch['review_progress'].update(status='waived', sha=fixtures.A,
            evidence='plans/evidence/missing.json', reason='User waiver')
        self.write_build()
        self.assertFalse(self.errors())
        row = self.row()
        self.assertEqual(row['status'], 'Unclear')
        self.assertTrue(any('missing' in note.lower() for note in row['notes']))

    def test_completion_does_not_qualify_build_freeze(self):
        self.select_build()
        self.build['state'] = 'released'
        self.assertTrue(any('freeze' in e for e in records.validate_record(self.build)))

    def test_no_deferral_or_historical_build_contract_is_added(self):
        data = copy.deepcopy(self.slice)
        data['deferral'] = {}
        self.assertTrue(records.validate_record(data))
        build = fixtures.build([fixtures.branch('one')])
        build['state'] = 'historical'
        self.assertTrue(records.validate_record(build))


if __name__ == '__main__':
    unittest.main()
