#!/usr/bin/env python3
"""Trace D1 ROI named Activity -> Bubble -> MapContainer -> MapDataTable ownership.

Pinned source: MontagueM/Charm commit
50d36ee1f9ecadad7522504c20b1f3f9c97e30af.

The important D1 distinction is that Activities are *named/package-global tags*. They
must not be discovered by scanning ordinary file-entry Reference values for the
SActivity_ROI schema class. D1 Package.GetAllActivities() reads the package named-tag
table instead:

  PackageHeader +0xEC NamedTagTableCount
                +0xF0 NamedTagTableOffset
    -> 0x44-byte SPackageActivityEntry_D1 slots
       +0x00 TagHash
       +0x04 TagClassHash
       +0x08 null-terminated name bytes

For a named tag whose TagClassHash is SActivity_ROI (Charm display 2E058080; project
raw/canonical uint 8080052E), the TagHash payload is deserialized directly as:

  SActivity_ROI / 0x28
    +0x10 DynamicArray<S0A418080>, elem 0x04
      -> ChildMapReference: SBubbleDefinition / 808091E0
        +0x08 DynamicArray<SMapContainerEntry>, elem 0x04
          -> SMapContainer / 80808A54
            +0x18 DynamicArray<SMapDataTableEntry>, elem 0x04
              -> SMapDataTable / 808009A2

Only the highest physical patch generation for each package id contributes the current
named-tag table, mirroring Charm's one-current-Package-per-package-id behavior. All
physical named-tag tables are still inventoried so patch history is loss-preserving.

When --activity is omitted, every current named SActivity_ROI in the supplied corpus is
walked. Explicit --activity values are legitimate caller-selected world roots; they must
still resolve to a current named SActivity_ROI entry.
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
    'Tiger/DESTINY1_RISE_OF_IRON/Package.cs + '
    'Tiger/PackageResourcer.cs + Tiger/Schema/Activity/Activity.cs + '
    'ActivityStructsROI.cs + Tiger/Schema/Static/StaticMapData.cs'
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
    """Charm schema strings display the uint bytes in the opposite textual order."""
    h = norm(raw_uint_hex)
    return ''.join(reversed([h[i:i + 2] for i in range(0, 8, 2)]))


def canonical_named_class(raw_uint_hex: str) -> str:
    """Normalize either project/raw uint or Charm byte-display notation."""
    h = norm(raw_uint_hex)
    aliases = {
        ACTIVITY_ROI: ACTIVITY_ROI,
        charm_display(ACTIVITY_ROI): ACTIVITY_ROI,
        UNK_ACTIVITY_ROI: UNK_ACTIVITY_ROI,
        charm_display(UNK_ACTIVITY_ROI): UNK_ACTIVITY_ROI,
    }
    return aliases.get(h, h)


def current_hashes_by_ref(c, reference: str) -> list[str]:
    out = []
    for h in c.occ:
        m = c.entry_meta(h)
        if m and norm(m.get('reference')) == reference:
            out.append(norm(h))
    return sorted(set(out))


def scan_named_tag_tables(paths: list[Path]) -> dict:
    """Inventory all physical named tables and choose the highest patch per package id."""
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
        sha_matches = actual_sha.lower() == expected_sha if expected_sha else None
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
            'entries': entries,
        }
        physical.append(row)
        by_pkg[int(h['pkg_id'])].append(row)

    current_packages = []
    current_entries = []
    for pkg_id, rows in sorted(by_pkg.items()):
        # Header patch id is authoritative; filename generation is a deterministic
        # secondary key for equal/odd historical headers.
        chosen = max(rows, key=lambda r: (r['header_patch_id'], r['generation']))
        current_packages.append({
            'package_id': f'{pkg_id:04X}',
            'snapshot': chosen['snapshot'],
            'generation': chosen['generation'],
            'header_patch_id': chosen['header_patch_id'],
            'named_tag_table_count': chosen['named_tag_table_count'],
        })
        for e in chosen['entries']:
            raw_cls = norm(e['class_hash'])
            current_entries.append({
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

    # FileHash includes package id, so duplicate current TagHashes are not expected.
    dup = Counter(x['tag_hash'] for x in current_entries)
    duplicate_current = {h: n for h, n in dup.items() if n != 1}
    if duplicate_current:
        violations.append('duplicate_current_named_tag_hashes:' + json.dumps(duplicate_current, sort_keys=True))

    return {
        'physical_tables': physical,
        'current_packages': current_packages,
        'current_entries': current_entries,
        'current_class_counts': dict(Counter(x['class_hash_canonical'] for x in current_entries)),
        'current_raw_class_counts': dict(Counter(x['class_hash_raw_uint'] for x in current_entries)),
        'duplicate_current_tag_hashes': duplicate_current,
        'violations': violations,
    }


def parse_activity(c, named: dict) -> dict:
    h = norm(named['tag_hash'])
    named_class = canonical_named_class(named.get('class_hash_raw_uint', named.get('class_hash_canonical', '')))
    meta = c.entry_meta(h)
    rep = {
        'activity': h,
        'activity_name': named.get('name'),
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

    # D1 named/global tags are not classed by the ordinary file-entry Reference.
    # Preserve that reference as evidence, but do not require it to equal 8080052E.
    rep['file_entry_reference'] = norm(meta.get('reference', ''))
    rep['file_entry_reference_is_activity_class'] = rep['file_entry_reference'] == ACTIVITY_ROI

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
    # LocationNames is a Tag at +0x08. It is retained as evidence but is not
    # required for map ownership closure.
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

    # Preserve source order while deduplicating shared roots.
    bubbles = list(dict.fromkeys(bubbles))
    containers = list(dict.fromkeys(containers))
    tables = list(dict.fromkeys(tables))
    return {
        'activity': activity['activity'],
        'activity_name': activity.get('activity_name'),
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
                violations.append(
                    f'explicit_activity_wrong_named_class:{h}:{n["class_hash_canonical"]}'
                )
                continue
            selected_named.append(n)
        selection_mode = 'explicit_current_named_activity_roots'
    else:
        selected_named = current_activity_named
        selection_mode = 'all_current_named_SActivity_ROI_in_corpus'

    # Deduplicate explicit arguments without changing named-table source order.
    selected_named = list({x['tag_hash']: x for x in selected_named}.values())
    selected = [x['tag_hash'] for x in selected_named]
    if not selected:
        violations.append('no_selected_or_current_named_SActivity_ROI')

    activities = [parse_activity(c, n) for n in selected_named]
    components = [component_summary(x) for x in activities]

    for x in activities:
        if not x.get('validation_ok'):
            violations.append(f"activity:{x['activity']}:validation_failed")

    all_bubbles = list(dict.fromkeys(
        h for cpt in components for h in cpt.get('bubbles', [])
    ))
    all_containers = list(dict.fromkeys(
        h for cpt in components for h in cpt.get('map_containers', [])
    ))
    all_tables = list(dict.fromkeys(
        h for cpt in components for h in cpt.get('map_data_tables', [])
    ))
    table_entry_counts = {}
    table_activity_owners: dict[str, list[str]] = defaultdict(list)
    bubble_activity_owners: dict[str, list[str]] = defaultdict(list)
    container_activity_owners: dict[str, list[str]] = defaultdict(list)

    for cpt in components:
        ah = cpt['activity']
        for h in cpt.get('bubbles', []):
            if ah not in bubble_activity_owners[h]:
                bubble_activity_owners[h].append(ah)
        for h in cpt.get('map_containers', []):
            if ah not in container_activity_owners[h]:
                container_activity_owners[h].append(ah)
        for h in cpt.get('map_data_tables', []):
            if ah not in table_activity_owners[h]:
                table_activity_owners[h].append(ah)
        for h, n in cpt.get('map_data_table_entry_counts', {}).items():
            if h in table_entry_counts and table_entry_counts[h] != n:
                violations.append(
                    f'table_entry_count_conflict:{h}:{table_entry_counts[h]}!={n}'
                )
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
        'schema_version': 2,
        'status': 'D1_WORLD_ACTIVITY_MAP_ROOT_CENSUS_COMPLETE' if not violations else 'D1_WORLD_ACTIVITY_MAP_ROOT_CENSUS_PARTIAL',
        'pinned_source': PINNED_SOURCE,
        'selection_mode': selection_mode,
        'named_tag_discovery': {
            'physical_named_table_count': len(named_scan['physical_tables']),
            'current_package_count': len(named_scan['current_packages']),
            'current_named_tag_count': len(current_named),
            'current_named_class_counts': named_scan['current_class_counts'],
            'current_raw_named_class_counts': named_scan['current_raw_class_counts'],
            'current_SActivity_ROI_count': len(current_activity_named),
            'current_SUnkActivity_ROI_count': len(current_unk_activity_named),
            'current_packages': named_scan['current_packages'],
            'current_activities': current_activity_named,
            'current_unknown_activities': current_unk_activity_named,
            'duplicate_current_tag_hashes': named_scan['duplicate_current_tag_hashes'],
            'physical_tables': named_scan['physical_tables'],
        },
        'current_d1_activity_count': len(current_activity_named),
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
            'D1 Activities are discovered from the current physical package named-tag '
            'tables, not from ordinary file-entry Reference classes. Only current named '
            'SActivity_ROI tags are walked by default. Their payloads are interpreted '
            'using the pinned +0x10 Bubbles schema, then ownership is followed through '
            'SBubbleDefinition -> SMapContainer -> SMapDataTable. Unknown named '
            'activity-class tags are preserved but are not coerced into SActivity_ROI.'
        ),
    }

    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({k: out[k] for k in (
        'status', 'selection_mode', 'current_d1_activity_count',
        'current_unknown_activity_count', 'selected_activity_count', 'selected_activities',
        'reachable_bubble_count', 'bubble_definitions',
        'reachable_map_container_count', 'reachable_map_data_table_count',
        'map_data_tables', 'map_data_table_entry_counts',
        'total_reachable_map_entries', 'unowned_current_bubble_definitions',
        'unowned_current_map_containers', 'unowned_current_map_data_tables',
        'violations'
    )}, indent=2))
    return 0 if not violations else 2


if __name__ == '__main__':
    raise SystemExit(main())
