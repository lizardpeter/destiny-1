#!/usr/bin/env python3
"""Build an exact visual/material plan for the 57 source-owned Tower spawned actors.

The input is the universal spawned-EntitySK reclassification report.  This adapter
extracts each actor's exact EntityModel parent resource, embedded s_entity_model,
skeleton resource and runtime rig, then reopens every unique model through the
verified universal retail package catalog to enumerate the vertex/index header and
backing FileHash dependencies required for geometry export.

The generated ``candidates`` array intentionally uses the existing
D1_WORLD_ARTICULATED_ENTITY_PLAN_COMPLETE interface so the already source-validated
owning-parent material resolver and stage-0 model exporter can be reused without a
second material/geometry implementation.  ``runtime_placement_count`` is not emitted:
spawn locations are a separate D912 concern and are never synthesized here.

No actor location, material, LOD, identity name, or animation is inferred.  Model
ownership comes only from each SEntity's source-owned EntityResource; stream package
families come only from literal FileHash edges in the exact s_entity_model.
"""
from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from d1_entity_model_probe import parse_model
from d1_investment_arrangement_probe import filehash_pkg_index
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_activity_placements import RemoteCorpus
from d1_split_tar_extract import SplitHttpTar

ENTITY_MODEL = '80801AB5'
MODEL_PAIR = ('80801A80', '80801A9C')
SKELETON_PAIR = ('808006BD', '8080049A')
RIG_PAIR = ('808008B2', '8080099B')
NULLS = {'00000000', 'FFFFFFFF'}


def norm(x):
    return str(x).upper().removeprefix('0X').zfill(8)


def pkgid(h: str) -> str | None:
    h = norm(h)
    if h in NULLS:
        return None
    p, _ = filehash_pkg_index(int(h, 16))
    return f'{p:04x}'


def pair_of(rr: dict) -> tuple[str, str] | None:
    er = rr.get('entity_resource') or {}
    a = (er.get('unk10') or {}).get('class_hash')
    b = (er.get('unk18') or {}).get('class_hash')
    return None if not a or not b else (norm(a), norm(b))


