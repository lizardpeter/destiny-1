#!/usr/bin/env python3
"""Apply the retail-closed D1 Tower 809DCD66 shader family in Blender.

Run inside Blender 4.5+::

    blender --background --python tools/d1_blender_apply_809dcd66.py -- \
      --input-glb tower_with_d1_basis.glb \
      --manifest 809DCD66_blender_adapter_manifest.json \
      --texture-root textures \
      --out-blend tower_809dcd66.blend \
      --report 809dcd66_blender_report.json

The graph replays the exact semantic equations closed from PS4 retail GCN while
keeping unresolved runtime state explicit:

* source ``_D1_NORMAL`` and ``_D1_TANGENT_XYZ`` are transformed Object -> World
  as ordinary VECTORs;
* one reciprocal length from transformed N scales both N and T, matching VS
  80CA0DDA rather than Blender's conventional independently-normalized basis;
* ``B = cross(N,T) * _D1_TANGENT_W``;
* Blender/glTF portable V is the proven ``1-native_v``, therefore the native
  parallax Y displacement changes sign when added to imported TEXCOORD_0;
* t0/t1 red channels feed the exact palette/intensity equation;
* ``api13[6]`` and ``api13[7]`` are visible Value nodes defaulting to the
  manifest's explicitly labelled preview fallbacks (currently 1), never silently
  renamed as engine semantics;
* output is Emission as a Blender preview because D1's native blend/composition
  state is still unresolved. This script does not claim retail framebuffer or
  deferred-renderer equivalence.

Dynamic TFX materials use the exact c6.x sample at abstract native Frame[0]=0.
No Blender-time animation is created until the D1 Frame[0] producer/unit/phase is
closed.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

try:
    import bpy
except Exception as ex:  # pragma: no cover - this file must execute in Blender
    raise SystemExit(f"This tool must run inside Blender Python: {ex!r}")

MAT_RE = re.compile(r"(?:TigerMaterial_|D1_)([0-9A-Fa-f]{8})")
REQUIRED_ATTRS = ("_D1_NORMAL", "_D1_TANGENT_XYZ", "_D1_TANGENT_W")


def cli() -> argparse.Namespace:
    raw = sys.argv
    args = raw[raw.index("--") + 1 :] if "--" in raw else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--input-glb", type=Path, required=True)
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--texture-root", type=Path, required=True)
    ap.add_argument("--out-blend", type=Path, required=True)
    ap.add_argument("--report", type=Path, required=True)
    ap.add_argument("--api13-6", type=float, default=None,
                    help="explicit preview override for unresolved native api13[6]")
    ap.add_argument("--api13-7", type=float, default=None,
                    help="explicit preview override for unresolved native api13[7]")
    return ap.parse_args(args)


def material_hash(name: str) -> str | None:
    m = MAT_RE.search(str(name or ""))
    return m.group(1).upper() if m else None


def input_socket(node, *names):
    for name in names:
        s = node.inputs.get(name)
        if s is not None:
            return s
    raise KeyError(f"{node.bl_idname}: missing input socket {names}; have {[x.name for x in node.inputs]}")


def output_socket(node, *names):
    for name in names:
        s = node.outputs.get(name)
        if s is not None:
            return s
    raise KeyError(f"{node.bl_idname}: missing output socket {names}; have {[x.name for x in node.outputs]}")


def new(nodes, kind: str, name: str, x: float, y: float):
    n = nodes.new(kind)
    n.name = name
    n.label = name
    n.location = (x, y)
    return n


def value(nodes, name: str, v: float, x: float, y: float):
    n = new(nodes, "ShaderNodeValue", name, x, y)
    output_socket(n, "Value").default_value = float(v)
    return n


def combine_xyz(nodes, name: str, xyz, x: float, y: float):
    n = new(nodes, "ShaderNodeCombineXYZ", name, x, y)
    for socket, v in zip(("X", "Y", "Z"), xyz):
        input_socket(n, socket).default_value = float(v)
    return n


def vmath(nodes, op: str, name: str, x: float, y: float):
    n = new(nodes, "ShaderNodeVectorMath", name, x, y)
    n.operation = op
    return n


def mathn(nodes, op: str, name: str, x: float, y: float):
    n = new(nodes, "ShaderNodeMath", name, x, y)
    n.operation = op
    return n


def resolve_image(root: Path, rel: str | None, tag: str) -> Path:
    candidates = []
    if rel:
        rp = Path(rel)
        candidates.extend((root / rp, root / rp.name, root / "textures" / rp.name))
    candidates.extend((root / f"{tag}.png", root / "textures" / f"{tag}.png"))
    seen = set()
    for p in candidates:
        q = p.resolve()
        if q in seen:
            continue
        seen.add(q)
        if q.is_file():
            return q
    raise FileNotFoundError(f"{tag}: exact PNG not found beneath {root}; manifest path={rel!r}")


def load_image(path: Path, tag: str):
    # check_existing gives all target materials one shared datablock per retail
    # texture instead of loading 24 duplicate copies.
    im = bpy.data.images.load(str(path), check_existing=True)
    im.name = f"D1_{tag}_{path.name}"
    # The exact recovered resources are BC1 sRGB. Image Texture's sRGB decode is
    # the closest direct Blender representation of that sampled resource.
    try:
        im.colorspace_settings.name = "sRGB"
    except Exception:
        pass
    return im


def assert_target_mesh_attributes(target_hashes: set[str]) -> dict:
    rows = []
    used = 0
    missing = []
    for obj in bpy.data.objects:
        if obj.type != "MESH" or obj.data is None:
            continue
        hashes = {material_hash(slot.material.name) for slot in obj.material_slots if slot.material}
        hashes.discard(None)
        matched = sorted(hashes & target_hashes)
        if not matched:
            continue
        used += 1
        names = set(obj.data.attributes.keys())
        absent = [x for x in REQUIRED_ATTRS if x not in names]
        if absent:
            missing.append({"object": obj.name, "materials": matched, "missing": absent,
                            "available": sorted(names)})
        rows.append({"object": obj.name, "materials": matched,
                     "vertex_count": len(obj.data.vertices), "attributes": sorted(names)})
    if used == 0:
        raise RuntimeError("no imported mesh objects use the 809DCD66 target materials")
    if missing:
        raise RuntimeError("target meshes lost required D1 application attributes: " + json.dumps(missing[:8]))
    return {"target_mesh_object_count": used, "objects": rows}


def configure_texture_node(nodes, name: str, image, extension: str, x: float, y: float):
    n = new(nodes, "ShaderNodeTexImage", name, x, y)
    n.image = image
    n.interpolation = "Linear"
    n.extension = extension
    return n


def build_material(mat, rec: dict, t0_image, t1_image, api6: float, api7: float) -> dict:
    mat.use_nodes = True
    nt = mat.node_tree
    nodes = nt.nodes
    links = nt.links
    nodes.clear()

    # --- source D1 basis -----------------------------------------------------
    a_n = new(nodes, "ShaderNodeAttribute", "D1_SOURCE_NORMAL", -1500, 520)
    a_n.attribute_type = "GEOMETRY"; a_n.attribute_name = "_D1_NORMAL"
    a_t = new(nodes, "ShaderNodeAttribute", "D1_SOURCE_TANGENT_XYZ", -1500, 310)
    a_t.attribute_type = "GEOMETRY"; a_t.attribute_name = "_D1_TANGENT_XYZ"
    a_w = new(nodes, "ShaderNodeAttribute", "D1_SOURCE_TANGENT_W", -1500, 100)
    a_w.attribute_type = "GEOMETRY"; a_w.attribute_name = "_D1_TANGENT_W"

    n_xf = new(nodes, "ShaderNodeVectorTransform", "D1_N_OBJECT_TO_WORLD_VECTOR", -1260, 520)
    n_xf.vector_type = "VECTOR"; n_xf.convert_from = "OBJECT"; n_xf.convert_to = "WORLD"
    t_xf = new(nodes, "ShaderNodeVectorTransform", "D1_T_OBJECT_TO_WORLD_VECTOR", -1260, 310)
    t_xf.vector_type = "VECTOR"; t_xf.convert_from = "OBJECT"; t_xf.convert_to = "WORLD"
    links.new(output_socket(a_n, "Vector"), input_socket(n_xf, "Vector"))
    links.new(output_socket(a_t, "Vector"), input_socket(t_xf, "Vector"))

    n_len = vmath(nodes, "LENGTH", "D1_LENGTH_NRAW", -1040, 520)
    links.new(output_socket(n_xf, "Vector"), input_socket(n_len, "Vector"))
    inv_n = mathn(nodes, "DIVIDE", "D1_INV_NORMAL_LENGTH", -840, 520)
    input_socket(inv_n, "Value", "Value_001").default_value = 1.0
    # DIVIDE socket ordering is A/B. Set A=1 and link N length to B.
    inv_n.inputs[0].default_value = 1.0
    links.new(output_socket(n_len, "Value"), inv_n.inputs[1])

    N = vmath(nodes, "SCALE", "D1_NATIVE_N", -610, 520)
    T = vmath(nodes, "SCALE", "D1_NATIVE_T_SHARED_INV_N", -610, 310)
    links.new(output_socket(n_xf, "Vector"), input_socket(N, "Vector"))
    links.new(output_socket(inv_n, "Value"), input_socket(N, "Scale"))
    links.new(output_socket(t_xf, "Vector"), input_socket(T, "Vector"))
    links.new(output_socket(inv_n, "Value"), input_socket(T, "Scale"))

    cross = vmath(nodes, "CROSS_PRODUCT", "D1_CROSS_N_T", -390, 210)
    links.new(output_socket(N, "Vector"), cross.inputs[0]); links.new(output_socket(T, "Vector"), cross.inputs[1])
    B = vmath(nodes, "SCALE", "D1_NATIVE_B_CROSS_NT_TIMES_W", -170, 210)
    links.new(output_socket(cross, "Vector"), input_socket(B, "Vector"))
    links.new(output_socket(a_w, "Fac", "Value"), input_socket(B, "Scale"))

    # --- view projection and portable UV conversion -------------------------
    geom = new(nodes, "ShaderNodeNewGeometry", "D1_VIEW_GEOMETRY", -610, -40)
    V = vmath(nodes, "NORMALIZE", "D1_VIEW_TO_CAMERA_NORMALIZED", -390, -40)
    links.new(output_socket(geom, "Incoming"), input_socket(V, "Vector"))

    dot_t = vmath(nodes, "DOT_PRODUCT", "D1_DOT_VIEW_T", 70, 290)
    dot_b = vmath(nodes, "DOT_PRODUCT", "D1_DOT_VIEW_B", 70, 150)
    dot_n = vmath(nodes, "DOT_PRODUCT", "D1_DOT_VIEW_N", 70, 10)
    for dn, basis in ((dot_t, T), (dot_b, B), (dot_n, N)):
        links.new(output_socket(V, "Vector"), dn.inputs[0])
        links.new(output_socket(basis, "Vector"), dn.inputs[1])

    ratio_u = mathn(nodes, "DIVIDE", "D1_TX_DIV_TZ", 280, 290)
    ratio_v = mathn(nodes, "DIVIDE", "D1_TY_DIV_TZ", 280, 150)
    links.new(output_socket(dot_t, "Value"), ratio_u.inputs[0]); links.new(output_socket(dot_n, "Value"), ratio_u.inputs[1])
    links.new(output_socket(dot_b, "Value"), ratio_v.inputs[0]); links.new(output_socket(dot_n, "Value"), ratio_v.inputs[1])

    c4x = float(rec["c4_x_parallax"])
    du = mathn(nodes, "MULTIPLY", "D1_NATIVE_DU_NEG_C4_TX_TZ", 480, 290)
    du.inputs[1].default_value = -c4x; links.new(output_socket(ratio_u, "Value"), du.inputs[0])
    # Native dv=-c4*Ty/Tz, but portable V=1-nativeV, therefore portable offset Y=-dv=+c4*Ty/Tz.
    portable_dy = mathn(nodes, "MULTIPLY", "D1_PORTABLE_DY_POS_C4_TY_TZ", 480, 150)
    portable_dy.inputs[1].default_value = c4x; links.new(output_socket(ratio_v, "Value"), portable_dy.inputs[0])
    uv_offset = new(nodes, "ShaderNodeCombineXYZ", "D1_PORTABLE_PARALLAX_OFFSET", 690, 210)
    links.new(output_socket(du, "Value"), input_socket(uv_offset, "X"))
    links.new(output_socket(portable_dy, "Value"), input_socket(uv_offset, "Y"))

    texcoord = new(nodes, "ShaderNodeTexCoord", "D1_IMPORTED_TEXCOORD_0", 480, -120)
    uv2 = vmath(nodes, "ADD", "D1_PORTABLE_DISPLACED_UV", 900, 70)
    links.new(output_socket(texcoord, "UV"), uv2.inputs[0]); links.new(output_socket(uv_offset, "Vector"), uv2.inputs[1])

    t0 = configure_texture_node(nodes, "D1_T0_8093E9A3_R", t0_image, "REPEAT", 900, -260)
    t1 = configure_texture_node(nodes, "D1_T1_8093E9A2_R_PARALLAX", t1_image, "EXTEND", 1110, 70)
    links.new(output_socket(texcoord, "UV"), input_socket(t0, "Vector"))
    links.new(output_socket(uv2, "Vector"), input_socket(t1, "Vector"))
    sep0 = new(nodes, "ShaderNodeSeparateColor", "D1_T0_RED", 1120, -260); sep0.mode = "RGB"
    sep1 = new(nodes, "ShaderNodeSeparateColor", "D1_T1_RED", 1330, 70); sep1.mode = "RGB"
    links.new(output_socket(t0, "Color"), input_socket(sep0, "Color")); links.new(output_socket(t1, "Color"), input_socket(sep1, "Color"))
    clamp0 = new(nodes, "ShaderNodeClamp", "D1_SATURATE_T0_R", 1330, -260)
    input_socket(clamp0, "Min").default_value = 0.0; input_socket(clamp0, "Max").default_value = 1.0
    links.new(output_socket(sep0, "Red", "R"), input_socket(clamp0, "Value"))

    # --- palette and exact post-sample scalar chain -------------------------
    c2 = combine_xyz(nodes, "D1_C2_PALETTE_BASE", rec["c2_palette_base"][:3], 1120, -520)
    c3 = combine_xyz(nodes, "D1_C3_PALETTE_DELTA", rec["c3_palette_delta"][:3], 1330, -520)
    slope = vmath(nodes, "SCALE", "D1_C3_TIMES_SAT_T0R", 1530, -410)
    links.new(output_socket(c3, "Vector"), input_socket(slope, "Vector")); links.new(output_socket(clamp0, "Result", "Value"), input_socket(slope, "Scale"))
    palette = vmath(nodes, "ADD", "D1_PALETTE_RGB", 1740, -410)
    links.new(output_socket(c2, "Vector"), palette.inputs[0]); links.new(output_socket(slope, "Vector"), palette.inputs[1])

    c5 = combine_xyz(nodes, "D1_C5_RGB_MULTIPLIER", rec["c5_rgb_multiplier"][:3], 1530, -610)
    mul_c5 = vmath(nodes, "MULTIPLY", "D1_RGB_TIMES_C5", 1950, -370)
    links.new(output_socket(palette, "Vector"), mul_c5.inputs[0]); links.new(output_socket(c5, "Vector"), mul_c5.inputs[1])
    mul_t1 = vmath(nodes, "SCALE", "D1_RGB_TIMES_T1_R", 2160, -300)
    links.new(output_socket(mul_c5, "Vector"), input_socket(mul_t1, "Vector")); links.new(output_socket(sep1, "Red", "R"), input_socket(mul_t1, "Scale"))

    c6 = value(nodes, "D1_C6_X_AT_ABSTRACT_FRAME0_ZERO", float(rec["c6_x_at_abstract_frame0_zero"]), 1950, -560)
    g6 = value(nodes, "D1_API13_DWORD6_UNRESOLVED_PREVIEW", api6, 2160, -560)
    g7 = value(nodes, "D1_API13_DWORD7_UNRESOLVED_PREVIEW", api7, 2370, -560)
    mul_c6 = vmath(nodes, "SCALE", "D1_RGB_TIMES_C6", 2370, -250)
    links.new(output_socket(mul_t1, "Vector"), input_socket(mul_c6, "Vector")); links.new(output_socket(c6, "Value"), input_socket(mul_c6, "Scale"))
    mul_g6 = vmath(nodes, "SCALE", "D1_RGB_TIMES_API13_6", 2580, -200)
    links.new(output_socket(mul_c6, "Vector"), input_socket(mul_g6, "Vector")); links.new(output_socket(g6, "Value"), input_socket(mul_g6, "Scale"))
    mul_g7 = vmath(nodes, "SCALE", "D1_RGB_TIMES_API13_7", 2790, -150)
    links.new(output_socket(mul_g6, "Vector"), input_socket(mul_g7, "Vector")); links.new(output_socket(g7, "Value"), input_socket(mul_g7, "Scale"))

    emission = new(nodes, "ShaderNodeEmission", "D1_809DCD66_EMISSION_PREVIEW_BLEND_UNRESOLVED", 3010, -120)
    links.new(output_socket(mul_g7, "Vector"), input_socket(emission, "Color"))
    output = new(nodes, "ShaderNodeOutputMaterial", "D1_MATERIAL_OUTPUT", 3240, -120)
    links.new(output_socket(emission, "Emission"), input_socket(output, "Surface"))

    # Durable proof boundary in the .blend itself.
    mat["d1_vertex_shader"] = rec["vertex_shader"]
    mat["d1_pixel_shader"] = rec["pixel_shader"]
    mat["d1_c2"] = rec["c2_palette_base"]
    mat["d1_c3"] = rec["c3_palette_delta"]
    mat["d1_c4"] = rec["c4"]
    mat["d1_c5"] = rec["c5_rgb_multiplier"]
    mat["d1_serialized_c6"] = rec["serialized_c6"]
    mat["d1_c6_mode"] = rec["c6_mode"]
    mat["d1_c6_frame0_zero"] = float(rec["c6_x_at_abstract_frame0_zero"])
    mat["d1_tfx_expression_x"] = rec["tfx_expression_x"]
    mat["d1_tfx_bytecode_hex"] = rec["tfx_bytecode_hex"]
    mat["d1_api13_6_runtime_source"] = "UNRESOLVED"
    mat["d1_api13_7_runtime_source"] = "UNRESOLVED"
    mat["d1_api13_6_preview_value"] = float(api6)
    mat["d1_api13_7_preview_value"] = float(api7)
    mat["d1_native_blend_state"] = "UNRESOLVED"
    mat["d1_preview_output"] = "EMISSION_ONLY_NOT_NATIVE_BLEND_CLAIM"
    mat["d1_frame0_unit"] = "UNRESOLVED"
    mat["d1_frame0_phase"] = "UNRESOLVED"
    mat["d1_t0_taghash"] = rec["texture_bindings"]["t0"]["taghash"]
    mat["d1_t1_taghash"] = rec["texture_bindings"]["t1"]["taghash"]
    mat["d1_t0_sampler"] = rec["texture_bindings"]["t0"]["sampler"]
    mat["d1_t1_sampler"] = rec["texture_bindings"]["t1"]["sampler"]
    mat["d1_sampler_adapter_note"] = "t0 REPEAT, t1 EXTEND are Blender preview states; native sampler IDs remain authoritative"

    return {
        "material_name": mat.name,
        "material_hash": rec["material"],
        "node_count": len(nodes),
        "c6_mode": rec["c6_mode"],
        "c6_x": float(rec["c6_x_at_abstract_frame0_zero"]),
        "api13_6_preview": float(api6),
        "api13_7_preview": float(api7),
    }


def main() -> int:
    a = cli()
    manifest = json.loads(a.manifest.read_text())
    if manifest.get("status") != "D1_TOWER_809DCD66_BLENDER_ADAPTER_INPUTS_CLOSED":
        raise SystemExit(f"unexpected adapter manifest status: {manifest.get('status')}")
    records = {str(k).upper(): v for k, v in manifest["materials"].items()}
    if len(records) != 24:
        raise SystemExit(f"adapter manifest changed: expected 24 materials, got {len(records)}")

    # Start from an empty file so command-line use is deterministic.
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(a.input_glb.resolve()))

    target_mats = {}
    for mat in bpy.data.materials:
        h = material_hash(mat.name)
        if h in records:
            if h in target_mats:
                raise RuntimeError(f"duplicate imported target material {h}: {target_mats[h].name}, {mat.name}")
            target_mats[h] = mat
    if not target_mats:
        raise RuntimeError("no 809DCD66 materials were found after glTF import")

    mesh_report = assert_target_mesh_attributes(set(target_mats))

    # All 24 records share the same two exact source textures.
    anyrec = next(iter(records.values()))
    t0rec = anyrec["texture_bindings"]["t0"]
    t1rec = anyrec["texture_bindings"]["t1"]
    t0path = resolve_image(a.texture_root, t0rec.get("portable_png"), t0rec["taghash"])
    t1path = resolve_image(a.texture_root, t1rec.get("portable_png"), t1rec["taghash"])
    t0im = load_image(t0path, t0rec["taghash"])
    t1im = load_image(t1path, t1rec["taghash"])

    fallback6 = float(manifest["global_inputs"]["api13_dword6"]["preview_fallback"])
    fallback7 = float(manifest["global_inputs"]["api13_dword7"]["preview_fallback"])
    api6 = fallback6 if a.api13_6 is None else float(a.api13_6)
    api7 = fallback7 if a.api13_7 is None else float(a.api13_7)

    rows = []
    for h, mat in sorted(target_mats.items()):
        rows.append(build_material(mat, records[h], t0im, t1im, api6, api7))

    # File-level provenance remains visible to users/scripts opening the blend.
    scene = bpy.context.scene
    scene["d1_809dcd66_adapter_status"] = "NATIVE_EQUATION_PREVIEW"
    scene["d1_809dcd66_materials_present"] = len(rows)
    scene["d1_809dcd66_manifest_material_count"] = len(records)
    scene["d1_api13_runtime_values"] = "UNRESOLVED; node fallbacks/overrides are explicit"
    scene["d1_native_blend_state"] = "UNRESOLVED"
    scene["d1_frame0_time_unit_phase"] = "UNRESOLVED"

    a.out_blend.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(a.out_blend.resolve()))

    # Re-open the just-written blend in the same process. This catches node/custom
    # property serialization failures before declaring the adapter usable.
    bpy.ops.wm.open_mainfile(filepath=str(a.out_blend.resolve()))
    verified = []
    for row in rows:
        mat = bpy.data.materials.get(row["material_name"])
        if mat is None or not mat.use_nodes:
            raise RuntimeError(f"saved blend lost target material {row['material_name']}")
        names = {n.name for n in mat.node_tree.nodes}
        need = {
            "D1_SOURCE_NORMAL", "D1_SOURCE_TANGENT_XYZ", "D1_SOURCE_TANGENT_W",
            "D1_NATIVE_N", "D1_NATIVE_T_SHARED_INV_N", "D1_NATIVE_B_CROSS_NT_TIMES_W",
            "D1_PORTABLE_DISPLACED_UV", "D1_T0_8093E9A3_R", "D1_T1_8093E9A2_R_PARALLAX",
            "D1_PALETTE_RGB", "D1_API13_DWORD6_UNRESOLVED_PREVIEW",
            "D1_API13_DWORD7_UNRESOLVED_PREVIEW", "D1_809DCD66_EMISSION_PREVIEW_BLEND_UNRESOLVED",
        }
        absent = sorted(need - names)
        if absent:
            raise RuntimeError(f"saved blend material {mat.name} lost adapter nodes: {absent}")
        verified.append(mat.name)

    report = {
        "schema_version": 1,
        "status": "D1_TOWER_809DCD66_BLENDER_NATIVE_EQUATION_PREVIEW_BUILT",
        "blender_version": list(bpy.app.version),
        "blender_version_string": bpy.app.version_string,
        "input_glb": str(a.input_glb),
        "manifest": str(a.manifest),
        "texture_root": str(a.texture_root),
        "output_blend": str(a.out_blend),
        "output_blend_bytes": a.out_blend.stat().st_size,
        "target_materials_in_input": len(rows),
        "manifest_material_count": len(records),
        "verified_saved_material_count": len(verified),
        "mesh_attribute_validation": mesh_report,
        "t0_png": str(t0path),
        "t1_png": str(t1path),
        "api13_6_preview": api6,
        "api13_7_preview": api7,
        "api13_runtime_source_resolved": False,
        "native_blend_state_resolved": False,
        "frame0_time_unit_phase_resolved": False,
        "dynamic_material_policy": "exact c6.x sample at abstract native Frame[0]=0; no guessed Blender time mapping",
        "sampler_policy": "native sampler IDs retained as material properties; Blender REPEAT/EXTEND are preview mappings",
        "render_policy": "Emission output replays closed RGB equation but is not claimed to reproduce unresolved native blend/deferred composition",
        "materials": rows,
    }
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: report[k] for k in (
        "status", "blender_version_string", "target_materials_in_input",
        "verified_saved_material_count", "output_blend_bytes", "api13_6_preview", "api13_7_preview"
    )}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
