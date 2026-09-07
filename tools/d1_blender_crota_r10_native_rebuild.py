#!/usr/bin/env python3
"""Blender-native Crota R10 material rebuild.

Run inside Blender with:
  blender --background --python d1_blender_crota_r10_native_rebuild.py -- \
    --input <carrier.glb> --output <scene.blend> --preview <render.png> --mode bind|anim

The GLB remains a transport carrier.  This script replaces its portable PBR preview
with a Blender-native shader graph that directly represents the source-closed D1
composition:

    Destination * (1 - attenuation) + emissive RGB

Native evidence used:
* paired color PS 8108E953/955/956 export RGB with A=0;
* paired attenuation PS 80AAE1CD/8108E958/959 export RGB=0 with alpha;
* material state 0x88 = Source + Destination*(1-SourceAlpha).

The Blender material expresses those two passes in one surface closure to avoid
coplanar duplicate meshes and z-fighting:
* Mix(Transparent, Black Surface, attenuation) transmits Destination*(1-a)
* Add Shader adds Crota's emissive color contribution.

Where the exact runtime attenuation scalar is not source-closed, the graph uses a
source-constrained proxy driven by the exact retail control texture plus a bounded
material-specific factor.  The exact retail textures remain embedded and the proxy
nodes are explicitly named D1_PROXY_*.
"""
from __future__ import annotations
import argparse, json, math, sys
from pathlib import Path

import bpy
from mathutils import Vector

MAT_PROC = {'D1_8108E7A9', 'D1_8108E7B2'}
MAT_ATLAS = {'D1_8108E7AA', 'D1_8108E7B3'}
MAT_DETAIL = {'D1_8108E7B1'}
ACTIVE = MAT_PROC | MAT_ATLAS | MAT_DETAIL

PROC_COLOR = (0.18661969900131226, 1.0, 0.8700880408287048, 1.0)
DETAIL_COLOR = (0.22183096408843994, 1.0, 0.9177990555763245, 1.0)


def args_after_double_dash():
    argv = sys.argv
    if '--' in argv:
        argv = argv[argv.index('--') + 1:]
    else:
        argv = []
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--preview', type=Path, required=True)
    ap.add_argument('--mode', choices=('bind','anim'), required=True)
    return ap.parse_args(argv)


def find_image(token: str):
    token = token.upper()
    hits = [im for im in bpy.data.images if token in im.name.upper()]
    if len(hits) != 1:
        raise RuntimeError(f'expected one Blender image containing {token}, got {[x.name for x in hits]}')
    return hits[0]


def set_blend_compat(mat):
    # Blender <=4.1
    if hasattr(mat, 'blend_method'):
        try: mat.blend_method = 'BLEND'
        except Exception: pass
    if hasattr(mat, 'shadow_method'):
        try: mat.shadow_method = 'NONE'
        except Exception: pass
    # Blender 4.2+
    if hasattr(mat, 'surface_render_method'):
        for value in ('DITHERED', 'BLENDED'):
            try:
                mat.surface_render_method = value
                break
            except Exception:
                pass
    if hasattr(mat, 'use_transparency_overlap'):
        try: mat.use_transparency_overlap = False
        except Exception: pass
    mat.use_nodes = True


def add_tex(nodes, image, name, x, y):
    n = nodes.new('ShaderNodeTexImage')
    n.name = name; n.label = name; n.image = image; n.location = (x,y)
    try: n.interpolation = 'Linear'
    except Exception: pass
    return n


def add_rgb(nodes, rgba, name, x, y):
    n = nodes.new('ShaderNodeRGB'); n.name=name; n.label=name; n.location=(x,y)
    n.outputs['Color'].default_value = rgba
    return n


def add_value(nodes, value, name, x, y):
    n=nodes.new('ShaderNodeValue'); n.name=name; n.label=name; n.location=(x,y)
    n.outputs[0].default_value=float(value); return n


