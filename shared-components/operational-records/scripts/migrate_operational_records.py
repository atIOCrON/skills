#!/usr/bin/env python3
"""Explicit one-time import of historical records. Never used by the dashboard."""
from __future__ import annotations
import argparse
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile
import os
from validate_operational_records import load_record, validate_record, scope_digest

SHA = re.compile(r'^[0-9a-f]{40,64}$')
STAGES = {'draft','backlog','to_do','in_progress','hold','review','in_release','merged','fulfilled','superseded'}


def markdown_value(text, label, allowed):
    """Explicit historical import only; the dashboard never reads these fields."""
    pattern = r'(?im)^\s*(?:#{1,6}\s*)?(?:\*\*)?' + re.escape(label) + r'(?:\*\*)?\s*:?(?:\*\*)?\s*\n?\s*`?(' + '|'.join(allowed) + r')\b'
    match = re.search(pattern, text)
    return match[1].lower() if match else 'unknown'


def ownership_rows(text):
    columns = None
    owners = []
    for line in text.splitlines():
        if not line.lstrip().startswith('|'):
            columns = None
            continue
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        labels = [c.strip('`*').lower() for c in cells]
        if 'acceptance id' in labels:
            slice_column = next((i for i, c in enumerate(labels) if c in {'owning slice', 'slice', 'slice slug'}), None)
            columns = (labels.index('acceptance id'), slice_column) if slice_column is not None else None
            continue
        if columns and len(cells) > max(columns):
            acceptance = cells[columns[0]].strip('`*')
            cell = cells[columns[1]]
            link = re.fullmatch(r'\[([^]]+)\]\([^)]+\)', cell)
            slug = (link[1] if link else cell).strip('`*')
            if acceptance and not acceptance.startswith('-') and re.fullmatch(r'[a-z][a-z0-9_]*', slug):
                owners.append({'acceptance_id': acceptance, 'slice_slug': slug})
    return owners


def full_sha(value):
    return value if isinstance(value,str) and SHA.fullmatch(value) else None


def pr(raw):
    raw = raw if isinstance(raw,dict) else {}
    state = str(raw.get('state','none')).lower()
    state = {'open':'ready','opened':'ready','declined':'closed'}.get(state,state)
    return {'id':str(raw['id']) if raw.get('id') is not None else None,'url':raw.get('url'),
            'state':state if state in {'none','draft','ready','merged','closed'} else 'unknown',
            'target_branch':raw.get('target_branch'),'landed_sha':full_sha(raw.get('landed_sha') or raw.get('merge_sha'))}


def phase(raw,kind,tip,record_path,version=None):
    raw = raw if isinstance(raw,dict) else {}
    state = raw.get('status')
    completed = raw.get('completed_passes')
    if state == 'pending':
        state = 'running' if raw.get('evidence') or isinstance(completed,int) and completed > 0 else 'not_started'
    elif state not in {'clean','proportionate','review_cap_reached','waived'}:
        state = 'unknown'
    if state in {'clean','proportionate','review_cap_reached','waived'} and raw.get('sha',tip if kind=='code' else None) != tip:
        state = 'unknown'
    reason = raw.get('reason') or ('Historical phase state is unavailable.' if state=='unknown' else 'Review was explicitly waived.' if state=='waived' else None)
    result = {'status':state,'sha':tip if state in {'clean','proportionate','review_cap_reached','waived'} else None,
              'evidence':record_path if state in {'clean','proportionate','review_cap_reached','waived'} else None,
              'accounting':'unknown','completed_passes':None,'historical_completed_passes':None,'passes':[],'baseline':None,
              'reason':reason or 'Historical completed-pass receipts are unavailable; original JSON counts are retained in extensions.'}
    if kind=='code':
        limit = raw.get('pass_limit')
        result['pass_limit'] = limit if isinstance(limit,int) and not isinstance(limit,bool) and limit>0 else 5
    else:
        result['applicability'] = 'zero_diff' if raw.get('applicability')=='zero_diff' else 'normal'
    if version==1 and isinstance(raw.get('passes'),list):
        result.update(accounting='receipts',completed_passes=raw.get('completed_passes'),historical_completed_passes=raw.get('historical_completed_passes'),
                      passes=[{**r,'reason':r.get('reason'),'reviewers':r.get('reviewers',[])} for r in raw['passes']],reason=reason)
    elif state=='not_started' and completed==0 and not raw.get('historical_completed_passes'):
        result.update(accounting='receipts',completed_passes=0,historical_completed_passes=0,passes=[],reason=None)
    return result


