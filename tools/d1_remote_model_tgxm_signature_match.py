#!/usr/bin/env python3
"""Match retail D1 PS4 ``s_entity_model`` assets to an exact Bungie TGXM model.

This is a structural candidate resolver, not a visual matcher.  The target TGXM is
parsed losslessly with :mod:`d1_tgxm_unpack`; PS4 models are parsed with the exact
D1 ``SEntityModel`` parser.  The comparison uses serialized invariants which are
meaningful across the mobile/web and PS4 encodings:

* render mesh count and mesh order;
* vertex count per mesh (all vertex streams must agree internally);
* index count per mesh;
* stage-0 highest-LOD part count;
* stage-0 highest-LOD per-part index-count sequence.

Vertex *strides* and formats are recorded but deliberately not required to match,
because Bungie's published TGXM geometry can use a different vertex encoding from
retail PS4.  No spatial similarity, naming, neighboring FileHash, or guessed bone
semantics participates in the score.

Remote package families are opened lazily from verified member catalogs.  Every
FileHash routes to the exact package encoded by the Tiger hash; no locality fallback
is permitted.
"""
from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from d1_entity_model_probe import D1_ENTITY_MODEL_CLASS, parse_model
from d1_guardian_stage_part_material_resolve import HIGHEST_LODS
from d1_investment_arrangement_probe import filehash_pkg_index
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_investment_parent_probe import RemoteLogicalPackage
from d1_split_tar_extract import SplitHttpTar
from d1_tgxm_unpack import parse_tgxm


def norm_hash(v: str) -> str:
    return v.upper().removeprefix('0X').zfill(8)


def package_of_hash(v: str) -> int:
    return filehash_pkg_index(int(norm_hash(v), 16))[0]


class LazyExactHashResolver:
    """Resolve Tiger FileHashes through only their encoded verified package family."""

    def __init__(self, arc: SplitHttpTar, catalogs: dict[int, dict], runtime: Path):
        self.arc = arc
        self.catalogs = catalogs
        self.runtime = runtime
        self.views: dict[int, RemoteLogicalPackage] = {}
        self.maps: dict[int, dict[str, dict]] = {}

    def view(self, pkg: int) -> RemoteLogicalPackage:
        if pkg not in self.catalogs:
            raise KeyError(f'no verified member catalog for package {pkg:04X}')
        if pkg not in self.views:
            self.views[pkg] = RemoteLogicalPackage(self.arc, self.catalogs[pkg], self.runtime)
        return self.views[pkg]

    def hash_map(self, pkg: int) -> dict[str, dict]:
        if pkg not in self.maps:
            view = self.view(pkg)
            m: dict[str, dict] = {}
            for e in view.entries:
                h = e['tag_hash'].upper()
                if h in m:
                    raise ValueError(f'duplicate FileHash {h} in package {pkg:04X}')
                m[h] = e
            self.maps[pkg] = m
        return self.maps[pkg]

    def locate(self, tag_hash: str) -> tuple[RemoteLogicalPackage, dict]:
        h = norm_hash(tag_hash)
        pkg = package_of_hash(h)
        e = self.hash_map(pkg).get(h)
        if e is None:
            raise KeyError(f'{h}: not present in exact logical package {pkg:04X}')
        return self.view(pkg), e

    def bytes(self, tag_hash: str) -> tuple[RemoteLogicalPackage, dict, bytes]:
        view, e = self.locate(tag_hash)
        return view, e, view.entry(e['index'])