def build_native_material(mat):
    set_blend_compat(mat)
    nodes = mat.node_tree.nodes; links = mat.node_tree.links
    nodes.clear()

    out = nodes.new('ShaderNodeOutputMaterial'); out.location=(820,40); out.name='D1_NATIVE_OUTPUT'
    transparent = nodes.new('ShaderNodeBsdfTransparent'); transparent.location=(250,-180); transparent.name='D1_DESTINATION_TRANSPARENT'
    black = nodes.new('ShaderNodeBsdfDiffuse'); black.location=(250,-20); black.name='D1_ATTENUATION_BLACK'
    black.inputs['Color'].default_value=(0,0,0,1); black.inputs['Roughness'].default_value=1.0
    mix = nodes.new('ShaderNodeMixShader'); mix.location=(500,-100); mix.name='D1_DESTINATION_ATTENUATION'
    links.new(transparent.outputs['BSDF'],mix.inputs[1]); links.new(black.outputs['BSDF'],mix.inputs[2])

    emission = nodes.new('ShaderNodeEmission'); emission.location=(490,180); emission.name='D1_ADDITIVE_COLOR'
    add = nodes.new('ShaderNodeAddShader'); add.location=(700,50); add.name='D1_NATIVE_SOURCE_PLUS_DESTINATION'
    links.new(mix.outputs['Shader'],add.inputs[0]); links.new(emission.outputs['Emission'],add.inputs[1]); links.new(add.outputs['Shader'],out.inputs['Surface'])

    tag = mat.name.upper()
    tex_control = find_image('8108E7B6')
    tex_atlas = find_image('8108E951')
    tex_detail = find_image('8108E952')

    if tag in MAT_PROC:
        # Exact PS8108E955 is procedural and consumes the control family.  Use the
        # exact BC4 scalar only as modulation, never as literal albedo.
        t = add_tex(nodes, tex_control, 'D1_EXACT_8108E7B6_CONTROL', -820,170)
        ramp = nodes.new('ShaderNodeValToRGB'); ramp.name='D1_PROXY_PROC_COLOR_RAMP'; ramp.label='D1_PROXY_PROC_COLOR_RAMP'; ramp.location=(-500,190)
        ramp.color_ramp.elements[0].position=0.05; ramp.color_ramp.elements[0].color=(0.005,0.025,0.02,1)
        ramp.color_ramp.elements[1].position=0.72; ramp.color_ramp.elements[1].color=(PROC_COLOR[0],PROC_COLOR[1],PROC_COLOR[2],1)
        links.new(t.outputs['Color'],ramp.inputs['Fac'])
        links.new(ramp.outputs['Color'],emission.inputs['Color'])
        emission.inputs['Strength'].default_value=1.65

        alpha_mul=nodes.new('ShaderNodeMath'); alpha_mul.operation='MULTIPLY'; alpha_mul.name='D1_PROXY_ATTENUATION_SCALE'; alpha_mul.location=(-220,-190); alpha_mul.inputs[1].default_value=0.58
        alpha_bias=nodes.new('ShaderNodeMath'); alpha_bias.operation='ADD'; alpha_bias.name='D1_PROXY_ATTENUATION_BIAS'; alpha_bias.location=(10,-190); alpha_bias.inputs[1].default_value=0.08
        links.new(t.outputs['Color'],alpha_mul.inputs[0]); links.new(alpha_mul.outputs[0],alpha_bias.inputs[0]); links.new(alpha_bias.outputs[0],mix.inputs['Fac'])
        proxy='PS8108E955_COLOR + PS8108E958_ATTENUATION_PROXY_FROM_EXACT_BC4'

    elif tag in MAT_ATLAS:
        t=add_tex(nodes,tex_atlas,'D1_EXACT_8108E951_COLOR_ATLAS',-780,190)
        mult=nodes.new('ShaderNodeVectorMath'); mult.operation='MULTIPLY'; mult.name='D1_ATLAS_GREEN_GAIN'; mult.location=(-430,190)
        tint=add_rgb(nodes,(0.72,1.0,0.86,1.0),'D1_SOURCE_GREEN_TINT',-700,20)
        links.new(t.outputs['Color'],mult.inputs[0]); links.new(tint.outputs['Color'],mult.inputs[1]); links.new(mult.outputs['Vector'],emission.inputs['Color'])
        emission.inputs['Strength'].default_value=2.2
        # PS8108E959 samples the atlas alpha lane; retail BC1 resolves opaque in
        # this decode, so the unresolved runtime scalar is represented separately.
        a=add_value(nodes,0.34,'D1_PROXY_8108E959_RUNTIME_ATTENUATION',-120,-160)
        links.new(a.outputs[0],mix.inputs['Fac'])
        proxy='PS8108E956_EXACT_ATLAS_COLOR + PS8108E959_RUNTIME_ALPHA_PROXY'

    elif tag in MAT_DETAIL:
        t=add_tex(nodes,tex_detail,'D1_EXACT_8108E952_DETAIL_COLOR',-780,190)
        tint=add_rgb(nodes,DETAIL_COLOR,'D1_EXACT_DETAIL_TINT',-690,20)
        mult=nodes.new('ShaderNodeVectorMath'); mult.operation='MULTIPLY'; mult.name='D1_DETAIL_COLOR_MULT'; mult.location=(-430,190)
        links.new(t.outputs['Color'],mult.inputs[0]); links.new(tint.outputs['Color'],mult.inputs[1]); links.new(mult.outputs['Vector'],emission.inputs['Color'])
        emission.inputs['Strength'].default_value=2.0
        a=add_value(nodes,0.78,'D1_PROXY_80AAE1CD_ATTENUATION',-120,-160); links.new(a.outputs[0],mix.inputs['Fac'])
        proxy='PS8108E953_EXACT_DETAIL_COLOR + 80AAE1CD_BLACK_ATTENUATION'
    else:
        raise RuntimeError(tag)

    mat.diffuse_color = (0.04,0.65,0.45,0.35)
    mat['d1_r10_native_contract']='Source + Destination*(1-SourceAlpha)'
    mat['d1_r10_blender_closure']='AddShader(attenuated destination, emissive color)'
    mat['d1_r10_proxy']=proxy


