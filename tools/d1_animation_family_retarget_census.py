#!/usr/bin/env python3
"""Exact family-level census of D1 actor animation retarget structure."""
from __future__ import annotations
import argparse,collections,json
from pathlib import Path

def hist(xs):
 c=collections.Counter(xs);return {str(k):v for k,v in sorted(c.items(),key=lambda x:str(x[0]))}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('input',type=Path);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
 d=json.loads(a.input.read_text());v=[]
 if d.get('schema')!='d1_remote_spawned_actor_animation_options/v3':v.append('expected v3 animation options')
 if d.get('status')!='D1_ACTIVITY_ACTOR_ANIMATION_OPTIONS_COMPLETE' or d.get('violation_count') or d.get('frontier_count'):v.append('source animation options not complete')
 fam={(f.get('skeleton'),f.get('runtime_rig'),tuple(f.get('controls') or [])):f for f in d.get('families',[])}
 rows=[];by_control=collections.defaultdict(list)
 for t in d.get('targets',[]):
  clips=t.get('clips') or []
  if not clips:v.append(f"{t.get('target_id')}: empty clip population");continue
  dims=[(int(x['source_node_count']),int(x['source_rig_control_count'])) for x in clips]
  limits=[int(x.get('native_control_limit',-1)) for x in clips]
  stops=[str((x.get('component_prefix') or {}).get('stop_reason')) for x in clips]
  frames=[int(x['frame_count']) for x in clips];exact=sum(bool(x.get('source_dimensions_exact')) for x in clips)
  control=t['control'];f=fam.get((t['skeleton'],t['runtime_rig'],(control,)))
  row={'target_id':t['target_id'],'skeleton':t['skeleton'],'runtime_rig':t['runtime_rig'],'control':control,
       'entities':[] if not f else f.get('entities',[]),'entity_count':0 if not f else int(f.get('entity_count',0)),
       'target_node_count':int(t['skeleton_node_count']),'target_rig_control_count':int(t['runtime_rig_control_count']),
       'selected_clip_count':len(clips),'exact_dimension_clip_count':exact,'native_retarget_required_clip_count':len(clips)-exact,
       'source_dimension_histogram':hist(dims),'native_control_limit_histogram':hist(limits),
       'component_prefix_stop_reason_histogram':hist(stops),'frame_count_histogram':hist(frames),
       'frame_count_min':min(frames),'frame_count_max':max(frames),'selected_clip_hashes':[x['clip'] for x in clips]}
  rows.append(row);by_control[control].append(row)
 controls=[]
 for control,rs in sorted(by_control.items()):
  sets=[set(x['selected_clip_hashes']) for x in rs];inter=set.intersection(*sets) if sets else set();union=set.union(*sets) if sets else set()
  controls.append({'control':control,'target_count':len(rs),'targets':[x['target_id'] for x in rs],
   'skeletons':sorted({x['skeleton'] for x in rs}),'runtime_rigs':sorted({x['runtime_rig'] for x in rs}),
   'selected_clip_counts':[x['selected_clip_count'] for x in rs],'shared_clip_intersection_count':len(inter),'clip_union_count':len(union),
   'all_targets_use_identical_clip_set':all(s==sets[0] for s in sets[1:]) if sets else True})
 crota=next((x for x in rows if x['target_id']=='8108E4BB:8108E4CB:8108E5C0'),None)
 if crota is None:v.append('Crota exact animation target absent')
 else:
  if crota['selected_clip_count']!=82:v.append(f"Crota clip count drift {crota['selected_clip_count']}")
  if (crota['target_node_count'],crota['target_rig_control_count'])!=(50,44):v.append('Crota target dimensions drift')
  if (crota['exact_dimension_clip_count'],crota['native_retarget_required_clip_count'])!=(0,82):v.append('Crota retarget population drift')
  if crota['native_control_limit_histogram']!={'37':82}:v.append(f"Crota control-limit drift {crota['native_control_limit_histogram']}")
  if crota['component_prefix_stop_reason_histogram']!={'component_hash_mismatch':82}:v.append(f"Crota component boundary drift {crota['component_prefix_stop_reason_histogram']}")
 out={'schema':'d1_animation_family_retarget_census/v1','status':'D1_ANIMATION_FAMILY_RETARGET_CENSUS_EXACT' if rows and not v else 'D1_ANIMATION_FAMILY_RETARGET_CENSUS_PARTIAL',
      'target_count':len(rows),'control_count':len(controls),'targets':rows,'control_reuse':controls,'crota_target':crota,
      'total_clip_target_instances':sum(x['selected_clip_count'] for x in rows),
      'exact_dimension_clip_target_instances':sum(x['exact_dimension_clip_count'] for x in rows),
      'native_retarget_required_clip_target_instances':sum(x['native_retarget_required_clip_count'] for x in rows),
      'violations':v,
      'policy':'Dimension-exact requires node/control dimensions and runtime-component sequence to agree. Native-retarget classification comes from the already-executed pinned retail path; behavioral clip names remain unassigned.'}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'status':out['status'],'targets':out['target_count'],'total':out['total_clip_target_instances'],'exact':out['exact_dimension_clip_target_instances'],'retarget':out['native_retarget_required_clip_target_instances'],'reused_controls':[x for x in controls if x['target_count']>1],'crota':crota,'violations':v},indent=2))
 return 0 if out['status']=='D1_ANIMATION_FAMILY_RETARGET_CENSUS_EXACT' else 2
if __name__=='__main__':raise SystemExit(main())
