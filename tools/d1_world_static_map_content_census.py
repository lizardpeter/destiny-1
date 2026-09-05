#!/usr/bin/env python3
"""Classify every closed D1 static-map resource by actual baked-static content.

Input is the loss-preserving resource-chain report produced by
`d1_world_static_map_resource_chain_census.py`.  For every unique
SStaticMapData/808008B4 target this tool follows +0x30 to D1 static data
(80801B75), validates the static tables with the existing binary validator, and
applies the exact retail GetStatics visibility gate without exporting geometry:

    DetailLevel in {0,1,2,3,10} AND material.Unk08 == 1

This is intentionally a census, not an exporter.  It answers the key world-
closure question: which map resources actually contain renderable baked statics,
which are empty/nonvisual, and how many exact placements they contribute.

Safety:
- current class-stable/sized Tiger reader only;
- material class must be 80801AD7 before Unk08 is read at +0x08;
- unresolved material state is reported and prevents `visual_selection_complete`;
- no geometry, LOD, material role, or ownership is guessed.
"""
from __future__ import annotations

import argparse, json, struct, sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import d1_tower_map_schema_validate_v5 as v5

STATIC_MAP_DATA = '808008B4'
D1_STATIC_MAP_DATA = '80801B75'
MATERIAL_CLASS = '80801AD7'
ALLOWED_DETAIL = {0, 1, 2, 3, 10}


def norm(x):
    return str(x).upper().removeprefix('0X').zfill(8)


def u32(b, o):
    return struct.unpack_from('<I', b, o)[0]


def hx(x):
    return f'{x:08X}'


