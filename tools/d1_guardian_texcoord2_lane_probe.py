#!/usr/bin/env python3
"""Probe D1 Guardian secondary vertex-stream lanes for Bungie a_texcoord2.

The archived Bungie D1 web renderer consumes a semantic named `texcoord2` as a
vec2 and computes:

    detail_uv = (base_uv * texcoord2) * detail_transform.xy
                + detail_transform.zw

Our retail PKG parser already source-closes position, UV0, normal, tangent and
skinning for the Spektar proof.  Community D1 parsers have historically called
the final 4-byte lane in several secondary layouts "colour" or unresolved.  The
first raw census showed those bytes form values such as 0x4400/0x4800; those are
4.0/8.0 when decoded as IEEE binary16.

This v2 census therefore records every 4-byte aligned lane simultaneously as
short2, ubyte4 and half2, and applies one deliberately narrow *candidate* rule:

  * stride1 0x14 with UV0 already in the primary stream -> final half2 @ 0x10
  * stride1 0x18 -> final half2 @ 0x14
  * all other stream pairs -> no texcoord2 candidate

A candidate passes only when every component is finite, strictly positive and
<= 64.0.  Passing this probe is still evidence, not semantic promotion: the
native PS4 vertex-shader/input-signature path must be checked independently
before the generic exporter calls the lane TEXCOORD_1.
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
    halfs = [struct.unpack_from('<ee', data, i * stride + offset) for i in range(n)]
    pc = collections.Counter(pairs)
    bc = collections.Counter(bytes4)
    hc = collections.Counter(halfs)
    sentinel = sum(1 for x, y in pairs if abs(x) in (32767, 32768) or abs(y) in (32767, 32768))
    exact_unit = sum(1 for x, y in pairs if (x, y) in ((32767, 32767), (-32767, -32767), (32767, -32767), (-32767, 32767)))
    exact_zero = pc.get((0, 0), 0)

    def sn(v: int) -> float:
        return max(-1.0, v / 32767.0)

    xs = [sn(x) for x, _ in pairs]
    ys = [sn(y) for _, y in pairs]
    finite_halfs = [(float(x), float(y)) for x, y in halfs if math.isfinite(x) and math.isfinite(y)]
    positive_halfs = [(x, y) for x, y in finite_halfs if x > 0.0 and y > 0.0]
    plausible_halfs = [(x, y) for x, y in positive_halfs if x <= 64.0 and y <= 64.0]
    hx = [x for x, _ in finite_halfs]
    hy = [y for _, y in finite_halfs]
    return {
        'offset': offset,
        'vertex_count': n,
        'short2_unique_count': len(pc),
        'short2_top': [{'value': [x, y], 'count': c} for (x, y), c in pc.most_common(topn)],
        'ubyte4_unique_count': len(bc),
        'ubyte4_top': [{'value': list(v), 'count': c} for v, c in bc.most_common(topn)],
        'half2_unique_count': len(hc),
        'half2_top': [{'value': [float(x), float(y)], 'count': c} for (x, y), c in hc.most_common(topn)],
        'half2_finite_vertex_count': len(finite_halfs),
        'half2_positive_vertex_count': len(positive_halfs),
        'half2_plausible_0_to_64_vertex_count': len(plausible_halfs),
        'half2_bounds_finite': {
            'min': [min(hx) if hx else None, min(hy) if hy else None],
            'max': [max(hx) if hx else None, max(hy) if hy else None],
        },
        'sentinel_component_vertex_count': sentinel,
        'exact_unit_pair_count': exact_unit,
        'zero_pair_count': exact_zero,
        'snorm2_bounds': {
            'min': [min(xs) if xs else None, min(ys) if ys else None],
            'max': [max(xs) if xs else None, max(ys) if ys else None],
        },
        'snorm2_mean': [sum(xs) / n if n else None, sum(ys) / n if n else None],
    }


def candidate_offset(stride1: int, uv_source: str) -> int | None:
    if stride1 == 0x14 and uv_source == 'primary':
        return 0x10
    if stride1 == 0x18:
        return 0x14
    return None


def candidate_result(lanes: list[dict], stride1: int, uv_source: str) -> dict:
    off = candidate_offset(stride1, uv_source)
    if off is None:
        return {
            'candidate_present': False,
            'candidate_offset': None,
            'candidate_encoding': None,
            'candidate_valid': None,
            'reason': 'stream family has no spare final half2 lane under the conservative rule',
        }
    lane = next((x for x in lanes if x['offset'] == off), None)
    if lane is None:
        return {
            'candidate_present': True,
            'candidate_offset': off,
            'candidate_encoding': 'IEEE754_binary16x2_little_endian',
            'candidate_valid': False,
            'reason': 'expected aligned lane absent',
        }
    n = lane['vertex_count']
    valid = (
        lane['half2_finite_vertex_count'] == n and
        lane['half2_positive_vertex_count'] == n and
        lane['half2_plausible_0_to_64_vertex_count'] == n
    )
    return {
        'candidate_present': True,
        'candidate_offset': off,
        'candidate_encoding': 'IEEE754_binary16x2_little_endian',
        'candidate_valid': valid,
        'vertex_count': n,
        'finite_vertex_count': lane['half2_finite_vertex_count'],
        'positive_vertex_count': lane['half2_positive_vertex_count'],
        'plausible_0_to_64_vertex_count': lane['half2_plausible_0_to_64_vertex_count'],
        'half2_bounds_finite': lane['half2_bounds_finite'],
        'half2_top': lane['half2_top'],
        'reason': (
            'all candidate half2 components are finite, positive and <= 64'
            if valid else
            'candidate half2 contains non-finite, non-positive or >64 component(s)'
        ),
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
            return {'known': [[0, 8, 'normal'], [8, 16, 'tangent']], 'unresolved': [[16, 20, 'half2_texcoord2_candidate']]}
        return {'known': [[0, 4, 'uv0'], [4, 12, 'normal'], [12, 20, 'tangent']], 'unresolved': []}
    if stride1 == 0x18:
        if uv_source == 'primary':
            return {'known': [[0, 8, 'normal'], [8, 16, 'tangent']], 'unresolved': [[16, 20, 'other_4byte_lane'], [20, 24, 'half2_texcoord2_candidate']]}
        return {'known': [[0, 4, 'uv0']], 'unresolved': [[4, 20, 'normal_tangent_plus_other_4byte_layout_contested'], [20, 24, 'half2_texcoord2_candidate']]}
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
        _, b = model_entry(tag, multi, hmap)
        model = parse_model(b, 'PS4')
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
            cand = candidate_result(lanes, s1, uv_source)
            row = {
                'model_tag': tag,
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
                'texcoord2_candidate': cand,
                'aligned_4byte_lane_stats': lanes,
            }
            rows.append(row)
            print('MESH', tag, mi, f'{s0:#x}/{s1:#x}', 'uv0', uv_source,
                  'verts', row['vertex_count'], 'texcoord2', cand)

    candidates = [x for x in rows if x['texcoord2_candidate']['candidate_present']]
    valid_candidates = [x for x in candidates if x['texcoord2_candidate']['candidate_valid']]
    invalid_candidates = [x for x in candidates if not x['texcoord2_candidate']['candidate_valid']]
    report = {
        'schema': 'd1_guardian_texcoord2_lane_probe/v2',
        'model_count': len(wanted),
        'mesh_count': len(rows),
        'stride_pair_distribution': {f'{a:#x}/{b:#x}': c for (a, b), c in sorted(stride_pairs.items())},
        'uv0_source_distribution': dict(sorted(uv_sources.items())),
        'texcoord2_candidate_mesh_count': len(candidates),
        'texcoord2_valid_candidate_mesh_count': len(valid_candidates),
        'texcoord2_invalid_candidate_mesh_count': len(invalid_candidates),
        'texcoord2_absent_candidate_mesh_count': len(rows) - len(candidates),
        'texcoord2_candidate_stride_distribution': dict(collections.Counter(f"{x['stride0']:#x}/{x['stride1']:#x}" for x in candidates)),
        'models': [],
        'meshes': rows,
        'invalid_candidates': [
            {'model_tag': x['model_tag'], 'mesh_index': x['mesh_index'], **x['texcoord2_candidate']}
            for x in invalid_candidates
        ],
        'promotion_policy': (
            'A final 4-byte lane is only a texcoord2 candidate here. Passing the half2 numeric test is necessary but not sufficient; native PS4 material/vertex-shader input evidence is required before the generic exporter promotes it.'
        ),
        'bungie_web_renderer_contract': (
            'Bungie Spasm consumes a_texcoord2 as vec2 and computes v_texcoord2 = ((texcoord * a_texcoord2) * u_detail_transform.xy) + u_detail_transform.zw.'
        ),
    }
    for tag in wanted:
        ms = [x for x in rows if x['model_tag'] == tag]
        cs = [x for x in ms if x['texcoord2_candidate']['candidate_present']]
        report['models'].append({
            'model_tag': tag,
            'mesh_count': len(ms),
            'stride_pairs': dict(collections.Counter(f"{x['stride0']:#x}/{x['stride1']:#x}" for x in ms)),
            'texcoord2_candidate_mesh_count': len(cs),
            'texcoord2_valid_candidate_mesh_count': sum(bool(x['texcoord2_candidate']['candidate_valid']) for x in cs),
        })
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2) + '\n')
    print('SUMMARY', json.dumps({k: v for k, v in report.items() if k not in ('meshes', 'models', 'invalid_candidates')}, indent=2))
    if invalid_candidates:
        raise SystemExit(f'{len(invalid_candidates)} texcoord2 candidate mesh(es) failed half2 validation')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
