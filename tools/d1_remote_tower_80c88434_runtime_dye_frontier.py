#!/usr/bin/env python3
"""Fail-closed runtime-dye provenance frontier for Tower model 80C88434.

The sole remaining three-NPC pixel-shader family, PS 8087670E, has five visible
stage-0 ranges. Its native GCN uses a runtime ImmConstBuffer api15 and a t4
resource that are not serialized in Materials 808766B2/808766B6. All five ranges
serialize GearDyeChangeColorIndex=0.

This probe searches only exact source-owned objects:
  * the three EntitySKs that own model 80C88434 in Tower data;
  * their directly serialized Resource[] members;
  * model 80C88434 and model-parent EntityResource 80C883FD;
  * materials 808766B2 and 808766B6.

Every aligned u32 that resolves as an actual D1 FileHash is recorded. Direct
SDye_D1 (class 80801AF4 / Charm F41A8080) targets are decoded with the already
source-closed 0xD0 dye schema. This is provenance discovery only: a dye is not
promoted as the live slot-0 binding unless the source graph yields a unique typed
edge. No color/texture similarity is used.
"""
from __future__ import annotations
import argparse, collections, hashlib, json, struct, sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
if str(HERE) not in sys.path: sys.path.insert(0,str(HERE))

from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_activity_placements import RemoteCorpus, package_of
from d1_remote_s_entity_resource_package_find import S_ENTITY_REF, parse_entity_resources
from d1_split_tar_extract import SplitHttpTar
from d1_investment_dye_resolver import DYE_CLASS, parse_dye_payload

ENTITIES=['80C7A5AD','80C7ACC5','80C883CA']
MODEL='80C88434'
PARENT='80C883FD'
MATERIALS=['808766B2','808766B6']
SEEDS=[MODEL,PARENT,*MATERIALS]
NULLS={0,0xFFFFFFFF}

def norm(x): return str(x).upper().removeprefix('0X').zfill(8)

def aligned_edges(c:RemoteCorpus, owner:str, payload:bytes, catalogs:dict)->list[dict]:
    out=[]; seen=set()
    for off in range(0,len(payload)-3,4):
        v=struct.unpack_from('<I',payload,off)[0]
        if v in NULLS or (v>>24)!=0x80: continue
        try: pkg=package_of(f'{v:08X}')
        except Exception: continue
        if pkg not in catalogs: continue
        h=f'{v:08X}'
        # Same value may legitimately occur at multiple fields; preserve offsets.
        meta=c.entry_meta(h)
        if meta is None: continue
        key=(off,h)
        if key in seen: continue
        seen.add(key)
        out.append({'owner':owner,'offset':off,'file_hash':h,'package_id':f'{pkg:04X}',
                    'reference':norm(meta.get('reference','FFFFFFFF')),'type':meta.get('type'),
                    'subtype':meta.get('subtype'),'size':meta.get('file_size')})
    return out

def decode_dye(c:RemoteCorpus,h:str)->dict:
    meta=c.entry_meta(h); b,src=c.payload(h)
    row={'file_hash':h,'source':str(src) if src else None,'metadata':meta}
    if meta is None or b is None:
        row['error']='metadata_or_payload_unavailable'; return row
    if norm(meta.get('reference',''))!=f'{DYE_CLASS:08X}':
        row['error']='not_direct_SDye_D1'; return row
    try:
        row['dye']=parse_dye_payload(b)
        row['payload_sha256']=hashlib.sha256(b).hexdigest()
    except Exception as ex: row['error']=repr(ex)
    return row

