#!/usr/bin/env python3
"""Prove serialized Crota color/partner part ordering for duplicated geometry.

Consumes the exact owning-parent material-binding artifact for model 8108E5B7.
For each known color/partner material family it joins parts by the exact geometry
key (mesh, LOD, index offset/count, primitive type).

This proves serialized part-array order only.  It does not promote render-stage
membership, draw submission order, render-target identity, or framebuffer order.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

MODEL='8108E5B7'
PARENT='8108E4BA'
PAIRS={
 '8108E7A9':'8108E7AB',
 '8108E7AA':'8108E7AC',
 '8108E7B1':'809DD1DC',
 '8108E7B2':'8108E7B4',
 '8108E7B3':'8108E7B5',
}

def norm(x):return str(x).upper().removeprefix('0X').zfill(8)

def selected(p):
    return norm(((p.get('selected_material') or {}).get('hash')) or 'FFFFFFFF')

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--material-bindings',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    d=json.loads(a.material_bindings.read_text())
    violations=[];rows=[]
    if d.get('status')!='D1_REMOTE_ACTIVITY_MODEL_PARENT_MATERIAL_BINDINGS_COMPLETE' and d.get('violations'):
        violations.append(f"material bindings not clean: {d.get('status')}")
    hits=[x for x in d.get('bindings',[]) if norm(x.get('model'))==MODEL and norm(x.get('parent_resource'))==PARENT]
    if len(hits)!=1:
        violations.append(f'expected one {MODEL}/{PARENT} binding, got {len(hits)}')
        hit={'meshes':[]}
    else:
        hit=hits[0]
        if not hit.get('validation_ok') or hit.get('violations'):
            violations.append('selected binding validation not closed')

    for mesh in hit.get('meshes',[]):
        mi=int(mesh['mesh_index']);parts=mesh.get('parts',[])
        bymat={}
        for p in parts:
            bymat.setdefault(selected(p),[]).append(p)
        for color,partner in PAIRS.items():
            for cp in bymat.get(color,[]):
                key=(int(cp['lod']),int(cp['index_offset']),int(cp['index_count']),int(cp['primitive_type']))
                matches=[pp for pp in bymat.get(partner,[]) if (
                    int(pp['lod']),int(pp['index_offset']),int(pp['index_count']),int(pp['primitive_type'])
                )==key]
                if len(matches)!=1:
                    violations.append(f'mesh{mi}:{color}:part{cp["part_index"]}: partner match count {len(matches)} for {key}')
                    continue
                pp=matches[0]
                rows.append({
                    'mesh_index':mi,
                    'geometry_key':{
                        'lod':key[0],'index_offset':key[1],'index_count':key[2],'primitive_type':key[3],
                    },
                    'color_material':color,'partner_material':partner,
                    'color_part_index':int(cp['part_index']),
                    'partner_part_index':int(pp['part_index']),
                    'serialized_relation':'COLOR_BEFORE_PARTNER' if int(cp['part_index'])<int(pp['part_index']) else 'PARTNER_BEFORE_COLOR',
                    'part_index_delta':int(pp['part_index'])-int(cp['part_index']),
                })

    color_before=sum(x['serialized_relation']=='COLOR_BEFORE_PARTNER' for x in rows)
    partner_before=sum(x['serialized_relation']=='PARTNER_BEFORE_COLOR' for x in rows)
    if len(rows)!=14:
        violations.append(f'expected 14 duplicated geometry pair instances, got {len(rows)}')
    if partner_before:
        violations.append(f'{partner_before} instances violate frozen color-before-partner relation')

    out={
        'schema':'d1_crota_serialized_pair_order/v1',
        'status':'D1_CROTA_SERIALIZED_PAIR_ORDER_EXACT' if len(rows)==14 and not violations else 'D1_CROTA_SERIALIZED_PAIR_ORDER_PARTIAL',
        'model':MODEL,'parent_resource':PARENT,
        'pair_instance_count':len(rows),
        'color_before_partner_count':color_before,
        'partner_before_color_count':partner_before,
        'rows':rows,'violations':violations,
        'conditional_framebuffer_consequence':{
            'premise':'IF color and partner are submitted sequentially to the same destination with promoted blend state 8',
            'color_shader_alpha':'0 for PS8108E953/955/956',
            'partner_shader_rgb':'0 for PS80AAE1CD/8108E958/959',
            'color_then_partner_formula':'after color: D1=C+D0; after partner: D2=(C+D0)*(1-A_partner)',
            'alpha_one_partner_consequence':'For 80AAE1CD and current PS8108E959 partner materials, A_partner=1, so same-target color-then-partner would yield D2=0.',
            'promotion':'CONDITIONAL_ALGEBRA_ONLY_NOT_DRAW_ORDER_PROOF',
        },
        'semantic_boundary':{
            'serialized_part_order':'EXACT',
            'render_stage':'WITHHELD',
            'draw_submission_order':'WITHHELD',
            'render_target_identity':'WITHHELD',
            'native_pass_order':'WITHHELD',
        },
        'policy':'Exact D1 part-array order is not equated with engine draw order. The alpha-one conditional shows why that distinction is material: naïve same-target serialized execution would erase the color family.',
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'status':out['status'],'instances':len(rows),
                      'color_before_partner':color_before,'partner_before_color':partner_before,
                      'rows':rows,'violations':violations},indent=2))
    return 0 if out['status']=='D1_CROTA_SERIALIZED_PAIR_ORDER_EXACT' else 2

if __name__=='__main__':raise SystemExit(main())
