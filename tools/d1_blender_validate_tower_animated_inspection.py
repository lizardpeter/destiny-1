#!/usr/bin/env python3
"""Validate a saved D1 Tower animated inspection .blend in Blender 5.2.1.

This is intentionally a reopen-time validation. It runs after the production
builder has saved the file and checks that the durable .blend still contains the
expected source-alternative collections, collection instances, actor armatures,
and shared D1 Action libraries without promoting a runtime-active state.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    import bpy
except Exception as ex:  # pragma: no cover
    raise SystemExit(f'This tool must run inside Blender Python: {ex!r}')


def cli():
    raw = sys.argv
    args = raw[raw.index('--') + 1:] if '--' in raw else []
    ap = argparse.ArgumentParser()
    ap.add_argument('--report', type=Path, required=True)
    ap.add_argument('--expect-environment', action='store_true')
    return ap.parse_args(args)


def main() -> int:
    a = cli()
    violations: list[str] = []
    scene = bpy.context.scene

    if scene.get('d1InspectionOnly') is not True:
        violations.append('scene_missing_d1InspectionOnly')
    if scene.get('d1RuntimeScenarioSelected') is not False:
        violations.append('runtime_scenario_promoted')
    if scene.get('d1RuntimeActorAnimationStateSelected') is not False:
        violations.append('runtime_animation_state_promoted')

    scenario_cols = [c for c in bpy.data.collections if c.name.startswith('D1_SCENARIO_') and c.name.endswith('_SOURCE_ALTERNATIVES')]
    if len(scenario_cols) != 8:
        violations.append(f'scenario_collection_count:{len(scenario_cols)}')
    for c in scenario_cols:
        if not c.hide_viewport or not c.hide_render:
            violations.append(f'scenario_not_hidden:{c.name}')
        if c.get('d1RuntimeActive') is not False:
            violations.append(f'scenario_runtime_active:{c.name}')

    placements = [o for o in bpy.data.objects if o.instance_type == 'COLLECTION' and o.get('d1Scenario') is not None]
    if len(placements) != 547:
        violations.append(f'placement_instance_count:{len(placements)}')
    for o in placements:
        if o.instance_collection is None:
            violations.append(f'placement_missing_instance_collection:{o.name}')
        if o.get('d1RuntimeActive') is not False:
            violations.append(f'placement_runtime_active:{o.name}')
        if o.get('d1RuntimeAnimationStateSelected') is not False:
            violations.append(f'placement_animation_state_active:{o.name}')

    asset_cols = [c for c in bpy.data.collections if c.name.startswith('D1_ASSET_')]
    if len(asset_cols) != 29:
        violations.append(f'actor_asset_collection_count:{len(asset_cols)}')

    actor_arms = [o for o in bpy.data.objects if o.type == 'ARMATURE' and o.get('d1VisualVariantKey') is not None]
    models = sorted({str(o.get('d1Model')) for o in actor_arms})
    if len(models) != 13:
        violations.append(f'actor_model_count:{len(models)}')
    if not actor_arms:
        violations.append('no_actor_armatures')
    for arm in actor_arms:
        if not arm.get('d1ActionFamilyRepresentative'):
            violations.append(f'armature_missing_action_family:{arm.name}')
        if int(arm.get('d1CompatibleActionCount', 0)) <= 0:
            violations.append(f'armature_missing_action_count:{arm.name}')
        if arm.get('d1RuntimeAnimationStateSelected') is not False:
            violations.append(f'armature_runtime_animation_active:{arm.name}')
        ad = arm.animation_data
        if ad is not None and ad.action is not None:
            violations.append(f'armature_has_selected_action:{arm.name}')

    d1_actions = [act for act in bpy.data.actions if act.name.startswith('D1_')]
    family_reps = sorted({str(act.get('d1ActionFamilyRepresentative')) for act in d1_actions if act.get('d1ActionFamilyRepresentative')})
    if len(family_reps) != 6:
        violations.append(f'action_family_count:{len(family_reps)}')
    if len(d1_actions) != 1365:
        violations.append(f'shared_action_count:{len(d1_actions)}')
    for act in d1_actions:
        if not act.use_fake_user:
            violations.append(f'action_missing_fake_user:{act.name}')

    readme = bpy.data.texts.get('D1_TOWER_INSPECTION_README')
    if readme is None:
        violations.append('inspection_readme_missing')

    env = bpy.data.collections.get('D1_TOWER_ENVIRONMENT_CARD_FIXED')
    if a.expect_environment:
        if env is None:
            violations.append('environment_collection_missing')
        elif len(env.objects) == 0:
            violations.append('environment_collection_empty')
    elif env is not None:
        violations.append('unexpected_environment_collection')

    result = {
        'schema_version': 1,
        'status': 'D1_TOWER_ANIMATED_BLENDER_REOPEN_VALIDATION_COMPLETE' if not violations else 'D1_TOWER_ANIMATED_BLENDER_REOPEN_VALIDATION_FAILED',
        'blender_version': bpy.app.version_string,
        'blend_filepath': bpy.data.filepath,
        'scenario_collection_count': len(scenario_cols),
        'placement_instance_count': len(placements),
        'actor_asset_collection_count': len(asset_cols),
        'actor_armature_count': len(actor_arms),
        'actor_model_count': len(models),
        'shared_action_family_count': len(family_reps),
        'shared_action_count': len(d1_actions),
        'environment_present': env is not None,
        'runtime_active_scenario_selected': bool(scene.get('d1RuntimeScenarioSelected')),
        'runtime_actor_animation_state_selected': bool(scene.get('d1RuntimeActorAnimationStateSelected')),
        'violations': violations,
    }
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
    if violations:
        raise SystemExit(1)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
