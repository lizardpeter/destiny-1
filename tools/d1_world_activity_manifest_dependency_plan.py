#!/usr/bin/env python3
"""Derive D1 shared-manifest package dependencies from named Activity child Tags.

This is a deliberately *pre-manifest* planning pass. It needs only the physical world
root corpus containing the named SActivity_ROI tag and its referenced child TagHash file
entries. It does not need the shared-manifest packages yet.

Pinned D1 source establishes two facts:

1. SActivity_ROI +0x10 is DynamicArray<S0A418080>, whose 4-byte value is a
   Tag<SBubbleDefinition> ChildMapReference.
2. D1 global Tags whose ordinary file-entry Reference is not the class itself resolve
   that Reference as a FileHash to an S48018080 manifest parent
   (FileHash.GetReferenceFromManifest()).

Therefore, for every selected/current named SActivity_ROI child Bubble Tag:

- if its ordinary file-entry Reference is already 808091E0, no manifest package is
  required for that edge;
- otherwise that Reference is preserved as the candidate S48018080 parent FileHash and
  its encoded package id is emitted as a required manifest package dependency.

No package IDs are accepted as inputs. World-specific values such as Tower's 0430/0431
must be consequences of the serialized child references and may only be asserted later
as regressions.
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
import d1_world_map_data_layer_census as layer
from d1_world_activity_map_root_census import ACTIVITY_ROI, scan_named_tag_tables, norm

BUBBLE_DEFINITION = '808091E0'
PINNED_SOURCE = (
    'MontagueM/Charm@50d36ee1f9ecadad7522504c20b1f3f9c97e30af '
    'Tiger/Schema/Activity/ActivityStructsROI.cs + '
    'Tiger/TigerHash.cs::FileHash.PackageId/GetReferenceFromManifest'
)


def hx(v: int) -> str:
    return f'{v:08X}'


def u32(b: bytes, o: int) -> int:
    return struct.unpack_from('<I', b, o)[0]


def filehash_package_id(raw_hash: str) -> int:
    """Exact D1 FileHash.PackageId calculation from pinned Charm TigerHash.cs."""
    v = int(norm(raw_hash), 16)
    bank = (v >> 0x17) & 0x3
    # Valid D1 FileHashes use bank 1..3. Keep invalid results explicit rather than
    # wrapping the subtraction as an unsigned integer.
    if bank == 0:
        raise ValueError(f'{norm(raw_hash)} has invalid D1 FileHash bank 0')
    return ((v >> 0x0D) & 0x3FF) + (bank - 1) * 0x400


def merge_activity_named_rows(named_scan: dict) -> list[dict]:
    return [
        x for x in named_scan.get('current_entries', [])
        if x.get('class_hash_canonical') == ACTIVITY_ROI
    ]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--snapshot', type=Path, action='append', required=True)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('--activity', action='append', default=[])
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--package-id-list', type=Path)
    a = ap.parse_args()

    paths = [p.resolve() for p in a.snapshot]
    c = v5.v3.base.Corpus(paths, a.runtime.resolve())
    named = scan_named_tag_tables(paths)
    violations = list(named.get('violations', []))

    current_activities = merge_activity_named_rows(named)
    by_hash = {x['tag_hash']: x for x in current_activities}
    if a.activity:
        selected = []
        for raw in a.activity:
            h = norm(raw)
            row = by_hash.get(h)
            if row is None:
                violations.append(f'explicit_activity_not_current_named_SActivity_ROI:{h}')
            else:
                selected.append(row)
    else:
        selected = current_activities
    selected = list({x['tag_hash']: x for x in selected}.values())
    if not selected:
        violations.append('no_selected_or_current_named_SActivity_ROI')

    activities = []
    edges = []
    package_ids = []
    for named_activity in selected:
        ah = norm(named_activity['tag_hash'])
        b, src = c.payload(ah)
        ar = {
            'activity': ah,
            'activity_name': named_activity.get('name'),
            'aliases': named_activity.get('aliases', [named_activity.get('name')]),
            'payload_source': src,
            'payload_bytes': None if b is None else len(b),
            'bubbles_array': None,
            'child_edges': [],
            'violations': [],
        }
        if b is None or len(b) < 0x28:
            ar['violations'].append('activity_payload_unavailable_or_short')
            violations.append(f'activity:{ah}:payload_unavailable_or_short')
            activities.append(ar)
            continue

        arr = layer.dyn(b, 0x10, 0x04)
        ar['bubbles_array'] = arr
        if not arr['ok']:
            ar['violations'].append('activity_bubbles_array_bounds')
            violations.append(f'activity:{ah}:bubbles_array_bounds')
            activities.append(ar)
            continue

        for i in range(arr['count']):
            o = arr['absolute'] + i * 4
            child = hx(u32(b, o))
            meta = c.entry_meta(child)
            edge = {
                'activity': ah,
                'bubble_index': i,
                'bubble_tag': child,
                'bubble_tag_meta': meta,
                'ordinary_reference': None,
                'reference_mode': None,
                'manifest_parent_hash': None,
                'manifest_package_id': None,
                'manifest_package_id_hex': None,
                'violations': [],
            }
            if child in {'00000000', 'FFFFFFFF'}:
                edge['reference_mode'] = 'null_child'
            elif meta is None:
                edge['violations'].append('bubble_tag_file_entry_missing')
                violations.append(f'activity:{ah}:bubble[{i}]={child}:file_entry_missing')
            else:
                ref = norm(meta.get('reference', ''))
                edge['ordinary_reference'] = ref
                if ref == BUBBLE_DEFINITION:
                    edge['reference_mode'] = 'direct_class_reference'
                else:
                    edge['reference_mode'] = 'd1_manifest_parent_filehash'
                    edge['manifest_parent_hash'] = ref
                    try:
                        pid = filehash_package_id(ref)
                    except ValueError as ex:
                        edge['violations'].append(str(ex))
                        violations.append(f'activity:{ah}:bubble[{i}]={child}:{ex}')
                    else:
                        edge['manifest_package_id'] = pid
                        edge['manifest_package_id_hex'] = f'{pid:04X}'
                        package_ids.append(pid)
            ar['child_edges'].append(edge)
            edges.append(edge)
        activities.append(ar)

    package_ids = sorted(set(package_ids))
    mode_counts = Counter(x.get('reference_mode') or 'UNRESOLVED' for x in edges)
    out = {
        'schema_version': 1,
        'status': 'D1_WORLD_ACTIVITY_MANIFEST_DEPENDENCY_PLAN_COMPLETE' if not violations else 'D1_WORLD_ACTIVITY_MANIFEST_DEPENDENCY_PLAN_PARTIAL',
        'pinned_source': PINNED_SOURCE,
        'selection_mode': 'explicit_current_named_activity_roots' if a.activity else 'all_current_named_SActivity_ROI_in_corpus',
        'selected_activity_count': len(selected),
        'selected_activities': [x['tag_hash'] for x in selected],
        'child_edge_count': len(edges),
        'reference_mode_counts': dict(mode_counts),
        'manifest_parent_edge_count': sum(x.get('reference_mode') == 'd1_manifest_parent_filehash' for x in edges),
        'direct_class_edge_count': sum(x.get('reference_mode') == 'direct_class_reference' for x in edges),
        'manifest_package_id_count': len(package_ids),
        'manifest_package_ids': [f'{x:04X}' for x in package_ids],
        'manifest_parent_hashes': sorted({x['manifest_parent_hash'] for x in edges if x.get('manifest_parent_hash')}),
        'activities': activities,
        'child_edges': edges,
        'violations': violations,
        'policy': (
            'Shared-manifest package dependencies are derived only from ordinary '
            'file-entry References of serialized SActivity_ROI ChildMapReference Tags. '
            'The tool accepts no manifest package IDs. The returned package IDs are a '
            'physical dependency plan for the later manifest-aware class-resolution pass.'
        ),
    }

    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=2) + '\n')
    if a.package_id_list:
        a.package_id_list.parent.mkdir(parents=True, exist_ok=True)
        a.package_id_list.write_text('\n'.join(out['manifest_package_ids']) + ('\n' if package_ids else ''))

    print(json.dumps({k: out[k] for k in (
        'status', 'selected_activity_count', 'selected_activities', 'child_edge_count',
        'reference_mode_counts', 'manifest_parent_edge_count', 'direct_class_edge_count',
        'manifest_package_id_count', 'manifest_package_ids', 'manifest_parent_hashes',
        'violations'
    )}, indent=2))
    return 0 if not violations else 2


if __name__ == '__main__':
    raise SystemExit(main())
