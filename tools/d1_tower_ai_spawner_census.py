#!/usr/bin/env python3
"""Trace D1 Tower NPC/enemy/AI carriers that the normal placement census does not collapse.

Charm's D1 Activity.CollapseResourceParent contains an explicit (commented) path for
"NPCs, enemies and other AI":

    SF6038080 -> EntityResource
      Unk10 ResourcePointer is SBC078080 / 808007BC
      Unk18 ResourcePointer is SA7058080 / 808005A7
        SA7058080 +0x68 -> Tag<SD9128080> / 808012D9

The ordinary Tower placement census intentionally only collapses the S2E098080 ->
SDD078080 world-object path.  This tool follows the separate AI path exactly,
parses the referenced SD912 scripted-entity tables, and then classifies every
spawned EntitySK through the existing source-pinned SEntity dependency parser.

No human/vendor identity is inferred from appearance.  The only semantic promotion
made here is Charm's own broad category: NPC/enemy/other-AI carrier.
"""
from __future__ import annotations

import argparse
import json
import struct
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import d1_tower_map_schema_validate_v5 as v5
from d1_world_scripted_entity_identity_census import parse_d912, placement_index, resource_ptr
from d1_world_entity_dependency_census import parse_entity

F603 = '808003F6'
ENTITY_RESOURCE = '80800861'
SBC07 = '808007BC'
A705 = '808005A7'
D912 = '808012D9'
NULLS = {'00000000', 'FFFFFFFF'}
PINNED_SOURCE = (
    'MontagueM/Charm@50d36ee1f9ecadad7522504c20b1f3f9c97e30af '
    'Tiger/Schema/Activity/Activity.cs D1 CollapseResourceParent explicit NPC/enemy/AI path + '
    'Tiger/Schema/Activity/ActivityStructsROI.cs SBC078080/SA7058080/SD9128080 layouts.'
)


def norm(x):
    return str(x).upper().removeprefix('0X').zfill(8)


def hx(v):
    return f'{v:08X}'


def u32(b, o):
    return struct.unpack_from('<I', b, o)[0]


def activity_f603_owners(entity_tables: dict) -> dict[str, list[dict]]:
    owners = defaultdict(list)
    for act in entity_tables.get('activities', []):
        aname = act.get('activity_name')
        ahash = norm(act.get('hash', 'FFFFFFFF'))
        for loc in act.get('locations', []):
            for eg in loc.get('activity_entity_groups', []):
                parent = eg.get('resource_parent') or {}
                for group in parent.get('groups', []):
                    for rr in group.get('resources', []):
                        for stage in rr.get('stages', []):
                            for er in stage.get('entity_resource_tables', []):
                                h = norm(er.get('hash', 'FFFFFFFF'))
                                if h in NULLS:
                                    continue
                                owners[h].append({
                                    'activity_hash': ahash,
                                    'activity_name': aname,
                                    'location_name_hash': loc.get('location_name_hash'),
                                    'phase_name_hash': eg.get('phase_name_hash'),
                                    'bubble_name_hash': eg.get('bubble_name_hash'),
                                    'resource_parent': parent.get('hash'),
                                    's6e_resource': rr.get('hash'),
                                    'stage_index': stage.get('index'),
                                })
    # exact duplicate provenance rows are common across scenario serialization; retain one
    for h, rows in list(owners.items()):
        uniq = []
        seen = set()
        for r in rows:
            k = tuple(sorted(r.items()))
            if k not in seen:
                seen.add(k)
                uniq.append(r)
        owners[h] = uniq
    return dict(owners)


def exact_payload(c, h, expected_ref=None):
    h = norm(h)
    m = c.entry_meta(h)
    b, src = c.payload(h)
    if m is None or b is None:
        raise ValueError(f'{h}: payload unavailable')
    ref = norm(m.get('reference', 'FFFFFFFF'))
    if expected_ref is not None and ref != norm(expected_ref):
        raise ValueError(f'{h}: reference {ref} != {norm(expected_ref)}')
    return m, b, src


