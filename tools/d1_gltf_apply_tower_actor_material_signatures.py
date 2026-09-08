#!/usr/bin/env python3
"""Apply closed Tower actor visible-material signatures to exact skinned GLBs.

This adapter does not touch geometry, skinning, joint matrices, accessors, bufferViews,
binary payloads, or animation data. It changes only primitive Material indices for
source-visible ranges whose variant_shader_index is nonnegative, and appends bare
D1_<MaterialHash> glTF Material records when a selected retail material was not
already present in the base GLB.

Range identity comes from the green articulated model export. Signature identity comes
from D1_TOWER_ACTOR_VISIBLE_MATERIAL_SIGNATURES_COMPLETE. Multiple exact signatures
are emitted as distinct GLBs rather than collapsed.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import struct
from pathlib import Path

MAT_RE = re.compile(r'^D1_([0-9A-Fa-f]{8})$')


def norm(x: object) -> str:
    return str(x).upper().removeprefix('0X').zfill(8)


def read_glb(path: Path):
    b = path.read_bytes()
    if len(b) < 12:
        raise ValueError(f'{path}: short GLB')
    magic, ver, total = struct.unpack_from('<4sII', b, 0)
    if magic != b'glTF' or ver != 2 or total != len(b):
        raise ValueError(f'{path}: invalid GLB header')
    chunks = []
    o = 12
    while o < len(b):
        if o + 8 > len(b):
            raise ValueError(f'{path}: short chunk header')
        n, typ = struct.unpack_from('<I4s', b, o); o += 8
        if o + n > len(b):
            raise ValueError(f'{path}: chunk OOB')
        chunks.append((typ, b[o:o+n])); o += n
    if not chunks or chunks[0][0] != b'JSON':
        raise ValueError(f'{path}: JSON chunk missing')
    doc = json.loads(chunks[0][1].decode('utf-8').rstrip('\x00 '))
    return doc, chunks


def write_glb(path: Path, doc: dict, chunks: list[tuple[bytes, bytes]]):
    raw = json.dumps(doc, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
    raw += b' ' * ((4 - len(raw) % 4) % 4)
    rebuilt = [(b'JSON', raw)] + chunks[1:]
    total = 12 + sum(8 + len(data) for _, data in rebuilt)
    out = bytearray(struct.pack('<4sII', b'glTF', 2, total))
    for typ, data in rebuilt:
        out += struct.pack('<I4s', len(data), typ)
        out += data
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(out)


def structural_fingerprint(doc: dict) -> dict:
    return {
        'scene': doc.get('scene'),
        'scenes': doc.get('scenes'),
        'nodes': doc.get('nodes'),
        'skins': doc.get('skins'),
        'accessors': doc.get('accessors'),
        'bufferViews': doc.get('bufferViews'),
        'buffers': doc.get('buffers'),
        'animations': doc.get('animations'),
        'mesh_names': [m.get('name') for m in doc.get('meshes', [])],
        'mesh_primitive_attributes': [
            [copy.deepcopy(p.get('attributes')) for p in m.get('primitives', [])]
            for m in doc.get('meshes', [])
        ],
        'mesh_primitive_indices': [
            [p.get('indices') for p in m.get('primitives', [])]
            for m in doc.get('meshes', [])
        ],
        'mesh_primitive_modes': [
            [p.get('mode') for p in m.get('primitives', [])]
            for m in doc.get('meshes', [])
        ],
    }


def material_hashes(doc: dict) -> dict[str, int]:
    out = {}
    for i, m in enumerate(doc.get('materials', [])):
        mm = MAT_RE.match(str(m.get('name') or ''))
        if mm:
            h = norm(mm.group(1))
            if h in out:
                raise ValueError(f'duplicate D1 material hash in GLB: {h}')
            out[h] = i
    return out


def ensure_material(doc: dict, h: str) -> tuple[int, bool]:
    h = norm(h)
    by = material_hashes(doc)
    if h in by:
        return by[h], False
    mats = doc.setdefault('materials', [])
    mats.append({'name': f'D1_{h}'})
    return len(mats) - 1, True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--signatures', type=Path, required=True)
    ap.add_argument('--model-export', type=Path, required=True)
    ap.add_argument('--input-dir', type=Path, required=True)
    ap.add_argument('--input-suffix', default='_SKINNED_NATIVE_D1.glb')
    ap.add_argument('--out-dir', type=Path, required=True)
    ap.add_argument('--report', type=Path, required=True)
    a = ap.parse_args()

    sig = json.loads(a.signatures.read_text())
    exp = json.loads(a.model_export.read_text())
    violations = []
    if sig.get('status') != 'D1_TOWER_ACTOR_VISIBLE_MATERIAL_SIGNATURES_COMPLETE' or sig.get('violations'):
        violations.append('signature_report_not_green')
    if exp.get('status') != 'D1_WORLD_ARTICULATED_MODEL_SET_COMPLETE' or exp.get('errors'):
        violations.append('model_export_not_green')

    exp_by = {norm(x['model']): x for x in exp.get('models', [])}
    sig_by = {norm(x['model']): x for x in sig.get('models', [])}
    if set(exp_by) != set(sig_by):
        violations.append('model_set_mismatch')

    outputs = []
    for model in sorted(sig_by):
        base = a.input_dir / f'{model}{a.input_suffix}'
        if not base.is_file():
            violations.append(f'{model}:base_glb_missing:{base}')
            continue
        try:
            base_doc, chunks = read_glb(base)
            base_fp = structural_fingerprint(base_doc)
            nonjson_sha = hashlib.sha256(b''.join(typ + data for typ, data in chunks[1:])).hexdigest()
            range_by_name = {str(x['name']): x for x in exp_by[model].get('ranges', [])}
            mesh_names = [str(m.get('name') or '') for m in base_doc.get('meshes', [])]
            missing_ranges = sorted(set(mesh_names) - set(range_by_name))
            if missing_ranges:
                raise ValueError(f'{len(missing_ranges)} GLB meshes absent from model range report: {missing_ranges[:3]}')

            for s in sig_by[model].get('signatures', []):
                si = int(s['signature_index'])
                mapping = {
                    int(x['variant_shader_index']): norm(x['material_tag_hash'])
                    for x in s.get('visible_external_materials', [])
                }
                doc = copy.deepcopy(base_doc)
                added = 0
                changed = 0
                used_vis = set()
                assignments = []
                for mi, mesh in enumerate(doc.get('meshes', [])):
                    name = str(mesh.get('name') or '')
                    rr = range_by_name[name]
                    vis = sorted({int(x.get('variant_shader_index', -1)) for x in rr.get('parts', []) if int(x.get('variant_shader_index', -1)) >= 0})
                    if not vis:
                        continue
                    wanted = []
                    for vi in vis:
                        if vi not in mapping:
                            raise ValueError(f'signature {si} range {name}: visible variant {vi} missing from signature')
                        wanted.append(mapping[vi]); used_vis.add(vi)
                    if len(set(wanted)) != 1:
                        raise ValueError(f'signature {si} range {name}: conflicting signature materials {sorted(set(wanted))}')
                    h = wanted[0]
                    mat_index, was_added = ensure_material(doc, h)
                    added += int(was_added)
                    for pi, prim in enumerate(mesh.get('primitives', [])):
                        old = prim.get('material')
                        prim['material'] = mat_index
                        changed += int(old != mat_index)
                        assignments.append({
                            'mesh_index': mi, 'mesh_name': name, 'primitive_index': pi,
                            'variant_shader_indices': vis, 'material_tag_hash': h,
                            'old_material_index': old, 'new_material_index': mat_index,
                        })
                if used_vis != set(mapping):
                    raise ValueError(f'signature {si}: unused/missing visible variants expected={sorted(mapping)} used={sorted(used_vis)}')
                if structural_fingerprint(doc) != base_fp:
                    raise ValueError(f'signature {si}: non-material GLTF structure mutated')
                out_path = a.out_dir / f'{model}_SIG{si:02d}_SKINNED_NATIVE_D1.glb'
                write_glb(out_path, doc, chunks)
                check_doc, check_chunks = read_glb(out_path)
                check_nonjson_sha = hashlib.sha256(b''.join(typ + data for typ, data in check_chunks[1:])).hexdigest()
                if check_nonjson_sha != nonjson_sha:
                    raise ValueError(f'signature {si}: non-JSON GLB chunks changed')
                if structural_fingerprint(check_doc) != base_fp:
                    raise ValueError(f'signature {si}: roundtrip non-material structure changed')
                outputs.append({
                    'model': model,
                    'signature_index': si,
                    'source_glb': str(base),
                    'output_glb': str(out_path),
                    'output_sha256': hashlib.sha256(out_path.read_bytes()).hexdigest(),
                    'output_bytes': out_path.stat().st_size,
                    'visible_external_materials': [
                        {'variant_shader_index': vi, 'material_tag_hash': mapping[vi]}
                        for vi in sorted(mapping)
                    ],
                    'visible_variant_count': len(mapping),
                    'changed_primitive_material_assignment_count': changed,
                    'added_material_record_count': added,
                    'primitive_assignments': assignments,
                    'non_json_glb_chunks_sha256': nonjson_sha,
                    'skin_count': len(check_doc.get('skins', [])),
                    'animation_count_preserved': len(check_doc.get('animations', [])),
                    'mesh_count': len(check_doc.get('meshes', [])),
                    'node_count': len(check_doc.get('nodes', [])),
                    'accessor_count': len(check_doc.get('accessors', [])),
                })
        except Exception as ex:
            violations.append(f'{model}:{ex!r}')

    expected = int(sig.get('total_unique_visible_external_signature_count', -1))
    if len(outputs) != expected:
        violations.append(f'expected_{expected}_variant_outputs_got_{len(outputs)}')
    per_model = {}
    for x in outputs:
        per_model.setdefault(x['model'], 0); per_model[x['model']] += 1
    for model, row in sig_by.items():
        n = int(row.get('unique_visible_external_signature_count') or 0)
        if per_model.get(model, 0) != n:
            violations.append(f'{model}:expected_{n}_outputs_got_{per_model.get(model,0)}')

    out = {
        'schema_version': 1,
        'status': 'D1_TOWER_ACTOR_MATERIAL_SIGNATURE_GLB_VARIANTS_COMPLETE' if not violations else 'D1_TOWER_ACTOR_MATERIAL_SIGNATURE_GLB_VARIANTS_VIOLATIONS',
        'actor_model_count': len(sig_by),
        'expected_variant_count': expected,
        'output_variant_count': len(outputs),
        'per_model_output_counts': dict(sorted(per_model.items())),
        'outputs': outputs,
        'violations': violations,
        'proof': {
            'input_signatures_green': sig.get('status') == 'D1_TOWER_ACTOR_VISIBLE_MATERIAL_SIGNATURES_COMPLETE',
            'geometry_skin_accessors_buffer_views_nodes_preserved': not violations,
            'non_json_glb_chunks_preserved_byte_exact': not violations,
            'only_visible_external_primitive_material_indices_changed': not violations,
            'runtime_active_variant_selected': False,
            'runtime_actor_animation_state_selected': False,
            'D1_retail_descriptor_evaluator_source_closed': False,
        },
        'policy': (
            'Each closed visible material signature becomes a separate portable actor GLB. The adapter changes only '
            'material records/primitive material indices for source-visible external-selector ranges. Geometry, topology, '
            'skin, joints, weights, binary buffers and animations are unchanged. Multi-signature families remain distinct; '
            'no runtime-active variant or action is selected.'
        ),
    }
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({
        'status': out['status'],
        'actor_model_count': out['actor_model_count'],
        'expected_variant_count': expected,
        'output_variant_count': len(outputs),
        'per_model_output_counts': out['per_model_output_counts'],
        'violations': violations,
    }, indent=2))
    return 0 if not violations else 2


if __name__ == '__main__':
    raise SystemExit(main())