def material_state(c, cache, h):
    h = norm(h)
    if h in cache:
        return cache[h]
    meta = c.entry_meta(h)
    b, src = c.payload(h)
    row = {'hash': h, 'meta': meta, 'source': src, 'unk08': None, 'visual': None}
    if not meta:
        row['error'] = 'material_missing'
    elif norm(meta.get('reference', '')) != MATERIAL_CLASS:
        row['error'] = f'material_class_{norm(meta.get("reference", ""))}_not_{MATERIAL_CLASS}'
    elif b is None or len(b) < 0x0C:
        row['error'] = 'material_payload_unavailable_or_short'
    else:
        row['unk08'] = u32(b, 0x08)
        row['visual'] = row['unk08'] == 1
    cache[h] = row
    return row


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--snapshot', type=Path, action='append', required=True)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('--chain-json', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()

    chain = json.loads(a.chain_json.read_text())
    if chain.get('closed_chain_count') != chain.get('entry_count'):
        raise SystemExit('resource-chain input is not fully closed')

    static_maps = sorted({
        norm(r['static_map']['hash'])
        for t in chain.get('tables', [])
        for r in t.get('entries', [])
        if r.get('chain_closed') and r.get('static_map')
    })
    c = v5.v3.base.Corpus([p.resolve() for p in a.snapshot], a.runtime.resolve())
    base = v5.v3.base
    mat_cache = {}
    rows = []
    violations = []

    for n, sm in enumerate(static_maps, 1):
        meta = c.entry_meta(sm)
        b, src = c.payload(sm)
        row = {
            'static_map': sm,
            'meta': meta,
            'source': src,
            'd1_static_map_data': None,
            'structural_ok': False,
            'visual_selection_complete': False,
        }
        if not meta or norm(meta.get('reference', '')) != STATIC_MAP_DATA:
            row['error'] = 'static_map_missing_or_class_mismatch'
            violations.append(f'{sm}: {row["error"]}')
            rows.append(row); continue
        if b is None or len(b) < 0x34:
            row['error'] = 'static_map_payload_unavailable_or_short'
            violations.append(f'{sm}: {row["error"]}')
            rows.append(row); continue

        d1 = hx(u32(b, 0x30))
        row['d1_static_map_data'] = d1
        dm = c.entry_meta(d1)
        row['d1_meta'] = dm
        if not dm or norm(dm.get('reference', '')) != D1_STATIC_MAP_DATA:
            row['error'] = 'd1_static_map_data_missing_or_class_mismatch'
            violations.append(f'{sm}: {row["error"]}:{d1}')
            rows.append(row); continue

        vr = base.validate_static_data_d1(c, d1)
        row['structural_validation'] = {
            'ok': bool(vr.get('ok')),
            'violations': vr.get('violations', []),
            'source': vr.get('source'),
            'payload_size': vr.get('payload_size'),
            'instance_count': vr.get('instance_count'),
            'instance_transforms': vr.get('instance_transforms'),
            'summary': vr.get('summary', {}),
        }
        if not vr.get('ok'):
            row['error'] = 'd1_static_data_structural_validation_failed'
            violations.append(f'{sm}/{d1}: structural validation failed: {vr.get("violations")}')
            rows.append(row); continue
        row['structural_ok'] = True

        serialized_placements = 0
        detail_candidate_placements = 0
        detail_rejected_placements = 0
        visual_placements = 0
        material_rejected_placements = 0
        unresolved_material_placements = 0
        visual_info_records = 0
        detail_candidate_info_records = 0
        unresolved_materials = set()
        all_materials = set()
        visual_materials = set()
        detail_population = Counter()
        static_table_rows = []

        for t in vr.get('static_tables', []):
            ts = {
                'hash': t.get('hash'),
                'materials': t.get('summary', {}).get('materials', 0),
                'meshes': t.get('summary', {}).get('meshes', 0),
                'infos': t.get('summary', {}).get('infos', 0),
                'serialized_placements': 0,
                'detail_candidate_placements': 0,
                'visual_placements': 0,
                'unresolved_material_placements': 0,
            }
            mats = t.get('material_hashes', [])
            meshes = t.get('mesh_entries', [])
            for info in t.get('info_entries', []):
                count = int(info.get('instance_count', 0))
                if count < 0:
                    violations.append(f'{sm}/{d1}/{t.get("hash")}: negative instance count')
                    continue
                serialized_placements += count
                ts['serialized_placements'] += count
                si = int(info['static_index']); mi = int(info['material_index'])
                mesh = meshes[si]
                detail = int(mesh['detail_level'])
                detail_population[str(detail)] += count
                if detail not in ALLOWED_DETAIL:
                    detail_rejected_placements += count
                    continue
                detail_candidate_info_records += 1
                detail_candidate_placements += count
                ts['detail_candidate_placements'] += count
                mh = norm(mats[mi]); all_materials.add(mh)
                ms = material_state(c, mat_cache, mh)
                if ms.get('unk08') is None:
                    unresolved_materials.add(mh)
                    unresolved_material_placements += count
                    ts['unresolved_material_placements'] += count
                elif ms['unk08'] == 1:
                    visual_info_records += 1
                    visual_placements += count
                    ts['visual_placements'] += count
                    visual_materials.add(mh)
                else:
                    material_rejected_placements += count
            static_table_rows.append(ts)

        row['content'] = {
            'instance_transform_count': int(vr.get('instance_count', 0)),
            'static_table_refs': int(vr.get('summary', {}).get('static_table_refs', 0)),
            'unique_static_tables': int(vr.get('summary', {}).get('unique_static_tables', 0)),
            'mesh_records': int(vr.get('summary', {}).get('total_static_mesh_records', 0)),
            'info_records': int(vr.get('summary', {}).get('total_static_info_records', 0)),
            'serialized_placements': serialized_placements,
            'detail_candidate_info_records': detail_candidate_info_records,
            'detail_candidate_placements': detail_candidate_placements,
            'visual_info_records': visual_info_records,
            'visual_placements': visual_placements,
            'detail_rejected_placements': detail_rejected_placements,
            'material_rejected_placements': material_rejected_placements,
            'unresolved_material_placements': unresolved_material_placements,
            'unique_materials_in_detail_candidates': len(all_materials),
            'visual_materials': len(visual_materials),
            'unresolved_materials': sorted(unresolved_materials),
            'detail_population': dict(detail_population),
            'has_serialized_static_placements': serialized_placements > 0,
            'has_retail_visible_static_placements': visual_placements > 0,
            'static_tables': static_table_rows,
        }
        row['visual_selection_complete'] = not unresolved_materials
        rows.append(row)
        print('MAP', n, '/', len(static_maps), sm, d1,
              'serialized', serialized_placements,
              'visible', visual_placements,
              'unresolved_materials', len(unresolved_materials), flush=True)

    structurally_ok = [r for r in rows if r.get('structural_ok')]
    visual_complete = [r for r in structurally_ok if r.get('visual_selection_complete')]
    emitters = [r for r in visual_complete if r.get('content', {}).get('visual_placements', 0) > 0]
    nonemitters = [r for r in visual_complete if r.get('content', {}).get('visual_placements', 0) == 0]
    unresolved_visual = [r for r in structurally_ok if not r.get('visual_selection_complete')]

    out = {
        'schema_version': 1,
        'status': 'D1_WORLD_STATIC_MAP_CONTENT_CENSUS_COMPLETE' if len(structurally_ok) == len(rows) and not unresolved_visual and not violations else 'D1_WORLD_STATIC_MAP_CONTENT_CENSUS_PARTIAL',
        'source_chain_status': chain.get('status'),
        'static_map_count': len(rows),
        'structurally_valid_static_maps': len(structurally_ok),
        'visual_selection_complete_static_maps': len(visual_complete),
        'retail_visible_static_map_emitters': len(emitters),
        'retail_visible_static_map_nonemitters': len(nonemitters),
        'unresolved_visual_selection_static_maps': len(unresolved_visual),
        'unique_d1_static_map_data': len({r.get('d1_static_map_data') for r in rows if r.get('d1_static_map_data')}),
        'total_instance_transforms': sum(r.get('content', {}).get('instance_transform_count', 0) for r in structurally_ok),
        'total_static_mesh_records': sum(r.get('content', {}).get('mesh_records', 0) for r in structurally_ok),
        'total_static_info_records': sum(r.get('content', {}).get('info_records', 0) for r in structurally_ok),
        'total_serialized_placements': sum(r.get('content', {}).get('serialized_placements', 0) for r in structurally_ok),
        'total_detail_candidate_placements': sum(r.get('content', {}).get('detail_candidate_placements', 0) for r in visual_complete),
        'total_retail_visible_placements': sum(r.get('content', {}).get('visual_placements', 0) for r in visual_complete),
        'material_cache_count': len(mat_cache),
        'material_cache_unresolved': sum(1 for x in mat_cache.values() if x.get('unk08') is None),
        'top_visible_static_maps': [
            {'static_map': r['static_map'], 'd1_static_map_data': r['d1_static_map_data'],
             'visual_placements': r['content']['visual_placements'],
             'serialized_placements': r['content']['serialized_placements']}
            for r in sorted(emitters, key=lambda x: (-x['content']['visual_placements'], x['static_map']))[:100]
        ],
        'rows': rows,
        'violations': violations,
        'policy': 'Exact structural census plus retail DetailLevel/material.Unk08 gate only. No geometry is exported and no unresolved material is treated as visible or invisible.',
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({k: out[k] for k in (
        'status','static_map_count','structurally_valid_static_maps',
        'visual_selection_complete_static_maps','retail_visible_static_map_emitters',
        'retail_visible_static_map_nonemitters','unresolved_visual_selection_static_maps',
        'unique_d1_static_map_data','total_instance_transforms','total_static_mesh_records',
        'total_static_info_records','total_serialized_placements',
        'total_detail_candidate_placements','total_retail_visible_placements',
        'material_cache_count','material_cache_unresolved','violations')}, indent=2))
    return 0 if out['status'] == 'D1_WORLD_STATIC_MAP_CONTENT_CENSUS_COMPLETE' else 2


if __name__ == '__main__':
    raise SystemExit(main())
