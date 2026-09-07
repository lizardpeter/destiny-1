#!/usr/bin/env python3
"""Resolve exact D1 PS4 ROI material-local shader state for both VS and PS stages.

This tool is deliberately semantic-conservative.  It combines already source-closed
D1 structures into one fail-closed report:

* canonical PS4 ROI material parsing (`80801AD7`);
* exact VS/PS texture tag arrays;
* exact VS/PS TFX bytecode, private Vec4 constants and CBuffer Vec4 arrays;
* optional external Vector4Container headers/payloads and byte comparison to inline
  CBuffers;
* exact inline sampler records plus their referenced PS4 `80801A42` native Gnm S#
  descriptors;
* TFX opcode framing/disassembly using the pinned Tiger opcode schema.

The report does not infer albedo/normal/PBR roles, does not assign meanings to arbitrary
constant vectors, and does not globally name the four Material +0x20 state bytes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import d1_tower_map_schema_validate_v5 as v5
from d1_material_decode import parse_material
from d1_ps4_sampler_probe import SAMPLER_CLASS, decode_blob as decode_sampler
from d1_tfx_program_inventory import disassemble as disassemble_tfx
from d1_world_material_constant_export import export_container

MAT_CLASS = '80801AD7'
NULLS = {'00000000', 'FFFFFFFF'}


def norm(x: object) -> str:
    return str(x).upper().removeprefix('0X').zfill(8)


def hbytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def inline_vec_u32_hex(rec: dict) -> list[str]:
    raw = bytes.fromhex(rec['raw_hex'])
    return [f'{x:08X}' for x in struct.unpack('<4I', raw)]


def external_u32_rows(ext: dict | None) -> list[list[str]] | None:
    if not ext or ext.get('error'):
        return None
    return [list(v['u32_hex']) for v in ext.get('vectors', [])]


def inline_u32_rows(arr: dict) -> list[list[str]]:
    return [inline_vec_u32_hex(x) for x in arr.get('items', [])]


def resolve_sampler(c, tag: str) -> dict:
    h = norm(tag)
    meta = c.entry_meta(h)
    b, src = c.payload(h)
    row = {'sampler': h, 'meta': meta, 'source': src}
    if meta is None:
        row['error'] = 'sampler metadata unavailable'
        return row
    row['class_hash'] = norm(meta.get('reference', 'FFFFFFFF'))
    if row['class_hash'] != SAMPLER_CLASS:
        row['error'] = f'unexpected sampler class {row["class_hash"]}; expected {SAMPLER_CLASS}'
        return row
    if b is None:
        row['error'] = 'sampler payload unavailable'
        return row
    row['payload_bytes'] = len(b)
    row['payload_sha256'] = hbytes(b)
    row['raw_hex'] = b.hex()
    try:
        row['decoded'] = decode_sampler(b)
    except Exception as ex:
        row['error'] = f'native sampler decode failed: {ex!r}'
    return row


def stage_row(c, p: dict, stage: str) -> dict:
    assert stage in ('vs', 'ps')
    tfx = p[f'{stage}_tfx_bytecode']
    tfx_constants = p[f'{stage}_tfx_bytecode_constants']
    cbuffers = p[f'{stage}_cbuffers']
    samplers = p[f'{stage}_samplers']
    textures = p[f'{stage}_textures']
    container_hash = norm(p[f'{stage}_vector4_container'])

    ext = export_container(c, container_hash) if container_hash not in NULLS else None
    ext_rows = external_u32_rows(ext)
    inline_rows = inline_u32_rows(cbuffers)
    if ext is None:
        relation = 'inline_cbuffers_only'
        identical = None
    elif ext.get('error'):
        relation = 'external_container_unresolved'
        identical = None
    else:
        identical = (inline_rows == ext_rows)
        relation = 'inline_cbuffers_plus_external_identical' if identical else 'inline_cbuffers_plus_external_different'

    raw_tfx = bytes.fromhex(tfx.get('bytes_hex', ''))
    b1 = [x.get('value') for x in tfx_constants.get('items', [])]
    b2 = [x.get('value') for x in cbuffers.get('items', [])]
    tfx_dis = disassemble_tfx(raw_tfx, b1, b2)

    sampler_refs = []
    for rec in samplers.get('items', []):
        h = norm(rec.get('first_dword_hex', 'FFFFFFFF'))
        sampler_refs.append({
            'inline_index': int(rec['index']),
            'inline_offset': int(rec['offset']),
            'inline_raw_hex': rec['raw_hex'],
            'inline_dwords_hex': rec['dwords_hex'],
            'sampler_taghash': h,
            'native_sampler': None if h in NULLS else resolve_sampler(c, h),
        })

    return {
        'shader': norm(p['vertex_shader'] if stage == 'vs' else p['pixel_shader']),
        'textures': textures,
        'tfx_bytecode': tfx,
        'tfx_program_sha256': hbytes(raw_tfx),
        'tfx_disassembly': tfx_dis,
        'tfx_private_constants': tfx_constants,
        'cbuffers': cbuffers,
        'external_vector4_container': container_hash,
        'external_vector4_container_data': ext,
        'cbuffers_external_u32_identical': identical,
        'vector_storage_relation': relation,
        'samplers': samplers,
        'sampler_references': sampler_refs,
    }


def resolve_material(c, h: str) -> dict:
    mh = norm(h)
    meta = c.entry_meta(mh)
    b, src = c.payload(mh)
    row = {'material': mh, 'meta': meta, 'source': src}
    if meta is None:
        row['error'] = 'material metadata unavailable'
        return row
    if norm(meta.get('reference', '')) != MAT_CLASS:
        row['error'] = f'unexpected material class {norm(meta.get("reference", ""))}; expected {MAT_CLASS}'
        return row
    if b is None:
        row['error'] = 'material payload unavailable'
        return row
    try:
        p = parse_material(b, 'PS4')
    except Exception as ex:
        row['error'] = f'parse_material failed: {ex!r}'
        return row

    state = list(p['material_state4_u8'])
    row.update({
        'payload_bytes': len(b),
        'payload_sha256': hbytes(b),
        'declared_file_size': p['declared_file_size'],
        'material_state4_hex': p['material_state4_hex'],
        'material_state4_u8': state,
        'material_state4_selector_syntax': [
            {'lane': i, 'raw': v, 'high_bit': bool(v & 0x80), 'low7': v & 0x7F}
            for i, v in enumerate(state)
        ],
        'unk08': p['unk08'], 'unk0c': p['unk0c'], 'unk10': p['unk10'],
        'vs': stage_row(c, p, 'vs'),
        'ps': stage_row(c, p, 'ps'),
    })
    return row


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--snapshot', type=Path, action='append', required=True)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('--material', action='append', required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()

    c = v5.v3.base.Corpus([p.resolve() for p in a.snapshot], a.runtime.resolve())
    selected = sorted({norm(x) for x in a.material})
    materials = {h: resolve_material(c, h) for h in selected}

    violations = []
    tfx_programs = defaultdict(list)
    shader_materials = {'vs': defaultdict(list), 'ps': defaultdict(list)}
    sampler_tags = set()
    container_tags = set()
    relation_counts = Counter()
    state4_counts = Counter()
    total_tfx_ops = Counter()
    total_externs = Counter()

    for h, r in materials.items():
        if r.get('error'):
            violations.append(f'{h}:{r["error"]}')
            continue
        state4_counts[r['material_state4_hex']] += 1
        for stage in ('vs', 'ps'):
            s = r[stage]
            shader_materials[stage][s['shader']].append(h)
            relation_counts[f'{stage}:{s["vector_storage_relation"]}'] += 1
            tfx_programs[f'{stage}:{s["tfx_program_sha256"]}'].append(h)
            if not s['tfx_disassembly'].get('complete'):
                violations.append(f'{h}:{stage}:TFX disassembly incomplete')
            for op in s['tfx_disassembly'].get('ops', []):
                total_tfx_ops[op['name']] += 1
                if 'extern_name' in op:
                    total_externs[op['extern_name']] += 1
            ch = s['external_vector4_container']
            if ch not in NULLS:
                container_tags.add(ch)
                if s['external_vector4_container_data'].get('error'):
                    violations.append(f'{h}:{stage}:external:{s["external_vector4_container_data"]["error"]}')
            for sr in s['sampler_references']:
                sh = sr['sampler_taghash']
                if sh in NULLS:
                    continue
                sampler_tags.add(sh)
                n = sr['native_sampler']
                if not n or n.get('error'):
                    violations.append(f'{h}:{stage}:sampler:{sh}:{None if not n else n.get("error")}')

    out = {
        'schema_version': 1,
        'status': 'D1_MATERIAL_STAGE_STATE_EXACT' if not violations else 'D1_MATERIAL_STAGE_STATE_PARTIAL',
        'selected_material_count': len(selected),
        'resolved_material_count': sum(1 for r in materials.values() if not r.get('error')),
        'unique_vertex_shader_count': len(shader_materials['vs']),
        'unique_pixel_shader_count': len(shader_materials['ps']),
        'unique_tfx_program_count_by_stage_sha': len(tfx_programs),
        'unique_external_vector4_container_count': len(container_tags),
        'unique_native_sampler_count': len(sampler_tags),
        'vector_storage_relation_counts': dict(relation_counts),
        'material_state4_histogram': dict(state4_counts),
        'tfx_opcode_histogram': dict(total_tfx_ops),
        'tfx_extern_histogram': dict(total_externs),
        'shader_materials': {
            stage: {k: sorted(v) for k, v in sorted(d.items())}
            for stage, d in shader_materials.items()
        },
        'tfx_program_groups': {k: sorted(v) for k, v in sorted(tfx_programs.items())},
        'external_vector4_containers': sorted(container_tags),
        'native_sampler_tags': sorted(sampler_tags),
        'violations': violations,
        'materials': materials,
        'policy': (
            'Exact source material state only. TFX opcode identities/framing use the pinned Tiger schema; '
            'constant values, arbitrary Material +0x20 state lanes and texture roles remain semantically unnamed '
            'unless independently promoted elsewhere. Native sampler S# descriptors retain raw words.'
        ),
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({k: out[k] for k in (
        'status','selected_material_count','resolved_material_count','unique_vertex_shader_count',
        'unique_pixel_shader_count','unique_tfx_program_count_by_stage_sha',
        'unique_external_vector4_container_count','unique_native_sampler_count',
        'vector_storage_relation_counts','material_state4_histogram','tfx_opcode_histogram',
        'tfx_extern_histogram','violations')}, indent=2))
    return 0 if not violations else 2


if __name__ == '__main__':
    raise SystemExit(main())
