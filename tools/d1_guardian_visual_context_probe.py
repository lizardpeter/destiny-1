#!/usr/bin/env python3
"""Census exact D1 Guardian UV-source and render-parent context.

This probe is intentionally non-rendering. It joins the already proven playable
Guardian model selection to two independent retail structures:

1. the D1 model-parent EntityResource, including TexturePlatesROI and external
   material banks;
2. the D1 primary/secondary vertex-stream layout used to decide which stream
   actually carries UV0.

Important D1 ROI rule for primary stride 0x0C:
  * ordinary position W -> bytes 8..11 are UV0 and W is a rigid joint index;
  * position W == +/-0x7FFF -> bytes 8..11 are two inline joints + weights,
    therefore UV0 must come from the secondary stream.

The existing generic entity-model exporter currently always asks buffer1 for
UVs on 0x04/0x0C/0x14/0x18 secondary strides. This probe reports exact meshes
where that policy disagrees with the ROI stream-pair rule before any exporter
change is made.
"""
from __future__ import annotations

import argparse
import collections
import json
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from d1_investment_arrangement_probe import filehash_pkg_index
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_investment_parent_probe import RemoteLogicalPackage
from d1_remote_model_export import MultiPackageReader, models_from_report
from d1_split_tar_extract import SplitHttpTar
from d1_entity_model_probe import parse_model
from d1_entity_model_export import byhash, read_linked, hdr_stride
from d1_render_owner_probe import parse_parent_resource

SENTINELS = {32767, -32767}


def primary_w_mode(data: bytes, stride: int) -> dict:
    if stride not in (0x08, 0x0C, 0x10, 0x1C, 0x20):
        return {'mode': 'unsupported_primary_stride', 'stride': stride}
    if stride < 8 or len(data) % stride:
        return {'mode': 'malformed_primary_stream', 'stride': stride, 'bytes': len(data)}
    ws = [struct.unpack_from('<h', data, o + 6)[0] for o in range(0, len(data), stride)]
    dist = collections.Counter(ws)
    sentinel = sum(dist[x] for x in SENTINELS)
    ordinary = len(ws) - sentinel
    if stride == 0x0C:
        if sentinel and ordinary:
            mode = 'mixed_inline2_and_primary_uv'
        elif sentinel:
            mode = 'inline2_no_primary_uv'
        else:
            mode = 'rigid_primary_uv'
    elif stride == 0x10:
        mode = 'inline4_no_primary_uv'
    elif stride == 0x08:
        mode = 'rigid_position_only'
    else:
        mode = 'non_skin_primary_layout'
    return {
        'mode': mode,
        'vertex_count': len(ws),
        'sentinel_count': sentinel,
        'ordinary_count': ordinary,
        'w_unique_count': len(dist),
        'w_min': min(ws) if ws else None,
        'w_max': max(ws) if ws else None,
    }


def correct_uv_source(s0: int, s1: int, wmode: str) -> tuple[str, str]:
    if s0 == 0x0C:
        if wmode == 'rigid_primary_uv':
            return 'primary', 'D1 0x0C ordinary-W path consumes bytes 8..11 as UV0'
        if wmode == 'mixed_inline2_and_primary_uv':
            return 'unresolved_mixed', 'mixed sentinel/non-sentinel W in one 0x0C stream requires part/shader context'
    # If primary did not establish UV0, known D1 buffer1 layouts that begin with UV0.
    if s1 in (0x04, 0x0C, 0x14, 0x18):
        return 'secondary', f'D1 buffer1 stride {s1:#x} supplies UV0 when primary UV0 is absent'
    if s1 in (0x08, 0x10):
        return 'none_in_known_pair', f'D1 buffer1 stride {s1:#x} is normal/tangent data and primary did not supply UV0'
    return 'unresolved_stride', f'unhandled D1 stream pair {s0:#x}/{s1:#x}'


def current_exporter_uv_source(s1: int) -> str:
    # tools/d1_entity_model_export.py decode_vb1 as of this probe.
    return 'secondary' if s1 in (0x04, 0x0C, 0x14, 0x18) else 'none'


