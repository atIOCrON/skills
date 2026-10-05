#!/usr/bin/env python3
"""Export selected current-build operator handoffs to the branch tracker row contract."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
from validate_operational_records import load_record, validate_record, record_paths

STAGES = {'draft':'Draft','backlog':'Backlog','to_do':'To Do','in_progress':'In Progress',
          'review':'Review','in_release':'In Release','merged':'Merged','fulfilled':'Fulfilled',
          'superseded':'Superseded','hold':'On Hold'}


def export_rows(root: Path, manifest: Path, sources: list[str]) -> list[dict]:
    root=root.resolve(); manifest=manifest.resolve()
    try: manifest.relative_to(root/'plans/builds')
    except ValueError: raise ValueError('Manifest must be under project plans/builds')
    data=load_record(manifest)
    errors=validate_record(data,'build',manifest,root)
    if errors: raise ValueError('; '.join(errors))
    if not sources or len(set(sources))!=len(sources): raise ValueError('Request distinct source branches')
    branches={b['source']:b for b in data['branches']}
    slices={}
    requested_slugs={branches[s]['slice_slug'] for s in sources if s in branches}
    for kind,path in record_paths(root):
        if kind!='slice' or path.parent.name not in requested_slugs:continue
        record=load_record(path)
        errors=validate_record(record,'slice',path,root)
        if errors:raise ValueError('; '.join(errors))
        slug=record['slice_slug']
        if slug in slices:raise ValueError('Duplicate slice record: '+slug)
        slices[slug]=record
    for source in sources:
        if source not in branches:raise ValueError('Source absent from this build: '+source)
        b=branches[source];record=slices.get(b['slice_slug']);handoff=b.get('operator_handoff')
        if record is None or record['current']!={'build_id':data['build_id'],'source':source,'tip_sha':b['tip_sha']}:
            raise ValueError('Current slice selection/pin differs from this build: '+source)
        if not handoff or handoff['state']!='ready' or handoff['sha']!=b['tip_sha']:
            raise ValueError('Ready current-pin operator handoff required: '+source)
    # Connect only actual ancestry, including omitted ancestors; a shared base alone is not a dependency.
    def ancestors(source):
        result=set();parent=branches[source]['target']
        while parent in branches:
            if parent in result:raise ValueError('Branch dependency cycle')
            result.add(parent);parent=branches[parent]['target']
        return result
    ancestry={s:ancestors(s) for s in sources};remaining=list(sources);groups=[]
    while remaining:
        group={remaining[0]};changed=True
        while changed:
            additions={s for s in remaining if any(s in ancestry[t] or t in ancestry[s] or ancestry[s]&ancestry[t] for t in group)}-group
            changed=bool(additions);group|=additions
        groups.append([s for s in remaining if s in group]);remaining=[s for s in remaining if s not in group]
    rows=[]
    for stack,group in enumerate(groups,1):
        while group:
            ready=[s for s in group if not ancestry[s]&set(group)]
            if not ready:raise ValueError('Branch dependency cycle')
            for source in ready:
                group.remove(source);b=branches[source];record=slices[b['slice_slug']];h=b['operator_handoff']
                row={'Sort':len(rows)+1,'Stack':stack,'Target Branch':b['target'],'Source Branch':source,
                     'Status':STAGES[record['stage']],'To Do':'','Plan':record['plan'],'Note':''}
                for field,key in [('Operator problem','problem'),('Solution','solution'),('Suggested operator test path','test_path'),('Pass condition','pass_condition')]:
                    row[field]=' '.join(h[key].split())
                for field,key in [('Type(s)','types'),('Change surface(s)','change_surfaces'),('Package(s)','packages')]:row[field]='; '.join(h[key])
                rows.append(row)
    return rows


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project',type=Path);parser.add_argument('manifest',type=Path)
    parser.add_argument('--source',action='append',required=True)
    args=parser.parse_args()
    try:rows=export_rows(args.project,args.manifest,args.source)
    except (ValueError,OSError) as exc:parser.exit(2,str(exc)+'\n')
    print(json.dumps(rows,indent=2,ensure_ascii=False))

if __name__=='__main__':main()
