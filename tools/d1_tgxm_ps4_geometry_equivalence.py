#!/usr/bin/env python3
"""Verify decoded geometry equivalence between a Bungie D1 TGXM and retail PS4 model.

This closes the gap left by structural signature matching.  It compares decoded
vertex positions in original vertex order and expands every selected stage-0 /
highest-detail triangle strip to explicit nondegenerate triangles before comparing
retail topology.

TGXM decoding follows the archived Bungie/Spasm vertex layout contract recorded
in render_metadata.js: format elements are serialized in stream order; the target
mobile D1 position element is float4.  The first three components are the mobile
geometry position and the fourth is retained as the rigid-bone/index lane when the
layout uses it.  No web-only position_scale/position_offset transform is applied to
mobile GearAsset TGXM geometry.

PS4 decoding delegates to the project's source-crosschecked ROI model decoder and
generic vertex/index decoding helpers.  Cross-package buffers are resolved only by
their encoded Tiger FileHashes through verified member catalogs.

A pass requires exact active mesh order/count and part-count sequence, equal vertex
counts, per-index positions within --position-tolerance, equal expanded triangle
count per part, and exact expanded triangle vertex-index sequences.  Raw strip
index counts may differ and are reported rather than required.
"""
from __future__ import annotations

import argparse
import json
import math
import struct
import sys
from pathlib import Path
from typing import Any

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from d1_entity_model_export import decode_indices, decode_vb0, hdr_stride, index_is32, primitive_faces
from d1_entity_model_probe import parse_model
from d1_guardian_stage_part_material_resolve import HIGHEST_LODS
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_model_tgxm_signature_match import LazyExactHashResolver
from d1_split_tar_extract import SplitHttpTar
from d1_tgxm_unpack import parse_tgxm


def norm(v: str) -> str:
    return v.upper().removeprefix('0X').zfill(8)


def tgxm_payload(data: bytes, rep: dict, name: str) -> bytes:
    row = next((x for x in rep['files'] if x['file_name'] == name), None)
    if row is None:
        raise KeyError(f'TGXM missing payload {name!r}')
    a = int(row['file_offset']); b = a + int(row['file_size'])
    return data[a:b]


def element_count_and_width(type_name: str) -> tuple[str, int, int]:
    prefix = '_vertex_format_attribute_'
    if not type_name.startswith(prefix):
        raise ValueError(f'unexpected TGXM vertex attribute type {type_name!r}')
    s = type_name[len(prefix):]
    for base, width in [('ubyte',1),('byte',1),('ushort',2),('short',2),('uint',4),('int',4),('float',4)]:
        if s.startswith(base):
            tail = s[len(base):]
            if not tail.isdigit() or int(tail) <= 0:
                raise ValueError(f'bad TGXM vertex attribute arity {type_name!r}')
            return base, int(tail), width
    raise ValueError(f'unsupported TGXM vertex attribute type {type_name!r}')


