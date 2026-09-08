#!/usr/bin/env python3
"""Render deterministic inspection shots from the full D1 Tower Blender scene.

The full inspection .blend deliberately leaves all source-scenario collections
hidden because retail runtime activation is unresolved. This renderer keeps
that proof boundary: clean environment shots hide every scenario, while the
actor shots enable exactly one serialized source-scenario collection and label
that choice only in the JSON report, never as a retail-active claim.

Lighting/cameras are neutral diagnostic choices for visual inspection, not a
reconstruction of Destiny 1 retail lighting or camera state.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector


def cli():
    raw = sys.argv
    args = raw[raw.index("--") + 1 :] if "--" in raw else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--report", type=Path, required=True)
    ap.add_argument("--width", type=int, default=1280)
    ap.add_argument("--height", type=int, default=720)
    return ap.parse_args(args)


def percentile(vals, p):
    xs = sorted(float(x) for x in vals)
    if not xs:
        raise RuntimeError("empty percentile input")
    if len(xs) == 1:
        return xs[0]
    q = (len(xs) - 1) * p
    i = int(math.floor(q))
    j = min(i + 1, len(xs) - 1)
    t = q - i
    return xs[i] * (1.0 - t) + xs[j] * t


def collection_recursive_objects(coll):
    seen = set()
    out = []
    stack = [coll]
    while stack:
        c = stack.pop()
        for o in c.objects:
            if o.name not in seen:
                seen.add(o.name)
                out.append(o)
        stack.extend(list(c.children))
    return out


def scenario_collections():
    rows = []
    for c in bpy.data.collections:
        if c.name.startswith("D1_SCENARIO_") and c.name.endswith("_SOURCE_ALTERNATIVES"):
            rows.append(c)
    rows.sort(key=lambda c: (int(c.get("d1PlacementAlternativeCount", 1 << 30)), c.name))
    return rows


def set_scenarios_hidden(hidden=True):
    for c in scenario_collections():
        c.hide_viewport = hidden
        c.hide_render = hidden


def scenario_positions(coll):
    pts = []
    for o in collection_recursive_objects(coll):
        if o.type == "EMPTY" and o.instance_type == "COLLECTION" and o.instance_collection is not None:
            p = o.matrix_world.translation
            if all(math.isfinite(v) for v in p):
                pts.append(Vector((p.x, p.y, p.z)))
    return pts


def robust_frame_from_points(pts):
    if len(pts) < 3:
        raise RuntimeError(f"not enough placement points: {len(pts)}")
    xs = [p.x for p in pts]
    ys = [p.y for p in pts]
    zs = [p.z for p in pts]
    x0, x1 = percentile(xs, 0.05), percentile(xs, 0.95)
    y0, y1 = percentile(ys, 0.05), percentile(ys, 0.95)
    z0, z1 = percentile(zs, 0.10), percentile(zs, 0.90)
    center = Vector(((x0 + x1) * 0.5, (y0 + y1) * 0.5, percentile(zs, 0.45)))
    span = max(x1 - x0, y1 - y0, 4.0)
    zspan = max(z1 - z0, 2.0)
    return center, span, zspan, {"x05": x0, "x95": x1, "y05": y0, "y95": y1, "z10": z0, "z90": z1}


def densest_point(pts, span):
    radius = max(span * 0.14, 4.0)
    r2 = radius * radius
    best = None
    best_n = -1
    for p in pts:
        n = 0
        sx = sy = sz = 0.0
        for q in pts:
            dx, dy = q.x - p.x, q.y - p.y
            if dx * dx + dy * dy <= r2:
                n += 1
                sx += q.x
                sy += q.y
                sz += q.z
        if n > best_n:
            best_n = n
            best = Vector((sx / n, sy / n, sz / n))
    return best, best_n, radius


def look_at(obj, target):
    direction = Vector(target) - obj.location
    if direction.length < 1e-6:
        raise RuntimeError("camera direction is degenerate")
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def ensure_camera():
    cam_data = bpy.data.cameras.get("D1_INSPECTION_CAMERA") or bpy.data.cameras.new("D1_INSPECTION_CAMERA")
    cam = bpy.data.objects.get("D1_INSPECTION_CAMERA") or bpy.data.objects.new("D1_INSPECTION_CAMERA", cam_data)
    if cam.name not in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.link(cam)
    cam.data.lens = 35.0
    cam.data.sensor_width = 36.0
    cam.data.clip_start = 0.05
    cam.data.clip_end = 100000.0
    bpy.context.scene.camera = cam
    return cam


def ensure_lights(center, span):
    for name in ("D1_INSPECTION_SUN", "D1_INSPECTION_FILL"):
        o = bpy.data.objects.get(name)
        if o is not None:
            bpy.data.objects.remove(o, do_unlink=True)

    sun_data = bpy.data.lights.new("D1_INSPECTION_SUN", type="SUN")
    sun_data.energy = 2.0
    sun_data.angle = math.radians(18.0)
    sun = bpy.data.objects.new("D1_INSPECTION_SUN", sun_data)
    bpy.context.scene.collection.objects.link(sun)
    sun.rotation_euler = (math.radians(34), math.radians(-18), math.radians(-32))

    area_data = bpy.data.lights.new("D1_INSPECTION_FILL", type="AREA")
    area_data.energy = max(2500.0, span * span * 5.0)
    area_data.shape = "DISK"
    area_data.size = max(span * 0.8, 20.0)
    area = bpy.data.objects.new("D1_INSPECTION_FILL", area_data)
    bpy.context.scene.collection.objects.link(area)
    area.location = (center.x, center.y, center.z + max(span * 0.55, 20.0))
    look_at(area, center)

    world = bpy.context.scene.world or bpy.data.worlds.new("D1_INSPECTION_WORLD")
    bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg is not None:
        bg.inputs["Color"].default_value = (0.055, 0.065, 0.085, 1.0)
        bg.inputs["Strength"].default_value = 0.65


def configure_render(a):
    s = bpy.context.scene
    s.render.engine = "BLENDER_EEVEE_NEXT"
    s.render.resolution_x = a.width
    s.render.resolution_y = a.height
    s.render.resolution_percentage = 100
    s.render.image_settings.file_format = "PNG"
    s.render.image_settings.color_mode = "RGBA"
    s.render.film_transparent = False
    try:
        s.render.image_settings.color_depth = "8"
    except Exception:
        pass
    try:
        s.view_settings.look = "AgX - Medium High Contrast"
    except Exception:
        pass


def render(path, camera, pos, target, lens):
    camera.location = Vector(pos)
    camera.data.lens = float(lens)
    look_at(camera, Vector(target))
    bpy.context.scene.render.filepath = str(path.resolve())
    bpy.ops.render.render(write_still=True)
    if not path.is_file() or path.stat().st_size < 1024:
        raise RuntimeError(f"render missing/too small: {path}")
    return {
        "file": path.name,
        "bytes": path.stat().st_size,
        "camera": [float(x) for x in camera.location],
        "target": [float(x) for x in target],
        "lens_mm": float(lens),
    }


def main():
    a = cli()
    a.out_dir.mkdir(parents=True, exist_ok=True)
    a.report.parent.mkdir(parents=True, exist_ok=True)

    env = bpy.data.collections.get("D1_TOWER_ENVIRONMENT_CARD_FIXED")
    if env is None:
        raise SystemExit("full Tower environment collection is missing")
    scenarios = scenario_collections()
    if len(scenarios) != 8:
        raise SystemExit(f"expected 8 scenario collections, found {len(scenarios)}")

    chosen = scenarios[0]
    pts = scenario_positions(chosen)
    center, span, zspan, bounds = robust_frame_from_points(pts)
    dense, dense_n, dense_radius = densest_point(pts, span)

    configure_render(a)
    cam = ensure_camera()
    ensure_lights(center, span)
    set_scenarios_hidden(True)

    target = center + Vector((0.0, 0.0, max(zspan * 0.05, 1.0)))
    d = span * 1.18
    h = max(span * 0.34, zspan * 1.8, 12.0)

    shots = []
    shots.append(render(a.out_dir / "01_tower_wide_environment.png", cam, center + Vector((d * 0.78, -d, h)), target, 38.0))
    shots[-1]["actors_visible"] = False

    shots.append(render(a.out_dir / "02_tower_opposite_environment.png", cam, center + Vector((-d, d * 0.62, h * 0.88)), target, 40.0))
    shots[-1]["actors_visible"] = False

    chosen.hide_viewport = False
    chosen.hide_render = False

    shots.append(render(a.out_dir / "03_tower_wide_with_source_actors.png", cam, center + Vector((d * 0.68, -d * 0.92, h * 0.78)), target, 42.0))
    shots[-1]["actors_visible"] = True

    local_span = max(dense_radius * 2.2, span * 0.24, 10.0)
    actor_target = dense + Vector((0.0, 0.0, 1.5))
    shots.append(render(a.out_dir / "04_tower_actor_cluster.png", cam, dense + Vector((local_span * 0.80, -local_span, max(local_span * 0.32, 5.5))), actor_target, 52.0))
    shots[-1]["actors_visible"] = True

    rep = {
        "status": "D1_TOWER_RENDERED_INSPECTION_SHOTS_COMPLETE",
        "blender_version": bpy.app.version_string,
        "render_engine": bpy.context.scene.render.engine,
        "resolution": [a.width, a.height],
        "environment_collection": env.name,
        "scenario_collection_count": len(scenarios),
        "inspection_source_scenario": chosen.name,
        "inspection_source_scenario_hash": str(chosen.get("d1ScenarioHash", "")),
        "inspection_source_scenario_placement_alternatives": int(chosen.get("d1PlacementAlternativeCount", len(pts))),
        "runtime_active_scenario_selected": False,
        "runtime_actor_animation_state_selected": False,
        "placement_point_count_used_for_framing": len(pts),
        "robust_frame_center": [float(x) for x in center],
        "robust_frame_span": float(span),
        "robust_frame_zspan": float(zspan),
        "robust_frame_bounds": bounds,
        "densest_actor_cluster_center": [float(x) for x in dense],
        "densest_actor_cluster_count": int(dense_n),
        "densest_actor_cluster_radius": float(dense_radius),
        "lighting_policy": "Neutral diagnostic sun/fill/world lighting; not retail Destiny 1 lighting.",
        "shots": shots,
    }
    a.report.write_text(json.dumps(rep, indent=2) + "\n")
    print(json.dumps(rep, indent=2))


if __name__ == "__main__":
    main()
