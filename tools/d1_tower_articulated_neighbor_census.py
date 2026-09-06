#!/usr/bin/env python3
"""Find exact source-owned dynamic placements spatially adjacent to selected Tower actors.

This is intended for missing held/nearby prop investigation.  It never assumes that
a nearby placement is attached to the actor.  It simply joins the independently
materialized runtime WorldID placement census to exact SEntity resource/model data
and reports metric distance in the native Tower coordinate space.
"""
from __future__ import annotations
import argparse,json,math,struct,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import d1_tower_map_schema_validate_v5 as v5
from d1_entity_resource_probe import parse_resource

SENTITY='80800734'; ENTITY_RESOURCE='80800861'; NULLS={'00000000','FFFFFFFF'}
def norm(x):return str(x).upper().removeprefix('0X').zfill(8)
def u32(b,o):return struct.unpack_from('<I',b,o)[0]
def i64(b,o):return struct.unpack_from('<q',b,o)[0]
def dyn_resources(b):
    n=u32(b,0x20);rel=i64(b,0x28);hdr=0x28+rel
    if n==0:return []
    if hdr<0 or hdr+0x10>len(b):raise ValueError('SEntity resource header OOB')
    if u32(b,hdr)!=n:raise ValueError('SEntity resource count mismatch')
    data=hdr+0x10;end=data+n*0x0c
    if end>len(b):raise ValueError('SEntity resource array OOB')
    return [f'{u32(b,data+i*0x0c):08X}' for i in range(n)]
def d3(a,b):return math.sqrt(sum((float(a[i])-float(b[i]))**2 for i in range(3)))
def inspect_entity(c,h,cache):
    h=norm(h)
    if h in cache:return cache[h]
    m=c.entry_meta(h);b,src=c.payload(h);out={'entity':h,'meta':m,'source':src,'resources':[],'model_hashes':[]}
    if not m or norm(m.get('reference',''))!=SENTITY or b is None:
        out['error']='SEntity unavailable/wrong class';cache[h]=out;return out
    try:rhs=dyn_resources(b)
    except Exception as ex:out['error']=repr(ex);cache[h]=out;return out
    models=set()
    for rh in rhs:
        rm=c.entry_meta(rh);rb,rsrc=c.payload(rh);rr={'resource':rh,'meta':rm,'source':rsrc}
        if rm and norm(rm.get('reference',''))==ENTITY_RESOURCE and rb is not None:
            try:
                p=parse_resource(rb,'PS4');rr['semantic_role']=p.get('semantic_role');rr['embedded_model_tag_hash']=p.get('embedded_model_tag_hash')
                rr['class_pair']=[norm((p.get('unk10') or {}).get('class_hash','0')),norm((p.get('unk18') or {}).get('class_hash','0'))]
                if p.get('embedded_model_tag_hash') not in (None,'FFFFFFFF','00000000'):
                    models.add(norm(p['embedded_model_tag_hash']))
            except Exception as ex:rr['parse_error']=repr(ex)
        out['resources'].append(rr)
    out['resource_count']=len(rhs);out['model_hashes']=sorted(models);cache[h]=out;return out

def main()->int:
    ap=argparse.ArgumentParser();ap.add_argument('--placements',type=Path,required=True)
    ap.add_argument('--snapshot',type=Path,action='append',required=True);ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('--world-id',action='append',required=True);ap.add_argument('--radius',type=float,default=5.0);ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args();d=json.loads(a.placements.read_text());rows=d.get('unique_world_placements',[]);by={str(x['world_id_hex']).upper():x for x in rows}
    c=v5.v3.base.Corpus([p.resolve() for p in a.snapshot],a.runtime.resolve());cache={};targets=[];viol=[]
    for wid0 in a.world_id:
        wid=wid0.upper();t=by.get(wid)
        if not t:viol.append(f'target WorldID absent:{wid}');continue
        neighbors=[]
        for x in rows:
            dist=d3(t['translation'],x['translation'])
            if dist<=a.radius+1e-9:
                neighbors.append({'distance':dist,'world_id_hex':x['world_id_hex'],'entity_hash':x['entity_hash'],'translation':x['translation'],'rotation':x['rotation'],
                                  'data_resource_class':x.get('data_resource_class'),'serialized_reference_count':x.get('serialized_reference_count'),
                                  'entity_detail':inspect_entity(c,x['entity_hash'],cache)})
        neighbors.sort(key=lambda x:(x['distance'],x['world_id_hex']))
        targets.append({'world_id_hex':wid,'entity_hash':t['entity_hash'],'translation':t['translation'],'rotation':t['rotation'],'radius':a.radius,
                        'neighbor_count_including_self':len(neighbors),'neighbors':neighbors})
    out={'schema_version':1,'status':'D1_TOWER_ARTICULATED_SPATIAL_NEIGHBOR_CENSUS_COMPLETE' if not viol else 'D1_TOWER_ARTICULATED_SPATIAL_NEIGHBOR_CENSUS_PARTIAL',
         'placement_count':len(rows),'target_count':len(targets),'radius':a.radius,'targets':targets,'unique_inspected_entity_count':len(cache),'violations':viol,
         'policy':'Distance is computed from exact source-owned runtime placement translations. Spatial proximity does not prove attachment, ownership, NPC identity, or held-prop semantics. Entity resources/model hashes are exact source joins only.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'status':out['status'],'placement_count':len(rows),'targets':[{'world_id_hex':x['world_id_hex'],'entity_hash':x['entity_hash'],'translation':x['translation'],'neighbors':[(n['distance'],n['world_id_hex'],n['entity_hash'],n['entity_detail'].get('model_hashes')) for n in x['neighbors']]} for x in targets],'violations':viol},indent=2))
    return 0 if not viol else 2
if __name__=='__main__':raise SystemExit(main())
