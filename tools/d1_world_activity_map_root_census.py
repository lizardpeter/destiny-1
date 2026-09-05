#!/usr/bin/env python3
"""Trace D1 ROI named Activity -> Bubble -> MapContainer -> MapDataTable ownership.

Pinned source: MontagueM/Charm commit
50d36ee1f9ecadad7522504c20b1f3f9c97e30af.

D1 Activities are package named/global tags, not ordinary entries classified by their
file-entry Reference. D1 Package.GetAllActivities() reads the named-tag table:

  PackageHeader +0xEC NamedTagTableCount
                +0xF0 NamedTagTableOffset
    -> 0x44-byte SPackageActivityEntry_D1 slots
       +0x00 TagHash
       +0x04 TagClassHash
       +0x08 null-terminated name bytes

A single TagHash may deliberately appear more than once with different names. Charm
separates its hash->class and hash->name caches, so these are aliases, not duplicate
assets. This census preserves every physical row and merges same-hash/same-class current
rows into one semantic Tag with an aliases[] list. Conflicting classes remain failures.

A named tag whose TagClassHash is SActivity_ROI (Charm display 2E058080; project raw
uint 8080052E) is opened directly by TagHash and deserialized as:

  SActivity_ROI / 0x28
    +0x10 DynamicArray<S0A418080>, elem 0x04
      -> ChildMapReference: SBubbleDefinition / 808091E0
        -> SMapContainer / 80808A54
          -> SMapDataTable / 808009A2

The lower Tag class checks are D1-manifest-aware through d1_world_map_root_census.py.
Only the highest physical patch generation for each package id contributes the current
named-tag table; older tables remain loss-preserving evidence.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import d1_tower_map_schema_validate_v5 as v5
import d1_world_map_data_layer_census as layer
import d1_world_map_root_census as roots
from d1_pkg_probe import parse_header, parse_named, read_table

ACTIVITY_ROI = '8080052E'       # Charm schema display: 2E058080
UNK_ACTIVITY_ROI = '80800616'   # Charm schema display: 16068080
BUBBLE_DEFINITION = roots.BUBBLE_DEFINITION
NAMED_SLOT_STRIDE = 0x44
PINNED_SOURCE = (
    'MontagueM/Charm@50d36ee1f9ecadad7522504c20b1f3f9c97e30af '
    'Tiger/DESTINY1_RISE_OF_IRON/Package.cs + Tiger/PackageResourcer.cs + '
    'Tiger/Schema/Activity/Activity.cs + ActivityStructsROI.cs + '
    'Tiger/Schema/Static/StaticMapData.cs + Tiger/TigerHash.cs::GetReferenceFromManifest'
)


def norm(x: object) -> str:
    return str(x).upper().removeprefix('0X').zfill(8)


def u32(b: bytes, o: int) -> int:
    return struct.unpack_from('<I', b, o)[0]


def hx(v: int) -> str:
    return f'{v:08X}'


def generation(path: Path) -> int:
    m = re.search(r'_(\d+)\.pkg(?:\.bin)?$', path.name, re.IGNORECASE)
    return int(m.group(1)) if m else -1


def charm_display(raw_uint_hex: str) -> str:
    h = norm(raw_uint_hex)
    return ''.join(reversed([h[i:i + 2] for i in range(0, 8, 2)]))


def canonical_named_class(raw_uint_hex: str) -> str:
    h = norm(raw_uint_hex)
    aliases = {
        ACTIVITY_ROI: ACTIVITY_ROI,
        charm_display(ACTIVITY_ROI): ACTIVITY_ROI,
        UNK_ACTIVITY_ROI: UNK_ACTIVITY_ROI,
        charm_display(UNK_ACTIVITY_ROI): UNK_ACTIVITY_ROI,
    }
    return aliases.get(h, h)


def current_hashes_by_ref(c, reference: str) -> list[str]:
    return roots.current_hashes_by_ref(c, reference)


def merge_current_named_rows(rows: list[dict]) -> tuple[list[dict], list[str]]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for x in rows:
        grouped[x['tag_hash']].append(x)

    merged = []
    violations = []
    for h in sorted(grouped):
        xs = grouped[h]
        classes = sorted({x['class_hash_canonical'] for x in xs})
        packages = sorted({x['source_package_id'] for x in xs})
        if len(classes) != 1:
            violations.append(f'current_named_tag_class_conflict:{h}:{classes}')
        # A FileHash encodes its package id, so cross-package ownership for the same
        # current hash would be contradictory even if the class happened to match.
        if len(packages) != 1:
            violations.append(f'current_named_tag_package_conflict:{h}:{packages}')

        aliases = []
        named_indices = []
        for x in xs:
            if x.get('name') not in aliases:
                aliases.append(x.get('name'))
            named_indices.append(int(x['index']))
        # Match Charm's activity-name preference: keep the longest alias as display
        # name while retaining all aliases and source row indices losslessly.
        display_name = max((x for x in aliases if x is not None), key=len, default=None)
        base = dict(xs[0])
        base['name'] = display_name
        base['aliases'] = aliases
        base['named_table_indices'] = named_indices
        base['alias_count'] = len(xs)
        merged.append(base)
    return merged, violations


def scan_named_tag_tables(paths: list[Path]) -> dict:
    """Inventory all physical named tables and choose highest patch per package id."""
    physical = []
    by_pkg: dict[int, list[dict]] = defaultdict(list)
    violations = []

    for p in sorted(paths, key=lambda x: (x.name, generation(x))):
        with p.open('rb') as f:
            h = parse_header(f)
            count = int(h['named_tag_table_count'])
            off = int(h['named_tag_table_offset'])
            raw = read_table(f, off, count, NAMED_SLOT_STRIDE) if count else b''
        entries = parse_named(raw)
        actual_sha = hashlib.sha1(raw).hexdigest()
        expected_sha = str(h.get('named_tag_table_hash') or '').lower()
        absent_zero_table = count == 0 and off == 0 and expected_sha == ('0' * 40)
        if absent_zero_table:
            sha_matches = True
            hash_policy = 'ABSENT_TABLE_ZERO_HEADER_HASH'
        else:
            sha_matches = actual_sha.lower() == expected_sha if expected_sha else None
            hash_policy = 'SHA1_OF_SERIALIZED_NAMED_TABLE'
        if sha_matches is False:
            violations.append(f'{p.name}:named_tag_table_sha1_mismatch')
        row = {
            'snapshot': p.name,
            'generation': generation(p),
            'package_id': f"{int(h['pkg_id']):04X}",
            'header_patch_id': int(h.get('patch_id', -1)),
            'named_tag_table_count': count,
            'named_tag_table_offset': off,
            'named_tag_table_bytes': len(raw),
            'named_tag_table_sha1_expected': expected_sha,
            'named_tag_table_sha1_actual': actual_sha,
            'named_tag_table_sha1_matches': sha_matches,
            'named_tag_table_hash_policy': hash_policy,
            'entries': entries,
        }
        physical.append(row)
        by_pkg[int(h['pkg_id'])].append(row)

    current_packages = []
    current_rows = []
    for pkg_id, rows in sorted(by_pkg.items()):
        chosen = max(rows, key=lambda r: (r['header_patch_id'], r['generation']))
        current_packages.append({
            'package_id': f'{pkg_id:04X}',
            'snapshot': chosen['snapshot'],
            'generation': chosen['generation'],
            'header_patch_id': chosen['header_patch_id'],
            'named_tag_table_count': chosen['named_tag_table_count'],
            'named_tag_table_hash_policy': chosen['named_tag_table_hash_policy'],
        })
        for e in chosen['entries']:
            raw_cls = norm(e['class_hash'])
            current_rows.append({
                **e,
                'tag_hash': norm(e['tag_hash']),
                'class_hash_raw_uint': raw_cls,
                'class_hash_charm_display': charm_display(raw_cls),
                'class_hash_canonical': canonical_named_class(raw_cls),
                'source_snapshot': chosen['snapshot'],
                'source_package_id': f'{pkg_id:04X}',
                'source_generation': chosen['generation'],
                'source_patch_id': chosen['header_patch_id'],
            })

    current_entries, merge_violations = merge_current_named_rows(current_rows)
    violations.extend(merge_violations)

    return {
        'physical_tables': physical,
        'current_packages': current_packages,
        'current_rows': current_rows,
        'current_entries': current_entries,
        'current_named_row_count': len(current_rows),
        'current_unique_tag_count': len(current_entries),
        'current_alias_row_count': len(current_rows) - len(current_entries),
        'current_class_counts': dict(Counter(x['class_hash_canonical'] for x in current_entries)),
        'current_class_row_counts': dict(Counter(x['class_hash_canonical'] for x in current_rows)),
        'current_raw_class_counts': dict(Counter(x['class_hash_raw_uint'] for x in current_entries)),
        'violations': violations,
    }


def parse_activity(c, named: dict) -> dict:
    h = norm(named['tag_hash'])
    named_class = canonical_named_class(named.get('class_hash_raw_uint', named.get('class_hash_canonical', '')))
    meta = c.entry_meta(h)
    rep = {
        'activity': h,
        'activity_name': named.get('name'),
        'activity_aliases': named.get('aliases', [named.get('name')]),
        'named_table_indices': named.get('named_table_indices', [named.get('index')]),
        'named_tag': named,
        'named_tag_class': named_class,
        'meta': meta,
        'bubble_references': [],
        'validation_ok': False,
        'violations': [],
    }
    if named_class != ACTIVITY_ROI:
        rep['violations'].append(f'named_tag_class_mismatch:{named_class}!={ACTIVITY_ROI}')
        return rep
    if not meta:
        rep['violations'].append('named_activity_tag_hash_not_present_in_file_entries')
        return rep

    rep['file_entry_reference'] = norm(meta.get('reference', ''))

    b, src = c.payload(h)
    rep['payload_source'] = src
    if b is None:
        rep['violations'].append('payload_unavailable')
        return rep
    rep['payload_bytes'] = len(b)
    if len(b) < 0x28:
        rep['violations'].append('payload_shorter_than_SActivity_ROI_0x28')
        return rep

    rep['declared_file_size'] = struct.unpack_from('<q', b, 0)[0]
    rep['location_names_raw'] = hx(u32(b, 0x08))

    arr = layer.dyn(b, 0x10, 0x04)
    rep['bubbles_array'] = arr
    if not arr['ok']:
        rep['violations'].append('bubbles_array_bounds')
        return rep

    for i in range(arr['count']):
        o = arr['absolute'] + i * 4
        bh = hx(u32(b, o))
        t = roots.target(c, bh, BUBBLE_DEFINITION)
        row = {
            'bubble_index': i,
            'offset': o,
            'bubble_definition': bh,
            'is_null_sentinel': bh in {'00000000', 'FFFFFFFF'},
            'target': t,
        }
        if row['is_null_sentinel']:
            row['skipped'] = 'null_child_map_reference'
        elif not t['reference_matches']:
            row['violation'] = 'bubble_definition_missing_or_class_mismatch'
            rep['violations'].append(f'bubble[{i}]={bh}:target_mismatch')
        else:
            row['bubble_validation'] = roots.parse_bubble(c, bh)
            if not row['bubble_validation']['validation_ok']:
                rep['violations'].append(f'bubble[{i}]={bh}:payload_validation_failed')
        rep['bubble_references'].append(row)

    rep['non_null_bubble_count'] = sum(not x['is_null_sentinel'] for x in rep['bubble_references'])
    rep['resolved_bubble_count'] = sum(
        bool(x.get('target', {}).get('reference_matches'))
        for x in rep['bubble_references'] if not x['is_null_sentinel']
    )
    rep['validation_ok'] = not rep['violations']
    return rep


def component_summary(activity: dict) -> dict:
    bubbles = []
    containers = []
    tables = []
    table_entry_counts = {}

    for br in activity.get('bubble_references', []):
        if br.get('is_null_sentinel') or not br.get('target', {}).get('reference_matches'):
            continue
        bh = norm(br['bubble_definition'])
        bubbles.append(bh)
        bv = br.get('bubble_validation') or {}
        for cr in bv.get('map_containers', []):
            if not cr.get('target', {}).get('reference_matches'):
                continue
            ch = norm(cr['map_container'])
            containers.append(ch)
            cv = cr.get('container_validation') or {}
            for tr in cv.get('map_data_tables', []):
                if not tr.get('target', {}).get('reference_matches'):
                    continue
                th = norm(tr['map_data_table'])
                tables.append(th)
                tv = tr.get('table_validation') or {}
                if tv.get('validation_ok'):
                    table_entry_counts.setdefault(th, int(tv.get('entry_count', 0)))

    bubbles = list(dict.fromkeys(bubbles))
    containers = list(dict.fromkeys(containers))
    tables = list(dict.fromkeys(tables))
    return {
        'activity': activity['activity'],
        'activity_name': activity.get('activity_name'),
        'activity_aliases': activity.get('activity_aliases'),
        'validation_ok': activity.get('validation_ok'),
        'bubble_count': len(bubbles),
        'bubbles': bubbles,
        'map_container_count': len(containers),
        'map_containers': containers,
        'map_data_table_count': len(tables),
        'map_data_tables': tables,
        'map_data_table_entry_counts': table_entry_counts,
        'total_map_entries': sum(table_entry_counts.values()),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--snapshot', type=Path, action='append', required=True)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('--activity', action='append', default=[])
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()

    paths = [p.resolve() for p in a.snapshot]
    c = v5.v3.base.Corpus(paths, a.runtime.resolve())
    named_scan = scan_named_tag_tables(paths)
    violations = list(named_scan['violations'])

    current_named = named_scan['current_entries']
    current_activity_named = [x for x in current_named if x['class_hash_canonical'] == ACTIVITY_ROI]
    current_unk_activity_named = [x for x in current_named if x['class_hash_canonical'] == UNK_ACTIVITY_ROI]
    by_hash = {x['tag_hash']: x for x in current_named}

    if a.activity:
        selected_named = []
        for raw in a.activity:
            h = norm(raw)
            n = by_hash.get(h)
            if not n:
                violations.append(f'explicit_activity_not_in_current_named_table:{h}')
                continue
            if n['class_hash_canonical'] != ACTIVITY_ROI:
                violations.append(f'explicit_activity_wrong_named_class:{h}:{n["class_hash_canonical"]}')
                continue
            selected_named.append(n)
        selection_mode = 'explicit_current_named_activity_roots'
    else:
        selected_named = current_activity_named
        selection_mode = 'all_current_named_SActivity_ROI_in_corpus'

    selected_named = list({x['tag_hash']: x for x in selected_named}.values())
    selected = [x['tag_hash'] for x in selected_named]
    if not selected:
        violations.append('no_selected_or_current_named_SActivity_ROI')

    activities = [parse_activity(c, n) for n in selected_named]
    components = [component_summary(x) for x in activities]

    for x in activities:
        if not x.get('validation_ok'):
            violations.append(f"activity:{x['activity']}:validation_failed")

    all_bubbles = list(dict.fromkeys(h for cpt in components for h in cpt.get('bubbles', [])))
    all_containers = list(dict.fromkeys(h for cpt in components for h in cpt.get('map_containers', [])))
    all_tables = list(dict.fromkeys(h for cpt in components for h in cpt.get('map_data_tables', [])))
    table_entry_counts = {}
    table_activity_owners: dict[str, list[str]] = defaultdict(list)
    bubble_activity_owners: dict[str, list[str]] = defaultdict(list)
    container_activity_owners: dict[str, list[str]] = defaultdict(list)

    for cpt in components:
        ah = cpt['activity']
        for h in cpt.get('bubbles', []):
            if ah not in bubble_activity_owners[h]: bubble_activity_owners[h].append(ah)
        for h in cpt.get('map_containers', []):
            if ah not in container_activity_owners[h]: container_activity_owners[h].append(ah)
        for h in cpt.get('map_data_tables', []):
            if ah not in table_activity_owners[h]: table_activity_owners[h].append(ah)
        for h, n in cpt.get('map_data_table_entry_counts', {}).items():
            if h in table_entry_counts and table_entry_counts[h] != n:
                violations.append(f'table_entry_count_conflict:{h}:{table_entry_counts[h]}!={n}')
            table_entry_counts[h] = n

    current_bubbles = current_hashes_by_ref(c, roots.BUBBLE_DEFINITION)
    current_containers = current_hashes_by_ref(c, roots.MAP_CONTAINER)
    current_tables = current_hashes_by_ref(c, roots.MAP_DATA_TABLE)

    if selected and not all_bubbles:
        violations.append('selected_activities_reach_no_bubbles')
    if all_bubbles and not all_containers:
        violations.append('activity_bubbles_reach_no_map_containers')
    if all_containers and not all_tables:
        violations.append('activity_containers_reach_no_map_data_tables')

    out = {
        'schema_version': 3,
        'status': 'D1_WORLD_ACTIVITY_MAP_ROOT_CENSUS_COMPLETE' if not violations else 'D1_WORLD_ACTIVITY_MAP_ROOT_CENSUS_PARTIAL',
        'pinned_source': PINNED_SOURCE,
        'selection_mode': selection_mode,
        'named_tag_discovery': {
            'physical_named_table_count': len(named_scan['physical_tables']),
            'current_package_count': len(named_scan['current_packages']),
            'current_named_tag_row_count': named_scan['current_named_row_count'],
            'current_unique_named_tag_count': named_scan['current_unique_tag_count'],
            'current_alias_row_count': named_scan['current_alias_row_count'],
            'current_named_class_counts': named_scan['current_class_counts'],
            'current_named_class_row_counts': named_scan['current_class_row_counts'],
            'current_raw_named_class_counts': named_scan['current_raw_class_counts'],
            'current_SActivity_ROI_count': len(current_activity_named),
            'current_SActivity_ROI_named_row_count': sum(x['alias_count'] for x in current_activity_named),
            'current_SUnkActivity_ROI_count': len(current_unk_activity_named),
            'current_packages': named_scan['current_packages'],
            'current_activities': current_activity_named,
            'current_unknown_activities': current_unk_activity_named,
            'physical_tables': named_scan['physical_tables'],
        },
        'current_d1_activity_count': len(current_activity_named),
        'current_d1_activity_named_row_count': sum(x['alias_count'] for x in current_activity_named),
        'current_d1_activities': [x['tag_hash'] for x in current_activity_named],
        'current_unknown_activity_count': len(current_unk_activity_named),
        'current_unknown_activities': [x['tag_hash'] for x in current_unk_activity_named],
        'selected_activity_count': len(selected),
        'selected_activities': selected,
        'reachable_bubble_count': len(all_bubbles),
        'bubble_definitions': all_bubbles,
        'reachable_map_container_count': len(all_containers),
        'map_containers': all_containers,
        'reachable_map_data_table_count': len(all_tables),
        'map_data_tables': all_tables,
        'map_data_table_entry_counts': table_entry_counts,
        'total_reachable_map_entries': sum(table_entry_counts.values()),
        'bubble_activity_owners': dict(bubble_activity_owners),
        'container_activity_owners': dict(container_activity_owners),
        'table_activity_owners': dict(table_activity_owners),
        'unowned_current_bubble_definitions': sorted(set(current_bubbles) - set(all_bubbles)),
        'unowned_current_map_containers': sorted(set(current_containers) - set(all_containers)),
        'unowned_current_map_data_tables': sorted(set(current_tables) - set(all_tables)),
        'activity_components': components,
        'activities': activities,
        'violations': violations,
        'policy': (
            'D1 Activities are discovered from current physical package named-tag '
            'tables. Same-TagHash/same-class rows are preserved as naming aliases, '
            'not duplicated Activities. Zero-count/zero-offset named tables with a '
            'zero header hash are valid absent tables. Selected SActivity_ROI payloads '
            'are walked through D1 manifest-aware Bubble -> MapContainer -> MapDataTable '
            'ownership. Unknown named activity classes remain preserved and separate.'
        ),
    }

    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({k: out[k] for k in (
        'status', 'selection_mode', 'current_d1_activity_count',
        'current_d1_activity_named_row_count', 'current_unknown_activity_count',
        'selected_activity_count', 'selected_activities', 'reachable_bubble_count',
        'bubble_definitions', 'reachable_map_container_count',
        'reachable_map_data_table_count', 'map_data_tables',
        'map_data_table_entry_counts', 'total_reachable_map_entries',
        'unowned_current_bubble_definitions', 'unowned_current_map_containers',
        'unowned_current_map_data_tables', 'violations'
    )}, indent=2))
    return 0 if not violations else 2


if __name__ == '__main__':
    raise SystemExit(main())
