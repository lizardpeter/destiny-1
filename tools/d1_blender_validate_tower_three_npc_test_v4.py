#!/usr/bin/env python3
"""Reopen/fail-closed validation for the Tower 3-NPC V4 Blender checkpoint."""
from __future__ import annotations
import argparse,json,math,sys
from pathlib import Path
import bpy

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import d1_blender_build_tower_three_npc_test_v4 as v4


def cli():
    raw=sys.argv;args=raw[raw.index('--')+1:] if '--' in raw else []
    ap=argparse.ArgumentParser();ap.add_argument('--report',type=Path,required=True);return ap.parse_args(args)


def material_image_stats():
    textured=[]
    for m in bpy.data.materials:
        n=0
        if m.use_nodes and m.node_tree:
            n=sum(1 for x in m.node_tree.nodes if x.type=='TEX_IMAGE' and getattr(x,'image',None) is not None)
        if n:textured.append({'material':m.name,'image_texture_node_count':n})
    return {'material_count':len(bpy.data.materials),'material_with_image_texture_count':len(textured),'rows':textured}


def motion_delta(scene,arm,act):
    v4.assign_action(arm,act);arm.data.pose_position='POSE';frames=v4.sample_frames(act,6);snaps=[]
    for f in frames:
        scene.frame_set(f);bpy.context.view_layer.update();snaps.append([float(pb.matrix_basis[r][c]) for pb in arm.pose.bones for r in range(4) for c in range(4)])
    d=0.0
    for a,b in zip(snaps,snaps[1:]):d=max(d,max((abs(x-y) for x,y in zip(a,b)),default=0.0))
    return frames,d


def main():
    a=cli();scene=bpy.context.scene;viol=[];rows=[]
    roots=[o for o in bpy.data.objects if o.type=='EMPTY' and o.get('d1LaptopTestAsset')]
    arms=[o for o in bpy.data.objects if o.type=='ARMATURE' and o.get('d1V4PreviewAction')]
    if len(roots)!=3:viol.append(f'root_count:{len(roots)}')
    if len(arms)!=3:viol.append(f'armature_count:{len(arms)}')
    for root in roots:
        if abs(float(root.rotation_euler.x)+math.pi/2)>1e-5:viol.append(f'{root.name}:root_x_not_minus_90:{root.rotation_euler.x}')
    for arm in arms:
        ad=arm.animation_data;act=ad.action if ad else None
        if act is None:viol.append(f'{arm.name}:no_action');continue
        key=str(arm.get('d1VisualVariantKey') or '')
        objs=[o for o in bpy.data.objects if o.get('d1VisualVariantKey')==key]
        try:
            frames,motion=motion_delta(scene,arm,act)
            gate=v4.bbox_gate(scene,arm,objs,act)
        except Exception as ex:
            viol.append(f'{arm.name}:evaluation:{ex!r}');continue
        if motion<=1e-7:viol.append(f'{arm.name}:no_pose_motion:{motion}')
        if not gate.get('deformed_mesh_sane'):viol.append(f'{arm.name}:deformed_mesh_gate_failed:{gate}')
        rows.append({'armature':arm.name,'key':key,'action':act.name,'sample_frames':frames,'temporal_pose_motion':motion,'mesh_gate':gate})
    mats=material_image_stats()
    if mats['material_with_image_texture_count']<10:
        viol.append(f'too_few_textured_materials:{mats["material_with_image_texture_count"]}')
    if len(bpy.data.images)<10:viol.append(f'too_few_images:{len(bpy.data.images)}')
    if not bool(scene.get('d1TowerThreeNpcTestV4')):viol.append('missing_v4_scene_marker')
    rep={'schema_version':4,'status':'D1_TOWER_THREE_NPC_VISUAL_TEST_V4_REOPEN_VALIDATION','violations':viol,
         'root_count':len(roots),'armature_count':len(arms),'image_count':len(bpy.data.images),'packed_image_count':sum(1 for im in bpy.data.images if im.packed_file is not None),
         'material_stats':mats,'rows':rows}
    a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(rep,indent=2)+'\n');print(json.dumps(rep,indent=2))
    if viol:raise SystemExit('V4 reopen validation failed: '+','.join(viol))
if __name__=='__main__':main()
