#!/usr/bin/env python3
"""Measure exact semantic coverage of the D1 Tower common-layer shader corpus.

This is deliberately stricter than "all textures exported".  For each exact native
pixel shader:
* recover visible-material frequency from the shader extract;
* intersect native sampled t# indices with t# indices actually serialized by visible
  materials using that shader;
* compare those sampled material registers with the instruction-proven role table.

Runtime resource-table image descriptors are not counted as missing material roles,
because they are not serialized material t# bindings.

A family is FULL_MATERIAL_TEXTURE_ROLE_COVERAGE only when every serialized material
texture register actually sampled by native GCN has an instruction-proven role.
This says nothing about full arithmetic/PBR/lighting reproduction; it only closes the
sampled material-resource semantics for that shader family.
"""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
if str(HERE) not in sys.path:sys.path.insert(0,str(HERE))
from d1_shader_texture_roles import PROVEN_PIXEL_SHADER_ROLES

def norm(x):return str(x).upper().removeprefix('0X').zfill(8)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--extract-report',type=Path,required=True)
    ap.add_argument('--image-usage',type=Path,required=True)
    ap.add_argument('--manifest',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()

    ex=json.loads(a.extract_report.read_text())
    iu=json.loads(a.image_usage.read_text())
    man=json.loads(a.manifest.read_text())
    violations=[]
    if ex.get('status')!='D1_WORLD_PIXEL_SHADER_GCN_EXACT' or ex.get('error_count'):
        violations.append('shader extract not exact')
    if iu.get('status')!='D1_GCN_IMAGE_RESOURCE_USAGE_EXACT':
        violations.append('image usage not exact')

    usage={norm(x['shader']):x for x in iu.get('shaders',[])}
    mats_by_shader={}
    for mh,m in (man.get('materials') or {}).items():
        sh=m.get('pixel_shader')
        if sh:mats_by_shader.setdefault(norm(sh),[]).append((norm(mh),m))

    rows=[]
    total_visible=0;role_visible=0;full_visible=0
    exact_families=0;role_families=0;full_families=0
    sampled_binding_total=0;proven_binding_total=0
    for er in ex.get('shaders',[]):
        sh=norm(er.get('shader'))
        if er.get('error'):continue
        exact_families+=1
        freq=int(er.get('visible_material_count',0))
        total_visible+=freq
        u=usage.get(sh)
        if not u:
            violations.append(f'{sh}: native image usage missing')
            continue
        mats=mats_by_shader.get(sh,[])
        # Exact union of serialized PS texture register indices for all visible materials.
        serialized=set()
        material_indices={}
        for mh,m in mats:
            inds={int(b['texture_index']) for b in m.get('bindings',[]) if b.get('stage')=='ps'}
            serialized.update(inds);material_indices[mh]=sorted(inds)
        used={int(x) for x in u.get('used_texture_indices',[])}
        sampled_material=sorted(used & serialized)
        runtime_only=sorted(used-serialized)
        rolemap={int(k):v for k,v in PROVEN_PIXEL_SHADER_ROLES.get(sh,{}).items()}
        proven_sampled=sorted(set(sampled_material)&set(rolemap))
        missing=sorted(set(sampled_material)-set(rolemap))
        extraneous=sorted(set(rolemap)-used)

        has_roles=bool(rolemap)
        full=not missing
        if has_roles:
            role_families+=1;role_visible+=freq
        if full:
            full_families+=1;full_visible+=freq
        sampled_binding_total+=len(sampled_material)
        proven_binding_total+=len(proven_sampled)
        rows.append({
            'shader':sh,
            'visible_material_count':freq,
            'visible_materials':[mh for mh,_ in mats],
            'native_image_instruction_count':int(u.get('image_instruction_count',0)),
            'native_used_texture_indices':sorted(used),
            'serialized_material_texture_indices':sorted(serialized),
            'sampled_serialized_material_texture_indices':sampled_material,
            'runtime_or_nonmaterial_texture_indices':runtime_only,
            'proven_roles':{str(k):v for k,v in sorted(rolemap.items())},
            'proven_sampled_material_texture_indices':proven_sampled,
            'unproven_sampled_material_texture_indices':missing,
            'role_indices_not_used_by_native_shader':extraneous,
            'semantic_resource_status':'FULL_MATERIAL_TEXTURE_ROLE_COVERAGE' if full else ('PARTIAL_MATERIAL_TEXTURE_ROLE_COVERAGE' if has_roles else 'NO_PROVEN_MATERIAL_TEXTURE_ROLES'),
            'material_serialized_indices':material_indices,
        })

    if exact_families!=65:violations.append(f'exact family count {exact_families} != 65')
    if len(rows)!=65:violations.append(f'coverage row count {len(rows)} != 65')

    unresolved=sorted(
        [x for x in rows if x['unproven_sampled_material_texture_indices']],
        key=lambda x:(-x['visible_material_count'],-x['native_image_instruction_count'],x['shader'])
    )
    role_rows=sorted(
        [x for x in rows if x['proven_roles']],
        key=lambda x:(-x['visible_material_count'],x['shader'])
    )

    def frac(a,b):return (a/b if b else None)
    out={
        'schema':'d1_tower_common_shader_semantic_coverage/v1',
        'status':'D1_TOWER_COMMON_SHADER_SEMANTIC_COVERAGE_EXACT' if rows and not violations else 'D1_TOWER_COMMON_SHADER_SEMANTIC_COVERAGE_PARTIAL',
        'exact_shader_family_count':exact_families,
        'visible_material_frequency_sum':total_visible,
        'families_with_any_proven_roles':role_families,
        'families_with_full_sampled_material_texture_role_coverage':full_families,
        'families_with_unproven_sampled_material_texture_roles':len(unresolved),
        'visible_material_frequency_with_any_proven_roles':role_visible,
        'visible_material_frequency_with_full_sampled_material_texture_role_coverage':full_visible,
        'family_any_role_fraction':frac(role_families,exact_families),
        'family_full_material_texture_role_fraction':frac(full_families,exact_families),
        'visible_material_frequency_any_role_fraction':frac(role_visible,total_visible),
        'visible_material_frequency_full_material_texture_role_fraction':frac(full_visible,total_visible),
        'sampled_serialized_material_texture_register_count':sampled_binding_total,
        'proven_sampled_serialized_material_texture_register_count':proven_binding_total,
        'sampled_material_texture_register_role_fraction':frac(proven_binding_total,sampled_binding_total),
        'highest_priority_unresolved_families':unresolved,
        'covered_families':role_rows,
        'rows':sorted(rows,key=lambda x:(-x['visible_material_count'],x['shader'])),
        'violations':violations,
        'semantic_boundary':{
            'native_image_consumption':'EXACT',
            'serialized_material_bindings':'EXACT',
            'role_strings':'INSTRUCTION_PROVEN_TABLE',
            'full_shader_arithmetic':'NOT_MEASURED',
            'lighting_global_buffers':'NOT_MEASURED',
            'portable_renderer_equivalence':'NOT_MEASURED',
        },
        'policy':'Coverage measures sampled serialized material-resource semantics only. It must not be interpreted as full shader, lighting, reflection, transparency, or framebuffer reproduction.',
    }
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({
        'status':out['status'],
        'exact_shader_family_count':exact_families,
        'families_with_any_proven_roles':role_families,
        'families_with_full_sampled_material_texture_role_coverage':full_families,
        'visible_material_frequency_sum':total_visible,
        'visible_material_frequency_any_role_fraction':out['visible_material_frequency_any_role_fraction'],
        'visible_material_frequency_full_material_texture_role_fraction':out['visible_material_frequency_full_material_texture_role_fraction'],
        'sampled_material_texture_register_role_fraction':out['sampled_material_texture_register_role_fraction'],
        'top_unresolved':[
            {'shader':x['shader'],'visible_material_count':x['visible_material_count'],
             'missing_t':x['unproven_sampled_material_texture_indices'],
             'used_t':x['native_used_texture_indices']}
            for x in unresolved[:15]
        ],
        'violations':violations,
    },indent=2))
    return 0 if out['status']=='D1_TOWER_COMMON_SHADER_SEMANTIC_COVERAGE_EXACT' else 2

if __name__=='__main__':raise SystemExit(main())
