#!/usr/bin/env python3
"""Reduce exact Xur native shader + material-local state into a fail-closed semantic-lifting frontier.

This tool does not infer albedo/normal/PBR roles and does not claim retail-equivalent
shader semantics. It combines two already exact checkpoints:

* Xur native shader census: exact bounded PS4 GCN programs and exact PS image-resource usage.
* Xur material-local state: exact VS/PS TFX framing, local constants/CBuffer layouts,
  native sampler descriptors and preserved material state fields.

It parameterizes away literal texture TagHashes and literal constant values to identify
*structural lifting units*: the same native GCN program under the same TFX/state/layout
shape. Such grouping is a work-reduction device only; grouped materials can still render
differently because their literal textures/constants differ.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

STATE_STATUS = 'D1_MATERIAL_STAGE_STATE_EXACT'
SHADER_STATUS = 'D1_XUR_ALL_NATIVE_SHADER_DISASSEMBLY_EXACT'
IMAGE_STATUS = 'D1_GCN_IMAGE_RESOURCE_USAGE_EXACT'
OUT_STATUS = 'D1_XUR_SHADER_SEMANTIC_LIFTING_FRONTIER_EXACT'


def canonical(obj: object) -> str:
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=True)


def sha_obj(obj: object) -> str:
    return hashlib.sha256(canonical(obj).encode('utf-8')).hexdigest()


def sampler_payload_sequence(stage: dict) -> list[str | None]:
    out = []
    for row in stage.get('sampler_references', []):
        native = row.get('native_sampler')
        if row.get('sampler_taghash') in ('00000000', 'FFFFFFFF'):
            out.append(None)
            continue
        if not native or native.get('error'):
            raise ValueError(f'unresolved native sampler: {row!r}')
        digest = native.get('payload_sha256')
        if not digest:
            raise ValueError(f'native sampler missing payload sha256: {row!r}')
        out.append(digest)
    return out


def stage_key(material: dict, stage_name: str, shader_by_tag: dict[str, dict]) -> dict:
    stage = material[stage_name]
    tag = stage['shader']
    shader = shader_by_tag.get(tag)
    if shader is None:
        raise ValueError(f'{material["material"]}:{stage_name}: shader {tag} absent from exact shader census')
    if stage.get('tfx_disassembly', {}).get('complete') is not True:
        raise ValueError(f'{material["material"]}:{stage_name}: TFX not fully framed')
    return {
        'stage': stage_name,
        'gcn_sha256': shader['gcn_sha256'],
        'tfx_program_sha256': stage['tfx_program_sha256'],
        'tfx_private_constant_count': int(stage['tfx_private_constants']['count']),
        'cbuffer_vec4_count': int(stage['cbuffers']['count']),
        'texture_slot_count': int(stage['textures']['count']),
        'native_sampler_payload_sha256_sequence': sampler_payload_sequence(stage),
        'vector_storage_relation': stage['vector_storage_relation'],
        'material_state4_hex': material['material_state4_hex'],
        'unk08': material['unk08'],
        'unk0c': material['unk0c'],
        'unk10': material['unk10'],
    }


def material_family_key(material: dict, shader_by_tag: dict[str, dict]) -> dict:
    return {
        'material_state4_hex': material['material_state4_hex'],
        'unk08': material['unk08'],
        'unk0c': material['unk0c'],
        'unk10': material['unk10'],
        'vs': stage_key(material, 'vs', shader_by_tag),
        'ps': stage_key(material, 'ps', shader_by_tag),
    }


def histogram(groups: dict[str, list[str]]) -> dict[str, int]:
    return {str(k): v for k, v in sorted(Counter(map(len, groups.values())).items())}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--material-state', type=Path, required=True)
    ap.add_argument('--shader-census', type=Path, required=True)
    ap.add_argument('--image-usage', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()

    state = json.loads(args.material_state.read_text())
    census = json.loads(args.shader_census.read_text())
    images = json.loads(args.image_usage.read_text())

    violations: list[str] = []
    if state.get('status') != STATE_STATUS:
        violations.append(f'material-state status {state.get("status")!r} != {STATE_STATUS!r}')
    if state.get('violations'):
        violations.append(f'material-state has violations: {state.get("violations")!r}')
    if census.get('status') != SHADER_STATUS:
        violations.append(f'shader-census status {census.get("status")!r} != {SHADER_STATUS!r}')
    if images.get('status') != IMAGE_STATUS:
        violations.append(f'image-usage status {images.get("status")!r} != {IMAGE_STATUS!r}')
    if images.get('unmatched_image_instruction_count') != 0:
        violations.append('image-usage has unmatched image instructions')
    if images.get('missing_disassembly_shaders'):
        violations.append('image-usage has missing PS disassemblies')

    materials = state.get('materials') or {}
    shader_rows = census.get('shaders') or []
    shader_by_tag = {r['shader']: r for r in shader_rows}
    image_by_tag = {r['shader']: r for r in (images.get('shaders') or [])}

    if len(materials) != 54:
        violations.append(f'expected 54 materials, got {len(materials)}')
    if len(shader_by_tag) != 36:
        violations.append(f'expected 36 shader headers, got {len(shader_by_tag)}')
    if census.get('unique_bounded_gcn_program_count') != 31:
        violations.append(f'expected 31 bounded GCN programs, got {census.get("unique_bounded_gcn_program_count")}')
    if images.get('shader_count') != 25:
        violations.append(f'expected 25 PS image-usage rows, got {images.get("shader_count")}')
    if images.get('image_instruction_count') != 116:
        violations.append(f'expected 116 exact PS image instructions, got {images.get("image_instruction_count")}')

    expected_tags = set(state.get('shader_materials', {}).get('vs', {})) | set(state.get('shader_materials', {}).get('ps', {}))
    census_tags = set(shader_by_tag)
    if expected_tags != census_tags:
        violations.append(f'shader header set mismatch: state-only={sorted(expected_tags-census_tags)}, census-only={sorted(census_tags-expected_tags)}')
    expected_ps = set(state.get('shader_materials', {}).get('ps', {}))
    if expected_ps != set(image_by_tag):
        violations.append(f'PS image-usage set mismatch: state-only={sorted(expected_ps-set(image_by_tag))}, image-only={sorted(set(image_by_tag)-expected_ps)}')

    if violations:
        out = {'schema_version': 1, 'status': 'D1_XUR_SHADER_SEMANTIC_LIFTING_FRONTIER_PARTIAL', 'violations': violations}
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(out, indent=2) + '\n')
        print(json.dumps(out, indent=2))
        return 2

    stage_groups: dict[str, dict[str, list[str]]] = {'vs': defaultdict(list), 'ps': defaultdict(list)}
    stage_keys: dict[str, dict] = {}
    material_groups: dict[str, list[str]] = defaultdict(list)
    material_keys: dict[str, dict] = {}

    try:
        for mh, material in sorted(materials.items()):
            for stage_name in ('vs', 'ps'):
                key = stage_key(material, stage_name, shader_by_tag)
                sig = sha_obj(key)
                stage_groups[stage_name][sig].append(mh)
                stage_keys[sig] = key
            mkey = material_family_key(material, shader_by_tag)
            msig = sha_obj(mkey)
            material_groups[msig].append(mh)
            material_keys[msig] = mkey
    except ValueError as exc:
        out = {'schema_version': 1, 'status': 'D1_XUR_SHADER_SEMANTIC_LIFTING_FRONTIER_PARTIAL', 'violations': [str(exc)]}
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(out, indent=2) + '\n')
        print(json.dumps(out, indent=2))
        return 2

    stage_units = []
    for stage_name in ('vs', 'ps'):
        for sig, members in sorted(stage_groups[stage_name].items()):
            first = materials[members[0]]
            key = stage_keys[sig]
            gcn = key['gcn_sha256']
            headers = sorted({materials[m][stage_name]['shader'] for m in members})
            native_rows = [shader_by_tag[h] for h in headers]
            if {r['gcn_sha256'] for r in native_rows} != {gcn}:
                raise AssertionError('stage unit mixed GCN payloads')
            image_count = 0
            used_texture_indices = []
            if stage_name == 'ps':
                image_rows = [image_by_tag[h] for h in headers]
                image_count = max(r['image_instruction_count'] for r in image_rows)
                used_texture_indices = sorted({i for r in image_rows for i in r['used_texture_indices']})
            stage_units.append({
                'unit_id': f'{stage_name.upper()}U-{sig[:16]}',
                'signature_sha256': sig,
                'stage': stage_name,
                'material_count': len(members),
                'materials': sorted(members),
                'shader_headers': headers,
                'gcn_sha256': gcn,
                'gcn_bytes': native_rows[0]['gcn_bytes'],
                'instruction_count_approx': native_rows[0]['instruction_count_approx'],
                'image_instruction_count': image_count,
                'used_texture_indices': used_texture_indices,
                'structural_key': key,
                'literal_parameters_withheld_from_group_key': ['texture TagHashes', 'TFX private constant values', 'CBuffer Vec4 values'],
                'semantic_lifting_complete': False,
            })

    material_families = []
    for sig, members in sorted(material_groups.items()):
        first = materials[members[0]]
        psrow = shader_by_tag[first['ps']['shader']]
        vsrow = shader_by_tag[first['vs']['shader']]
        ps_image = image_by_tag[first['ps']['shader']]
        material_families.append({
            'family_id': f'MFU-{sig[:16]}',
            'signature_sha256': sig,
            'material_count': len(members),
            'materials': sorted(members),
            'vs_shader_headers': sorted({materials[m]['vs']['shader'] for m in members}),
            'ps_shader_headers': sorted({materials[m]['ps']['shader'] for m in members}),
            'vs_gcn_sha256': vsrow['gcn_sha256'],
            'ps_gcn_sha256': psrow['gcn_sha256'],
            'ps_instruction_count_approx': psrow['instruction_count_approx'],
            'ps_image_instruction_count': ps_image['image_instruction_count'],
            'structural_key': material_keys[sig],
            'semantic_lifting_complete': False,
        })

    stage_units.sort(key=lambda r: (-r['material_count'], 0 if r['stage'] == 'ps' else 1, -r['instruction_count_approx'], r['signature_sha256']))
    material_families.sort(key=lambda r: (-r['material_count'], -r['ps_instruction_count_approx'], -r['ps_image_instruction_count'], r['signature_sha256']))

    gcn_materials: dict[str, set[str]] = defaultdict(set)
    gcn_stages: dict[str, set[str]] = defaultdict(set)
    gcn_headers: dict[str, set[str]] = defaultdict(set)
    for mh, material in materials.items():
        for stage_name in ('vs', 'ps'):
            h = material[stage_name]['shader']
            g = shader_by_tag[h]['gcn_sha256']
            gcn_materials[g].add(mh)
            gcn_stages[g].add(stage_name)
            gcn_headers[g].add(h)
    gcn_queue = []
    for g, members in gcn_materials.items():
        rows = [shader_by_tag[h] for h in gcn_headers[g]]
        gcn_queue.append({
            'gcn_sha256': g,
            'material_count': len(members),
            'materials': sorted(members),
            'stages': sorted(gcn_stages[g]),
            'shader_headers': sorted(gcn_headers[g]),
            'gcn_bytes': rows[0]['gcn_bytes'],
            'instruction_count_approx': rows[0]['instruction_count_approx'],
            'image_instruction_count_lexical_max': max(r.get('image_instruction_count_lexical', 0) for r in rows),
            'semantic_lifting_complete': False,
        })
    gcn_queue.sort(key=lambda r: (-r['material_count'], -r['instruction_count_approx'], -r['image_instruction_count_lexical_max'], r['gcn_sha256']))

    out = {
        'schema_version': 1,
        'status': OUT_STATUS,
        'inputs': {
            'material_state_status': state['status'],
            'shader_census_status': census['status'],
            'image_usage_status': images['status'],
        },
        'xur_identity': {'string_hash': '46C55854', 'entity_model': '80C88CEF'},
        'material_count': len(materials),
        'shader_header_count': len(shader_by_tag),
        'native_gcn_program_count': len(gcn_queue),
        'exact_ps_image_instruction_count': images['image_instruction_count'],
        'stage_structural_unit_count': len(stage_units),
        'vs_stage_structural_unit_count': sum(1 for x in stage_units if x['stage'] == 'vs'),
        'ps_stage_structural_unit_count': sum(1 for x in stage_units if x['stage'] == 'ps'),
        'material_structural_family_count': len(material_families),
        'stage_unit_member_count_histogram': {
            'vs': histogram(stage_groups['vs']),
            'ps': histogram(stage_groups['ps']),
        },
        'material_family_member_count_histogram': histogram(material_groups),
        'native_gcn_lifting_queue': gcn_queue,
        'stage_structural_lifting_queue': stage_units,
        'material_structural_families': material_families,
        'violations': [],
        'policy': (
            'Exact work-reduction frontier only. A structural unit means identical native GCN SHA, TFX SHA, '
            'state/layout counts, ordered native sampler descriptor payloads, vector-storage relation and preserved '
            'material state fields. Literal texture TagHashes and literal constant values are parameters, not grouping '
            'keys. No texture role, PBR meaning, arbitrary state-byte meaning, or retail-equivalent shader semantics '
            'is inferred by this report.'
        ),
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({k: out[k] for k in (
        'status', 'material_count', 'shader_header_count', 'native_gcn_program_count',
        'exact_ps_image_instruction_count', 'stage_structural_unit_count',
        'vs_stage_structural_unit_count', 'ps_stage_structural_unit_count',
        'material_structural_family_count', 'stage_unit_member_count_histogram',
        'material_family_member_count_histogram', 'violations')}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
