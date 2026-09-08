#!/usr/bin/env python3
"""Prove that each Tower actor visual model can consume its decoded family action library.

The selector-selected action census already collapses the 57 spawned Tower actors into
six skeleton/runtime-rig/control families.  This adapter closes the portable handoff:
for every one of the 13 source visual models, compare its skin joint domain and bind/rest
joint transforms to the representative ALL_ACTIONS GLB for its family.

No action/default state is selected here.  A green result only proves that the full
family action library can be assigned to that model by joint name without retargeting.
"""
from __future__ import annotations

import argparse, hashlib, json, math
from pathlib import Path

from d1_gltf_layer_merge import read_glb


def hfile(p: Path) -> str:
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def vec(v, default):
    x = default if v is None else v
    return tuple(float(z) for z in x)


def joint_snapshot(doc: dict) -> list[dict]:
    skins = doc.get('skins') or []
    if len(skins) != 1:
        raise ValueError(f'expected one skin, got {len(skins)}')
    out = []
    seen = set()
    for ni in skins[0].get('joints') or []:
        n = doc['nodes'][int(ni)]
        name = str(n.get('name') or '')
        if not name or name in seen:
            raise ValueError(f'invalid/duplicate joint name {name!r}')
        seen.add(name)
        out.append({
            'name': name,
            'translation': vec(n.get('translation'), [0, 0, 0]),
            'rotation': vec(n.get('rotation'), [0, 0, 0, 1]),
            'scale': vec(n.get('scale'), [1, 1, 1]),
        })
    return out


def max_delta(a: list[dict], b: list[dict]) -> float:
    if [x['name'] for x in a] != [x['name'] for x in b]:
        return math.inf
    d = 0.0
    for x, y in zip(a, b):
        for k in ('translation', 'rotation', 'scale'):
            d = max(d, max(abs(p-q) for p, q in zip(x[k], y[k])))
    return d


def channel_joint_names(doc: dict) -> tuple[set[str], set[str]]:
    names = set()
    paths = set()
    for anim in doc.get('animations') or []:
        for ch in anim.get('channels') or []:
            tgt = ch.get('target') or {}
            ni = int(tgt['node'])
            name = str(doc['nodes'][ni].get('name') or '')
            if not name:
                raise ValueError(f'animation targets unnamed node {ni}')
            names.add(name)
            paths.add(str(tgt.get('path') or ''))
    return names, paths


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--family-summary', type=Path, required=True)
    ap.add_argument('--skinned-dir', type=Path, required=True)
    ap.add_argument('--action-dir', type=Path, required=True)
    ap.add_argument('--rest-tolerance', type=float, default=1e-7)
    ap.add_argument('-o', '--out', type=Path, required=True)
    a = ap.parse_args()

    fam = json.loads(a.family_summary.read_text())
    if fam.get('status') != 'D1_TOWER_SPAWNED_ACTOR_FAMILY_ANIMATION_LIBRARIES_COMPLETE':
        raise SystemExit('family action summary is not complete')
    rows = []
    violations = []
    seen_models = set()
    for f in fam.get('families') or []:
        rep = str(f['representative_model']).upper()
        pattern = f'{rep}_{str(f["skeleton"]).upper()}_{str(f["control"]).upper()}_ALL_ACTIONS.glb'
        rp = a.action_dir / pattern
        if not rp.exists():
            violations.append(f'{rep}: representative action GLB missing {pattern}')
            continue
        rg, _ = read_glb(rp)
        rj = joint_snapshot(rg)
        rnames = [x['name'] for x in rj]
        chan_names, chan_paths = channel_joint_names(rg)
        if not chan_names.issubset(set(rnames)):
            violations.append(f'{rep}: animation targets outside representative skin')
        if not chan_paths.issubset({'translation','rotation','scale'}):
            violations.append(f'{rep}: unsupported animation target paths {sorted(chan_paths)}')
        if len(rg.get('animations') or []) != int(f['appended_animation_count']):
            violations.append(f'{rep}: action count disagrees with source summary')
        for model0 in f.get('family_models') or []:
            model = str(model0).upper()
            if model in seen_models:
                violations.append(f'{model}: appears in multiple action families')
                continue
            seen_models.add(model)
            tp = a.skinned_dir / f'{model}_SKINNED.glb'
            if not tp.exists():
                violations.append(f'{model}: source skinned GLB missing')
                continue
            tg, _ = read_glb(tp)
            tj = joint_snapshot(tg)
            same_names = [x['name'] for x in tj] == rnames
            delta = max_delta(tj, rj)
            compatible = same_names and delta <= a.rest_tolerance
            if not compatible:
                violations.append(f'{model}: family bind/rest mismatch names={same_names} max_delta={delta}')
            rows.append({
                'model': model,
                'representative_model': rep,
                'skeleton': str(f['skeleton']).upper(),
                'runtime_rig': str(f['runtime_rig']).upper(),
                'control': str(f['control']).upper(),
                'joint_count': len(tj),
                'ordered_joint_names_identical': same_names,
                'max_joint_rest_component_delta': delta,
                'action_count': int(f['appended_animation_count']),
                'selector_state_count': int(f['selector_state_count']),
                'selected_clip_count': int(f['selected_clip_count']),
                'exact_dimension_animation_count': int(f['exact_dimension_animation_count']),
                'native_retarget_required_animation_count': int(f['native_retarget_required_animation_count']),
                'animation_target_joint_count': len(chan_names),
                'animation_target_paths': sorted(chan_paths),
                'source_skinned_glb': tp.name,
                'source_skinned_sha256': hfile(tp),
                'representative_action_glb': rp.name,
                'representative_action_sha256': hfile(rp),
                'shared_action_library_assignable_by_joint_name': compatible,
            })

    expected = {str(x).upper() for f in fam.get('families') or [] for x in f.get('family_models') or []}
    if len(expected) != 13:
        violations.append(f'family summary covers {len(expected)} source models, expected 13')
    if seen_models != expected:
        violations.append(f'model coverage mismatch missing={sorted(expected-seen_models)} extra={sorted(seen_models-expected)}')
    if len(rows) != 13:
        violations.append(f'compatibility row count {len(rows)} != 13')

    out = {
        'schema_version': 1,
        'status': 'D1_TOWER_ACTOR_SHARED_ACTION_FAMILY_COMPATIBILITY_CLOSED' if not violations else 'D1_TOWER_ACTOR_SHARED_ACTION_FAMILY_COMPATIBILITY_PARTIAL',
        'actor_model_count': len(rows),
        'action_family_count': len(fam.get('families') or []),
        'actor_entity_count': int(fam.get('actor_entity_count', 0)),
        'models': sorted(rows, key=lambda x: x['model']),
        'violations': violations,
        'gates': {
            'runtime_actor_animation_state_selected': False,
            'runtime_active_scenario_selected': False,
        },
        'policy': 'Family compatibility requires identical ordered skin-joint names and source bind/rest TRS within tolerance. It proves library assignability only; no idle/default/runtime action is selected.'
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({
        'status': out['status'],
        'actor_model_count': out['actor_model_count'],
        'action_family_count': out['action_family_count'],
        'action_counts_by_model': {r['model']: r['action_count'] for r in out['models']},
        'max_rest_delta': max((r['max_joint_rest_component_delta'] for r in rows), default=None),
        'violations': violations,
    }, indent=2))
    return 0 if not violations else 2


if __name__ == '__main__':
    raise SystemExit(main())