def fetch_tag_bytes(tag: str, views: dict[int, RemoteLogicalPackage]) -> tuple[RemoteLogicalPackage, dict, bytes]:
    pkg, idx = filehash_pkg_index(int(tag, 16))
    view = views.get(pkg)
    if view is None:
        raise KeyError(f'{tag}: package {pkg:04X} absent from member catalogs')
    if idx >= len(view.entries):
        raise IndexError(f'{tag}: index {idx} outside package {pkg:04X}')
    e = view.entries[idx]
    if e['tag_hash'].upper() != tag.upper():
        raise ValueError(f'{tag}: logical entry mismatch {e["tag_hash"]}')
    return view, e, view.entry(idx)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--report', type=Path, required=True)
    ap.add_argument('--body-role', choices=('masculine', 'feminine'), required=True)
    ap.add_argument('--member-catalog', type=Path, action='append', required=True)
    ap.add_argument('--base-url', required=True)
    ap.add_argument('--part-count', type=int, default=10)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('-o', '--output', type=Path, required=True)
    a = ap.parse_args()

    src = json.loads(a.report.read_text())
    selected = models_from_report(src, a.body_role)
    if not selected:
        raise SystemExit('no models selected from report')

    catalogs = load_catalogs(a.member_catalog)
    base = a.base_url.rstrip('/')
    arc = SplitHttpTar([f'{base}/packages.tar.{i:03d}' for i in range(1, a.part_count + 1)], retries=6, timeout=90)
    views = {pkg: RemoteLogicalPackage(arc, fam, a.runtime) for pkg, fam in sorted(catalogs.items())}
    multi = MultiPackageReader(views)
    hmap = byhash(multi)

    models = []
    mismatch_meshes = []
    plate_headers = []
    external_materials = []
    errors = []

    for sel in selected:
        model_tag = sel['tag_hash'].upper()
        rec = {**sel, 'tag_hash': model_tag}
        try:
            # Exact render-parent context comes from the EntityResource selected by
            # the final s_entity Resource[] edge for this named body branch.
            resource_tag = str(sel.get('entity_resource_hash') or '').upper()
            if not resource_tag:
                raise ValueError('selected model lacks entity_resource_hash provenance')
            _, re, rb = fetch_tag_bytes(resource_tag, views)
            parent = parse_parent_resource(rb)
            rec['entity_resource_reference'] = re['reference'].upper()
            rec['render_parent'] = parent
            if parent is None:
                raise ValueError(f'{resource_tag}: EntityResource does not contain standard D1 model parent')
            if parent.get('embedded_model_tag_hash') != model_tag:
                raise ValueError(f'{resource_tag}: parent embeds {parent.get("embedded_model_tag_hash")}, expected {model_tag}')
            for p in parent.get('texture_plates_roi_entries', []):
                h = p['texture_plate_header_tag_hash'].upper()
                if h not in plate_headers:
                    plate_headers.append(h)
            for h in parent.get('external_material_tag_hashes', []):
                if h not in external_materials:
                    external_materials.append(h)

            me = hmap.get(model_tag)
            if me is None:
                raise KeyError(f'{model_tag}: model absent from multi-package view')
            mb = multi.entry(me['index'])
            model = parse_model(mb, 'PS4')
            meshes = []
            for mi, mesh in enumerate(model['meshes']):
                _, _, _, v1d = read_linked(multi, hmap, mesh['vertices1'])
                _, v1h, _, _ = read_linked(multi, hmap, mesh['vertices1'])
                _, v2h, _, _ = read_linked(multi, hmap, mesh['vertices2'])
                s0, s1 = hdr_stride(v1h), hdr_stride(v2h)
                wm = primary_w_mode(v1d, s0)
                correct, reason = correct_uv_source(s0, s1, wm['mode'])
                current = current_exporter_uv_source(s1)
                mismatch = correct in ('primary', 'secondary') and current != correct
                mrow = {
                    'mesh_index': mi,
                    'vertices1': mesh['vertices1'],
                    'vertices2': mesh['vertices2'],
                    'stride0': s0,
                    'stride1': s1,
                    'primary_w': wm,
                    'correct_uv_source': correct,
                    'uv_source_evidence': reason,
                    'current_generic_exporter_uv_source': current,
                    'current_exporter_mismatch': mismatch,
                    'texcoord_scale': mesh['texcoord_scale'],
                    'texcoord_translation': mesh['texcoord_translation'],
                }
                meshes.append(mrow)
                if mismatch:
                    mismatch_meshes.append({'model_tag': model_tag, **mrow})
            rec['meshes'] = meshes
            rec['mesh_count'] = len(meshes)
        except Exception as ex:
            rec['error'] = repr(ex)
            errors.append({'model_tag': model_tag, 'error': repr(ex)})
        models.append(rec)

    uv_counts = collections.Counter()
    mode_counts = collections.Counter()
    for m in models:
        for x in m.get('meshes', []):
            uv_counts[x['correct_uv_source']] += 1
            mode_counts[x['primary_w']['mode']] += 1

    report = {
        'schema': 'd1_guardian_visual_context_probe/v1',
        'body_role': a.body_role,
        'model_count': len(models),
        'mesh_count': sum(len(x.get('meshes', [])) for x in models),
        'uv_source_counts': dict(uv_counts),
        'primary_mode_counts': dict(mode_counts),
        'current_exporter_uv_mismatch_count': len(mismatch_meshes),
        'texture_plate_header_tags': plate_headers,
        'texture_plate_header_count': len(plate_headers),
        'external_material_tag_hashes': external_materials,
        'external_material_count': len(external_materials),
        'models': models,
        'mismatch_meshes': mismatch_meshes,
        'errors': errors,
        'policy': (
            'Model selection and EntityResource ownership come from the prior byte-proven playable Guardian graph. '
            'UV source is classified from D1 ROI primary-W and stream-stride rules. Mixed or unknown layouts are '
            'reported unresolved rather than guessed. Texture-plate and external-material hashes are read only from '
            'the exact standard model parent embedded in the selected EntityResource.'
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k not in ('models', 'mismatch_meshes', 'errors')}, indent=2))
    for m in models:
        ex = (m.get('examples') or [{}])[0]
        print('\nMODEL', ex.get('name'), m['tag_hash'], 'resource', m.get('entity_resource_hash'))
        rp = m.get('render_parent') or {}
        print(' plates', [x.get('texture_plate_header_tag_hash') for x in rp.get('texture_plates_roi_entries', [])],
              'external_materials', len(rp.get('external_material_tag_hashes', [])))
        for x in m.get('meshes', []):
            print(' mesh', x['mesh_index'], f"{x['stride0']:#x}/{x['stride1']:#x}", x['primary_w']['mode'],
                  'uv=', x['correct_uv_source'], 'generic=', x['current_generic_exporter_uv_source'],
                  'MISMATCH' if x['current_exporter_mismatch'] else '')
    if errors:
        raise SystemExit(f'{len(errors)} model(s) failed visual-context resolution')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
