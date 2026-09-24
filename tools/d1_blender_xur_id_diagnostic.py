#!/usr/bin/env python3
"""Render deterministic material/object ID diagnostics from an already-open Xur .blend.

This intentionally replaces shading only for the debug renders and never saves
those replacements back to the source blend.  It is used to identify which exact
source material/range owns a visible artifact without inferring semantics from
screen appearance.
"""
from __future__ import annotations
import argparse, colorsys, hashlib, json, math, sys
from pathlib import Path
import bpy

def argv_after_dashdash():
    a=sys.argv
    return a[a.index('--')+1:] if '--' in a else []

def vivid(seed:str):
    h=int(hashlib.sha256(seed.encode()).hexdigest()[:8],16)/0xffffffff
    s=0.72 + (int(hashlib.sha256((seed+'s').encode()).hexdigest()[:2],16)/255)*0.22
    v=0.78 + (int(hashlib.sha256((seed+'v').encode()).hexdigest()[:2],16)/255)*0.20
    r,g,b=colorsys.hsv_to_rgb(h,s,v)
    return (r,g,b,1.0)

def flat_material(mat,color):
    mat.use_nodes=True
    nt=mat.node_tree; nt.nodes.clear()
    out=nt.nodes.new('ShaderNodeOutputMaterial')
    em=nt.nodes.new('ShaderNodeEmission')
    em.inputs['Color'].default_value=color
    em.inputs['Strength'].default_value=1.0
    nt.links.new(em.outputs['Emission'],out.inputs['Surface'])
    try: mat.surface_render_method='DITHERED'
    except Exception: pass

def render(path:Path):
    sc=bpy.context.scene
    try: sc.render.engine='BLENDER_EEVEE_NEXT'
    except Exception: pass
    sc.render.resolution_x=900;sc.render.resolution_y=1200;sc.render.resolution_percentage=100
    sc.render.image_settings.file_format='PNG'
    sc.render.filepath=str(path.resolve())
    if sc.world:
        sc.world.color=(0,0,0)
        if sc.world.use_nodes:
            bg=next((n for n in sc.world.node_tree.nodes if n.type=='BACKGROUND'),None)
            if bg:
                bg.inputs['Color'].default_value=(0,0,0,1)
                bg.inputs['Strength'].default_value=0.0
    bpy.context.view_layer.update()
    bpy.ops.render.render(write_still=True)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--material-output',type=Path,required=True)
    ap.add_argument('--object-output',type=Path,required=True)
    ap.add_argument('--report',type=Path,required=True)
    a=ap.parse_args(argv_after_dashdash())
    mats=[]; material_colors={}
    for mat in bpy.data.materials:
        tag=str(mat.get('d1_material_taghash') or '').upper()
        if not tag: continue
        col=vivid('mat:'+tag)
        material_colors[tag]=col
        mats.append((mat,tag,col))
    if not mats: raise RuntimeError('no d1_material_taghash materials')
    for mat,tag,col in mats: flat_material(mat,col)
    a.material_output.parent.mkdir(parents=True,exist_ok=True)
    render(a.material_output)

    # Object ID pass: each mesh object gets its own temporary emission material.
    object_rows=[]
    for obj in [o for o in bpy.data.objects if o.type=='MESH']:
        key=obj.name
        col=vivid('obj:'+key)
        dbg=bpy.data.materials.new('D1_DEBUG_OBJECT_'+hashlib.sha1(key.encode()).hexdigest()[:10])
        flat_material(dbg,col)
        old=[s.material for s in obj.material_slots]
        if not obj.data.materials:
            obj.data.materials.append(dbg)
        else:
            for i in range(len(obj.data.materials)): obj.data.materials[i]=dbg
        object_rows.append({
            'object':obj.name,'color_rgba':list(col),
            'source_materials':[str(m.get('d1_material_taghash') or '') if m else None for m in old],
            'bounds_world':[[float(x) for x in obj.matrix_world @ obj.bound_box[i]] for i in range(8)]
        })
    render(a.object_output)

    rep={
      'schema_version':1,'status':'D1_XUR_BLENDER_ID_DIAGNOSTIC_EXACT',
      'frame':int(bpy.context.scene.frame_current),
      'material_id_render':str(a.material_output),
      'object_id_render':str(a.object_output),
      'materials':[{'material':tag,'color_rgba':list(col),'blender_name':mat.name} for mat,tag,col in mats],
      'objects':object_rows,
      'policy':'Deterministic false-color ownership diagnostic only. Colors carry no material/visibility semantics and the source blend is not saved after replacement.'
    }
    a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(rep,indent=2)+'\n')
    print('D1_XUR_BLENDER_ID_DIAGNOSTIC_GREEN',len(mats),len(object_rows),bpy.context.scene.frame_current)

if __name__=='__main__':main()
