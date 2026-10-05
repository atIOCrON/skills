#!/usr/bin/env python3
"""Validate canonical operational JSON without reading Markdown or running Git."""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime, timezone
import json
import hashlib
from pathlib import Path
import re
import sys

SCHEMA_PATH = Path(__file__).resolve().parent.parent / 'operational-records.schema.json'
if not SCHEMA_PATH.exists():
    SCHEMA_PATH = Path(__file__).resolve().parent.parent / 'references/operational-records.schema.json'
SCHEMA = json.loads(SCHEMA_PATH.read_text())
KINDS = ('spec', 'slice', 'build', 'release', 'deployment')
PATTERNS = {'spec':'plans/specs/*/*/record.json', 'slice':'plans/slices/*/*/record.json',
            'build':'plans/builds/*/manifest.json', 'release':'plans/releases/*/*/preparation.json',
            'deployment':'plans/deployments/*/manifest.json'}
REVIEWERS = {'claude','codex','cursor'}


def no_duplicates(pairs):
    data = {}
    for key, value in pairs:
        if key in data:
            raise ValueError('Duplicate JSON key: ' + key)
        data[key] = value
    return data


def load_record(path):
    def reject(value):
        raise ValueError('Invalid JSON constant: ' + value)
    return json.loads(Path(path).read_text(encoding='utf-8'), object_pairs_hook=no_duplicates, parse_constant=reject)


def schema_errors(data, schema, at='$'):
    if '$ref' in schema:
        return schema_errors(data, SCHEMA['$defs'][schema['$ref'].split('/')[-1]], at)
    if 'anyOf' in schema:
        errors = [schema_errors(data, choice, at) for choice in schema['anyOf']]
        return [] if any(not e for e in errors) else [at + ' does not match its required type']
    expected = schema.get('type')
    types = {'object':dict, 'array':list, 'string':str, 'integer':int, 'null':type(None)}
    if expected and (not isinstance(data, types[expected]) or (expected == 'integer' and isinstance(data, bool))):
        return [at + ' must be ' + expected]
    if 'enum' in schema and not any(type(data) is type(v) and data == v for v in schema['enum']):
        return [at + ' must be one of ' + repr(schema['enum'])]
    errors = []
    if expected == 'object':
        properties = schema.get('properties', {})
        for key in schema.get('required', []):
            if key not in data:
                errors.append(at + '.' + key + ' is required')
        if schema.get('additionalProperties') is False:
            errors.extend(at + '.' + key + ' is not allowed; contextual data belongs in extensions' for key in data if key not in properties)
        for key, value in data.items():
            if key in properties:
                errors.extend(schema_errors(value, properties[key], at + '.' + key))
    elif expected == 'array':
        for index, value in enumerate(data):
            errors.extend(schema_errors(value, schema['items'], f'{at}[{index}]'))
    elif expected == 'string':
        if len(data.strip()) < schema.get('minLength', 0):
            errors.append(at + ' must be non-empty')
        if 'pattern' in schema and not re.search(schema['pattern'], data):
            errors.append(at + ' has an invalid format')
        if schema.get('format') == 'utc-timestamp':
            try:
                stamp = datetime.fromisoformat(data.replace('Z','+00:00'))
                valid = stamp.tzinfo is not None and stamp.utcoffset() == timezone.utc.utcoffset(stamp)
            except (ValueError, TypeError):
                valid = False
            if not valid:
                errors.append(at + ' must be a UTC ISO timestamp')
    elif expected == 'integer' and data < schema.get('minimum', data):
        errors.append(at + ' is below its minimum')
    return errors


