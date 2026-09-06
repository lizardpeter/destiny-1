#!/usr/bin/env python3
"""Resolve the exact D1 Guardian gear stage-0, highest-LOD draw set.

Bungie's archived D1 Spasm renderer explicitly sets `stagesToRender = [0]` and
iterates stage parts in the half-open interval:

    [stage_part_offsets[0], stage_part_offsets[1])

It then keeps only LOD names containing "0".  Charm independently defines the
corresponding D1 highest-detail enum set as {0,1,2,3,10}.

For those exact parts this tool also mirrors Charm's D1 material resolution:
VariantShaderIndex == -1 uses the inline material; otherwise material variant 0
is selected through the owning EntityResource ExternalMaterialsMap/bank.
"""
from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))

from d1_entity_model_export import byhash
from d1_entity_model_probe import D1_ENTITY_MODEL_CLASS, parse_model
from d1_guardian_stage_part_material_resolve import HIGHEST_LODS, parent_for_model, resolve_material, norm_hash, pkg_id
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_investment_parent_probe import RemoteLogicalPackage
from d1_remote_model_export import MultiPackageReader
from d1_split_tar_extract import SplitHttpTar


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--visual-context',type=Path,required=True)
    ap.add_argument('--model',action='append',required=True)
    ap.add_argument('--member-catalog',type=Path,action='append',required=True)
    ap.add_argument('--base-url',required=True)
    ap.add_argument('--part-count',type=int,default=10)
    ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args()

    visual=json.loads(a.visual_context.read_text())
    if visual.get('schema')!='d1_guardian_visual_context_probe/v1' or visual.get('errors'):
        raise ValueError('visual context is not a clean v1 report')
    wanted=[norm_hash(x) for x in a.model]
    catalogs=load_catalogs(a.member_catalog)
    missing=sorted({pkg_id(x) for x in wanted}-set(catalogs))
    if missing: raise SystemExit('missing model catalogs: '+', '.join(f'{x:04X}' for x in missing))
    base=a.base_url.rstrip('/')
    arc=SplitHttpTar([f'{base}/packages.tar.{i:03d}' for i in range(1,a.part_count+1)],retries=6,timeout=90)
    views={pkg:RemoteLogicalPackage(arc,fam,a.runtime) for pkg,fam in sorted(catalogs.items())}
    multi=MultiPackageReader(views); hmap=byhash(multi)

    mesh_rows=[]; selected=[]; errors=[]
    for tag in wanted:
        parent=parent_for_model(visual,tag)
        me=hmap.get(tag)
        if me is None or me['reference'].upper()!=D1_ENTITY_MODEL_CLASS:
            raise ValueError(f'{tag}: exact D1 model unavailable')
        model=parse_model(multi.entry(me['index']),'PS4')
        for mi,mesh in enumerate(model['meshes']):
            offsets=[int(x) for x in (mesh.get('stage_part_offsets_source_derived') or [])]
            if len(offsets)<2:
                raise ValueError(f'{tag} mesh {mi}: no stage-0 boundaries')
            start,end=offsets[0],offsets[1]
            if start<0 or end<start or end>len(mesh['parts']):
                raise ValueError(f'{tag} mesh {mi}: invalid stage-0 [{start},{end}) for {len(mesh["parts"])} parts; offsets={offsets}')
            msel=[]
            for pi in range(start,end):
                p=mesh['parts'][pi]
                highest=int(p['lod']) in HIGHEST_LODS
                mat=resolve_material(p,parent)
                row={
                    'model_tag':tag,'mesh_index':mi,'part_index':pi,
                    'stage_index':0,'stage0_start':start,'stage0_end_exclusive':end,
                    'index_offset':int(p['index_offset']),'index_count':int(p['index_count']),
                    'primitive_type':int(p['primitive_type']),'lod':int(p['lod']),
                    'highest_detail':highest,
                    'gear_dye_change_color_index':int(p['gear_dye_change_color_index']),
                    'flags_d1':int(p['flags_d1']),'external_identifier':int(p['external_identifier']),
                    **mat,
                }
                if mat.get('error'):
                    errors.append(row)
                if highest:
                    selected.append(row); msel.append(row)
            mesh_rows.append({
                'model_tag':tag,'mesh_index':mi,'part_count':len(mesh['parts']),
                'stage_part_offsets':offsets,'stage0_start':start,'stage0_end_exclusive':end,
                'stage0_part_count':end-start,'stage0_highest_detail_part_count':len(msel),
                'selected_part_indices':[x['part_index'] for x in msel],
            })

    ranges=collections.defaultdict(list)
    for x in selected:
        k=(x['model_tag'],x['mesh_index'],x['index_offset'],x['index_count'],x['primitive_type'])
        ranges[k].append(x)
    range_rows=[]
    for k,rows in sorted(ranges.items()):
        mats=sorted({x['active_material_hash'] for x in rows if x.get('active_material_hash')})
        dyes=sorted({x['gear_dye_change_color_index'] for x in rows})
        range_rows.append({
            'model_tag':k[0],'mesh_index':k[1],'index_offset':k[2],'index_count':k[3],'primitive_type':k[4],
            'selected_part_count':len(rows),'part_indices':[x['part_index'] for x in rows],
            'gear_dye_change_color_indices':dyes,'active_material_hashes':mats,
            'active_material_count':len(mats),'parts':rows,
        })

    rep={
        'schema':'d1_guardian_stage0_material_resolve/v1',
        'model_count':len(wanted),'mesh_count':len(mesh_rows),
        'selected_part_count':len(selected),'selected_range_count':len(range_rows),
        'multi_part_selected_range_count':sum(x['selected_part_count']>1 for x in range_rows),
        'multi_material_selected_range_count':sum(x['active_material_count']>1 for x in range_rows),
        'unresolved_material_count':len(errors),
        'highest_detail_lods':sorted(HIGHEST_LODS),
        'active_material_package_ids':sorted({f'{pkg_id(x["active_material_hash"]):04X}' for x in selected if x.get('active_material_hash')}),
        'meshes':mesh_rows,'ranges':range_rows,'parts':selected,'errors':errors,
        'policy':(
            'Stage selection is the archived Bungie D1 gear renderer contract: stage 0 only, half-open stage_part_offsets[0:1]. LOD selection is Charm ELod.IsHighestLevel. Active materials use exact D1 inline/external-material resolution. No duplicate pass is retained unless it independently survives all three rules.'
        ),
    }
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(rep,indent=2)+'\n')
    print('MODELS',rep['model_count'],'MESHES',rep['mesh_count'],'SELECTED_PARTS',rep['selected_part_count'],'RANGES',rep['selected_range_count'])
    print('MULTI_PART',rep['multi_part_selected_range_count'],'MULTI_MATERIAL',rep['multi_material_selected_range_count'],'ERRORS',len(errors))
    print('ACTIVE_PACKAGES',rep['active_material_package_ids'])
    for r in range_rows:
        print('RANGE',r['model_tag'],r['mesh_index'],r['index_offset'],r['index_count'],'parts',r['part_indices'],'dye',r['gear_dye_change_color_indices'],'material',r['active_material_hashes'])
    if errors: raise SystemExit(f'{len(errors)} material resolution error(s)')
    return 0


if __name__=='__main__':
    raise SystemExit(main())
