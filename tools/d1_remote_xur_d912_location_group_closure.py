#!/usr/bin/env python3
"""Close Xur scripted D912 location -> SD614 group assignments fail-closed.

This probe intentionally does not assign gameplay meaning to the opaque S2B138080
+0x28 word.  The checked-in Tower corpus has already shown that word behaves as a
structural SD614 group index when it is in-range, nondecreasing, and stable across
duplicate D912 serializations.  Here we apply the same structural tests directly to
the ten exact Xur D912 tables and retain every source-owned entity/group/location.

The higher 80800861 parent of every D912 was independently closed by exact aligned
backlinks.  This probe re-validates that edge at +0x540 and the exact retail StringHash
serialized at +0x5F0 for the three observed black-market branches.  Those parent
StringHashes have exact retail preimages from the Tower string corpus:

  07A04EFA = sq_boulevard_vendor_black_market
  4AC210DE = vendor_black_market
  E4105D4B = sq_underwatch_vendor_black_market

No coordinate proximity, descriptor adjacency, or material default state is used.
Material E6/E7/E8 gates remain false.
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

from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_activity_placements import RemoteCorpus
from d1_split_tar_extract import SplitHttpTar
import d1_world_scripted_entity_identity_census as scripted
import d1_remote_activity_scripted_entity_census as census

D912_CLASS = '808012D9'
PARENT_CLASS = '80800861'
XURS = {'80C7ACC8', '80C885AA'}
EMPTY_FNV1 = 0x811C9DC5

# Exact D912 -> 80800861 parent edges independently closed by the backlink census.
# expected branch hash is re-read from the parent at +0x5F0 in this probe.
TARGETS = {
    '80C7A251': ('80C7A270', '07A04EFA', 'sq_boulevard_vendor_black_market'),
    '80C7A441': ('80C7A451', '4AC210DE', 'vendor_black_market'),
    '80C7A58F': ('80C7A5A7', 'E4105D4B', 'sq_underwatch_vendor_black_market'),
    '80C7A719': ('80C7A75E', '4AC210DE', 'vendor_black_market'),
    '80C7AC71': ('80C7AC73', '07A04EFA', 'sq_boulevard_vendor_black_market'),
    '80C7AC81': ('80C7AC87', '4AC210DE', 'vendor_black_market'),
    '80C7ACB9': ('80C7ACC2', 'E4105D4B', 'sq_underwatch_vendor_black_market'),
    '80C88185': ('80C88190', '07A04EFA', 'sq_boulevard_vendor_black_market'),
    '80C8831B': ('80C88335', '4AC210DE', 'vendor_black_market'),
    '80C88591': ('80C885C2', 'E4105D4B', 'sq_underwatch_vendor_black_market'),
}


def norm(x):
    return str(x).upper().removeprefix('0X').zfill(8)


def u32(b: bytes, o: int) -> int:
    return struct.unpack_from('<I', b, o)[0]


def tail_words(hex_text: str):
    b = bytes.fromhex(hex_text)
    if len(b) != 0x10:
        raise ValueError(f'S2B tail length 0x{len(b):X}, expected 0x10')
    return struct.unpack('<4I', b)


def parent_check(c, d912: str, parent: str, branch_hash: str, branch_name: str):
    m = c.entry_meta(parent)
    b, src = c.payload(parent)
    out = {
        'parent': parent,
        'expected_class': PARENT_CLASS,
        'branch_string_hash': branch_hash,
        'branch_name_exact_retail_preimage': branch_name,
        'payload_source': src,
        'violations': [],
    }
    if m is None or norm(m.get('reference', '')) != PARENT_CLASS or b is None:
        out['violations'].append('parent_missing_class_or_payload')
        return out
    out['bytes'] = len(b)
    out['sha256'] = hashlib.sha256(b).hexdigest()
    if len(b) < 0x5F4:
        out['violations'].append('parent_shorter_than_0x5F4')
        return out
    out['d912_backlink_offset'] = 0x540
    out['d912_backlink_value'] = f'{u32(b, 0x540):08X}'
    out['branch_hash_offset'] = 0x5F0
    out['branch_hash_value'] = f'{u32(b, 0x5F0):08X}'
    if out['d912_backlink_value'] != d912:
        out['violations'].append(f'parent_0x540_{out["d912_backlink_value"]}_not_{d912}')
    if out['branch_hash_value'] != branch_hash:
        out['violations'].append(f'parent_0x5F0_{out["branch_hash_value"]}_not_{branch_hash}')
    return out


def canonical_table(row: dict):
    return (
        tuple((g['group_index'], g['type_string_hash'], tuple(g['unique_entity_hashes'])) for g in row['groups']),
        tuple((x['location_index'], tuple(x['location']), tuple(x['rotation']), x['candidate_group_index'], x['group_type_string_hash'], tuple(x['group_unique_entity_hashes'])) for x in row['locations']),
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--member-catalog', type=Path, action='append', required=True)
    ap.add_argument('--base-url', required=True)
    ap.add_argument('--part-count', type=int, default=10)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('-o', '--output', type=Path, required=True)
    a = ap.parse_args()

    cats = load_catalogs(a.member_catalog)
    arc = SplitHttpTar([f"{a.base_url.rstrip('/')}/packages.tar.{i:03d}" for i in range(1, a.part_count + 1)], retries=6, timeout=90)
    c = RemoteCorpus(arc, cats, a.runtime)

    violations = []
    rows = []
    by_branch = collections.defaultdict(list)
    group_type_counts = collections.Counter()
    entity_counts = collections.Counter()
    tail_index_counts = collections.Counter()

    for h, (parent, branch_hash, branch_name) in TARGETS.items():
        row = {
            'd912': h,
            'parent': parent,
            'branch_string_hash': branch_hash,
            'branch_name_exact_retail_preimage': branch_name,
            'violations': [],
        }
        try:
            m = c.entry_meta(h)
            b, src = c.payload(h)
            if m is None or norm(m.get('reference', '')) != D912_CLASS or b is None:
                raise ValueError('D912 missing class or payload')
            row['payload_source'] = src
            row['bytes'] = len(b)
            row['sha256'] = hashlib.sha256(b).hexdigest()

            pc = parent_check(c, h, parent, branch_hash, branch_name)
            row['parent_validation'] = pc
            row['violations'].extend(pc['violations'])

            t = scripted.parse_d912(c, h, {})
            t = census.normalize_scripted_overlay_semantics(t)
            census.attach_locations(c, t)
            row['parse_violations'] = list(t.get('violations', []))
            row['violations'].extend(f'parse:{x}' for x in t.get('violations', []))

            groups = {}
            for g in t.get('groups', []):
                gi = int(g.get('group_index', -1))
                ents = sorted({norm(r.get('entity_hash')) for r in g.get('records', []) if norm(r.get('entity_hash', 'FFFFFFFF')) not in {'00000000', 'FFFFFFFF'}})
                xurs = sorted(set(ents) & XURS)
                gr = {
                    'group_index': gi,
                    'type_string_hash': norm(g.get('type_string_hash')),
                    'record_count': len(g.get('records', [])),
                    'unique_entity_hashes': ents,
                    'xur_entity_hashes': xurs,
                    'unique_xur_entity_count': len(xurs),
                }
                groups[gi] = gr
                group_type_counts[gr['type_string_hash']] += 1
                for e in ents:
                    entity_counts[e] += 1
            if sorted(groups) != list(range(len(groups))):
                row['violations'].append(f'non_dense_group_indices:{sorted(groups)}')
            row['groups'] = [groups[i] for i in sorted(groups)]
            row['group_count'] = len(groups)

            seen = []
            loc_rows = []
            for loc in t.get('locations', []):
                w0, w1, gi, w3 = tail_words(loc.get('tail_20_30_hex', ''))
                seen.append(gi)
                tail_index_counts[str(gi)] += 1
                lr = {
                    'location_index': int(loc.get('index', -1)),
                    'location': loc.get('location'),
                    'rotation': loc.get('rotation'),
                    'tail_words_hex': [f'{x:08X}' for x in (w0, w1, gi, w3)],
                    'tail_first_two_are_empty_fnv1': w0 == EMPTY_FNV1 and w1 == EMPTY_FNV1,
                    'candidate_group_index': gi,
                    'tail_unk2c': w3,
                }
                if gi not in groups:
                    row['violations'].append(f'location_{lr["location_index"]}:group_index_{gi}_out_of_range')
                    lr['assignment_status'] = 'group_index_out_of_range'
                else:
                    g = groups[gi]
                    ents = list(g['unique_entity_hashes'])
                    xurs = list(g['xur_entity_hashes'])
                    lr.update({
                        'group_type_string_hash': g['type_string_hash'],
                        'group_unique_entity_hashes': ents,
                        'group_xur_entity_hashes': xurs,
                    })
                    if len(ents) == 1:
                        lr['entity_hash'] = ents[0]
                        lr['assignment_status'] = 'exact_unique_entity_within_structurally_indexed_group'
                    else:
                        lr['assignment_status'] = 'ambiguous_multiple_entities_within_structurally_indexed_group'
                    if len(xurs) == 1:
                        lr['xur_entity_hash'] = xurs[0]
                        lr['xur_assignment_status'] = 'exact_unique_xur_entity_within_structurally_indexed_group'
                    elif len(xurs) > 1:
                        lr['xur_assignment_status'] = 'ambiguous_multiple_xur_entities_within_structurally_indexed_group'
                    else:
                        lr['xur_assignment_status'] = 'group_contains_no_xur_entity'
                loc_rows.append(lr)
            if seen != sorted(seen):
                row['violations'].append(f'candidate_group_indices_not_nondecreasing:{seen}')
            if any(not x['tail_first_two_are_empty_fnv1'] for x in loc_rows):
                row['violations'].append('tail_first_two_words_not_uniform_empty_fnv1')
            row['candidate_group_index_sequence'] = seen
            row['locations'] = loc_rows
            row['location_count'] = len(loc_rows)
            row['exact_unique_entity_location_count'] = sum(x.get('assignment_status') == 'exact_unique_entity_within_structurally_indexed_group' for x in loc_rows)
            row['exact_unique_xur_location_count'] = sum(x.get('xur_assignment_status') == 'exact_unique_xur_entity_within_structurally_indexed_group' for x in loc_rows)
        except Exception as ex:
            row['violations'].append(repr(ex))

        if row['violations']:
            violations.extend(f'{h}:{x}' for x in row['violations'])
        rows.append(row)
        by_branch[branch_name].append(row)

    branch_reports = []
    for name, br in sorted(by_branch.items()):
        sigs = collections.defaultdict(list)
        for r in br:
            if r.get('groups') is not None and r.get('locations') is not None:
                sigs[repr(canonical_table(r))].append(r['d912'])
        branch_reports.append({
            'branch_name': name,
            'branch_string_hash': br[0]['branch_string_hash'],
            'd912_count': len(br),
            'd912s': [r['d912'] for r in br],
            'canonical_group_location_signature_count': len(sigs),
            'identical_group_location_serialization_within_branch': len(sigs) == 1,
            'signature_members': list(sigs.values()),
            'total_location_count': sum(int(r.get('location_count', 0)) for r in br),
            'exact_unique_xur_location_count': sum(int(r.get('exact_unique_xur_location_count', 0)) for r in br),
        })

    all_locations = [dict(d912=r['d912'], parent=r['parent'], branch=r['branch_name_exact_retail_preimage'], **x) for r in rows for x in r.get('locations', [])]
    exact_xur_locations = [x for x in all_locations if x.get('xur_assignment_status') == 'exact_unique_xur_entity_within_structurally_indexed_group']

    out = {
        'schema_version': 1,
        'status': 'D1_XUR_D912_LOCATION_GROUP_CLOSURE_COMPLETE' if not violations else 'D1_XUR_D912_LOCATION_GROUP_CLOSURE_VIOLATIONS',
        'source_contract': 'Charm ROI SD912/SD614/S2B138080 plus exact retail D912->80800861 backlink parents; S2B +0x28 is structural group index only, not gameplay semantics.',
        'target_d912_count': len(TARGETS),
        'decoded_d912_count': sum('groups' in r for r in rows),
        'branch_count': len(branch_reports),
        'branches': branch_reports,
        'group_type_counts': dict(group_type_counts),
        'entity_group_membership_counts': dict(entity_counts),
        'candidate_group_index_counts': dict(tail_index_counts),
        'location_count': len(all_locations),
        'exact_unique_xur_location_count': len(exact_xur_locations),
        'exact_unique_xur_locations': exact_xur_locations,
        'rows': rows,
        'violations': violations,
        'gates': {
            'E6_80C885E6_live_selection_proven': False,
            'E7_80C885E7_live_selection_proven': False,
            'E8_80C885E8_live_selection_proven': False,
        },
        'policy': 'No coordinate proximity, descriptor adjacency, or default material state is promoted. Location assignment is exact only through the source-owned S2B +0x28 structural group index and a unique Xur EntitySK within that indexed SD614 group. Material gates remain fail-closed.',
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({
        'status': out['status'],
        'target_d912_count': out['target_d912_count'],
        'decoded_d912_count': out['decoded_d912_count'],
        'branch_count': out['branch_count'],
        'location_count': out['location_count'],
        'exact_unique_xur_location_count': out['exact_unique_xur_location_count'],
        'branches': out['branches'],
        'violations': out['violations'],
        'gates': out['gates'],
    }, indent=2))
    return 0 if not violations else 2


if __name__ == '__main__':
    raise SystemExit(main())
