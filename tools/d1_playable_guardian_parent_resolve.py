#!/usr/bin/env python3
"""Resolve named D1 playable-Guardian art assignments to final EntityDataROI hashes.

Input is the evidence-gated output of d1-playable-guardian-arrangement-join.  Each
row already carries the exact retail art-arrangement assignment hashes and their
EntityParent FileHashes.  This tool performs the next serialized edge:

  InventoryItem -> gearArtArrangementIndex -> assignment -> EntityParent
      -> EntityDataROI FileHash

The historical item name/class/type metadata is presentation metadata only.  The
assignment, EntityParent and EntityDataROI edges are all read from retail bytes.
Masculine/feminine roles are preserved by matching each assignment hash to the
parallel parent list emitted by the D1 arrangement decoder.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from d1_investment_arrangement_probe import filehash_pkg_index
from d1_remote_investment_parent_probe import Member, RemoteLogicalPackage
from d1_split_tar_extract import SplitHttpTar


def parse_catalog(path: Path, needed: set[int]) -> dict[int, dict[int, Member]]:
    src = json.loads(path.read_text())
    families = src.get('families', {})
    out: dict[int, dict[int, Member]] = {}
    for pkg in sorted(needed):
        key = f'{pkg:04X}'
        rows = families.get(key) or families.get(key.lower())
        if not rows:
            continue
        fam: dict[int, Member] = {}
        for row in rows:
            name = row['name']
            off = int(str(row['data_offset']), 0)
            size = int(row['size'])
            # Final suffix is the patch generation.
            patch = int(name.rsplit('_', 1)[1].split('.', 1)[0])
            fam[patch] = Member(name, off, size, pkg, patch)
        if fam:
            out[pkg] = fam
    return out


def assignment_role_map(row: dict) -> dict[str, str]:
    """Return assignment hash -> body-role without relying on list order."""
    out: dict[str, str] = {}
    masc = str(row.get('masculine_single_assignment') or '').upper()
    fem = str(row.get('feminine_single_assignment') or '').upper()
    if masc not in ('', '00000000', 'FFFFFFFF'):
        out[masc] = 'masculine'
    if fem not in ('', '00000000', 'FFFFFFFF'):
        # If retail ever serializes the same assignment for both, record shared.
        out[fem] = 'shared' if fem in out else 'feminine'
    return out


def parent_rows(row: dict) -> list[dict]:
    assignments = [str(x).upper() for x in row.get('assignment_hashes', [])]
    parents = row.get('entity_parents', [])
    roles = assignment_role_map(row)
    out = []
    for i, p in enumerate(parents):
        if isinstance(p, dict):
            ph = str(p.get('hash') or '').upper()
        else:
            ph = str(p or '').upper()
        if not ph:
            continue
        ah = assignments[i] if i < len(assignments) else None
        out.append({
            'assignment_hash': ah,
            'body_role': roles.get(ah, 'multiple_or_unclassified') if ah else 'unclassified',
            'parent_hash': ph,
        })
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('guardian_join', type=Path)
    ap.add_argument('--member-catalog', type=Path, required=True)
    ap.add_argument('--base-url', required=True)
    ap.add_argument('--part-count', type=int, default=10)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('-o', '--output', type=Path, required=True)
    a = ap.parse_args()

    src = json.loads(a.guardian_join.read_text())
    arrangements = src.get('arrangements', [])

    unique_parents: dict[str, dict] = {}
    needed_pkgs: set[int] = set()
    arrangement_links: dict[tuple[str, int], list[dict]] = {}
    for row in arrangements:
        key = (str(row.get('className')), int(row['arrangement_index']))
        links = parent_rows(row)
        arrangement_links[key] = links
        for link in links:
            ph = link['parent_hash']
            pkg, idx = filehash_pkg_index(int(ph, 16))
            needed_pkgs.add(pkg)
            unique_parents.setdefault(ph, {'parent_hash': ph, 'package_id': pkg, 'file_index': idx})

    catalog = parse_catalog(a.member_catalog, needed_pkgs)
    missing_catalog = sorted(needed_pkgs - set(catalog))
    base = a.base_url.rstrip('/')
    arc = SplitHttpTar([f'{base}/packages.tar.{i:03d}' for i in range(1, a.part_count + 1)], retries=6, timeout=90)
    views = {pkg: RemoteLogicalPackage(arc, members, a.runtime) for pkg, members in sorted(catalog.items())}

    resolved: dict[str, dict] = {}
    errors = []
    for n, ph in enumerate(sorted(unique_parents), 1):
        seed = unique_parents[ph]
        pkg = int(seed['package_id']); idx = int(seed['file_index'])
        rec = dict(seed)
        r = views.get(pkg)
        if r is None:
            rec.update({'resolved': False, 'reason': 'package family absent from verified member catalog'})
            resolved[ph] = rec
            continue
        if idx >= len(r.entries):
            rec.update({'resolved': False, 'reason': 'file index outside logical entry table'})
            resolved[ph] = rec
            continue
        e = r.entries[idx]
        rec.update({'logical_view': r.view.name, 'reference': e['reference'].upper(), 'size': e['file_size']})
        if e['tag_hash'].upper() != ph:
            rec.update({'resolved': False, 'reason': f"logical tag mismatch {e['tag_hash']}"})
            resolved[ph] = rec
            continue
        try:
            b = r.entry(idx)
            if len(b) < 0x14:
                raise RuntimeError(f'EntityParent payload too short: {len(b)}')
            entity = struct.unpack_from('<I', b, 0x10)[0]
            if entity in (0, 0xFFFFFFFF):
                raise RuntimeError(f'null EntityDataROI hash {entity:08X}')
            epkg, eidx = filehash_pkg_index(entity)
            rec.update({
                'resolved': True,
                'entity_data_hash': f'{entity:08X}',
                'entity_data_package_id': epkg,
                'entity_data_file_index': eidx,
                'payload_sha256': hashlib.sha256(b).hexdigest(),
            })
        except Exception as ex:
            rec.update({'resolved': False, 'reason': repr(ex)})
            errors.append({'parent_hash': ph, 'error': repr(ex)})
        resolved[ph] = rec
        if n % 250 == 0:
            print(f'parents {n}/{len(unique_parents)} resolved={sum(bool(x.get("resolved")) for x in resolved.values())}', flush=True)

    entity_pkgs = collections.Counter()
    body_roles = collections.Counter()
    class_entities: dict[str, set[str]] = collections.defaultdict(set)
    augmented = []
    for row in arrangements:
        key = (str(row.get('className')), int(row['arrangement_index']))
        links = []
        for link in arrangement_links.get(key, []):
            p = resolved.get(link['parent_hash'], {})
            x = {**link, 'parent_resolution': p}
            if p.get('resolved'):
                eh = p['entity_data_hash']
                entity_pkgs[f"{int(p['entity_data_package_id']):04X}"] += 1
                body_roles[link['body_role']] += 1
                class_entities[str(row.get('className'))].add(eh)
                x['entity_data_hash'] = eh
                x['entity_data_package_id'] = int(p['entity_data_package_id'])
                x['entity_data_file_index'] = int(p['entity_data_file_index'])
            links.append(x)
        augmented.append({**row, 'resolved_body_assignments': links})

    # Attach the same exact arrangement result to individual named inventory items.
    by_key = {(x['className'], int(x['arrangement_index'])): x for x in augmented}
    named_items = []
    for item in src.get('items', []):
        g = by_key.get((item.get('className'), int(item['arrangement_index'])))
        named_items.append({**item, 'resolved_body_assignments': g.get('resolved_body_assignments', []) if g else []})

    report = {
        'schema': 'd1_playable_guardian_parent_resolve/v1',
        'source_schema': src.get('schema'),
        'arrangement_count': len(arrangements),
        'named_item_count': len(named_items),
        'unique_parent_count': len(unique_parents),
        'resolved_parent_count': sum(bool(x.get('resolved')) for x in resolved.values()),
        'unresolved_parent_count': sum(not bool(x.get('resolved')) for x in resolved.values()),
        'needed_parent_package_ids': [f'{x:04X}' for x in sorted(needed_pkgs)],
        'missing_member_catalog_package_ids': [f'{x:04X}' for x in missing_catalog],
        'final_entity_package_counts': dict(entity_pkgs.most_common()),
        'resolved_body_role_counts': dict(body_roles),
        'unique_final_entities_by_class': {k: len(v) for k, v in sorted(class_entities.items())},
        'logical_views': {f'{pkg:04X}': r.view.name for pkg, r in sorted(views.items())},
        'parents': resolved,
        'arrangements': augmented,
        'items': named_items,
        'errors': errors,
        'policy': (
            'Inventory names/classes/types are historical presentation metadata. Every assignment->EntityParent and '
            'EntityParent->EntityDataROI edge in this report is serialized retail D1 data. Masculine/feminine labels '
            'come from the corresponding explicit fields in the retail art-arrangement row.'
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2) + '\n')
    summary = {k: v for k, v in report.items() if k not in ('parents', 'arrangements', 'items', 'errors')}
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
