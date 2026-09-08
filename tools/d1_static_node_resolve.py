#!/usr/bin/env python3
"""Resolve an exported D1 static node name back to exact source records.

The retail-visible static exporter names nodes as:

    <StaticTableHash>_info<InfoIndex>_xform<TransformIndex>

Given the generic baked-validation document, this tool resolves that portable node
identity to the exact StaticTable info row, mesh entry, material TagHash, transform
range, and serialized geometry resource FileHashes.  No GLB inspection or visual
heuristic is used.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

NODE_RE = re.compile(r'^(?P<table>[0-9A-Fa-f]{8})_info(?P<info>\d+)_xform(?P<xform>\d+)$')


def norm(x) -> str:
    return str(x).upper().removeprefix('0X').zfill(8)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--validation-json', type=Path, required=True)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--node', help='exported node, e.g. 810B197B_info129_xform114')
    g.add_argument('--table-hash')
    ap.add_argument('--info-index', type=int)
    ap.add_argument('--transform-index', type=int)
    ap.add_argument('-o', '--out', type=Path, required=True)
    a = ap.parse_args()

    if a.node:
        m = NODE_RE.match(a.node)
        if not m:
            raise SystemExit('node does not match <8hex>_infoN_xformN')
        table_hash = norm(m.group('table'))
        info_index = int(m.group('info'))
        transform_index = int(m.group('xform'))
    else:
        if a.info_index is None:
            raise SystemExit('--info-index is required with --table-hash')
        table_hash = norm(a.table_hash)
        info_index = int(a.info_index)
        transform_index = a.transform_index

    doc = json.loads(a.validation_json.read_text())
    d1_rows = doc.get('static_map_data_d1') or []
    matches = []
    for cell in d1_rows:
        for table in cell.get('static_tables') or []:
            if norm(table.get('hash')) != table_hash:
                continue
            infos = table.get('info_entries') or []
            info = next((x for x in infos if int(x.get('index', -1)) == info_index), None)
            if info is None:
                matches.append({'cell': cell, 'table': table, 'error': f'info index {info_index} absent'})
                continue
            static_index = int(info['static_index'])
            material_index = int(info['material_index'])
            meshes = table.get('mesh_entries') or []
            materials = table.get('material_hashes') or []
            if static_index < 0 or static_index >= len(meshes):
                raise SystemExit(f'{table_hash}/info{info_index}: static_index {static_index} outside mesh_entries {len(meshes)}')
            if material_index < 0 or material_index >= len(materials):
                raise SystemExit(f'{table_hash}/info{info_index}: material_index {material_index} outside material_hashes {len(materials)}')
            mesh = meshes[static_index]
            start = int(info['transform_index'])
            count = int(info['instance_count'])
            end = start + count
            selected_xform = None
            if transform_index is not None:
                if not (start <= transform_index < end):
                    raise SystemExit(f'{table_hash}/info{info_index}: xform {transform_index} not in [{start},{end})')
                selected_xform = transform_index
            matches.append({
                'd1_static_map_data': norm(cell.get('hash')),
                'table_hash': table_hash,
                'info_index': info_index,
                'info': info,
                'static_index': static_index,
                'material_index': material_index,
                'material_hash': norm(materials[material_index]),
                'mesh': mesh,
                'transform_range': [start, end],
                'selected_transform_index': selected_xform,
            })

    good = [x for x in matches if 'error' not in x]
    if len(good) != 1:
        raise SystemExit(f'expected exactly one source mapping, got {len(good)} good / {len(matches)} table matches')
    r = good[0]
    mesh = r['mesh']
    out = {
        'schema_version': 1,
        'status': 'D1_STATIC_NODE_SOURCE_RESOLVED',
        'requested_node': a.node,
        'table_hash': r['table_hash'],
        'info_index': r['info_index'],
        'selected_transform_index': r['selected_transform_index'],
        'd1_static_map_data': r['d1_static_map_data'],
        'static_index': r['static_index'],
        'material_index': r['material_index'],
        'material_hash': r['material_hash'],
        'detail_level': int(mesh.get('detail_level', -1)),
        'mesh_resources': {
            'vertices0': norm(mesh.get('vertices0')),
            'vertices1': norm(mesh.get('vertices1')),
            'indices': norm(mesh.get('indices')),
            'index_offset': int(mesh.get('index_offset', 0)),
            'index_count': int(mesh.get('index_count', 0)),
            'primitive_type': int(mesh.get('primitive_type', 0)),
        },
        'transform_range': r['transform_range'],
        'source_info_entry': r['info'],
        'policy': 'Exact validation/source-table resolution only; no appearance-based inference.',
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps(out, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
