#!/usr/bin/env python3
"""Census exact D1 animation frame-event pointer structures.

Consumes animation-options v3 output after the native parser has preserved the
header's frame-event Vec_Pointer array.  This tool clusters exact pointer counts and
bounded target prefixes for selector-selected clips only.

It does not claim a frame-event record size, event opcode, event name, or behavioral
meaning.
"""
from __future__ import annotations
import argparse,collections,hashlib,json
from pathlib import Path

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--options',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
 d=json.loads(a.options.read_text());violations=[];rows=[]
 if d.get('schema')!='d1_remote_spawned_actor_animation_options/v3':violations.append('options schema not v3')
 if d.get('status')!='D1_ACTIVITY_ACTOR_ANIMATION_OPTIONS_COMPLETE':violations.append('options not source-closed complete')
 selected=[str(x).upper() for x in d.get('unique_selector_selected_clip_hashes',[])]
 clips={str(k).upper():v for k,v in (d.get('clips') or {}).items()}
 hist=collections.Counter();prefixes=collections.Counter();nonnull=0;pointer_total=0
 for h in selected:
  cp=clips.get(h)
  if not cp:
   violations.append(f'{h}: selected clip metadata missing');continue
  ev=cp.get('frame_event_pointers')
  if not ev:
   violations.append(f'{h}: frame-event pointer summary missing');continue
  if ev.get('semantic_boundary')!='POINTER_STRUCTURE_AND_BOUNDED_PREFIX_ONLY_EVENT_SCHEMA_WITHHELD':
   violations.append(f'{h}: frame-event semantic boundary drift')
  count=int(ev.get('count',-1));ptrs=ev.get('pointers') or []
  if count!=len(ptrs):violations.append(f'{h}: pointer count/list mismatch {count}/{len(ptrs)}')
  hist[count]+=1;pointer_total+=max(count,0)
  if count>0:nonnull+=1
  prow=[]
  for p in ptrs:
   hx=str(p.get('target_prefix_hex') or '')
   bc=int(p.get('target_prefix_byte_count',0))
   if len(hx)!=bc*2:violations.append(f"{h}: pointer {p.get('index')} prefix length mismatch")
   sha=hashlib.sha256(bytes.fromhex(hx)).hexdigest()
   if p.get('target_offset') is not None:prefixes[(bc,sha,hx)]+=1
   prow.append({
    'index':int(p['index']),'pointer_offset':int(p['pointer_offset']),
    'raw_relative_u64':int(p['raw_relative_u64']),'raw_relative_hex':p['raw_relative_hex'],
    'target_offset':p.get('target_offset'),'target_prefix_byte_count':bc,
    'target_prefix_sha256':sha,'target_prefix_hex':hx,
   })
  rows.append({'clip':h,'frame_count':int(cp['frame_count']),'clip_size':int(cp['size']),
               'frame_event_pointer_count':count,'nonnull_pointer_count':int(ev.get('nonnull_count',0)),
               'unique_nonnull_target_count':int(ev.get('unique_nonnull_target_count',0)),
               'pointer_array_offset':int(ev.get('array_offset',0)),'pointers':prow})
 groups=[{'target_prefix_byte_count':bc,'target_prefix_sha256':sha,'target_prefix_hex':hx,'occurrence_count':n}
         for (bc,sha,hx),n in sorted(prefixes.items(),key=lambda x:(-x[1],x[0][1]))]
 out={'schema':'d1_animation_frame_event_pointer_census/v1',
      'status':'D1_ANIMATION_FRAME_EVENT_POINTER_CENSUS_EXACT' if len(rows)==len(selected) and not violations else 'D1_ANIMATION_FRAME_EVENT_POINTER_CENSUS_PARTIAL',
      'selected_unique_clip_count':len(selected),'resolved_clip_count':len(rows),
      'clips_with_nonzero_frame_event_pointer_count':nonnull,'total_frame_event_pointer_count':pointer_total,
      'frame_event_pointer_count_histogram':{str(k):v for k,v in sorted(hist.items())},
      'unique_nonnull_target_prefix_count':len(groups),'target_prefix_groups':groups,'rows':rows,'violations':violations,
      'semantic_boundary':{'pointer_array':'EXACT','relative_pointer_words':'EXACT','target_offsets':'EXACT','bounded_target_prefix':'EXACT_BYTES','event_record_schema':'WITHHELD','event_names':'WITHHELD','event_timing_semantics':'WITHHELD'},
      'policy':'The parser comment identifies an array of relative pointers to frame events, but the pointed-to D1 record schema is not source-closed. This census therefore preserves pointer structure and bounded bytes only; no record size or event meaning is inferred.'}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'status':out['status'],'selected_unique_clip_count':len(selected),'clips_with_nonzero_events':nonnull,
                   'pointer_count_histogram':out['frame_event_pointer_count_histogram'],
                   'unique_target_prefixes':len(groups),'top_prefix_groups':groups[:12],'violations':violations},indent=2))
 return 0 if out['status']=='D1_ANIMATION_FRAME_EVENT_POINTER_CENSUS_EXACT' else 2

if __name__=='__main__':raise SystemExit(main())
