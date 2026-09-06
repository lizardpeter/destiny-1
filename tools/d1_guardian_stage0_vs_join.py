#!/usr/bin/env python3
"""Join exact Bungie stage-0 Guardian draw parts to native PS4 VS signatures.

Consumes d1_guardian_stage0_material_resolve/v1.  Each selected range must already
have exactly one active material.  This tool follows only that material's retail
ROI +0x28 VertexShader link, decodes the D1 PS4 32:9 Gnmx input semantic table,
and joins it to the exact model stream pair and independently classified half2
detail-multiplier lane.

The decisive negative-control families differ only by the final four bytes in
secondary stride:
  0x0C/0x10 -> 0x0C/0x14
  0x0C/0x14 -> 0x0C/0x18   (secondary-UV family)
  0x10/0x14 -> 0x10/0x18
The report tests whether each detail-family native signature is the corresponding
no-detail signature plus one final 2-component input.  It does not name native
semantic IDs by source-language convention.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import struct
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))

from d1_entity_model_export import byhash, hdr_stride, read_linked
from d1_entity_model_probe import D1_ENTITY_MODEL_CLASS, parse_model
from d1_guardian_texcoord2_lane_probe import candidate_offset
from d1_guardian_visual_context_probe import primary_w_mode, correct_uv_source
from d1_investment_arrangement_probe import filehash_pkg_index
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_ps4_vertex_shader_header import parse_header, VERTEX_SHADER_TYPE, VERTEX_SHADER_SUBTYPE
from d1_remote_investment_parent_probe import RemoteLogicalPackage
from d1_remote_model_export import MultiPackageReader
from d1_split_tar_extract import SplitHttpTar

PS4_MATERIAL_CLASS='80801AD7'


def pkg_id(tag:str)->int:
    return filehash_pkg_index(int(tag,16))[0]


def u32(b:bytes,o:int)->int:
    return struct.unpack_from('<I',b,o)[0]


def h32(v:int)->str:
    return f'{v & 0xffffffff:08X}'


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--stage0-report',type=Path,required=True)
    ap.add_argument('--member-catalog',type=Path,action='append',required=True)
    ap.add_argument('--base-url',required=True)
    ap.add_argument('--part-count',type=int,default=10)
    ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args()

    src=json.loads(a.stage0_report.read_text())
    if src.get('schema')!='d1_guardian_stage0_material_resolve/v1':
        raise ValueError('unexpected stage0 report schema')
    if src.get('errors') or src.get('multi_material_selected_range_count')!=0:
        raise ValueError('stage0 report is not uniquely material-resolved')

    model_tags=sorted({r['model_tag'] for r in src['ranges']})
    active_materials=sorted({r['active_material_hashes'][0] for r in src['ranges']})
    catalogs=load_catalogs(a.member_catalog)
    required={pkg_id(x) for x in model_tags+active_materials}
    missing=sorted(required-set(catalogs))
    if missing:
        raise SystemExit('missing model/material package catalogs: '+', '.join(f'{x:04X}' for x in missing))

    base=a.base_url.rstrip('/')
    arc=SplitHttpTar([f'{base}/packages.tar.{i:03d}' for i in range(1,a.part_count+1)],retries=6,timeout=90)
    views={pkg:RemoteLogicalPackage(arc,fam,a.runtime) for pkg,fam in sorted(catalogs.items())}
    multi=MultiPackageReader(views); hmap=byhash(multi)

    mesh_layout={}
    for tag in model_tags:
        e=hmap.get(tag)
        if e is None or e['reference'].upper()!=D1_ENTITY_MODEL_CLASS:
            raise ValueError(f'{tag}: D1 model unavailable')
        m=parse_model(multi.entry(e['index']),'PS4')
        for mi,mesh in enumerate(m['meshes']):
            _,h0,_,d0=read_linked(multi,hmap,mesh['vertices1'])
            _,h1,_,_=read_linked(multi,hmap,mesh['vertices2'])
            s0,s1=hdr_stride(h0),hdr_stride(h1)
            wm=primary_w_mode(d0,s0)
            uvsrc,uvreason=correct_uv_source(s0,s1,wm['mode'])
            off=candidate_offset(s1,uvsrc)
            mesh_layout[(tag,mi)]={
                'stride0':s0,'stride1':s1,'primary_w_mode':wm['mode'],
                'uv0_source':uvsrc,'uv0_source_evidence':uvreason,
                'detail_half2_candidate':off is not None,'detail_half2_offset':off,
            }

    material_cache={}; shader_cache={}
    rows=[]
    for rr in src['ranges']:
        if len(rr['active_material_hashes'])!=1 or rr['selected_part_count']!=1:
            raise ValueError(f'non-unique stage0 range {rr}')
        mh=rr['active_material_hashes'][0]
        if mh not in material_cache:
            me=hmap.get(mh)
            if me is None: raise KeyError(f'{mh}: active material unavailable')
            if me['reference'].upper()!=PS4_MATERIAL_CLASS:
                raise ValueError(f'{mh}: {me["reference"]} is not ROI material')
            mb=multi.entry(me['index'])
            vs=h32(u32(mb,0x28))
            material_cache[mh]={'vertex_shader_hash':vs,'payload_sha256':hashlib.sha256(mb).hexdigest()}
        vs=material_cache[mh]['vertex_shader_hash']
        if vs not in shader_cache:
            ve=hmap.get(vs)
            if ve is None: raise KeyError(f'{vs}: stage0 vertex shader unavailable; package {pkg_id(vs):04X}')
            if (ve['type'],ve['subtype'])!=(VERTEX_SHADER_TYPE,VERTEX_SHADER_SUBTYPE):
                raise ValueError(f'{vs}: unexpected class {ve["type"]}:{ve["subtype"]}')
            vb=multi.entry(ve['index'])
            ne=hmap.get(ve['reference'].upper())
            if ne is None: raise KeyError(f'{vs}: native shader {ve["reference"]} unavailable')
            nb=multi.entry(ne['index'])
            dec=parse_header(vb,nb)
            shader_cache[vs]={
                'native_shader_hash':ve['reference'].upper(),
                'input_component_widths':[x['size_in_elements'] for x in dec['gnmx']['input_semantics']],
                'input_semantic_ids':[x['semantic'] for x in dec['gnmx']['input_semantics']],
                'input_vgprs':[x['vgpr'] for x in dec['gnmx']['input_semantics']],
                'num_input_semantics':dec['gnmx']['num_input_semantics'],
                'num_export_semantics':dec['gnmx']['num_export_semantics'],
                'header_size':dec['header_size'],'checks':dec['checks'],'native_checks':dec.get('native_checks'),
            }
        layout=mesh_layout[(rr['model_tag'],rr['mesh_index'])]
        rows.append({
            'model_tag':rr['model_tag'],'mesh_index':rr['mesh_index'],
            'index_offset':rr['index_offset'],'index_count':rr['index_count'],'primitive_type':rr['primitive_type'],
            'part_index':rr['part_indices'][0],
            'gear_dye_change_color_index':rr['gear_dye_change_color_indices'][0],
            'active_material_hash':mh,'vertex_shader_hash':vs,
            **layout,**shader_cache[vs],
        })

    sigsets=collections.defaultdict(set)
    shader_sets=collections.defaultdict(set)
    for r in rows:
        key=(r['stride0'],r['stride1'],r['uv0_source'],r['detail_half2_candidate'])
        sigsets[key].add(tuple(r['input_component_widths']))
        shader_sets[key].add(r['vertex_shader_hash'])

    # Exact byte-layout control pairs. The second member has four extra secondary
    # bytes and the independently validated half2 lane.
    pair_specs=[
        ((0x0c,0x10,'primary',False),(0x0c,0x14,'primary',True)),
        ((0x0c,0x14,'secondary',False),(0x0c,0x18,'secondary',True)),
        ((0x10,0x14,'secondary',False),(0x10,0x18,'secondary',True)),
    ]
    controls=[]
    all_pass=True
    for base_key,detail_key in pair_specs:
        b=sigsets.get(base_key,set()); d=sigsets.get(detail_key,set())
        present=bool(b and d)
        passed=None
        if present:
            passed=all(any(ds==bs+(2,) for bs in b) for ds in d) and all(any(ds==bs+(2,) for ds in d) for bs in b)
            all_pass &= passed
        controls.append({
            'base_layout':{'stride0':base_key[0],'stride1':base_key[1],'uv0_source':base_key[2],'detail':False},
            'detail_layout':{'stride0':detail_key[0],'stride1':detail_key[1],'uv0_source':detail_key[2],'detail':True},
            'base_signatures':[list(x) for x in sorted(b)],'detail_signatures':[list(x) for x in sorted(d)],
            'base_shaders':sorted(shader_sets.get(base_key,set())),'detail_shaders':sorted(shader_sets.get(detail_key,set())),
            'both_present':present,'detail_equals_base_plus_final_vec2':passed,
        })
    comparable=[c for c in controls if c['both_present']]

    rep={
        'schema':'d1_guardian_stage0_vs_join/v1',
        'range_count':len(rows),'distinct_active_material_count':len(material_cache),
        'distinct_vertex_shader_count':len(shader_cache),
        'detail_range_count':sum(r['detail_half2_candidate'] for r in rows),
        'no_detail_range_count':sum(not r['detail_half2_candidate'] for r in rows),
        'control_count':len(controls),'comparable_control_count':len(comparable),
        'all_comparable_controls_pass':all_pass and bool(comparable),
        'controls':controls,'ranges':rows,
        'policy':(
            'Only Bungie stage-0 + highest-detail + source-resolved active materials participate. Native semantic IDs remain numeric. The additional final vec2 is named the D1 dye-detail texcoord multiplier only when combined with the independent retail half2 byte census and archived Bungie a_texcoord2 shader contract.'
        ),
    }
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(rep,indent=2)+'\n')
    print('RANGES',len(rows),'MATERIALS',len(material_cache),'SHADERS',len(shader_cache),'DETAIL',rep['detail_range_count'],'NO_DETAIL',rep['no_detail_range_count'])
    for c in controls: print('CONTROL',c)
    for r in rows: print('DRAW',r['model_tag'],r['mesh_index'],r['index_offset'],r['active_material_hash'],r['vertex_shader_hash'],f"{r['stride0']:#x}/{r['stride1']:#x}",r['uv0_source'],r['detail_half2_candidate'],r['input_component_widths'])
    return 0


if __name__=='__main__':
    raise SystemExit(main())
