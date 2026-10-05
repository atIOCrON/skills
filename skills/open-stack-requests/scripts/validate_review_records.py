#!/usr/bin/env python3
"""Validate structured review accounting and its local evidence; never edit records."""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys

REVIEWERS = {'claude', 'codex', 'cursor'}
SHA = re.compile(r'[0-9a-f]{40,64}')


def count_value(value):
    return value if isinstance(value, int) and not isinstance(value, bool) and value >= 0 else None


def utc_timestamp(value):
    try:
        stamp = datetime.fromisoformat(value.replace('Z', '+00:00'))
        return stamp.tzinfo is not None and stamp.utcoffset() == timezone.utc.utcoffset(stamp)
    except (AttributeError, TypeError, ValueError):
        return False


def evidence_errors(value, prefix, root=None):
    if not isinstance(value, str) or not value.strip():
        return [prefix + ' must be a non-empty evidence path']
    if root is None:
        return []
    root = Path(root).resolve()
    path = Path(value)
    path = path if path.is_absolute() else root / path
    try:
        path = path.resolve()
        path.relative_to(root / 'plans')
        if not path.is_file() or path.stat().st_size == 0:
            return [prefix + ' evidence is missing or empty: ' + value]
    except (ValueError, OSError):
        return [prefix + ' evidence must resolve inside the project plans directory: ' + value]
    return []


def validate_phase(phase, kind, tip_sha, root=None, prefix='review'):
    """Check receipts, period totals and the current result's identity."""
    if not isinstance(phase, dict):
        return [prefix + ' must be an object']
    errors = []
    counts = {key: count_value(phase.get(key)) for key in ('completed_passes', 'historical_completed_passes')}
    for key, value in counts.items():
        if value is None:
            errors.append(f'{prefix}.{key} must be a non-negative integer')
    states = {'pending', 'proportionate', 'waived'} if kind == 'trim' else {'pending', 'clean', 'review_cap_reached', 'waived'}
    status = phase.get('status')
    if not isinstance(status, str) or status not in states:
        errors.append(prefix + '.status is invalid')
    if 'sha' not in phase or 'evidence' not in phase:
        errors.append(prefix + ' requires explicit sha and evidence fields (null while unavailable)')
    if isinstance(status, str) and status != 'pending' and status in states:
        if not isinstance(tip_sha, str) or not SHA.fullmatch(tip_sha) or phase.get('sha') != tip_sha:
            errors.append(prefix + '.sha must match the full current tip_sha when the result is complete')
        errors.extend(evidence_errors(phase.get('evidence'), prefix + '.evidence', root))
    elif status == 'pending' and phase.get('sha') is not None:
        errors.append(prefix + '.sha must be null while the current result is pending')
    passes = phase.get('passes')
    if not isinstance(passes, list):
        return errors + [prefix + '.passes must be an array of completed or disqualified pass receipts']
    seen = set()
    totals = Counter()
    for index, receipt in enumerate(passes):
        at = f'{prefix}.passes[{index}]'
        if not isinstance(receipt, dict):
            errors.append(at + ' must be an object')
            continue
        pass_id = receipt.get('pass_id')
        if not isinstance(pass_id, str) or not pass_id.strip():
            errors.append(at + '.pass_id must be a non-empty stable ID')
        elif pass_id in seen:
            errors.append(at + '.pass_id duplicates ' + pass_id)
        else:
            seen.add(pass_id)
        period, state = receipt.get('period'), receipt.get('status')
        if period not in ('current', 'historical'):
            errors.append(at + '.period must be current or historical')
        if state not in ('completed', 'disqualified'):
            errors.append(at + '.status must be completed or disqualified; incomplete launches are not receipts')
        if not utc_timestamp(receipt.get('completed_at')):
            errors.append(at + '.completed_at must be a UTC ISO timestamp')
        if not isinstance(receipt.get('reviewed_sha'), str) or not SHA.fullmatch(receipt['reviewed_sha']):
            errors.append(at + '.reviewed_sha must be a full hexadecimal SHA')
        errors.extend(evidence_errors(receipt.get('triage_evidence'), at + '.triage_evidence', root))
        if state == 'disqualified':
            if not isinstance(receipt.get('reason'), str) or not receipt['reason'].strip():
                errors.append(at + '.reason is required for a disqualified pass')
            continue
        reviewers = receipt.get('reviewers')
        if not isinstance(reviewers, list):
            errors.append(at + '.reviewers must contain the three validated reviewer outputs')
            continue
        names = [r.get('reviewer') for r in reviewers if isinstance(r, dict) and isinstance(r.get('reviewer'), str)]
        if len(reviewers) != 3 or set(names) != REVIEWERS:
            errors.append(at + '.reviewers must contain Claude, Codex and Cursor exactly once')
        for number, reviewer in enumerate(reviewers):
            where = f'{at}.reviewers[{number}]'
            if not isinstance(reviewer, dict):
                errors.append(where + ' must be an object')
                continue
            if reviewer.get('validated') is not True:
                errors.append(where + '.validated must be true after the existing reviewer-output checks pass')
            if reviewer.get('sha') != receipt.get('reviewed_sha'):
                errors.append(where + '.sha must match the pass reviewed_sha')
            errors.extend(evidence_errors(reviewer.get('evidence'), where + '.evidence', root))
        if period in ('current', 'historical'):
            totals[period] += 1
    for key, period in [('completed_passes', 'current'), ('historical_completed_passes', 'historical')]:
        if counts[key] is not None and counts[key] != totals[period]:
            errors.append(f'{prefix}.{key} is {counts[key]}, but {totals[period]} completed {period} pass receipts are recorded')
    total = sum(totals.values())
    if kind == 'code':
        limit = count_value(phase.get('pass_limit'))
        if not limit:
            errors.append(prefix + '.pass_limit must be a positive integer')
        elif total > limit:
            errors.append(prefix + '.completed pass total exceeds pass_limit')
        elif status == 'review_cap_reached' and total != limit:
            errors.append(prefix + '.review_cap_reached requires the completed pass total to equal pass_limit')
    if status in ('clean', 'proportionate', 'review_cap_reached') and total == 0:
        if kind != 'trim' or phase.get('applicability') != 'zero_diff':
            errors.append(prefix + ' requires a completed pass; zero-pass trim requires applicability: zero_diff and evidence')
    return errors


