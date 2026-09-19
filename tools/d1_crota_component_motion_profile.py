#!/usr/bin/env python3
"""Profile Crota animation runtime-component families by exact retargeted motion.

Inputs:
* exact selector/runtime-component family census;
* exact native decode -> retarget -> local-space motion census;
* exact node-hash order with pinned-lineage display names.

The family IDs remain neutral structural labels. This tool measures frame-count
population, source/target dimension facts, local dynamic-track counts and per-node
motion incidence. It does not assign behavior (idle/walk/attack/etc.) to a family.
"""
from __future__ import annotations
import argparse,collections,json
from pathlib import Path

KINDS=(
 ('any','dynamic_any_track_indices'),
 ('scale','dynamic_scale_track_indices'),
 ('rotation','dynamic_rotation_track_indices'),
 ('translation','dynamic_translation_track_indices'),
)

def hist(vals):
 c=collections.Counter(int(x) for x in vals)
 return {str(k):c[k] for k in sorted(c)}

def rng(vals):
 vals=[float(x) for x in vals]
 return [min(vals),max(vals)] if vals else None

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--component-state',type=Path,required=True)
 ap.add_argument('--motion',type=Path,required=True)
 ap.add_argument('--lineage-names',type=Path,required=True)
 ap.add_argument('--out',type=Path,required=True)
 a=ap.parse_args()
 cs=json.loads(a.component_state.read_text())
 mo=json.loads(a.motion.read_text())
 nm=json.loads(a.lineage_names.read_text())
 v=[]
 if cs.get('status')!='D1_CROTA_ANIMATION_COMPONENT_STATE_CENSUS_EXACT' or cs.get('violations'):
  v.append('component-state census not exact')
 if mo.get('status')!='D1_ANIMATION_MOTION_CENSUS_EXACT' or mo.get('missing_motion_summary_count') or mo.get('missing_motion_summaries'):
  v.append('motion census not exact')
 if nm.get('status')!='D1_SKELETON_LINEAGE_NAME_MAP_EXACT_HASH_JOIN' or nm.get('violations'):
  v.append('lineage-name join not exact')
 names=nm.get('rows') or []
 if len(names)!=50:v.append(f'lineage node count {len(names)} != 50')
 byclip=collections.defaultdict(list)
 for r in mo.get('rows',[]):byclip[str(r.get('clip')).upper()].append(r)
 families=[]
 accounted=set()
 for fam in cs.get('families',[]):
  fi=int(fam['family_index']);members=[str(x).upper() for x in fam.get('selected_clips',[])]
  rows=[];missing=[]
  for h in members:
   rr=byclip.get(h,[])
   if len(rr)!=1:
    missing.append({'clip':h,'motion_row_count':len(rr)})
   else:
    rows.append(rr[0]);accounted.add(h)
  if missing:v.append(f'family {fi}: missing/duplicate motion rows {missing}')
  frame_counts=[int(r['frame_count']) for r in rows]
  dyn={k:[] for k,_ in KINDS}
  node_counts={k:collections.Counter() for k,_ in KINDS}
  bone0_end=[];bone0_peak=[]
  exact_dims=0
  for r in rows:
   if int(r.get('target_node_count',-1))!=50:
    v.append(f"family {fi}:{r.get('clip')}: target node count {r.get('target_node_count')} != 50")
   exact_dims+=bool(r.get('source_dimensions_exact'))
   ms=r.get('local_motion_summary') or {}
   if int(ms.get('track_count',-1))!=50:
    v.append(f"family {fi}:{r.get('clip')}: motion track count {ms.get('track_count')} != 50")
   for kind,key in KINDS:
    inds=[int(x) for x in ms.get(key,[]) or []]
    dyn[kind].append(len(inds))
    for i in inds:
     if 0<=i<len(names):node_counts[kind][i]+=1
     else:v.append(f"family {fi}:{r.get('clip')}:{kind}: node {i} OOB")
   b0=ms.get('bone0_translation_syntax') or {}
   if b0.get('translation_end_displacement') is not None:
    bone0_end.append(float(b0['translation_end_displacement']))
   if b0.get('translation_peak_displacement_from_start') is not None:
    bone0_peak.append(float(b0['translation_peak_displacement_from_start']))
  node_rows=[]
  for i,n in enumerate(names):
   node_rows.append({
    'index':i,'node_hash':n.get('node_hash'),'bungie_name':n.get('bungie_name'),
    'name_evidence':n.get('name_evidence'),
    'dynamic_any_clip_instances':node_counts['any'][i],
    'dynamic_scale_clip_instances':node_counts['scale'][i],
    'dynamic_rotation_clip_instances':node_counts['rotation'][i],
    'dynamic_translation_clip_instances':node_counts['translation'][i],
   })
  families.append({
   'family_index':fi,
   'runtime_components':fam.get('runtime_components'),
   'selected_clip_count':len(members),
   'motion_row_count':len(rows),
   'selected_clips':members,
   'frame_count_histogram':hist(frame_counts),
   'frame_count_range':rng(frame_counts),
   'source_dimension_exact_count':exact_dims,
   'native_retarget_required_count':len(rows)-exact_dims,
   'dynamic_any_track_count_histogram':hist(dyn['any']),
   'dynamic_scale_track_count_histogram':hist(dyn['scale']),
   'dynamic_rotation_track_count_histogram':hist(dyn['rotation']),
   'dynamic_translation_track_count_histogram':hist(dyn['translation']),
   'bone0_translation_end_displacement_range':rng(bone0_end),
   'bone0_translation_peak_displacement_range':rng(bone0_peak),
   'nodes_dynamic_in_any_family_clip':sum(x['dynamic_any_clip_instances']>0 for x in node_rows),
   'nodes_dynamic_translation_in_any_family_clip':sum(x['dynamic_translation_clip_instances']>0 for x in node_rows),
   'nodes_dynamic_rotation_in_any_family_clip':sum(x['dynamic_rotation_clip_instances']>0 for x in node_rows),
   'nodes_dynamic_scale_in_any_family_clip':sum(x['dynamic_scale_clip_instances']>0 for x in node_rows),
   'node_motion_incidence':node_rows,
  })
 expected={str(x).upper() for f in cs.get('families',[]) for x in f.get('selected_clips',[])}
 extras=sorted(set(byclip)-expected)
 missing=sorted(expected-accounted)
 if extras:v.append(f'motion census contains clips outside component families: {extras}')
 if missing:v.append(f'component-family clips without exact motion row: {missing}')
 out={
  'schema':'d1_crota_component_motion_profile/v1',
  'status':'D1_CROTA_COMPONENT_MOTION_PROFILE_EXACT' if len(families)==3 and not v else 'D1_CROTA_COMPONENT_MOTION_PROFILE_PARTIAL',
  'control':cs.get('control'),
  'component_family_count':len(families),
  'selected_clip_count':len(expected),
  'families':families,
  'violations':v,
  'semantic_boundary':{
   'component_family':'EXACT_SERIALIZED_RUNTIME_COMPONENT_SIGNATURE',
   'frame_counts':'EXACT_RETAIL_CLIP_HEADER',
   'motion_variation':'EXACT_PINNED_NATIVE_RETARGET_LOCAL_SPACE_NUMERICAL_CENSUS',
   'node_hash':'EXACT_RETAIL_ENTITYSKELETON',
   'bungie_name':'PINNED_COMMUNITY_PARSER_LINEAGE_TABLE',
   'bone0_root_motion_semantic':'WITHHELD',
   'component_family_behavior':'WITHHELD',
   'clip_behavior':'WITHHELD',
  },
  'policy':'Profiles compare neutral serialized runtime-component families using exact numerical clip and retargeted-motion facts. Differences are not converted into gameplay or animation-state names.',
 }
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({
  'status':out['status'],
  'families':[{
   'family_index':x['family_index'],'clips':x['selected_clip_count'],
   'frame_histogram':x['frame_count_histogram'],
   'dynamic_any_histogram':x['dynamic_any_track_count_histogram'],
   'nodes_dynamic_any':x['nodes_dynamic_in_any_family_clip'],
   'bone0_end_range':x['bone0_translation_end_displacement_range'],
  } for x in families],
  'violations':v,
 },indent=2))
 return 0 if out['status']=='D1_CROTA_COMPONENT_MOTION_PROFILE_EXACT' else 2

if __name__=='__main__':raise SystemExit(main())