def decode_tgxm_position_stream(data: bytes, rep: dict, mesh: dict, mesh_index: int) -> tuple[np.ndarray, np.ndarray | None, dict]:
    defs = mesh.get('stage_part_vertex_stream_layout_definitions') or []
    if len(defs) != 1:
        raise ValueError(f'TGXM mesh {mesh_index}: expected exactly one vertex stream layout definition')
    formats = defs[0].get('formats') or []
    buffers = mesh.get('vertex_buffers') or []
    if len(formats) != len(buffers):
        raise ValueError(f'TGXM mesh {mesh_index}: layout format/buffer count mismatch {len(formats)}/{len(buffers)}')

    position = None
    position4 = None
    source = None
    for bi, (fmt, vb) in enumerate(zip(formats, buffers)):
        stride = int(vb['stride_byte_size'])
        payload = tgxm_payload(data, rep, vb['file_name'])
        if len(payload) != int(vb['byte_size']) or len(payload) % stride:
            raise ValueError(f'TGXM mesh {mesh_index} stream {bi}: byte-size/stride mismatch')
        n = len(payload) // stride
        cursor = 0
        for ei, element in enumerate(fmt.get('elements') or []):
            base, count, width = element_count_and_width(str(element['type']))
            byte_count = count * width
            semantic = str(element.get('semantic',''))
            if semantic == '_tfx_vb_semantic_position':
                if position is not None:
                    raise ValueError(f'TGXM mesh {mesh_index}: multiple position elements')
                if base != 'float' or count != 4:
                    raise ValueError(f'TGXM mesh {mesh_index}: position is {element["type"]}, expected archived mobile D1 float4')
                vals = np.empty((n,4), dtype=np.float32)
                for vi in range(n):
                    off = vi * stride + cursor
                    vals[vi] = np.frombuffer(payload, dtype='<f4', count=4, offset=off)
                if not np.all(np.isfinite(vals)):
                    raise ValueError(f'TGXM mesh {mesh_index}: non-finite position values')
                position4 = vals
                position = vals[:,:3].copy()
                source = {'vertex_buffer_index': bi, 'element_index': ei, 'serialized_cursor': cursor,
                          'metadata_offset': int(element.get('offset',-1)), 'type': element['type'],
                          'stride': stride, 'vertex_count': n}
            cursor += byte_count
        if cursor != stride:
            raise ValueError(f'TGXM mesh {mesh_index} stream {bi}: serialized element widths total {cursor}, stride is {stride}')
    if position is None:
        raise ValueError(f'TGXM mesh {mesh_index}: no position semantic')
    return position, position4, source


def tgxm_active_parts(mesh: dict) -> list[dict[str, Any]]:
    offsets = [int(x) for x in mesh.get('stage_part_offsets') or []]
    if len(offsets) < 2:
        raise ValueError('TGXM mesh missing stage-0 boundaries')
    parts = mesh.get('stage_part_list') or []
    a,b = offsets[0], offsets[1]
    if a < 0 or b < a or b > len(parts):
        raise ValueError(f'invalid TGXM stage0 range [{a},{b})/{len(parts)}')
    out=[]
    for pi in range(a,b):
        p=parts[pi]
        name=str((p.get('lod_category') or {}).get('name',''))
        # Same source rule used by the calibrated matcher; D1 highest-detail names
        # contain category 0/1 families. Exact selected Spektar fixtures use _01.
        if '0' not in name:
            continue
        out.append({'part_index':pi,'start_index':int(p['start_index']),'index_count':int(p['index_count']),
                    'primitive_type':int(p['primitive_type']),'lod_name':name})
    return out


def ps4_active_parts(mesh: dict) -> list[dict[str, Any]]:
    offsets=[int(x) for x in mesh.get('stage_part_offsets_source_derived') or []]
    if len(offsets)<2: raise ValueError('PS4 mesh missing source-derived stage0 boundaries')
    parts=mesh['parts']; a,b=offsets[0],offsets[1]
    if a<0 or b<a or b>len(parts): raise ValueError(f'invalid PS4 stage0 range [{a},{b})/{len(parts)}')
    out=[]
    for pi in range(a,b):
        p=parts[pi]
        if int(p['lod']) not in HIGHEST_LODS: continue
        out.append({'part_index':pi,'start_index':int(p['index_offset']),'index_count':int(p['index_count']),
                    'primitive_type':int(p['primitive_type']),'lod':int(p['lod'])})
    return out


