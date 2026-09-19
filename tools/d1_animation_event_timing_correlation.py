#!/usr/bin/env python3
"""Join exact Crota frame-event pointer structure to clip timing and selector reuse.

This is structural correlation only.  A pointer count is not an event count unless
the pointed-to record schema is later source-closed, and no target-prefix bytes are
interpreted as event opcodes.
"""
from __future__ import annotations
import argparse,collections,json
from pathlib import Path

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--events',type=Path,required=True)
 ap.add_argument('--timing',type=Path,required=True)
 ap.add_argument('--aliases',type=Path,required=True)
 ap.add_argument('--out',type=Path,required=True)
 a=ap.parse_args()
 e=json.loads(a.events.read_text());t=json.loads(a.timing.read_text());al=json.loads(a.aliases.read_text());v=[]
 if e.get('status')!='D1_ANIMATION_FRAME_EVENT_POINTER_CENSUS_EXACT' or e.get('violations'):v.append('event pointer census not exact')
 if t.get('status')!='D1_ANIMATION_STATE_SCALAR_TIMING_RATIO_EXACT' or t.get('violations'):v.append('timing proof not exact')
 if al.get('status')!='D1_ANIMATION_SELECTOR_ALIAS_CENSUS_EXACT' or al.get('violations'):v.append('alias census not exact')
 er={x['clip']:x for x in e.get('rows',[])}
 clip_states=collections.defaultdict(set)
 for g in al.get('selected_sequence_groups',[]):
  for h in g.get('selected_clip_sequence',[]):
   clip_states[h].update(g.get('state_hashes',[]))
 rows=[];count_frames=collections.defaultdict(collections.Counter);bearing=[]
 for h,r in sorted(er.items()):
  pc=int(r['frame_event_pointer_count']);fc=int(r['frame_count'])
  count_frames[pc][fc]+=1
  row={'clip':h,'frame_count':fc,'frame_intervals':max(0,fc-1),
       'frame_event_pointer_count':pc,'nonnull_pointer_count':int(r['nonnull_pointer_count']),
       'unique_nonnull_target_count':int(r['unique_nonnull_target_count']),
       'state_hash_count':len(clip_states.get(h,set())),'state_hashes':sorted(clip_states.get(h,set())),
       'pointer_count_per_frame_interval':None if fc<=1 else pc/(fc-1)}
  rows.append(row)
  if pc>0:bearing.append(row)
 groups=[]
 for pc,fh in sorted(count_frames.items()):
  groups.append({'frame_event_pointer_count':pc,'clip_count':sum(fh.values()),
                 'frame_count_histogram':{str(k):n for k,n in sorted(fh.items())},
                 'frame_count_min':min(fh) if fh else None,'frame_count_max':max(fh) if fh else None})
 # Timing source covers state records; verify all event-census clips are known selector clips.
 selected=set()
 for r in t.get('single_selection_records',[])+t.get('multi_selection_records',[]):
  selected.update(x['clip'] for x in r.get('selected',[]))
 missing=sorted(set(er)-selected)
 if missing:v.append(f'event-census clips absent from timing selector rows: {missing}')
 out={'schema':'d1_animation_event_timing_correlation/v1',
      'status':'D1_ANIMATION_EVENT_TIMING_CORRELATION_EXACT' if rows and not v else 'D1_ANIMATION_EVENT_TIMING_CORRELATION_PARTIAL',
      'clip_count':len(rows),'event_pointer_bearing_clip_count':len(bearing),
      'event_pointer_zero_clip_count':len(rows)-len(bearing),
      'pointer_count_frame_groups':groups,'rows':rows,
      'event_pointer_bearing_clips':bearing,'violations':v,
      'semantic_boundary':{'frame_count':'EXACT','selector_aliases':'EXACT','frame_event_pointer_array':'EXACT','pointer_count_as_event_count':'WITHHELD','event_record_schema':'WITHHELD','event_behavior':'WITHHELD'},
      'policy':'Correlates only exact clip/frame/selector/pointer-array facts. Pointer density is a numerical diagnostic, not an event frequency semantic.'}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'status':out['status'],'clip_count':len(rows),'event_pointer_bearing_clip_count':len(bearing),
                   'pointer_count_frame_groups':groups,
                   'bearing_preview':[(x['clip'],x['frame_count'],x['frame_event_pointer_count'],x['state_hash_count']) for x in bearing[:25]],
                   'violations':v},indent=2))
 return 0 if out['status']=='D1_ANIMATION_EVENT_TIMING_CORRELATION_EXACT' else 2
if __name__=='__main__':raise SystemExit(main())