def main()->int:
    ap=argparse.ArgumentParser();ap.add_argument('--member-catalog',type=Path,action='append',required=True)
    ap.add_argument('--base-url',required=True);ap.add_argument('--part-count',type=int,default=10)
    ap.add_argument('--runtime',type=Path,required=True);ap.add_argument('--visual-report',type=Path,required=True)
    ap.add_argument('-o','--output',type=Path,required=True);a=ap.parse_args()
    catalogs=load_catalogs(a.member_catalog)
    arc=SplitHttpTar([f'{a.base_url.rstrip("/")}/packages.tar.{i:03d}' for i in range(1,a.part_count+1)],retries=6,timeout=90)
    c=RemoteCorpus(arc,catalogs,a.runtime);viol=[]

    visual=json.loads(a.visual_report.read_text())
    vm=next((x for x in visual.get('models',[]) if norm(x.get('model'))==MODEL),None)
    if visual.get('status')!='D1_WORLD_ARTICULATED_MODEL_SET_COMPLETE' or vm is None:
        viol.append('pinned visual model report missing/not green')
        target_ranges=[]
    else:
        target_ranges=[]
        for r in vm.get('ranges',[]):
            if norm(r.get('material')) not in MATERIALS: continue
            for p in r.get('parts',[]):
                target_ranges.append({'name':r.get('name'),'material':norm(r.get('material')),
                                      'mesh_index':r.get('mesh_index'),'part_index':p.get('part_index'),
                                      'lod':p.get('lod'),'gear_dye_change_color_index':p.get('gear_dye_change_color_index'),
                                      'variant_shader_index':p.get('variant_shader_index')})
        if len(target_ranges)!=5: viol.append(f'expected five target ranges/parts, got {len(target_ranges)}')
        if any(int(x.get('gear_dye_change_color_index',-1))!=0 for x in target_ranges):
            viol.append('target range dye selector is not uniformly zero')

    owners=[];edges=[]
    # Exact fixed seeds.
    for h in SEEDS:
        meta=c.entry_meta(h); b,src=c.payload(h)
        rec={'kind':'fixed_seed','hash':h,'reference':None if meta is None else norm(meta.get('reference','FFFFFFFF')),
             'source':str(src) if src else None,'byte_count':None if b is None else len(b)}
        owners.append(rec)
        if b is None: viol.append(f'{h}: seed payload unavailable')
        else: edges.extend(aligned_edges(c,h,b,catalogs))

    # Three exact EntitySKs and all directly serialized resources.
    entity_rows=[]
    for eh in ENTITIES:
        em=c.entry_meta(eh); eb,esrc=c.payload(eh)
        erow={'entity_hash':eh,'source':str(esrc) if esrc else None,'resources':[]}
        if em is None or eb is None or norm(em.get('reference',''))!=S_ENTITY_REF:
            viol.append(f'{eh}: entity unavailable/class mismatch');entity_rows.append(erow);continue
        edges.extend(aligned_edges(c,eh,eb,catalogs))
        try: rr=parse_entity_resources(eb)
        except Exception as ex:
            viol.append(f'{eh}: resource parse {ex!r}');entity_rows.append(erow);continue
        for q in rr:
            rh=norm(q['resource_hash']);rm=c.entry_meta(rh);rb,rsrc=c.payload(rh)
            x={'resource_index':int(q.get('resource_index',-1)),'resource_hash':rh,
               'reference':None if rm is None else norm(rm.get('reference','FFFFFFFF')),
               'source':str(rsrc) if rsrc else None,'byte_count':None if rb is None else len(rb)}
            erow['resources'].append(x)
            if rb is not None: edges.extend(aligned_edges(c,rh,rb,catalogs))
        erow['resource_count']=len(erow['resources']);entity_rows.append(erow)

    # Deduplicate exact owner+offset+target edges and decode every direct typed dye hit.
    uniq=[];seen=set()
    for e in edges:
        k=(e['owner'],e['offset'],e['file_hash'])
        if k not in seen:seen.add(k);uniq.append(e)
    dye_edges=[e for e in uniq if e['reference']==f'{DYE_CLASS:08X}']
    dye_hashes=sorted({e['file_hash'] for e in dye_edges})
    dyes={h:decode_dye(c,h) for h in dye_hashes}

    # Physical direct-Dye census in the two source packages that own the model/materials.
    package_dyes={}
    for pkg in (0x003B,0x0244):
        if pkg not in catalogs: continue
        try:
            rows=[]
            for e in c.view(pkg).entries:
                if norm(e.get('reference',''))==f'{DYE_CLASS:08X}':
                    rows.append({'tag_hash':norm(e['tag_hash']),'index':e['index'],'size':e['file_size']})
            package_dyes[f'{pkg:04X}']=rows
        except Exception as ex: package_dyes[f'{pkg:04X}']={'error':repr(ex)}

    unique_typed=len(dye_hashes)==1
    out={'schema_version':1,
         'status':'D1_TOWER_80C88434_RUNTIME_DYE_FRONTIER_EXACT' if not viol else 'D1_TOWER_80C88434_RUNTIME_DYE_FRONTIER_VIOLATIONS',
         'model':MODEL,'shader':'8087670E','materials':MATERIALS,'target_ranges':target_ranges,
         'entity_rows':entity_rows,'fixed_seed_owners':owners,
         'resolved_filehash_edge_count':len(uniq),'direct_typed_dye_edge_count':len(dye_edges),
         'direct_typed_dye_hashes':dye_hashes,'direct_typed_dye_edges':dye_edges,'dyes':dyes,
         'source_package_direct_dye_entries':package_dyes,'violations':viol,
         'gates':{'stage_part_slot0_selector_exact':not viol and len(target_ranges)==5 and all(int(x['gear_dye_change_color_index'])==0 for x in target_ranges),
                  'unique_typed_runtime_dye_edge_found':unique_typed,
                  'api15_runtime_binding_closed':False,'t4_runtime_binding_closed':False,
                  'portable_blender_recreation_complete':False},
         'policy':'Only aligned u32 values that resolve to exact catalog FileHashes are considered. SDye_D1 promotion requires direct metadata Reference 80801AF4. A unique direct typed edge is discovery evidence for runtime-dye ownership; API15/t4 binding is not promoted by this probe alone.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'status':out['status'],'target_ranges':target_ranges,'resolved_filehash_edge_count':len(uniq),
                      'direct_typed_dye_edges':dye_edges,'direct_typed_dye_hashes':dye_hashes,
                      'source_package_direct_dye_counts':{k:(len(v) if isinstance(v,list) else v) for k,v in package_dyes.items()},
                      'gates':out['gates'],'violations':viol},indent=2))
    return 0 if not viol else 2
if __name__=='__main__':raise SystemExit(main())
