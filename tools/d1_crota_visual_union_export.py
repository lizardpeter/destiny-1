#!/usr/bin/env python3
"""Export Crota's complete highest-detail geometry union without duplicate render variants.

The old Crota Blender checkpoint incorrectly took only StagePartOffsets[0:1].  For
8108E5B7 that interval covers only the first material/pass ranges and omits other
disjoint highest-detail index ranges, including the ranges whose retail materials
reference Crota's 2048x2048 colour atlas 8108E951.

This adapter preserves every unique highest-detail (mesh,index range,primitive)
serialized by the model and chooses the first source-ordered material candidate when
the same range is repeated by a later render variant.  Later variants are retained in
the report, never silently discarded.  No geometry range is duplicated in the GLB.

This is deliberately a Blender visual-union adapter, not a claim that all later render
variants are semantically interchangeable.  Native shader closure is used separately
to reproduce material behaviour.
"""
from __future__ import annotations

import argparse,json,sys
from collections import defaultdict
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))

import d1_world_articulated_model_export as base
from d1_entity_model_corpus_export import HIGHEST_LODS,NULLS,norm
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_split_tar_extract import SplitHttpTar
from d1_remote_activity_placements import RemoteCorpus


def visual_union_ranges(model:dict,binding:dict):
    selected=[];mesh_summaries=[]
    bmeshes={int(x['mesh_index']):x for x in binding.get('meshes',[])}
    for mi,mesh in enumerate(model['meshes']):
        bm=bmeshes.get(mi)
        if bm is None: raise ValueError(f'mesh {mi}: no material binding')
        bparts={int(x['part_index']):x for x in bm.get('parts',[])}
        grouped=defaultdict(list)
        for pi,p in enumerate(mesh['parts']):
            if int(p['lod']) not in HIGHEST_LODS: continue
            bp=bparts.get(pi)
            if bp is None: raise ValueError(f'mesh {mi} part {pi}: missing exact material binding')
            sm=bp.get('selected_material') or {};mh=norm(sm.get('hash','FFFFFFFF'))
            if not sm.get('class_matches') or mh in NULLS:
                raise ValueError(f'mesh {mi} part {pi}: selected material unresolved {mh}')
            key=(int(p['index_offset']),int(p['index_count']),int(p['primitive_type']))
            grouped[key].append({
                'part_index':pi,'lod':int(p['lod']),'material':mh,
                'gear_dye_change_color_index':int(p['gear_dye_change_color_index']),
                'variant_shader_index':int(p['variant_shader_index']),
                'flags_d1':int(p['flags_d1']),
            })
        for (off,count,prim),rows in sorted(grouped.items(),key=lambda kv:min(x['part_index'] for x in kv[1])):
            rows=sorted(rows,key=lambda x:x['part_index']);chosen=rows[0]
            selected.append({
                'mesh_index':mi,'index_offset':off,'index_count':count,'primitive_type':prim,
                'material':chosen['material'],'part_indices':[chosen['part_index']],
                'lod_values':[chosen['lod']],
                'dye_indices':[chosen['gear_dye_change_color_index']],
                'parts':[chosen],
                'visual_union_source_first_part':chosen['part_index'],
                'duplicate_render_variants':rows[1:],
                'all_candidate_part_indices':[x['part_index'] for x in rows],
                'all_candidate_materials':[x['material'] for x in rows],
            })
        mesh_summaries.append({
            'mesh_index':mi,'part_count':len(mesh['parts']),
            'highest_detail_part_count':sum(int(p['lod']) in HIGHEST_LODS for p in mesh['parts']),
            'unique_highest_detail_range_count':len(grouped),
        })
    return selected,mesh_summaries


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--material-bindings',type=Path,required=True)
    ap.add_argument('--member-catalog',type=Path,action='append',required=True)
    ap.add_argument('--base-url',required=True);ap.add_argument('--part-count',type=int,default=10)
    ap.add_argument('--runtime',type=Path,required=True);ap.add_argument('--out-dir',type=Path,required=True)
    ap.add_argument('--model',default='8108E5B7');ap.add_argument('--parent',default='8108E4BA')
    a=ap.parse_args();model=norm(a.model);parent=norm(a.parent)
    bd=json.loads(a.material_bindings.read_text())
    if bd.get('status') not in ('D1_REMOTE_ACTIVITY_MODEL_MATERIAL_BINDINGS_COMPLETE','D1_WORLD_ENTITY_MODEL_MATERIAL_BINDINGS_COMPLETE'):
        raise SystemExit(f'bindings not complete: {bd.get("status")}')
    rows=[x for x in bd.get('bindings',[]) if norm(x.get('model'))==model and norm(x.get('parent_resource'))==parent]
    if len(rows)!=1: raise SystemExit(f'expected one {model}/{parent} binding, got {len(rows)}')
    if not rows[0].get('validation_ok') or rows[0].get('violations'): raise SystemExit('binding validation failed')
    cats=load_catalogs(a.member_catalog);arc=SplitHttpTar([f'{a.base_url.rstrip("/")}/packages.tar.{i:03d}' for i in range(1,a.part_count+1)],retries=6,timeout=90)
    c=RemoteCorpus(arc,cats,a.runtime)
    original=base.selected_ranges;base.selected_ranges=visual_union_ranges
    try: rep=base.export_one(c,model,rows[0],a.out_dir)
    finally: base.selected_ranges=original
    rep['status']='D1_CROTA_VISUAL_UNION_EXPORT_COMPLETE'
    rep['selection_policy_visual_union']=(
        'All unique highest-detail serialized index ranges across the model are retained. '
        'When later render variants repeat an identical range, the first source-ordered candidate is exported and every later candidate remains recorded in duplicate_render_variants. '
        'This repairs the old StagePartOffsets[0:1]-only Blender omission without rendering duplicate passes simultaneously.'
    )
    rp=a.out_dir/f'{model}.json';rp.write_text(json.dumps(rep,indent=2)+'\n')
    print('CROTA_VISUAL_UNION','RANGES',rep['geometry_count'],'TRIANGLES',rep['triangle_count'],'MATERIALS',rep['active_materials'])
    for r in rep['ranges']:
        print('RANGE',r['mesh_index'],r['index_offset'],r['index_count'],'PART',r['visual_union_source_first_part'],'MAT',r['material'],'DUPLICATES',[(x['part_index'],x['material']) for x in r['duplicate_render_variants']])
    return 0

if __name__=='__main__':raise SystemExit(main())
