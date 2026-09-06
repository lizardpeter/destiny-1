#!/usr/bin/env python3
"""Build the archive-wide metadata index used to drive D1 "export everything".

The index walks the current PS4 packages.txt / split TAR, preserves every physical
package member, and reads only Tiger package headers plus entry/named-tag tables.
It does not fetch asset payload bodies. By default, entry tables are indexed for
the exact current generation of every package id; --all-generations expands this
to every physical patch occurrence.

Unknown classes are first-class rows with export_route=unknown. A conservative
registry may attach byte-validated labels and existing exporter routes, but never
infers semantic ownership from filenames, adjacency, or appearance.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path

from d1_pkg_probe import parse_entries, parse_header, parse_named
from d1_split_tar_extract import SplitHttpTar

ENTRY_STRIDE = 16
NAMED_STRIDE = 68
PKG_RX = re.compile(r'_([0-9A-Fa-f]{4})_([0-9]+)\.pkg$', re.I)


def norm(x: object) -> str:
    return str(x).upper().removeprefix('0X').zfill(8)


def sha1(b: bytes) -> str:
    return hashlib.sha1(b).hexdigest()


def identity(name: str) -> tuple[str, int] | None:
    m = PKG_RX.search(Path(name).name)
    return (m.group(1).upper(), int(m.group(2))) if m else None


def load_registry(path: Path | None) -> dict:
    if path is None:
        return {'reference_classes': {}, 'type_subtype_classes': {}}
    d = json.loads(path.read_text())
    if d.get('schema') != 'd1_export_class_registry/v1':
        raise ValueError(f'unsupported class registry: {d.get("schema")!r}')
    return d


def classify(e: dict, reg: dict) -> dict:
    ref = norm(e['reference'])
    rec = (reg.get('reference_classes') or {}).get(ref)
    source = f'reference:{ref}' if rec is not None else None
    if rec is None:
        k = f"{int(e['type'])}:{int(e['subtype'])}"
        rec = (reg.get('type_subtype_classes') or {}).get(k)
        source = f'type_subtype:{k}' if rec is not None else None
    if rec is None:
        return dict(label=None, route='unknown', standalone=0, source=None,
                    semantic_status='unclassified', tool=None)
    return dict(
        label=rec.get('label'), route=rec.get('export_route') or 'known_unrouted',
        standalone=int(bool(rec.get('standalone_export'))), source=source,
        semantic_status=rec.get('semantic_status') or 'known', tool=rec.get('tool'))


def make_db(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()
    db = sqlite3.connect(path)
    db.executescript('''
      PRAGMA journal_mode=OFF;
      PRAGMA synchronous=OFF;
      PRAGMA temp_store=MEMORY;

      CREATE TABLE meta(key TEXT PRIMARY KEY,value TEXT NOT NULL);
      CREATE TABLE physical_packages(
        package_row INTEGER PRIMARY KEY,
        name TEXT NOT NULL UNIQUE,
        package_id TEXT NOT NULL,
        filename_package_id TEXT NOT NULL,
        filename_generation INTEGER NOT NULL,
        header_patch_id INTEGER NOT NULL,
        platform TEXT NOT NULL,
        platform_code INTEGER NOT NULL,
        language TEXT NOT NULL,
        language_code INTEGER NOT NULL,
        tar_header_offset INTEGER NOT NULL,
        data_offset INTEGER NOT NULL,
        size INTEGER NOT NULL,
        entry_table_count INTEGER NOT NULL,
        entry_table_offset INTEGER NOT NULL,
        entry_table_sha1_expected TEXT NOT NULL,
        block_table_count INTEGER NOT NULL,
        block_table_offset INTEGER NOT NULL,
        named_tag_table_count INTEGER NOT NULL,
        named_tag_table_offset INTEGER NOT NULL,
        named_tag_table_sha1_expected TEXT NOT NULL,
        is_current INTEGER NOT NULL CHECK(is_current IN(0,1)));

      CREATE TABLE entry_occurrences(
        occurrence_id INTEGER PRIMARY KEY,
        package_row INTEGER NOT NULL REFERENCES physical_packages(package_row),
        package_name TEXT NOT NULL,
        package_id TEXT NOT NULL,
        package_generation INTEGER NOT NULL,
        package_patch_id INTEGER NOT NULL,
        is_current INTEGER NOT NULL CHECK(is_current IN(0,1)),
        entry_index INTEGER NOT NULL,
        tag_hash TEXT NOT NULL,
        reference TEXT NOT NULL,
        type INTEGER NOT NULL,
        subtype INTEGER NOT NULL,
        entry_b TEXT NOT NULL,
        file_size INTEGER NOT NULL,
        starting_block INTEGER NOT NULL,
        starting_block_offset INTEGER NOT NULL,
        class_label TEXT,
        export_route TEXT NOT NULL,
        standalone_export INTEGER NOT NULL CHECK(standalone_export IN(0,1)),
        classification_source TEXT,
        semantic_status TEXT NOT NULL,
        route_tool TEXT,
        UNIQUE(package_row,entry_index));

      CREATE TABLE named_tag_occurrences(
        occurrence_id INTEGER PRIMARY KEY,
        package_row INTEGER NOT NULL REFERENCES physical_packages(package_row),
        package_name TEXT NOT NULL,
        package_id TEXT NOT NULL,
        is_current INTEGER NOT NULL CHECK(is_current IN(0,1)),
        named_index INTEGER NOT NULL,
        tag_hash TEXT NOT NULL,
        class_hash TEXT NOT NULL,
        name TEXT,
        UNIQUE(package_row,named_index));

      CREATE TABLE class_registry(
        key_type TEXT NOT NULL,key_value TEXT NOT NULL,label TEXT,export_route TEXT,
        standalone_export INTEGER NOT NULL,semantic_status TEXT,tool TEXT,notes TEXT,
        PRIMARY KEY(key_type,key_value));
      CREATE TABLE violations(
        violation_id INTEGER PRIMARY KEY,package_name TEXT,stage TEXT NOT NULL,detail TEXT NOT NULL);

      CREATE INDEX idx_pkg_current ON physical_packages(package_id,is_current);
      CREATE INDEX idx_entry_tag ON entry_occurrences(tag_hash);
      CREATE INDEX idx_entry_ref ON entry_occurrences(reference);
      CREATE INDEX idx_entry_type ON entry_occurrences(type,subtype);
      CREATE INDEX idx_entry_current ON entry_occurrences(is_current);
      CREATE INDEX idx_entry_route ON entry_occurrences(export_route,is_current);
      CREATE INDEX idx_named_tag ON named_tag_occurrences(tag_hash);
      CREATE INDEX idx_named_class ON named_tag_occurrences(class_hash);

      CREATE VIEW current_entries AS SELECT * FROM entry_occurrences WHERE is_current=1;
      CREATE VIEW current_export_queue AS
        SELECT occurrence_id,package_name,package_id,entry_index,tag_hash,reference,type,subtype,
               class_label,export_route,standalone_export,semantic_status,route_tool
        FROM entry_occurrences WHERE is_current=1;
      CREATE VIEW current_logical_resources AS
        SELECT tag_hash,COUNT(*) occurrence_count,COUNT(DISTINCT package_id) package_id_count,
               GROUP_CONCAT(DISTINCT reference) references,
               GROUP_CONCAT(DISTINCT export_route) export_routes,
               MAX(class_label) class_label,MAX(standalone_export) any_standalone_export
        FROM entry_occurrences WHERE is_current=1 GROUP BY tag_hash;
    ''')
    return db


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--package-list', type=Path, required=True)
    ap.add_argument('--registry', type=Path)
    ap.add_argument('--sqlite', type=Path, required=True)
    ap.add_argument('--summary', type=Path, required=True)
    ap.add_argument('--queue', type=Path, required=True)
    ap.add_argument('--all-generations', action='store_true')
    ap.add_argument('--base-url', default='https://crypt.cohae.dev/destiny/ps4/packages/latest')
    ap.add_argument('--part-count', type=int, default=10)
    ap.add_argument('--retries', type=int, default=6)
    ap.add_argument('--timeout', type=int, default=120)
    a = ap.parse_args()

    reg = load_registry(a.registry)
    list_bytes = a.package_list.read_bytes()
    list_sha = hashlib.sha256(list_bytes).hexdigest()
    names = sorted({Path(x.strip()).name for x in list_bytes.decode('utf-8', 'replace').splitlines()
                    if x.strip() and identity(Path(x.strip()).name) is not None})
    if not names:
        raise SystemExit('packages.txt yielded no package members')

    arc = SplitHttpTar([f"{a.base_url.rstrip('/')}/packages.tar.{i:03d}"
                        for i in range(1, a.part_count + 1)],
                       retries=a.retries, timeout=a.timeout)
    locations, headers_scanned = arc.find(set(names))
    missing = sorted(set(names) - set(locations))
    if missing:
        raise SystemExit(f'{len(missing)} package members missing from split TAR: {missing[:20]}')

    physical: list[dict] = []
    families: dict[str, list[int]] = defaultdict(list)
    violations: list[dict] = []
    for n, name in enumerate(names, 1):
        loc = locations[name]
        fid = identity(name)
        assert fid is not None
        filename_pkg, generation = fid
        if int(loc['size']) < 0x140:
            violations.append({'package_name': name, 'stage': 'header', 'detail': f'size {loc["size"]} < 0x140'})
            continue
        try:
            h = parse_header(io.BytesIO(arc.read_at(int(loc['data_offset']), 0x140)))
        except Exception as ex:
            violations.append({'package_name': name, 'stage': 'header', 'detail': repr(ex)})
            continue
        pkg = f"{int(h['pkg_id']):04X}"
        if pkg != filename_pkg:
            violations.append({'package_name': name, 'stage': 'header', 'detail': f'filename package {filename_pkg} != header {pkg}'})
        if h['platform'] != 'PS4':
            violations.append({'package_name': name, 'stage': 'header', 'detail': f'unexpected platform {h["platform"]}'})
        row = {
            'package_row': len(physical), 'name': name, 'package_id': pkg,
            'filename_package_id': filename_pkg, 'filename_generation': generation,
            'header_patch_id': int(h['patch_id']), 'platform': h['platform'],
            'platform_code': int(h['platform_code']), 'language': h['language'],
            'language_code': int(h['language_code']), 'tar_header_offset': int(loc['header_offset']),
            'data_offset': int(loc['data_offset']), 'size': int(loc['size']),
            'entry_table_count': int(h['entry_table_count']), 'entry_table_offset': int(h['entry_table_offset']),
            'entry_table_sha1_expected': str(h['entry_table_hash']).lower(),
            'block_table_count': int(h['block_table_count']), 'block_table_offset': int(h['block_table_offset']),
            'named_tag_table_count': int(h['named_tag_table_count']), 'named_tag_table_offset': int(h['named_tag_table_offset']),
            'named_tag_table_sha1_expected': str(h['named_tag_table_hash']).lower(), 'is_current': 0,
        }
        physical.append(row)
        families[pkg].append(row['package_row'])
        if n % 100 == 0 or n == len(names):
            print(f'HEADERS {n}/{len(names)}', flush=True)

    for pkg, indexes in families.items():
        winner = max(indexes, key=lambda i: (
            physical[i]['header_patch_id'], physical[i]['filename_generation'], physical[i]['name']))
        physical[winner]['is_current'] = 1

    db = make_db(a.sqlite)
    try:
        db.executemany('INSERT INTO meta VALUES(?,?)', [
            ('schema', 'd1_remote_everything_index/v1'), ('packages_txt_sha256', list_sha),
            ('base_url', a.base_url), ('part_count', str(a.part_count)),
            ('index_mode', 'all_generations' if a.all_generations else 'current_only')])
        for key_type, group in (('reference', reg.get('reference_classes') or {}),
                                ('type_subtype', reg.get('type_subtype_classes') or {})):
            for k, r in sorted(group.items()):
                db.execute('INSERT INTO class_registry VALUES(?,?,?,?,?,?,?,?)', (
                    key_type, norm(k) if key_type == 'reference' else k, r.get('label'),
                    r.get('export_route'), int(bool(r.get('standalone_export'))),
                    r.get('semantic_status'), r.get('tool'), r.get('notes')))

        psql = '''INSERT INTO physical_packages(
          package_row,name,package_id,filename_package_id,filename_generation,header_patch_id,
          platform,platform_code,language,language_code,tar_header_offset,data_offset,size,
          entry_table_count,entry_table_offset,entry_table_sha1_expected,block_table_count,
          block_table_offset,named_tag_table_count,named_tag_table_offset,named_tag_table_sha1_expected,is_current)
          VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'''
        for p in physical:
            db.execute(psql, tuple(p[k] for k in (
                'package_row','name','package_id','filename_package_id','filename_generation','header_patch_id',
                'platform','platform_code','language','language_code','tar_header_offset','data_offset','size',
                'entry_table_count','entry_table_offset','entry_table_sha1_expected','block_table_count','block_table_offset',
                'named_tag_table_count','named_tag_table_offset','named_tag_table_sha1_expected','is_current')))

        all_refs, all_types, all_routes, all_classes = Counter(), Counter(), Counter(), Counter()
        cur_refs, cur_types, cur_routes, cur_classes = Counter(), Counter(), Counter(), Counter()
        indexed_packages = indexed_entries = current_entries = indexed_named = current_named = 0
        esql = '''INSERT INTO entry_occurrences(
          package_row,package_name,package_id,package_generation,package_patch_id,is_current,
          entry_index,tag_hash,reference,type,subtype,entry_b,file_size,starting_block,starting_block_offset,
          class_label,export_route,standalone_export,classification_source,semantic_status,route_tool)
          VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'''
        nsql = '''INSERT INTO named_tag_occurrences(
          package_row,package_name,package_id,is_current,named_index,tag_hash,class_hash,name)
          VALUES(?,?,?,?,?,?,?,?)'''

        for step, p in enumerate(physical, 1):
            if not (p['is_current'] or a.all_generations):
                continue
            indexed_packages += 1
            en = p['entry_table_count'] * ENTRY_STRIDE
            nn = p['named_tag_table_count'] * NAMED_STRIDE
            if p['entry_table_offset'] + en > p['size']:
                violations.append({'package_name': p['name'], 'stage': 'entry_table', 'detail': 'table exceeds physical member'})
                continue
            try:
                eb = arc.read_at(p['data_offset'] + p['entry_table_offset'], en)
            except Exception as ex:
                violations.append({'package_name': p['name'], 'stage': 'entry_table', 'detail': repr(ex)})
                continue
            got = sha1(eb)
            if got != p['entry_table_sha1_expected']:
                violations.append({'package_name': p['name'], 'stage': 'entry_table', 'detail': f'sha1 {got} != {p["entry_table_sha1_expected"]}'})
                continue
            entries = parse_entries(eb, int(p['package_id'], 16))
            if len(entries) != p['entry_table_count']:
                violations.append({'package_name': p['name'], 'stage': 'entry_table', 'detail': 'parsed entry count mismatch'})
                continue
            for e in entries:
                c = classify(e, reg)
                db.execute(esql, (
                    p['package_row'], p['name'], p['package_id'], p['filename_generation'], p['header_patch_id'], p['is_current'],
                    int(e['index']), norm(e['tag_hash']), norm(e['reference']), int(e['type']), int(e['subtype']), norm(e['entry_b']),
                    int(e['file_size']), int(e['starting_block']), int(e['starting_block_offset']), c['label'], c['route'],
                    c['standalone'], c['source'], c['semantic_status'], c['tool']))
                ref, typ = norm(e['reference']), f"{int(e['type'])}:{int(e['subtype'])}"
                all_refs[ref] += 1; all_types[typ] += 1; all_routes[c['route']] += 1
                if c['label']: all_classes[c['label']] += 1
                indexed_entries += 1
                if p['is_current']:
                    cur_refs[ref] += 1; cur_types[typ] += 1; cur_routes[c['route']] += 1
                    if c['label']: cur_classes[c['label']] += 1
                    current_entries += 1

            if nn:
                if p['named_tag_table_offset'] + nn > p['size']:
                    violations.append({'package_name': p['name'], 'stage': 'named_tag_table', 'detail': 'table exceeds physical member'})
                else:
                    try:
                        nb = arc.read_at(p['data_offset'] + p['named_tag_table_offset'], nn)
                        gotn = sha1(nb)
                        if gotn != p['named_tag_table_sha1_expected']:
                            violations.append({'package_name': p['name'], 'stage': 'named_tag_table', 'detail': f'sha1 {gotn} != {p["named_tag_table_sha1_expected"]}'})
                        else:
                            for x in parse_named(nb):
                                db.execute(nsql, (p['package_row'], p['name'], p['package_id'], p['is_current'],
                                                   int(x['index']), norm(x['tag_hash']), norm(x['class_hash']), x.get('name')))
                                indexed_named += 1
                                if p['is_current']: current_named += 1
                    except Exception as ex:
                        violations.append({'package_name': p['name'], 'stage': 'named_tag_table', 'detail': repr(ex)})
            if step % 50 == 0 or step == len(physical):
                print(f'TABLES {step}/{len(physical)} packages={indexed_packages} entries={indexed_entries}', flush=True)

        for v in violations:
            db.execute('INSERT INTO violations(package_name,stage,detail) VALUES(?,?,?)',
                       (v.get('package_name'), v['stage'], v['detail']))
        db.commit()

        distinct_tags = int(db.execute('SELECT COUNT(DISTINCT tag_hash) FROM current_entries').fetchone()[0])
        duplicate_tags = int(db.execute('SELECT COUNT(*) FROM (SELECT tag_hash FROM current_entries GROUP BY tag_hash HAVING COUNT(*)>1)').fetchone()[0])
        standalone = int(db.execute('SELECT COUNT(*) FROM current_entries WHERE standalone_export=1').fetchone()[0])
        contextual = int(db.execute("SELECT COUNT(*) FROM current_entries WHERE export_route!='unknown' AND standalone_export=0").fetchone()[0])
        unknown = int(cur_routes.get('unknown', 0))
        summary = {
            'schema': 'd1_remote_everything_index/v1',
            'status': 'D1_REMOTE_EVERYTHING_INDEX_COMPLETE' if not violations else 'D1_REMOTE_EVERYTHING_INDEX_PARTIAL',
            'mode': 'all_generations' if a.all_generations else 'current_only',
            'source': {'package_list': str(a.package_list), 'packages_txt_sha256': list_sha,
                       'base_url': a.base_url, 'part_count': a.part_count, 'part_sizes': arc.sizes,
                       'logical_split_tar_bytes': arc.logical_size, 'tar_headers_scanned': headers_scanned},
            'physical_package_member_count': len(physical), 'package_family_count': len(families),
            'current_package_count': sum(p['is_current'] for p in physical),
            'indexed_package_generation_count': indexed_packages,
            'indexed_entry_occurrence_count': indexed_entries, 'current_entry_count': current_entries,
            'current_distinct_tag_hash_count': distinct_tags, 'current_duplicate_tag_hash_count': duplicate_tags,
            'indexed_named_tag_count': indexed_named, 'current_named_tag_count': current_named,
            'current_known_routed_entry_count': current_entries - unknown,
            'current_unknown_entry_count': unknown,
            'current_standalone_export_candidate_count': standalone,
            'current_context_required_candidate_count': contextual,
            'current_reference_counts': dict(sorted(cur_refs.items())),
            'current_type_subtype_counts': dict(sorted(cur_types.items())),
            'current_export_route_counts': dict(sorted(cur_routes.items())),
            'current_class_label_counts': dict(sorted(cur_classes.items())),
            'indexed_reference_counts': dict(sorted(all_refs.items())),
            'indexed_type_subtype_counts': dict(sorted(all_types.items())),
            'indexed_export_route_counts': dict(sorted(all_routes.items())),
            'indexed_class_label_counts': dict(sorted(all_classes.items())),
            'package_families': {pkg: [{k: physical[i][k] for k in (
                'name','package_id','filename_generation','header_patch_id','is_current','data_offset','size',
                'entry_table_count','entry_table_offset','named_tag_table_count','named_tag_table_offset')}
                for i in ids] for pkg, ids in sorted(families.items())},
            'violations': violations,
            'policy': {
                'current_generation': 'max(header.patch_id, filename_generation, filename) within exact package id',
                'payloads': 'package metadata tables only; no asset payload bodies read',
                'unknowns': 'retained as export_route=unknown rather than omitted',
                'semantics': 'registry routes are byte-validated capabilities and do not prove asset ownership/placement'},
        }
        a.summary.parent.mkdir(parents=True, exist_ok=True)
        a.summary.write_text(json.dumps(summary, indent=2) + '\n')

        fields = ['package_name','package_id','entry_index','tag_hash','reference','type','subtype','file_size',
                  'class_label','export_route','standalone_export','semantic_status','route_tool']
        a.queue.parent.mkdir(parents=True, exist_ok=True)
        with a.queue.open('w', newline='', encoding='utf-8') as f:
            w = csv.writer(f, delimiter='\t'); w.writerow(fields)
            for row in db.execute('''SELECT package_name,package_id,entry_index,tag_hash,reference,type,subtype,file_size,
                                            class_label,export_route,standalone_export,semantic_status,route_tool
                                     FROM current_entries ORDER BY package_id,entry_index'''):
                w.writerow(row)

        print(json.dumps({k: summary[k] for k in (
            'status','physical_package_member_count','package_family_count','current_package_count',
            'current_entry_count','current_distinct_tag_hash_count','current_known_routed_entry_count',
            'current_unknown_entry_count','current_standalone_export_candidate_count')}, indent=2))
        print('ROUTES', json.dumps(summary['current_export_route_counts'], sort_keys=True))
        print('VIOLATIONS', len(violations))
        return 0 if not violations else 2
    finally:
        db.close()


if __name__ == '__main__':
    raise SystemExit(main())
