#!/usr/bin/env python3
"""Render rest and selected-pose canaries from a saved Tower 3-NPC V4 blend."""
from __future__ import annotations
import argparse,math,sys
from pathlib import Path
import bpy
from mathutils import Vector


def cli():
    raw=sys.argv;args=raw[raw.index('--')+1:] if '--' in raw else []
    ap=argparse.ArgumentParser();ap.add_argument('--out-dir',type=Path,required=True);return ap.parse_args(args)


def look_at(obj,target):
    direction=Vector(target)-obj.location
    obj.rotation_euler=direction.to_track_quat('-Z','Y').to_euler()


def choose_eevee_engine():
    # Blender's public enum changed across releases: 4.x commonly exposed
    # BLENDER_EEVEE_NEXT, while pinned Blender 5.2.1 exposes BLENDER_EEVEE.
    # Query the running build instead of assuming either spelling.
    items=bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items
    available={item.identifier for item in items}
    for candidate in ('BLENDER_EEVEE','BLENDER_EEVEE_NEXT'):
        if candidate in available:
            return candidate
    raise RuntimeError(f'no Eevee render engine in running Blender; available={sorted(available)}')


def setup_scene():
    s=bpy.context.scene
    s.render.engine=choose_eevee_engine();s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100
    s.render.image_settings.file_format='PNG';s.render.film_transparent=False
    if s.world is None:
        s.world=bpy.data.worlds.new('V4_CANARY_WORLD')
    s.world.color=(0.035,0.035,0.035)
    camd=bpy.data.cameras.new('V4_CANARY_CAMERA');cam=bpy.data.objects.new('V4_CANARY_CAMERA',camd);s.collection.objects.link(cam);s.camera=cam
    cam.location=(7.5,-11.5,4.8);camd.lens=52;look_at(cam,(0,0,1.25))
    for name,loc,energy,size in [('Key',(2.5,-4.0,7.0),1600,5.0),('Fill',(-5.0,-1.0,4.0),900,4.0),('Rim',(3.0,5.0,6.0),1200,3.0)]:
        d=bpy.data.lights.new(name,'AREA');d.energy=energy;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=loc;look_at(o,(0,0,1.3))
    return s


def render(path):
    bpy.context.scene.render.filepath=str(path.resolve());bpy.ops.render.render(write_still=True)


def main():
    a=cli();a.out_dir.mkdir(parents=True,exist_ok=True);s=setup_scene();arms=[o for o in bpy.data.objects if o.type=='ARMATURE' and o.get('d1V4PreviewAction')]
    if len(arms)!=3:raise SystemExit(f'expected 3 V4 armatures, got {len(arms)}')
    for arm in arms:arm.data.pose_position='REST'
    s.frame_set(s.frame_start);bpy.context.view_layer.update();render(a.out_dir/'V4_REST.png')
    for arm in arms:arm.data.pose_position='POSE'
    mid=int(round((s.frame_start+s.frame_end)/2));s.frame_set(mid);bpy.context.view_layer.update();render(a.out_dir/'V4_SELECTED_MID.png')
    print('V4_RENDER_CANARIES','engine',s.render.engine,a.out_dir/'V4_REST.png',a.out_dir/'V4_SELECTED_MID.png','mid',mid)
if __name__=='__main__':main()
