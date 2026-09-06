#!/usr/bin/env python3
"""Build an archive-wide, queryable Destiny 1 PS4 Tiger entry index.

This is the dispatch layer for the project's "export everything" goal.  It walks
current packages.txt and the split TAR once, retains every physical package
occurrence, reads only package metadata tables, and indexes every entry from the
selected current package generation (or every physical generation with
--all-generations).

No asset payload bodies are downloaded.  Unknown reference classes and unknown
(type, subtype) pairs are retained unchanged.  The optional export class registry
adds only previously byte-validated labels/routes and never upgrades semantic
ownership by filename or proximity.
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

from d1_pkg_probe import parse_header, parse_entries, parse_named
from d1_split_tar_extract import SplitHttpTar

ENTRY_STRIDE = 16
NAMED_STRIDE = 68
PKG_RX = re.compile(r'_([0-9A-Fa-f]{4})_([0-9]+)\.pkg$', re.IGNORECASE)


def sha1(data: bytes) -> str:
    return hashlib.sha1(data).hexdigest()


def filename_identity(name: str) -> tuple[str, int] | None:
    m = PKG_RX.search(Path(name).name)
    if not m:
        return None
    return m.group(1).upper(), int(m.group(2))


def norm_hash(x: object) -> str:
    return str(x).upper().removeprefix('0X').zfill(8)


def load_registry(path: Path | None) -> dict:
    if path is None:
        return {'reference_classes': {}, 'type_subtype_classes': {}}
    d = json.loads(path.read_text())
    if d.get('schema') != 'd1_export_class_registry/v1':
        raise ValueError(f'{path}: unsupported registry schema {d.get("schema")!r}')
    return d


def classify(entry: dict, registry: dict) -> dict:
    ref = norm_hash(entry['reference'])
    rr = (registry.get('reference_classes') or {}).get(ref)
    if rr is not None:
        source = f'reference:{ref}'
        rec = rr
    else:
        key = f"{int(entry['type'])}:{int(entry['subtype'])}"
        rec = (registry.get('type_subtype_classes') or {}).get(key)
        source = f'type_subtype:{key}' if rec is not None else None
    if rec is None:
        return {
            'class_label': None,
            'export_route': 'unknown',
            'standalone_export': False,
            'classification_source': None,
            'semantic_status': 'unclassified',
            'route_tool': None,
        }
    standalone = bool(rec.get('standalone_export'))
    return {
        'class_label': rec.get('label'),
        'export_route': rec.get('export_route') or 'known_unrouted',
        'standalone_export': standalone,
        'classification_source': source,
        'semantic_status': rec.get('semantic_status'),
        'route_tool': rec.get('tool'),
    }


def compact_package(p: dict) -> dict:
    keys = (
        'name', 'package_id', 'filename_generation', 'header_patch_id', 'is_current',
        'data_offset', 'size', 'entry_table_count', 'entry_table_offset',
        'named_tag_table_count', 'named_tag_table_offset',
    )
    return {k: p[k] for k in keys}


def create_db(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()
    db = sqlite3.connect(path)
    db.executescript('''
    PRAGMA journal_mode=OFF;
    PRAGMA synchronous=OFF;
    PRAGMA temp_store=MEMORY;

    CREATE TABLE meta (
      key TEXT PRIMARY KEY,
      value TEXT NOT NULL
    );

    CREATE TABLE physical_packages (
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
      is_current INTEGER NOT NULL CHECK(is_current IN (0,1))
    );

    CREATE TABLE entry_occurrences (
      occurrence_id INTEGER PRIMARY KEY,
      package_row INTEGER NOT NULL REFERENCES physical_packages(package_row),
      package_name TEXT NOT NULL,
      package_id TEXT NOT NULL,
      package_generation INTEGER NOT NULL,
      package_patch_id INTEGER NOT NULL,
      is_current INTEGER NOT NULL CHECK(is_current IN (0,1)),
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
      standalone_export INTEGER NOT NULL CHECK(standalone_export IN (0,1)),
      classification_source TEXT,
      semantic_status TEXT NOT NULL,
      route_tool TEXT,
      UNIQUE(package_row, entry_index)
    );

    CREATE TABLE named_tag_occurrences (
      occurrence_id INTEGER PRIMARY KEY,
      package_row INTEGER NOT NULL REFERENCES physical_packages(package_row),
      package_name TEXT NOT NULL,
      package_id TEXT NOT NULL,
      is_current INTEGER NOT NULL CHECK(is_current IN (0,1)),
      named_index INTEGER NOT NULL,
      tag_hash TEXT NOT NULL,
      class_hash TEXT NOT NULL,
      name TEXT,
      UNIQUE(package_row, named_index)
    );

    CREATE TABLE class_registry (
      key_type TEXT NOT NULL,
      key_value TEXT NOT NULL,
      label TEXT,
      export_route TEXT,
      standalone_export INTEGER NOT NULL,
      semantic_status TEXT,
      tool TEXT,
      notes TEXT,
      PRIMARY KEY(key_type, key_value)
    );

    CREATE TABLE violations (
      violation_id INTEGER PRIMARY KEY,
      package_name TEXT,
      stage TEXT NOT NULL,
      detail TEXT NOT NULL
    );

    CREATE INDEX idx_pkg_family ON physical_packages(package_id, is_current);
    CREATE INDEX idx_entry_tag ON entry_occurrences(tag_hash);
    CREATE INDEX idx_entry_ref ON entry_occurrences(reference);
    CREATE INDEX idx_entry_type_subtype ON entry_occurrences(type, subtype);
    CREATE INDEX idx_entry_current ON entry_occurrences(is_current);
    CREATE INDEX idx_entry_route ON entry_occurrences(export_route, is_current);
    CREATE INDEX idx_named_tag ON named_tag_occurrences(tag_hash);
    CREATE INDEX idx_named_class ON named_tag_occurrences(class_hash);

    CREATE VIEW current_entries AS
      SELECT * FROM entry_occurrences WHERE is_current=1;

    CREATE VIEW current_export_queue AS
      SELECT occurrence_id, package_name, package_id, entry_index, tag_hash,
             reference, type, subtype, class_label, export_route,
             standalone_export, semantic_status, route_tool
      FROM entry_occurrences
      WHERE is_current=1;

    CREATE VIEW current_logical_resources AS
      SELECT tag_hash,
             COUNT(*) AS occurrence_count,
             COUNT(DISTINCT package_id) AS package_id_count,
             GROUP_CONCAT(DISTINCT reference) AS references,
             GROUP_CONCAT(DISTINCT export_route) AS export_routes,
             MAX(class_label) AS class_label,
             MAX(standalone_export) AS any_standalone_export
      FROM entry_occurrences
      WHERE is_current=1
      GROUP BY tag_hash;
    ''')
    return db


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--package-list', type=Path, required=True)
    ap.add_argument('--registry', type=Path)
    ap.add_argument('--sqlite', type=Path, required=True)
    ap.add_argument('--summary', type=Path, required=True)
    ap.add_argument('--queue', type=Path, required=True)
    ap.add_argument('--all-generations', action='store_true',
                    help='index entry/named-tag tables for every physical generation, not only current winners')
    ap.add_argument('--base-url', default='https://crypt.cohae.dev/destiny/ps4/packages/latest')
    ap.add_argument('--part-count', type=int, default=10)
    ap.add_argument('--retries', type=int, default=6)
    ap.add_argument('--timeout', type=int, default=120)
    a = ap.parse_args()

    registry = load_registry(a.registry)
    package_list_bytes = a.package_list.read_bytes()
    package_list_sha256 = hashlib.sha256(package_list_bytes).hexdigest()
    listed: list[str] = []
    seen = set()
    for raw in package_list_bytes.decode('utf-8', errors='replace').splitlines():
        name = Path(raw.strip()).name
        if not name or name in seen or filename_identity(name) is None:
            continue
        seen.add(name)
        listed.append(name)
    listed.sort()
    if not listed:
        raise SystemExit('packages.txt yielded no parseable .pkg members')

    arc = SplitHttpTar(
        [f"{a.base_url.rstrip('/')}/packages.tar.{i:03d}" for i in range(1, a.part_count + 1)],
        retries=a.retries,
        timeout=a.timeout,
    )
    locations, tar_headers_scanned = arc.find(set(listed))
    missing = sorted(set(listed) - set(locations))
    if missing:
        raise SystemExit(f'{len(missing)} packages.txt members absent from split TAR: {missing[:20]}')

    violations: list[dict] = []
    physical: list[dict] = []
    families: dict[str, list[int]] = defaultdict(list)

    for n, name in enumerate(listed, 1):
        loc = locations[name]
        ident = filename_identity(name)
        assert ident is not None
        filename_pkg, generation = ident
        if int(loc['size']) < 0x140:
            violations.append({'package_name': name, 'stage': 'header', 'detail': f'package shorter than 0x140: {loc["size"]}'})
            continue
        hb = arc.read_at(int(loc['data_offset']), 0x140)
        try:
            h = parse_header(io.BytesIO(hb))
        except Exception as ex:
            violations.append({'package_name': name, 'stage': 'header', 'detail': repr(ex)})
            continue
        pkg = f"{int(h['pkg_id']):04X}"
        if pkg != filename_pkg:
            violations.append({'package_name': name, 'stage': 'header', 'detail': f'filename package {filename_pkg} != header {pkg}'})
        if h['platform'] != 'PS4':
            violations.append({'package_name': name, 'stage': 'header', 'detail': f'unexpected platform {h["platform"]}'})
        row = {
            'name': name,
            'package_id': pkg,
            'filename_package_id': filename_pkg,
            'filename_generation': generation,
            'header_patch_id': int(h['patch_id']),
            'platform': h['platform'],
            'platform_code': int(h['platform_code']),
            'language': h['language'],
            'language_code': int(h['language_code']),
            'tar_header_offset': int(loc['header_offset']),
            'data_offset': int(loc['data_offset']),
            'size': int(loc['size']),
            'entry_table_count': int(h['entry_table_count']),
            'entry_table_offset': int(h['entry_table_offset']),
            'entry_table_sha1_expected': str(h['entry_table_hash']).lower(),
            'block_table_count': int(h['block_table_count']),
            'block_table_offset': int(h['block_table_offset']),
            'named_tag_table_count': int(h['named_tag_table_count']),
            'named_tag_table_offset': int(h['named_tag_table_offset']),
            'named_tag_table_sha1_expected': str(h['named_tag_table_hash']).lower(),
            'is_current': False,
        }
        pi = len(physical)
        physical.append(row)
        families[pkg].append(pi)
        if n % 100 == 0 or n == len(listed):
            print(f'HEADERS {n}/{len(listed)}', flush=True)

    for pkg, indexes in families.items():
        winner = max(indexes, key=lambda i: (
            physical[i]['header_patch_id'], physical[i]['filename_generation'], physical[i]['name']))
        physical[winner]['is_current'] = True

    db = create_db(a.sqlite)
    try:
        db.executemany(
            'INSERT INTO meta(key,value) VALUES(?,?)',
            [
                ('schema', 'd1_remote_everything_index/v1'),
                ('packages_txt_sha256', package_list_sha256),
                ('base_url', a.base_url),
                ('part_count', str(a.part_count)),
                ('index_mode', 'all_generations' if a.all_generations else 'current_only'),
            ],
        )
        for key, rec in sorted((registry.get('reference_classes') or {}).items()):
            db.execute('INSERT INTO class_registry VALUES(?,?,?,?,?,?,?,?)', (
                'reference', norm_hash(key), rec.get('label'), rec.get('export_route'), int(bool(rec.get('standalone_export'))),
                rec.get('semantic_status'), rec.get('tool'), rec.get('notes')))
        for key, rec in sorted((registry.get('type_subtype_classes') or {}).items()):
            db.execute('INSERT INTO class_registry VALUES(?,?,?,?,?,?,?,?)', (
                'type_subtype', key, rec.get('label'), rec.get('export_route'), int(bool(rec.get('standalone_export'))),
                rec.get('semantic_status'), rec.get('tool'), rec.get('notes')))

        for i, p in enumerate(physical):
            db.execute('INSERT INTO physical_packages VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', (
                i, p['name'], p['package_id'], p['filename_package_id'], p['filename_generation'], p['header_patch_id'],
                p['platform'], p['platform_code'], p['language'], p['language_code'], p['tar_header_offset'], p['data_offset'],
                p['size'], p['entry_table_count'], p['entry_table_offset'], p['entry_table_sha1_expected'],
                p['block_table_count'], p['block_table_offset'], p['named_tag_table_count'], p['named_tag_table_offset'],
                p['named_tag_table_sha1_expected'], int(p['is_current'])))

        reference_counts = Counter()
        type_counts = Counter()
        route_counts = Counter()
        class_counts = Counter()
        current_reference_counts = Counter()
        current_type_counts = Counter()
        current_route_counts = Counter()
        current_class_counts = Counter()
        indexed_packages = 0
        indexed_entries = 0
        current_entries = 0
        named_rows = 0
        current_named_rows = 0

        for n, p in enumerate(physical, 1):
            if not (p['is_current'] or a.all_generations):
                continue
            indexed_packages += 1
            et_n = p['entry_table_count'] * ENTRY_STRIDE
            nt_n = p['named_tag_table_count'] * NAMED_STRIDE
            if p['entry_table_offset'] < 0 or p['entry_table_offset'] + et_n > p['size']:
                violations.append({'package_name': p['name'], 'stage': 'entry_table', 'detail': f'bounds {p["entry_table_offset"]}+{et_n}>{p["size"]}'})
                continue
            try:
                et = arc.read_at(p['data_offset'] + p['entry_table_offset'], et_n)
            except Exception as ex:
                violations.append({'package_name': p['name'], 'stage': 'entry_table', 'detail': repr(ex)})
                continue
            actual = sha1(et)
            if actual != p['entry_table_sha1_expected']:
                violations.append({'package_name': p['name'], 'stage': 'entry_table', 'detail': f'sha1 {actual} != {p["entry_table_sha1_expected"]}'})
                continue
            entries = parse_entries(et, int(p['package_id'], 16))
            if len(entries) != p['entry_table_count']:
                violations.append({'package_name': p['name'], 'stage': 'entry_table', 'detail': f'parsed count {len(entries)} != {p["entry_table_count"]}'})
                continue
            for e in entries:
                cl = classify(e, registry)
                db.execute('''INSERT INTO entry_occurrences(
                    package_row,package_name,package_id,package_generation,package_patch_id,is_current,
                    entry_index,tag_hash,reference,type,subtype,entry_b,file_size,starting_block,starting_block_offset,
                    class_label,export_route,standalone_export,classification_source,semantic_status,route_tool)
                    VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (
                    physical.index(p), p['name'], p['package_id'], p['filename_generation'], p['header_patch_id'], int(p['is_current']),
                    int(e['index']), norm_hash(e['tag_hash']), norm_hash(e['reference']), int(e['type']), int(e['subtype']),
                    norm_hash(e['entry_b']), int(e['file_size']), int(e['starting_block']), int(e['starting_block_offset']),
                    cl['class_label'], cl['export_route'], int(cl['standalone_export']), cl['classification_source'],
                    cl['semantic_status'], cl['route_tool']))
                reference_counts[norm_hash(e['reference'])] += 1
                type_counts[f"{int(e['type'])}:{int(e['subtype'])}"] += 1
                route_counts[cl['export_route']] += 1
                if cl['class_label']:
                    class_counts[cl['class_label']] += 1
                indexed_entries += 1
                if p['is_current']:
                    current_reference_counts[norm_hash(e['reference'])] += 1
                    current_type_counts[f"{int(e['type'])}:{int(e['subtype'])}"] += 1
                    current_route_counts[cl['export_route']] += 1
                    if cl['class_label']:
                        current_class_counts[cl['class_label']] += 1
                    current_entries += 1

            if nt_n:
                if p['named_tag_table_offset'] < 0 or p['named_tag_table_offset'] + nt_n > p['size']:
                    violations.append({'package_name': p['name'], 'stage': 'named_tag_table', 'detail': f'bounds {p["named_tag_table_offset"]}+{nt_n}>{p["size"]}'})
                else:
                    try:
                        nt = arc.read_at(p['data_offset'] + p['named_tag_table_offset'], nt_n)
                        nsha = sha1(nt)
                        if nsha != p['named_tag_table_sha1_expected']:
                            violations.append({'package_name': p['name'], 'stage': 'named_tag_table', 'detail': f'sha1 {nsha} != {p["named_tag_table_sha1_expected"]}'})
                        else:
                            for x in parse_named(nt):
                                db.execute('''INSERT INTO named_tag_occurrences(package_row,package_name,package_id,is_current,named_index,tag_hash,class_hash,name)
                                              VALUES(?,?,?,?,?,?,?,?)''', (
                                    physical.index(p), p['name'], p['package_id'], int(p['is_current']), int(x['index']),
                                    norm_hash(x['tag_hash']), norm_hash(x['class_hash']), x.get('name')))
                                named_rows += 1
                                if p['is_current']:
                                    current_named_rows += 1
                    except Exception as ex:
                        violations.append({'package_name': p['name'], 'stage': 'named_tag_table', 'detail': repr(ex)})
            if n % 50 == 0 or n == len(physical):
                print(f'TABLES {n}/{len(physical)} indexed_packages={indexed_packages} entries={indexed_entries}', flush=True)

        for v in violations:
            db.execute('INSERT INTO violations(package_name,stage,detail) VALUES(?,?,?)', (v.get('package_name'), v['stage'], v['detail']))
        db.commit()

        distinct_current_tags = db.execute('SELECT COUNT(DISTINCT tag_hash) FROM current_entries').fetchone()[0]
        duplicate_current_tags = db.execute('''SELECT COUNT(*) FROM (
            SELECT tag_hash FROM current_entries GROUP BY tag_hash HAVING COUNT(*)>1)''').fetchone()[0]
        unknown_current = int(current_route_counts.get('unknown', 0))
        known_current = current_entries - unknown_current
        standalone_current = db.execute('SELECT COUNT(*) FROM current_entries WHERE standalone_export=1').fetchone()[0]
        contextual_current = db.execute("SELECT COUNT(*) FROM current_entries WHERE export_route!='unknown' AND standalone_export=0").fetchone()[0]

        summary = {
            'schema': 'd1_remote_everything_index/v1',
            'status': 'D1_REMOTE_EVERYTHING_INDEX_COMPLETE' if not violations else 'D1_REMOTE_EVERYTHING_INDEX_PARTIAL',
            'mode': 'all_generations' if a.all_generations else 'current_only',
            'source': {
                'package_list': str(a.package_list),
                'packages_txt_sha256': package_list_sha256,
                'base_url': a.base_url,
                'part_count': a.part_count,
                'part_sizes': arc.sizes,
                'logical_split_tar_bytes': arc.logical_size,
                'tar_headers_scanned': tar_headers_scanned,
            },
            'physical_package_member_count': len(physical),
            'package_family_count': len(families),
            'current_package_count': sum(int(p['is_current']) for p in physical),
            'indexed_package_generation_count': indexed_packages,
            'indexed_entry_occurrence_count': indexed_entries,
            'current_entry_count': current_entries,
            'current_distinct_tag_hash_count': int(distinct_current_tags),
            'current_duplicate_tag_hash_count': int(duplicate_current_tags),
            'indexed_named_tag_count': named_rows,
            'current_named_tag_count': current_named_rows,
            'current_known_routed_entry_count': known_current,
            'current_unknown_entry_count': unknown_current,
            'current_standalone_export_candidate_count': int(standalone_current),
            'current_context_required_candidate_count': int(contextual_current),
            'current_reference_counts': dict(sorted(current_reference_counts.items())),
            'current_type_subtype_counts': dict(sorted(current_type_counts.items())),
            'current_export_route_counts': dict(sorted(current_route_counts.items())),
            'current_class_label_counts': dict(sorted(current_class_counts.items())),
            'indexed_reference_counts': dict(sorted(reference_counts.items())),
            'indexed_type_subtype_counts': dict(sorted(type_counts.items())),
            'indexed_export_route_counts': dict(sorted(route_counts.items())),
            'indexed_class_label_counts': dict(sorted(class_counts.items())),
            'package_families': {
                pkg: [compact_package(physical[i]) for i in indexes]
                for pkg, indexes in sorted(families.items())
            },
            'violations': violations,
            'policy': {
                'current_generation': 'max(header.patch_id, filename_generation, filename) within exact package id',
                'payloads': 'no asset payload bodies are read; only package header, entry table and named-tag table metadata',
                'unknowns': 'unknown classes/type-subtypes remain indexed with export_route=unknown',
                'semantics': 'registry labels/routes are byte-validated capabilities only and never infer ownership/placement from package names',
            },
        }
        a.summary.parent.mkdir(parents=True, exist_ok=True)
        a.summary.write_text(json.dumps(summary, indent=2) + '\n')

        a.queue.parent.mkdir(parents=True, exist_ok=True)
        with a.queue.open('w', newline='', encoding='utf-8') as f:
            fields = [
                'package_name','package_id','entry_index','tag_hash','reference','type','subtype','file_size',
                'class_label','export_route','standalone_export','semantic_status','route_tool'
            ]
            w = csv.DictWriter(f, fieldnames=fields, delimiter='\t')
            w.writeheader()
            cur = db.execute('''SELECT package_name,package_id,entry_index,tag_hash,reference,type,subtype,file_size,
                                       class_label,export_route,standalone_export,semantic_status,route_tool
                                FROM current_entries ORDER BY package_id,entry_index''')
            for row in cur:
                w.writerow(dict(zip(fields, row)))

        print(json.dumps({
            'status': summary['status'],
            'physical_package_member_count': summary['physical_package_member_count'],
            'package_family_count': summary['package_family_count'],
            'current_entry_count': summary['current_entry_count'],
            'current_distinct_tag_hash_count': summary['current_distinct_tag_hash_count'],
            'current_known_routed_entry_count': summary['current_known_routed_entry_count'],
            'current_unknown_entry_count': summary['current_unknown_entry_count'],
            'current_export_route_counts': summary['current_export_route_counts'],
            'violation_count': len(violations),
        }, indent=2))
        return 0 if not violations else 2
    finally:
        db.close()


if __name__ == '__main__':
    raise SystemExit(main())
