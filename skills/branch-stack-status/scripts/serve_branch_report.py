#!/usr/bin/env python3
"""Serve a read-only slice/branch report using Python's standard library."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import html
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
import threading
from urllib.parse import parse_qs, quote, urlparse
import webbrowser

from validate_operational_records import load_record, validate_record, record_paths

COLUMNS = [{'id':key,'label':title,'default':default} for key,title,default in [
    ('target','Target branches',True),('source','Source branches',True),('stage','Stages',True),
    ('status','Statuses',True),('trim_loops','Trim loops',True),('code_loops','Code loops',True),
    ('specs','Specs',True),('slice','Slices',True),('builds','Builds',True),('releases','Releases',True),
    ('prs','PRs',True),('deployments','Deployments',True),('problem','Operator problems',False),
    ('solution','Solutions',False),('test_path','Suggested operator test paths',False),
    ('pass_condition','Pass conditions',False),('types','Types',True),('change_surfaces','Change surfaces',True),
    ('packages','Packages',True)]]
HEADERS = [column['label'] for column in COLUMNS]
MAX_RECORD_BYTES = 16 * 1024 * 1024


def record_link(path: str) -> str:
    return '/record?path=' + quote(path, safe='')


def label(name: str, path: str, **extra) -> dict:
    return {'name': name, 'url': record_link(path), **extra}


def review_summary(branch: dict, current_sha: str) -> dict:
    """Derive display values exclusively from the validated JSON contract."""
    code, trim = branch['review_progress'], branch['trim_review']
    notes = [name + ': ' + phase['reason'] for name, phase in (('Trim review',trim), ('Code review',code)) if phase['reason']]
    counts = {name: phase['completed_passes'] + phase['historical_completed_passes']
              if phase['accounting'] == 'receipts' else 'Unclear'
              for name, phase in [('code_loops',code),('trim_loops',trim)]}
    if current_sha != branch['tip_sha']:
        status = 'Unclear'
        notes.append('Current slice pin differs from the build review pin; update qualification in JSON before claiming completion.')
    elif code['status'] == 'review_cap_reached':
        status = 'Exhausted'
    elif code['status'] == 'clean':
        status = 'Complete'
    elif code['status'] == 'running':
        status = 'Code Review Started'
    elif code['status'] in {'unknown','waived'}:
        status = 'Unclear'
    elif trim['status'] == 'proportionate':
        status = 'Trim Finished'
    elif trim['status'] == 'running':
        status = 'Trim Started'
    elif trim['status'] in {'unknown','waived'}:
        status = 'Unclear'
    else:
        status = {'verified':'Implementation Finished','running':'Implementation Started',
                  'not_started':'Not Started','unknown':'Unclear'}[branch['implementation']['status']]
        if branch['implementation']['reason']:
            notes.append(branch['implementation']['reason'])
    return {'status':status, **counts, 'notes':notes, 'review_sha':branch['tip_sha']}


class Report:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.issues = []

    def safe_path(self, value: str) -> Path | None:
        path = Path(value)
        if not path.is_absolute():
            path = self.root / path
        try:
            resolved = path.resolve()
            resolved.relative_to(self.root / 'plans')
        except (ValueError, OSError):
            return None
        return resolved

    def text(self, path: Path) -> str:
        # Record viewer only; the snapshot never reads linked Markdown evidence.
        safe = self.safe_path(str(path))
        try:
            return safe.read_text(encoding='utf-8') if safe and safe.stat().st_size <= MAX_RECORD_BYTES else ''
        except (OSError, UnicodeError):
            return ''

    def snapshot(self):
        self.issues = []
        records = {kind:{} for kind in ('spec','slice','build','release','deployment')}
        invalid = {}
        for kind,path in record_paths(self.root):
            rel = str(path.relative_to(self.root))
            safe = self.safe_path(rel)
            try:
                if safe is None or safe.stat().st_size > MAX_RECORD_BYTES:
                    raise ValueError('record is unsafe or exceeds the size limit')
                data = load_record(safe)
                errors = validate_record(data,kind,path,self.root)
            except (OSError,ValueError) as exc:
                errors = [str(exc)]
            if errors:
                self.issues.extend(rel + ': ' + error for error in errors)
                if kind == 'slice':
                    invalid[path.parent.name] = errors
                continue
            self.issues.extend(rel+': '+issue for issue in data['unresolved'])
            key = data[kind+'_slug'] if kind in {'spec','slice'} else data[kind+'_id']
            if key in records[kind]:
                self.issues.append(f'Duplicate {kind} identity: {key}')
                records[kind][key] = None
                if kind == 'slice':
                    invalid[key] = ['Duplicate canonical slice identity.']
            else:
                records[kind][key] = {'data':data,'path':rel}
        specs, slices, builds, releases, deployments = (records[k] for k in ('spec','slice','build','release','deployment'))
        rows = []
        # Build branches without slice metadata stay visible as explicit errors.
        slugs = set(slices) | set(invalid)
        for entry in builds.values():
            if entry:
                slugs.update(b['slice_slug'] for b in entry['data']['branches'])
                if entry['data']['schedule']:
                    slugs.update(w['slice_slug'] for w in entry['data']['schedule']['work'])
        for slug in sorted(slugs):
            entry = slices.get(slug)
            data = entry['data'] if entry else None
            notes = list(invalid.get(slug, []))
            if not data:
                notes.append('Missing or invalid canonical slice record.json; no Markdown fallback is used.')
                self.issues.append(slug+': missing or invalid slice JSON')
            current = data['current'] if data else None
            branch = None
            scheduled = None
            build_history, build_links = [], []
            for bid, build in builds.items():
                if not build:
                    continue
                members = [b for b in build['data']['branches'] if b['slice_slug']==slug]
                work = [w for w in build['data']['schedule']['work'] if w['slice_slug']==slug] if build['data']['schedule'] else []
                if members or work:
                    build_links.append(label(bid,build['path'],state=build['data']['state']))
                    build_history.extend({'build':bid, **{key:b[key] for key in ('source','tip_sha','parent','implementation','trim_review','review_progress')}} for b in members)
                    if current and current['build_id']==bid:
                        branch = next((b for b in members if b['source']==current['source']),None)
                        scheduled = next((w for w in work if w['source']==current['source']),None)
            source = current['source'] if current else ''
            tip = current['tip_sha'] if current else ''
            target = branch['parent']['branch'] if branch else ''
            summary = {'status':'Not Started' if data and not current and data['stage'] in {'draft','backlog','to_do'} else 'Unclear',
                       'trim_loops':'Unclear','code_loops':'Unclear','notes':[],'review_sha':''}
            if branch:
                summary = review_summary(branch,tip)
                if tip != branch['tip_sha']:self.issues.append(slug+': current JSON pin differs from build qualification pin')
            elif current:
                build = builds.get(current['build_id'])
                if build and build['data']['schedule'] and scheduled:
                    target = scheduled['parent']['branch'] if scheduled['parent'] else ''
                    summary = review_summary({**scheduled,'tip_sha':scheduled['prepared_sha']},tip)
                    if scheduled['status'] not in {'queued','implementing','prepared'}:
                        summary['notes'].append('Work status has no accepted review record.')
                else:
                    summary['notes'].append('Current build/source does not resolve to a valid JSON branch or scheduled work item.')
                    self.issues.append(slug+': current build/source does not resolve')
            else:
                summary['notes'].append('No current build/source is recorded.')
            spec_links = []
            if data and data['spec_slug']:
                spec = specs.get(data['spec_slug'])
                if spec:
                    spec_links.append(label(data['spec_slug'],spec['path']))
                    owners = {o['slice_slug'] for o in spec['data']['slice_map']['owners']}
                    if slug not in owners:
                        notes.append('Specification JSON ownership map does not list this slice.')
                else:
                    notes.append('Linked specification JSON is missing or invalid.')
            if branch and data and branch['spec_slug'] != data['spec_slug']:
                notes.append('Build and slice JSON disagree about specification ownership.')
            release_links, release_history, prs = [], [], []
            for rid, release in releases.items():
                if not release:
                    continue
                members = [c for c in release['data']['changes'] if c['slice_slug']==slug]
                if not members:
                    continue
                release_links.append(label(rid,release['path'],state=release['data']['state'],lifecycle=release['data']['lifecycle']))
                release_history.extend({'release':rid, **{key:c[key] for key in ('source','head_sha','original_parent','state','pr')}, 'acceptance':release['data']['acceptance']} for c in members)
                for member in members:
                    pr = member['pr']
                    if pr['url']:
                        prs.append({'name':'Slice #'+str(pr['id']),'url':pr['url'],'state':pr['state']})
                pr = release['data']['final_pr']
                if pr['url']:
                    prs.append({'name':'Final #'+str(pr['id']),'url':pr['url'],'state':pr['state']})
            if branch and branch['change_request']['url']:
                pr = branch['change_request']
                prs.append({'name':'Slice #'+str(pr['id']),'url':pr['url'],'state':pr['state']})
            deployed, deployment_history = [], []
            for did, deployment in deployments.items():
                if not deployment:
                    continue
                d = deployment['data']
                members = [m for m in d['included_slices'] if m['slice_slug']==slug]
                item = label(did,deployment['path'],environment=d['environment'],result=d['outcome'],candidate_sha=d['candidate']['sha'])
                if d['outcome']=='verified' and any(m['source']==source and m['tip_sha']==tip for m in members):
                    deployed.append(item)
                elif members:
                    deployment_history.append({**item,'memberships':members})
            handoff = (branch or scheduled or {}).get('operator_handoff')
            handoff_state = handoff['state'] if handoff else 'not_recorded'
            if handoff and handoff['state']=='ready' and handoff['sha']!=tip:
                handoff_state='stale'
                notes.append('Operator handoff describes a different pin; its wording is historical until reconciled.')
            rows.append({'operator_handoff':handoff,'handoff_state':handoff_state,'id':slug,'source':source,'target':target,'stage':data['stage'] if data else 'Unclear',**summary,
                         'notes':notes + (data['notes'] if data else []) + summary['notes'],'tip_sha':tip,
                         'specs':spec_links,'slice':label(slug,entry['path']) if entry else {'name':slug,'url':''},
                         'builds':build_links,'releases':release_links,'prs':list({p['url']:p for p in prs}.values()),
                         'deployments':deployed,'deployment_history':deployment_history,'build_history':build_history,
                         'release_history':release_history,'plan_record':data,'rank':[current['build_id'] if current else '~unassigned',slug]})
        remaining = {r['id']:r for r in rows}
        groups = []
        while remaining:
            seed = min(remaining.values(),key=lambda r:(r['rank'],r['id']))
            component = {seed['id']} if seed['source'] else {r['id'] for r in remaining.values() if not r['source']}
            changed = True
            while changed:
                changed = False
                sources = {remaining[s]['source'] for s in component}
                targets = {remaining[s]['target'] for s in component if remaining[s]['target']}
                for slug,row in remaining.items():
                    if slug not in component and row['source'] and (row['target'] in sources or row['source'] in targets or row['target'] in targets):
                        component.add(slug); changed = True
            items = [remaining[s] for s in component]
            ordered = []
            while items:
                ready = [r for r in items if not any(p['source'] and p['source']==r['target'] for p in items)]
                if not ready:
                    self.issues.append('Branch dependency cycle: '+', '.join(r['id'] for r in items)); ready = items[:]
                for row in sorted(ready,key=lambda r:(r['rank'],r['id'])):
                    ordered.append(row); items.remove(row)
            groups.append({'name':ordered[0]['target'] or 'No branch assigned','rows':ordered})
            for slug in component:
                remaining.pop(slug)
        return {'project':self.root.name,'refreshed_at':datetime.now(timezone.utc).isoformat(),'headers':HEADERS,'columns':COLUMNS,'groups':groups,
                'issues':list(dict.fromkeys(self.issues)),
                'notes':['Stages describe delivery; statuses describe recorded implementation and review progress.',
                         'Only schema-v2 JSON is consumed. Markdown evidence and Git state are not parsed.',
                         'Unclear means missing, invalid or explicitly unknown JSON information; inspect row details.',
                         'Deployment membership and source versions are recorded by the producing skill.']}


PAGE = r'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Slice report</title>
<style>
:root{color-scheme:light;font-family:system-ui,-apple-system,sans-serif;color:#193128;background:#f5f7f4}*{box-sizing:border-box}body{margin:0}header{padding:26px 30px 18px;border-bottom:1px solid #d8e1da;background:#fff}h1{margin:0 0 8px;font-size:26px;letter-spacing:-.6px}.sub{color:#66756c;font-size:13px}.tools{display:flex;gap:10px;flex-wrap:wrap;margin-top:20px;align-items:center}input,button{font:inherit;font-size:13px;border:1px solid #cbd6ce;border-radius:6px;padding:9px 11px;background:#fff;color:inherit}input[type=search]{min-width:230px;flex:1;max-width:420px}.overview{padding:14px 30px;color:#55665b;font-size:13px}.notice{background:#fff4de;color:#745617;border:1px solid #e6d4a8;margin:0 30px 16px;padding:12px;border-radius:6px}.wrap{overflow:auto;margin:0 24px 25px;border:1px solid #d5dfd7;background:#fff;border-radius:8px;max-height:calc(100vh - 215px)}table{border-collapse:separate;border-spacing:0;min-width:1640px;width:100%;font-size:12px}th{position:sticky;top:0;background:#eef3ee;text-align:left;padding:12px 11px;font-size:11px;letter-spacing:.04em;color:#4d6253;z-index:2;border-bottom:1px solid #cdd9cf}td{padding:12px 11px;border-bottom:1px solid #e6ece7;vertical-align:top;max-width:210px;overflow-wrap:anywhere}td.branch{min-width:205px;max-width:245px;font-family:ui-monospace,monospace;font-size:11px}.row:hover{background:#f3f8f2}.row{cursor:pointer}.group td{background:#f1f5f0;color:#53694e;padding:9px 12px;font-size:11px;font-weight:650}.badge{display:inline-block;padding:4px 7px;border-radius:4px;background:#e9eee9;white-space:nowrap}.review,.in_release{background:#fff0cc;color:#7e5912}.merged,.fulfilled,.complete{background:#dceee0;color:#275b34}.in_progress{background:#e1ecfb;color:#28537b}.unclear,.exhausted{background:#f7e2df;color:#913b31}a{color:#265e43;text-decoration:none}a:hover{text-decoration:underline}.links a{display:block;margin-bottom:5px}.context{opacity:.65}.detail td{background:#f9fbf8;padding:22px 25px}.detail-box{max-width:1100px;display:grid;grid-template-columns:1fr 1fr;gap:20px}.detail h3{margin:0 0 8px;font-size:13px}.detail pre{font-family:inherit;white-space:pre-wrap;line-height:1.6;font-size:12px;max-height:370px;overflow:auto;margin:0}.empty{text-align:center;padding:40px;color:#637366}.error{color:#933b31}.count{text-align:center;min-width:70px}.section{margin-top:16px}footer{padding:0 30px 22px;color:#708074;font-size:11px}.compact{max-height:82px;overflow:auto}.detail summary{cursor:pointer;font-weight:600;margin-bottom:8px}
.predecessors{display:flex;align-items:center;gap:7px;font-size:13px;cursor:pointer}.predecessors input{margin:0;accent-color:#245c40}
.filter{position:relative;font-size:13px;min-width:150px}.filter>summary{padding:9px 11px;border:1px solid #cbd6ce;border-radius:6px;background:#fff;cursor:pointer;max-width:240px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.filter[open]>summary{border-color:#245c40}.filter-menu{position:absolute;top:calc(100% + 5px);left:0;background:#fff;border:1px solid #cbd6ce;border-radius:6px;box-shadow:0 8px 24px #19312825;min-width:260px;max-width:min(430px,85vw);z-index:10;padding:8px;max-height:330px;overflow:auto}.filter-menu label{display:flex;gap:9px;align-items:start;padding:7px 5px;cursor:pointer;overflow-wrap:anywhere}.filter-menu input{margin:2px 0 0;accent-color:#245c40}.filter-menu label:hover{background:#f1f5f0}.filter-menu .all{border-bottom:1px solid #e6ece7;font-weight:600;margin-bottom:5px}.filter:focus-within>summary{outline-offset:2px}
.filter-menu input[type=search]{width:100%;min-width:0;max-width:none;margin:0 0 8px;flex:none}.filter-choices{max-height:260px;overflow:auto}.filter-choice[hidden]{display:none}.filter-menu .filter-empty{padding:8px;color:#66756c}.column-actions{display:flex;gap:6px;padding-bottom:8px}.operator-text{min-width:230px;max-width:330px;line-height:1.5}.hold{background:#e7e1f3;color:#594471}table{min-width:0;width:max-content;min-width:100%}</style>
<header><h1>Slice report</h1><div class="sub" id="subtitle">Reading project records…</div><div class="tools"><input id="search" type="search" placeholder="Find branches, slices, specs or builds" aria-label="Search"><details id="stage" class="filter"><summary>Stages</summary><div class="filter-menu"></div></details><details id="status" class="filter"><summary>Statuses</summary><div class="filter-menu"></div></details><details id="build" class="filter"><summary>Builds</summary><div class="filter-menu"></div></details><details id="release" class="filter"><summary>Releases</summary><div class="filter-menu"></div></details><details id="spec" class="filter"><summary>Specs</summary><div class="filter-menu"></div></details><details id="types" class="filter"><summary>Types</summary><div class="filter-menu"></div></details><details id="surfaces" class="filter"><summary>Change surfaces</summary><div class="filter-menu"></div></details><details id="packages" class="filter"><summary>Packages</summary><div class="filter-menu"></div></details><details id="columns" class="filter"><summary>Columns</summary><div class="filter-menu"></div></details><label class="predecessors"><input id="predecessors" type="checkbox">Show predecessors</label></div></header>
<div id="overview" class="overview"></div><details id="issues" class="notice" hidden><summary></summary><div></div></details><div class="wrap"><table><thead><tr id="headers"></tr></thead><tbody id="rows"></tbody></table></div><footer id="foot"></footer>
<script>
const $ = id => document.getElementById(id);
const expanded = new Set(), names = {stage:'stages',status:'statuses',build:'builds',release:'releases',spec:'specs',types:'types',surfaces:'change surfaces',packages:'packages'};
const params = new URLSearchParams(location.search), selected = {};
let report = null, busy = false, visibleColumns = null, columnStorageKey = null;
for (const id of Object.keys(names)) {
  const values = params.getAll(id);
  selected[id] = values.includes('*') ? new Set() : values.length ? new Set(values) : id === 'stage' ? null : new Set();
}
$('search').value = params.get('q') || '';
$('predecessors').checked = params.get('predecessors') === '1';
function el(tag, text, cls) {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  if (cls) node.className = cls;
  return node;
}
function link(item) {
  const url = item.url || '';
  if (!(url.startsWith('/record?') || /^https?:\/\//.test(url))) return el('span', item.name);
  const node = el('a', item.name);
  node.href = url; node.target = '_blank'; node.rel = 'noopener noreferrer';
  node.title = item.state || item.result || '';
  node.onclick = event => event.stopPropagation();
  return node;
}
function links(items) {
  if (!items.length) return el('span', '—');
  const node = el('div', undefined, 'links compact');
  for (const item of items) node.append(link(item));
  return node;
}
function saveFilters() {
  const query = new URLSearchParams();
  for (const id of Object.keys(names)) {
    if (!selected[id].size && id === 'stage') query.append(id, '*');
    for (const value of [...selected[id]].sort()) query.append(id, value);
  }
  if ($('search').value) query.set('q', $('search').value);
  if ($('predecessors').checked) query.set('predecessors', '1');
  history.replaceState(null, '', location.pathname + (query.size ? '?' + query : ''));
}
function choiceMenu(id) {
  const menu = $(id).querySelector('.filter-menu');
  if (!menu.querySelector('input[type=search]')) {
    const search = document.createElement('input'); search.type = 'search';
    search.placeholder = 'Search ' + (names[id] || 'columns'); search.setAttribute('aria-label',search.placeholder);
    const choices = el('div',undefined,'filter-choices'), empty = el('div','No matching options.','filter-empty');
    empty.hidden = true; menu.append(search,choices,empty);
    search.oninput = () => searchChoices(id);
  }
  return menu.querySelector('.filter-choices');
}
function searchChoices(id) {
  const menu = $(id).querySelector('.filter-menu'), query = menu.querySelector('input[type=search]').value.trim().toLowerCase();
  let found = false;
  for (const choice of menu.querySelectorAll('.filter-choice')) {
    choice.hidden = !choice.classList.contains('all') && !choice.textContent.toLowerCase().includes(query);
    if (!choice.hidden && !choice.classList.contains('all')) found = true;
  }
  menu.querySelector('.filter-empty').hidden = found;
}
function options(id, available) {
  const values = [...new Set(available)].sort(), container = $(id);
  if (selected[id] === null) selected[id] = new Set(values.filter(v => !['fulfilled','superseded','done'].includes(v)));
  const summary = container.querySelector('summary'), choices = choiceMenu(id);
  summary.textContent = selected[id].size === 0 ? 'All ' + names[id] : selected[id].size === 1 ? [...selected[id]][0] : selected[id].size + ' ' + names[id];
  summary.title = selected[id].size ? [...selected[id]].join(', ') : 'All ' + names[id];
  const fragment = document.createDocumentFragment();
  for (const value of [null, ...new Set([...values, ...selected[id]])]) {
    const label = el('label',undefined,'filter-choice' + (value === null ? ' all' : ''));
    const input = document.createElement('input'); input.type = 'checkbox';
    input.checked = value === null ? !selected[id].size : selected[id].has(value);
    label.append(input,el('span',value === null ? 'All ' + names[id] : value + (values.includes(value) ? '' : ' (missing from current records)')));
    input.onchange = () => {
      if (value === null) selected[id].clear();
      else if (input.checked) selected[id].add(value);
      else selected[id].delete(value);
      saveFilters(); options(id,available); render();
    };
    fragment.append(label);
  }
  choices.replaceChildren(fragment); searchChoices(id);
}
function configureColumns() {
  const ids = new Set(report.columns.map(c=>c.id));
  if (visibleColumns === null) {
    columnStorageKey = 'slice-report-columns:' + location.origin + ':' + report.project;
    try {
      const saved = JSON.parse(localStorage.getItem(columnStorageKey));
      if (Array.isArray(saved)) visibleColumns = new Set(saved.filter(id=>ids.has(id)));
    } catch (_) { /* Storage may be disabled; preferences still work in this page. */ }
    if (!visibleColumns || !visibleColumns.size) visibleColumns = new Set(report.columns.filter(c=>c.default).map(c=>c.id));
  }
  const choices = choiceMenu('columns'), menu = $('columns').querySelector('.filter-menu');
  if (!menu.querySelector('.column-actions')) {
    const actions = el('div',undefined,'column-actions');
    for (const [title,predicate] of [['Show all',()=>true],['Reset',c=>c.default]]) {
      const button = el('button',title); button.onclick = () => { visibleColumns = new Set(report.columns.filter(predicate).map(c=>c.id)); saveColumns(); configureColumns(); render(); };
      actions.append(button);
    }
    menu.insertBefore(actions,choices);
  }
  const fragment = document.createDocumentFragment();
  for (const column of report.columns) {
    const label = el('label',undefined,'filter-choice'), input = document.createElement('input');
    input.type = 'checkbox'; input.checked = visibleColumns.has(column.id); label.append(input,el('span',column.label));
    input.onchange = () => {
      if (!input.checked && visibleColumns.size===1) { input.checked=true; return; }
      if (input.checked) visibleColumns.add(column.id); else visibleColumns.delete(column.id);
      saveColumns(); render();
    };
    fragment.append(label);
  }
  choices.replaceChildren(fragment); searchChoices('columns');
}
function saveColumns() {
  try { localStorage.setItem(columnStorageKey,JSON.stringify([...visibleColumns])); } catch (_) {}
}
function columns() { return report.columns.filter(column=>visibleColumns.has(column.id)); }
function cellContent(row,id) {
  if (['target','source'].includes(id)) return row[id] || (id==='source' ? 'Not assigned' : 'Not recorded');
  if (['stage','status'].includes(id)) return el('span',row[id],'badge ' + row[id].toLowerCase().replaceAll(' ','_'));
  if (['trim_loops','code_loops'].includes(id)) return String(row[id]);
  if (id==='slice') return link(row.slice);
  if (['specs','builds','releases','prs'].includes(id)) return links(row[id]);
  if (id==='deployments') return links(row.deployments.map(d=>({...d,name:d.environment + ' · ' + d.name.replace(/^staging-rebuild-/, '')})));
  const handoff = row.operator_handoff;
  if (!handoff) return 'Not recorded';
  const value = Array.isArray(handoff[id]) ? handoff[id].join('; ') || 'None' : handoff[id] || 'Not recorded';
  return (row.handoff_state==='ready' ? '' : row.handoff_state[0].toUpperCase()+row.handoff_state.slice(1)+' · ') + value;
}
function detail(row) {
  const tr = el('tr', undefined, 'detail'), td = el('td'); td.colSpan = columns().length;
  const box = el('div', undefined, 'detail-box'), left = el('div'), right = el('div');
  left.append(el('h3','Slice JSON record'), link(row.slice), el('pre', JSON.stringify(row.plan_record,null,2) || 'No valid canonical slice record.'));
  if (row.operator_handoff) left.append(el('h3','Operator handoff · ' + row.handoff_state),el('pre',JSON.stringify(row.operator_handoff,null,2)));
  right.append(el('h3','Source and review evidence'), el('pre', `Source: ${row.tip_sha || 'Not recorded'}\nReview record: ${row.review_sha || 'Not recorded'}\n\n${row.notes.join('\n\n') || 'No evidence conflicts detected.'}`));
  for (const [title, entries] of [['Build history',row.build_history],['Release / PR destination / acceptance',row.release_history],['Other deployment versions and attempts',row.deployment_history]]) {
    if (!entries.length) continue;
    const node = el('details', undefined, 'section');
    node.append(el('summary', title), el('pre', JSON.stringify(entries,null,2))); right.append(node);
  }
  box.append(left,right); td.append(box); tr.append(td); return tr;
}
function includes(id, values) { return !selected[id].size || values.some(value => selected[id].has(value)); }
function render() {
  if (!report) return;
  const wrap = document.querySelector('.wrap'), scrollTop = wrap.scrollTop, scrollLeft = wrap.scrollLeft;
  $('headers').replaceChildren(...columns().map(column=>el('th',column.label)));
  const all = report.groups.flatMap(group => group.rows), query = $('search').value.toLowerCase().trim(), matches = new Set();
  for (const row of all) {
    const text = [row.source,row.target,row.id,...row.specs.map(x=>x.name),...row.builds.map(x=>x.name),...row.releases.map(x=>x.name),...Object.values(row.operator_handoff || {}).filter(v=>typeof v==='string' || Array.isArray(v)).flat()].join(' ').toLowerCase();
    if ((!query || text.includes(query)) && includes('stage',[row.stage]) && includes('status',[row.status]) && includes('build',row.builds.map(x=>x.name)) && includes('release',row.releases.map(x=>x.name)) && includes('spec',row.specs.map(x=>x.name)) && includes('types',row.operator_handoff?.types || []) && includes('surfaces',row.operator_handoff?.change_surfaces || []) && includes('packages',row.operator_handoff?.packages || [])) matches.add(row.id);
  }
  const show = new Set(matches), sources = new Map(all.filter(row=>row.source).map(row=>[row.source,row]));
  if ($('predecessors').checked) {
    for (const row of all.filter(row=>matches.has(row.id))) {
      let parent = sources.get(row.target); const visited = new Set();
      while (parent && !visited.has(parent.id)) {
        visited.add(parent.id); show.add(parent.id); parent = sources.get(parent.target);
      }
    }
  }
  const fragment = document.createDocumentFragment();
  for (const group of report.groups) {
    const rows = group.rows.filter(row=>show.has(row.id));
    if (!rows.length) continue;
    const heading = el('tr', undefined, 'group'), cell = el('td', `${group.name} · ${rows.length} slice${rows.length === 1 ? '' : 's'}`);
    cell.colSpan = columns().length; heading.append(cell); fragment.append(heading);
    for (const row of rows) {
      const tr = el('tr', undefined, 'row' + (matches.has(row.id) ? '' : ' context'));
      tr.dataset.id = row.id; tr.tabIndex = 0;
      tr.setAttribute('aria-expanded', expanded.has(row.id)); tr.setAttribute('aria-label','Details for ' + row.id);
      const add = (content, cls) => { const td = el('td',undefined,cls); td.append(typeof content === 'string' ? el('span',content) : content); tr.append(td); };
      for (const column of columns()) {
        const cls = ['target','source'].includes(column.id) ? 'branch' : ['trim_loops','code_loops'].includes(column.id) ? 'count' : ['problem','solution','test_path','pass_condition'].includes(column.id) ? 'operator-text' : '';
        add(cellContent(row,column.id),cls);
      }
      const toggle = () => { expanded.has(row.id) ? expanded.delete(row.id) : expanded.add(row.id); render(); };
      tr.onclick = toggle;
      tr.onkeydown = event => { if (event.target === tr && ['Enter',' '].includes(event.key)) { event.preventDefault(); toggle(); } };
      fragment.append(tr); if (expanded.has(row.id)) fragment.append(detail(row));
    }
  }
  if (!show.size) {
    const tr = el('tr'), td = el('td','No slices match these filters.','empty'); td.colSpan = columns().length; tr.append(td); fragment.append(tr);
  }
  $('rows').replaceChildren(fragment); wrap.scrollTop = scrollTop; wrap.scrollLeft = scrollLeft;
  $('overview').textContent = `${matches.size} matching slice${matches.size === 1 ? '' : 's'}${show.size > matches.size ? ' · ' + (show.size-matches.size) + ' predecessors shown for context' : ''} · Click a slice for details`;
}
async function refresh() {
  if (busy) return; busy = true;
  try {
    const response = await fetch('/api/report', {cache:'no-store'});
    if (!response.ok) throw Error('Report request failed (' + response.status + ')');
    report = await response.json(); const all = report.groups.flatMap(group=>group.rows);
    $('subtitle').textContent = report.project + ' · Read ' + new Date(report.refreshed_at).toLocaleTimeString() + ' · Refreshes automatically every __REFRESH__ seconds';
    $('subtitle').classList.remove('error');
    configureColumns();
    options('stage',all.map(row=>row.stage)); options('status',all.map(row=>row.status)); options('build',all.flatMap(row=>row.builds.map(x=>x.name)));
    options('release',all.flatMap(row=>row.releases.map(x=>x.name))); options('spec',all.flatMap(row=>row.specs.map(x=>x.name)));
    options('types',all.flatMap(row=>row.operator_handoff?.types || [])); options('surfaces',all.flatMap(row=>row.operator_handoff?.change_surfaces || [])); options('packages',all.flatMap(row=>row.operator_handoff?.packages || []));
    $('issues').hidden = !report.issues.length;
    $('issues').querySelector('summary').textContent = report.issues.length + ' record issue(s)';
    $('issues').querySelector('div').replaceChildren(...report.issues.map(issue=>el('p',issue)));
    $('foot').textContent = report.notes.join(' '); render();
  } catch (error) {
    $('subtitle').textContent = error.message + ' · Showing the last successful snapshot.'; $('subtitle').classList.add('error');
  } finally { busy = false; }
}
$('search').oninput = () => { saveFilters(); render(); };
$('predecessors').onchange = () => { saveFilters(); render(); };
document.addEventListener('click', event => { for (const id of [...Object.keys(names),'columns']) if (!$(id).contains(event.target)) $(id).open = false; });
document.addEventListener('keydown', event => { if (event.key === 'Escape') for (const id of [...Object.keys(names),'columns']) $(id).open = false; });
setInterval(() => { if (!document.hidden) refresh(); }, __REFRESH__ * 1000);
refresh();
</script></html>
'''

def make_server(root: Path, port: int = 8765, refresh: int = 15):
    report = Report(root)
    lock = threading.Lock()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):
            pass

        def send(self, status, body, content_type='text/html; charset=utf-8'):
            raw = body.encode('utf-8')
            try:
                self.send_response(status)
                self.send_header('Content-Type', content_type)
                self.send_header('Content-Length', str(len(raw)))
                self.send_header('Cache-Control', 'no-store')
                self.send_header('X-Content-Type-Options', 'nosniff')
                self.send_header('X-Frame-Options', 'DENY')
                self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'")
                self.end_headers()
                self.wfile.write(raw)
            except (BrokenPipeError, ConnectionResetError):
                pass  # Browser reloads may cancel an in-flight snapshot.

        def do_GET(self):
            if self.headers.get('Host') not in {f'localhost:{self.server.server_port}', f'127.0.0.1:{self.server.server_port}'}:
                return self.send(403, 'Local requests only.', 'text/plain; charset=utf-8')
            url = urlparse(self.path)
            if url.path == '/':
                return self.send(200, PAGE.replace('__REFRESH__', str(refresh)))
            if url.path == '/api/report':
                try:
                    with lock:
                        snapshot = report.snapshot()
                    return self.send(200, json.dumps(snapshot, ensure_ascii=False), 'application/json; charset=utf-8')
                except Exception as exc:
                    return self.send(500, json.dumps({'error': type(exc).__name__ + ': ' + str(exc)}), 'application/json; charset=utf-8')
            if url.path == '/record':
                value = parse_qs(url.query).get('path', [''])[0]
                path = report.safe_path(value)
                if path is None or not path.is_file() or path.suffix.lower() != '.json':
                    return self.send(404, 'Record not found.', 'text/plain; charset=utf-8')
                text = report.text(path)
                if path.stat().st_size > MAX_RECORD_BYTES:
                    return self.send(413, 'Record is too large for this viewer.', 'text/plain; charset=utf-8')
                return self.send(200, '<!doctype html><meta charset="utf-8"><title>' + html.escape(path.name) + '</title><style>body{margin:30px;font:14px system-ui;color:#193128}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:13px ui-monospace;line-height:1.6}a{color:#265e43}</style><a href="/">← Slice report</a><h2>' + html.escape(str(path.relative_to(report.root))) + '</h2><pre>' + html.escape(text) + '</pre>')
            return self.send(404, 'Not found.', 'text/plain; charset=utf-8')

    return ThreadingHTTPServer(('127.0.0.1', port), Handler)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project', type=Path, help='Project containing plans/builds, plans/slices, plans/releases and plans/deployments')
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--refresh', type=int, default=15, help='Browser refresh interval in seconds')
    parser.add_argument('--no-open', action='store_true', help='Leave browser opening to the caller')
    args = parser.parse_args()
    if not (args.project / 'plans').is_dir():
        parser.error('The project must contain a plans directory.')
    if not 0 <= args.port <= 65535 or args.refresh < 1:
        parser.error('Use a port between 0 and 65535 and a positive refresh interval.')
    try:
        server = make_server(args.project, args.port, args.refresh)
    except OSError as exc:
        parser.exit(1, f'Could not start report: {exc}. Try --port with another port.\n')
    url = f'http://127.0.0.1:{server.server_port}/'
    print(f'Slice report: {url}\nProject: {args.project.resolve()}\nRead-only; Ctrl+C stops the server.', flush=True)
    if not args.no_open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
