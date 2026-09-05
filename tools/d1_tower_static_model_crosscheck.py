#!/usr/bin/env python3
"""Cross-check a validator-passing D1 baked-static table against decoded s_entity_model reports.

This does not infer ownership.  It only records exact cross-representation equality of:
  vertex0 FileHash, vertex1 FileHash, index FileHash,
  serialized index offset/count, primitive type and LOD/detail level.

When an exact match exists, the ordinary model report supplies an independently decoded
vertex stride/quantization signature which can be used as evidence when validating a
static-world geometry decoder.  No model is assigned to a static record merely because
its buffers overlap.
"""
from __future__ import annotations
import argparse, collections, json
from pathlib import Path


def norm(s: str) -> str:
    return str(s).upper().removeprefix('0X').zfill(8)


def model_index(paths: list[Path]):
    exact = collections.defaultdict(list)
    range_only = collections.defaultdict(list)
    buffers = collections.defaultdict(list)
    report_count = 0
    model_count = 0
    for root in paths:
        files = [root] if root.is_file() else sorted(root.rglob('*.json'))
        for p in files:
            try:
                d = json.loads(p.read_text())
            except Exception:
                continue
            if not isinstance(d, dict) or not isinstance(d.get('meshes'), list) or not d.get('model_tag_hash'):
                continue
            report_count += 1
            model_count += 1
            for mesh_i, m in enumerate(d['meshes']):
                v0, v1, ib = (m.get('vertices1'), m.get('vertices2'), m.get('indices'))
                if not all((v0, v1, ib)):
                    continue
                sig = {
                    'model_tag_hash': norm(d['model_tag_hash']),
                    'model_report': str(p),
                    'mesh_index': mesh_i,
                    'model_scale': m.get('model_scale'),
                    'model_translation': m.get('model_translation'),
                    'texcoord_scale': m.get('texcoord_scale'),
                    'texcoord_translation': m.get('texcoord_translation'),
                    'vertex_stride0': m.get('vertex_stride0'),
                    'vertex_stride1': m.get('vertex_stride1'),
                    'vertex_count': m.get('vertex_count'),
                }
                triple = (norm(v0), norm(v1), norm(ib))
                for g in m.get('primitive_groups', []):
                    base = triple + (int(g['index_offset']), int(g['index_count']), int(g['primitive_type']))
                    rec = {**sig,
                           'candidate_materials': [norm(x) for x in g.get('candidate_materials', [])],
                           'part_indices': g.get('part_indices', []),
                           'lod_values': g.get('lod_values', [])}
                    range_only[base].append(rec)
                    buffers[triple].append(rec)
                    for lod in g.get('lod_values', []) or [None]:
                        exact[base + (None if lod is None else int(lod),)].append(rec)
    return exact, range_only, buffers, {'decoded_model_reports': report_count, 'decoded_models': model_count}


def decode_signature(r: dict):
    return (
        tuple(r.get('model_scale') or []),
        tuple(r.get('model_translation') or []),
        r.get('vertex_stride0'), r.get('vertex_stride1'), r.get('vertex_count'),
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--validation-json', type=Path, required=True)
    ap.add_argument('--model-report-dir', type=Path, action='append', required=True)
    ap.add_argument('--static-map-data', required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()

    validation = json.loads(a.validation_json.read_text())
    h = norm(a.static_map_data)
    rows = [x for x in validation.get('static_map_data', []) if norm(x.get('hash', '0')) == h and x.get('ok')]
    if len(rows) != 1:
        raise SystemExit(f'{h}: expected exactly one validator-passing row, got {len(rows)}')
    d1 = rows[0].get('d1_validation') or {}
    if not d1.get('ok'):
        raise SystemExit(f'{h}: validator-passing parent lacks validator-passing D1 child')

    exact, range_only, buffers, source_summary = model_index(a.model_report_dir)
    out_rows = []
    summary = collections.Counter()
    matching_models = collections.Counter()
    matched_buffer_triples = set()
    conflicting_buffer_triples = set()

    for table_i, table in enumerate(d1.get('static_tables', [])):
        for m in table.get('mesh_entries', []):
            triple = (norm(m['vertices0']), norm(m['vertices1']), norm(m['indices']))
            base = triple + (int(m['index_offset']), int(m['index_count']), int(m['primitive_type']))
            key = base + (int(m['detail_level']),)
            ee = exact.get(key, [])
            rr = range_only.get(base, [])
            bb = buffers.get(triple, [])
            if ee:
                kind = 'EXACT_BUFFER_RANGE_PRIMITIVE_LOD'
                summary['exact'] += 1
                matched_buffer_triples.add(triple)
                sigs = {decode_signature(x) for x in ee}
                if len(sigs) == 1:
                    summary['exact_unique_decode_signature'] += 1
                else:
                    summary['exact_conflicting_decode_signature'] += 1
                    conflicting_buffer_triples.add(triple)
                for x in ee:
                    matching_models[x['model_tag_hash']] += 1
                candidates = ee
            elif rr:
                kind = 'EXACT_BUFFER_RANGE_PRIMITIVE_DIFFERENT_OR_MISSING_LOD'
                summary['range_only'] += 1
                candidates = rr
            elif bb:
                kind = 'BUFFER_TRIPLE_ONLY'
                summary['buffer_only'] += 1
                candidates = bb
            else:
                kind = 'NO_DECODED_MODEL_MATCH'
                summary['none'] += 1
                candidates = []
            out_rows.append({
                'static_table': norm(table['hash']),
                'table_index': table_i,
                'static_mesh_index': int(m['index']),
                'vertices0': triple[0], 'vertices1': triple[1], 'indices': triple[2],
                'index_offset': int(m['index_offset']), 'index_count': int(m['index_count']),
                'primitive_type': int(m['primitive_type']), 'detail_level': int(m['detail_level']),
                'match_kind': kind,
                'candidate_count': len(candidates),
                'matches': candidates,
            })

    report = {
        'evidence_status': 'CROSS_REPRESENTATION_EQUALITY_ONLY',
        'static_map_data': h,
        'd1_static_map_data': norm(d1['hash']),
        'source_model_reports': source_summary,
        'summary': {
            'static_mesh_records': len(out_rows),
            'exact_buffer_range_primitive_lod_matches': summary['exact'],
            'exact_matches_with_unique_decode_signature': summary['exact_unique_decode_signature'],
            'exact_matches_with_conflicting_decode_signature': summary['exact_conflicting_decode_signature'],
            'range_only_matches': summary['range_only'],
            'buffer_only_matches': summary['buffer_only'],
            'no_decoded_model_match': summary['none'],
            'matching_models': dict(sorted(matching_models.items())),
            'matched_unique_buffer_triples': len(matched_buffer_triples),
            'conflicting_decode_buffer_triples': [list(x) for x in sorted(conflicting_buffer_triples)],
        },
        'records': out_rows,
        'policy': {
            'ownership': 'never inferred from shared buffers or matching primitive ranges',
            'promotion': 'only exact serialized equality is reported; model decode parameters are corroborating geometry-layout evidence',
            'unmatched': 'NO_DECODED_MODEL_MATCH means only that supplied decoded model reports contain no exact counterpart',
        },
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report['summary'], indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