def phase_errors(phase, kind, tip, at):
    errors = []
    terminal = {'clean','proportionate','review_cap_reached','waived'}
    if phase['status'] in terminal and (phase['sha'] != tip or not phase['evidence']):
        errors.append(at + ' terminal result requires current tip sha and evidence')
    if phase['status'] in {'not_started','running','unknown'} and phase['sha'] is not None:
        errors.append(at + '.sha must be null without a completed current result')
    if phase['status'] in {'unknown','waived'} and not phase['reason']:
        errors.append(at + '.reason is required for unknown or waived results')
    if phase['accounting'] == 'unknown':
        if phase['completed_passes'] is not None or phase['historical_completed_passes'] is not None or phase['passes'] or phase['baseline'] is not None or not phase['reason']:
            errors.append(at + ' unknown accounting requires null counts, no receipts, and a reason')
        return errors
    baseline=phase['baseline']
    totals = Counter({'current':baseline['completed_passes'],'historical':baseline['historical_completed_passes']}) if baseline else Counter()
    ids = set()
    for index, receipt in enumerate(phase['passes']):
        where = f'{at}.passes[{index}]'
        if receipt['pass_id'] in ids:
            errors.append(where + '.pass_id is duplicated')
        ids.add(receipt['pass_id'])
        if receipt['status'] == 'disqualified':
            if not receipt['reason']:
                errors.append(where + '.reason is required after disqualification')
            continue
        reviewers = receipt['reviewers']
        if len(reviewers) != 3 or {r['reviewer'] for r in reviewers} != REVIEWERS:
            errors.append(where + '.reviewers must contain three distinct validated reviewers')
        if any(r['sha'] != receipt['reviewed_sha'] for r in reviewers):
            errors.append(where + '.reviewers must match reviewed_sha')
        totals[receipt['period']] += 1
    for field, period in [('completed_passes','current'),('historical_completed_passes','historical')]:
        if phase[field] != totals[period]:
            errors.append(at + '.' + field + ' must equal the imported baseline plus completed receipts')
    total = sum(totals.values())
    if kind == 'code':
        if total > phase['pass_limit'] or (phase['status'] == 'review_cap_reached' and total != phase['pass_limit']):
            errors.append(at + ' completed receipts conflict with pass_limit')
    if phase['status'] in {'clean','proportionate','review_cap_reached'} and not total:
        if kind != 'trim' or phase['applicability'] != 'zero_diff':
            errors.append(at + ' requires completed receipts')
    if phase['status'] == 'not_started' and total:
        errors.append(at + ' cannot have completed receipts while not_started')
    return errors


def scope_digest(data):
    """Bind canonical scope/pins and required checks; review progress is not scope."""
    payload = {'base':data['base'], 'branches':[
        {key:branch[key] for key in ('slice_slug','spec_slug','plan','source','parent','target','tip_sha','tree_sha')}
        | {'required_check_ids':branch['implementation']['required_check_ids'],
           'checks':[{'id':c['id'],'kind':c['kind'],'command':c['extensions'].get('command')} for c in branch['checks']]}
        for branch in data['branches']]}
    encoded=json.dumps(payload,sort_keys=True,separators=(',',':')).encode()
    return 'sha256:'+hashlib.sha256(encoded).hexdigest()


