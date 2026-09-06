#!/usr/bin/env python3
"""Probe D1 Guardian secondary vertex-stream lanes for Bungie a_texcoord2.

This is deliberately a census, not a decoder.  The archived Bungie D1 web
renderer consumes a semantic named `texcoord2` as a vec2 and computes:

    detail_uv = (base_uv * texcoord2) * detail_transform.xy
                + detail_transform.zw

Our retail PKG parser already source-closes position, UV0, normal, tangent and
skinning for the Spektar proof, but the remaining bytes in several D1 secondary
stream layouts are still called "colour" or "unresolved" by community tools.
This probe reads those bytes without assigning semantics and reports every
4-byte-aligned lane as both little-endian short2 and ubyte4.

A later decoder may promote one lane to TEXCOORD_1 only after the same offset and
encoding are supported across the relevant retail stream families.  This tool
never mutates geometry and never fabricates UVs.
"""
from __future__ import annotations

import argparse
import collections
import json
import math
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from d1_entity_model_export import byhash, hdr_stride, read_linked
from d1_entity_model_probe import D1_ENTITY_MODEL_CLASS, parse_model
from d1_guardian_visual_context_probe import primary_w_mode, correct_uv_source
from d1_investment_arrangement_probe import filehash_pkg_index
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_investment_parent_probe import RemoteLogicalPackage
from d1_remote_model_export import MultiPackageReader
from d1_split_tar_extract import SplitHttpTar


def norm_hash(v: str) -> str:
    v = str(v).upper().removeprefix('0X').zfill(8)
    if len(v) != 8:
        raise ValueError(v)
    int(v, 16)
    return v


def pair_stats(data: bytes, stride: int, offset: int, topn: int = 8) -> dict:
    if offset < 0 or offset + 4 > stride:
        raise ValueError((stride, offset))
    if len(data) % stride:
        raise ValueError(f'payload {len(data)} not divisible by stride {stride}')
    n = len(data) // stride
    pairs = [struct.unpack_from('<hh', data, i * stride + offset) for i in range(n)]
    bytes4 = [tuple(data[i * stride + offset:i * stride + offset + 4]) for i in range(n)]
    pc = collections.Counter(pairs)
    bc = collections.Counter(bytes4)
    sentinel = sum(1 for x, y in pairs if abs(x) in (32767, 32768) or abs(y) in (32767, 32768))
    exact_unit = sum(1 for x, y in pairs if (x, y) in ((32767, 32767), (-32767, -32767), (32767, -32767), (-32767, 32767)))
    exact_zero = pc.get((0, 0), 0)
    # snorm-ish summaries are useful for identifying multiplier-like lanes but
    # are evidence only; no semantic is inferred here.
    def sn(v: int) -> float:
        return max(-1.0, v / 32767.0)
    xs = [sn(x) for x, _ in pairs]
    ys = [sn(y) for _, y in pairs]
    return {
        'offset': offset,
        'vertex_count': n,
        'short2_unique_count': len(pc),
        'short2_top': [{'value': [x, y], 'count': c} for (x, y), c in pc.most_common(topn)],
        'ubyte4_unique_count': len(bc),
        'ubyte4_top': [{'value': list(v), 'count': c} for v, c in bc.most_common(topn)],
        'sentinel_component_vertex_count': sentinel,
        'exact_unit_pair_count': exact_unit,
        'zero_pair_count': exact_zero,
        'snorm2_bounds': {
            'min': [min(xs) if xs else None, min(ys) if ys else None],
            'max': [max(xs) if xs else None, max(ys) if ys else None],
        },
        'snorm2_mean': [sum(xs) / n if n else None, sum(ys) / n if n else None],
    }


def model_entry(tag: str, multi: MultiPackageReader, hmap: dict[str, dict]) -> tuple[dict, bytes]:
    e = hmap.get(tag)
    if e is None:
        raise KeyError(f'{tag}: absent from supplied logical views')
    if e['reference'].upper() != D1_ENTITY_MODEL_CLASS:
        raise ValueError(f'{tag}: {e["reference"]} is not D1 SEntityModel')
    return e, multi.entry(e['index'])


