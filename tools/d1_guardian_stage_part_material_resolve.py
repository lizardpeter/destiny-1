#!/usr/bin/env python3
"""Resolve D1 Guardian stage-part materials exactly as the ROI entity path does.

This closes an important distinction that a mesh-wide material census loses.
For every serialized D1 stage part we preserve:
  * the exact index range and primitive type;
  * the exact LOD category;
  * the inline Material FileHash;
  * VariantShaderIndex;
  * GearDyeChangeColorIndex;
  * the owning EntityResource's ExternalMaterialsMap/ExternalMaterials.

Source-backed D1 rules mirrored from Charm:
  highest-detail LOD categories = {0,1,2,3,10}
  VariantShaderIndex == -1 -> active material is part.Material
  otherwise -> ExternalMaterials[
      ExternalMaterialsMap[VariantShaderIndex].MaterialStartIndex + 0]

No range is forced to one material.  If several highest-detail stage parts target
the same serialized range, all are reported as separate render-pass candidates.
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
from d1_investment_arrangement_probe import filehash_pkg_index
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_investment_parent_probe import RemoteLogicalPackage
from d1_remote_model_export import MultiPackageReader
from d1_split_tar_extract import SplitHttpTar

HIGHEST_LODS={0,1,2,3,10}


def norm_hash(v:str)->str:
    v=str(v).upper().removeprefix('0X').zfill(8)
    if len(v)!=8: raise ValueError(v)
    int(v,16); return v


def pkg_id(tag:str)->int:
    return filehash_pkg_index(int(tag,16))[0]


def parent_for_model(visual:dict, tag:str)->dict:
    rows=[m for m in visual.get('models',[]) if str(m.get('tag_hash') or '').upper()==tag]
    if len(rows)!=1:
        raise ValueError(f'{tag}: expected exactly one visual-context model row, got {len(rows)}')
    row=rows[0]
    parent=row.get('render_parent') or {}
    if parent.get('embedded_model_tag_hash') != tag:
        raise ValueError(f'{tag}: render-parent/model mismatch {parent.get("embedded_model_tag_hash")}')
    if parent.get('external_materials_map',{}).get('error'):
        raise ValueError(f'{tag}: external-material map error')
    if parent.get('external_materials',{}).get('error'):
        raise ValueError(f'{tag}: external-material bank error')
    return parent


def resolve_material(part:dict,parent:dict)->dict:
    inline=norm_hash(part['material'])
    variant=int(part['variant_shader_index'])
    if variant == -1:
        return {
            'mode':'inline_material',
            'inline_material_hash':inline,
            'variant_shader_index':variant,
            'active_material_hash':inline,
        }
    maps=parent.get('external_materials_map_entries') or []
    mats=[norm_hash(x) for x in (parent.get('external_material_tag_hashes') or [])]
    if variant < 0 or variant >= len(maps):
        return {
            'mode':'unresolved_external_variant',
            'inline_material_hash':inline,
            'variant_shader_index':variant,
            'error':f'variant index {variant} outside external map count {len(maps)}',
        }
    mr=maps[variant]
    count=int(mr['material_count']); start=int(mr['material_start_index'])
    if count <= 0:
        return {
            'mode':'unresolved_external_variant',
            'inline_material_hash':inline,
            'variant_shader_index':variant,
            'external_map_entry':mr,
            'error':f'variant has non-positive material_count {count}',
        }
    if start < 0 or start >= len(mats):
        return {
            'mode':'unresolved_external_variant',
            'inline_material_hash':inline,
            'variant_shader_index':variant,
            'external_map_entry':mr,
            'error':f'material_start_index {start} outside material bank count {len(mats)}',
        }
    return {
        'mode':'external_material_variant0',
        'inline_material_hash':inline,
        'variant_shader_index':variant,
        'external_map_entry':mr,
        'external_material_bank_index':start,
        'external_material_count':count,
        'active_material_hash':mats[start],
    }


def group_index_map(offsets:list[int], part_count:int)->dict[int,int]:
    # Exact Charm construction: unique StagePartOffsets, sorted, then each
    # adjacent pair assigns part indices in [boundary_i,boundary_{i+1}).
    bounds=sorted(set(int(x) for x in offsets))
    out={}
    for gi in range(max(0,len(bounds)-1)):
        a,b=bounds[gi],bounds[gi+1]
        for pi in range(a,b):
            if 0 <= pi < part_count:
                out[pi]=gi
    return out


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
    if visual.get('schema')!='d1_guardian_visual_context_probe/v1':
        raise ValueError('unexpected visual-context schema')
    if visual.get('errors'):
        raise ValueError('visual context has errors')
    wanted=[norm_hash(x) for x in a.model]
    if len(set(wanted))!=len(wanted): raise ValueError('duplicate --model')

    catalogs=load_catalogs(a.member_catalog)
    missing=sorted({pkg_id(x) for x in wanted}-set(catalogs))
    if missing: raise SystemExit('missing model package catalogs: '+', '.join(f'{x:04X}' for x in missing))
    base=a.base_url.rstrip('/')
    arc=SplitHttpTar([f'{base}/packages.tar.{i:03d}' for i in range(1,a.part_count+1)],retries=6,timeout=90)
    views={pkg:RemoteLogicalPackage(arc,fam,a.runtime) for pkg,fam in sorted(catalogs.items())}
    multi=MultiPackageReader(views); hmap=byhash(multi)

    parts=[]; errors=[]
    for tag in wanted:
        parent=parent_for_model(visual,tag)
        me=hmap.get(tag)
        if me is None or me['reference'].upper()!=D1_ENTITY_MODEL_CLASS:
            raise ValueError(f'{tag}: D1 entity model absent')
        model=parse_model(multi.entry(me['index']),'PS4')
        for mi,mesh in enumerate(model['meshes']):
            offsets=mesh.get('stage_part_offsets_source_derived') or []
            groups=group_index_map(offsets,len(mesh['parts']))
            for pi,p in enumerate(mesh['parts']):
                mat=resolve_material(p,parent)
                highest=int(p['lod']) in HIGHEST_LODS
                row={
                    'model_tag':tag,
                    'mesh_index':mi,
                    'part_index':pi,
                    'stage_group_index':groups.get(pi),
                    'index_offset':int(p['index_offset']),
                    'index_count':int(p['index_count']),
                    'primitive_type':int(p['primitive_type']),
                    'lod':int(p['lod']),
                    'highest_detail':highest,
                    'gear_dye_change_color_index':int(p['gear_dye_change_color_index']),
                    'flags_d1':int(p['flags_d1']),
                    'external_identifier':int(p['external_identifier']),
                    **mat,
                }
                if mat.get('error'):
                    errors.append({k:row.get(k) for k in ('model_tag','mesh_index','part_index','variant_shader_index','error')})
                parts.append(row)

    highest=[x for x in parts if x['highest_detail']]
    ranges=collections.defaultdict(list)
    for x in highest:
        k=(x['model_tag'],x['mesh_index'],x['index_offset'],x['index_count'],x['primitive_type'])
        ranges[k].append(x)
    range_rows=[]
    for k,rows in sorted(ranges.items()):
        active=sorted({x.get('active_material_hash') for x in rows if x.get('active_material_hash')})
        dyes=sorted({x['gear_dye_change_color_index'] for x in rows})
        groups=sorted({x['stage_group_index'] for x in rows if x['stage_group_index'] is not None})
        variants=sorted({x['variant_shader_index'] for x in rows})
        range_rows.append({
            'model_tag':k[0],'mesh_index':k[1],'index_offset':k[2],'index_count':k[3],'primitive_type':k[4],
            'highest_detail_part_count':len(rows),
            'part_indices':[x['part_index'] for x in rows],
            'stage_group_indices':groups,
            'variant_shader_indices':variants,
            'gear_dye_change_color_indices':dyes,
            'active_material_hashes':active,
            'active_material_count':len(active),
            'parts':rows,
        })

    rep={
        'schema':'d1_guardian_stage_part_material_resolve/v1',
        'model_count':len(wanted),
        'all_part_count':len(parts),
        'highest_detail_part_count':len(highest),
        'highest_detail_range_count':len(range_rows),
        'multi_material_highest_detail_range_count':sum(x['active_material_count']>1 for x in range_rows),
        'multi_part_highest_detail_range_count':sum(x['highest_detail_part_count']>1 for x in range_rows),
        'unresolved_material_count':len(errors),
        'highest_detail_lods':sorted(HIGHEST_LODS),
        'active_material_package_ids':sorted({f'{pkg_id(x["active_material_hash"]):04X}' for x in highest if x.get('active_material_hash')}),
        'ranges':range_rows,
        'parts':parts,
        'errors':errors,
        'policy':(
            'Highest-detail classification mirrors Charm ELod.IsHighestLevel. Active material mirrors D1 DynamicMeshPart: inline material when VariantShaderIndex==-1, otherwise the first material selected by the owning EntityResource ExternalMaterialsMap entry. Multiple surviving passes/ranges are preserved rather than collapsed.'
        ),
    }
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(rep,indent=2)+'\n')
    print('MODELS',rep['model_count'],'PARTS',rep['all_part_count'],'HIGHEST',rep['highest_detail_part_count'],'RANGES',rep['highest_detail_range_count'])
    print('MULTI_PART_RANGES',rep['multi_part_highest_detail_range_count'],'MULTI_MATERIAL_RANGES',rep['multi_material_highest_detail_range_count'],'ERRORS',len(errors))
    print('ACTIVE_MATERIAL_PACKAGES',rep['active_material_package_ids'])
    for r in range_rows:
        print('RANGE',r['model_tag'],r['mesh_index'],r['index_offset'],r['index_count'],'parts',r['part_indices'],'groups',r['stage_group_indices'],'variants',r['variant_shader_indices'],'dyes',r['gear_dye_change_color_indices'],'materials',r['active_material_hashes'])
    if errors:
        raise SystemExit(f'{len(errors)} stage-part material resolution error(s)')
    return 0


if __name__=='__main__':
    raise SystemExit(main())
