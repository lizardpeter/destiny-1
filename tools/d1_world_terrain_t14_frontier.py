#!/usr/bin/env python3
"""Correlate exact D1 terrain material, native PS and per-part dyemap evidence.

This adapter deliberately stops one step short of naming T14 as the dyemap binding.
It proves whether native T14 consumption is external to SMaterial_ROI.PSTextures and
whether every source-selected terrain part using a T14-consuming shader carries an
exact effective STerrain dyemap under the source-replayed fallback policy.

That distinction matters: a resource-table index observed in GCN is exact, but its
runtime producer must not be guessed solely from the numerical slot.
"""
from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path

NULLS={"00000000","FFFFFFFF",None}

def norm(v):
    return str(v).upper().removeprefix("0X").zfill(8)


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--ps-resources',type=Path,required=True)
    ap.add_argument('--image-usage',type=Path,required=True)
    ap.add_argument('--terrain-scene',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    c=json.loads(a.ps_resources.read_text())
    u=json.loads(a.image_usage.read_text())
    s=json.loads(a.terrain_scene.read_text())
    if c.get('status')!='D1_WORLD_TERRAIN_PS_RESOURCE_CENSUS_COMPLETE' or c.get('violations') or c.get('missing_dependency_package_ids'):
        raise SystemExit('terrain PS resource census not authoritative')
    if u.get('status')!='D1_GCN_IMAGE_RESOURCE_USAGE_EXACT' or u.get('unmatched_image_instruction_count') or u.get('missing_disassembly_shaders'):
        raise SystemExit('terrain GCN image usage not authoritative')
    if s.get('status')!='D1_WORLD_TERRAIN_SCENE_COMPLETE':
        raise SystemExit('terrain scene not authoritative')

    use={norm(r['shader']):{int(x) for x in r.get('used_texture_indices',[])} for r in u.get('shaders',[])}
    mats={norm(r['material']):r for r in c.get('materials',[]) if r.get('status')=='D1_TERRAIN_SELECTED_MATERIAL_PS_LINK_PRESERVED'}
    if len(mats)!=int(c.get('selected_material_count',-1)):
        raise SystemExit('selected material coverage mismatch')
    if set(use)!=set(c.get('pixel_shader_frequency',{})):
        raise SystemExit('shader set mismatch')

    t14_shaders=sorted(h for h,x in use.items() if 14 in x)
    no_t14_shaders=sorted(h for h,x in use.items() if 14 not in x)
    serialized_t14=[]
    t14_materials=[]
    non_t14_materials=[]
    material_rows=[]
    for mh,r in sorted(mats.items()):
        ps=norm(r['pixel_shader'])
        inds=[int(x) for x in r.get('ps_texture_indices',[])]
        has_serialized_14=14 in inds
        shader_uses_14=14 in use[ps]
        if has_serialized_14: serialized_t14.append(mh)
        (t14_materials if shader_uses_14 else non_t14_materials).append(mh)
        material_rows.append({
            'material':mh,'pixel_shader':ps,'shader_uses_t14':shader_uses_14,
            'serialized_ps_texture_indices':inds,'serialized_material_has_t14':has_serialized_14,
        })

    part_rows=[];missing_effective=[];unknown_material=[]
    part_hist=collections.Counter();control_hist=collections.Counter();dyemap_hist=collections.Counter()
    for p in s.get('parts',[]):
        mh=norm(p.get('material'))
        mr=mats.get(mh)
        if mr is None:
            unknown_material.append({'terrain':p.get('terrain'),'part_index':p.get('part_index'),'material':mh})
            continue
        ps=norm(mr['pixel_shader']);uses14=14 in use[ps]
        dy=p.get('effective_dyemap');dy_norm=None if dy in NULLS else norm(dy)
        ctrl=tuple(float(x) for x in p.get('dyemap_control_rgba',[]))
        part_hist['t14' if uses14 else 'no_t14']+=1
        if uses14 and dy_norm is None:
            missing_effective.append({'terrain':p.get('terrain'),'part_index':p.get('part_index'),'material':mh,'pixel_shader':ps})
        if uses14:
            if dy_norm is not None:dyemap_hist[dy_norm]+=1
            control_hist[str(list(ctrl))]+=1
        part_rows.append({
            'terrain':p.get('terrain'),'part_index':p.get('part_index'),'group_index':p.get('group_index'),
            'material':mh,'pixel_shader':ps,'shader_uses_t14':uses14,
            'effective_dyemap':dy_norm,'dyemap_control_rgba':list(ctrl),
        })

    conditions={
        'all_95_shader_families_accounted':len(use)==95,
        't14_shader_count_is_91':len(t14_shaders)==91,
        'non_t14_shader_count_is_4':len(no_t14_shaders)==4,
        'no_selected_material_serializes_ps_texture_index_14':not serialized_t14,
        'all_108_materials_accounted':len(mats)==108,
        'all_1582_selected_parts_accounted':len(part_rows)==1582 and not unknown_material,
        'every_t14_part_has_exact_effective_dyemap':not missing_effective,
    }
    complete=all(conditions.values())
    out={
        'schema_version':1,
        'status':'D1_WORLD_TERRAIN_T14_EXTERNAL_RESOURCE_FRONTIER_COMPLETE' if complete else 'D1_WORLD_TERRAIN_T14_EXTERNAL_RESOURCE_FRONTIER_PARTIAL',
        'conditions':conditions,
        'shader_count':len(use),'t14_shader_count':len(t14_shaders),'non_t14_shader_count':len(no_t14_shaders),
        't14_shaders':t14_shaders,'non_t14_shaders':no_t14_shaders,
        'material_count':len(mats),'t14_material_count':len(t14_materials),'non_t14_material_count':len(non_t14_materials),
        'serialized_material_t14_count':len(serialized_t14),'serialized_material_t14_materials':serialized_t14,
        'selected_part_count':len(part_rows),'t14_part_count':part_hist['t14'],'non_t14_part_count':part_hist['no_t14'],
        't14_part_unique_effective_dyemap_count':len(dyemap_hist),
        't14_part_dyemap_control_histogram':dict(sorted(control_hist.items())),
        't14_part_effective_dyemap_usage_histogram':dict(sorted(dyemap_hist.items())),
        't14_parts_missing_effective_dyemap':missing_effective,
        'unknown_part_materials':unknown_material,
        'materials':material_rows,
        'parts':part_rows,
        'conclusion':(
            'Native terrain PS T14 consumption is proven external to every selected SMaterial_ROI serialized PS texture array. '
            'Every source-selected part whose shader consumes T14 simultaneously owns an exact effective STerrain dyemap. '
            'This tightly bounds T14 to a terrain-provided external resource, but this adapter does not yet name that resource as the dyemap '
            'until an independent runtime/export binding path or instruction-level producer proof closes the final edge.'
        ),
    }
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ('status','shader_count','t14_shader_count','non_t14_shader_count','material_count','t14_material_count','non_t14_material_count','serialized_material_t14_count','selected_part_count','t14_part_count','non_t14_part_count','t14_part_unique_effective_dyemap_count','t14_part_dyemap_control_histogram','conditions')},indent=2))
    return 0 if complete else 2

if __name__=='__main__':raise SystemExit(main())
