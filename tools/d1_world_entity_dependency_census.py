#!/usr/bin/env python3
"""Trace source-owned D1 map placements into SEntity resource families.

Input is d1_world_activity_entity_resource_census.py. Each unique placed entity is
validated as D1 SEntity / 80800734 and its +0x20 DynamicArrayUnloaded resource list
(stride 0x0C, D1 S15078080) is materialized. EntityResource / 80800861 children are
then classified with the already source-pinned d1_entity_resource_probe parser.

This is the ownership bridge from Tower placements to model, skeleton, physics,
children and as-yet-unknown entity resources. It does not guess that every placed
entity is an NPC; static props, vendors, scripted objects and characters remain
separate until their resource composition proves the distinction.
"""
from __future__ import annotations
import argparse,json,sys
from collections import Counter
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import d1_tower_map_schema_validate_v5 as v5
import d1_world_activity_entity_table_census as act
from d1_entity_resource_probe import ENTITY_RESOURCE_CLASS,parse_resource

SENTITY='80800734';MODEL_CLASS='80801AB5';RESOURCE_ENTRY_STRIDE=0x0C;NULLS={'00000000','FFFFFFFF'}
PINNED_SOURCE=('MontagueM/Charm@50d36ee1f9ecadad7522504c20b1f3f9c97e30af '
 'Tiger/Schema/Entity/Entity.cs + EntityStructs.cs; project d1_entity_resource_probe.py')

def norm(x):return str(x).upper().removeprefix('0X').zfill(8)
def hx(v):return f'{v:08X}'
def u32(b,o):
 import struct
 return struct.unpack_from('<I',b,o)[0]
def pkgid(h):
 h=norm(h)
 if h in NULLS:return None
 v=int(h,16)-0x80800000
 return None if v<0 else f'{(v>>13)&0x7ff:04x}'

def model_meta(c,h):
 h=norm(h);m=c.entry_meta(h)
 return {'hash':h,'meta':m,'class_matches':bool(m and norm(m.get('reference',''))==MODEL_CLASS),'package_id':pkgid(h)}

