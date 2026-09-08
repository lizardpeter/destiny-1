#!/usr/bin/env python3
"""Trace the exact D1 ROI client_startup_globals root to renderer scope candidates.

Current PS4 named-tag bytes identify 80B1A000 / class 80800341 as
``client_startup_globals``. This probe follows only aligned u32 values that resolve
as actual current FileHashes in the pinned universal package catalog. The walk is
bounded and is discovery-only: an integer edge is not assigned field semantics
unless the target's serialized FileEntry.Reference independently identifies a
known class.

For the final three-NPC material closure we specifically preserve all reached
D1 ROI ``s_scope`` objects (class 80801C47), because TFX gear-plated/gear-dye
state is renderer scope state rather than Material-local state.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from collections import Counter, deque
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_activity_placements import RemoteCorpus, package_of
from d1_split_tar_extract import SplitHttpTar

ROOT = '80B1A000'
ROOT_NAMED_CLASS = '80800341'
SCOPE_CLASS = '80801C47'
NULLS = {'00000000', 'FFFFFFFF'}


def norm(x: object) -> str:
    return str(x).upper().removeprefix('0X').zfill(8)


def filehash_edges(c: RemoteCorpus, owner: str, payload: bytes, catalogs: dict) -> list[dict]:
    out = []
    for off in range(0, len(payload) - 3, 4):
        v = struct.unpack_from('<I', payload, off)[0]
        h = f'{v:08X}'
        if h in NULLS or (v >> 24) != 0x80:
            continue
        try:
            pkg = package_of(h)
        except Exception:
            continue
        if pkg not in catalogs:
            continue
        meta = c.entry_meta(h)
        if meta is None:
            continue
        out.append({
            'owner': owner,
            'offset': off,
            'target': h,
            'package_id': f'{pkg:04X}',
            'reference': norm(meta.get('reference', 'FFFFFFFF')),
            'type': meta.get('type'),
            'subtype': meta.get('subtype'),
            'size': meta.get('file_size'),
        })
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--member-catalog', type=Path, action='append', required=True)
    ap.add_argument('--base-url', required=True)
    ap.add_argument('--part-count', type=int, default=10)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('--max-depth', type=int, default=3)
    ap.add_argument('--max-nodes', type=int, default=512)
    ap.add_argument('--dump-dir', type=Path)
    ap.add_argument('-o', '--output', type=Path, required=True)
    a = ap.parse_args()

    catalogs = load_catalogs(a.member_catalog)
    arc = SplitHttpTar([f'{a.base_url.rstrip("/")}/packages.tar.{i:03d}' for i in range(1, a.part_count + 1)], retries=6, timeout=90)
    c = RemoteCorpus(arc, catalogs, a.runtime)
    violations = []

    root_meta = c.entry_meta(ROOT)
    root_payload, root_src = c.payload(ROOT)
    if root_meta is None or root_payload is None:
        violations.append('client_startup_globals root unavailable')
    if root_meta is not None and package_of(ROOT) != 0x018D:
        violations.append('client_startup_globals root package mismatch')

    q = deque([(ROOT, 0)])
    seen = set()
    nodes = {}
    edges = []
    while q and len(seen) < a.max_nodes:
        h, depth = q.popleft()
        if h in seen:
            continue
        seen.add(h)
        meta = c.entry_meta(h)
        payload, src = c.payload(h)
        row = {
            'hash': h,
            'depth': depth,
            'meta': meta,
            'source': str(src) if src else None,
            'payload_bytes': None if payload is None else len(payload),
            'payload_sha256': None if payload is None else hashlib.sha256(payload).hexdigest(),
        }
        nodes[h] = row
        if payload is None:
            continue
        if a.dump_dir:
            a.dump_dir.mkdir(parents=True, exist_ok=True)
            (a.dump_dir / f'{h}.bin').write_bytes(payload)
        local_edges = filehash_edges(c, h, payload, catalogs)
        edges.extend(local_edges)
        row['resolved_aligned_filehash_edge_count'] = len(local_edges)
        if depth < a.max_depth:
            for e in local_edges:
                if e['target'] not in seen:
                    q.append((e['target'], depth + 1))

    if q and len(seen) >= a.max_nodes:
        violations.append(f'bounded walk hit max_nodes={a.max_nodes}')

    scope_edges = [e for e in edges if e['reference'] == SCOPE_CLASS]
    scope_hashes = sorted({e['target'] for e in scope_edges})
    scope_rows = []
    for h in scope_hashes:
        meta = c.entry_meta(h)
        payload, src = c.payload(h)
        scope_rows.append({
            'scope': h,
            'source': str(src) if src else None,
            'meta': meta,
            'payload_bytes': None if payload is None else len(payload),
            'payload_sha256': None if payload is None else hashlib.sha256(payload).hexdigest(),
            'prefix_hex': None if payload is None else payload[:256].hex(),
            'incoming_edges': [e for e in scope_edges if e['target'] == h],
        })
        if payload is not None and a.dump_dir:
            (a.dump_dir / f'SCOPE_{h}.bin').write_bytes(payload)

    class_hist = Counter(norm((r.get('meta') or {}).get('reference', 'FFFFFFFF')) for r in nodes.values())
    out = {
        'schema_version': 1,
        'status': 'D1_CLIENT_STARTUP_GLOBALS_SCOPE_FRONTIER_EXACT' if not violations else 'D1_CLIENT_STARTUP_GLOBALS_SCOPE_FRONTIER_VIOLATIONS',
        'named_root': {'hash': ROOT, 'named_class': ROOT_NAMED_CLASS, 'package_id': '018D'},
        'walk': {'max_depth': a.max_depth, 'max_nodes': a.max_nodes, 'visited_node_count': len(nodes), 'edge_count': len(edges)},
        'visited_class_histogram': dict(class_hist),
        'scope_class': SCOPE_CLASS,
        'scope_edge_count': len(scope_edges),
        'unique_scope_count': len(scope_hashes),
        'scope_hashes': scope_hashes,
        'scope_rows': scope_rows,
        'edges': edges,
        'nodes': nodes,
        'violations': violations,
        'gates': {
            'client_startup_root_recovered': root_payload is not None,
            'd1_scope_class_reached': bool(scope_hashes),
            'gear_dye_scope_identified': False,
            'api15_runtime_value_closed': False,
            'runtime_t4_binding_closed': False,
        },
        'policy': 'Bounded aligned-FileHash provenance discovery only. Target FileEntry.Reference establishes target class. No arbitrary aligned integer receives field semantics and no reached s_scope is called gear-dye until its own scope contents/usage prove that role.',
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({
        'status': out['status'], 'walk': out['walk'], 'unique_scope_count': out['unique_scope_count'],
        'scope_hashes': scope_hashes, 'class_histogram': dict(class_hist), 'violations': violations,
    }, indent=2))
    return 0 if not violations else 2


if __name__ == '__main__':
    raise SystemExit(main())
