#!/usr/bin/env python3
"""Fail-closed recursive D1 PS4 entity/control dependency walker.

This tool exists for raid-scale reversal, not only one boss. It deliberately
separates two evidence classes:

1. TYPED_EXACT edges: source/schema-closed serialized relationships, currently
   including s_entity Resource[], known EntityResource model/name/scripted/
   dialogue fields, and validated EntityChildren arrays.
2. UNTYPED_LITERAL edges: aligned u32 values inside otherwise unresolved
   structured payloads which exactly resolve to current FileHashes. These are
   discovery evidence only. They are never promoted to ownership or identity.

The walker can follow both classes to discover deeper controller graphs while
preserving the proof boundary on every path. This makes it suitable for
building a complete raid extraction graph without turning coincidental scalar
matches into semantic claims.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from collections import deque
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from d1_crota_raid_candidate_probe import LazyExactHashResolver, meta_row, norm
from d1_entity_resource_probe import ENTITY_RESOURCE_CLASS, parse_resource
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_entity_child_find import parse_children_resource
from d1_remote_s_entity_resource_package_find import S_ENTITY_REF, parse_entity_resources
from d1_skeleton_probe import parse_skeleton_resource
from d1_split_tar_extract import SplitHttpTar

ENTITY_MODEL_CLASS = '80801AB5'
NULLS = {'00000000', 'FFFFFFFF'}
# These are common support/hash-table-like targets which are useful to record
# but are too broad to recurse through in a control/actor closure.
DEFAULT_NO_RECURSE_REFS = {'8080058A', '80800000'}


def filehash_parts(v: int) -> tuple[int, int] | None:
    # Current D1 Tiger FileHash encoding used throughout the project.
    if not (0x80800000 <= v <= 0x817FFFFF):
        return None
    x = v - 0x80800000
    return (x >> 13) & 0x7FF, x & 0x1FFF


def printable_runs(b: bytes, min_len: int = 4, max_len: int = 256) -> list[dict]:
    printable = set(range(0x20, 0x7F))
    out = []
    start = None
    for i, x in enumerate(b + b'\x00'):
        if x in printable:
            if start is None:
                start = i
        elif start is not None:
            n = i - start
            if min_len <= n <= max_len:
                try:
                    s = b[start:i].decode('utf-8')
                except UnicodeDecodeError:
                    s = None
                if s is not None:
                    out.append({'offset': start, 'string': s})
            start = None
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--seed', action='append', required=True, help='Root FileHash, normally an s_entity')
    ap.add_argument('--member-catalog', action='append', type=Path, required=True)
    ap.add_argument('--base-url', required=True)
    ap.add_argument('--part-count', type=int, default=10)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('--max-depth', type=int, default=5)
    ap.add_argument('--max-nodes', type=int, default=300)
    ap.add_argument('--max-payload-size', type=int, default=8_000_000)
    ap.add_argument('--recurse-untyped', action='store_true',
                    help='Follow exact-but-untyped aligned FileHash discoveries. They remain marked discovery-only.')
    ap.add_argument('-o', '--output', type=Path, required=True)
    a = ap.parse_args()

    catalogs = load_catalogs(a.member_catalog)
    base = a.base_url.rstrip('/')
    arc = SplitHttpTar(
        [f'{base}/packages.tar.{i:03d}' for i in range(1, a.part_count + 1)],
        retries=6,
        timeout=90,
    )
    resolver = LazyExactHashResolver(arc, catalogs, a.runtime)

    seeds = [norm(x) for x in dict.fromkeys(a.seed)]
    q = deque((h, 0, 'TYPED_EXACT_ROOT') for h in seeds)
    # Best path quality: 0 means all typed/root edges; 1 means at least one
    # untyped discovery edge. A later typed route may improve a node.
    best_quality: dict[str, int] = {h: 0 for h in seeds}
    best_depth: dict[str, int] = {h: 0 for h in seeds}
    nodes: dict[str, dict] = {}
    edges: list[dict] = []
    edge_keys = set()
    violations: list[dict] = []
    view_cache: dict[int, object] = {}

    def add_edge(subject: str, predicate: str, obj: str, evidence_class: str,
                 *, offset: int | None = None, attrs: dict | None = None) -> None:
        key = (subject, predicate, obj, evidence_class, offset)
        if key in edge_keys:
            return
        edge_keys.add(key)
        row = {
            'subject': subject,
            'predicate': predicate,
            'object': obj,
            'evidence_class': evidence_class,
        }
        if offset is not None:
            row['offset'] = offset
            row['offset_hex'] = f'0x{offset:X}'
        if attrs:
            row['attrs'] = attrs
        edges.append(row)

    def locate_exact(h: str):
        v = int(h, 16)
        parts = filehash_parts(v)
        if parts is None:
            raise KeyError('not_current_d1_filehash_range')
        pkg, idx = parts
        if pkg not in catalogs:
            raise KeyError(f'package_{pkg:04X}_not_in_verified_catalog')
        view = view_cache.get(pkg)
        if view is None:
            view = resolver.view(pkg)
            view_cache[pkg] = view
        if idx >= len(view.entries):
            raise KeyError(f'file_index_{idx}_outside_{pkg:04X}')
        e = view.entries[idx]
        if e['tag_hash'].upper() != h:
            raise KeyError(f'logical_tag_mismatch_{e["tag_hash"].upper()}')
        return view, e

    def aligned_resolved(payload: bytes, subject: str) -> list[dict]:
        found = []
        end = len(payload) - (len(payload) % 4)
        seen_local = set()
        for off in range(0, end, 4):
            v = struct.unpack_from('<I', payload, off)[0]
            parts = filehash_parts(v)
            if parts is None:
                continue
            h = f'{v:08X}'
            if h in NULLS or h == subject:
                continue
            pkg, idx = parts
            if pkg not in catalogs:
                continue
            try:
                view, e = locate_exact(h)
            except Exception:
                continue
            key = (off, h)
            if key in seen_local:
                continue
            seen_local.add(key)
            found.append({
                'offset': off,
                'tag_hash': h,
                'package_id': f'{pkg:04X}',
                'entry': meta_row(e),
            })
        return found

    def enqueue(target: str, parent_depth: int, parent_quality: int, evidence_class: str, ref: str | None) -> None:
        if parent_depth + 1 > a.max_depth:
            return
        quality = max(parent_quality, 1 if evidence_class == 'UNTYPED_LITERAL' else 0)
        oldq = best_quality.get(target)
        oldd = best_depth.get(target)
        if oldq is None or quality < oldq or (quality == oldq and parent_depth + 1 < oldd):
            best_quality[target] = quality
            best_depth[target] = parent_depth + 1
            # Do not recursively explode through common support tables.
            if ref not in DEFAULT_NO_RECURSE_REFS:
                q.append((target, parent_depth + 1,
                          'TYPED_EXACT_PATH' if quality == 0 else 'CONTAINS_UNTYPED_DISCOVERY'))

    while q and len(nodes) < a.max_nodes:
        h, depth, path_class = q.popleft()
        # If this is an obsolete worse/deeper queue occurrence, skip it.
        qclass = 0 if path_class in ('TYPED_EXACT_ROOT', 'TYPED_EXACT_PATH') else 1
        if qclass != best_quality.get(h, qclass) or depth != best_depth.get(h, depth):
            continue
        if h in nodes and nodes[h].get('processed_path_quality', 99) <= qclass:
            continue

        row = nodes.setdefault(h, {'tag_hash': h})
        row['depth'] = depth
        row['path_class'] = path_class
        row['processed_path_quality'] = qclass
        row.setdefault('violations', [])

        try:
            view, e = locate_exact(h)
            ref = e['reference'].upper()
            row['package_id'] = f'{int(view.h["pkg_id"]):04X}'
            row['entry'] = meta_row(e)
            row['kind'] = (
                's_entity' if ref == S_ENTITY_REF else
                'entity_resource' if ref == ENTITY_RESOURCE_CLASS else
                's_entity_model' if ref == ENTITY_MODEL_CLASS else
                'structured_tag'
            )
            if int(e.get('file_size', 0)) > a.max_payload_size:
                row['payload_skipped'] = 'over_max_payload_size'
                continue
            payload = view.entry(e['index'])
            row['payload_size'] = len(payload)
            row['payload_sha256'] = hashlib.sha256(payload).hexdigest()
            row['printable_strings'] = printable_runs(payload)

            if ref == S_ENTITY_REF:
                resources = parse_entity_resources(payload)
                row['resource_count'] = len(resources)
                row['resources'] = []
                models = set()
                skeletons = []
                child_entities = []
                specific_names = set()
                generic_names = set()
                for rr in resources:
                    rh = norm(rr['resource_hash'])
                    rrout = dict(rr)
                    if rh in NULLS:
                        rrout['resolution_status'] = 'null_or_sentinel'
                        row['resources'].append(rrout)
                        continue
                    try:
                        rv, re = locate_exact(rh)
                        rref = re['reference'].upper()
                        rrout['resolution_status'] = 'resolved_exact'
                        rrout['entry'] = meta_row(re)
                        add_edge(h, 'S_ENTITY_RESOURCE', rh, 'TYPED_EXACT',
                                 attrs={'resource_index': rr.get('resource_index')})
                        enqueue(rh, depth, qclass, 'TYPED_EXACT', rref)
                        if rref == ENTITY_MODEL_CLASS:
                            models.add(rh)
                        if rref == ENTITY_RESOURCE_CLASS and re['type'] == 16 and re['subtype'] == 0:
                            rb = rv.entry(re['index'])
                            er = parse_resource(rb, 'PS4')
                            ers = {
                                'semantic_role': er.get('semantic_role'),
                                'unk10_class': (er.get('unk10') or {}).get('class_hash'),
                                'unk18_class': (er.get('unk18') or {}).get('class_hash'),
                                'embedded_model_tag_hash': er.get('embedded_model_tag_hash'),
                                'entity_name_string_hash': er.get('entity_name_string_hash'),
                                'entity_name_tag_hash': er.get('entity_name_tag_hash'),
                                'scripted_entity_table_tag_hash': er.get('scripted_entity_table_tag_hash'),
                                'dialogue_entity_tag_hash': er.get('dialogue_entity_tag_hash'),
                            }
                            rrout['entity_resource'] = ers
                            if ers.get('embedded_model_tag_hash'):
                                models.add(norm(ers['embedded_model_tag_hash']))
                            if ers.get('entity_name_string_hash'):
                                specific_names.add(norm(ers['entity_name_string_hash']))
                            if ers.get('entity_name_tag_hash'):
                                generic_names.add(norm(ers['entity_name_tag_hash']))
                            if er.get('semantic_role') == 'entity_skeleton':
                                try:
                                    sk = parse_skeleton_resource(rb)
                                    info = sk['skeleton_info']
                                    sr = {
                                        'resource_hash': rh,
                                        'node_count': int(info['node_hierarchy']['count']),
                                        'bone_hashes': [x['node_hash'] for x in info.get('bones', [])],
                                    }
                                    skeletons.append(sr)
                                    rrout['skeleton'] = sr
                                except Exception as ex:
                                    rrout['skeleton_parse_error'] = repr(ex)
                            if er.get('semantic_role') == 'entity_children':
                                try:
                                    ch = parse_children_resource(rb)
                                    if ch is None:
                                        raise ValueError('validated children parser returned None')
                                    rrout['entity_children'] = ch
                                    for c in ch.get('children', []):
                                        eh = norm(c.get('entity_hash', '00000000'))
                                        if eh in NULLS:
                                            continue
                                        child_entities.append({'resource_hash': rh, **c})
                                        add_edge(rh, 'ENTITY_CHILD', eh, 'TYPED_EXACT')
                                        try:
                                            _cv, ce = locate_exact(eh)
                                            enqueue(eh, depth + 1, qclass, 'TYPED_EXACT', ce['reference'].upper())
                                        except Exception:
                                            pass
                    except Exception as ex:
                        rrout['resolution_status'] = 'resolution_error'
                        rrout['resolution_error'] = repr(ex)
                    row['resources'].append(rrout)
                row['embedded_models'] = sorted(models)
                row['skeletons'] = skeletons
                row['child_entities'] = child_entities
                row['specific_name_string_hashes'] = sorted(specific_names)
                row['generic_name_tags'] = sorted(generic_names)
                row['articulated'] = bool(models and skeletons)

            elif ref == ENTITY_RESOURCE_CLASS and e['type'] == 16 and e['subtype'] == 0:
                er = parse_resource(payload, 'PS4')
                role = er.get('semantic_role')
                row['semantic_role'] = role
                row['unk10_class'] = (er.get('unk10') or {}).get('class_hash')
                row['unk18_class'] = (er.get('unk18') or {}).get('class_hash')

                typed_targets: list[tuple[str, str]] = []
                if er.get('embedded_model_tag_hash'):
                    typed_targets.append(('ENTITY_MODEL', norm(er['embedded_model_tag_hash'])))
                if er.get('entity_name_tag_hash'):
                    typed_targets.append(('GENERIC_NAME_TAG', norm(er['entity_name_tag_hash'])))
                if er.get('scripted_entity_table_tag_hash'):
                    typed_targets.append(('SCRIPTED_ENTITY_TABLE', norm(er['scripted_entity_table_tag_hash'])))
                if er.get('dialogue_entity_tag_hash'):
                    typed_targets.append(('DIALOGUE_ENTITY', norm(er['dialogue_entity_tag_hash'])))
                if er.get('entity_name_string_hash'):
                    row['entity_name_string_hash'] = norm(er['entity_name_string_hash'])

                if role == 'entity_skeleton':
                    try:
                        sk = parse_skeleton_resource(payload)
                        info = sk['skeleton_info']
                        row['skeleton'] = {
                            'node_count': int(info['node_hierarchy']['count']),
                            'bone_hashes': [x['node_hash'] for x in info.get('bones', [])],
                        }
                    except Exception as ex:
                        row['skeleton_parse_error'] = repr(ex)
                if role == 'entity_children':
                    try:
                        ch = parse_children_resource(payload)
                        if ch is None:
                            raise ValueError('validated children parser returned None')
                        row['entity_children'] = ch
                        for c in ch.get('children', []):
                            eh = norm(c.get('entity_hash', '00000000'))
                            if eh in NULLS:
                                continue
                            typed_targets.append(('ENTITY_CHILD', eh))
                    except Exception as ex:
                        row['entity_children_parse_error'] = repr(ex)

                for pred, th in typed_targets:
                    if th in NULLS:
                        continue
                    add_edge(h, pred, th, 'TYPED_EXACT')
                    try:
                        _tv, te = locate_exact(th)
                        enqueue(th, depth, qclass, 'TYPED_EXACT', te['reference'].upper())
                    except Exception:
                        pass

                raw = aligned_resolved(payload, h)
                row['aligned_resolved_tags'] = raw
                for m in raw:
                    th = m['tag_hash']
                    tref = m['entry']['reference'].upper()
                    add_edge(h, 'ALIGNED_RESOLVED_FILEHASH', th, 'UNTYPED_LITERAL', offset=m['offset'],
                             attrs={'target_reference': tref})
                    if a.recurse_untyped:
                        enqueue(th, depth, qclass, 'UNTYPED_LITERAL', tref)

            elif ref == ENTITY_MODEL_CLASS:
                # Deliberate leaf for actor-identity closure. Geometry/material
                # dependency expansion is a separate extractor stage.
                row['model_leaf'] = True

            else:
                # Generic structured controller tags reached through the graph.
                # Their aligned matches remain discovery-only until their class
                # schema is independently closed.
                raw = aligned_resolved(payload, h)
                row['aligned_resolved_tags'] = raw
                for m in raw:
                    th = m['tag_hash']
                    tref = m['entry']['reference'].upper()
                    add_edge(h, 'ALIGNED_RESOLVED_FILEHASH', th, 'UNTYPED_LITERAL', offset=m['offset'],
                             attrs={'target_reference': tref})
                    if a.recurse_untyped:
                        enqueue(th, depth, qclass, 'UNTYPED_LITERAL', tref)

        except Exception as ex:
            msg = repr(ex)
            row['violations'].append(msg)
            violations.append({'tag_hash': h, 'depth': depth, 'error': msg})

    articulated = []
    for h, n in nodes.items():
        if n.get('kind') == 's_entity' and n.get('articulated'):
            articulated.append({
                'tag_hash': h,
                'depth': n.get('depth'),
                'path_class': n.get('path_class'),
                'embedded_models': n.get('embedded_models', []),
                'skeletons': [
                    {'resource_hash': s['resource_hash'], 'node_count': s['node_count']}
                    for s in n.get('skeletons', [])
                ],
                'specific_name_string_hashes': n.get('specific_name_string_hashes', []),
                'generic_name_tags': n.get('generic_name_tags', []),
            })

    out = {
        'schema': 'd1_remote_entity_dependency_closure/v1',
        'status': 'D1_ENTITY_DEPENDENCY_CLOSURE_COMPLETE' if not violations else 'D1_ENTITY_DEPENDENCY_CLOSURE_WITH_VIOLATIONS',
        'seeds': seeds,
        'max_depth': a.max_depth,
        'max_nodes': a.max_nodes,
        'recurse_untyped': a.recurse_untyped,
        'node_count': len(nodes),
        'edge_count': len(edges),
        'nodes': [nodes[h] for h in sorted(nodes)],
        'edges': edges,
        'articulated_entities': sorted(articulated, key=lambda x: (x['depth'], x['tag_hash'])),
        'typed_edge_count': sum(e['evidence_class'] == 'TYPED_EXACT' for e in edges),
        'untyped_literal_edge_count': sum(e['evidence_class'] == 'UNTYPED_LITERAL' for e in edges),
        'violations': violations,
        'proof_policy': {
            'typed_exact': 'May support ownership/structure claims when the referenced source-pinned schema says so.',
            'untyped_literal': 'Exact current FileHash equality only. Discovery evidence; never semantic ownership or identity by itself.',
            'path_class': 'Any node whose path_class contains untyped discovery must not be promoted through that path until the intervening schema is closed.',
        },
    }
    if len(nodes) >= a.max_nodes and q:
        out['truncated'] = True
        out['truncation_reason'] = 'max_nodes'
        out['remaining_queue_count'] = len(q)
    else:
        out['truncated'] = False

    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2) + '\n')

    print('STATUS', out['status'], 'SEEDS', seeds, 'NODES', out['node_count'], 'EDGES', out['edge_count'],
          'TYPED', out['typed_edge_count'], 'UNTYPED', out['untyped_literal_edge_count'],
          'ARTICULATED', len(out['articulated_entities']), 'TRUNCATED', out['truncated'])
    for x in out['articulated_entities']:
        print('ARTICULATED', x['tag_hash'], 'DEPTH', x['depth'], 'PATH', x['path_class'],
              'MODELS', x['embedded_models'], 'SKELETONS', x['skeletons'],
              'SPECIFIC', x['specific_name_string_hashes'], 'GENERIC', x['generic_name_tags'])
    return 0 if not violations else 2


if __name__ == '__main__':
    raise SystemExit(main())
