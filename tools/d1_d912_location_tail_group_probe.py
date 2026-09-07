#!/usr/bin/env python3
"""Validate the previously-opaque 0x10-byte tail of D1 ROI S2B138080 locations.

Charm pins S2B138080 at stride 0x30 but currently names only the first 0x20 bytes:
Location Vector4 + Rotation Vector4.  The Tower scripted-entity census preserves the
remaining +0x20..+0x2F bytes losslessly as ``tail_20_30_hex``.

Across the Tower corpus the tail is four little-endian uint32 values.  This probe
keeps their semantics conservative while testing a strong structural hypothesis:

    +0x20 u32 unk20
    +0x24 u32 unk24
    +0x28 u32 candidate_group_index
    +0x2C u32 unk2C

``candidate_group_index`` is accepted as a *structural grouping key* only if every
observed value is in range for the source-owned SD9128080 Unk20/SD614 group array,
location order is nondecreasing by that value, and duplicate appearances of one
D912 table across scenario variants decode identically.  It is not given a gameplay
semantic name by this tool.

Once the grouping key passes those fail-closed invariants, a location can be joined
to the corresponding SD614 group.  If that group contains exactly one unique non-null
EntitySK FileHash, the EntitySK identity at that source-owned location is exact even
when the group serializes repeated records or multiple locations.  Groups containing
multiple unique EntitySKs remain explicitly ambiguous.
"""
from __future__ import annotations

import argparse
import collections
import json
import struct
from pathlib import Path

NULLS = {None, '00000000', 'FFFFFFFF'}
EMPTY_FNV1 = 0x811C9DC5


def norm(x):
    return None if x is None else str(x).upper().removeprefix('0X').zfill(8)


def tail_words(hex_text: str) -> tuple[int, int, int, int]:
    b = bytes.fromhex(hex_text)
    if len(b) != 0x10:
        raise ValueError(f'S2B138080 tail must be 0x10 bytes, got 0x{len(b):X}')
    return struct.unpack('<4I', b)