def tgxm_target_signature(path: Path) -> dict[str, Any]:
    rep = parse_tgxm(path.read_bytes())
    md = rep.get('render_metadata') or {}
    meshes = ((md.get('render_model') or {}).get('render_meshes') or [])
    if not meshes:
        raise ValueError('target TGXM has no render_model.render_meshes')
    out_meshes = []
    for mi, mesh in enumerate(meshes):
        vertex_counts = []
        strides = []
        vertex_bytes = []
        for vb in mesh.get('vertex_buffers') or []:
            size = int(vb['byte_size'])
            stride = int(vb['stride_byte_size'])
            if stride <= 0 or size % stride:
                raise ValueError(f'target mesh {mi}: invalid vertex buffer size/stride {size}/{stride}')
            vertex_counts.append(size // stride)
            strides.append(stride)
            vertex_bytes.append(size)
        if not vertex_counts or len(set(vertex_counts)) != 1:
            raise ValueError(f'target mesh {mi}: vertex streams disagree {vertex_counts}')
        ib = mesh['index_buffer']
        ib_size = int(ib['byte_size'])
        ib_value = int(ib['value_byte_size'])
        if ib_value not in (2, 4) or ib_size % ib_value:
            raise ValueError(f'target mesh {mi}: invalid index buffer size/value size {ib_size}/{ib_value}')
        offsets = [int(x) for x in (mesh.get('stage_part_offsets') or [])]
        parts = mesh.get('stage_part_list') or []
        if len(offsets) < 2:
            raise ValueError(f'target mesh {mi}: missing stage 0 boundaries')
        start, end = offsets[0], offsets[1]
        if start < 0 or end < start or end > len(parts):
            raise ValueError(f'target mesh {mi}: invalid stage0 [{start},{end})/{len(parts)}')
        selected = []
        for pi in range(start, end):
            p = parts[pi]
            lod_name = str((p.get('lod_category') or {}).get('name', ''))
            if '0' not in lod_name:
                continue
            selected.append({
                'part_index': pi,
                'index_start': int(p['start_index']),
                'index_count': int(p['index_count']),
                'primitive_type': int(p['primitive_type']),
                'lod_name': lod_name,
                'gear_dye_change_color_index': int(p.get('gear_dye_change_color_index', 0)),
            })
        out_meshes.append({
            'mesh_index': mi,
            'vertex_count': vertex_counts[0],
            'vertex_stream_count': len(vertex_counts),
            'vertex_strides': strides,
            'vertex_buffer_bytes': vertex_bytes,
            'index_count': ib_size // ib_value,
            'index_value_byte_size': ib_value,
            'stage0_start': start,
            'stage0_end_exclusive': end,
            'stage0_highest_part_count': len(selected),
            'stage0_highest_index_counts': [x['index_count'] for x in selected],
            'stage0_highest_primitive_types': [x['primitive_type'] for x in selected],
            'stage0_highest_parts': selected,
        })
    return {
        'source_tgxm': str(path),
        'tgxm_sha256': rep['sha256'],
        'tgxm_file_identifier': rep['file_identifier'],
        'mesh_count': len(out_meshes),
        'meshes': out_meshes,
    }


def linked_buffer_signature(resolver: LazyExactHashResolver, header_hash: str, kind: str) -> dict[str, Any]:
    h = norm_hash(header_hash)
    if h == 'FFFFFFFF':
        raise ValueError(f'{kind}: missing FFFFFFFF resource')
    _view, e, hb = resolver.bytes(h)
    payload_hash = norm_hash(e['reference'])
    _pv, pe = resolver.locate(payload_hash)
    payload_size = int(pe['file_size'])
    if kind == 'vertex':
        if len(hb) < 6:
            raise ValueError(f'{h}: vertex header shorter than 6 bytes')
        stride = int(struct.unpack_from('<h', hb, 4)[0])
        if stride <= 0 or payload_size % stride:
            raise ValueError(f'{h}: vertex payload {payload_size} not divisible by stride {stride}')
        return {
            'header_hash': h,
            'header_package_id': f'{package_of_hash(h):04X}',
            'payload_hash': payload_hash,
            'payload_package_id': f'{package_of_hash(payload_hash):04X}',
            'payload_bytes': payload_size,
            'stride': stride,
            'value_count': payload_size // stride,
        }
    if kind == 'index':
        if len(hb) < 2:
            raise ValueError(f'{h}: index header shorter than 2 bytes')
        value_size = 4 if bool(hb[1]) else 2
        if payload_size % value_size:
            raise ValueError(f'{h}: index payload {payload_size} not divisible by {value_size}')
        return {
            'header_hash': h,
            'header_package_id': f'{package_of_hash(h):04X}',
            'payload_hash': payload_hash,
            'payload_package_id': f'{package_of_hash(payload_hash):04X}',
            'payload_bytes': payload_size,
            'value_byte_size': value_size,
            'value_count': payload_size // value_size,
        }
    raise ValueError(kind)


def ps4_model_signature(resolver: LazyExactHashResolver, model_hash: str, model_bytes: bytes) -> dict[str, Any]:
    model = parse_model(model_bytes, 'PS4')
    out_meshes = []
    for mi, mesh in enumerate(model['meshes']):
        v0 = linked_buffer_signature(resolver, mesh['vertices1'], 'vertex')
        v1 = linked_buffer_signature(resolver, mesh['vertices2'], 'vertex')
        if v0['value_count'] != v1['value_count']:
            raise ValueError(f'{model_hash} mesh {mi}: PS4 vertex streams disagree {v0["value_count"]}/{v1["value_count"]}')
        ib = linked_buffer_signature(resolver, mesh['indices'], 'index')
        offsets = [int(x) for x in (mesh.get('stage_part_offsets_source_derived') or [])]
        if len(offsets) < 2:
            raise ValueError(f'{model_hash} mesh {mi}: missing PS4 stage0 boundaries')
        parts = mesh['parts']
        start, end = offsets[0], offsets[1]
        if start < 0 or end < start or end > len(parts):
            raise ValueError(f'{model_hash} mesh {mi}: invalid PS4 stage0 [{start},{end})/{len(parts)}')
        selected = []
        for pi in range(start, end):
            p = parts[pi]
            if int(p['lod']) not in HIGHEST_LODS:
                continue
            selected.append({
                'part_index': pi,
                'index_offset': int(p['index_offset']),
                'index_count': int(p['index_count']),
                'primitive_type': int(p['primitive_type']),
                'lod': int(p['lod']),
                'gear_dye_change_color_index': int(p['gear_dye_change_color_index']),
            })
        out_meshes.append({
            'mesh_index': mi,
            'vertex_count': v0['value_count'],
            'vertex_stream_count': 2,
            'vertex_strides': [v0['stride'], v1['stride']],
            'vertex_buffers': [v0, v1],
            'index_count': ib['value_count'],
            'index_value_byte_size': ib['value_byte_size'],
            'index_buffer': ib,
            'stage0_start': start,
            'stage0_end_exclusive': end,
            'stage0_highest_part_count': len(selected),
            'stage0_highest_index_counts': [x['index_count'] for x in selected],
            'stage0_highest_primitive_types': [x['primitive_type'] for x in selected],
            'stage0_highest_parts': selected,
        })
    return {
        'model_tag_hash': norm_hash(model_hash),
        'mesh_count': model['mesh_count'],
        'meshes': out_meshes,
    }


def compare_signatures(target: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    tm = target['meshes']
    cm = candidate['meshes']
    mesh_count_match = len(tm) == len(cm)
    n = min(len(tm), len(cm))
    vertex_matches = [tm[i]['vertex_count'] == cm[i]['vertex_count'] for i in range(n)]
    index_matches = [tm[i]['index_count'] == cm[i]['index_count'] for i in range(n)]
    stage_count_matches = [tm[i]['stage0_highest_part_count'] == cm[i]['stage0_highest_part_count'] for i in range(n)]
    stage_index_count_matches = [tm[i]['stage0_highest_index_counts'] == cm[i]['stage0_highest_index_counts'] for i in range(n)]
    # Primitive enum values happen to use 3/5 in both published TGXM and PS4 metadata,
    # but keep this as a separate corroborating field rather than folding it into the
    # minimum structural match.
    primitive_matches = [tm[i]['stage0_highest_primitive_types'] == cm[i]['stage0_highest_primitive_types'] for i in range(n)]
    score = (
        1000 * int(mesh_count_match)
        + 100 * sum(vertex_matches)
        + 50 * sum(index_matches)
        + 20 * sum(stage_count_matches)
        + 10 * sum(stage_index_count_matches)
        + 5 * sum(primitive_matches)
    )
    topology_structure_exact = (
        mesh_count_match
        and len(tm) == n
        and all(vertex_matches)
        and all(index_matches)
        and all(stage_count_matches)
        and all(stage_index_count_matches)
    )
    return {
        'score': score,
        'mesh_count_match': mesh_count_match,
        'vertex_count_matches': vertex_matches,
        'index_count_matches': index_matches,
        'stage0_highest_part_count_matches': stage_count_matches,
        'stage0_highest_index_count_sequence_matches': stage_index_count_matches,
        'stage0_highest_primitive_sequence_matches': primitive_matches,
        'topology_structure_exact': topology_structure_exact,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--scan-package-id', action='append', type=lambda x: int(x, 0), required=True)
    ap.add_argument('--target-tgxm', type=Path, required=True)
    ap.add_argument('--member-catalog', type=Path, action='append', required=True)
    ap.add_argument('--base-url', required=True)
    ap.add_argument('--part-count', type=int, default=10)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('--keep-top', type=int, default=25)
    ap.add_argument('-o', '--output', type=Path, required=True)
    a = ap.parse_args()

    target = tgxm_target_signature(a.target_tgxm)
    catalogs = load_catalogs(a.member_catalog)
    scan_ids = list(dict.fromkeys(a.scan_package_id))
    missing = [x for x in scan_ids if x not in catalogs]
    if missing:
        raise SystemExit('missing verified scan package catalogs: ' + ', '.join(f'{x:04X}' for x in missing))

    base = a.base_url.rstrip('/')
    arc = SplitHttpTar([f'{base}/packages.tar.{i:03d}' for i in range(1, a.part_count + 1)], retries=6, timeout=90)
    resolver = LazyExactHashResolver(arc, catalogs, a.runtime)

    candidates = []
    scanned_models = 0
    mesh_count_candidates = 0
    errors = []
    for pkg in scan_ids:
        view = resolver.view(pkg)
        for e in view.entries:
            if e['type'] != 16 or e['subtype'] != 0 or e['reference'].upper() != D1_ENTITY_MODEL_CLASS:
                continue
            scanned_models += 1
            tag = e['tag_hash'].upper()
            try:
                raw = view.entry(e['index'])
                model = parse_model(raw, 'PS4')
                if int(model['mesh_count']) != int(target['mesh_count']):
                    continue
                mesh_count_candidates += 1
                sig = ps4_model_signature(resolver, tag, raw)
                cmp = compare_signatures(target, sig)
                candidates.append({
                    'package_id': f'{pkg:04X}',
                    'entry_index': e['index'],
                    'tag_hash': tag,
                    'model_file_size': int(e['file_size']),
                    'comparison': cmp,
                    'signature': sig,
                })
                if cmp['topology_structure_exact']:
                    print('EXACT_STRUCTURAL_MATCH', f'{pkg:04X}', tag, 'score', cmp['score'])
            except Exception as ex:
                errors.append({'package_id': f'{pkg:04X}', 'tag_hash': tag, 'entry_index': e['index'], 'error': repr(ex)})

    candidates.sort(key=lambda x: (-x['comparison']['score'], x['package_id'], x['tag_hash']))
    exact = [x for x in candidates if x['comparison']['topology_structure_exact']]
    top = candidates[:max(0, a.keep_top)]
    rep = {
        'schema': 'd1_remote_model_tgxm_signature_match/v1',
        'target': target,
        'scan_package_ids': [f'{x:04X}' for x in scan_ids],
        'scanned_entity_model_count': scanned_models,
        'target_mesh_count_candidate_count': mesh_count_candidates,
        'resolved_candidate_count': len(candidates),
        'exact_topology_structure_match_count': len(exact),
        'exact_matches': exact,
        'top_candidates': top,
        'error_count': len(errors),
        'errors': errors,
        'policy': (
            'Candidate comparison uses only exact serialized cross-platform structural invariants: mesh order/count, '
            'per-mesh vertex/index counts, and source-defined stage-0 highest-LOD part/index-count structure. Vertex '
            'formats/strides are recorded but are not required to match across mobile TGXM and PS4. No names, visual '
            'similarity, neighboring hashes, bounds proximity, or bone guesses affect matching. A structural match is '
            'candidate evidence only until decoded geometry/topology and retail ownership are independently closed.'
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(rep, indent=2) + '\n')
    print('TARGET', target['tgxm_file_identifier'], 'meshes', target['mesh_count'])
    print('SCAN_PACKAGES', ','.join(rep['scan_package_ids']), 'MODELS', scanned_models, 'MESH_COUNT_CANDIDATES', mesh_count_candidates)
    print('RESOLVED', len(candidates), 'EXACT_STRUCTURAL', len(exact), 'ERRORS', len(errors))
    for x in top[:10]:
        print('TOP', x['package_id'], x['tag_hash'], 'score', x['comparison']['score'], 'exact', x['comparison']['topology_structure_exact'],
              'verts', [m['vertex_count'] for m in x['signature']['meshes']],
              'indices', [m['index_count'] for m in x['signature']['meshes']],
              'stageparts', [m['stage0_highest_part_count'] for m in x['signature']['meshes']])
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