def validate_review_records(data, root=None, require=True):
    if not isinstance(data, dict):
        return ['manifest must be an object']
    if data.get('schema_version') == 2:
        from validate_operational_records import validate_record
        return validate_record(data, 'build')
    version = data.get('review_records_version')
    if version is None and not require:
        return []
    if version != 1 or not isinstance(version, int) or isinstance(version, bool):
        return ['review_records_version must be 1; legacy manifests need evidence reconciliation before adopting this contract']
    branches = data.get('branches')
    if not isinstance(branches, list):
        return ['branches must be an array']
    errors = []
    for index, branch in enumerate(branches):
        prefix = f'branches[{index}]'
        if not isinstance(branch, dict):
            errors.append(prefix + ' must be an object')
            continue
        if root is not None:
            errors.extend(evidence_errors(branch.get('plan'), prefix + '.plan', root))
            for field in ('reviews', 'checks'):
                entries = branch.get(field)
                if not isinstance(entries, list):
                    continue  # The full manifest validator reports structural errors.
                for number, entry in enumerate(entries):
                    if isinstance(entry, dict) and entry.get('evidence') is not None:
                        errors.extend(evidence_errors(entry['evidence'], f'{prefix}.{field}[{number}].evidence', root))
            handoff = branch.get('review_handoff')
            if isinstance(handoff, dict):
                errors.extend(evidence_errors(handoff.get('evidence'), prefix + '.review_handoff.evidence', root))
        for field, kind in [('trim_review', 'trim'), ('review_progress', 'code')]:
            errors.extend(validate_phase(branch.get(field), kind, branch.get('tip_sha'), root, prefix + '.' + field))
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path)
    parser.add_argument('--project-root', type=Path, required=True)
    parser.add_argument('--allow-legacy', action='store_true', help='Check the existing manifest contract without requiring v1 pass receipts')
    args = parser.parse_args()
    try:
        data = json.loads(args.manifest.read_text(encoding='utf-8'))
    except (OSError, ValueError) as exc:
        parser.exit(1, f'Cannot read manifest: {exc}\n')
    from validate_release_manifest import validate
    try:
        errors = validate(data)
    except (TypeError, ValueError, AttributeError, KeyError) as exc:
        errors = ['Malformed manifest field types: ' + str(exc)]
    errors.extend(validate_review_records(data, args.project_root, require=not args.allow_legacy))
    errors = list(dict.fromkeys(errors))
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    if data.get('schema_version') == 2:
        print('Schema-v2 operational build valid; historical extensions do not certify new review receipts.')
        return 0
    print('Manifest and review records valid.' + (' Legacy review counts remain unverified.' if data.get('review_records_version') is None else ' Evidence paths checked.'))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
