#!/usr/bin/env python3
"""Follow D1 Guardian stage-part material -> PS4 vertex-shader ownership.

This probe starts from an explicit, already-proven set of D1 SEntityModel
FileHashes.  For every mesh it preserves the exact stage-part material hashes,
reads each resident ROI material, extracts its serialized VertexShader FileHash
at +0x28, and follows that shader header to its native Orbis payload when the
verified package catalogs contain the required hashes.

The goal is not to infer material semantics.  It is to compare native PS4
vertex-shader families against the independently observed secondary-stream
half2 texcoord2 candidate.  Missing packages are reported by exact Tiger
package id rather than guessed from filenames.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from d1_entity_model_export import byhash, hdr_stride, read_linked
from d1_entity_model_probe import D1_ENTITY_MODEL_CLASS, parse_model
from d1_guardian_texcoord2_lane_probe import candidate_offset
from d1_guardian_visual_context_probe import primary_w_mode, correct_uv_source
from d1_investment_arrangement_probe import filehash_pkg_index
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_ps4_shader_binary_probe import find_footer, parse_binary_info, parse_usage
from d1_remote_investment_parent_probe import RemoteLogicalPackage
from d1_remote_model_export import MultiPackageReader
from d1_split_tar_extract import SplitHttpTar

PS4_MATERIAL_CLASS = '80801AD7'


def u32(b: bytes, o: int) -> int:
    if o < 0 or o + 4 > len(b):
        raise ValueError(f'u32 out of bounds 0x{o:X}/0x{len(b):X}')
    return struct.unpack_from('<I', b, o)[0]


def h32(v: int) -> str:
    return f'{v & 0xFFFFFFFF:08X}'


def norm_hash(v: str) -> str:
    v = str(v).upper().removeprefix('0X').zfill(8)
    if len(v) != 8:
        raise ValueError(v)
    int(v, 16)
    return v


def entry_desc(e: dict | None) -> dict | None:
    if e is None:
        return None
    return {
        'tag_hash': e['tag_hash'].upper(),
        'reference': e['reference'].upper(),
        'type': e['type'],
        'subtype': e['subtype'],
        'declared_file_size': e['file_size'],
        'source_package_id': f"{int(e.get('_source_package_id')):04X}" if e.get('_source_package_id') is not None else None,
        'source_file_index': e.get('_source_file_index'),
    }


def required_pkg(tag: str) -> str:
    return f'{filehash_pkg_index(int(tag, 16))[0]:04X}'


def native_shader_info(payload: bytes) -> dict:
    footer, checks = find_footer(payload)
    row = {
        'payload_size': len(payload),
        'payload_sha256': hashlib.sha256(payload).hexdigest(),
        'orbshdr_locator': checks,
        'prefix_32': payload[:32].hex(),
        'suffix_64': payload[-64:].hex(),
    }
    if footer is None:
        row['orbshdr_resolved'] = False
        return row
    info = parse_binary_info(payload, footer)
    row['orbshdr_resolved'] = True
    row['binary_info'] = info
    row['code_sha256'] = hashlib.sha256(payload[:info['code_length_bytes']]).hexdigest()
    row['bytes_between_code_and_footer'] = footer - info['code_length_bytes']
    row['metadata_between_code_and_footer_hex'] = payload[info['code_length_bytes']:footer].hex()
    try:
        row['usage'] = parse_usage(payload, footer, info)
    except Exception as ex:
        row['usage_error'] = repr(ex)
    return row


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
    required_models = {filehash_pkg_index(int(x, 16))[0] for x in wanted}
    missing_models = sorted(required_models - set(catalogs))
    if missing_models:
        raise SystemExit('missing model package catalogs: ' + ', '.join(f'{x:04X}' for x in missing_models))

    base = a.base_url.rstrip('/')
    arc = SplitHttpTar([f'{base}/packages.tar.{i:03d}' for i in range(1, a.part_count + 1)], retries=6, timeout=90)
    views = {pkg: RemoteLogicalPackage(arc, fam, a.runtime) for pkg, fam in sorted(catalogs.items())}
    multi = MultiPackageReader(views)
    hmap = byhash(multi)

    mesh_rows = []
    material_users: dict[str, list[dict]] = collections.defaultdict(list)
    for tag in wanted:
        me = hmap.get(tag)
        if me is None or me['reference'].upper() != D1_ENTITY_MODEL_CLASS:
            raise ValueError(f'{tag}: exact D1 model not present in supplied views')
        model = parse_model(multi.entry(me['index']), 'PS4')
        for mi, mesh in enumerate(model['meshes']):
            _, h0, _, d0 = read_linked(multi, hmap, mesh['vertices1'])
            _, h1, _, _ = read_linked(multi, hmap, mesh['vertices2'])
            s0, s1 = hdr_stride(h0), hdr_stride(h1)
            wm = primary_w_mode(d0, s0)
            uv0_source, uv0_reason = correct_uv_source(s0, s1, wm['mode'])
            t2off = candidate_offset(s1, uv0_source)
            mats = sorted({p['material'].upper() for p in mesh['parts'] if p['material'].upper() not in ('00000000', 'FFFFFFFF')})
            row = {
                'model_tag': tag,
                'mesh_index': mi,
                'stride0': s0,
                'stride1': s1,
                'uv0_source': uv0_source,
                'uv0_source_evidence': uv0_reason,
                'texcoord2_half2_candidate': t2off is not None,
                'texcoord2_candidate_offset': t2off,
                'stage_part_count': mesh['part_count'],
                'material_hashes': mats,
            }
            mesh_rows.append(row)
            for m in mats:
                material_users[m].append({
                    'model_tag': tag,
                    'mesh_index': mi,
                    'stride0': s0,
                    'stride1': s1,
                    'texcoord2_half2_candidate': t2off is not None,
                })

    unresolved_pkg_ids: set[str] = set()
    materials = []
    vs_users: dict[str, list[str]] = collections.defaultdict(list)
    for tag in sorted(material_users):
        e = hmap.get(tag)
        rec = {
            'material_hash': tag,
            'users': material_users[tag],
            'texcoord2_candidate_usage_values': sorted({bool(x['texcoord2_half2_candidate']) for x in material_users[tag]}),
            'required_package_id': required_pkg(tag),
        }
        if e is None:
            unresolved_pkg_ids.add(required_pkg(tag))
            rec['resolved'] = False
            rec['error'] = 'material FileHash absent from supplied logical views'
            materials.append(rec)
            continue
        rec['entry'] = entry_desc(e)
        if e['reference'].upper() != PS4_MATERIAL_CLASS:
            rec['resolved'] = False
            rec['error'] = f"entry reference {e['reference'].upper()} != ROI material {PS4_MATERIAL_CLASS}"
            materials.append(rec)
            continue
        try:
            b = multi.entry(e['index'])
            rec['material_payload_size'] = len(b)
            rec['material_payload_sha256'] = hashlib.sha256(b).hexdigest()
            vs = h32(u32(b, 0x28))
            rec['vertex_shader_hash'] = vs
            rec['vertex_shader_required_package_id'] = required_pkg(vs) if vs not in ('00000000', 'FFFFFFFF') else None
            rec['resolved'] = True
            if vs not in ('00000000', 'FFFFFFFF'):
                vs_users[vs].append(tag)
        except Exception as ex:
            rec['resolved'] = False
            rec['error'] = repr(ex)
        materials.append(rec)

    vertex_shaders = []
    for tag in sorted(vs_users):
        e = hmap.get(tag)
        rec = {
            'vertex_shader_hash': tag,
            'material_hashes': sorted(set(vs_users[tag])),
            'required_package_id': required_pkg(tag),
        }
        use_flags = set()
        for mh in rec['material_hashes']:
            for u in material_users[mh]:
                use_flags.add(bool(u['texcoord2_half2_candidate']))
        rec['texcoord2_candidate_usage_values'] = sorted(use_flags)
        if e is None:
            unresolved_pkg_ids.add(required_pkg(tag))
            rec['resolved_header'] = False
            rec['error'] = 'vertex-shader FileHash absent from supplied logical views'
            vertex_shaders.append(rec)
            continue
        rec['header_entry'] = entry_desc(e)
        rec['resolved_header'] = True
        try:
            hb = multi.entry(e['index'])
            rec['header_payload_size'] = len(hb)
            rec['header_payload_sha256'] = hashlib.sha256(hb).hexdigest()
            native_tag = e['reference'].upper()
            rec['native_shader_hash'] = native_tag
            rec['native_shader_required_package_id'] = required_pkg(native_tag)
            ne = hmap.get(native_tag)
            if ne is None:
                unresolved_pkg_ids.add(required_pkg(native_tag))
                rec['resolved_native'] = False
                rec['native_error'] = 'native shader payload FileHash absent from supplied logical views'
            else:
                rec['native_entry'] = entry_desc(ne)
                nb = multi.entry(ne['index'])
                rec['resolved_native'] = True
                rec['native_shader'] = native_shader_info(nb)
        except Exception as ex:
            rec['resolved_native'] = False
            rec['native_error'] = repr(ex)
        vertex_shaders.append(rec)

    mat_resolved = sum(bool(x.get('resolved')) for x in materials)
    vs_header_resolved = sum(bool(x.get('resolved_header')) for x in vertex_shaders)
    vs_native_resolved = sum(bool(x.get('resolved_native')) for x in vertex_shaders)
    stage_counts = collections.Counter()
    for v in vertex_shaders:
        st = ((v.get('native_shader') or {}).get('binary_info') or {}).get('stage')
        if st:
            stage_counts[st] += 1

    report = {
        'schema': 'd1_guardian_material_vs_census/v1',
        'model_count': len(wanted),
        'mesh_count': len(mesh_rows),
        'distinct_material_count': len(materials),
        'resolved_material_count': mat_resolved,
        'distinct_vertex_shader_count': len(vertex_shaders),
        'resolved_vertex_shader_header_count': vs_header_resolved,
        'resolved_native_vertex_shader_count': vs_native_resolved,
        'native_shader_stage_distribution': dict(stage_counts),
        'unresolved_package_ids': sorted(unresolved_pkg_ids),
        'meshes': mesh_rows,
        'materials': materials,
        'vertex_shaders': vertex_shaders,
        'policy': (
            'Material hashes come only from exact retail D1 SEntityModel stage parts. VertexShader comes only from ROI material +0x28. Native shader ownership comes only from the exact vertex-shader FileEntry.Reference. No shader/material identity is inferred from adjacency or names.'
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2) + '\n')
    print('MODELS', report['model_count'], 'MESHES', report['mesh_count'])
    print('MATERIALS', len(materials), 'resolved', mat_resolved)
    print('VERTEX_SHADERS', len(vertex_shaders), 'headers', vs_header_resolved, 'native', vs_native_resolved)
    print('STAGES', dict(stage_counts))
    print('UNRESOLVED_PACKAGES', report['unresolved_package_ids'])
    for v in vertex_shaders:
        ni = (v.get('native_shader') or {}).get('binary_info') or {}
        print('VS', v['vertex_shader_hash'], 'materials', len(v['material_hashes']),
              'texcoord2_usage', v['texcoord2_candidate_usage_values'],
              'native', v.get('native_shader_hash'), 'stage', ni.get('stage'),
              'usage_slots', ni.get('num_input_usage_slots'),
              'code', (v.get('native_shader') or {}).get('code_sha256'))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
