#!/usr/bin/env python3
"""Build a Blender-native Xur master from the calibrated exact-resource carrier.

This is deliberately fail-closed:
- geometry/skin/267 actions are imported unchanged from the carrier;
- native material -> PS -> t# texture bindings come from glTF extras;
- only source-closed PS semantics choose visible texture inputs;
- unresolved full native equations are marked as proxies instead of guessed PBR;
- the known 80876579 control texture is never exposed as visible RGB.

The result is a Blender authoring/inspection master, not a claim that the still-open
D1 runtime external-material evaluator (E6/E7/E8) has been source-closed.
"""
from __future__ import annotations

import argparse, hashlib, json, math, struct, sys
from pathlib import Path

import bpy
from mathutils import Vector

DIRECT_T0 = {"8087688C", "80AADCB3", "80AAE1C7", "80876EDF", "808764AA", "808768B7", "80A08C16"}
PRODUCT_T0_T1 = {"80876575", "808768C0", "80876952"}
PALETTE_T1 = {"80876579"}

SEMANTIC_CLASS = {
    "8087688C": "direct_rgb_bc5_normal",
    "80AADCB3": "direct_rgb_bc5_normal_alpha_pack",
    "80AAE1C7": "direct_rgb_bc5_normal_native_w_pack",
    "80876EDF": "direct_rgb_bc5_normal_pack_modulated",
    "808764AA": "normal_reflected_cube_surface",
    "808768B7": "masked_surface_reflection_normal",
    "80A08C16": "masked_surface_reflection_normal",
    "80876575": "masked_product_surface_reflection_normal",
    "808768C0": "dual_normal_reflected_cube_fresnel_detail",
    "80876952": "detail_normal_reflection_cube_surface",
    "80876579": "control_palette_surface_reflection",
}

def cli():
    raw=sys.argv
    argv=raw[raw.index("--")+1:] if "--" in raw else []
    ap=argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--preview", type=Path, required=True)
    ap.add_argument("--report", type=Path, required=True)
    return ap.parse_args(argv)

def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(8<<20), b""): h.update(b)
    return h.hexdigest()

def glb_json(path: Path) -> dict:
    raw=path.read_bytes()
    if raw[:4] != b"glTF": raise RuntimeError("input is not GLB")
    n,t=struct.unpack_from("<II", raw, 12)
    if t != 0x4E4F534A: raise RuntimeError("GLB missing JSON chunk")
    return json.loads(raw[20:20+n].decode("utf-8").rstrip(" \t\r\n\0"))

def mat_meta(doc: dict) -> dict[str,dict]:
    out={}
    for m in doc.get("materials") or []:
        ex=m.get("extras") or {}
        tag=str(ex.get("d1_material_taghash") or "").upper()
        if tag:
            out[tag]={
                "name":m.get("name"),
                "tag":tag,
                "vs":str(ex.get("d1_vertex_shader") or "").upper(),
                "ps":str(ex.get("d1_pixel_shader") or "").upper(),
                "bindings":list(ex.get("d1_native_texture_bindings") or []),
            }
    return out

def find_imported_material(tag: str):
    exact=f"D1_{tag}"
    hit=bpy.data.materials.get(exact)
    if hit: return hit
    hits=[m for m in bpy.data.materials if tag in m.name.upper()]
    if len(hits)==1: return hits[0]
    raise RuntimeError(f"{tag}: imported material not uniquely found: {[m.name for m in hits]}")

def find_image(tag: str, derived=False):
    prefix=("D1_DERIVED_NORMAL_" if derived else "D1_TEXTURE_")+tag.upper()
    im=bpy.data.images.get(prefix)
    if im: return im
    hits=[x for x in bpy.data.images if x.name==prefix or x.name.startswith(prefix+".")]
    return hits[0] if len(hits)==1 else None

def ps_binding(meta: dict, slot: int):
    for b in meta["bindings"]:
        if str(b.get("stage") or "").lower()=="ps" and int(b.get("t",-1))==slot:
            return str(b.get("taghash") or "").upper()
    return None