def inspect_carrier(c, f603_hash, owners):
    h = norm(f603_hash)
    row = {
        'f603': h,
        'activity_owners': owners.get(h, []),
        'violations': [],
        'is_charm_ai_carrier': False,
    }
    try:
        fm, fb, fsrc = exact_payload(c, h, F603)
        row['f603_meta'] = fm
        row['f603_payload_source'] = fsrc
        if len(fb) < 0x10:
            raise ValueError('F603 shorter than 0x10')
        erh = hx(u32(fb, 0x0C))
        row['entity_resource'] = erh
        em, eb, esrc = exact_payload(c, erh, ENTITY_RESOURCE)
        row['entity_resource_meta'] = em
        row['entity_resource_payload_source'] = esrc
        if len(eb) < 0x20:
            raise ValueError('EntityResource shorter than 0x20')
        p10 = resource_ptr(eb, 0x10)
        p18 = resource_ptr(eb, 0x18)
        row['unk10_pointer'] = p10
        row['unk18_pointer'] = p18
        pair = (p10.get('resource_class'), p18.get('resource_class'))
        row['resource_class_pair'] = list(pair)
        row['is_charm_ai_carrier'] = pair == (SBC07, A705)
        if not row['is_charm_ai_carrier']:
            return row
        if not p18.get('ok') or not isinstance(p18.get('absolute'), int):
            raise ValueError('A705 ResourcePointer invalid')
        abase = int(p18['absolute'])
        row['a705_absolute'] = abase
        if abase < 0 or abase + 0x6C > len(eb):
            raise ValueError(f'A705 +0x68 Tag field OOB at 0x{abase:X}')
        dh = hx(u32(eb, abase + 0x68))
        row['d912'] = dh
        dm = c.entry_meta(dh)
        row['d912_meta'] = dm
        if dh in NULLS:
            row['violations'].append('A705_D912_is_null')
        elif dm is None:
            row['violations'].append('A705_D912_unresolved')
        elif norm(dm.get('reference', 'FFFFFFFF')) != D912:
            row['violations'].append(f'A705_D912_reference_{norm(dm.get("reference"))}_not_{D912}')
    except Exception as ex:
        row['violations'].append(repr(ex))
    return row


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--snapshot', type=Path, action='append', required=True)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('--entity-tables', type=Path, required=True)
    ap.add_argument('--placements', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()

    et = json.loads(a.entity_tables.read_text())
    p = json.loads(a.placements.read_text())
    live = placement_index(p)
    c = v5.v3.base.Corpus([x.resolve() for x in a.snapshot], a.runtime.resolve())
    owners = activity_f603_owners(et)

    carriers = [inspect_carrier(c, h, owners) for h in sorted(owners)]
    ai = [x for x in carriers if x.get('is_charm_ai_carrier')]
    violations = [f'{x["f603"]}:{v}' for x in carriers for v in x.get('violations', [])]

    d912_hashes = sorted({norm(x.get('d912')) for x in ai if x.get('d912') and norm(x.get('d912')) not in NULLS})
    tables = {}
    for h in d912_hashes:
        t = parse_d912(c, h, live)
        tables[h] = t
        violations.extend(f'{h}:{v}' for v in t.get('violations', []))

    # Preserve one scripted record per D912 table record, regardless of how many
    # F603 carriers reference that table. Carrier ownership is joined separately.
    d912_carriers = defaultdict(list)
    for x in ai:
        if x.get('d912'):
            d912_carriers[norm(x['d912'])].append(x['f603'])

    records = []
    for dh, t in tables.items():
        for r in t.get('records', []):
            e = norm(r.get('entity_hash', 'FFFFFFFF'))
            if e in NULLS:
                continue
            records.append({
                'd912': dh,
                'carrier_f603': sorted(d912_carriers.get(dh, [])),
                'group_index': r.get('group_index'),
                'record_index': r.get('record_index'),
                'type_string_hash': r.get('type_string_hash'),
                'entity_hash': e,
                'world_id_hex': r.get('world_id_hex'),
                'rotation': r.get('rotation'),
                'translation': r.get('translation'),
                'entity_name_string_hash': r.get('entity_name_string_hash'),
                'script_name_data_present': r.get('script_name_data_present'),
                'placement_match': r.get('placement_match'),
                'record_violations': r.get('violations', []),
            })

    spawned_entities = sorted({r['entity_hash'] for r in records})
    entity_rows = {h: parse_entity(c, h) for h in spawned_entities}
    for h, er in entity_rows.items():
        violations.extend(f'{h}:{v}' for v in er.get('violations', []))

    classification_counts = Counter((entity_rows[h].get('composition') or {}).get('classification', 'unparsed') for h in spawned_entities)
    bone_counts = Counter()
    for h in spawned_entities:
        for n in (entity_rows[h].get('composition') or {}).get('bone_counts', []):
            bone_counts[str(n)] += 1

    articulated_classes = {'rigged_articulated_entity_candidate', 'model_skeleton_articulated_candidate'}
    articulated_entities = [h for h in spawned_entities if (entity_rows[h].get('composition') or {}).get('classification') in articulated_classes]
    runtime_worldids = set(live)
    spawned_worldids = {str(r.get('world_id_hex')).upper() for r in records if r.get('world_id_hex')}
    spawned_not_direct = sorted(spawned_worldids - runtime_worldids)
    direct_overlap = sorted(spawned_worldids & runtime_worldids)

    activity_counts = Counter()
    ambient_ai = []
    for x in ai:
        names = sorted({str(o.get('activity_name')) for o in x.get('activity_owners', []) if o.get('activity_name')})
        for n in names:
            activity_counts[n] += 1
        if 'ambient_city_tower:scenario_client' in names:
            ambient_ai.append(x['f603'])

    name_hashes = Counter(r['entity_name_string_hash'] for r in records if r.get('entity_name_string_hash') not in (None, *NULLS))
    type_hashes = Counter(r['type_string_hash'] for r in records if r.get('type_string_hash') not in (None, *NULLS))

    out = {
        'schema_version': 1,
        'status': 'D1_TOWER_AI_SPAWNER_CENSUS_COMPLETE' if not violations else 'D1_TOWER_AI_SPAWNER_CENSUS_PARTIAL',
        'pinned_source': PINNED_SOURCE,
        'f603_source_count': len(carriers),
        'charm_ai_carrier_count': len(ai),
        'charm_ai_carrier_activity_counts': dict(activity_counts),
        'ambient_city_tower_ai_carrier_count': len(set(ambient_ai)),
        'ambient_city_tower_ai_carriers': sorted(set(ambient_ai)),
        'unique_d912_count': len(d912_hashes),
        'd912_hashes': d912_hashes,
        'scripted_spawn_record_count': len(records),
        'unique_spawned_entity_count': len(spawned_entities),
        'spawned_entity_hashes': spawned_entities,
        'spawned_entity_classification_counts': dict(classification_counts),
        'spawned_entity_bone_count_frequency': dict(sorted(bone_counts.items(), key=lambda kv: int(kv[0]))),
        'spawned_articulated_entity_count': len(articulated_entities),
        'spawned_articulated_entities': articulated_entities,
        'unique_spawned_world_id_count': len(spawned_worldids),
        'spawned_world_ids_absent_from_direct_placement_census_count': len(spawned_not_direct),
        'spawned_world_ids_absent_from_direct_placement_census': spawned_not_direct,
        'spawned_world_ids_overlapping_direct_placement_census_count': len(direct_overlap),
        'spawned_world_ids_overlapping_direct_placement_census': direct_overlap,
        'entity_name_string_hash_reference_counts': dict(name_hashes),
        'type_string_hash_reference_counts': dict(type_hashes),
        'carriers': carriers,
        'd912_tables': tables,
        'spawn_records': records,
        'spawned_entities': entity_rows,
        'violations': violations,
        'policy': (
            'Carrier semantic is source-pinned to Charm\'s explicit D1 NPC/enemy/other-AI path only when '
            'EntityResource Unk10 is SBC078080 and Unk18 is SA7058080. Spawned EntitySK classification uses '
            'the same exact SEntity model/skeleton/resource rules as the world dependency census. Human/vendor '
            'identity is never inferred from geometry, package names, bone counts, or proximity.'
        ),
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=2) + '\n')
    summary_keys = (
        'status', 'f603_source_count', 'charm_ai_carrier_count', 'charm_ai_carrier_activity_counts',
        'ambient_city_tower_ai_carrier_count', 'unique_d912_count', 'scripted_spawn_record_count',
        'unique_spawned_entity_count', 'spawned_entity_classification_counts', 'spawned_entity_bone_count_frequency',
        'spawned_articulated_entity_count', 'spawned_articulated_entities', 'unique_spawned_world_id_count',
        'spawned_world_ids_absent_from_direct_placement_census_count',
        'spawned_world_ids_overlapping_direct_placement_census_count', 'entity_name_string_hash_reference_counts',
        'type_string_hash_reference_counts', 'violations',
    )
    print(json.dumps({k: out[k] for k in summary_keys}, indent=2))
    return 0 if not violations else 2


if __name__ == '__main__':
    raise SystemExit(main())
