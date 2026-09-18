#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,math,sys
from pathlib import Path
import bpy

def cli():
    raw=sys.argv;args=raw[raw.index('--')+1:] if '--' in raw else []
    ap=argparse.ArgumentParser();ap.add_argument('--report',type=Path,required=True);return ap.parse_args(args)

def main():
    a=cli();viol=[]
    roots=[o for o in bpy.data.objects if o.name.startswith('TEST_') and o.type=='EMPTY']
    arms=[o for o in bpy.data.objects if o.type=='ARMATURE' and o.get('d1LaptopTestAsset')]
    actions=[x for x in bpy.data.actions if x.name.startswith('D1_TEST_')]
    assigned=[o for o in arms if o.animation_data and o.animation_data.action]
    models=sorted({str(o.get('d1Model') or '') for o in roots if o.get('d1Model')})
    if len(roots)!=3:viol.append(f'root_count:{len(roots)}')
    if len(arms)!=3:viol.append(f'armature_count:{len(arms)}')
    if len(models)!=3:viol.append(f'model_count:{len(models)}')
    if len(actions)!=8:viol.append(f'action_count:{len(actions)}')
    if len(assigned)!=3:viol.append(f'assigned_action_count:{len(assigned)}')
    for o in roots:
        if abs(float(o.rotation_euler.x)+math.pi/2)>1e-5:viol.append(f'root_basis:{o.name}:{float(o.rotation_euler.x)}')
        if o.get('d1BlenderBasisCorrection')!='ROT_X_NEG_90_AFTER_GLTF_IMPORT':viol.append(f'root_basis_marker:{o.name}')
    for o in assigned:
        if not o.animation_data.action.name.startswith('D1_TEST_'):viol.append(f'non_test_action:{o.name}:{o.animation_data.action.name}')
        if not o.get('d1TestPreviewActionAssigned'):viol.append(f'missing_preview_action_marker:{o.name}')
    if bpy.context.scene.frame_end<=bpy.context.scene.frame_start:viol.append('invalid_frame_range')
    if not bpy.context.scene.get('d1TestPreviewAnimationAssigned'):viol.append('scene_preview_action_marker_false')
    if bpy.context.scene.get('d1RuntimeActorAnimationStateSelected') is not False:viol.append('runtime_animation_gate_promoted')
    rep={'schema_version':2,'status':'D1_TOWER_THREE_NPC_LAPTOP_TEST_V2_REOPEN_VALIDATION','violations':viol,'actor_root_count':len(roots),'armature_count':len(arms),'model_count':len(models),'retained_action_count':len(actions),'assigned_preview_action_count':len(assigned),'scene_frame_start':bpy.context.scene.frame_start,'scene_frame_end':bpy.context.scene.frame_end,'root_rotations_x':{o.name:float(o.rotation_euler.x) for o in roots},'assigned_actions':{o.name:o.animation_data.action.name for o in assigned},'material_count':len(bpy.data.materials),'image_count':len(bpy.data.images)}
    a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(rep,indent=2)+'\n');print(json.dumps(rep,indent=2))
    if viol:raise SystemExit('validation failed: '+','.join(viol))
if __name__=='__main__':main()