def clear_nodes(mat):
    mat.use_nodes=True
    nodes=mat.node_tree.nodes
    nodes.clear()
    out=nodes.new("ShaderNodeOutputMaterial"); out.name="D1_NATIVE_OUTPUT"; out.location=(780,60)
    bsdf=nodes.new("ShaderNodeBsdfPrincipled"); bsdf.name="D1_NATIVE_PORTABLE_CLOSURE"; bsdf.location=(500,60)
    bsdf.inputs["Metallic"].default_value=0.0
    bsdf.inputs["Roughness"].default_value=0.58
    mat.node_tree.links.new(bsdf.outputs["BSDF"],out.inputs["Surface"])
    return bsdf

def tex_node(mat, tag, name, x, y, noncolor=False):
    im=find_image(tag)
    if im is None: return None
    if noncolor:
        try: im.colorspace_settings.name="Non-Color"
        except Exception: pass
    n=mat.node_tree.nodes.new("ShaderNodeTexImage")
    n.name=name; n.label=name; n.image=im; n.location=(x,y); n.interpolation="Linear"
    return n

def normal_node(mat, tag, x=-350, y=-300):
    # Prefer the binder's deterministic BC5->portable-normal derivation when present.
    im=find_image(tag, derived=True)
    if im is None: return None
    try: im.colorspace_settings.name="Non-Color"
    except Exception: pass
    t=mat.node_tree.nodes.new("ShaderNodeTexImage")
    t.name=f"D1_DERIVED_NORMAL_{tag}"; t.image=im; t.location=(x,y)
    n=mat.node_tree.nodes.new("ShaderNodeNormalMap")
    n.name=f"D1_NATIVE_BC5_NORMAL_{tag}"; n.location=(20,y)
    mat.node_tree.links.new(t.outputs["Color"],n.inputs["Color"])
    return n

def multiply_rgb(mat, a, b, name, x=120, y=120):
    n=mat.node_tree.nodes.new("ShaderNodeMixRGB")
    n.blend_type="MULTIPLY"; n.inputs[0].default_value=1.0; n.name=name; n.label=name; n.location=(x,y)
    mat.node_tree.links.new(a.outputs["Color"],n.inputs[1])
    mat.node_tree.links.new(b.outputs["Color"],n.inputs[2])
    return n

def build_material(meta:dict, mat):
    ps=meta["ps"]; bsdf=clear_nodes(mat); links=mat.node_tree.links
    t0=ps_binding(meta,0); t1=ps_binding(meta,1); t2=ps_binding(meta,2); t3=ps_binding(meta,3)
    status="UNRESOLVED_FAIL_CLOSED"
    visible_tag=None

    if ps in DIRECT_T0 and t0:
        n0=tex_node(mat,t0,"D1_INSTRUCTION_PROVEN_SURFACE_T0",-650,180)
        if n0:
            links.new(n0.outputs["Color"],bsdf.inputs["Base Color"])
            visible_tag=t0
            status="SOURCE_CLOSED_SURFACE_INPUT_PROXY"
        normal_tag=t1
        if normal_tag:
            nn=normal_node(mat,normal_tag)
            if nn: links.new(nn.outputs["Normal"],bsdf.inputs["Normal"])

    elif ps in PRODUCT_T0_T1 and t0 and t1:
        a=tex_node(mat,t0,"D1_INSTRUCTION_PROVEN_SURFACE_T0",-700,220)
        b=tex_node(mat,t1,"D1_INSTRUCTION_PROVEN_SURFACE_T1",-700,20)
        if a and b:
            mul=multiply_rgb(mat,a,b,"D1_NATIVE_SURFACE_PRODUCT")
            links.new(mul.outputs["Color"],bsdf.inputs["Base Color"])
            visible_tag=f"{t0}*{t1}"
            status="SOURCE_CLOSED_SURFACE_PRODUCT_PROXY"
        # These families use dual/detail normals; use the first exact normal contributor
        # only when a derived portable normal exists and mark this as incomplete.
        normal_tag=t2
        if normal_tag:
            nn=normal_node(mat,normal_tag)
            if nn: links.new(nn.outputs["Normal"],bsdf.inputs["Normal"])

    elif ps in PALETTE_T1 and t1:
        # Native proof: t0 is RGB control/palette data, never direct visible color.
        # Full palette reconstruction needs material/runtime constants not preserved in
        # this carrier, so use only the proven surface atlas and fail closed on palette.
        n1=tex_node(mat,t1,"D1_PROVEN_SURFACE_ATLAS_T1",-650,180)
        if n1:
            links.new(n1.outputs["Color"],bsdf.inputs["Base Color"])
            visible_tag=t1
            status="PROVEN_SURFACE_ATLAS_PALETTE_CONSTANTS_PENDING"
        mat["d1_forbidden_visible_texture_t0"]=t0 or ""
        mat["d1_80876579_control_texture_never_basecolor"]=True

    else:
        bsdf.inputs["Base Color"].default_value=(0.18,0.18,0.18,1.0)
        bsdf.inputs["Roughness"].default_value=0.72

    mat["d1_material_taghash"]=meta["tag"]
    mat["d1_vertex_shader"]=meta["vs"]
    mat["d1_pixel_shader"]=ps
    mat["d1_native_semantic_class"]=SEMANTIC_CLASS.get(ps,"UNRESOLVED")
    mat["d1_blender_recreation_status"]=status
    mat["d1_visible_source"]=visible_tag or ""
    mat["d1_full_native_equation_claimed"]=False
    mat["d1_runtime_permutation_selection_claimed"]=False
    return status