def occupancy_hint(stride0: int, stride1: int, uv_source: str) -> dict:
    """Document bytes already claimed by the current source-backed decoder."""
    if stride1 == 0x04:
        return {'known': [[0, 4, 'uv0']] if uv_source == 'secondary' else [], 'unresolved': []}
    if stride1 == 0x08:
        return {'known': [[0, 8, 'normal']], 'unresolved': []}
    if stride1 == 0x0C:
        return {'known': [[0, 4, 'uv0'], [4, 12, 'normal']] if uv_source == 'secondary' else [[0, 12, 'unresolved_conflict']], 'unresolved': []}
    if stride1 == 0x10:
        return {'known': [[0, 8, 'normal'], [8, 16, 'tangent']], 'unresolved': []}
    if stride1 == 0x14:
        if uv_source == 'primary':
            return {'known': [[0, 8, 'normal'], [8, 16, 'tangent']], 'unresolved': [[16, 20, 'legacy_colour_lane']]}
        return {'known': [[0, 4, 'uv0'], [4, 12, 'normal'], [12, 20, 'tangent']], 'unresolved': []}
    if stride1 == 0x18:
        if uv_source == 'primary':
            return {'known': [[0, 8, 'normal'], [8, 16, 'tangent']], 'unresolved': [[16, 24, 'legacy_colour_or_unresolved_lane']]}
        # D1 community parsers disagree about placement of the 4-byte colour-ish
        # lane in this family. Preserve the whole post-UV region as contested.
        return {'known': [[0, 4, 'uv0']], 'unresolved': [[4, 24, 'normal_tangent_plus_4byte_lane_layout_contested']]}
    return {'known': [], 'unresolved': [[0, stride1, 'unsupported_stride']]}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--model', action='append', required=True)
    ap.add_argument('--member-catalog', type=Path, action='append', required=True)
    ap.add_argument('--base-url', required=True)
    ap.add_argument('--part-count', type=int, default=10)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('-o', '--output', type=Path, required=True)
    a = ap.parse_args()

    wanted = [norm_hash(x) for x in a.model]
    if len(set(wanted)) != len(wanted):
        raise ValueError('duplicate --model')
    catalogs = load_catalogs(a.member_catalog)
    required = {filehash_pkg_index(int(x, 16))[0] for x in wanted}
    missing = sorted(required - set(catalogs))
    if missing:
        raise SystemExit('missing package catalogs: ' + ', '.join(f'{x:04X}' for x in missing))

    base = a.base_url.rstrip('/')
    arc = SplitHttpTar([f'{base}/packages.tar.{i:03d}' for i in range(1, a.part_count + 1)], retries=6, timeout=90)
    views = {pkg: RemoteLogicalPackage(arc, fam, a.runtime) for pkg, fam in sorted(catalogs.items())}
    multi = MultiPackageReader(views)
    hmap = byhash(multi)

    rows = []
    stride_pairs = collections.Counter()
    uv_sources = collections.Counter()
    for tag in wanted:
        e, b = model_entry(tag, multi, hmap)
        model = parse_model(b, 'PS4')
        mrow = {'model_tag': tag, 'source_package_id': f'{filehash_pkg_index(int(tag,16))[0]:04X}', 'meshes': []}
        for mi, mesh in enumerate(model['meshes']):
            _, h0, _, d0 = read_linked(multi, hmap, mesh['vertices1'])
            _, h1, _, d1 = read_linked(multi, hmap, mesh['vertices2'])
            s0, s1 = hdr_stride(h0), hdr_stride(h1)
            w = primary_w_mode(d0, s0)
            uv_source, uv_reason = correct_uv_source(s0, s1, w['mode'])
            stride_pairs[(s0, s1)] += 1
            uv_sources[uv_source] += 1
            lanes = [pair_stats(d1, s1, off) for off in range(0, s1 - 3, 4)]
            occ = occupancy_hint(s0, s1, uv_source)
            row = {
                'mesh_index': mi,
                'vertices1': mesh['vertices1'],
                'vertices2': mesh['vertices2'],
                'stride0': s0,
                'stride1': s1,
                'vertex_count': len(d1) // s1,
                'primary_w': w,
                'uv0_source': uv_source,
                'uv0_source_evidence': uv_reason,
                'occupancy': occ,
                'aligned_4byte_lane_stats': lanes,
            }
            mrow['meshes'].append(row)
            rows.append({'model_tag': tag, **row})
        mrow['mesh_count'] = len(mrow['meshes'])
        mrow['stride_pairs'] = collections.Counter((x['stride0'], x['stride1']) for x in mrow['meshes'])
        mrow['stride_pairs'] = {f'{a:#x}/{b:#x}': c for (a, b), c in sorted(mrow['stride_pairs'].items())}
        rows_for_model = mrow['meshes']
        print('MODEL', tag, 'meshes', len(rows_for_model), 'pairs', mrow['stride_pairs'])
        for x in rows_for_model:
            print(' MESH', x['mesh_index'], f"{x['stride0']:#x}/{x['stride1']:#x}", 'uv0', x['uv0_source'], 'verts', x['vertex_count'])
            for lo in x['occupancy']['unresolved']:
                print('  UNRESOLVED', lo)
            for lane in x['aligned_4byte_lane_stats']:
                if any(lane['offset'] >= lo[0] and lane['offset'] + 4 <= lo[1] for lo in x['occupancy']['unresolved']):
                    print('   LANE', lane['offset'], 'short2_top', lane['short2_top'][:4], 'u8_top', lane['ubyte4_top'][:4])

    report = {
        'schema': 'd1_guardian_texcoord2_lane_probe/v1',
        'model_count': len(wanted),
        'mesh_count': len(rows),
        'stride_pair_distribution': {f'{a:#x}/{b:#x}': c for (a, b), c in sorted(stride_pairs.items())},
        'uv0_source_distribution': dict(sorted(uv_sources.items())),
        'models': [],
        'meshes': rows,
        'promotion_policy': (
            'No lane is called texcoord2 by this report. Promotion requires a consistent byte offset and numeric encoding backed by Bungie vertex-layout semantics or equivalent retail shader/input evidence.'
        ),
        'bungie_web_renderer_contract': (
            'Bungie Spasm consumes a_texcoord2 as vec2 and computes v_texcoord2 = ((texcoord * a_texcoord2) * u_detail_transform.xy) + u_detail_transform.zw.'
        ),
    }
    # Avoid duplicating large rows under models; retain a compact per-model summary.
    for tag in wanted:
        ms = [x for x in rows if x['model_tag'] == tag]
        report['models'].append({
            'model_tag': tag,
            'mesh_count': len(ms),
            'stride_pairs': dict(collections.Counter(f"{x['stride0']:#x}/{x['stride1']:#x}" for x in ms)),
            'unresolved_lane_mesh_count': sum(bool(x['occupancy']['unresolved']) for x in ms),
        })
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2) + '\n')
    print('SUMMARY', json.dumps({k: v for k, v in report.items() if k not in ('meshes', 'models')}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