def clean_scene_import(path: Path):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(path))
    # Keep armature data for animation, but never show the Blender bone shapes.
    for obj in bpy.context.scene.objects:
        if obj.type == 'ARMATURE':
            obj.data.display_type='STICK'; obj.show_in_front=False; obj.hide_set(True); obj.hide_render=True


def rebuild_materials():
    found=[]
    for mat in list(bpy.data.materials):
        if mat.name.upper() in ACTIVE:
            build_native_material(mat); found.append(mat.name.upper())
    if set(found) != ACTIVE:
        raise RuntimeError(f'active material mismatch: {found}')


def add_stage_and_camera():
    # Dark neutral world makes the additive/attenuation behavior legible.
    world=bpy.data.worlds.new('D1_CROTA_DARK_WORLD'); world.use_nodes=True
    bg=world.node_tree.nodes.get('Background'); bg.inputs['Color'].default_value=(0.006,0.009,0.008,1); bg.inputs['Strength'].default_value=0.12
    bpy.context.scene.world=world

    # Camera positioned from actual mesh bounds.
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH' and not o.hide_get()]
    pts=[]
    for o in meshes:
        for c in o.bound_box: pts.append(o.matrix_world @ Vector(c))
    if not pts: raise RuntimeError('no visible Crota meshes')
    mn=Vector((min(p.x for p in pts),min(p.y for p in pts),min(p.z for p in pts)))
    mx=Vector((max(p.x for p in pts),max(p.y for p in pts),max(p.z for p in pts)))
    center=(mn+mx)*0.5; extent=max((mx-mn).length,1.0)
    cam_data=bpy.data.cameras.new('CROTA_PREVIEW_CAMERA'); cam=bpy.data.objects.new('CROTA_PREVIEW_CAMERA',cam_data); bpy.context.scene.collection.objects.link(cam)
    cam.location=center+Vector((extent*0.15,-extent*1.15,extent*0.05))
    direction=center-cam.location; cam.rotation_euler=direction.to_track_quat('-Z','Y').to_euler(); cam_data.lens=58; bpy.context.scene.camera=cam

    # Soft fill lights only; Crota color itself remains emissive.
    for name,loc,energy,size in [
        ('KEY',center+Vector((-extent*0.45,-extent*0.55,extent*0.55)),500,extent*0.45),
        ('RIM',center+Vector((extent*0.65,extent*0.25,extent*0.35)),700,extent*0.35),
    ]:
        ld=bpy.data.lights.new(name,'AREA'); ld.energy=energy; ld.shape='DISK'; ld.size=size
        lo=bpy.data.objects.new(name,ld); lo.location=loc; lo.rotation_euler=(center-loc).to_track_quat('-Z','Y').to_euler(); bpy.context.scene.collection.objects.link(lo)


def configure_render(preview: Path):
    sc=bpy.context.scene
    # Prefer Eevee for user viewport parity; fall back if engine name differs.
    for engine in ('BLENDER_EEVEE_NEXT','BLENDER_EEVEE'):
        try: sc.render.engine=engine; break
        except Exception: pass
    sc.render.resolution_x=900; sc.render.resolution_y=1100; sc.render.resolution_percentage=100
    sc.render.image_settings.file_format='PNG'; sc.render.filepath=str(preview)
    sc.render.film_transparent=False
    sc.view_settings.look='AgX - Medium High Contrast' if 'AgX - Medium High Contrast' in [i.name for i in bpy.types.ColorManagedViewSettings.bl_rna.properties['look'].enum_items] else sc.view_settings.look


def save_and_render(output:Path, preview:Path, mode:str):
    sc=bpy.context.scene
    if mode=='anim':
        sc.frame_start=1; sc.frame_end=61; sc.frame_set(1)
    else:
        sc.frame_start=1; sc.frame_end=1; sc.frame_set(1)
    output.parent.mkdir(parents=True,exist_ok=True); preview.parent.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(output))
    bpy.ops.render.render(write_still=True)


def main():
    a=args_after_double_dash()
    clean_scene_import(a.input)
    rebuild_materials()
    add_stage_and_camera()
    configure_render(a.preview)
    save_and_render(a.output,a.preview,a.mode)
    print(json.dumps({
        'status':'D1_CROTA_R10_BLENDER_NATIVE_COMPLETE',
        'input':str(a.input),'output':str(a.output),'preview':str(a.preview),'mode':a.mode,
        'materials':sorted(ACTIVE),
        'native_contract':'Source + Destination*(1-SourceAlpha)',
        'implementation':'single Blender closure = attenuated destination + emission',
        'frame_range':[bpy.context.scene.frame_start,bpy.context.scene.frame_end],
    },indent=2))

if __name__=='__main__': main()
