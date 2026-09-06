#!/usr/bin/env python3
"""Decode exact D1 map-light shading materials from a semantic light probe.

The semantic probe proves that LightData +0x80 resolves to canonical D1 SMaterial_ROI
(80801AD7) for every Tower light. This tool consumes only those proven references and
reuses the exact PS4 D1 material decoder. It preserves shader identities, material TFX,
texture/sampler bindings and constant-container references without assigning visual
light semantics.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import d1_tower_map_schema_validate_v5 as v5
from d1_material_decode import parse_material

MAT_CLASS = '80801AD7'
NULLS = {'00000000', 'FFFFFFFF'}


def norm(x: object) -> str:
    return str(x).upper().removeprefix('0X').zfill(8)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--snapshot', type=Path, action='append', required=True)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('--semantic-probe', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()

    sem = json.loads(a.semantic_probe.read_text())
    if sem.get('status') != 'D1_WORLD_MAP_LIGHT_SEMANTIC_PROBE_COMPLETE':
        raise SystemExit(f'incomplete semantic probe: {sem.get("status")}')

    usage = Counter()
    for r in sem.get('light_instances', []):
        m = r.get('candidate_ref80') or {}
        h = norm(m.get('hash', 'FFFFFFFF'))
        if not m.get('exists') or norm(m.get('reference', 'FFFFFFFF')) != MAT_CLASS:
            raise SystemExit(f'light material proof violation: {m}')
        usage[h] += 1

    c = v5.v3.base.Corpus([p.resolve() for p in a.snapshot], a.runtime.resolve())
    materials = {}
    errors = []
    psfreq = Counter()
    vsfreq = Counter()
    ps_materials: dict[str, list[str]] = {}
    vs_materials: dict[str, list[str]] = {}
    constrefs = Counter()

    for mh in sorted(usage):
        meta = c.entry_meta(mh)
        b, src = c.payload(mh)
        row = {
            'material': mh,
            'light_instance_count': usage[mh],
            'meta': meta,
            'source': src,
        }
        if meta is None or norm(meta.get('reference', '')) != MAT_CLASS or b is None:
            row['error'] = 'material unavailable/non-80801AD7'
            errors.append(mh)
            materials[mh] = row
            continue
        try:
            p = parse_material(b, 'PS4')
            ps = norm(p['pixel_shader'])
            vs = norm(p['vertex_shader'])
            psfreq[ps] += usage[mh]
            vsfreq[vs] += usage[mh]
            ps_materials.setdefault(ps, []).append(mh)
            vs_materials.setdefault(vs, []).append(mh)
            vs_items = list(p['vs_textures']['items'])
            ps_items = list(p['ps_textures']['items'])
            vsc = norm(p['vs_vector4_container'])
            psc = norm(p['ps_vector4_container'])
            for h in (vsc, psc):
                if h not in NULLS:
                    constrefs[h] += 1
            row.update({
                'declared_file_size': p['declared_file_size'],
                'actual_file_size': p['actual_file_size'],
                'unk08': p['unk08'],
                'unk0c': p['unk0c'],
                'unk10': p['unk10'],
                'vertex_shader': vs,
                'pixel_shader': ps,
                'vs_texture_count': p['vs_textures']['count'],
                'ps_texture_count': p['ps_textures']['count'],
                'vs_texture_tags': vs_items,
                'ps_texture_tags': ps_items,
                'bindings': [
                    {'stage': stage, 'texture_index': int(x['texture_index']), 'texture': norm(x['texture'])}
                    for stage, items in [('vs', vs_items), ('ps', ps_items)] for x in items
                ],
                'constants': {
                    'vs_vector4_container': vsc,
                    'ps_vector4_container': psc,
                },
                'samplers': {'vs': p['vs_samplers'], 'ps': p['ps_samplers']},
                'tfx': {'vs': p['vs_tfx_bytecode'], 'ps': p['ps_tfx_bytecode']},
                'parsed_material_schema': 'd1_material_decode.parse_material/PS4',
            })
        except Exception as ex:
            row['error'] = repr(ex)
            errors.append(mh)
        materials[mh] = row

    out = {
        'schema_version': 1,
        'status': 'D1_WORLD_LIGHT_MATERIAL_MANIFEST_COMPLETE' if not errors else 'D1_WORLD_LIGHT_MATERIAL_MANIFEST_PARTIAL',
        'light_instance_count': sum(usage.values()),
        'unique_light_material_count': len(usage),
        'material_decode_errors': len(errors),
        'error_materials': errors,
        'pixel_shader_count': len(psfreq),
        'vertex_shader_count': len(vsfreq),
        'pixel_shader_frequency': dict(psfreq.most_common()),
        'vertex_shader_frequency': dict(vsfreq.most_common()),
        'pixel_shader_materials': {k: sorted(v) for k, v in sorted(ps_materials.items())},
        'vertex_shader_materials': {k: sorted(v) for k, v in sorted(vs_materials.items())},
        'unique_constant_container_count': len(constrefs),
        'constant_container_reference_counts': dict(constrefs),
        'material_instance_frequency': dict(usage.most_common()),
        'materials': materials,
        'proof': 'Every selected LightData +0x80 entry resolved to canonical D1 SMaterial_ROI 80801AD7 in the upstream semantic probe.',
        'policy': 'Exact source-proven D1 light materials only. No light type, colour, intensity, range, cone, shadow or appearance inference.',
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({
        k: out[k] for k in (
            'status','light_instance_count','unique_light_material_count','material_decode_errors',
            'pixel_shader_count','vertex_shader_count','unique_constant_container_count')
    }, indent=2))
    print('TOP_PIXEL_SHADERS', json.dumps(list(out['pixel_shader_frequency'].items())[:30]))
    return 0 if not errors else 2


if __name__ == '__main__':
    raise SystemExit(main())
