#!/usr/bin/env python3
"""Render two fast inspection views of one compact textured Tower cell GLB."""
from __future__ import annotations
import argparse,json,math,sys
from pathlib import Path
import bpy
from mathutils import Vector

def cli():
    raw=sys.argv; args=raw[raw.index('--')+1:] if '--' in raw else []
    ap=argparse.ArgumentParser(); ap.add_argument('--glb',type=Path,required=True); ap.add_argument('--out-dir',type=Path,required=True); ap.add_argument('--label',required=True); ap.add_argument('--width',type=int,default=960); ap.add_argument('--height',type=int,default=540); return ap.parse_args(args)

def pct(xs,p):
    xs=sorted(float(x) for x in xs); q=(len(xs)-1)*p; i=int(math.floor(q)); j=min(i+1,len(xs)-1); t=q-i; return xs[i]*(1-t)+xs[j]*t

def look(o,t):
    d=Vector(t)-o.location
    if d.length<1e-6: raise RuntimeError('degenerate camera direction')
    o.rotation_euler=d.to_track_quat('-Z','Y').to_euler()

def shot(path,cam,pos,target,lens):
    cam.location=Vector(pos); cam.data.lens=float(lens); look(cam,target); bpy.context.scene.render.filepath=str(path.resolve()); bpy.ops.render.render(write_still=True)
    if not path.is_file() or path.stat().st_size<4000: raise RuntimeError(f'render missing/too small: {path}')
    return {'file':path.name,'bytes':path.stat().st_size,'camera':[float(x) for x in cam.location],'target':[float(x) for x in target],'lens_mm':float(lens)}

def main():
    a=cli(); a.out_dir.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(a.glb.resolve()),import_pack_images=False)
    meshes=[o for o in bpy.data.objects if o.type=='MESH']
    if not meshes: raise SystemExit('no mesh objects imported')
    xs=[];ys=[];zs=[]
    for o in meshes:
        mw=o.matrix_world
        for c in o.bound_box:
            p=mw@Vector(c)
            if all(math.isfinite(v) for v in p): xs.append(p.x);ys.append(p.y);zs.append(p.z)
    if len(xs)<8: raise SystemExit('insufficient finite bounds')
    x0,x1=pct(xs,.015),pct(xs,.985); y0,y1=pct(ys,.015),pct(ys,.985); z0,z1=pct(zs,.03),pct(zs,.97)
    center=Vector(((x0+x1)/2,(y0+y1)/2,pct(zs,.45))); span=max(x1-x0,y1-y0,8.0); zspan=max(z1-z0,3.0)
    s=bpy.context.scene; s.render.engine='BLENDER_WORKBENCH'; s.render.resolution_x=a.width; s.render.resolution_y=a.height; s.render.resolution_percentage=100; s.render.image_settings.file_format='PNG'; s.render.film_transparent=False
    sh=s.display.shading; sh.light='STUDIO'; sh.show_shadows=True; sh.show_cavity=True; sh.cavity_type='BOTH'; sh.show_specular_highlight=True; sh.background_type='WORLD'
    try: sh.show_outline=False
    except Exception: pass
    try: sh.color_type='TEXTURE'
    except Exception: sh.color_type='MATERIAL'
    try: sh.studiolight_rotate_z=.55
    except Exception: pass
    world=s.world or bpy.data.worlds.new('D1_CELL_PREVIEW_WORLD'); s.world=world; world.color=(.025,.035,.055)
    cd=bpy.data.cameras.new('D1_CELL_CAMERA'); cam=bpy.data.objects.new('D1_CELL_CAMERA',cd); s.collection.objects.link(cam); s.camera=cam; cd.sensor_width=36; cd.clip_start=.05; cd.clip_end=100000
    target=center+Vector((0,0,max(1.0,zspan*.02))); d=span*1.04; h=max(span*.27,zspan*1.45,8.0)
    p1=a.out_dir/f'{a.label}_wide.png'; p2=a.out_dir/f'{a.label}_high.png'
    shots=[shot(p1,cam,center+Vector((d*.72,-d,h)),target,43.0), shot(p2,cam,center+Vector((-d*.58,d*.72,h*1.30)),target,46.0)]
    rep={'status':'D1_TOWER_CELL_RENDER_PREVIEW_COMPLETE','label':a.label,'source_glb':a.glb.name,'blender_version':bpy.app.version_string,'render_engine':s.render.engine,'workbench_color_type':s.display.shading.color_type,'mesh_object_count':len(meshes),'material_count':len(bpy.data.materials),'image_count':len(bpy.data.images),'center':[float(x) for x in center],'span':float(span),'zspan':float(zspan),'bounds_robust':{'x015':x0,'x985':x1,'y015':y0,'y985':y1,'z03':z0,'z97':z1},'shots':shots,'policy':'Fast Blender Workbench inspection view of one exact compact Tower baked-static cell. Camera/studio lighting are diagnostic, not retail.'}
    rp=a.out_dir/f'{a.label}_report.json'; rp.write_text(json.dumps(rep,indent=2)+'\n'); print(json.dumps(rep,indent=2))
if __name__=='__main__': main()