def validate_record(data, expected_kind=None, path=None, root=None):
    if not isinstance(data, dict) or data.get('kind') not in KINDS:
        return ['$: kind must identify spec, slice, build, release, or deployment']
    kind = data['kind']
    if expected_kind and kind != expected_kind:
        return [f'$.kind must be {expected_kind} at this path']
    errors = schema_errors(data, SCHEMA['$defs'][kind])
    if errors:
        return errors
    if path is not None and root is not None:
        try:
            rel = Path(path).resolve().relative_to(Path(root).resolve())
            if kind in {'spec','slice'}:
                if rel.parent.name != data[kind+'_slug'] or rel.parent.parent.name != data['stage']:
                    errors.append('$.stage and slug must match the record folder')
            elif rel.parent.name != data[kind+'_id']:
                errors.append('$.' + kind + '_id must match the record folder')
            if kind == 'release' and rel.parent.parent.name != data['lifecycle']:
                errors.append('$.lifecycle must match the release folder')
        except ValueError:
            errors.append('$: record must be inside the project')
    if kind == 'spec':
        ids = [o['acceptance_id'] for o in data['slice_map']['owners']]
        if len(ids) != len(set(ids)):
            errors.append('$.slice_map.owners must give each acceptance ID one owner')
    elif kind == 'build':
        slugs = [b['slice_slug'] for b in data['branches']]
        if len(slugs) != len(set(slugs)):
            errors.append('$.branches contains duplicate slice identities')
        if data['freeze'] and data['freeze']['scope_digest'] != scope_digest(data):
            errors.append('$.freeze.scope_digest does not match canonical build scope')
        if data['state'] in {'frozen','staged','accepted','released'} and data['freeze'] is None:
            errors.append('$.freeze is required for a frozen or later candidate')
        sources = [b['source'] for b in data['branches']]
        if len(sources) != len(set(sources)):
            errors.append('$.branches contains duplicate source identities')
        for index, branch in enumerate(data['branches']):
            at = f'$.branches[{index}]'
            if branch['target'] != branch['parent']['branch']:
                errors.append(at + '.target must equal its stack parent; PR destinations belong in change_request')
            disposition=branch.get('human_disposition')
            accepted=False
            if disposition and disposition['status']!='pending':
                if any(disposition[k] is None for k in ('sha','decided_by','decided_at','reason','evidence')):
                    errors.append(at + '.human_disposition requires complete decision fields')
                effective=disposition['sha']
                for mapping in disposition['mappings']:
                    if mapping['from_sha']!=effective:errors.append(at + '.human_disposition mappings do not form a SHA chain')
                    effective=mapping['to_sha']
                accepted=disposition['status']=='accepted' and effective==branch['tip_sha']
            if data['state'] in {'frozen','staged','accepted','released'}:
                if branch['implementation']['status']!='verified' or branch['trim_review']['status']!='proportionate' or not (branch['review_progress']['status']=='clean' or branch['review_progress']['status']=='review_cap_reached' and accepted):
                    errors.append(at + ' requires verified implementation, proportionate trim and qualified correctness before freezing')
                parents={data['base']['branch']:data['base']['sha'],**{b['source']:b['tip_sha'] for b in data['branches']}}
                if parents.get(branch['parent']['branch'])!=branch['parent']['sha']:
                    errors.append(at + '.parent must pin the recorded base or branch head before freezing')
            check_ids = [c['id'] for c in branch['checks']]
            if len(check_ids) != len(set(check_ids)):
                errors.append(at + '.checks contains duplicate IDs')
            implementation = branch['implementation']
            if implementation['status'] == 'unknown' and not implementation['reason']:
                errors.append(at + '.implementation.reason is required when unknown')
            if implementation['status'] == 'verified':
                checks = {c['id']:c for c in branch['checks']}
                required = implementation['required_check_ids']
                if implementation['sha'] != branch['tip_sha'] or not required or any(i not in checks or checks[i]['kind'] != 'agent' or checks[i]['status'] != 'passed' or checks[i]['sha'] != branch['tip_sha'] for i in required):
                    errors.append(at + '.implementation verified requires every declared agent check passed on tip_sha')
            if branch['review_progress']['status'] == 'clean':
                clean = {r['reviewer'] for r in branch['reviews'] if r['status']=='clean' and r['sha']==branch['tip_sha']}
                if clean != REVIEWERS or branch['trim_review']['status'] != 'proportionate':
                    errors.append(at + ' clean correctness requires three current-tip clean results and proportionate trim')
            for field, phase in [('trim_review','trim'),('review_progress','code')]:
                errors.extend(phase_errors(branch[field],phase,branch['tip_sha'],at+'.'+field))
        if data['schedule']:
            work = data['schedule']['work']
            ids = [w['slice_slug'] for w in work]
            if len(ids) != len(set(ids)):
                errors.append('$.schedule.work contains duplicate slice identities')
            for index,item in enumerate(work):
                at = f'$.schedule.work[{index}]'
                check_ids = [c['id'] for c in item['checks']]
                if len(check_ids) != len(set(check_ids)):
                    errors.append(at + '.checks contains duplicate IDs')
                implementation = item['implementation']
                if implementation['status'] == 'unknown' and not implementation['reason']:
                    errors.append(at + '.implementation.reason is required when unknown')
                if implementation['status'] == 'verified':
                    checks = {c['id']:c for c in item['checks']}
                    required = implementation['required_check_ids']
                    if not item['prepared_sha'] or implementation['sha'] != item['prepared_sha'] or not required or any(i not in checks or checks[i]['kind'] != 'agent' or checks[i]['status'] != 'passed' or checks[i]['sha'] != item['prepared_sha'] for i in required):
                        errors.append(at + '.implementation verified requires every declared agent check passed on prepared_sha')
                if item['review_progress']['status'] == 'clean':
                    accepted_branch = next((b for b in data['branches'] if b['slice_slug']==item['slice_slug'] and b['source']==item['source'] and b['tip_sha']==item['prepared_sha']),None)
                    if not accepted_branch or accepted_branch['review_progress']['status']!='clean':
                        errors.append(at + ' clean scheduled correctness requires the matching qualified accepted branch')
                for field, phase in [('trim_review','trim'),('review_progress','code')]:
                    errors.extend(phase_errors(item[field],phase,item['prepared_sha'],f'$.schedule.work[{index}].'+field))
                if item['status']=='prepared' and not item['prepared_sha']:
                    errors.append('$.schedule.work prepared requires prepared_sha')
                if item['status'] in {'stacked','complete'} and item['slice_slug'] not in slugs:
                    errors.append('$.schedule.work claims acceptance without an accepted branch')
    elif kind == 'release':
        identities = [c['slice_slug'] for c in data['changes']]
        if len(identities) != len(set(identities)):
            errors.append('$.changes contains duplicate slice identities')
        if data['state'] in {'assembled','testing','ready','merged'} and not data['candidate']['sha']:
            errors.append('$.candidate.sha is required after assembly')
    elif kind == 'deployment':
        if data['outcome'] == 'verified' and (not data['candidate']['sha'] or not data['evidence']):
            errors.append('$.outcome verified requires candidate sha and evidence')
        identities = [(m['slice_slug'],m['source'],m['tip_sha']) for m in data['included_slices']]
        if len(identities) != len(set(identities)):
            errors.append('$.included_slices contains duplicate memberships')
    return errors