def unique_resource(e: dict, pair: tuple[str, str]) -> dict:
    rows = [x for x in e.get('resources', []) if pair_of(x) == pair]
    if len(rows) != 1:
        raise ValueError(f"{e.get('entity')}: pair {pair} count {len(rows)} != 1")
    return rows[0]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--reclassify', type=Path, required=True)
    ap.add_argument('--member-catalog', type=Path, action='append', required=True)
    ap.add_argument('--base-url', required=True)
    ap.add_argument('--part-count', type=int, default=10)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('-o', '--output', type=Path, required=True)
    a = ap.parse_args()

    source = json.loads(a.reclassify.read_text())
    if source.get('status') != 'D1_TOWER_SPAWNED_ENTITY_UNIVERSAL_RECLASSIFY_COMPLETE':
        raise SystemExit(f'reclassification report is not complete: {source.get("status")}')
    if source.get('violations') or int(source.get('unresolved_dependency_count', -1)) != 0:
        raise SystemExit('reclassification report still has violations/unresolved dependencies')

    catalogs = load_catalogs(a.member_catalog)
    arc = SplitHttpTar([f"{a.base_url.rstrip('/')}/packages.tar.{i:03d}" for i in range(1, a.part_count + 1)], retries=6, timeout=90)
    c = RemoteCorpus(arc, catalogs, a.runtime)

    candidates = []
    family_members = collections.defaultdict(list)
    required_ids = set()
    model_dependency_rows = {}
    violations = []

    for h, e in sorted((source.get('entities') or {}).items()):
        h = norm(h)
        try:
            model_rr = unique_resource(e, MODEL_PAIR)
            sk_rr = unique_resource(e, SKELETON_PAIR)
            rig_rr = unique_resource(e, RIG_PAIR)
            er = model_rr.get('entity_resource') or {}
            model = norm(er.get('embedded_model_tag_hash', 'FFFFFFFF'))
            parent = norm(model_rr.get('resource_hash', 'FFFFFFFF'))
            skeleton = norm(sk_rr.get('resource_hash', 'FFFFFFFF'))
            rig = norm(rig_rr.get('resource_hash', 'FFFFFFFF'))
            if model in NULLS or parent in NULLS or skeleton in NULLS or rig in NULLS:
                raise ValueError('null model/parent/skeleton/rig')
            comp = e.get('composition') or {}
            cand = {
                'entity': h,
                'classification': comp.get('classification'),
                'models': [model],
                'model_parent_resources': [parent],
                'skeleton_resources': [skeleton],
                'runtime_rig_resources': [rig],
                'bone_counts': comp.get('bone_counts', []),
                'specific_name_hashes': comp.get('specific_name_hashes', []),
                'generic_name_hashes': comp.get('generic_name_hashes', []),
                'source_package_id': e.get('package_id'),
                'location_status': 'withheld_separate_D912_spawn_location_graph',
            }
            candidates.append(cand)
            family_members[(model, parent)].append(h)
            for x in (h, model, parent, skeleton, rig):
                p = pkgid(x)
                if p: required_ids.add(p)
        except Exception as ex:
            violations.append(f'{h}:{ex!r}')

    if len(candidates) != int(source.get('entity_count', -1)):
        violations.append(f'candidate_count_{len(candidates)}_not_source_{source.get("entity_count")}')

    # Enumerate exact geometry stream headers/backings for each unique model.
    for model in sorted({x['models'][0] for x in candidates}):
        row = {'model': model, 'streams': [], 'violations': []}
        try:
            mm = c.entry_meta(model)
            mb, msrc = c.payload(model)
            if mm is None or mb is None or norm(mm.get('reference', 'FFFFFFFF')) != ENTITY_MODEL:
                raise ValueError(f'model unavailable/wrong class {None if mm is None else mm.get("reference")}')
            parsed = parse_model(mb, 'PS4')
            row['source'] = msrc
            row['mesh_count'] = len(parsed.get('meshes', []))
            p = pkgid(model)
            if p: required_ids.add(p)
            for mi, mesh in enumerate(parsed.get('meshes', [])):
                for role in ('vertices1', 'vertices2', 'indices'):
                    hh = norm(mesh.get(role, 'FFFFFFFF'))
                    if hh in NULLS:
                        continue
                    hm = c.entry_meta(hh)
                    if hm is None:
                        raise ValueError(f'mesh {mi} {role} header {hh} unresolved')
                    backing = norm(hm.get('reference', 'FFFFFFFF'))
                    if backing in NULLS or c.entry_meta(backing) is None:
                        raise ValueError(f'mesh {mi} {role} backing {hh}->{backing} unresolved')
                    stream = {
                        'mesh_index': mi,
                        'role': role,
                        'header': hh,
                        'header_package_id': pkgid(hh),
                        'backing': backing,
                        'backing_package_id': pkgid(backing),
                    }
                    row['streams'].append(stream)
                    if stream['header_package_id']: required_ids.add(stream['header_package_id'])
                    if stream['backing_package_id']: required_ids.add(stream['backing_package_id'])
                # Inline materials are literal FileHash dependencies even though an
                # external variant may override them later through the parent map.
                for part in mesh.get('parts', []):
                    mh = norm(part.get('material', 'FFFFFFFF'))
                    p = pkgid(mh)
                    if p: required_ids.add(p)
            row['stream_count'] = len(row['streams'])
        except Exception as ex:
            row['violations'].append(repr(ex))
            violations.append(f'{model}:model_dependency_scan:{ex!r}')
        model_dependency_rows[model] = row

    families = []
    for n, ((model, parent), ents) in enumerate(sorted(family_members.items()), 1):
        sample = next(x for x in candidates if x['entity'] == ents[0])
        families.append({
            'family_id': f'SPAWN_VIS_{n:02d}',
            'model': model,
            'model_parent_resource': parent,
            'entity_count': len(ents),
            'entities': ents,
            'skeleton_resources': sorted({next(x for x in candidates if x['entity']==e)['skeleton_resources'][0] for e in ents}),
            'runtime_rig_resources': sorted({next(x for x in candidates if x['entity']==e)['runtime_rig_resources'][0] for e in ents}),
            'bone_counts': sorted({b for e in ents for b in next(x for x in candidates if x['entity']==e).get('bone_counts', [])}),
            'specific_name_hashes': dict(collections.Counter(h for e in ents for h in next(x for x in candidates if x['entity']==e).get('specific_name_hashes', []))),
            'generic_name_hashes': dict(collections.Counter(h for e in ents for h in next(x for x in candidates if x['entity']==e).get('generic_name_hashes', []))),
        })

    out = {
        'schema_version': 1,
        # Compatibility status consumed by the exact parent-material/model exporters.
        'status': 'D1_WORLD_ARTICULATED_ENTITY_PLAN_COMPLETE' if not violations else 'D1_WORLD_ARTICULATED_ENTITY_PLAN_PARTIAL',
        'semantic_scope': 'D1_TOWER_SPAWNED_AI_ACTOR_VISUAL_PLAN',
        'source_reclassification_status': source.get('status'),
        'candidate_count': len(candidates),
        'family_count': len(families),
        'unique_model_count': len(model_dependency_rows),
        'candidates': candidates,
        'families': families,
        'model_dependencies': model_dependency_rows,
        'required_initial_package_ids': sorted(required_ids),
        'violations': violations,
        'remote_logical_package_count': len(c.views),
        'remote_payload_cache_count': len(c.payload_cache),
        'policy': (
            'The WORLD_ARTICULATED status string is an interface adapter only: this plan contains spawned AI actors, not '
            'direct world placements. Each model-parent pair is literal SEntity ownership. Geometry stream header/backing '
            'dependencies are literal s_entity_model FileHash edges. Spawn transforms remain separate D912 evidence and are '
            'not synthesized or joined here.'
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2) + '\n')
    print('STATUS', out['status'], 'CANDIDATES', len(candidates), 'FAMILIES', len(families), 'MODELS', len(model_dependency_rows))
    print('REQUIRED_INITIAL_PACKAGE_IDS', out['required_initial_package_ids'])
    for f in families:
        print('FAMILY', f['family_id'], f['model'], f['model_parent_resource'], 'N', f['entity_count'], 'BONES', f['bone_counts'], 'SPECIFIC', f['specific_name_hashes'])
    print('VIOLATIONS', len(violations))
    for v in violations: print(v)
    return 0 if not violations else 2


if __name__ == '__main__':
    raise SystemExit(main())
