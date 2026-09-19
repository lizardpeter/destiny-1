#!/usr/bin/env python3
"""Prove Crota's exact runtime-rig component boundary against selected clips."""
from __future__ import annotations
import argparse,collections,json
from pathlib import Path
def seq(xs):return tuple((str(x['hash']).upper(),int(x['count'])) for x in xs)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--animation-options',type=Path,required=True);ap.add_argument('--runtime-rig',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
 an=json.loads(a.animation_options.read_text());rg=json.loads(a.runtime_rig.read_text());v=[]
 if an.get('status')!='D1_ACTIVITY_ACTOR_ANIMATION_OPTIONS_COMPLETE' or an.get('violation_count') or an.get('frontier_count'):v.append('animation options not exact')
 if rg.get('rig_resource_tag_hash')!='8108E4CB' or int(rg.get('control_count',-1))!=44:v.append('runtime rig identity/dimensions drift')
 target=seq(rg.get('runtime_rig_components',[]))
 expected=(('FFCA31D7',19),('23A671D5',18),('CFFF7271',0),('F0CA84A1',0),('9DE66AEE',7))
 if target!=expected:v.append(f'target component sequence drift {target}')
 t=next((x for x in an.get('targets',[]) if x.get('target_id')=='8108E4BB:8108E4CB:8108E5C0'),None)
 clips=[] if not t else t.get('clips') or []
 if not t:v.append('Crota target absent')
 if len(clips)!=82:v.append(f'Crota selected target clip count {len(clips)} != 82')
 cp=an.get('clips') or {};families=collections.Counter();limits=collections.Counter();stops=collections.Counter();missing=[]
 for x in clips:
  h=x['clip'];r=cp.get(h)
  if not r:missing.append(h);continue
  families[seq(r.get('runtime_components',[]))]+=1;limits[int(x.get('native_control_limit',-1))]+=1
  stops[str((x.get('component_prefix') or {}).get('stop_reason'))]+=1
 if missing:v.append(f'missing clip records {missing}')
 expected_families={
  (('FFCA31D7',19),('23A671D5',18),('CFFF7271',0),('1F98861C',7)):68,
  (('FFCA31D7',19),('23A671D5',18),('11864228',7)):13,
  (('FFCA31D7',19),('23A671D5',18),('5747B350',7)):1,
 }
 if dict(families)!=expected_families:v.append(f'clip component families drift {dict(families)}')
 if limits!={37:82}:v.append(f'control limit drift {dict(limits)}')
 if stops!={'component_hash_mismatch':82}:v.append(f'stop reason drift {dict(stops)}')
 rows=[]
 for s,n in sorted(families.items(),key=lambda x:(-x[1],x[0])):
  i=0
  while i<min(len(target),len(s)) and target[i]==s[i]:i+=1
  rows.append({'clip_count':n,'source_components':[{'hash':h,'count':c} for h,c in s],'first_difference_index':i,
   'target_component_at_difference':None if i>=len(target) else {'hash':target[i][0],'count':target[i][1]},
   'source_component_at_difference':None if i>=len(s) else {'hash':s[i][0],'count':s[i][1]},'shared_positive_control_prefix':37})
 out={'schema':'d1_crota_runtime_component_boundary/v1','status':'D1_CROTA_RUNTIME_COMPONENT_BOUNDARY_EXACT' if not v else 'D1_CROTA_RUNTIME_COMPONENT_BOUNDARY_PARTIAL',
  'target_runtime_rig':'8108E4CB','target_control_count':44,'target_components':[{'hash':h,'count':c} for h,c in target],
  'selected_clip_count':len(clips),'native_control_limit_histogram':{str(k):n for k,n in sorted(limits.items())},
  'stop_reason_histogram':dict(stops),'source_component_family_count':len(rows),'source_component_families':rows,
  'shared_retargetable_control_prefix_count':37,'remaining_target_control_count':7,
  'semantic_boundary':'COMPONENT_HASH_STRUCTURE_ONLY; component names/roles withheld','violations':v}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
 return 0 if out['status']=='D1_CROTA_RUNTIME_COMPONENT_BOUNDARY_EXACT' else 2
if __name__=='__main__':raise SystemExit(main())