def upright_root(imported):
    root=bpy.data.objects.new("XUR_D1_TO_BLENDER_ROOT",None)
    bpy.context.scene.collection.objects.link(root)
    roots=[o for o in imported if o.parent not in set(imported)]
    for o in roots:
        mw=o.matrix_world.copy(); o.parent=root; o.matrix_world=mw
    root.rotation_mode="XYZ"; root.rotation_euler.x=-math.pi/2
    root["d1_basis_adapter"]="GLTF_IMPORT_PLUS_90X_THEN_ROOT_NEG_90X"
    return root

def stage_camera():
    meshes=[o for o in bpy.context.scene.objects if o.type=="MESH"]
    pts=[o.matrix_world@Vector(c) for o in meshes for c in o.bound_box]
    if not pts: raise RuntimeError("no Xur meshes")
    mn=Vector((min(p.x for p in pts),min(p.y for p in pts),min(p.z for p in pts)))
    mx=Vector((max(p.x for p in pts),max(p.y for p in pts),max(p.z for p in pts)))
    c=(mn+mx)*0.5; e=max((mx-mn).length,1.0)
    world=bpy.data.worlds.new("XUR_PREVIEW_WORLD"); world.use_nodes=True
    bg=world.node_tree.nodes.get("Background"); bg.inputs["Color"].default_value=(0.018,0.021,0.027,1); bg.inputs["Strength"].default_value=0.22
    bpy.context.scene.world=world
    for name,off,energy,size in [
        ("XUR_KEY",(-0.6,-0.7,0.8),950,0.45),
        ("XUR_FILL",(0.7,-0.2,0.2),500,0.35),
        ("XUR_RIM",(0.2,0.7,0.6),1100,0.30),
    ]:
        ld=bpy.data.lights.new(name,"AREA"); ld.energy=energy; ld.shape="DISK"; ld.size=e*size
        lo=bpy.data.objects.new(name,ld); lo.location=c+Vector(off)*e
        lo.rotation_euler=(c-lo.location).to_track_quat("-Z","Y").to_euler()
        bpy.context.scene.collection.objects.link(lo)
    cd=bpy.data.cameras.new("XUR_PREVIEW_CAMERA"); cam=bpy.data.objects.new("XUR_PREVIEW_CAMERA",cd)
    bpy.context.scene.collection.objects.link(cam); cam.location=c+Vector((0,-1.35,0.10))*e
    cam.rotation_euler=(c-cam.location).to_track_quat("-Z","Y").to_euler(); cd.lens=62
    bpy.context.scene.camera=cam

