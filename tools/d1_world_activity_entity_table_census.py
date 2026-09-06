#!/usr/bin/env python3
"""Loss-preserving D1 ROI activity entity/data-table census.

This follows the native-era Charm D1 activity path used by
Activity.EnumerateActivityEntities/CollapseResourceParent, but reports the
serialized hashes/arrays rather than inventing entity semantics:

SUnkActivity_ROI (named/global class 80800616)
  Unk48[] S0C068080
    Unk08[] SA8068080
      +0x34 SF0088080 tag
        +0x1C untyped child FileHash
          child arrays +0x08/+0x18/+0x28 -> S6E078080 tags
            +0x30 SE9058080[]
              +0x10 SMapDataTable
              +0x18 S22428080[] -> SF6038080 entity-resource table

D1 SUnkActivity_ROI is selected from the package named-tag table, exactly like
SActivity_ROI. The ordinary file-entry Reference for the named TagHash is retained
as evidence but is not incorrectly required to equal the named class.

When --named-root-snapshot is supplied, only those packages are permitted to select
activity roots while the broader --snapshot corpus remains available for dependency
resolution. This prevents shared dependency packages from accidentally widening a
world-specific activity selection.
"""
from __future__ import annotations

import argparse
import json
import struct
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import d1_tower_map_schema_validate_v5 as v5
import d1_world_activity_map_root_census as named_roots

CLS_UNK_ACTIVITY = '80800616'
CLS_F008 = '808008F0'
CLS_6E07 = '8080076E'
CLS_MAP_TABLE = '808009A2'
CLS_F603 = '808003F6'
NULLS = {'00000000', 'FFFFFFFF'}
PINNED_SOURCE = (
    'MontagueM/Charm@50d36ee1f9ecadad7522504c20b1f3f9c97e30af '
    'Tiger/DESTINY1_RISE_OF_IRON/Package.cs + Tiger/PackageResourcer.cs + '
    'Tiger/Schema/Activity/Activity.cs + ActivityStructsROI.cs'
)


def norm(x):
    return str(x).upper().removeprefix('0X').zfill(8)


def hx(v):
    return f'{v:08X}'


def i32(b, o):
    return struct.unpack_from('<i', b, o)[0]


def u32(b, o):
    return struct.unpack_from('<I', b, o)[0]


def i64(b, o):
    return struct.unpack_from('<q', b, o)[0]


def pkgid(h: str) -> str | None:
    h = norm(h)
    if h in NULLS:
        return None
    v = int(h, 16) - 0x80800000
    if v < 0:
        return None
    return f'{(v >> 13) & 0x7ff:04x}'


def dyn(b: bytes, off: int, stride: int):
    if off + 0x10 > len(b):
        return {'ok': False, 'field_offset': off, 'error': 'descriptor_oob'}
    count = i32(b, off)
    unk = u32(b, off + 4)
    rel = i64(b, off + 8)
    absolute = off + 8 + rel + 0x10
    end = absolute + max(count, 0) * stride
    return {
        'ok': count >= 0 and absolute >= 0 and end <= len(b),
        'field_offset': off,
        'count': count,
        'unknown04': unk,
        'relative': rel,
        'absolute': absolute,
        'end': end,
        'stride': stride,
        'payload_size': len(b),
    }


def meta(c, h, expected=None):
    h = norm(h)
    m = c.entry_meta(h)
    return {
        'hash': h,
        'package_id': pkgid(h),
        'exists': m is not None,
        'meta': m,
        'expected_class': expected,
        'class_matches': bool(m and (expected is None or norm(m.get('reference')) == expected)),
        'is_null_sentinel': h in NULLS,
    }


def payload(c, h):
    b, s = c.payload(norm(h))
    return b, s


def arr_hashes(b, desc, offset=0):
    if not desc.get('ok'):
        return []
    return [hx(u32(b, desc['absolute'] + i * desc['stride'] + offset)) for i in range(desc['count'])]


def parse_s6e(c, h, violations):
    h = norm(h)
    m = meta(c, h, CLS_6E07)
    b, src = payload(c, h)
    r = {'hash': h, 'target': m, 'source': src, 'stages': []}
    if not m['class_matches'] or b is None:
        r['error'] = 'class_or_payload_unavailable'
        return r
    a = dyn(b, 0x30, 0x28)
    r['unk30_array'] = a
    if not a['ok']:
        violations.append(f'{h}: S6E Unk30 bounds')
        return r
    for i in range(a['count']):
        o = a['absolute'] + i * 0x28
        table = hx(u32(b, o + 0x10))
        sub = dyn(b, o + 0x18, 4)
        subs = arr_hashes(b, sub)
        row = {
            'index': i,
            'record_offset': o,
            'map_data_table': meta(c, table, CLS_MAP_TABLE),
            'entity_resource_array': sub,
            'entity_resource_tables': [meta(c, x, CLS_F603) for x in subs],
        }
        r['stages'].append(row)
    return r


