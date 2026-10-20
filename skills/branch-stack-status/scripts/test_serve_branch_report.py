#!/usr/bin/env python3
"""Exercise strict JSON inputs, report relationships, migration and HTTP safety."""
import copy
import http.client
import json
from pathlib import Path
import subprocess
import tempfile
import threading
import unittest
from unittest.mock import patch
import serve_branch_report as report
import validate_operational_records as records
from migrate_operational_records import Migration

A,B,C='a'*40,'b'*40,'c'*40


def phase(kind,status='not_started'):
    result={'status':status,'sha':None,'evidence':None,'accounting':'receipts','completed_passes':0,
            'historical_completed_passes':0,'passes':[],'baseline':None,'reason':None}
    result['pass_limit' if kind=='code' else 'applicability']=5 if kind=='code' else 'normal'
    return result


def pr():return {'id':None,'url':None,'state':'none','target_branch':None,'landed_sha':None}


def branch(slug,parent='master',sha=A):
    return {'slice_slug':slug,'spec_slug':None,'plan':f'plans/slices/review/{slug}/{slug}.md',
            'source':'feature/'+slug,'target':parent,'parent':{'branch':parent,'sha':C},'tip_sha':sha,'tree_sha':None,
            'implementation':{'status':'running','sha':None,'required_check_ids':[],'reason':None},
            'trim_review':phase('trim'),'review_progress':phase('code'),'checks':[],'reviews':[],
            'change_request':pr(),'extensions':{}}


def build(branches):return {'schema_version':2,'kind':'build','build_id':'build','state':'building',
                           'base':{'branch':'master','sha':C},'branches':branches,'schedule':None,'freeze':None,'unresolved':[],'extensions':{}}


def slice_record(slug,stage='review',sha=A,bid='build'):
    return {'schema_version':2,'kind':'slice','slice_slug':slug,'spec_slug':None,'stage':stage,'approval':'approved',
            'plan':f'plans/slices/{stage}/{slug}/{slug}.md','current':{'build_id':bid,'source':'feature/'+slug,'tip_sha':sha},'notes':[],'unresolved':[],'extensions':{}}


def receipt(pass_id='one',period='current',state='completed'):
    return {'pass_id':pass_id,'period':period,'status':state,'completed_at':'2026-10-04T09:00:00Z','reviewed_sha':A,
            'triage_evidence':'plans/evidence/triage.md','reviewers':[{'reviewer':r,'validated':True,'sha':A,'evidence':'plans/evidence/'+r+'.md'} for r in sorted(records.REVIEWERS)],
            'reason':'Disqualified output' if state=='disqualified' else None}


def prepared_work(slug='one'):
    b=branch(slug)
    work={k:copy.deepcopy(b[k]) for k in ('slice_slug','spec_slug','plan','source','parent','implementation','trim_review','review_progress','checks','extensions')}
    work.update(status='prepared',prepared_sha=A,waiting_on=[])
    work['implementation'].update(status='verified',sha=A,required_check_ids=['check'])
    work['checks']=[{'id':'check','kind':'agent','status':'passed','sha':A,'evidence':'plans/evidence/check.md','extensions':{}}]
    for key,status in [('trim_review','proportionate'),('review_progress','provisionally_complete')]:
        work[key].update(status=status,sha=A,evidence='plans/evidence/result.json',completed_passes=1,passes=[receipt()])
    work['reviews']=[{'reviewer':r,'status':'clean','sha':A,'evidence':'plans/evidence/clean-'+r+'.json',
                      'method':'direct','origin_sha':A} for r in sorted(records.REVIEWERS)]
    return work


