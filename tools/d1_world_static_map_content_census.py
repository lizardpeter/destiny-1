#!/usr/bin/env python3
"""Classify every closed D1 SStaticMapData resource by actual content.

Input is the ownership report from `d1_world_static_map_resource_chain_census.py`.
Each unique SStaticMapData/808008B4 is classified first:

- `direct_d1_baked_static`: +0x30 resolves to 80801B75. These are structurally
  validated and receive the exact retail GetStatics visibility census.
- `no_direct_d1_static_child`: legitimate large/common carriers. They are not
  failures and are left to the separate table-scoped embedded-model/decal parser.

For baked carriers the retail visibility gate is exact:

    DetailLevel in {0,1,2,3,10} AND material.Unk08 == 1

This tool does not export geometry. It proves which ownership resources are baked
static emitters, which are common carriers, and the exact placement population of
the baked subset.
"""
from __future__ import annotations

import argparse, json, struct, sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import d1_tower_map_schema_validate_v5 as v5

STATIC_MAP_DATA = '808008B4'
D1_STATIC_MAP_DATA = '80801B75'
MATERIAL_CLASS = '80801AD7'
ALLOWED_DETAIL = {0, 1, 2, 3, 10}
VALID_KINDS = {'direct_d1_baked_static', 'no_direct_d1_static_child'}


def norm(x):
    return str(x).upper().removeprefix('0X').zfill(8)