def parse_f008(c, h, violations):
    h = norm(h)
    m = meta(c, h, CLS_F008)
    b, src = payload(c, h)
    r = {'hash': h, 'target': m, 'source': src, 'groups': []}
    if not m['class_matches'] or b is None:
        r['error'] = 'class_or_payload_unavailable'
        return r
    if len(b) < 0x20:
        r['error'] = 'short_f008'
        violations.append(f'{h}: short F008')
        return r
    child = hx(u32(b, 0x1C))
    cb, csrc = payload(c, child)
    r['child'] = {
        'hash': child,
        'package_id': pkgid(child),
        'meta': c.entry_meta(child),
        'source': csrc,
        'payload_bytes': None if cb is None else len(cb),
    }
    if cb is None:
        r['error'] = 'child_payload_unavailable'
        return r
    if len(cb) < 0x38:
        r['error'] = 'short_child'
        violations.append(f'{h}: short F008 child {child}')
        return r
    for slot, off in enumerate((0x08, 0x18, 0x28)):
        a = dyn(cb, off, 4)
        vals = arr_hashes(cb, a)
        g = {'slot': slot, 'field_offset': off, 'array': a, 'resources': []}
        if not a['ok']:
            violations.append(f'{h}/{child}: child array {slot} bounds')
        else:
            for x in vals:
                g['resources'].append(parse_s6e(c, x, violations))
        r['groups'].append(g)
    return r