class ContractTests(unittest.TestCase):
    def test_missing_unknown_fields_types_and_versions_rejected(self):
        for mutation in [lambda d:d.pop('base'),lambda d:d.update(extra='alias'),lambda d:d.update(schema_version=True),
                         lambda d:d['branches'][0].update(tip_sha='short'),lambda d:d['branches'][0]['review_progress'].update(completed_passes=True)]:
            data=build([branch('one')]);mutation(data);self.assertTrue(records.validate_record(data))
        self.assertFalse(records.validate_record(build([branch('one')])))

    def test_operator_handoff_strict_fields_pin_and_ready_completeness(self):
        data=build([branch('one')]); b=data['branches'][0]
        self.assertTrue(records.require_operator_handoffs(data))
        b['operator_handoff']={'state':'ready','sha':A,'problem':'Problem','solution':'Solution',
            'test_path':'Try it','pass_condition':'Expected outcome','types':['Fix'],
            'change_surfaces':['Theme'],'packages':[],'evidence':['plans/evidence/operator.json'],'reason':None}
        self.assertFalse(records.validate_record(data));self.assertFalse(records.require_operator_handoffs(data))
        for key,value in [('sha',B),('problem',None),('types',['Invented']),('packages',['a','a']),('legacy_alias','value')]:
            changed=copy.deepcopy(data);changed['branches'][0]['operator_handoff'][key]=value
            self.assertTrue(records.validate_record(changed),key)
        b['operator_handoff'].update(state='unknown',reason=None)
        self.assertTrue(records.validate_record(data))
        b['operator_handoff'].update(state='draft',sha=None)
        self.assertFalse(records.validate_record(data))
        b['implementation'].update(status='verified',sha=A)
        self.assertTrue(records.require_operator_handoffs(data))

    def test_released_build_requires_freeze_qualification(self):
        data=build([branch('one')]);data['state']='released'
        errors=records.validate_record(data)
        self.assertTrue(any('freeze is required' in e for e in errors))
        self.assertTrue(any('qualified correctness' in e for e in errors))

    def test_scheduled_verification_requires_current_declared_checks(self):
        b=branch('one')
        work={k:copy.deepcopy(b[k]) for k in ('slice_slug','spec_slug','plan','source','parent','implementation','trim_review','review_progress','checks','extensions')}
        work.update(status='prepared',prepared_sha=A,waiting_on=[])
        work['implementation'].update(status='verified',sha=A,required_check_ids=['check'])
        data=build([]);data['schedule']={'work':[work],'extensions':{}}
        self.assertTrue(records.validate_record(data))
        work['checks']=[{'id':'check','kind':'agent','status':'passed','sha':A,'evidence':'plans/evidence/check.md','extensions':{}}]
        self.assertFalse(records.validate_record(data))
        work['checks'][0]['sha']=B;self.assertTrue(records.validate_record(data))
        work['checks'][0]['sha']=A
        work['review_progress'].update(status='clean',sha=A,evidence='plans/evidence/review.md',accounting='unknown',completed_passes=None,historical_completed_passes=None,reason='Historical accounting unavailable')
        self.assertTrue(any('matching qualified accepted branch' in e for e in records.validate_record(data)))

    def test_counts_require_receipts_and_distinct_reviewers(self):
        data=build([branch('one')]);p=data['branches'][0]['review_progress'];p.update(status='running',completed_passes=1,passes=[receipt()])
        self.assertFalse(records.validate_record(data))
        p['passes'][0]['reviewers'][1]=copy.deepcopy(p['passes'][0]['reviewers'][0]);self.assertTrue(records.validate_record(data))
        p['passes']=[receipt(),receipt()];p['completed_passes']=2;self.assertTrue(records.validate_record(data))

    def test_provisional_completion_requires_prepared_tip_qualification(self):
        work=prepared_work();data=build([]);data['schedule']={'work':[work],'extensions':{}}
        self.assertFalse(records.validate_record(data))
        for mutate in [lambda w:w.update(prepared_sha=None),lambda w:w.update(parent=None),lambda w:w.update(status='implementing'),
                       lambda w:w['implementation'].update(status='running'),lambda w:w['checks'][0].update(sha=B),
                       lambda w:w['trim_review'].update(status='running',sha=None),lambda w:w['trim_review'].update(sha=B),
                       lambda w:w['review_progress'].update(sha=None),lambda w:w['review_progress'].update(sha=B),
                       lambda w:w['review_progress'].update(evidence=None),
                       lambda w:w['review_progress'].update(completed_passes=0,passes=[]),lambda w:w.pop('reviews'),
                       lambda w:w['reviews'].pop(),lambda w:w['reviews'][0].update(reviewer=w['reviews'][1]['reviewer']),
                       lambda w:w['reviews'][0].update(status='changes_required'),lambda w:w['reviews'][0].update(sha=B),
                       lambda w:w['reviews'][0].update(evidence=None),lambda w:w['reviews'][0].update(method=None),
                       lambda w:w['reviews'][0].update(origin_sha=None),lambda w:w['reviews'][0].update(origin_sha=B)]:
            changed=copy.deepcopy(data);mutate(changed['schedule']['work'][0])
            self.assertTrue(records.validate_record(changed),changed['schedule']['work'][0])
        work['status']='blocked';self.assertFalse(records.validate_record(data))
        for review in work['reviews']:review.update(method='equal_range_diff',origin_sha=B)
        self.assertFalse(records.validate_record(data))

    def test_provisional_completion_is_not_accepted_or_frozen_qualification(self):
        work=prepared_work();b=branch('one')
        for key in ('implementation','checks','trim_review','review_progress','reviews'):b[key]=copy.deepcopy(work[key])
        data=build([b]);self.assertTrue(any('belongs in schedule.work' in e for e in records.validate_record(data)))
        data.update(state='frozen',freeze={'frozen_at':'2026-10-04T09:00:00Z','authorized_by':'user','scope_digest':records.scope_digest(data)})
        self.assertTrue(any('before freezing' in e for e in records.validate_record(data)))

    def test_provisional_review_evidence_is_checked_by_producers(self):
        work=prepared_work();data=build([]);data['schedule']={'work':[work],'extensions':{}}
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            evidence=['plans/evidence/check.md','plans/evidence/result.json','plans/evidence/triage.md']
            evidence.extend('plans/evidence/'+r+'.md' for r in records.REVIEWERS)
            evidence.extend(r['evidence'] for r in work['reviews'])
            for value in evidence:
                path=root/value
                path.parent.mkdir(parents=True,exist_ok=True);path.write_text('Evidence')
            self.assertFalse(records.validate_evidence(data,root))
            path=root/work['reviews'][0]['evidence'];path.unlink()
            self.assertEqual(records.validate_evidence(data,root),['Missing or empty evidence: '+work['reviews'][0]['evidence']])

    def test_historical_and_disqualified_receipts_are_counted_once(self):
        data=build([branch('one')]);p=data['branches'][0]['review_progress']
        p.update(status='running',completed_passes=1,historical_completed_passes=1,passes=[receipt(),receipt('old','historical'),receipt('bad',state='disqualified')])
        self.assertFalse(records.validate_record(data));self.assertEqual(report.review_summary(data['branches'][0],A)['code_loops'],2)
        p['completed_passes']=2;self.assertTrue(records.validate_record(data))

    def test_unknown_is_not_zero_or_a_clean_result(self):
        data=build([branch('one')]);p=data['branches'][0]['review_progress']
        p.update(status='unknown',accounting='unknown',completed_passes=None,historical_completed_passes=None,reason='No historical receipts')
        self.assertFalse(records.validate_record(data));summary=report.review_summary(data['branches'][0],A)
        self.assertEqual((summary['status'],summary['code_loops']),('Review status unknown','Unclear'))
        p['completed_passes']=0;self.assertTrue(records.validate_record(data))

    def test_all_declared_checks_must_pass_before_implementation_verified(self):
        data=build([branch('one')]);b=data['branches'][0]
        b['implementation'].update(status='verified',sha=A,required_check_ids=['first','second'])
        b['checks']=[{'id':i,'kind':'agent','status':s,'sha':A,'evidence':None,'extensions':{}} for i,s in [('first','passed'),('second','failed')]]
        self.assertTrue(records.validate_record(data));b['checks'][1]['status']='passed';self.assertFalse(records.validate_record(data))
        self.assertEqual(report.review_summary(b,A)['status'],'Implementation Finished')

    def test_imported_baseline_and_new_receipts_are_disjoint(self):
        data=build([branch('one')]);p=data['branches'][0]['review_progress']
        p.update(status='running',completed_passes=3,historical_completed_passes=1,passes=[receipt()],
                 baseline={'completed_passes':2,'historical_completed_passes':1,'evidence':'plans/audits/import/original.json'})
        self.assertFalse(records.validate_record(data))
        self.assertEqual(report.review_summary(data['branches'][0],A)['code_loops'],4)
        p['completed_passes']=4;self.assertTrue(records.validate_record(data))

    def test_freeze_digest_does_not_bypass_qualification(self):
        data=build([branch('one')]);data['state']='frozen'
        data['freeze']={'frozen_at':'2026-10-04T09:00:00Z','authorized_by':'user','scope_digest':records.scope_digest(data)}
        self.assertTrue(any('before freezing' in e for e in records.validate_record(data)))
        data['branches'][0]['tip_sha']=B
        self.assertTrue(any('scope_digest' in e for e in records.validate_record(data)))

    def test_current_pin_drift_is_explicit_not_a_git_query(self):
        b=branch('one');self.assertEqual(report.review_summary(b,B)['status'],'Unclear')

    def test_clean_requires_three_current_results_and_trim(self):
        data=build([branch('one')]);b=data['branches'][0]
        for key in ('trim_review','review_progress'):
            p=b[key];p.update(status='proportionate' if key=='trim_review' else 'clean',sha=A,evidence='plans/evidence/result.json',completed_passes=1,passes=[receipt()])
        self.assertTrue(records.validate_record(data))
        b['reviews']=[{'reviewer':r,'status':'clean','sha':A,'evidence':None,'method':'direct','origin_sha':A} for r in records.REVIEWERS]
        self.assertFalse(records.validate_record(data));self.assertEqual(report.review_summary(b,A)['status'],'Complete')
        b['reviews'][0]['sha']=B;self.assertTrue(records.validate_record(data))

    def test_waivers_are_not_clean_completion(self):
        b=branch('one')
        b['review_progress'].update(status='waived',sha=A,evidence='plans/evidence/waiver.json',reason='User waiver')
        self.assertFalse(records.validate_record(build([b])))
        self.assertEqual(report.review_summary(b,A)['status'],'Review waived')
        self.assertEqual(report.review_summary(b,B)['status'],'Unclear')

    def test_trim_waivers_and_unknowns_do_not_override_later_code_progress(self):
        for trim_status in ('waived','unknown'):
            b=branch('one')
            b['trim_review'].update(status=trim_status,reason='Trim decision',
                sha=A if trim_status=='waived' else None,
                evidence='plans/evidence/waiver.json' if trim_status=='waived' else None)
            self.assertFalse(records.validate_record(build([b])))
            expected='Review waived' if trim_status=='waived' else 'Review status unknown'
            self.assertEqual(report.review_summary(b,A)['status'],expected)
            b['review_progress']['status']='running'
            self.assertEqual(report.review_summary(b,A)['status'],'Code Review Started')
            b['review_progress'].update(status='unknown',reason='Code evidence unavailable')
            self.assertEqual(report.review_summary(b,A)['status'],'Review status unknown')

    def test_duplicate_keys_and_nonfinite_json_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'record.json'
            for text in ['{"kind":"slice","kind":"spec"}','{"x":NaN}']:
                path.write_text(text)
                with self.assertRaises(ValueError):records.load_record(path)


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        self.b=branch('one');self.write('plans/builds/build/manifest.json',build([self.b]))
        self.write('plans/slices/review/one/record.json',slice_record('one'))
    def write(self,path,data):
        file=self.root/path;file.parent.mkdir(parents=True,exist_ok=True);file.write_text(json.dumps(data));return file
    def rows(self):return [r for g in report.Report(self.root).snapshot()['groups'] for r in g['rows']]

    def test_all_plan_stages_preserve_review_status_except_superseded(self):
        (self.root/'plans/slices/review/one/record.json').unlink()
        stages=records.SCHEMA['$defs']['slice']['properties']['stage']['enum']
        for stage in stages:
            for selected in (False,True):
                with self.subTest(stage=stage,selected=selected):
                    data=slice_record('one',stage=stage)
                    if not selected:data['current']=None
                    path=self.write(f'plans/slices/{stage}/one/record.json',data)
                    self.assertFalse(records.validate_record(data,'slice',path,self.root))
                    original=path.read_bytes()
                    row=self.rows()[0]
                    if stage=='superseded':
                        expected='Superseded'
                    elif selected:
                        expected='Implementation Started'
                    elif stage in {'draft','backlog','to_do'}:
                        expected='Not Started'
                    else:
                        expected='Unclear'
                    self.assertEqual((row['stage'],row['status']),(stage,expected))
                    self.assertEqual(path.read_bytes(),original)
                    path.unlink()

    def test_superseded_without_build_needs_no_current_qualification(self):
        (self.root/'plans/slices/review/one/record.json').unlink()
        (self.root/'plans/builds/build/manifest.json').unlink()
        data=slice_record('one',stage='superseded');data['current']=None
        self.write('plans/slices/superseded/one/record.json',data)
        snapshot=report.Report(self.root).snapshot();row=snapshot['groups'][0]['rows'][0]
        self.assertEqual(row['status'],'Superseded')
        self.assertEqual((row['trim_loops'],row['code_loops']),('Unclear','Unclear'))
        self.assertFalse(row['notes']);self.assertFalse(snapshot['issues'])

    def test_superseded_preserves_recorded_review_counts_and_history(self):
        (self.root/'plans/slices/review/one/record.json').unlink()
        self.write('plans/slices/superseded/one/record.json',slice_record('one',stage='superseded'))
        for field in ('trim_review','review_progress'):
            self.b[field].update(status='running',completed_passes=1,passes=[receipt()])
        manifest=self.write('plans/builds/build/manifest.json',build([self.b]))
        original=manifest.read_bytes()
        row=self.rows()[0]
        self.assertEqual((row['status'],row['trim_loops'],row['code_loops']),('Superseded',1,1))
        self.assertEqual(row['build_history'][0]['review_progress'],self.b['review_progress'])
        self.assertEqual(manifest.read_bytes(),original)

    def test_superseded_preserves_reference_errors_and_rejects_invalid_slice(self):
        (self.root/'plans/slices/review/one/record.json').unlink()
        data=slice_record('one',stage='superseded',bid='missing')
        path=self.write('plans/slices/superseded/one/record.json',data)
        snapshot=report.Report(self.root).snapshot();row=snapshot['groups'][0]['rows'][0]
        self.assertEqual(row['status'],'Superseded')
        self.assertTrue(any('current build/source does not resolve' in e for e in snapshot['issues']))
        data['approval']='invalid';self.write(str(path.relative_to(self.root)),data)
        snapshot=report.Report(self.root).snapshot();row=snapshot['groups'][0]['rows'][0]
        self.assertEqual((row['stage'],row['status']),('Unclear','Unclear'))
        self.assertTrue(any('approval' in e for e in snapshot['issues']))

    def test_current_waivers_check_files_without_reading_or_rewriting_evidence(self):
        evidence=self.root/'plans/evidence/waiver.md'
        evidence.parent.mkdir(parents=True)
        evidence.write_text('Explicit user waiver')
        for field,name in [('review_progress','Code review'),('trim_review','Trim review')]:
            with self.subTest(field=field):
                b=branch('one')
                b[field].update(status='waived',sha=A,evidence='plans/evidence/waiver.md',reason='User waiver',
                    accounting='unknown',completed_passes=None,historical_completed_passes=None)
                manifest=self.write('plans/builds/build/manifest.json',build([b]))
                original=manifest.read_bytes()
                read_text=Path.read_text

                def guarded(path,*args,**kwargs):
                    self.assertEqual(path.suffix,'.json')
                    return read_text(path,*args,**kwargs)

                with patch.object(Path,'read_text',guarded):
                    row=self.rows()[0]
                count_field='code_loops' if field=='review_progress' else 'trim_loops'
                self.assertEqual(row['status'],'Review waived')
                self.assertEqual(row[count_field],'Unclear')
                self.assertIn(name+': User waiver',row['notes'])
                self.assertEqual(manifest.read_bytes(),original)
                self.assertEqual(evidence.read_text(),'Explicit user waiver')

    def test_waiver_evidence_file_failures_are_specific_and_never_waived(self):
        for field,name in [('review_progress','Code review'),('trim_review','Trim review')]:
            for case in ('missing','empty','directory','unsafe','symlink_loop'):
                with self.subTest(field=field,case=case):
                    value=f'plans/evidence/{field}-{case}.json'
                    path=self.root/value
                    path.parent.mkdir(parents=True,exist_ok=True)
                    if case=='empty':
                        path.touch()
                    elif case=='directory':
                        path.mkdir()
                    elif case=='unsafe':
                        outside=self.root/'outside.json'
                        outside.write_text('{}')
                        path.symlink_to(outside)
                    elif case=='symlink_loop':
                        path.symlink_to(path)
                    b=branch('one')
                    b[field].update(status='waived',sha=A,evidence=value,reason='User waiver')
                    self.write('plans/builds/build/manifest.json',build([b]))
                    snapshot=report.Report(self.root).snapshot()
                    row=snapshot['groups'][0]['rows'][0]
                    self.assertEqual(row['status'],'Unclear')
                    self.assertTrue(any(name in note and value in note for note in row['notes']))
                    self.assertTrue(any(value in issue for issue in snapshot['issues']))

    def test_invalid_waiver_qualification_explains_the_contract_error(self):
        cases=[('sha',B,'current tip sha'),('evidence',None,'evidence'),('reason',None,'reason')]
        for field,value,problem in cases:
            with self.subTest(field=field):
                b=branch('one')
                b['review_progress'].update(status='waived',sha=A,evidence='plans/evidence/waiver.json',reason='User waiver')
                b['review_progress'][field]=value
                self.write('plans/builds/build/manifest.json',build([b]))
                row=self.rows()[0]
                self.assertEqual(row['status'],'Unclear')
                self.assertTrue(any(problem in note for note in row['notes']))

    def test_scheduled_waiver_and_unknown_status_use_the_same_rules(self):
        work=prepared_work()
        work['review_progress'].update(status='waived',reason='User waiver')
        data=build([])
        data['schedule']={'work':[work],'extensions':{}}
        self.write('plans/builds/build/manifest.json',data)
        self.assertEqual(self.rows()[0]['status'],'Unclear')
        self.write('plans/evidence/result.json',{'waiver':'User waiver'})
        self.assertEqual(self.rows()[0]['status'],'Review waived')
        self.write('plans/slices/review/one/record.json',slice_record('one',sha=B))
        self.assertEqual(self.rows()[0]['status'],'Unclear')
        self.write('plans/slices/review/one/record.json',slice_record('one'))
        work['review_progress'].update(status='unknown',sha=None,reason='Current review unavailable')
        self.write('plans/builds/build/manifest.json',data)
        row=self.rows()[0]
        self.assertEqual((row['status'],row['code_loops']),('Review status unknown',1))
        self.assertIn('Code review: Current review unavailable',row['notes'])

    def test_snapshot_reads_only_json_and_never_queries_git(self):
        plan=self.root/'plans/slices/review/one/one.md';plan.write_text('Branch: feature/wrong\nCompleted discovery passes: 99')
        original=Path.read_text
        def guarded(path,*args,**kwargs):
            self.assertEqual(path.suffix,'.json');return original(path,*args,**kwargs)
        with patch.object(Path,'read_text',guarded),patch.object(subprocess,'run',side_effect=AssertionError('Git queried')):
            rows=self.rows()
        self.assertEqual((rows[0]['source'],rows[0]['code_loops']),('feature/one',0))
        plan.write_text('Different Markdown with invented clean reviews');self.assertEqual(self.rows(),rows)

    def test_provisional_reviews_display_separately_until_stack_qualification(self):
        work=prepared_work();data=build([]);data['schedule']={'work':[work],'extensions':{}}
        self.write('plans/builds/build/manifest.json',data)
        row=self.rows()[0]
        self.assertEqual((row['status'],row['trim_loops'],row['code_loops']),('Provisionally Complete',1,1))
        self.assertTrue(any('final stack acceptance' in note for note in row['notes']))
        work['review_progress'].update(status='running',sha=None)
        self.write('plans/builds/build/manifest.json',data)
        self.assertEqual(self.rows()[0]['status'],'Code Review Started')
        work['review_progress'].update(status='provisionally_complete',sha=A)
        self.write('plans/builds/build/manifest.json',data)
        self.write('plans/slices/review/one/record.json',slice_record('one',sha=B))
        self.assertEqual(self.rows()[0]['status'],'Unclear')
        # Restack qualification changes applicability, not completed loop counts.
        b=branch('one',sha=B)
        for key in ('implementation','checks','trim_review','review_progress','reviews'):b[key]=copy.deepcopy(work[key])
        b['implementation']['sha']=B;b['checks'][0]['sha']=B
        b['trim_review']['sha']=B;b['review_progress'].update(status='clean',sha=B)
        for review in b['reviews']:review.update(sha=B,method='equal_range_diff')
        work.update(status='complete',prepared_sha=B)
        for key in ('implementation','checks','trim_review','review_progress','reviews'):work[key]=copy.deepcopy(b[key])
        data['branches']=[b];self.write('plans/builds/build/manifest.json',data)
        self.assertFalse(records.validate_record(data))
        row=self.rows()[0];self.assertEqual((row['status'],row['trim_loops'],row['code_loops']),('Complete',1,1))

    def test_operator_text_comes_only_from_selected_json_and_marks_pin_conflict(self):
        self.b['operator_handoff']={'state':'ready','sha':A,'problem':'JSON problem','solution':'JSON solution',
            'test_path':'JSON test','pass_condition':'JSON condition','types':['Fix'],'change_surfaces':['Theme'],
            'packages':[],'evidence':['plans/evidence/operator.json'],'reason':None}
        self.write('plans/builds/build/manifest.json',build([self.b]))
        (self.root/'plans/slices/review/one/one.md').write_text('Operator problem: Markdown must not be read')
        row=self.rows()[0];self.assertEqual(row['operator_handoff']['problem'],'JSON problem');self.assertEqual(row['handoff_state'],'ready')
        self.write('plans/slices/review/one/record.json',slice_record('one',sha=B))
        row=self.rows()[0];self.assertEqual(row['handoff_state'],'stale');self.assertEqual(row['operator_handoff']['sha'],A)
        self.b.pop('operator_handoff');self.write('plans/builds/build/manifest.json',build([self.b]))
        self.assertEqual(self.rows()[0]['handoff_state'],'not_recorded')

    def test_held_slice_uses_explicit_json_stage_and_zero_counts(self):
        data=build([branch('one')]);data['branches'][0]['implementation']['status']='not_started'
        self.write('plans/builds/build/manifest.json',data)
        (self.root/'plans/slices/review/one/record.json').unlink()
        held=slice_record('one',stage='hold');self.write('plans/slices/hold/one/record.json',held)
        self.assertFalse(records.validate_record(held))
        row=self.rows()[0]
        self.assertEqual((row['stage'],row['status'],row['trim_loops'],row['code_loops']),('hold','Not Started',0,0))
        self.assertIn('hold',__import__('migrate_operational_records').STAGES)

    def test_bad_schema_is_rejected_without_legacy_aliases(self):
        data=build([self.b]);data['schema_version']=1;data['release_id']='legacy';self.write('plans/builds/build/manifest.json',data)
        snapshot=report.Report(self.root).snapshot();row=snapshot['groups'][0]['rows'][0]
        self.assertEqual(row['status'],'Unclear');self.assertTrue(any('schema_version' in e for e in snapshot['issues']))

    def test_current_build_is_explicit_even_when_another_build_looks_newer(self):
        data=build([branch('one',sha=B)]);data['build_id']='newer';self.write('plans/builds/newer/manifest.json',data)
        row=self.rows()[0];self.assertEqual(row['review_sha'],A);self.assertEqual(len(row['builds']),2)

    def test_graph_orders_ancestors_and_preserves_original_target(self):
        parent=branch('parent');child=branch('one',parent='feature/parent');child['change_request'].update(id='1',url='https://example.com/1',target_branch='integration',state='ready')
        self.write('plans/builds/build/manifest.json',build([child,parent]));self.write('plans/slices/review/parent/record.json',slice_record('parent'))
        rows=self.rows();self.assertEqual([r['id'] for r in rows],['parent','one']);self.assertEqual(rows[1]['target'],'feature/parent')

    def test_deployment_membership_is_exact_json_and_requires_verified_outcome(self):
        d={'schema_version':2,'kind':'deployment','deployment_id':'deploy','environment':'staging','release_id':None,
           'candidate':{'sha':C,'tree_sha':None},'outcome':'verified','included_slices':[{'slice_slug':'one','source':'feature/one','tip_sha':A}],
           'evidence':'plans/deployments/deploy/manifest.json','unresolved':[],'extensions':{}}
        self.write('plans/deployments/deploy/manifest.json',d);self.assertEqual(len(self.rows()[0]['deployments']),1)
        d['included_slices'][0]['tip_sha']=B;self.write('plans/deployments/deploy/manifest.json',d)
        self.assertFalse(self.rows()[0]['deployments']);self.assertEqual(len(self.rows()[0]['deployment_history']),1)
        d['outcome']='failed';d['included_slices'][0]['tip_sha']=A;self.write('plans/deployments/deploy/manifest.json',d);self.assertFalse(self.rows()[0]['deployments'])

    def test_release_alias_files_are_not_read(self):
        self.write('plans/releases/active/old/release.json',{'release_id':'old','branches':[self.b]})
        self.assertFalse(self.rows()[0]['releases'])

    def test_duplicate_metadata_and_stage_mismatch_are_errors(self):
        self.write('plans/slices/merged/one/record.json',slice_record('one','merged'))
        snapshot=report.Report(self.root).snapshot();self.assertEqual(snapshot['groups'][0]['rows'][0]['stage'],'Unclear')
        self.assertTrue(any('Duplicate' in e for e in snapshot['issues']))

    def test_scoped_validation_does_not_block_on_an_unrelated_legacy_build(self):
        self.write('plans/builds/archive/manifest.json',{'schema_version':1})
        data=records.load_record(self.root/'plans/slices/review/one/record.json')
        self.assertFalse(records.validate_related(data,self.root))
        self.assertTrue(records.validate_project(self.root))
        data['current']['tip_sha']=B
        self.assertTrue(any('qualification pin' in e for e in records.validate_related(data,self.root)))

    def test_http_is_read_only_and_blocks_escape(self):
        server=report.make_server(self.root,0);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        self.addCleanup(server.server_close);self.addCleanup(server.shutdown)
        client=http.client.HTTPConnection('127.0.0.1',server.server_port);self.addCleanup(client.close)
        client.request('GET','/api/report');response=client.getresponse();self.assertEqual(response.status,200);response.read()
        client.request('GET','/record?path=../secret.json');response=client.getresponse();self.assertEqual(response.status,404);response.read()
        client.request('GET','/',headers={'Host':'attacker.example'});response=client.getresponse();self.assertEqual(response.status,403);response.read()
        client.request('POST','/api/report');response=client.getresponse();self.assertEqual(response.status,501);response.read()


