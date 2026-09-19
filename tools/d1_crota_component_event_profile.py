#!/usr/bin/env python3
"""Profile Crota runtime-component families by exact frame-event pointer structure.

Joins neutral component-family membership to the source-closed selected-clip
frame-event pointer census. Pointer arrays, pointer words, target offsets and the
bounded target-prefix bytes are exact. A pointer count is not promoted to an event
count and target bytes are not decoded into event semantics here.
"""
from __future__ import annotations
import argparse,collections,json
from pathlib import Path

def hist(vals):
 c=collections.Counter(int(x) for x in vals)
 return {str(k):c[k] for k in sorted(c)}

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--component-state',type=Path,required=True)
 ap.add_argument('--events',type=Path,required=True)
 ap.add_argument('--out',type=Path,required=True)
 a=ap.parse_args()
 cs=json.loads(a.component_state.read_text());ev=json.loads(a.events.read_text());v=[]
 if cs.get('status')!='D1_CROTA_ANIMATION_COMPONENT_STATE_CENSUS_EXACT' or cs.get('violations'):
  v.append('component-state census not exact')
 if ev.get('status')!='D1_ANIMATION_FRAME_EVENT_POINTER_CENSUS_EXACT' or ev.get('violations'):
  v.append('frame-event pointer census not exact')
 byclip={str(x['clip']).upper():x for x in ev.get('rows',[])}
 families=[];accounted=set()
 for fam in cs.get('families',[]):
  fi=int(fam['family_index']);members=[str(x).upper() for x in fam.get('selected_clips',[])]
  rows=[];prefixes=collections.Counter();targets=collections.Counter()
  for h in members:
   r=byclip.get(h)
   if r is None:
    v.append(f'family {fi}: event row missing for {h}');continue
   rows.append(r);accounted.add(h)
   for p in r.get('pointers',[]) or []:
    if p.get('target_offset') is None:continue
    sha=str(p.get('target_prefix_sha256') or '')
    bc=int(p.get('target_prefix_byte_count',0))
    prefixes[(bc,sha)]+=1
    targets[(h,int(p['target_offset']))]+=1
  pc=[int(r['frame_event_pointer_count']) for r in rows]
  np=[int(r['nonnull_pointer_count']) for r in rows]
  ut=[int(r['unique_nonnull_target_count']) for r in rows]
  families.append({
   'family_index':fi,
   'runtime_components':fam.get('runtime_components'),
   'selected_clip_count':len(members),
   'resolved_event_row_count':len(rows),
   'clips_with_nonzero_pointer_array_count':sum(x>0 for x in pc),
   'clips_with_zero_pointer_array_count':sum(x==0 for x in pc),
   'frame_event_pointer_count_histogram':hist(pc),
   'nonnull_pointer_count_histogram':hist(np),
   'unique_nonnull_target_count_histogram':hist(ut),
   'total_pointer_array_entries':sum(pc),
   'total_nonnull_pointer_entries':sum(np),
   'exact_prefix_group_count':len(prefixes),
   'top_exact_prefix_groups':[
    {'target_prefix_byte_count':bc,'target_prefix_sha256':sha,'occurrence_count':n}
    for (bc,sha),n in sorted(prefixes.items(),key=lambda kv:(-kv[1],kv[0]))[:24]
   ],
   'clip_rows':[{
    'clip':str(r['clip']).upper(),'frame_count':int(r['frame_count']),
    'frame_event_pointer_count':int(r['frame_event_pointer_count']),
    'nonnull_pointer_count':int(r['nonnull_pointer_count']),
    'unique_nonnull_target_count':int(r['unique_nonnull_target_count']),
   } for r in rows],
  })
 expected={str(x).upper() for f in cs.get('families',[]) for x in f.get('selected_clips',[])}
 extra=sorted(set(byclip)-expected);missing=sorted(expected-accounted)
 if extra:v.append(f'event census contains selected clips outside component families: {extra}')
 if missing:v.append(f'component-family clips without event row: {missing}')
 out={
  'schema':'d1_crota_component_event_profile/v1',
  'status':'D1_CROTA_COMPONENT_EVENT_PROFILE_EXACT' if len(families)==3 and not v else 'D1_CROTA_COMPONENT_EVENT_PROFILE_PARTIAL',
  'control':cs.get('control'),'component_family_count':len(families),
  'selected_clip_count':len(expected),'families':families,'violations':v,
  'semantic_boundary':{
   'component_family':'EXACT_SERIALIZED_RUNTIME_COMPONENT_SIGNATURE',
   'pointer_array':'EXACT_RETAIL_STRUCTURE',
   'relative_pointer_words':'EXACT',
   'target_offsets':'EXACT',
   'bounded_target_prefix':'EXACT_BYTES',
   'pointer_count_as_event_count':'WITHHELD',
   'event_record_schema':'WITHHELD',
   'event_behavior':'WITHHELD',
   'component_family_behavior':'WITHHELD',
  },
  'policy':'This is a structural join only. Family differences in pointer arrays or target-prefix reuse are not interpreted as event frequency or gameplay behavior.',
 }
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'status':out['status'],'families':[{
  'family_index':x['family_index'],'clips':x['selected_clip_count'],
  'bearing':x['clips_with_nonzero_pointer_array_count'],
  'pointer_histogram':x['frame_event_pointer_count_histogram'],
  'prefix_groups':x['exact_prefix_group_count'],
 } for x in families],'violations':v},indent=2))
 return 0 if out['status']=='D1_CROTA_COMPONENT_EVENT_PROFILE_EXACT' else 2

if __name__=='__main__':raise SystemExit(main())
