#!/usr/bin/env python3
"""Exact selector-alias census for D1 animation control state tables.

Groups binary-decoded state records by their exact selected animation sequence.
This exposes control-state reuse without assigning behavioral meanings to state
hashes or clips.
"""
from __future__ import annotations
import argparse, collections, json
from pathlib import Path

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--options',type=Path,required=True)
    ap.add_argument('--timing',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    d=json.loads(a.options.read_text()); t=json.loads(a.timing.read_text())
    if d.get('schema')!='d1_remote_spawned_actor_animation_options/v3': raise SystemExit('options schema')
    if t.get('schema')!='d1_animation_state_scalar_timing_proof/v1': raise SystemExit('timing schema')
    groups=collections.defaultdict(list); record_count=0
    for e in d.get('entities',[]):
      for ctl in e.get('controls',[]):
        for r in (ctl.get('state_table') or {}).get('records',[]):
          record_count+=1
          seq=tuple(x['tag_hash'] for x in (r.get('selected_animations') or []))
          groups[seq].append({
            'entity':e['entity'],'control':ctl['tag_hash'],
            'record_index':int(r['record_index']),'state_hash':r['state_hash'],
            'state_name':r.get('state_name'),'scalar_f32':float(r['scalar_f32']),
            'selection_kind':r['selection_kind'],
            'selection_start':int(r['selection_start']),
            'selection_count':int(r['selection_count']),
            'implicit_null_count':int(r.get('implicit_null_count',0)),
          })
    rows=[]
    for seq,recs in groups.items():
      scalars=sorted({r['scalar_f32'] for r in recs})
      kinds=sorted({r['selection_kind'] for r in recs})
      rows.append({
        'selected_clip_sequence':list(seq),
        'state_record_count':len(recs),
        'state_hashes':[r['state_hash'] for r in recs],
        'scalar_values':scalars,
        'selection_kinds':kinds,
        'records':sorted(recs,key=lambda x:(x['entity'],x['control'],x['record_index'])),
        'same_scalar_for_all_aliases':len(scalars)<=1,
      })
    rows.sort(key=lambda x:(-x['state_record_count'],x['selected_clip_sequence']))
    aliases=[x for x in rows if x['state_record_count']>1]
    divergent=[x for x in aliases if not x['same_scalar_for_all_aliases']]
    clip_to_states=collections.defaultdict(list)
    for seq,recs in groups.items():
      for h in seq:
        clip_to_states[h].extend(r['state_hash'] for r in recs)
    clip_alias_rows=[
      {'clip':h,'state_hash_count':len(set(v)),'state_hashes':sorted(set(v))}
      for h,v in sorted(clip_to_states.items()) if len(set(v))>1
    ]
    out={
      'schema':'d1_animation_selector_alias_census/v1',
      'status':'D1_ANIMATION_SELECTOR_ALIAS_CENSUS_EXACT' if record_count and not divergent else 'D1_ANIMATION_SELECTOR_ALIAS_CENSUS_PARTIAL',
      'state_record_count':record_count,
      'unique_selected_sequence_count':len(rows),
      'alias_sequence_group_count':len(aliases),
      'state_records_in_alias_groups':sum(x['state_record_count'] for x in aliases),
      'maximum_state_records_per_selected_sequence':max((x['state_record_count'] for x in rows),default=0),
      'alias_groups_with_scalar_disagreement_count':len(divergent),
      'clips_selected_by_multiple_state_hashes_count':len(clip_alias_rows),
      'selected_sequence_groups':rows,
      'clip_state_aliases':clip_alias_rows,
      'timing_ratio_frame_intervals_per_scalar_unit':t.get('ratio_frame_intervals_per_scalar_unit'),
      'semantic_boundary':{
        'state_hash_to_selected_clip_reuse':'EXACT',
        'state_hash_behavior_names':'WITHHELD',
        'clip_behavior_names':'WITHHELD',
      },
      'violations':[f"alias scalar disagreement {x['selected_clip_sequence']}" for x in divergent],
      'policy':'State hashes are grouped only by the exact binary-decoded selector sequence. Reuse is structural evidence; no gameplay behavior is inferred from hash adjacency or clip identity.',
    }
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ('status','state_record_count','unique_selected_sequence_count','alias_sequence_group_count','state_records_in_alias_groups','maximum_state_records_per_selected_sequence','alias_groups_with_scalar_disagreement_count','clips_selected_by_multiple_state_hashes_count','violations')},indent=2))
    return 0 if out['status']=='D1_ANIMATION_SELECTOR_ALIAS_CENSUS_EXACT' else 2

if __name__=='__main__': raise SystemExit(main())
