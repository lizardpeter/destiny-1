#!/usr/bin/env python3
"""Render one compact Tower cell from one shared world-space camera.

Each cell is rendered in a fresh Blender process with transparent background so
all ten cells can later be composited without ever loading the full Tower scene
into Blender at once. This is a diagnostic view path, not retail lighting.
"""
from __future__ import annotations

import argparse, json, sys
from pathlib import Path

import bpy
from mathutils import Vector


def cli():
    raw = sys.argv
    args = raw[raw.index('--') + 1:] if '--' in raw else []
    ap = argparse.ArgumentParser()
    ap.add_argument('--glb', type=Path, required=True)
    ap.add_argument('--camera-plan', type=Path, required=True)
    ap.add_argument('--view', required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--report', type=Path, required=True)
    ap.add_argument('--width', type=int, default=1280)
    ap.add_argument('--height', type=int, default=720)
    return ap.parse_args(args)


def look(obj, target):
    d = Vector(target) - obj.location
    if d.length < 1e-8:
        raise RuntimeError('degenerate camera direction')
    obj.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()


def main():
    a = cli()
    plan = json.load(open(a.camera_plan))
    views = {x['name']: x for x in plan.get('views', [])}
    if a.view not in views:
        raise SystemExit(f'view not found: {a.view}')
    view = views[a.view]

    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.report.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(a.glb.resolve()), import_pack_images=False)
    meshes = [o for o in bpy.data.objects if o.type == 'MESH']
    if not meshes:
        raise SystemExit('no mesh objects imported')

    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_WORKBENCH'
    scene.render.resolution_x = a.width
    scene.render.resolution_y = a.height
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.film_transparent = True

    sh = scene.display.shading
    sh.light = 'STUDIO'
    sh.show_shadows = True
    sh.show_cavity = True
    sh.cavity_type = 'BOTH'
    sh.show_specular_highlight = True
    try:
        sh.color_type = 'TEXTURE'
    except Exception:
        sh.color_type = 'MATERIAL'
    try:
        sh.studiolight_rotate_z = .55
    except Exception:
        pass

    world = scene.world or bpy.data.worlds.new('D1_TOWER_LAYER_WORLD')
    scene.world = world
    world.color = (0.02, 0.025, 0.04)

    cd = bpy.data.cameras.new('D1_TOWER_SHARED_CAMERA')
    cam = bpy.data.objects.new('D1_TOWER_SHARED_CAMERA', cd)
    scene.collection.objects.link(cam)
    scene.camera = cam
    cd.sensor_width = 36.0
    cd.clip_start = 0.05
    cd.clip_end = 1000000.0
    cam.location = Vector(view['camera'])
    look(cam, view['target'])
    if view.get('type') == 'ORTHO':
        cd.type = 'ORTHO'
        cd.ortho_scale = float(view['ortho_scale'])
    else:
        cd.type = 'PERSP'
        cd.lens = float(view.get('lens_mm', 50.0))

    cell_num = None
    stem = a.glb.stem
    if stem.startswith('TOWER_CELL_'):
        try:
            cell_num = int(stem.rsplit('_', 1)[1])
        except Exception:
            pass
    center = None
    layer_class = 'core'
    if cell_num is not None:
        for row in plan.get('cell_bounds', []):
            if int(row.get('cell', -1)) == cell_num:
                center = Vector(row['center'])
                layer_class = str(row.get('layer_class', 'core'))
                break
    forward = (Vector(view['target']) - Vector(view['camera'])).normalized()
    sort_depth = None
    if center is not None:
        sort_depth = float((center - Vector(view['camera'])).dot(forward))

    scene.render.filepath = str(a.out.resolve())
    bpy.ops.render.render(write_still=True)
    if not a.out.is_file() or a.out.stat().st_size < 4000:
        raise SystemExit(f'render missing/too small: {a.out}')

    rep = {
        'status': 'D1_TOWER_SHARED_LAYER_RENDER_COMPLETE',
        'cell': cell_num,
        'layer_class': layer_class,
        'source_glb': a.glb.name,
        'view': a.view,
        'output': a.out.name,
        'bytes': a.out.stat().st_size,
        'blender_version': bpy.app.version_string,
        'render_engine': scene.render.engine,
        'color_type': scene.display.shading.color_type,
        'mesh_object_count': len(meshes),
        'material_count': len(bpy.data.materials),
        'image_count': len(bpy.data.images),
        'camera': [float(x) for x in cam.location],
        'target': [float(x) for x in view['target']],
        'camera_type': cd.type,
        'sort_depth': sort_depth,
        'policy': 'Transparent per-cell diagnostic render from a shared Blender-space camera. Retail lighting/camera are not claimed.'
    }
    a.report.write_text(json.dumps(rep, indent=2) + '\n')
    print(json.dumps(rep, indent=2))


if __name__ == '__main__':
    main()
