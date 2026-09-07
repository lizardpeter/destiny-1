#!/usr/bin/env python3
"""Build an exact model/material export plan for arbitrary source-owned D1 SEntities.

Unlike the spawned-actor adapter, this tool does not require a runtime rig. It is for
rigid or minimally articulated auxiliary entities such as carried props. For every
requested SEntity it reopens the exact Resource[] list, requires one source-owned
entity_model EntityResource, takes its embedded s_entity_model and owning parent, and
enumerates literal vertex/index header+backing dependencies from the retail model.

The output deliberately implements the existing D1_WORLD_ARTICULATED_ENTITY_PLAN
interface only so the exact parent-material resolver/model exporter can be reused.
No placement or animation semantics are invented.
"""
from __future__ import annotations
import argparse,collections,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_split_tar_extract import SplitHttpTar
from d1_remote_activity_placements import RemoteCorpus
from d1_remote_s_entity_resource_package_find import parse_entity_resources,S_ENTITY_REF
from d1_entity_resource_probe import parse_resource,ENTITY_RESOURCE_CLASS
from d1_entity_model_probe import parse_model
from d1_investment_arrangement_probe import filehash_pkg_index
NULLS={'00000000','FFFFFFFF'}
def norm(x):return str(x).upper().removeprefix('0X').zfill(8)
def pid(h):
 h=norm(h)
 if h in NULLS:return None
 return f'{filehash_pkg_index(int(h,16))[0]:04x}'

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--entity',action='append',required=True);ap.add_argument('--member-catalog',type=Path,action='append',required=True);ap.add_argument('--base-url',required=True);ap.add_argument('--part-count',type=int,default=10);ap.add_argument('--runtime',type=Path,required=True);ap.add_argument('-o','--output',type=Path,required=True);a=ap.parse_args()
 cats=load_catalogs(a.member_catalog);arc=SplitHttpTar([f"{a.base_url.rstrip('/')}/packages.tar.{i:03d}" for i in range(1,a.part_count+1)],retries=6,timeout=90);c=RemoteCorpus(arc,cats,a.runtime)
 candidates=[];models={};required=set();viol=[]
 for raw in a.entity:
  h=norm(raw)
  try:
   em=c.entry_meta(h);eb,esrc=c.payload(h)
   if em is None or eb is None or norm(em.get('reference'))!=S_ENTITY_REF:raise ValueError(f'{h}: not exact s_entity')
   resources=[]
   for rr in parse_entity_resources(eb):
    rh=norm(rr['resource_hash']);rm=c.entry_meta(rh);rb,rsrc=c.payload(rh)
    if rm is None or rb is None or norm(rm.get('reference'))!=ENTITY_RESOURCE_CLASS:continue
    pr=parse_resource(rb,'PS4');resources.append({'resource_hash':rh,'semantic_role':pr.get('semantic_role'),'embedded_model':norm(pr.get('embedded_model_tag_hash','FFFFFFFF')),'pair':[(pr.get('unk10') or {}).get('class_hash'),(pr.get('unk18') or {}).get('class_hash')]})
   owned=[x for x in resources if x['semantic_role']=='entity_model' and x['embedded_model'] not in NULLS]
   if len(owned)!=1:raise ValueError(f'{h}: expected one entity_model resource, got {owned}')
   parent=owned[0]['resource_hash'];model=owned[0]['embedded_model'];sk=[x['resource_hash'] for x in resources if x['semantic_role']=='entity_skeleton']
   cand={'entity':h,'models':[model],'model_parent_resources':[parent],'skeleton_resources':sk,'runtime_rig_resources':[],'bone_counts':[],'source_package_id':pid(h),'location_status':'withheld_external_source_owned_placement'};candidates.append(cand)
   for q in (h,parent,model,*sk):
    p=pid(q)
    if p:required.add(p)
   if model not in models:
    mm=c.entry_meta(model);mb,msrc=c.payload(model)
    if mm is None or mb is None or norm(mm.get('reference'))!='80801AB5':raise ValueError(f'{model}: unavailable model')
    pm=parse_model(mb,'PS4');mr={'model':model,'source':msrc,'mesh_count':len(pm.get('meshes',[])),'streams':[]}
    for mi,m in enumerate(pm.get('meshes',[])):
     for role in ('vertices1','vertices2','indices'):
      hh=norm(m.get(role,'FFFFFFFF'))
      if hh in NULLS:continue
      hm=c.entry_meta(hh)
      if hm is None:raise ValueError(f'{model} mesh {mi} {role} header {hh} unresolved')
      bk=norm(hm.get('reference','FFFFFFFF'))
      if bk in NULLS or c.entry_meta(bk) is None:raise ValueError(f'{model} mesh {mi} {role} backing {bk} unresolved')
      mr['streams'].append({'mesh_index':mi,'role':role,'header':hh,'header_package_id':pid(hh),'backing':bk,'backing_package_id':pid(bk)})
      for q in (hh,bk):
       p=pid(q)
       if p:required.add(p)
     for part in m.get('parts',[]):
      p=pid(part.get('material','FFFFFFFF'))
      if p:required.add(p)
    models[model]=mr
  except Exception as ex:viol.append(f'{h}:{ex!r}')
 fams=[]
 for i,(model,ents) in enumerate(sorted(collections.defaultdict(list,{m:[x['entity'] for x in candidates if x['models'][0]==m] for m in models}).items()),1):
  sample=next(x for x in candidates if x['models'][0]==model);fams.append({'family_id':f'OWNED_VIS_{i:02d}','model':model,'model_parent_resource':sample['model_parent_resources'][0],'entity_count':len(ents),'entities':ents,'skeleton_resources':sample['skeleton_resources'],'runtime_rig_resources':[],'bone_counts':[]})
 out={'schema':'d1_remote_owned_entity_visual_plan/v1','status':'D1_WORLD_ARTICULATED_ENTITY_PLAN_COMPLETE' if not viol else 'D1_WORLD_ARTICULATED_ENTITY_PLAN_PARTIAL','semantic_scope':'D1_SOURCE_OWNED_AUXILIARY_ENTITY_VISUAL_PLAN','candidate_count':len(candidates),'family_count':len(fams),'unique_model_count':len(models),'candidates':candidates,'families':fams,'model_dependencies':models,'required_initial_package_ids':sorted(required),'violations':viol,'policy':'WORLD_ARTICULATED status is an exporter interface adapter only. Model and parent ownership come only from each exact SEntity Resource[] entity_model edge. Stream dependencies are literal model FileHashes. No location, attachment socket, animation, or semantic identity is inferred.'}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n');print('STATUS',out['status'],'ENTITIES',len(candidates),'MODELS',len(models),'REQUIRED',out['required_initial_package_ids'],'VIOLATIONS',viol);return 0 if not viol else 2
if __name__=='__main__':raise SystemExit(main())