def record_paths(root):
    for kind, pattern in PATTERNS.items():
        for path in sorted(Path(root).glob(pattern)):
            yield kind, path


def validate_project(root):
    errors = []
    records = {kind:{} for kind in KINDS}
    for kind,path in record_paths(root):
        try:
            data = load_record(path)
            failures = validate_record(data,kind,path,root)
        except (OSError,ValueError) as exc:
            failures = [str(exc)]
        errors.extend(str(path.relative_to(root))+': '+e for e in failures)
        if not failures:
            key = data[kind+'_slug'] if kind in {'spec','slice'} else data[kind+'_id']
            if key in records[kind]:
                errors.append(f'{kind} {key}: duplicate canonical records')
            else:
                records[kind][key] = data
    for slug,slice_record in records['slice'].items():
        spec = slice_record['spec_slug']
        if spec is not None and spec not in records['spec']:
            errors.append(f'slice {slug}: missing spec {spec}')
        current = slice_record['current']
        if current:
            build = records['build'].get(current['build_id'])
            entries = [] if not build else build['branches'] + (build['schedule']['work'] if build['schedule'] else [])
            matching=[e for e in entries if e['slice_slug']==slug and e['source']==current['source']]
            if not matching:
                errors.append(f'slice {slug}: current build/source does not resolve')
            elif any(e.get('tip_sha',e.get('prepared_sha'))!=current['tip_sha'] for e in matching):
                errors.append(f'slice {slug}: current tip differs from its build qualification pin')
    for bid,build in records['build'].items():
        for branch in build['branches']:
            if branch['slice_slug'] not in records['slice']:
                errors.append(f"build {bid}: missing slice JSON {branch['slice_slug']}")
    for rid,release in records['release'].items():
        for change in release['changes']:
            if change['slice_slug'] not in records['slice']:
                errors.append(f"release {rid}: missing slice JSON {change['slice_slug']}")
            if change['build_id'] is not None and change['build_id'] not in records['build']:
                errors.append(f"release {rid}: missing build JSON {change['build_id']}")
    return errors


def validate_evidence(data,root):
    """Stat producer evidence references; never interpret narrative files."""
    references=[]
    def phase(phase):
        if phase['evidence']:references.append(phase['evidence'])
        if phase['baseline']:references.append(phase['baseline']['evidence'])
        for receipt in phase['passes']:
            references.append(receipt['triage_evidence'])
            references.extend(r['evidence'] for r in receipt['reviewers'])
    if data['kind']=='build':
        entries=data['branches']+(data['schedule']['work'] if data['schedule'] else [])
        for entry in entries:
            phase(entry['trim_review']);phase(entry['review_progress'])
            references.extend(c['evidence'] for c in entry['checks'] if c['evidence'])
    elif data['kind']=='deployment' and data['evidence']:
        references.append(data['evidence'])
    elif data['kind']=='release' and data['acceptance']['evidence']:
        references.append(data['acceptance']['evidence'])
    errors=[]
    for value in sorted(set(references)):
        path=(Path(root)/value).resolve()
        try:
            path.relative_to(Path(root).resolve()/'plans')
            if not path.is_file() or not path.stat().st_size:errors.append('Missing or empty evidence: '+value)
        except (ValueError,OSError):errors.append('Unsafe evidence path: '+value)
    return errors