class Migration:
    def __init__(self,root,reconcile_counts=False,reconcile_metadata=False):
        self.root = Path(root).resolve()
        self.outputs = {}
        self.reconcile_counts = reconcile_counts
        self.reconcile_metadata = reconcile_metadata
        self.baselines = {}
        self.warnings = []
        self.refs = {}
        self.plans = {'spec':{},'slice':{}}
        self.builds = {}
        self.releases = {}
        self.audit = 'plans/audits/operational-json-v2-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')

    def read(self,path):
        path = Path(path)
        raw = path.read_bytes()
        self.baselines[str(path)] = raw
        return load_record(path) if path.suffix=='.json' else raw.decode('utf-8')

    def add(self,path,data,kind):
        path = Path(path)
        if path.exists() and str(path) not in self.baselines:
            existing = self.read(path)
            if isinstance(existing,dict) and existing.get('schema_version')==2:
                changed = False
                if self.reconcile_metadata and existing.get('extensions',{}).get('imported_from'):
                    for field in ('approval','spec_slug'):
                        if field in data and existing.get(field) in (None,'unknown') and data[field] not in (None,'unknown'):
                            existing[field] = data[field]; changed = True
                    if kind == 'spec':
                        for field in ('status','owners'):
                            if existing['slice_map'][field] in ('unknown',[]) and data['slice_map'][field] not in ('unknown',[]):
                                existing['slice_map'][field] = data['slice_map'][field]; changed = True
                    if changed:
                        errors = validate_record(existing,kind,path,self.root)
                        if errors: raise ValueError(str(path)+': '+'; '.join(errors))
                        self.outputs[str(path)] = existing
                return existing
            raise ValueError('Refusing to replace unexpected record: '+str(path))
        rel=str(path.relative_to(self.root))
        data.setdefault('unresolved',[w for w in self.warnings if w.startswith(rel+':') or w.startswith(str(path)+':')])
        errors = validate_record(data,kind,path,self.root)
        if errors:
            self.warnings.extend(str(path.relative_to(self.root))+': '+e for e in errors)
            # Invalid historical records are imported explicitly. The dashboard rejects
            # them with field-level errors; the migration never fabricates repairs.
        self.outputs[str(path)] = data
        return data

    def relative(self,value):
        if not isinstance(value,str) or not value:
            return None
        path = Path(value)
        path = path if path.is_absolute() else self.root/path
        try:
            return str(path.resolve().relative_to(self.root)) if path.resolve().is_relative_to(self.root/'plans') else None
        except (ValueError,OSError):
            return None

    def scan_plans(self):
        for kind in ('spec','slice'):
            folder = 'specs' if kind=='spec' else 'slices'
            for path in sorted((self.root/'plans'/folder).glob('*/*/*.md')):
                if path.stem != path.parent.name or path.parent.parent.name not in STAGES:
                    continue
                slug = path.stem
                if slug in self.plans[kind]:
                    raise ValueError('Duplicate plan identity: '+slug)
                text = self.read(path)
                self.plans[kind][slug] = {'path':str(path.relative_to(self.root)),'stage':path.parent.parent.name,'text':text}
        # Explicit legacy plan import belongs here, never in the report.
        for stage in STAGES:
            for path in sorted((self.root/'plans'/stage).glob('*/*.md')):
                if path.stem==path.parent.name and path.stem not in self.plans['slice']:
                    self.plans['slice'][path.stem] = {'path':str(path.relative_to(self.root)),'stage':stage,'text':self.read(path),'legacy':True}

    def spec_for(self,slug):
        return self.owners.get(slug)

    def branch_spec(self, raw, slug):
        explicit = raw.get('spec_slug')
        if explicit:
            if self.spec_for(slug) and explicit != self.spec_for(slug):
                self.warnings.append('Slice '+slug+': historical JSON spec differs from plan metadata; preserved the explicit JSON value.')
            return explicit
        return self.spec_for(slug)

    def branch_slug(self,raw):
        value = raw.get('slice_slug') or raw.get('slug')
        if value:return value
        if isinstance(raw.get('plan'),str) and re.search(r'plans/(?:slices/[^/]+|(?:review|merged|fulfilled|to_do|in_progress))/[^/]+/[^/]+\.md$',raw['plan']):
            return Path(raw['plan']).parent.name
        return None

    def checks(self,raw):
        result = []
        for index,c in enumerate(raw.get('checks',[])):
            if not isinstance(c,dict):continue
            result.append({'id':c.get('id') or 'historical-check-'+str(index),'kind':c.get('kind','agent'),
                           'status':c.get('status','pending'),'sha':full_sha(c.get('sha')),
                           'evidence':self.relative(c.get('evidence')),'extensions':{k:v for k,v in c.items() if k not in {'id','kind','status','sha','evidence'}}})
        return result

    def implementation(self,raw,tip,checks):
        required = [c['id'] for c in checks if c['kind']=='agent']
        verified = bool(tip and required) and all(c['status']=='passed' and c['sha']==tip for c in checks if c['kind']=='agent')
        return {'status':'verified' if verified else 'running' if tip else 'not_started','sha':tip if verified else None,
                'required_check_ids':required,'reason':None}

    def import_counts(self,phase,original,rel):
        phase.setdefault('baseline',None)
        if phase['accounting']!='unknown' or not isinstance(original,dict):return
        current=original.get('completed_passes')
        historical=original.get('historical_completed_passes',0)
        if not all(isinstance(n,int) and not isinstance(n,bool) and n>=0 for n in (current,historical)):return
        if current+historical==0 and phase['status'] in {'clean','proportionate','review_cap_reached'} and phase.get('applicability')!='zero_diff':
            phase['reason']='Historical JSON claims a completed review but records zero passes; reconcile the original accounting.'
            return
        if 'pass_limit' in phase and current+historical>phase['pass_limit']:
            phase['reason']='Historical JSON counts exceed the recorded pass limit; reconcile the original accounting.'
            return
        phase.update(accounting='receipts',completed_passes=current,historical_completed_passes=historical,
                     baseline={'completed_passes':current,'historical_completed_passes':historical,'evidence':self.audit+'/originals/'+rel})
        if phase['status'] not in {'unknown','waived'}:phase['reason']=None

    def import_builds(self):
        for path in sorted((self.root/'plans/builds').glob('*/manifest.json')):
            raw = self.read(path)
            bid = path.parent.name
            if raw.get('schema_version')==2:
                changed=False
                if self.reconcile_counts:
                    for b in raw['branches']:
                        for field in ('trim_review','review_progress'):
                            before=json.dumps(b[field],sort_keys=True)
                            self.import_counts(b[field],b['extensions'].get('historical_record',{}).get(field),str(path.relative_to(self.root)))
                            changed |= before!=json.dumps(b[field],sort_keys=True)
                    if raw['schedule']:
                        for w in raw['schedule']['work']:
                            for field in ('trim_review','review_progress'):
                                before=json.dumps(w[field],sort_keys=True)
                                self.import_counts(w[field],w['extensions'].get('historical_record',{}).get(field),str(path.relative_to(self.root)))
                                changed |= before!=json.dumps(w[field],sort_keys=True)
                    if changed:
                        failures=validate_record(raw,'build',path,self.root)
                        if failures:raise ValueError(str(path)+': '+'; '.join(failures))
                        self.outputs[str(path)]=raw
                if self.reconcile_metadata:
                    for item in raw['branches'] + (raw['schedule']['work'] if raw['schedule'] else []):
                        if item['spec_slug'] is None:
                            spec = self.branch_spec(item['extensions'].get('historical_record',{}),item['slice_slug'])
                            if spec is not None:
                                item['spec_slug'] = spec; changed = True
                    if changed:
                        if raw['freeze']: raw['freeze']['scope_digest'] = scope_digest(raw)
                        failures = validate_record(raw,'build',path,self.root)
                        if failures: raise ValueError(str(path)+': '+'; '.join(failures))
                        self.outputs[str(path)] = raw
                self.builds[bid] = raw;continue
            rel = str(path.relative_to(self.root))
            branches=[]
            unmapped=[]
            for b in raw.get('branches',[]):
                slug=self.branch_slug(b)
                if not slug:
                    self.warnings.append(rel+': '+str(b.get('source'))+' has no resolvable slice identity');unmapped.append(b);continue
                tip=full_sha(b.get('tip_sha'))
                checks=self.checks(b)
                reviews=[{'reviewer':r.get('reviewer'),'status':r.get('status') if r.get('status') in {'pending','clean','changes_required','waived'} else 'unknown','sha':full_sha(r.get('sha')),
                          'evidence':self.relative(r.get('evidence')),'method':r.get('method') if r.get('method') in {'direct','equal_range_diff','reviewed_restack','test_only_closure'} else None,
                          'origin_sha':full_sha(r.get('origin_sha'))} for r in b.get('reviews',[]) if isinstance(r,dict)]
                trim=phase(b.get('trim_review'),'trim',tip,rel,raw.get('review_records_version'))
                code=phase(b.get('review_progress'),'code',tip,rel,raw.get('review_records_version'))
                if code['status']=='clean' and ({r['reviewer'] for r in reviews if r['status']=='clean' and r['sha']==tip}!={'claude','codex','cursor'} or trim['status']!='proportionate'):
                    code.update(status='unknown',sha=None,evidence=None,reason='Historical JSON does not establish three clean current-tip reviews and proportionate trim.')
                self.import_counts(trim,b.get('trim_review'),rel)
                self.import_counts(code,b.get('review_progress'),rel)
                parent=b.get('parent') or {}
                parent={'branch':parent.get('branch'),'sha':full_sha(parent.get('sha'))}
                branches.append({'slice_slug':slug,'spec_slug':self.branch_spec(b,slug),'plan':b.get('plan'),'source':b.get('source'),
                                 'parent':parent,'target':parent['branch'],'tip_sha':tip,'tree_sha':full_sha(b.get('tree_sha')),
                                 'implementation':self.implementation(b,tip,checks),'trim_review':trim,'review_progress':code,'checks':checks,
                                 'reviews':reviews,'change_request':pr(b.get('change_request')),'extensions':{'historical_record':b}})
            schedule=None
            if isinstance(raw.get('schedule'),dict):
                work=[]
                for item in raw['schedule'].get('work',[]):
                    slug=self.branch_slug(item)
                    if not slug:continue
                    accepted=next((b for b in branches if b['slice_slug']==slug),None)
                    tip=full_sha(item.get('prepared_sha'))
                    checks=self.checks(item)
                    work.append({'slice_slug':slug,'spec_slug':self.branch_spec(item,slug),'plan':item.get('plan'),'source':item.get('source'),
                                 'status':item.get('status'),'parent':accepted['parent'] if accepted else item.get('authoring_base'),
                                 'prepared_sha':tip,'waiting_on':item.get('waiting_on',[]),
                                 'implementation':self.implementation(item,tip,checks),
                                 'trim_review':phase(item.get('trim_review'),'trim',tip,rel),
                                 'review_progress':phase(item.get('review_progress'),'code',tip,rel),'checks':checks,
                                 'extensions':{'historical_record':item}})
                schedule={'work':work,'extensions':{k:v for k,v in raw['schedule'].items() if k!='work'}}
            data={'schema_version':2,'kind':'build','build_id':bid,'state':raw.get('state'),
                  'base':{'branch':raw.get('base',{}).get('branch'),'sha':raw.get('base',{}).get('sha')},
                  'branches':branches,'schedule':schedule,'freeze':None,'extensions':{k:v for k,v in raw.items() if k not in {'branches','schedule'}}}
            if unmapped:data['extensions']['unmapped_branches']=unmapped
            old_freeze=raw.get('freeze')
            if isinstance(old_freeze,dict) and old_freeze.get('frozen_at') and old_freeze.get('authorized_by'):
                data['freeze']={'frozen_at':old_freeze['frozen_at'],'authorized_by':old_freeze['authorized_by'],'scope_digest':scope_digest(data)}
            self.builds[bid]=self.add(path,data,'build')

    def import_specs(self):
        self.owners={}
        owner_candidates=defaultdict(set)
        for slug,plan in self.plans['spec'].items():
            path=self.root/Path(plan['path']).with_name(slug+'.slices.md')
            text=self.read(path) if path.exists() else ''
            owners=ownership_rows(text)
            for owner in owners:
                if plan['stage']!='superseded': owner_candidates[owner['slice_slug']].add(slug)
            map_status=markdown_value(text,'Slice Map Status',('draft','approved','stale'))
            approval=markdown_value(plan['text'],'Approval Status',('draft','approved'))
            data={'schema_version':2,'kind':'spec','spec_slug':slug,'stage':plan['stage'],'approval':approval,
                  'plan':plan['path'],'slice_map':{'status':map_status,'owners':owners},'extensions':{'imported_from':plan['path']}}
            self.add(self.root/Path(plan['path']).with_name('record.json'),data,'spec')
        self.owners.update({child:next(iter(parents)) for child,parents in owner_candidates.items() if len(parents)==1})
        # Explicit parent references fill relationships absent from historical maps.
        for slug,plan in self.plans['slice'].items():
            match=re.search(r'(?im)^Parent:\s*\[[^]]+\]\(([^)]+)\)',plan['text'])
            parent_slug=None
            if match:
                parent=(self.root/plan['path']).parent/ match[1]
                rel=self.relative(str(parent))
                if rel and rel.startswith('plans/specs/') and parent.stem in self.plans['spec']:
                    parent_slug=parent.stem
            if not parent_slug:
                match=re.search(r'plans/specs/(?:[^/]+/)?([^/]+)/\1\.md',plan['text'])
                parent_slug=match[1] if match and match[1] in self.plans['spec'] else None
            if parent_slug:
                if slug in self.owners and self.owners[slug]!=parent_slug:self.warnings.append('Slice '+slug+': explicit parent disagrees with historical map; imported the explicit parent for operator review.')
                self.owners[slug]=parent_slug

    def import_releases(self):
        for path in sorted((self.root/'plans/releases').glob('*/*/*.json')):
            if path.name not in {'preparation.json','manifest.json','release.json'}:continue
            raw=self.read(path);rid=path.parent.name
            canonical=path.with_name('preparation.json')
            if raw.get('schema_version')==2 and raw.get('kind')=='release':self.releases[rid]=raw;continue
            if canonical.exists() and canonical!=path:continue
            changes=[]
            inputs = raw.get('changes') or raw.get('branches') or []
            if not raw.get('changes') and isinstance(raw.get('integration'),dict) and raw['integration'].get('inputs'):
                inputs=raw['integration']['inputs']
            for c in inputs:
                slug=self.branch_slug(c)
                if not slug:
                    for value in c.get('verification_references',[]):
                        match=re.search(r'plans/slices/[^/]+/([^/]+)/',value)
                        if match:slug=match[1];break
                if not slug:
                    matches={b['slice_slug'] for build in self.builds.values() for b in build['branches'] if b['source']==c.get('source')}
                    if len(matches)==1:slug=next(iter(matches))
                if not slug:continue
                matches=[bid for bid,build in self.builds.items() if any(b['slice_slug']==slug and b['source']==c.get('source') for b in build['branches'])]
                pin=c.get('original_parent') or c.get('parent') or {}
                if not pin:
                    inherited=[b for build in self.builds.values() for b in build['branches'] if b['slice_slug']==slug and b['source']==c.get('source') and b['tip_sha']==(c.get('head_sha') or c.get('tip_sha'))]
                    if inherited:pin=inherited[0]['parent']
                if not pin:
                    self.warnings.append(str(path)+': release member '+slug+' lacks a pinned parent; retained in historical_record only');continue
                changes.append({'slice_slug':slug,'build_id':matches[0] if len(matches)==1 else None,'source':c.get('source'),
                                'head_sha':full_sha(c.get('head_sha') or c.get('tip_sha')),'original_parent':{'branch':pin.get('branch'),'sha':full_sha(pin.get('sha'))},
                                'state':'merged' if str(c.get('state')).lower()=='merged' else 'unknown','pr':pr(c.get('pr') or c.get('change_request')),
                                'extensions':{'historical_record':c}})
            integration=raw.get('integration') or {}
            candidate=full_sha(raw.get('candidate_sha') or raw.get('candidate_commit') or integration.get('candidate_sha') or integration.get('candidate_commit_sha'))
            tree=full_sha(raw.get('candidate_tree') or integration.get('tree_sha'))
            if isinstance(raw.get('candidate_commit'),dict):candidate=full_sha(raw['candidate_commit'].get('sha'))
            state={'awaiting-final-review':'ready','assembled':'assembled','building':'preparing'}.get(raw.get('state'),'unknown')
            final_raw=raw.get('final_pr') or raw.get('lifecycle_final_pr')
            if isinstance(final_raw,str):
                final_raw={'url':final_raw,'id':final_raw.rstrip('/').split('/')[-1],'state':'merged' if full_sha(raw.get('landed_master_sha')) else 'unknown','landed_sha':raw.get('landed_master_sha')}
            final=pr(final_raw)
            if final['state']=='merged' and candidate:state='merged'
            base=raw.get('base');base={'branch':base.get('branch'),'sha':full_sha(base.get('sha'))} if isinstance(base,dict) else None
            data={'schema_version':2,'kind':'release','release_id':rid,'lifecycle':raw.get('lifecycle') or path.parent.parent.name,'state':state,
                  'base':base,'integration_branch':raw.get('integration_branch') or integration.get('branch'),'candidate':{'sha':candidate,'tree_sha':tree},
                  'changes':changes,'final_pr':final,'acceptance':{'status':'unknown','evidence':None},
                  'staging_receipt':self.relative(raw.get('staging_receipt') if isinstance(raw.get('staging_receipt'),str) else None),
                  'extensions':{'historical_record':raw,'imported_from':str(path.relative_to(self.root))}}
            data['unresolved']=[w for w in self.warnings if w.startswith(str(path)+':')]
            self.releases[rid]=self.add(canonical,data,'release')

    def import_slices(self):
        result=subprocess.run(['git','-C',str(self.root),'for-each-ref','--format=%(refname) %(objectname)','refs/heads','refs/remotes/origin'],capture_output=True,text=True,check=True)
        for line in result.stdout.splitlines():
            ref,sha=line.split()
            if ref.startswith('refs/heads/'):self.refs[ref.removeprefix('refs/heads/')]=sha
            else:self.refs.setdefault(ref.removeprefix('refs/remotes/origin/'),sha)
        candidates=defaultdict(list)
        for bid,build in self.builds.items():
            original=build['extensions']
            stamp=str(original.get('updated_at') or original.get('created_at') or bid)
            for b in build['branches']:
                candidates[b['slice_slug']].append((bid,b['source'],b['tip_sha'],stamp))
            if build['schedule']:
                accepted={b['slice_slug'] for b in build['branches']}
                for w in build['schedule']['work']:
                    if w['slice_slug'] not in accepted:candidates[w['slice_slug']].append((bid,w['source'],w['prepared_sha'],stamp))
        for slug,plan in self.plans['slice'].items():
            choices=candidates[slug];notes=[];current=None
            declared=None
            for pattern in [r'^(?:Source [Bb]ranch|Branch)\s*:\s*`?([^`\s]+)',r'\bBranch `([^`]+)` from',r'Intended branch:\s*`([^`]+)`']:
                m=re.search(pattern,plan['text'],re.M)
                if m:declared=m[1];break
            active=[c for release in self.releases.values() if release['lifecycle']=='active' for c in release['changes'] if c['slice_slug']==slug and c['state']=='merged']
            source=active[0]['source'] if len({c['source'] for c in active})==1 else declared
            sources={c[1] for c in choices}
            if source not in sources:source=next(iter(sources)) if len(sources)==1 else None
            if source:
                matching=[c for c in choices if c[1]==source]
                local=self.refs.get(source)
                matching.sort(key=lambda c:(bool(local) and c[2]==local,c[3],c[0]),reverse=True)
                if matching:
                    bid,source,pin,_=matching[0]
                    current={'build_id':bid,'source':source,'tip_sha':local or pin}
                    if local and pin and local!=pin:notes.append('Import found local source drift; recorded current pin requires build qualification reconciliation.')
            if choices and not current:notes.append('Historical JSON records do not establish a unique current build/source; resolve current explicitly.')
            approval=markdown_value(plan['text'],'Approval Status',('draft','approved'))
            spec=self.spec_for(slug)
            existing_path=self.root/Path(plan['path']).with_name('record.json')
            selection=load_record(existing_path).get('current') if existing_path.exists() else current
            if selection:
                build=self.builds.get(selection['build_id'],{})
                selected=next((b for b in build.get('branches',[]) if b['slice_slug']==slug and b['source']==selection['source']),None)
                if selected is None and build.get('schedule'):
                    selected=next((w for w in build['schedule']['work'] if w['slice_slug']==slug and w['source']==selection['source']),None)
                if selected and selected['spec_slug'] is not None: spec=selected['spec_slug']
            data={'schema_version':2,'kind':'slice','slice_slug':slug,'spec_slug':spec,'stage':plan['stage'],
                  'approval':approval,'plan':plan['path'],'current':current,'notes':notes,
                  'extensions':{'imported_from':plan['path']}}
            path=self.root/Path(plan['path']).with_name('record.json') if not plan.get('legacy') else self.root/'plans/slices'/plan['stage']/slug/'record.json'
            self.add(path,data,'slice')

    def import_deployments(self):
        versions={(b['slice_slug'],b['source'],b['tip_sha']) for build in self.builds.values() for b in build['branches'] if b['tip_sha']}
        versions|={(c['slice_slug'],c['source'],c['head_sha']) for release in self.releases.values() for c in release['changes'] if c['head_sha']}
        ancestry={}
        for path in sorted((self.root/'plans/deployments').glob('*/manifest.json')):
            raw=self.read(path)
            if raw.get('schema_version')==2:continue
            d=raw.get('deployment') if isinstance(raw.get('deployment'),dict) else {}
            candidate=full_sha(d.get('live_candidate_sha') or (raw.get('integration') or {}).get('candidate_sha') or raw.get('expected_candidate_sha') or raw.get('staging_after'))
            outcome='verified' if raw.get('state')=='staged' and full_sha(raw.get('staging_after'))==candidate and candidate else 'failed' if raw.get('failure') else 'pending' if raw.get('state')=='building' else 'unknown'
            explicit={(b.get('source'),b.get('tip_sha') or b.get('head_sha')) for b in raw.get('branches',[]) if isinstance(b,dict)}
            ancestors=set()
            if candidate and outcome=='verified':
                if candidate not in ancestry:
                    git=subprocess.run(['git','-C',str(self.root),'rev-list',candidate],capture_output=True,text=True)
                    ancestry[candidate]=set(git.stdout.splitlines()) if git.returncode==0 else set()
                ancestors=ancestry[candidate]
            members=[{'slice_slug':slug,'source':source,'tip_sha':pin} for slug,source,pin in sorted(versions) if (source,pin) in explicit or pin in ancestors]
            rel=str(path.relative_to(self.root))
            data={'schema_version':2,'kind':'deployment','deployment_id':path.parent.name,'environment':raw.get('environment'),
                  'release_id':None,'candidate':{'sha':candidate,'tree_sha':full_sha((raw.get('integration') or {}).get('tree_sha'))},
                  'outcome':outcome,'included_slices':members,'evidence':rel if outcome=='verified' else None,'extensions':{'historical_record':raw}}
            self.add(path,data,'deployment')

    def prepare(self):
        self.scan_plans();self.import_specs();self.import_builds();self.import_releases();self.import_slices();self.import_deployments()
        return {'records':len(self.outputs),'by_kind':dict(__import__('collections').Counter(d['kind'] for d in self.outputs.values())),
                'warnings':self.warnings,'audit':self.audit}

    def apply(self):
        # Check every input before writing anything; never overwrite concurrent agent updates.
        for value,raw in self.baselines.items():
            if Path(value).read_bytes()!=raw:raise ValueError('Input changed during migration: '+value)
        for value in self.outputs:
            if value not in self.baselines and Path(value).exists():raise ValueError('Output appeared during migration: '+value)
        audit=self.root/self.audit
        audit.mkdir(parents=True)
        receipts=[]
        for value,data in self.outputs.items():
            path=Path(value);rel=path.relative_to(self.root)
            before=self.baselines.get(value)
            if before is not None:
                backup=audit/'originals'/rel
                backup.parent.mkdir(parents=True,exist_ok=True);backup.write_bytes(before)
                if path.read_bytes()!=before:raise ValueError('Input changed before replacement: '+value)
            path.parent.mkdir(parents=True,exist_ok=True)
            encoded=(json.dumps(data,indent=2,ensure_ascii=False)+'\n').encode()
            with tempfile.NamedTemporaryFile(dir=path.parent,prefix='.record-',delete=False) as tmp:
                tmp.write(encoded);temp=tmp.name
            os.replace(temp,path)
            receipts.append({'path':str(rel),'original_sha256':hashlib.sha256(before).hexdigest() if before is not None else None,
                             'new_sha256':hashlib.sha256(encoded).hexdigest()})
        (audit/'receipt.json').write_text(json.dumps({'records':receipts,'warnings':self.warnings},indent=2)+'\n')
        return str(audit/'receipt.json')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project',type=Path)
    parser.add_argument('--reconcile-json-counts',action='store_true',help='Import explicit historical JSON counts into pinned baselines in adopted v2 records')
    parser.add_argument('--reconcile-plan-metadata',action='store_true',help='Restore missing imported approvals and spec relationships without changing source pins or qualification')
    parser.add_argument('--apply',action='store_true',help='Apply the import with byte-for-byte originals and a migration receipt')
    args=parser.parse_args()
    migration=Migration(args.project,args.reconcile_json_counts,args.reconcile_plan_metadata)
    try:
        summary=migration.prepare()
        if args.apply:summary['receipt']=migration.apply()
        print(json.dumps(summary,indent=2))
        return 0
    except (OSError,ValueError,subprocess.SubprocessError) as exc:
        print(str(exc),file=__import__('sys').stderr);return 1

if __name__=='__main__':raise SystemExit(main())
