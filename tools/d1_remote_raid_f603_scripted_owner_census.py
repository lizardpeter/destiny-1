#!/usr/bin/env python3
"""Classify every SF603 EntityResource reachable from one exact activity traversal.

Input is a source-derived d1_remote_activity_placements/v1 report. For every
serialized SF603 (808003F6), this tool follows the source-pinned +0x0C
EntityResource FileHash, parses that 80800861 with the shared EntityResource
parser, and records any exact scripted-entity-table owner chain:

  SF603 +0x0C -> EntityResource 80800861
  EntityResource discriminator 808007BC -> parent 808005A7
  parent +0x68 -> Tag<808012D9>

No entity or table is assigned a semantic enemy identity by this census.
"""
from __future__ import annotations

import argparse, collections, json, struct, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from d1_entity_resource_probe import parse_resource
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_activity_placements import RemoteCorpus, norm
from d1_split_tar_extract import SplitHttpTar

F603 = '808003F6'
ENTITY_RESOURCE = '80800861'
D912 = '808012D9'
NULLS = {'00000000', 'FFFFFFFF'}


def u32(b: bytes, o: int) -> int:
    return struct.unpack_from('<I', b, o)[0]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--placements', type=Path, required=True)
    ap.add_argument('--member-catalog', type=Path, action='append', required=True)
    ap.add_argument('--base-url', required=True)
    ap.add_argument('--part-count', type=int, default=10)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('-o', '--output', type=Path, required=True)
    a = ap.parse_args()

    src = json.loads(a.placements.read_text())
    if src.get('schema') != 'd1_remote_activity_placements/v1':
        raise SystemExit(f'unexpected placements schema {src.get("schema")!r}')
    f603s = [norm(x) for x in src.get('unique_f603_entity_resources', []) if norm(x) not in NULLS]
    f603s = list(dict.fromkeys(f603s))

    catalogs = load_catalogs(a.member_catalog)
    base = a.base_url.rstrip('/')
    arc = SplitHttpTar([f'{base}/packages.tar.{i:03d}' for i in range(1, a.part_count + 1)], retries=6, timeout=90)
    c = RemoteCorpus(arc, catalogs, a.runtime)

    rows = []
    violations = []
    role_counts = collections.Counter()
    pair_counts = collections.Counter()
    table_counts = collections.Counter()

    for fh in f603s:
        row = {'f603': fh, 'violations': []}
        fm = c.entry_meta(fh)
        row['f603_reference'] = None if fm is None else norm(fm.get('reference'))
        fb, fsrc = c.payload(fh)
        row['f603_payload_source'] = fsrc
        if fm is None or row['f603_reference'] != F603 or fb is None:
            row['violations'].append('f603_missing_or_wrong_class')
            rows.append(row)
            violations.extend(f'{fh}:{x}' for x in row['violations'])
            continue
        if len(fb) < 0x10:
            row['violations'].append('f603_shorter_than_0x10')
            rows.append(row)
            violations.extend(f'{fh}:{x}' for x in row['violations'])
            continue

        erh = f'{u32(fb, 0x0C):08X}'
        row['entity_resource_hash'] = erh
        em = c.entry_meta(erh)
        row['entity_resource_reference'] = None if em is None else norm(em.get('reference'))
        eb, esrc = c.payload(erh)
        row['entity_resource_payload_source'] = esrc
        if erh in NULLS:
            row['entity_resource_null'] = True
            role_counts['null'] += 1
            rows.append(row)
            continue
        if em is None or row['entity_resource_reference'] != ENTITY_RESOURCE or eb is None:
            row['violations'].append('entity_resource_missing_or_wrong_class')
            rows.append(row)
            violations.extend(f'{fh}:{x}' for x in row['violations'])
            continue
        try:
            parsed = parse_resource(eb, 'PS4')
        except Exception as ex:
            row['violations'].append(f'entity_resource_parse_error:{type(ex).__name__}:{ex}')
            rows.append(row)
            violations.extend(f'{fh}:{x}' for x in row['violations'])
            continue

        role = parsed.get('semantic_role', 'other_or_unknown')
        row['semantic_role'] = role
        row['unk10_class'] = (parsed.get('unk10') or {}).get('class_hash')
        row['unk18_class'] = (parsed.get('unk18') or {}).get('class_hash')
        role_counts[role] += 1
        pair_counts[(row['unk10_class'], row['unk18_class'])] += 1

        if role == 'scripted_entity_table_owner':
            th = parsed.get('scripted_entity_table_tag_hash')
            row['scripted_entity_table_hash'] = th
            tm = None if not th else c.entry_meta(th)
            row['scripted_entity_table_reference'] = None if tm is None else norm(tm.get('reference'))
            row['scripted_entity_table_class_matches'] = bool(tm and row['scripted_entity_table_reference'] == D912)
            if not th or not row['scripted_entity_table_class_matches']:
                row['violations'].append('scripted_table_missing_or_wrong_class')
            else:
                table_counts[th] += 1

        rows.append(row)
        violations.extend(f'{fh}:{x}' for x in row['violations'])

    report = {
        'schema': 'd1_remote_raid_f603_scripted_owner_census/v1',
        'status': 'D1_RAID_F603_SCRIPTED_OWNER_CENSUS_EXACT' if not violations else 'D1_RAID_F603_SCRIPTED_OWNER_CENSUS_PARTIAL',
        'activity': src.get('activity'),
        'input_f603_count': len(f603s),
        'role_counts': dict(role_counts),
        'class_pair_counts': {f'{a or "NONE"}->{b or "NONE"}': n for (a, b), n in sorted(pair_counts.items(), key=lambda x: str(x[0]))},
        'scripted_owner_count': sum(1 for r in rows if r.get('semantic_role') == 'scripted_entity_table_owner'),
        'scripted_table_hashes': sorted(table_counts),
        'scripted_table_owner_counts': dict(sorted(table_counts.items())),
        'rows': rows,
        'violations': violations,
        'policy': 'Every edge is source-layout-derived from the exact activity-owned SF603 set. No FileHash, StringHash, entity, model, or scripted table receives Crota identity from proximity, package membership, or appearance.'
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2) + '\n')
    print('STATUS', report['status'], 'ACTIVITY', (report.get('activity') or {}).get('tag_hash'),
          'F603', len(f603s), 'ROLES', dict(role_counts), 'SCRIPTED_OWNERS', report['scripted_owner_count'],
          'TABLES', report['scripted_table_hashes'], 'VIOLATIONS', len(violations))
    for r in rows:
        if r.get('semantic_role') == 'scripted_entity_table_owner':
            print('SCRIPTED_OWNER', r['f603'], 'ENTITY_RESOURCE', r.get('entity_resource_hash'),
                  'TABLE', r.get('scripted_entity_table_hash'), 'CLASS_OK', r.get('scripted_entity_table_class_matches'))
    return 0 if not violations else 2


if __name__ == '__main__':
    raise SystemExit(main())
