#!/usr/bin/env python3
"""Export exact D1 animation selector-state hashes for source-name resolution.

Input is a source-closed d1_remote_spawned_actor_animation_options/v3 report.
The output keeps every occurrence and a deduplicated hash list.  It does not
attempt FNV preimages or infer behavior from selected clips.
"""
from __future__ import annotations
import argparse, collections, json
from pathlib import Path

def norm(x): return str(x).upper().removeprefix('0X').zfill(8)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('options',type=Path)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--args-out',type=Path)
    a=ap.parse_args()
    d=json.loads(a.options.read_text())
    violations=[]
    if d.get('schema')!='d1_remote_spawned_actor_animation_options/v3':
        violations.append(f"unexpected schema {d.get('schema')!r}")
    if d.get('status')!='D1_ACTIVITY_ACTOR_ANIMATION_OPTIONS_COMPLETE':
        violations.append(f"options status {d.get('status')!r} is not complete")
    if int(d.get('violation_count',0)) or int(d.get('frontier_count',0)):
        violations.append('source options contain violations/frontiers')
    rows=[]
    for e in d.get('entities',[]):
        for ctl in e.get('controls',[]) or []:
            for r in (ctl.get('state_table') or {}).get('records',[]) or []:
                h=norm(r.get('state_hash',''))
                rows.append({
                    'entity':norm(e.get('entity','')),
                    'control':norm(ctl.get('tag_hash','')),
                    'record_index':int(r.get('record_index',-1)),
                    'state_hash':h,
                    'state_name':r.get('state_name'),
                    'scalar_f32':float(r.get('scalar_f32',0.0)),
                    'selected_clip_sequence':[norm(x['tag_hash']) for x in (r.get('selected_animations') or [])],
                })
    if not rows:
        violations.append('no selector state records')
    hashes=sorted({x['state_hash'] for x in rows})
    counts=collections.Counter(x['state_hash'] for x in rows)
    named=[x for x in rows if x.get('state_name')]
    out={
        'schema':'d1_animation_state_hash_export/v1',
        'status':'D1_ANIMATION_STATE_HASH_EXPORT_EXACT' if not violations else 'D1_ANIMATION_STATE_HASH_EXPORT_PARTIAL',
        'state_record_count':len(rows),
        'unique_state_hash_count':len(hashes),
        'unique_state_hashes':hashes,
        'occurrence_histogram':dict(sorted(counts.items())),
        'source_payload_named_record_count':len(named),
        'records':rows,
        'violations':violations,
        'policy':'Exact binary-decoded selector hashes only. No behavior names or hash preimages are inferred.',
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2)+'\n')
    if a.args_out:
        a.args_out.parent.mkdir(parents=True,exist_ok=True)
        a.args_out.write_text(' '.join(f'--string-hash {h}' for h in hashes)+'\n')
    print(json.dumps({k:out[k] for k in ('status','state_record_count','unique_state_hash_count','source_payload_named_record_count','violations')},indent=2))
    return 0 if out['status']=='D1_ANIMATION_STATE_HASH_EXPORT_EXACT' else 2

if __name__=='__main__': raise SystemExit(main())