def linked_payload(resolver: LazyExactHashResolver, header_hash: str) -> tuple[bytes, bytes, dict]:
    _v,e,h = resolver.bytes(norm(header_hash))
    payload_hash = norm(e['reference'])
    _pv,pe,p = resolver.bytes(payload_hash)
    return h,p,{'header_hash':norm(header_hash),'payload_hash':payload_hash,
                'header_bytes':len(h),'payload_bytes':len(p),'payload_entry_size':int(pe['file_size'])}


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--target-tgxm',type=Path,required=True)
    ap.add_argument('--model',required=True)
    ap.add_argument('--member-catalog',type=Path,action='append',required=True)
    ap.add_argument('--base-url',required=True)
    ap.add_argument('--part-count',type=int,default=10)
    ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('--position-tolerance',type=float,default=2e-6)
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args()
    if a.position_tolerance < 0: raise SystemExit('negative position tolerance')

    tag=norm(a.model)
    tgx_data=a.target_tgxm.read_bytes(); tgx=parse_tgxm(tgx_data)
    tmeshes=((tgx.get('render_metadata') or {}).get('render_model') or {}).get('render_meshes') or []
    if not tmeshes: raise SystemExit('TGXM has no render meshes')

    catalogs=load_catalogs(a.member_catalog)
    base=a.base_url.rstrip('/')
    arc=SplitHttpTar([f'{base}/packages.tar.{i:03d}' for i in range(1,a.part_count+1)],retries=6,timeout=90)
    resolver=LazyExactHashResolver(arc,catalogs,a.runtime)
    _mv,me,mb=resolver.bytes(tag)
    model=parse_model(mb,'PS4')

    tactive=[]
    for mi,m in enumerate(tmeshes):
        parts=tgxm_active_parts(m)
        if parts: tactive.append((mi,m,parts))
    pactive=[]
    for mi,m in enumerate(model['meshes']):
        parts=ps4_active_parts(m)
        if parts: pactive.append((mi,m,parts))
    if [len(x[2]) for x in tactive] != [len(x[2]) for x in pactive]:
        raise ValueError(f'active part-count sequence mismatch TGXM {[len(x[2]) for x in tactive]} PS4 {[len(x[2]) for x in pactive]}')

    rows=[]; all_pass=True
    for slot,((tmi,tm,tparts),(pmi,pm,pparts)) in enumerate(zip(tactive,pactive)):
        tpos,tpos4,tpossrc=decode_tgxm_position_stream(tgx_data,tgx,tm,tmi)
        vh,vpayload,vmeta=linked_payload(resolver,pm['vertices1'])
        pstride=hdr_stride(vh)
        ppos=decode_vb0(vpayload,pstride)
        ppos=(ppos*np.asarray(pm['model_scale'][:3],dtype=np.float32)+np.asarray(pm['model_translation'][:3],dtype=np.float32)).astype(np.float32)
        if len(tpos)!=len(ppos): raise ValueError(f'active slot {slot}: vertex count mismatch {len(tpos)}/{len(ppos)}')
        delta=np.linalg.norm(tpos.astype(np.float64)-ppos.astype(np.float64),axis=1)
        per_index_pass=bool(np.all(delta<=a.position_tolerance))

        tih=tgxm_payload(tgx_data,tgx,tm['index_buffer']['file_name'])
        tis32=int(tm['index_buffer']['value_byte_size'])==4
        tindices=decode_indices(tih,tis32)
        pih,pipayload,pimeta=linked_payload(resolver,pm['indices'])
        pis32=index_is32(pih)
        pindices=decode_indices(pipayload,pis32)

        part_rows=[]; topology_pass=True
        for order,(tp,pp) in enumerate(zip(tparts,pparts)):
            if tp['primitive_type']!=pp['primitive_type']:
                topology_pass=False
                part_rows.append({'part_order':order,'primitive_match':False,'tgxm':tp,'ps4':pp})
                continue
            tf=primitive_faces(tindices[tp['start_index']:tp['start_index']+tp['index_count']],tp['primitive_type'],tis32)
            pf=primitive_faces(pindices[pp['start_index']:pp['start_index']+pp['index_count']],pp['primitive_type'],pis32)
            exact=bool(tf.shape==pf.shape and np.array_equal(tf,pf))
            topology_pass &= exact
            part_rows.append({
                'part_order':order,'primitive_match':True,
                'tgxm':tp,'ps4':pp,
                'tgxm_expanded_triangle_count':int(len(tf)),
                'ps4_expanded_triangle_count':int(len(pf)),
                'expanded_triangle_count_match':bool(len(tf)==len(pf)),
                'expanded_vertex_index_sequence_exact':exact,
                'tgxm_first_triangles':tf[:5].tolist(),
                'ps4_first_triangles':pf[:5].tolist(),
            })

        slot_pass=per_index_pass and topology_pass
        all_pass &= slot_pass
        rows.append({
            'active_slot':slot,'tgxm_mesh_index':tmi,'ps4_mesh_index':pmi,
            'vertex_count':int(len(tpos)),'tgxm_position_source':tpossrc,
            'ps4_position_buffer':vmeta,'ps4_position_stride':pstride,
            'position_tolerance':a.position_tolerance,
            'per_index_position_max_error':float(delta.max(initial=0)),
            'per_index_position_mean_error':float(delta.mean() if len(delta) else 0),
            'per_index_position_p99_error':float(np.quantile(delta,.99) if len(delta) else 0),
            'per_index_position_within_tolerance_count':int(np.sum(delta<=a.position_tolerance)),
            'per_index_position_sequence_equivalent':per_index_pass,
            'tgxm_position4_w_unique_sample':[float(x) for x in np.unique(tpos4[:,3])[:32]],
            'tgxm_index_count':int(len(tindices)),'ps4_index_count':int(len(pindices)),
            'ps4_index_buffer':pimeta,
            'part_count':len(tparts),'parts':part_rows,
            'expanded_topology_index_sequence_equivalent':topology_pass,
            'geometry_equivalent':slot_pass,
        })

    rep={
        'schema':'d1_tgxm_ps4_geometry_equivalence/v1',
        'target_tgxm':str(a.target_tgxm),'target_tgxm_sha256':tgx['sha256'],'target_tgxm_file_identifier':tgx['file_identifier'],
        'ps4_model_tag_hash':tag,'ps4_model_entry_size':int(me['file_size']),
        'tgxm_active_mesh_indices':[x[0] for x in tactive],'ps4_active_mesh_indices':[x[0] for x in pactive],
        'active_part_count_sequence':[len(x[2]) for x in tactive],
        'active_meshes':rows,'geometry_equivalent':bool(all_pass),
        'policy':(
            'Promotion requires original-order decoded positions to agree within an explicit quantization tolerance and '
            'expanded nondegenerate triangle vertex-index sequences to be exactly equal per selected part. Raw packed '
            'vertex/index bytes and strip index counts are not required to be equal across published mobile TGXM and retail PS4.'
        ),
    }
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(rep,indent=2)+'\n')
    print('TGXM',tgx['file_identifier'],tgx['sha256'])
    print('PS4',tag,'ACTIVE',rep['ps4_active_mesh_indices'],'PARTS',rep['active_part_count_sequence'])
    for x in rows:
        print('SLOT',x['active_slot'],'MESH',x['tgxm_mesh_index'],x['ps4_mesh_index'],'VERTS',x['vertex_count'],
              'POS_MAX',x['per_index_position_max_error'],'POS_PASS',x['per_index_position_sequence_equivalent'],
              'TOPOLOGY',x['expanded_topology_index_sequence_equivalent'])
        for p in x['parts']:
            print(' PART',p['part_order'],'RAW_COUNTS',p['tgxm']['index_count'],p['ps4']['index_count'],
                  'TRIS',p.get('tgxm_expanded_triangle_count'),p.get('ps4_expanded_triangle_count'),
                  'EXACT',p.get('expanded_vertex_index_sequence_exact'))
    print('GEOMETRY_EQUIVALENT',rep['geometry_equivalent'])
    return 0 if rep['geometry_equivalent'] else 2


if __name__=='__main__':
    raise SystemExit(main())