def parse_activity(c, named, violations):
    h = norm(named['tag_hash'])
    named_class = named_roots.canonical_named_class(
        named.get('class_hash_raw_uint', named.get('class_hash_canonical', ''))
    )
    entry = c.entry_meta(h)
    b, src = payload(c, h)
    r = {
        'hash': h,
        'activity_name': named.get('name'),
        'activity_aliases': named.get('aliases', [named.get('name')]),
        'named_table_indices': named.get('named_table_indices', [named.get('index')]),
        'named_tag': named,
        'named_tag_class': named_class,
        'file_entry': meta(c, h),
        'file_entry_reference': None if entry is None else norm(entry.get('reference')),
        'source': src,
        'locations': [],
    }
    if named_class != CLS_UNK_ACTIVITY:
        r['error'] = 'named_class_mismatch'
        violations.append(f'{h}: named class {named_class} != {CLS_UNK_ACTIVITY}')
        return r
    if entry is None or b is None:
        r['error'] = 'named_tag_payload_unavailable'
        return r
    if len(b) < 0x58:
        r['error'] = 'short_activity'
        violations.append(f'{h}: short activity')
        return r
    a = dyn(b, 0x48, 0x18)
    r['unk48_array'] = a
    if not a['ok']:
        violations.append(f'{h}: Unk48 bounds')
        return r
    for i in range(a['count']):
        o = a['absolute'] + i * 0x18
        loc_hash = hx(u32(b, o))
        inner = dyn(b, o + 0x08, 0x3C)
        loc = {
            'index': i,
            'record_offset': o,
            'location_name_hash': loc_hash,
            'unk08_array': inner,
            'activity_entity_groups': [],
        }
        if not inner['ok']:
            violations.append(f'{h}: location {i} inner bounds')
        else:
            for j in range(inner['count']):
                q = inner['absolute'] + j * 0x3C
                phase = hx(u32(b, q + 0x04))
                bubble = hx(u32(b, q + 0x30))
                parent = hx(u32(b, q + 0x34))
                loc['activity_entity_groups'].append({
                    'index': j,
                    'record_offset': q,
                    'phase_name_hash': phase,
                    'bubble_name_hash': bubble,
                    'resource_parent': parse_f008(c, parent, violations),
                })
        r['locations'].append(loc)
    return r


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--snapshot', type=Path, action='append', required=True,
                    help='Full dependency corpus used to resolve serialized hashes.')
    ap.add_argument('--named-root-snapshot', type=Path, action='append', default=[],
                    help='Optional world-root package subset used only for named activity selection.')
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('--activity', action='append', default=[])
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()

    paths = [p.resolve() for p in a.snapshot]
    named_paths = [p.resolve() for p in a.named_root_snapshot] if a.named_root_snapshot else paths
    c = v5.v3.base.Corpus(paths, a.runtime.resolve())
    named_scan = named_roots.scan_named_tag_tables(named_paths)
    violations = list(named_scan.get('violations', []))
    current_named = named_scan['current_entries']
    current_unk = [x for x in current_named if x['class_hash_canonical'] == CLS_UNK_ACTIVITY]
    by_hash = {x['tag_hash']: x for x in current_unk}

    if a.activity:
        selected = []
        for raw in a.activity:
            h = norm(raw)
            n = by_hash.get(h)
            if n is None:
                violations.append(f'explicit_activity_not_current_named_80800616:{h}')
            else:
                selected.append(n)
    else:
        selected = current_unk

    acts = [parse_activity(c, n, violations) for n in selected]
    table_hashes = []
    null_table_refs = 0
    f603 = []
    s6es = []
    f008s = []
    unresolved = []
    for act in acts:
        if act.get('file_entry', {}).get('exists') is False:
            unresolved.append(act['hash'])
        for loc in act.get('locations', []):
            for eg in loc.get('activity_entity_groups', []):
                p = eg.get('resource_parent') or {}
                f008s.append(p.get('hash'))
                if p.get('hash') and not p.get('target', {}).get('exists'):
                    unresolved.append(p['hash'])
                ch = p.get('child') or {}
                if ch.get('hash') and ch.get('meta') is None:
                    unresolved.append(ch['hash'])
                for g in p.get('groups', []):
                    for rr in g.get('resources', []):
                        s6es.append(rr.get('hash'))
                        if not rr.get('target', {}).get('exists'):
                            unresolved.append(rr.get('hash'))
                        for st in rr.get('stages', []):
                            t = st['map_data_table']
                            if t['hash'] in NULLS:
                                null_table_refs += 1
                            else:
                                table_hashes.append(t['hash'])
                                if not t['exists']:
                                    unresolved.append(t['hash'])
                            for er in st['entity_resource_tables']:
                                if er['hash'] in NULLS:
                                    continue
                                f603.append(er['hash'])
                                if not er['exists']:
                                    unresolved.append(er['hash'])
    unresolved = [h for h in unresolved if h and norm(h) not in NULLS]

    out = {
        'schema_version': 3,
        'status': 'D1_ACTIVITY_ENTITY_TABLE_CENSUS' if not violations else 'D1_ACTIVITY_ENTITY_TABLE_CENSUS_WITH_LAYOUT_VIOLATIONS',
        'activity_class': CLS_UNK_ACTIVITY,
        'named_root_mode': 'isolated_named_root_snapshots' if a.named_root_snapshot else 'full_snapshot_corpus',
        'named_root_snapshots': [p.name for p in named_paths],
        'named_tag_discovery': {
            'current_package_count': len(named_scan['current_packages']),
            'current_named_row_count': named_scan['current_named_row_count'],
            'current_unique_tag_count': named_scan['current_unique_tag_count'],
            'current_class_counts': named_scan['current_class_counts'],
            'current_80800616_count': len(current_unk),
            'selected_80800616_count': len(selected),
            'selected_activities': [
                {
                    'tag_hash': x['tag_hash'],
                    'name': x.get('name'),
                    'aliases': x.get('aliases', []),
                    'source_package_id': x.get('source_package_id'),
                }
                for x in selected
            ],
        },
        'activity_count': len(acts),
        'activities': acts,
        'summary': {
            'resource_parent_count': len([x for x in f008s if x]),
            'unique_resource_parents': len(set(x for x in f008s if x)),
            's6e_resource_count': len([x for x in s6es if x]),
            'unique_s6e_resources': len(set(x for x in s6es if x)),
            'map_data_table_refs': len(table_hashes),
            'null_map_data_table_refs': null_table_refs,
            'unique_map_data_tables': len(set(table_hashes)),
            'f603_entity_resource_refs': len(f603),
            'unique_f603_entity_resources': len(set(f603)),
            'unresolved_hash_count': len(unresolved),
            'unique_unresolved_hashes': len(set(unresolved)),
            'unresolved_package_ids': dict(Counter(pkgid(h) for h in unresolved if pkgid(h))),
        },
        'unique_map_data_tables': sorted(set(table_hashes)),
        'unique_f603_entity_resources': sorted(set(f603)),
        'unresolved_hashes': sorted(set(unresolved)),
        'violations': violations,
        'pinned_source': PINNED_SOURCE,
        'policy': (
            'SUnkActivity_ROI ownership comes from the current D1 package named-tag table. '
            'Ordinary file-entry Reference is evidence only for the named activity itself. '
            'Null map-data-table sentinels are preserved in stage records but excluded from '
            'dependency counts. This is serialized activity ownership/dependency evidence and '
            'does not claim every activity data table is simultaneously active in one runtime phase.'
        ),
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({
        'status': out['status'],
        'activity_count': len(acts),
        'named_80800616_count': len(current_unk),
        **out['summary'],
        'violations': violations,
    }, indent=2))
    return 0 if not violations else 2


if __name__ == '__main__':
    raise SystemExit(main())