def parse_entity(c,h):
 h=norm(h);m=c.entry_meta(h);b,src=c.payload(h)
 r={'entity':h,'package_id':pkgid(h),'meta':m,'payload_source':src,'resources':[],'violations':[]}
 if not m:
  r['violations'].append('entity_unresolved');return r
 if norm(m.get('reference',''))!=SENTITY:
  r['violations'].append('entity_class_mismatch');return r
 if b is None or len(b)<0x30:
  r['violations'].append('entity_payload_unavailable_or_short');return r
 arr=act.dyn(b,0x20,RESOURCE_ENTRY_STRIDE);r['entity_resources_array']=arr
 if not arr['ok']:
  r['violations'].append('entity_resources_array_bounds');return r
 for i in range(arr['count']):
  o=arr['absolute']+i*RESOURCE_ENTRY_STRIDE;rh=hx(u32(b,o));rm=c.entry_meta(rh)
  row={'index':i,'record_offset':o,'resource_hash':rh,'package_id':pkgid(rh),'is_null_sentinel':rh in NULLS,
       'meta':rm,'reference':None if rm is None else norm(rm.get('reference','')),'entity_resource':None}
  if rh not in NULLS and rm and row['reference']==ENTITY_RESOURCE_CLASS:
   rb,rsrc=c.payload(rh);row['payload_source']=rsrc
   if rb is not None:
    try:
     pr=parse_resource(rb);row['entity_resource']=pr
     mh=pr.get('embedded_model_tag_hash')
     if mh:row['embedded_model']=model_meta(c,mh)
     ph=pr.get('embedded_physics_model_tag_hash')
     if ph:row['embedded_physics_model']=model_meta(c,ph)
    except Exception as ex:row['parse_error']=repr(ex)
  r['resources'].append(row)
 r['resource_count']=len(r['resources']);r['validation_ok']=not r['violations'];return r

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--snapshot',type=Path,action='append',required=True)
 ap.add_argument('--runtime',type=Path,required=True);ap.add_argument('--placements',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
 p=json.loads(a.placements.read_text());entities=[norm(x) for x in p.get('unique_entity_hashes',[]) if norm(x) not in NULLS]
 if not entities:raise SystemExit('placement census contains no entity hashes')
 c=v5.v3.base.Corpus([x.resolve() for x in a.snapshot],a.runtime.resolve());rows=[parse_entity(c,h) for h in entities]
 roles=Counter();refs=Counter();models=Counter();physics_models=Counter();resource_hashes=Counter();viol=[];unresolved_entities=[];unresolved_resources=[];unresolved_models=[]
 for e in rows:
  if e.get('meta') is None:unresolved_entities.append(e['entity'])
  viol.extend(f"{e['entity']}:{x}" for x in e['violations'])
  for r in e['resources']:
   if r['is_null_sentinel']:continue
   resource_hashes[r['resource_hash']]+=1;refs[r.get('reference') or 'MISSING']+=1
   if r.get('meta') is None:unresolved_resources.append(r['resource_hash'])
   er=r.get('entity_resource')
   if er:
    roles[er.get('semantic_role','other_or_unknown')]+=1
    mh=er.get('embedded_model_tag_hash')
    if mh:
     models[mh]+=1
     if not r.get('embedded_model',{}).get('meta'):unresolved_models.append(mh)
    ph=er.get('embedded_physics_model_tag_hash')
    if ph:
     physics_models[ph]+=1
     if not r.get('embedded_physics_model',{}).get('meta'):unresolved_models.append(ph)
 unresolved_all=sorted(set(unresolved_entities+unresolved_resources+unresolved_models))
 out={'schema_version':2,'status':'D1_WORLD_ENTITY_DEPENDENCY_CENSUS_COMPLETE' if not viol and not unresolved_all else 'D1_WORLD_ENTITY_DEPENDENCY_CENSUS_PARTIAL',
      'pinned_source':PINNED_SOURCE,'placed_unique_entity_count':len(entities),'parsed_entity_count':sum(x.get('validation_ok',False) for x in rows),
      'unresolved_entity_count':len(set(unresolved_entities)),'unresolved_entity_hashes':sorted(set(unresolved_entities)),
      'entity_resource_reference_count':sum(resource_hashes.values()),'unique_entity_resource_hash_count':len(resource_hashes),
      'unresolved_resource_hash_count':len(set(unresolved_resources)),'unresolved_resource_hashes':sorted(set(unresolved_resources)),
      'resource_reference_class_counts':dict(refs),'entity_resource_role_counts':dict(roles),
      'unique_embedded_model_count':len(models),'embedded_model_reference_counts':dict(models),'unique_embedded_models':sorted(models),
      'unique_embedded_physics_model_count':len(physics_models),'embedded_physics_model_reference_counts':dict(physics_models),'unique_embedded_physics_models':sorted(physics_models),
      'unresolved_dependency_hashes':unresolved_all,'unresolved_dependency_package_ids':dict(Counter(pkgid(x) for x in unresolved_all if pkgid(x))),
      'entities':rows,'violations':viol,
      'policy':'Only source-owned placed entity hashes are traversed. Resource roles come from D1 EntityResource discriminators; other resources remain unknown. Missing hashes are emitted as package-ID expansion targets, never guessed.'}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
 keys=('status','placed_unique_entity_count','parsed_entity_count','unresolved_entity_count','entity_resource_reference_count','unique_entity_resource_hash_count',
       'unresolved_resource_hash_count','resource_reference_class_counts','entity_resource_role_counts','unique_embedded_model_count','unique_embedded_physics_model_count',
       'unresolved_dependency_package_ids','violations')
 print(json.dumps({k:out[k] for k in keys},indent=2));return 0 if out['status'].endswith('_COMPLETE') else 2
if __name__=='__main__':raise SystemExit(main())