def canonical_table(t: dict) -> tuple:
    groups = tuple(
        (
            int(g.get('group_index', -1)),
            norm(g.get('type_string_hash')),
            tuple(
                (
                    int(r.get('record_index', -1)),
                    norm(r.get('entity_hash')),
                    norm(r.get('type_string_hash')),
                    r.get('world_id_hex'),
                )
                for r in g.get('records', [])
            ),
        )
        for g in t.get('groups', [])
    )
    locs = tuple(
        (
            int(x.get('index', -1)),
            tuple(x.get('location') or []),
            tuple(x.get('rotation') or []),
            x.get('tail_20_30_hex'),
        )
        for x in t.get('locations', [])
    )
    return groups, locs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--scenario', type=Path, action='append', required=True,
                    help='d1_remote_activity_scripted_entity_census JSON; repeatable')
    ap.add_argument('-o', '--output', type=Path, required=True)
    a = ap.parse_args()

    violations: list[str] = []
    scenario_rows = []
    first_table: dict[str, tuple[tuple, str, dict]] = {}
    table_scenarios = collections.defaultdict(set)
    tail_word_counts = [collections.Counter() for _ in range(4)]
    candidate_index_counts = collections.Counter()
    unk2c_counts = collections.Counter()
    total_locations = 0
    exact_location_rows = []
    ambiguous_location_rows = []
    decoded_tables = {}

    for path in a.scenario:
        d = json.loads(path.read_text())
        slug = path.stem
        if d.get('violations'):
            violations.append(f'{slug}:source_census_violations:{len(d["violations"])}')
        sr = {
            'scenario': slug,
            'activity_hash': (d.get('activity') or {}).get('tag_hash'),
            'activity_name': (d.get('activity') or {}).get('name'),
            'table_count': len(d.get('scripted_tables', [])),
            'location_count': 0,
            'exact_entity_location_count': 0,
            'ambiguous_entity_location_count': 0,
        }

        for t in d.get('scripted_tables', []):
            th = norm(t.get('scripted_entity_table'))
            table_scenarios[th].add(slug)
            can = canonical_table(t)
            if th in first_table and first_table[th][0] != can:
                violations.append(f'{th}:cross_scenario_serialization_disagrees:{first_table[th][1]}:{slug}')
            else:
                first_table.setdefault(th, (can, slug, t))

            groups = {int(g.get('group_index', -1)): g for g in t.get('groups', [])}
            group_count = len(groups)
            # Source parser should have produced dense 0..N-1 group indices.
            if sorted(groups) != list(range(group_count)):
                violations.append(f'{slug}:{th}:non_dense_group_indices:{sorted(groups)}')

            seen_indices = []
            table_decoded_locations = []
            for loc in t.get('locations', []):
                sr['location_count'] += 1
                total_locations += 1
                try:
                    w0, w1, gi, w3 = tail_words(loc.get('tail_20_30_hex', ''))
                except Exception as ex:
                    violations.append(f'{slug}:{th}:location[{loc.get("index")}]:tail_decode:{ex!r}')
                    continue
                for i, v in enumerate((w0, w1, gi, w3)):
                    tail_word_counts[i][f'{v:08X}'] += 1
                candidate_index_counts[str(gi)] += 1
                unk2c_counts[str(w3)] += 1
                seen_indices.append(gi)
                if gi not in groups:
                    violations.append(f'{slug}:{th}:location[{loc.get("index")}]:candidate_group_index_{gi}_outside_0_{group_count-1}')
                    continue

                g = groups[gi]
                records = g.get('records', [])
                entities = sorted({
                    norm(r.get('entity_hash')) for r in records
                    if norm(r.get('entity_hash')) not in NULLS
                })
                row = {
                    'scenario': slug,
                    'activity_hash': sr['activity_hash'],
                    'd912': th,
                    'location_index': loc.get('index'),
                    'location': loc.get('location'),
                    'rotation': loc.get('rotation'),
                    'tail_words_hex': [f'{x:08X}' for x in (w0, w1, gi, w3)],
                    'tail_unk20': f'{w0:08X}',
                    'tail_unk24': f'{w1:08X}',
                    'candidate_group_index': gi,
                    'tail_unk2c': w3,
                    'group_type_string_hash': norm(g.get('type_string_hash')),
                    'group_record_count': len(records),
                    'group_unique_entity_count': len(entities),
                    'group_entity_hashes': entities,
                }
                if len(entities) == 1:
                    row['entity_hash'] = entities[0]
                    row['assignment_status'] = 'exact_unique_entity_within_structurally_indexed_group'
                    exact_location_rows.append(row)
                    sr['exact_entity_location_count'] += 1
                else:
                    row['assignment_status'] = 'ambiguous_multiple_entities_within_structurally_indexed_group'
                    ambiguous_location_rows.append(row)
                    sr['ambiguous_entity_location_count'] += 1
                table_decoded_locations.append(row)

            if seen_indices != sorted(seen_indices):
                violations.append(f'{slug}:{th}:candidate_group_indices_not_nondecreasing:{seen_indices}')

            # Keep only first physical D912 copy in the deduplicated table report;
            # cross-scenario identity above proves later copies byte-equivalent at
            # the decoded group/location level.
            if th not in decoded_tables:
                decoded_tables[th] = {
                    'd912': th,
                    'group_count': group_count,
                    'record_count': len(t.get('records', [])),
                    'location_count': len(t.get('locations', [])),
                    'candidate_group_index_sequence': seen_indices,
                    'tail_unk2c_values': sorted({x['tail_unk2c'] for x in table_decoded_locations}),
                    'locations': table_decoded_locations,
                }
        scenario_rows.append(sr)

    # Deduplicate exact/ambiguous physical locations by D912 + location index for
    # corpus-level counts, while retaining scenario-expanded rows separately.
    def dedup(rows):
        out = {}
        for r in rows:
            out.setdefault((r['d912'], int(r['location_index'])), r)
        return list(out.values())

    exact_unique = dedup(exact_location_rows)
    ambiguous_unique = dedup(ambiguous_location_rows)
    all_first_words_empty_fnv = (
        set(tail_word_counts[0]) <= {f'{EMPTY_FNV1:08X}'} and
        set(tail_word_counts[1]) <= {f'{EMPTY_FNV1:08X}'}
    )

    structurally_closed = not violations
    out = {
        'schema_version': 1,
        'status': 'D1_D912_LOCATION_TAIL_GROUPING_STRUCTURALLY_CLOSED' if structurally_closed else 'D1_D912_LOCATION_TAIL_GROUPING_PARTIAL',
        'scenario_count': len(a.scenario),
        'scenarios': scenario_rows,
        'scenario_expanded_location_count': total_locations,
        'unique_d912_count': len(decoded_tables),
        'unique_physical_location_count': len(exact_unique) + len(ambiguous_unique),
        'candidate_group_index_all_in_range': not any('outside_0_' in v for v in violations),
        'candidate_group_index_all_nondecreasing': not any('not_nondecreasing' in v for v in violations),
        'cross_scenario_duplicate_tables_identical': not any('cross_scenario_serialization_disagrees' in v for v in violations),
        'tail_word_value_counts': {f'word_{i}_offset_0x{0x20+i*4:02X}': dict(c) for i, c in enumerate(tail_word_counts)},
        'first_two_tail_words_always_fnv1_empty_basis': all_first_words_empty_fnv,
        'candidate_group_index_counts': dict(candidate_index_counts),
        'tail_unk2c_counts': dict(unk2c_counts),
        'scenario_expanded_exact_entity_location_count': len(exact_location_rows),
        'scenario_expanded_ambiguous_entity_location_count': len(ambiguous_location_rows),
        'unique_exact_entity_location_count': len(exact_unique),
        'unique_ambiguous_entity_location_count': len(ambiguous_unique),
        'unique_exact_entity_locations': exact_unique,
        'unique_ambiguous_entity_locations': ambiguous_unique,
        'scenario_expanded_exact_entity_locations': exact_location_rows,
        'decoded_tables': decoded_tables,
        'd912_scenario_membership': {h: sorted(v) for h, v in sorted(table_scenarios.items())},
        'violations': violations,
        'policy': (
            'S2B138080 +0x28 is promoted only as a structural D614-group indexing key after corpus-wide in-range, '
            'monotonic-order, dense-group, and cross-scenario-identity checks. Its gameplay semantic name remains unknown. '
            'An EntitySK-location assignment is called exact only when the indexed source-owned group contains one unique '
            'non-null EntitySK FileHash. Multi-entity groups remain ambiguous. +0x20/+0x24/+0x2C semantics are intentionally unset.'
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2) + '\n')
    print('STATUS', out['status'])
    print('SCENARIOS', out['scenario_count'], 'UNIQUE_D912', out['unique_d912_count'])
    print('LOCATIONS scenario-expanded', total_locations, 'unique', out['unique_physical_location_count'])
    print('EXACT unique', out['unique_exact_entity_location_count'], 'AMBIG unique', out['unique_ambiguous_entity_location_count'])
    print('TAIL_WORDS')
    for k, v in out['tail_word_value_counts'].items(): print(k, v)
    print('FIRST_TWO_EMPTY_FNV1', all_first_words_empty_fnv)
    print('VIOLATIONS', len(violations))
    for v in violations[:100]: print(v)
    return 0 if structurally_closed else 2


if __name__ == '__main__':
    raise SystemExit(main())
