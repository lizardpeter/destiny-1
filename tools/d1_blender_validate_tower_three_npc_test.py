#!/usr/bin/env python3
"""Reopen-validation for the laptop-friendly three-NPC Tower test blend."""
from __future__ import annotations

import argparse, json, sys
from pathlib import Path
import bpy


def cli():
    raw=sys.argv; args=raw[raw.index('--')+1:] if '--' in raw else []
    ap=argparse.ArgumentParser(); ap.add_argument('--report',type=Path,required=True); return ap.parse_args(args)


def main():
    a=cli(); violations=[]
    roots=[o for o in bpy.data.objects if bool(o.get('d1LaptopTestAsset')) and o.type=='EMPTY' and o.name.startswith('TEST_')]
    arms=[o for o in bpy.data.objects if o.type=='ARMATURE' and bool(o.get('d1LaptopTestAsset'))]
    actions=[x for x in bpy.data.actions if x.name.startswith('D1_TEST_')]
    models=sorted({str(o.get('d1Model')) for o in roots if o.get('d1Model')})
    reps=sorted({str(o.get('d1ActionFamilyRepresentative')) for o in arms if o.get('d1ActionFamilyRepresentative')})
    env=[c.name for c in bpy.data.collections if 'TOWER_ENVIRONMENT' in c.name]
    scenarios=[c.name for c in bpy.data.collections if c.name.startswith('D1_SCENARIO_')]
    unpacked=[im.name for im in bpy.data.images if im.source=='FILE' and im.packed_file is None]

    if len(roots)!=3: violations.append(f'root actor count {len(roots)} != 3')
    if len(models)!=3: violations.append(f'model count {len(models)} != 3')
    if len(arms)<3: violations.append(f'armature count {len(arms)} < 3')
    if len(reps)!=2: violations.append(f'action family count {len(reps)} != 2')
    if len(actions)!=8: violations.append(f'retained action count {len(actions)} != 8')
    if env: violations.append(f'environment unexpectedly present: {env}')
    if scenarios: violations.append(f'scenario collections unexpectedly present: {scenarios}')
    if unpacked: violations.append(f'unpacked external images remain: {unpacked[:10]}')
    if not bool(bpy.context.scene.get('d1LaptopThreeNpcTest')): violations.append('scene laptop-test marker missing')
    if bool(bpy.context.scene.get('d1RuntimeScenarioSelected')): violations.append('runtime scenario selected')
    if bool(bpy.context.scene.get('d1RuntimeActorAnimationStateSelected')): violations.append('runtime animation state selected')

    rep={
        'schema_version':1,'status':'D1_TOWER_THREE_NPC_LAPTOP_TEST_REOPEN_VALIDATION',
        'violations':violations,'actor_root_count':len(roots),'armature_count':len(arms),'model_count':len(models),
        'models':models,'action_family_count':len(reps),'action_family_representatives':reps,
        'retained_action_count':len(actions),'packed_image_count':sum(1 for im in bpy.data.images if im.packed_file is not None),
        'environment_present':bool(env),'scenario_collection_count':len(scenarios),
        'runtime_scenario_selected':bool(bpy.context.scene.get('d1RuntimeScenarioSelected')),
        'runtime_animation_state_selected':bool(bpy.context.scene.get('d1RuntimeActorAnimationStateSelected')),
    }
    a.report.parent.mkdir(parents=True,exist_ok=True); a.report.write_text(json.dumps(rep,indent=2)+'\n'); print(json.dumps(rep,indent=2))
    if violations: raise SystemExit('validation failed: '+json.dumps(violations))

if __name__=='__main__': main()
