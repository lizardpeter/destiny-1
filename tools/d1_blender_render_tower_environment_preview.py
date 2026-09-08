#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, math, sys
from pathlib import Path
import bpy
from mathutils import Vector


def cli():
    raw=sys.argv; args=raw[raw.index('--')+1:] if '--' in raw else []
    ap=argparse.ArgumentParser(); ap.add_argument('--glb',type=Path,required=True); ap.add_argument('--out-dir',type=Path,required=True); ap.add_argument('--report',type=Path,required=True); ap.add_argument('--width',type=int,default=1280); ap.add_argument('--height',type=int,default=720); return ap.parse_args(args)

def pct(xs,p):
    xs=sorted(xs); q=(len(xs)-1)*p; i=int(math.floor(q)); j=min(i+1,len(xs)-1); t=q-i; return xs[i]*(1-t)+xs[j]*t

def look_at(o,t): o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler()

def render(path,cam,pos,target,lens):
    cam.location=Vector(pos); cam.data.lens=lens; look_at(cam,target); bpy.context.scene.render.filepath=str(path.resolve()); bpy.ops.render.render(write_still=True)
    if not path.is_file() or path.stat().st_size<5000: raise RuntimeError(f'bad render {path}')
    return {'file':path.name,'bytes':path.stat().st_size,'camera':[float(x) for x in cam.location],'target':[float(x) for x in target],'lens_mm':lens}

def main():
    a=cli(); a.out_dir.mkdir(parents=True,exist_ok=True); a.report.parent.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(a.glb.resolve()),import_pack_images=False)
    meshes=[o for o in bpy.data.objects if o.type=='MESH']
    if not meshes: raise SystemExit('no mesh objects imported')
    xs=[]; ys=[]; zs=[]
    for o in meshes:
        mw=o.matrix_world
        for c in o.bound_box:
            p=mw@Vector(c); xs.append(p.x); ys.append(p.y); zs.append(p.z)
    x0,x1=pct(xs,.03),pct(xs,.97); y0,y1=pct(ys,.03),pct(ys,.97); z0,z1=pct(zs,.05),pct(zs,.95)
    center=Vector(((x0+x1)/2,(y0+y1)/2,pct(zs,.42))); span=max(x1-x0,y1-y0,10.0); zspan=max(z1-z0,4.0)
    s=bpy.context.scene; s.render.engine='BLENDER_WORKBENCH'; s.render.resolution_x=a.width; s.render.resolution_y=a.height; s.render.resolution_percentage=100; s.render.image_settings.file_format='PNG'; s.render.film_transparent=False
    sh=s.display.shading; sh.light='STUDIO'; sh.color_type='MATERIAL'; sh.show_shadows=True; sh.show_cavity=True; sh.cavity_type='BOTH'; sh.show_specular_highlight=True; sh.background_type='WORLD'; sh.show_outline=False
    try: sh.studiolight_rotate_z=0.65
    except Exception: pass
    world=s.world or bpy.data.worlds.new('D1_PREVIEW_WORLD'); s.world=world; world.color=(0.035,0.045,0.065)
    cd=bpy.data.cameras.new('D1_PREVIEW_CAMERA'); cam=bpy.data.objects.new('D1_PREVIEW_CAMERA',cd); s.collection.objects.link(cam); s.camera=cam; cd.sensor_width=36; cd.clip_start=.05; cd.clip_end=100000
    target=center+Vector((0,0,max(1.0,zspan*.03))); d=span*1.08; h=max(span*.30,zspan*1.5,10.0)
    shots=[]
    shots.append(render(a.out_dir/'01_tower_preview_wide.png',cam,center+Vector((d*.75,-d,h)),target,42.0))
    shots.append(render(a.out_dir/'02_tower_preview_opposite.png',cam,center+Vector((-d,d*.62,h*.82)),target,44.0))
    shots.append(render(a.out_dir/'03_tower_preview_high.png',cam,center+Vector((d*.28,-d*.42,h*1.65)),target,46.0))
    shots.append(render(a.out_dir/'04_tower_preview_side.png',cam,center+Vector((d,-d*.12,h*.55)),target,50.0))
    rep={'status':'D1_TOWER_LOW_MEMORY_ENVIRONMENT_PREVIEW_COMPLETE','blender_version':bpy.app.version_string,'render_engine':s.render.engine,'mesh_object_count':len(meshes),'material_count':len(bpy.data.materials),'image_count':len(bpy.data.images),'resolution':[a.width,a.height],'bounds_robust':{'x03':x0,'x97':x1,'y03':y0,'y97':y1,'z05':z0,'z95':z1},'center':[float(x) for x in center],'span':span,'zspan':zspan,'shots':shots,'policy':'Geometry/material-factor inspection render from card-corrected Tower GLB texture-stripped proxy. Not retail lighting and not an authoritative material preview.'}
    a.report.write_text(json.dumps(rep,indent=2)+'\n'); print(json.dumps(rep,indent=2))
if __name__=='__main__': main()
