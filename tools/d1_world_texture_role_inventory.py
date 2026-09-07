#!/usr/bin/env python3
"""Build a conservative semantic inventory from an exact D1 material/texture manifest.

The input manifest already proves material -> pixel shader -> t# -> Texture TagHash.
This tool deliberately separates three evidence levels:

* PROVEN: role was independently established by shader instruction dataflow.
* STRONG_FORMAT_CANDIDATE: resource format/topology is characteristic enough to
  guide a preview adapter, but is *not* promoted to canonical shader semantics.
* UNKNOWN: no safe semantic statement is made.

It is useful for prioritising shader families and for making a visibly textured
world preview without contaminating the canonical reverse-engineering record with
`t0 == albedo` guesses.

A native-dataflow role is authoritative even when it has no portable glTF slot.
In particular, a color-capable BC/RGBA texture proven to be an alpha/scalar/LOD
mask must never fall back to the generic "sole color t0" preview heuristic.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

from d1_shader_texture_roles import (
    PROVEN_PIXEL_SHADER_ROLES,
    PORTABLE_BASE_COLOR_ROLES,
    PORTABLE_NORMAL_ROLES,
)

COLOR_FORMATS={'BC1','BC2','BC3','RGBA8','BGRA8'}
NORMAL_VECTOR_FORMATS={'BC5'}
SCALAR_FORMATS={'BC4'}


def tex_shape(t:dict):
    h=t.get('header_info') or {}
    return (h.get('width'),h.get('height'),h.get('array_size'))


def resource_class(t:dict)->str:
    h=t.get('header_info') or {}
    arr=h.get('array_size')
    fmt=t.get('format_name')
    if arr==6:
        return 'CUBEMAP'
    if arr!=1:
        return 'UNKNOWN_ARRAY'
    if fmt in NORMAL_VECTOR_FORMATS:
        return 'VECTOR_BC5_2D'
    if fmt in SCALAR_FORMATS:
        return 'SCALAR_BC4_2D'
    if fmt in COLOR_FORMATS:
        return 'COLOR_CAPABLE_2D'
    return 'UNKNOWN_2D'


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('manifest',type=Path)
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args()
    d=json.loads(a.manifest.read_text())
    textures=d['textures'];materials=d['materials']

    shader_rows=defaultdict(list)
    material_semantics={}
    for mh,m in sorted(materials.items()):
        if 'pixel_shader' not in m:
            continue
        ps=m['pixel_shader']
        psb=sorted((b for b in m.get('bindings',[]) if b.get('stage')=='ps'),key=lambda x:int(x['texture_index']))
        rows=[]
        for b in psb:
            idx=int(b['texture_index'])
            t=textures.get(b['texture'],{})
            rc=resource_class(t)
            # New manifests may carry the semantic on each binding. Older exact
            # manifests remain valid by looking up the same independently proven
            # shader/t# table; this annotates semantics without changing the exact
            # serialized binding.
            proven=b.get('semantic_role') if b.get('semantic_status')=='PROVEN' else PROVEN_PIXEL_SHADER_ROLES.get(ps,{}).get(idx)
            row={
                'texture_index':idx,'texture':b['texture'],
                'format_name':t.get('format_name'),'shape':tex_shape(t),
                'resource_class':rc,'proven_role':proven,
                'evidence_status':'PROVEN' if proven else 'UNKNOWN',
                'preview_role':proven,
            }
            if not proven:
                if rc=='CUBEMAP':
                    row.update({'evidence_status':'STRONG_FORMAT_CANDIDATE','preview_role':'cubemap_resource'})
                elif rc=='VECTOR_BC5_2D':
                    row.update({'evidence_status':'STRONG_FORMAT_CANDIDATE','preview_role':'normal_vector_candidate'})
                elif rc=='SCALAR_BC4_2D':
                    row.update({'evidence_status':'STRONG_FORMAT_CANDIDATE','preview_role':'scalar_mask_candidate'})
            rows.append(row)

        # Canonically proven roles take precedence in the portable adapter. Only
        # when no instruction-proven direct base/normal exists do we fall back to
        # format-based preview heuristics, and those heuristics may consider only
        # rows whose semantics remain unproven. A proven non-portable mask/LOD/
        # palette role is negative evidence against treating that same binding as
        # base color or a normal merely because its storage format looks suitable.
        proven_base=[r for r in rows if r.get('proven_role') in PORTABLE_BASE_COLOR_ROLES]
        proven_normal=[r for r in rows if r.get('proven_role') in PORTABLE_NORMAL_ROLES]
        base=None;base_reason=None;base_conf='NONE'
        normal=None;normal_reason=None;normal_conf='NONE'
        if proven_base:
            proven_base.sort(key=lambda r:r['texture_index'])
            base=proven_base[0]['texture'];base_conf='PROVEN'
            base_reason=f'native shader dataflow proves {proven_base[0]["proven_role"]}'
        if proven_normal:
            proven_normal.sort(key=lambda r:r['texture_index'])
            normal=proven_normal[0]['texture'];normal_conf='PROVEN'
            normal_reason=f'native shader dataflow proves {proven_normal[0]["proven_role"]}'

        # Preview-only fallback selection. This is intentionally not canonical
        # semantic promotion. Prefer an *unproven* t0 color texture paired with a
        # same-size unproven BC5 resource; otherwise permit a sole unproven color
        # t0. Proven non-portable roles are excluded from all fallback candidates.
        byidx={r['texture_index']:r for r in rows}
        t0=byidx.get(0)
        if base is None and t0 and not t0.get('proven_role') and t0['resource_class']=='COLOR_CAPABLE_2D':
            t0shape=t0['shape']
            paired=[r for r in rows if r['texture_index']!=0 and not r.get('proven_role') and r['resource_class']=='VECTOR_BC5_2D' and r['shape']==t0shape]
            if paired:
                base=t0['texture'];base_reason='unproven t0 color-capable 2D paired with same-resolution unproven BC5 vector resource';base_conf='STRONG_FORMAT_CANDIDATE'
            else:
                color2d=[r for r in rows if not r.get('proven_role') and r['resource_class']=='COLOR_CAPABLE_2D']
                if len(color2d)==1:
                    base=t0['texture'];base_reason='sole unproven color-capable 2D PS resource and occupies t0';base_conf='MEDIUM_PREVIEW_CANDIDATE'

        # D1 frequently places scalar masks at t0 and the actual surface/normal
        # pair in later registers. For previews, recognize a *unique* exact-size
        # unproven COLOR_CAPABLE_2D + BC5 pair regardless of register number. This
        # remains format/topology evidence only.
        if base is None:
            color_rows=[r for r in rows if not r.get('proven_role') and r['resource_class']=='COLOR_CAPABLE_2D']
            normal_rows=[r for r in rows if not r.get('proven_role') and r['resource_class']=='VECTOR_BC5_2D']
            pairs=[(c,n) for c in color_rows for n in normal_rows if c['shape']==n['shape']]
            # Deduplicate repeated bindings of the same texture pair (some D1
            # shaders bind one physical texture to multiple t# registers).
            uniq={ (c['texture'],n['texture']):(c,n) for c,n in pairs }
            if len(uniq)==1:
                c,n=next(iter(uniq.values()))
                base=c['texture'];base_conf='STRONG_FORMAT_CANDIDATE'
                base_reason=f'unique same-resolution unproven color-capable/BC5 pair at t{c["texture_index"]}/t{n["texture_index"]}; preview-only'
                if normal is None:
                    normal=n['texture'];normal_conf='STRONG_FORMAT_CANDIDATE'
                    normal_reason=f'unique same-resolution unproven BC5 paired with preview color at t{c["texture_index"]}; preview-only'

        if normal is None and base:
            bs=tex_shape(textures.get(base,{}))
            same=[r for r in rows if not r.get('proven_role') and r['resource_class']=='VECTOR_BC5_2D' and r['shape']==bs]
            # Avoid silently selecting between genuinely distinct same-size normal
            # resources; duplicate t# bindings of one physical texture are fine.
            bytex={r['texture']:r for r in same}
            if len(bytex)==1:
                r=next(iter(bytex.values()))
                normal=r['texture'];normal_reason='unique unproven BC5 PS resource matches preview base dimensions';normal_conf='STRONG_FORMAT_CANDIDATE'

        rec={
            'material':mh,'pixel_shader':ps,'bindings':rows,
            'preview_base_color':base,'preview_base_confidence':base_conf,'preview_base_reason':base_reason,
            'preview_normal':normal,'preview_normal_confidence':normal_conf,
            'preview_normal_reason':normal_reason,
        }
        material_semantics[mh]=rec
        shader_rows[ps].append(rec)

    shader_inventory={}
    for ps,rows in shader_rows.items():
        idx_patterns=Counter(tuple(r['texture_index'] for r in x['bindings']) for x in rows)
        class_patterns=Counter(tuple((r['texture_index'],r['resource_class']) for r in x['bindings']) for x in rows)
        base=Counter(x['preview_base_confidence'] for x in rows)
        normal=Counter(x['preview_normal_confidence'] for x in rows)
        shader_inventory[ps]={
            'material_count':len(rows),
            'texture_index_patterns':[{'pattern':list(k),'count':v} for k,v in idx_patterns.most_common()],
            'resource_class_patterns':[{'pattern':[[i,c] for i,c in k],'count':v} for k,v in class_patterns.most_common()],
            'preview_base_confidence':dict(base),
            'preview_normal_confidence':dict(normal),
            'materials':[x['material'] for x in rows],
        }

    base_counts=Counter(x['preview_base_confidence'] for x in material_semantics.values())
    norm_counts=Counter(x['preview_normal_confidence'] for x in material_semantics.values())
    out={
        'schema_version':5,
        'status':'D1_WORLD_TEXTURE_ROLE_INVENTORY_EVIDENCE_SCOPED',
        'source_status':d.get('status'),
        'material_count':len(material_semantics),'pixel_shader_count':len(shader_inventory),
        'preview_base_coverage':dict(base_counts),'preview_normal_coverage':dict(norm_counts),
        'shader_inventory':dict(sorted(shader_inventory.items(),key=lambda kv:(-kv[1]['material_count'],kv[0]))),
        'materials':material_semantics,
        'policy':'PROVEN roles are canonical instruction-level semantics and exclude incompatible preview fallbacks on the same binding. STRONG_FORMAT_CANDIDATE and MEDIUM_PREVIEW_CANDIDATE apply only to still-unproven bindings and never overwrite exact shader t# semantics.',
    }
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({
        'materials':out['material_count'],'pixel_shaders':out['pixel_shader_count'],
        'preview_base_coverage':out['preview_base_coverage'],
        'preview_normal_coverage':out['preview_normal_coverage'],
    },indent=2))
    return 0

if __name__=='__main__':
    raise SystemExit(main())

# Dependency-closure rerun marker: bank-aware FileHash backing traversal is now authoritative.