def validate_related(data,root):
    """Check one producer's references without blocking on unrelated archives."""
    root=Path(root).resolve()
    errors=[]
    def find(kind,key):
        if kind in {'build','deployment'}:
            paths=[root/'plans'/('builds' if kind=='build' else 'deployments')/key/'manifest.json']
        else:
            pattern=PATTERNS[kind].replace('*/*', '*/'+key)
            paths=list(root.glob(pattern))
        if any(not p.resolve().is_relative_to(root/'plans') for p in paths):
            errors.append(f'{kind} {key}: unsafe canonical path');return None
        if len(paths)!=1:
            errors.append(f'{kind} {key}: canonical record must resolve exactly once');return None
        try:
            record=load_record(paths[0]);failures=validate_record(record,kind,paths[0],root)
        except (OSError,ValueError) as exc:
            failures=[str(exc)]
        errors.extend(f'{kind} {key}: '+e for e in failures)
        return record if not failures else None
    kind=data['kind']
    if kind=='slice':
        if data['spec_slug'] is not None:
            spec=find('spec',data['spec_slug'])
            if spec and data['slice_slug'] not in {o['slice_slug'] for o in spec['slice_map']['owners']}:
                errors.append('$.spec_slug ownership map does not include this slice')
        current=data['current']
        if current:
            build=find('build',current['build_id'])
            if build:
                entries=build['branches']+(build['schedule']['work'] if build['schedule'] else [])
                matching=[e for e in entries if e['slice_slug']==data['slice_slug'] and e['source']==current['source']]
                if not matching:errors.append('$.current does not identify a build branch/work item')
                elif any(e.get('tip_sha',e.get('prepared_sha'))!=current['tip_sha'] for e in matching):
                    errors.append('$.current.tip_sha differs from its build qualification pin')
    elif kind=='build':
        for branch in data['branches']:
            item=find('slice',branch['slice_slug'])
            if item and item['spec_slug']!=branch['spec_slug']:
                errors.append('$.branches specification ownership disagrees with slice JSON')
    elif kind=='release':
        for change in data['changes']:
            find('slice',change['slice_slug'])
            if change['build_id'] is not None:find('build',change['build_id'])
    elif kind=='deployment':
        for member in data['included_slices']:find('slice',member['slice_slug'])
    elif kind=='spec' and data['slice_map']['status']=='approved':
        for slug in sorted({o['slice_slug'] for o in data['slice_map']['owners']}):
            item=find('slice',slug)
            if item and item['spec_slug']!=data['spec_slug']:
                errors.append('$.slice_map ownership disagrees with child slice JSON')
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('path',type=Path,help='Canonical JSON file or project root')
    parser.add_argument('--print-scope-digest',action='store_true')
    parser.add_argument('--project-root',type=Path,help='Check this file and its related records in the original project')
    args = parser.parse_args()
    try:
        if args.print_scope_digest:
            data=load_record(args.path)
            if data.get('kind')!='build':raise ValueError('Scope digests apply only to builds')
            structural=schema_errors(data,SCHEMA['$defs']['build'])
            if structural:raise ValueError('\n'.join(structural))
            print(scope_digest(data));return 0
        if args.path.is_dir():errors=validate_project(args.path.resolve())
        else:
            data=load_record(args.path)
            errors=validate_record(data,path=args.path,root=args.project_root)
            if not errors and args.project_root:
                errors.extend(validate_related(data,args.project_root))
                errors.extend(validate_evidence(data,args.project_root))
    except (OSError,ValueError) as exc:
        errors = [str(exc)]
    if errors:
        print('\n'.join(errors),file=sys.stderr)
        return 1
    print('Operational JSON valid.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