class MigrationTests(unittest.TestCase):
    def test_import_is_explicit_preserves_originals_and_unknown_counts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);subprocess.run(['git','init','-q',str(root)],check=True)
            path=root/'plans/slices/review/one/one.md';path.parent.mkdir(parents=True);path.write_text('Approval Status: approved\nBranch: feature/one')
            file=root/'plans/builds/old/manifest.json';file.parent.mkdir(parents=True)
            b={'slice_slug':'one','plan':str(path.relative_to(root)),'source':'feature/one','parent':{'branch':'master','sha':C},'target':'master','tip_sha':A,'checks':[],
               'trim_review':{'status':'pending'},'review_progress':{'status':'pending','completed_passes':2,'pass_limit':5}}
            raw=json.dumps({'schema_version':1,'release_id':'old','state':'building','base':{'branch':'master','sha':C},'branches':[b]}).encode();file.write_bytes(raw)
            migration=Migration(root);migration.prepare();self.assertEqual(file.read_bytes(),raw)
            receipt_path=Path(migration.apply());self.assertTrue(receipt_path.exists())
            self.assertEqual((receipt_path.parent/'originals'/file.relative_to(root)).read_bytes(),raw)
            data=records.load_record(file);self.assertFalse(records.validate_record(data))
            self.assertEqual(data['branches'][0]['review_progress']['completed_passes'],2)
            self.assertIsNotNone(data['branches'][0]['review_progress']['baseline'])
            self.assertEqual(data['branches'][0]['extensions']['historical_record']['review_progress']['completed_passes'],2)
            again=Migration(root);self.assertEqual(again.prepare()['records'],0)

    def test_heading_approval_linked_ownership_and_relative_parent_import(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);subprocess.run(['git','init','-q',str(root)],check=True)
            spec=root/'plans/specs/review/parent/parent.md';spec.parent.mkdir(parents=True)
            spec.write_text('# Parent\n\n## Approval Status\n\napproved\n')
            spec.with_name('parent.slices.md').write_text('## Slice Map Status\n\napproved\n\n| Acceptance ID | Owning slice |\n| --- | --- |\n| AC-1 | [`one`](../../../slices/review/one/one.md) |\n')
            plan=root/'plans/slices/review/one/one.md';plan.parent.mkdir(parents=True)
            plan.write_text('## Approval Status\n\napproved\n\nParent: [parent](../../../specs/review/parent/parent.md)\n')
            migration=Migration(root);migration.prepare();migration.apply()
            parent=records.load_record(spec.with_name('record.json'))
            child=records.load_record(plan.with_name('record.json'))
            self.assertEqual(parent['approval'],'approved');self.assertEqual(parent['slice_map']['status'],'approved')
            self.assertEqual(parent['slice_map']['owners'],[{'acceptance_id':'AC-1','slice_slug':'one'}])
            self.assertEqual(child['approval'],'approved');self.assertEqual(child['spec_slug'],'parent')
            # Simulate the older import that lost heading/link metadata. Only an
            # explicit reconciliation repairs those adopted JSON records.
            parent['approval']='unknown';parent['slice_map']={'status':'unknown','owners':[]}
            child['approval']='unknown';child['spec_slug']=None
            spec.with_name('record.json').write_text(json.dumps(parent));plan.with_name('record.json').write_text(json.dumps(child))
            self.assertEqual(Migration(root).prepare()['records'],0)
            repair=Migration(root,reconcile_metadata=True);self.assertEqual(repair.prepare()['records'],2);repair.apply()
            fixed=records.load_record(plan.with_name('record.json'))
            self.assertEqual(fixed['spec_slug'],'parent');self.assertEqual(fixed['current'],child['current'])
            self.assertEqual(Migration(root,reconcile_metadata=True).prepare()['records'],0)

    def test_explicit_json_spec_is_preserved_during_import_and_repair(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);subprocess.run(['git','init','-q',str(root)],check=True)
            plan=root/'plans/slices/review/one/one.md';plan.parent.mkdir(parents=True);plan.write_text('Approval Status: approved')
            file=root/'plans/builds/old/manifest.json';file.parent.mkdir(parents=True)
            b={'slice_slug':'one','spec_slug':'parent','plan':str(plan.relative_to(root)),'source':'feature/one',
               'parent':{'branch':'master','sha':C},'tip_sha':A,'checks':[],
               'trim_review':{'status':'pending'},'review_progress':{'status':'pending','completed_passes':2,'pass_limit':5}}
            file.write_text(json.dumps({'schema_version':1,'state':'building','base':{'branch':'master','sha':C},'branches':[b]}))
            migration=Migration(root);migration.prepare();migration.apply()
            data=records.load_record(file);child=records.load_record(plan.with_name('record.json'))
            self.assertEqual(data['branches'][0]['spec_slug'],'parent');self.assertEqual(child['spec_slug'],'parent')
            data['branches'][0]['spec_slug']=None;child['spec_slug']=None
            file.write_text(json.dumps(data));plan.with_name('record.json').write_text(json.dumps(child))
            repair=Migration(root,reconcile_metadata=True);repair.prepare();repair.apply()
            fixed=records.load_record(file)
            self.assertEqual(fixed['branches'][0]['spec_slug'],'parent')
            self.assertEqual(fixed['branches'][0]['review_progress'],data['branches'][0]['review_progress'])
            self.assertEqual(fixed['branches'][0]['tip_sha'],data['branches'][0]['tip_sha'])
            self.assertEqual(records.load_record(plan.with_name('record.json'))['spec_slug'],'parent')

    def test_concurrent_input_change_aborts_without_replacement(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);file=root/'plans/builds/old/manifest.json';file.parent.mkdir(parents=True);file.write_text('{}')
            migration=Migration(root);migration.read(file);file.write_text('{"changed":true}')
            with self.assertRaises(ValueError):migration.apply()
            self.assertEqual(file.read_text(),'{"changed":true}')

if __name__=='__main__':unittest.main()