def u32(b, o):
    return struct.unpack_from('<I', b, o)[0]


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

    refs = defaultdict(list)
    for t in chain.get('tables', []):
        for r in t.get('entries', []):
            if not r.get('chain_closed') or not r.get('static_map'):
                continue
            refs[norm(r['static_map']['hash'])].append({
                'map_data_table': r.get('map_data_table'),
                'index': r.get('index'),
                'static_map_kind': r.get('static_map_kind'),
                'd1_static_map_data': (r.get('d1_static_map_data') or {}).get('hash'),
            })

    static_maps = sorted(refs)
    c = v5.v3.base.Corpus([p.resolve() for p in a.snapshot], a.runtime.resolve())
    base = v5.v3.base
    mat_cache = {}
    rows = []
    violations = []

    for n, sm in enumerate(static_maps, 1):
        source_refs = refs[sm]
        kinds = sorted({x.get('static_map_kind') for x in source_refs})
        row = {
            'static_map': sm,
            'reference_count': len(source_refs),
            'source_references': source_refs,
            'source_kinds': kinds,
            'kind': kinds[0] if len(kinds) == 1 else None,
            'classification_ok': False,
            'baked_structural_ok': None,
            'visual_selection_complete': None,
        }
        if len(kinds) != 1 or row['kind'] not in VALID_KINDS:
            row['error'] = 'inconsistent_or_unknown_static_map_kind'
            violations.append(f'{sm}: kinds={kinds}')
            rows.append(row); continue

        meta = c.entry_meta(sm)
        b, src = c.payload(sm)
        row['meta'] = meta
        row['source'] = src
        if not meta or norm(meta.get('reference', '')) != STATIC_MAP_DATA:
            row['error'] = 'static_map_missing_or_class_mismatch'
            violations.append(f'{sm}: {row["error"]}')
            rows.append(row); continue
        if b is None:
            row['error'] = 'static_map_payload_unavailable'
            violations.append(f'{sm}: {row["error"]}')
            rows.append(row); continue
        row['classification_ok'] = True

        if row['kind'] == 'no_direct_d1_static_child':
            row['payload_size'] = len(b)
            row['baked_structural_ok'] = None
            row['visual_selection_complete'] = None
            rows.append(row)
            print('MAP', n, '/', len(static_maps), sm, 'COMMON', 'refs', len(source_refs), flush=True)
            continue

        # Baked carrier: the chain report already proved the exact D1 child. Check
        # that all references agree, then validate the child's static tables.
        d1s = sorted({norm(x['d1_static_map_data']) for x in source_refs if x.get('d1_static_map_data')})
        if len(d1s) != 1:
            row['error'] = f'baked_d1_child_count_{len(d1s)}'
            violations.append(f'{sm}: {row["error"]}:{d1s}')
            rows.append(row); continue
        d1 = d1s[0]
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
            row['baked_structural_ok'] = False
            row['error'] = 'd1_static_data_structural_validation_failed'
            violations.append(f'{sm}/{d1}: structural validation failed: {vr.get("violations")}')
            rows.append(row); continue
        row['baked_structural_ok'] = True

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

    classified = [r for r in rows if r.get('classification_ok')]
    common = [r for r in classified if r.get('kind') == 'no_direct_d1_static_child']
    baked = [r for r in classified if r.get('kind') == 'direct_d1_baked_static']
    baked_ok = [r for r in baked if r.get('baked_structural_ok')]
    visual_complete = [r for r in baked_ok if r.get('visual_selection_complete')]
    emitters = [r for r in visual_complete if r.get('content', {}).get('visual_placements', 0) > 0]
    nonemitters = [r for r in visual_complete if r.get('content', {}).get('visual_placements', 0) == 0]
    unresolved_visual = [r for r in baked_ok if not r.get('visual_selection_complete')]

    complete = (
        len(classified) == len(rows)
        and len(baked_ok) == len(baked)
        and len(visual_complete) == len(baked_ok)
        and not violations
    )
    out = {
        'schema_version': 2,
        'status': 'D1_WORLD_STATIC_MAP_CONTENT_CENSUS_COMPLETE' if complete else 'D1_WORLD_STATIC_MAP_CONTENT_CENSUS_PARTIAL',
        'source_chain_status': chain.get('status'),
        'static_map_count': len(rows),
        'classified_static_maps': len(classified),
        'common_no_direct_d1_static_child_maps': len(common),
        'direct_d1_baked_static_maps': len(baked),
        'structurally_valid_baked_static_maps': len(baked_ok),
        'visual_selection_complete_baked_static_maps': len(visual_complete),
        'retail_visible_baked_static_emitters': len(emitters),
        'retail_visible_baked_static_nonemitters': len(nonemitters),
        'unresolved_visual_selection_baked_static_maps': len(unresolved_visual),
        'unique_d1_static_map_data': len({r.get('d1_static_map_data') for r in baked if r.get('d1_static_map_data')}),
        'total_instance_transforms': sum(r.get('content', {}).get('instance_transform_count', 0) for r in baked_ok),
        'total_static_mesh_records': sum(r.get('content', {}).get('mesh_records', 0) for r in baked_ok),
        'total_static_info_records': sum(r.get('content', {}).get('info_records', 0) for r in baked_ok),
        'total_serialized_placements': sum(r.get('content', {}).get('serialized_placements', 0) for r in baked_ok),
        'total_detail_candidate_placements': sum(r.get('content', {}).get('detail_candidate_placements', 0) for r in visual_complete),
        'total_retail_visible_placements': sum(r.get('content', {}).get('visual_placements', 0) for r in visual_complete),
        'material_cache_count': len(mat_cache),
        'material_cache_unresolved': sum(1 for x in mat_cache.values() if x.get('unk08') is None),
        'common_static_maps': [r['static_map'] for r in common],
        'baked_static_maps': [r['static_map'] for r in baked],
        'top_visible_static_maps': [
            {'static_map': r['static_map'], 'd1_static_map_data': r['d1_static_map_data'],
             'visual_placements': r['content']['visual_placements'],
             'serialized_placements': r['content']['serialized_placements']}
            for r in sorted(emitters, key=lambda x: (-x['content']['visual_placements'], x['static_map']))
        ],
        'rows': rows,
        'violations': violations,
        'policy': 'SStaticMapData is classified before baked-static parsing. Common carriers without a direct 80801B75 child are valid and excluded from the baked visibility totals. Baked totals use only exact structural validation plus the retail DetailLevel/material.Unk08 gate.',
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({k: out[k] for k in (
        'status','static_map_count','classified_static_maps',
        'common_no_direct_d1_static_child_maps','direct_d1_baked_static_maps',
        'structurally_valid_baked_static_maps','visual_selection_complete_baked_static_maps',
        'retail_visible_baked_static_emitters','retail_visible_baked_static_nonemitters',
        'unresolved_visual_selection_baked_static_maps','unique_d1_static_map_data',
        'total_instance_transforms','total_static_mesh_records','total_static_info_records',
        'total_serialized_placements','total_detail_candidate_placements',
        'total_retail_visible_placements','material_cache_count','material_cache_unresolved',
        'violations')}, indent=2))
    return 0 if complete else 2


if __name__ == '__main__':
    raise SystemExit(main())