def main():
    a=cli(); doc=glb_json(a.input); metadata=mat_meta(doc)
    if len(metadata)!=54: raise RuntimeError(f"expected 54 exact Xur materials, got {len(metadata)}")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    before=set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(a.input.resolve()), import_pack_images=True)
    imported=[o for o in bpy.data.objects if o not in before]
    arms=[o for o in imported if o.type=="ARMATURE"]
    if len(arms)!=1: raise RuntimeError(f"expected one Xur armature, got {len(arms)}")
    root=upright_root(imported)
    root["d1_identity"]="Xur/46C55854/80C88CEF"
    root["d1_material_selection"]="CORPUS_CALIBRATED_VISUAL_ADAPTER"
    root["d1_E6_E7_E8_live_selection_proven"]=False

    rows=[]; counts={}
    for tag,meta in sorted(metadata.items()):
        mat=find_imported_material(tag)
        st=build_material(meta,mat)
        counts[st]=counts.get(st,0)+1
        rows.append({"material":tag,"vs":meta["vs"],"ps":meta["ps"],"semantic_class":SEMANTIC_CLASS.get(meta["ps"],"UNRESOLVED"),"status":st})

    # Preserve all imported selector-owned actions. Do not invent retail idle/default.
    actions=list(bpy.data.actions)
    for act in actions: act.use_fake_user=True
    bpy.context.scene["d1_selector_owned_action_count"]=len(actions)
    bpy.context.scene["d1_runtime_default_action_selected"]=False
    bpy.context.scene["d1_native_material_semantics_fail_closed"]=True
    bpy.context.scene["d1_full_retail_equivalence_claimed"]=False

    readme=bpy.data.texts.new("XUR_NATIVE_MASTER_README")
    readme.write("Xur native-semantic Blender master.\n")
    readme.write("Geometry/skin/actions come from the calibrated 80C88CEF carrier.\n")
    readme.write("Material nodes use only instruction-proven visible surface inputs.\n")
    readme.write("80876579 t0 control data is explicitly forbidden from visible base color.\n")
    readme.write("Full reflection/palette/runtime-global equations remain marked pending where inputs are not carrier-resident.\n")
    readme.write("The corpus-calibrated external-material choice is an adapter; E6/E7/E8 retail live selection is still unproven.\n")

    stage_camera()
    sc=bpy.context.scene
    try: sc.render.engine="BLENDER_EEVEE_NEXT"
    except Exception: pass
    sc.render.resolution_x=900; sc.render.resolution_y=1200; sc.render.resolution_percentage=100
    sc.render.image_settings.file_format="PNG"; sc.render.filepath=str(a.preview.resolve())
    sc.frame_start=1; sc.frame_end=1; sc.frame_set(1)
    for im in bpy.data.images:
        if im.source=="FILE" and im.packed_file is None:
            try: im.pack()
            except Exception: pass
    a.output.parent.mkdir(parents=True,exist_ok=True); a.preview.parent.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(a.output.resolve()))
    bpy.ops.render.render(write_still=True)

    rep={
        "schema_version":1,
        "status":"D1_XUR_BLENDER_NATIVE_MASTER_V1_COMPLETE",
        "input":str(a.input),"input_sha256":sha256(a.input),
        "output":str(a.output),"output_sha256":sha256(a.output),"output_bytes":a.output.stat().st_size,
        "preview":str(a.preview),"preview_sha256":sha256(a.preview),
        "material_count":len(metadata),"action_count":len(actions),"armature_count":len(arms),
        "material_status_counts":counts,"materials":rows,
        "basis_adapter":"native D1 Z-up payload -> Blender glTF import -> root -90deg X",
        "runtime_material_selection_proven":False,
        "runtime_default_action_selected":False,
        "full_native_equation_claimed":False,
        "policy":"Fail-closed Blender reconstruction. Source-closed shader semantics choose visible inputs; unresolved runtime/global/palette/reflection portions are labeled rather than guessed."
    }
    a.report.parent.mkdir(parents=True,exist_ok=True); a.report.write_text(json.dumps(rep,indent=2)+"\n")
    print(json.dumps({k:rep[k] for k in ["status","material_count","action_count","material_status_counts","output_sha256","preview_sha256"]},indent=2))

if __name__=="__main__": main()
