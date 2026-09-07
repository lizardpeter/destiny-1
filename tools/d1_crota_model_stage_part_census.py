#!/usr/bin/env python3
"""Exact Crota 8108E5B7 stage/LOD/material census.

This is diagnostic-only. It reopens the retail PS4 model, reproduces Charm's
StagePartOffsets -> GroupIndex construction, and joins each part to the already
source-closed owning-parent material binding. It does not choose a Blender-visible
stage or collapse duplicate render variants.
"""
from __future__ import annotations
import argparse, collections, json, sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))

from d1_entity_model_probe import parse_model, D1_ENTITY_MODEL_CLASS
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_activity_placements import RemoteCorpus
from d1_split_tar_extract import SplitHttpTar

MODEL='8108E5B7'
PARENT='8108E4BA'
LOD_NAMES={0:'MainGeom0',1:'GripStock0',2:'Stickers0',3:'InternalGeom0',4:'LowPolyGeom1',7:'LowPolyGeom2',8:'GripStockScope2',9:'LowPolyGeom3',10:'Detail0'}
HIGHEST={0,1,2,3,10}


def norm(x): return str(x).upper().removeprefix('0X').zfill(8)

def binding_for(doc):
    rows=[x for x in doc.get('bindings',[]) if norm(x.get('model'))==MODEL and norm(x.get('parent_resource'))==PARENT]
    if len(rows)!=1: raise ValueError(f'expected one {MODEL}/{PARENT} binding, got {len(rows)}')
    r=rows[0]
    if not r.get('validation_ok') or r.get('violations'): raise ValueError('owning-parent binding not closed')
    return r

