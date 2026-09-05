#!/usr/bin/env python3
"""D1 Tower map schema validator v2: permit the shipped null Vertices1 sentinel.

This is a narrow correction layered over d1_tower_map_schema_validate.py.
The original validator treated every StaticMesh Vertices0/Vertices1/Indices FileHash
as mandatory. Retail D1 baked-static records use FFFFFFFF specifically for an absent
secondary vertex/UV stream. This is independently corroborated by the archived D1
MontevenDynamicExtractor, whose Static parser only constructs vertUVFile when
UVHash != "ffffffff".

Safety boundary:
- Vertices0 remains mandatory.
- Indices remains mandatory.
- Vertices1 is optional only when exactly FFFFFFFF.
- Any other unresolved Vertices1 remains a violation.
- No semantic ownership or LOD rule is changed.

The patch keeps the legacy `all_targets_exist` / `all_mesh_targets_exist` keys but
redefines them to mean "all required targets exist", so existing strict workflows can
consume the corrected report without silently weakening V0/index checks.
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import d1_tower_map_schema_validate as base

NULL_FILEHASH = 'FFFFFFFF'


def parse_static_table_v2(c: base.Corpus, h: str, instance_total=None):
    b, src = c.payload(h)
    if b is None:
        return {'hash': h, 'ok': False, 'error': 'payload_unavailable'}
    mats = base.dyn(b, 0x08, 0x08)
    meshes = base.dyn(b, 0x18, 0x18)
    infos = base.dyn(b, 0x28, 0x18)
    rep = {
        'hash': h,
        'source': src,
        'payload_size': len(b),
        'arrays': {'materials': mats, 'meshes': meshes, 'infos': infos},
        'ok': all(x['ok'] for x in (mats, meshes, infos)),
        'mesh_entries': [],
        'info_entries': [],
        'violations': [],
        'validator_revision': 'v2_optional_vertices1_null_sentinel',
    }
    if not rep['ok']:
        rep['violations'].append('dynamic_array_bounds')
        return rep

    material_hashes = []
    for i in range(mats['count']):
        o = mats['absolute'] + i * 8
        material_hashes.append(base.hx(base.u32(b, o + 4)))
    rep['material_hashes'] = material_hashes

    for i in range(meshes['count']):
        o = meshes['absolute'] + i * 0x18
        v0, v1, ind = (base.hx(base.u32(b, o + j)) for j in (0, 4, 8))
        v1_null = v1 == NULL_FILEHASH
        targets = {
            'vertices0': c.entry_meta(v0),
            'vertices1': None if v1_null else c.entry_meta(v1),
            'indices': c.entry_meta(ind),
        }
        row = {
            'index': i,
            'vertices0': v0,
            'vertices1': v1,
            'indices': ind,
            'vertices1_is_null_sentinel': v1_null,
            'unk0C': base.u16(b, o + 0xC),
            'detail_level': struct.unpack_from('<b', b, o + 0xE)[0],
            'primitive_type': struct.unpack_from('<b', b, o + 0xF)[0],
            'index_offset': base.u32(b, o + 0x10),
            'index_count': base.u32(b, o + 0x14),
            'targets': targets,
        }
        row['required_targets_exist'] = bool(
            targets['vertices0'] is not None and
            targets['indices'] is not None and
            (v1_null or targets['vertices1'] is not None)
        )
        # Compatibility key: now explicitly means every required concrete target.
        row['all_targets_exist'] = row['required_targets_exist']
        ints = [int(v0, 16), int(v1, 16), int(ind, 16)]
        row['consecutive_filehash_triple'] = bool(
            not v1_null and ints[1] == ints[0] + 1 and ints[2] == ints[1] + 1
        )
        rep['mesh_entries'].append(row)
        if not row['required_targets_exist']:
            missing = []
            if targets['vertices0'] is None:
                missing.append(f'vertices0={v0}')
            if not v1_null and targets['vertices1'] is None:
                missing.append(f'vertices1={v1}')
            if targets['indices'] is None:
                missing.append(f'indices={ind}')
            rep['violations'].append(f"mesh[{i}] unresolved required buffer target(s): {', '.join(missing)}")

    for i in range(infos['count']):
        o = infos['absolute'] + i * 0x18
        ic = base.i16(b, o)
        mi = base.i16(b, o + 4)
        si = base.i16(b, o + 8)
        ti = base.i16(b, o + 0xA)
        row = {
            'index': i,
            'instance_count': ic,
            'material_index': mi,
            'static_index': si,
            'transform_index': ti,
            'material_in_bounds': 0 <= mi < mats['count'],
            'static_in_bounds': 0 <= si < meshes['count'],
            'transform_in_bounds': instance_total is None or (
                ic >= 0 and ti >= 0 and ti + ic <= instance_total
            ),
        }
        row['all_indices_in_bounds'] = (
            row['material_in_bounds'] and row['static_in_bounds'] and row['transform_in_bounds']
        )
        rep['info_entries'].append(row)
        if not row['all_indices_in_bounds']:
            rep['violations'].append(f'info[{i}] index bounds')

    null_v1_count = sum(x['vertices1_is_null_sentinel'] for x in rep['mesh_entries'])
    rep['summary'] = {
        'materials': mats['count'],
        'meshes': meshes['count'],
        'infos': infos['count'],
        'all_mesh_targets_exist': all(x['required_targets_exist'] for x in rep['mesh_entries']),
        'all_required_mesh_targets_exist': all(x['required_targets_exist'] for x in rep['mesh_entries']),
        'null_vertices1_sentinel_records': null_v1_count,
        'consecutive_mesh_triples': sum(x['consecutive_filehash_triple'] for x in rep['mesh_entries']),
        'all_info_indices_in_bounds': all(x['all_indices_in_bounds'] for x in rep['info_entries']),
    }
    rep['ok'] = rep['ok'] and not rep['violations']
    return rep


# validate_static_data_d1 resolves this module-global function on the imported base
# module at runtime, so patch it before entering the unmodified CLI/main traversal.
base.parse_static_table = parse_static_table_v2

if __name__ == '__main__':
    raise SystemExit(base.main())