def group_map(offsets, part_count):
    # Exact Charm EntityModel.GenerateParts construction.
    bounds=sorted(set(int(x) for x in offsets))
    out={}
    intervals=[]
    for gi in range(max(0,len(bounds)-1)):
        a,b=bounds[gi],bounds[gi+1]
        intervals.append({'group_index':gi,'start':a,'end':b})
        for pi in range(a,b):
            if 0 <= pi < part_count: out[pi]=gi
    return bounds,intervals,out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--material-bindings',type=Path,required=True)
    ap.add_argument('--member-catalog',type=Path,action='append',required=True)
    ap.add_argument('--base-url',required=True); ap.add_argument('--part-count',type=int,default=10)
    ap.add_argument('--runtime',type=Path,required=True); ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args()

    bdoc=json.loads(a.material_bindings.read_text()); bind=binding_for(bdoc)
    bmeshes={int(x['mesh_index']):x for x in bind['meshes']}
    cats=load_catalogs(a.member_catalog)
    arc=SplitHttpTar([f"{a.base_url.rstrip('/')}/packages.tar.{i:03d}" for i in range(1,a.part_count+1)],retries=6,timeout=90)
    c=RemoteCorpus(arc,cats,a.runtime)
    meta=c.entry_meta(MODEL); payload,source=c.payload(MODEL)
    if meta is None or payload is None or norm(meta.get('reference'))!=D1_ENTITY_MODEL_CLASS:
        raise ValueError('exact Crota model payload unavailable')
    model=parse_model(payload,'PS4')
    if len(model['meshes'])!=3: raise ValueError('Crota mesh-count drift')

    meshes=[]; allparts=[]; families=collections.defaultdict(list)
    for mi,mesh in enumerate(model['meshes']):
        bm=bmeshes.get(mi)
        if bm is None: raise ValueError(f'mesh {mi}: owning-parent binding absent')
        bp={int(x['part_index']):x for x in bm['parts']}
        offsets=[int(x) for x in mesh['stage_part_offsets_source_derived']]
        bounds,intervals,gmap=group_map(offsets,len(mesh['parts']))
        rows=[]
        for pi,p in enumerate(mesh['parts']):
            br=bp.get(pi)
            if br is None: raise ValueError(f'mesh {mi} part {pi}: binding absent')
            sm=br.get('selected_material') or {}
            mat=norm(sm.get('hash','FFFFFFFF')) if sm else 'FFFFFFFF'
            row={
                'mesh_index':mi,'part_index':pi,'group_index':gmap.get(pi),
                'lod':int(p['lod']),'lod_name':LOD_NAMES.get(int(p['lod']),f'Unknown{int(p["lod"])}'),
                'is_highest':int(p['lod']) in HIGHEST,
                'index_offset':int(p['index_offset']),'index_count':int(p['index_count']),'primitive_type':int(p['primitive_type']),
                'variant_shader_index':int(p['variant_shader_index']),'inline_material':norm(p['material']),
                'selected_material':mat,'selection':br.get('selection'),'renderable':bool(br.get('renderable')),
                'flags_d1':int(p['flags_d1']),'external_identifier':int(p['external_identifier']),
                'gear_dye_change_color_index':int(p['gear_dye_change_color_index']),
                'unk10':int(p['unk10']),'unk14':int(p['unk14']),'unk20':int(p['unk20']),'lod_run':int(p['lod_run']),
            }
            rows.append(row);allparts.append(row)
            families[(mi,row['index_offset'],row['index_count'],row['primitive_type'])].append(row)
        meshes.append({'mesh_index':mi,'part_count':len(rows),'stage_part_offsets_raw':offsets,'stage_bounds_unique_sorted':bounds,'stage_intervals':intervals,'parts':rows})

    fam=[]
    for key,rows in sorted(families.items()):
        fam.append({
            'mesh_index':key[0],'index_offset':key[1],'index_count':key[2],'primitive_type':key[3],
            'part_indices':[x['part_index'] for x in rows],
            'groups':sorted({x['group_index'] for x in rows if x['group_index'] is not None}),
            'lods':sorted({x['lod'] for x in rows}),'lod_names':sorted({x['lod_name'] for x in rows}),
            'materials':[x['selected_material'] for x in rows],
            'variants':[x['variant_shader_index'] for x in rows],
            'flags':[x['flags_d1'] for x in rows],
            'highest_parts':[x['part_index'] for x in rows if x['is_highest']],
        })
    stage_summary=[]
    for mi,m in enumerate(meshes):
        for iv in m['stage_intervals']:
            rows=[x for x in m['parts'] if x['group_index']==iv['group_index']]
            stage_summary.append({
                'mesh_index':mi,**iv,'part_count':len(rows),
                'part_indices':[x['part_index'] for x in rows],
                'lods':sorted({x['lod'] for x in rows}),
                'lod_names':sorted({x['lod_name'] for x in rows}),
                'highest_part_indices':[x['part_index'] for x in rows if x['is_highest']],
                'materials':sorted({x['selected_material'] for x in rows if x['renderable']}),
                'variant_shader_indices':sorted({x['variant_shader_index'] for x in rows}),
                'flags_d1':sorted({x['flags_d1'] for x in rows}),
            })
    out={
        'schema':'d1_crota_model_stage_part_census/v1','status':'D1_CROTA_MODEL_STAGE_PART_CENSUS_COMPLETE',
        'model':MODEL,'parent_resource':PARENT,'source':source,'model_payload_bytes':len(payload),
        'mesh_count':len(meshes),'part_count':len(allparts),'highest_part_count':sum(x['is_highest'] for x in allparts),
        'lod_enum':LOD_NAMES,'highest_lods':sorted(HIGHEST),'meshes':meshes,'stage_summary':stage_summary,'geometry_families':fam,
        'policy':'Stage GroupIndex reproduces pinned Charm GenerateParts exactly from unique sorted StagePartOffsets. LOD names reproduce pinned Charm ELodCategory. No stage/material candidate is promoted as visible by this census.'
    }
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n')
    print('STATUS',out['status'],'PARTS',out['part_count'],'HIGHEST',out['highest_part_count'])
    for m in meshes: print('MESH',m['mesh_index'],'PARTS',m['part_count'],'RAW_OFFSETS',m['stage_part_offsets_raw'],'BOUNDS',m['stage_bounds_unique_sorted'])
    for s in stage_summary: print('STAGE',s['mesh_index'],s['group_index'],f"[{s['start']},{s['end']})",'PARTS',s['part_indices'],'LODS',s['lod_names'],'MATS',s['materials'],'VARIANTS',s['variant_shader_indices'],'FLAGS',s['flags_d1'])
    for f in fam: print('FAMILY',f['mesh_index'],f['index_offset'],f['index_count'],'PARTS',f['part_indices'],'GROUPS',f['groups'],'LODS',f['lod_names'],'MATS',f['materials'],'VARS',f['variants'],'FLAGS',f['flags'])
    return 0
if __name__=='__main__': raise SystemExit(main())
