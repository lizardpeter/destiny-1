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

import argparse, hashlib, json, math, struct, sys, tempfile
from pathlib import Path

import bpy
from mathutils import Vector

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import d1_blender_build_tower_three_npc_test_v4 as posev4

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from d1_gltf_layer_merge import read_glb as read_glb_exact

DIRECT_T0 = {
    "8087688C", "80AADCB3", "80AAE1C7", "80876EDF", "808764AA",
    "808768B7", "80A08C16",
    # Later three-NPC native/current-state proofs reused by exact shader header.
    "8087645C", "80876566", "8087656E", "80AA8E93", "808768AF",
}
PRODUCT_T0_T1 = {
    "80876575", "808768C0", "80876952",
    "8087656A", "80876537", "809D8351",
}
PALETTE_T1 = {"80876579", "808762E1", "80876577"}
SCALAR_MOD_T0_T2 = {"8087630D", "809D8370"}
SUBTRACT_MASK_T0_T1 = {"809D836C"}
CONSTANT_BLACK = {"80AAE185", "8087688E"}

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
    "808762E1": "control_palette_surface",
    "8087645C": "surface_reflection_detail",
    "80876566": "constant_tinted_surface",
    "80876577": "three_branch_palette_surface_reflection",
    "8087656A": "product_surface_reflection_dual_normal",
    "8087656E": "constant_tinted_masked_surface",
    "80876537": "product_surface_dual_normal",
    "80AAE185": "constant_rgb_exact",
    "8087688E": "constant_rgb_exact_current_black",
    "80AA8E93": "surface_plus_cube",
    "808768AF": "direct_texture_rgb_exact",
    "8087630D": "surface_scalar_view_tint",
    "809D8370": "surface_scalar_view_tint",
    "809D836C": "subtractive_mask_surface_view_tint",
    "809D8351": "product_surface_palette_mask",
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

def hydrate_embedded_native_images(path: Path, doc: dict) -> tuple[int,int]:
    """Hydrate exact binder-owned PNG resources omitted by Blender's glTF import."""
    parsed,bin_data=read_glb_exact(path)
    if len(parsed.get("images") or [])!=len(doc.get("images") or []):
        raise RuntimeError("GLB image count changed between parsers")
    loaded=0
    skipped_unmarked=0
    with tempfile.TemporaryDirectory(prefix="xur_native_images_") as td:
        td=Path(td)
        for ii,img in enumerate(doc.get("images") or []):
            name=str(img.get("name") or "")
            ex=img.get("extras") or {}
            exact_native=ex.get("d1_native_texture_resource") is True
            derived_normal=ex.get("d1_derived_portable_normal") is True
            if not (exact_native or derived_normal):
                skipped_unmarked+=1
                continue
            if bpy.data.images.get(name) is not None or any(x.name.startswith(name+".") for x in bpy.data.images):
                continue
            if img.get("mimeType")!="image/png" or "bufferView" not in img:
                raise RuntimeError(f"{name}: binder-owned image is not embedded image/png")
            bv=(doc.get("bufferViews") or [])[int(img["bufferView"])]
            off=int(bv.get("byteOffset",0)); size=int(bv["byteLength"])
            payload=bin_data[off:off+size]
            if len(payload)!=size or not payload.startswith(bytes.fromhex("89504e470d0a1a0a")):
                raise RuntimeError(f"{name}: binder-owned payload is not PNG at BIN {off}+{size}; first16={payload[:16].hex()}")
            expected=ex.get("d1_embedded_png_sha256") or ex.get("d1_png_sha256")
            got=hashlib.sha256(payload).hexdigest()
            if expected and got!=expected:
                raise RuntimeError(f"{name}: embedded PNG SHA mismatch {got} != {expected}")
            tmp=td/f"{ii:04d}.png"; tmp.write_bytes(payload)
            im=bpy.data.images.load(str(tmp),check_existing=False)
            im.name=name
            im.pack()
            loaded+=1
    del bin_data
    return loaded,skipped_unmarked

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

def rgb_const(mat, rgb, name, x=-500, y=0):
    n=mat.node_tree.nodes.new("ShaderNodeRGB")
    n.name=name; n.label=name; n.location=(x,y)
    n.outputs["Color"].default_value=(float(rgb[0]),float(rgb[1]),float(rgb[2]),1.0)
    return n

def multiply_color_sockets(mat, a, b, name, x=0, y=0):
    n=mat.node_tree.nodes.new("ShaderNodeMixRGB")
    n.blend_type="MULTIPLY"; n.inputs[0].default_value=1.0
    n.name=name; n.label=name; n.location=(x,y)
    mat.node_tree.links.new(a,n.inputs[1]); mat.node_tree.links.new(b,n.inputs[2])
    return n

def mix_color_sockets(mat, fac, a, b, name, x=0, y=0):
    n=mat.node_tree.nodes.new("ShaderNodeMixRGB")
    n.blend_type="MIX"; n.name=name; n.label=name; n.location=(x,y)
    mat.node_tree.links.new(fac,n.inputs[0]); mat.node_tree.links.new(a,n.inputs[1]); mat.node_tree.links.new(b,n.inputs[2])
    return n

def channel_socket(mat, texture_node, channel, name, x=-180, y=0):
    sep=mat.node_tree.nodes.new("ShaderNodeSeparateColor")
    sep.name=name; sep.label=name; sep.location=(x,y)
    mat.node_tree.links.new(texture_node.outputs["Color"],sep.inputs["Color"])
    return sep.outputs[channel]

def scaled_color(mat, color_socket, rgb, name, x=0, y=0):
    k=rgb_const(mat,rgb,name+"_K",x-220,y-80)
    return multiply_color_sockets(mat,color_socket,k.outputs["Color"],name,x,y)

def build_three_branch_palette_surface(mat, tags, palette_a, palette_b, palette_c, scale, name_prefix):
    # Native current-state form used by 808762E1 / 80876577:
    # A=t2*4*Pa, B=t3*4*Pb, C=t4*4*Pc (all current P<0.25);
    # P1=lerp(1,A,t0.r); P2=lerp(P1,B,t0.g); P3=lerp(P2,C,t5.b);
    # Cs=scale*t1.rgb*P3.
    t0,t1,t2,t3,t4,t5=tags
    ns=[
        tex_node(mat,t0,name_prefix+"_CONTROL_T0",-1100,300,noncolor=True),
        tex_node(mat,t1,name_prefix+"_SURFACE_T1",-1100,100),
        tex_node(mat,t2,name_prefix+"_PALETTE_A_T2",-1100,-100),
        tex_node(mat,t3,name_prefix+"_PALETTE_B_T3",-1100,-300),
        tex_node(mat,t4,name_prefix+"_PALETTE_C_T4",-1100,-500),
        tex_node(mat,t5,name_prefix+"_CONTROL_T5",-1100,-700,noncolor=True),
    ]
    if any(x is None for x in ns): return None
    n0,n1,n2,n3,n4,n5=ns
    A=scaled_color(mat,n2.outputs["Color"],tuple(4*x for x in palette_a),name_prefix+"_A",-700,-100)
    B=scaled_color(mat,n3.outputs["Color"],tuple(4*x for x in palette_b),name_prefix+"_B",-700,-300)
    C=scaled_color(mat,n4.outputs["Color"],tuple(4*x for x in palette_c),name_prefix+"_C",-700,-500)
    white=rgb_const(mat,(1,1,1),name_prefix+"_WHITE",-700,300)
    r=channel_socket(mat,n0,"Red",name_prefix+"_T0_R",-850,420)
    g=channel_socket(mat,n0,"Green",name_prefix+"_T0_G",-850,340)
    b=channel_socket(mat,n5,"Blue",name_prefix+"_T5_B",-850,-680)
    p1=mix_color_sockets(mat,r,white.outputs["Color"],A.outputs["Color"],name_prefix+"_P1",-390,220)
    p2=mix_color_sockets(mat,g,p1.outputs["Color"],B.outputs["Color"],name_prefix+"_P2",-150,120)
    p3=mix_color_sockets(mat,b,p2.outputs["Color"],C.outputs["Color"],name_prefix+"_P3",90,20)
    surf=multiply_color_sockets(mat,n1.outputs["Color"],p3.outputs["Color"],name_prefix+"_SURFACE",300,120)
    return scaled_color(mat,surf.outputs["Color"],(scale,scale,scale),name_prefix+"_SCALED",500,120)

def scalar_rgb(mat, texture_node, channel="Red", invert=False, name="D1_SCALAR", x=-120, y=-80):
    sep=mat.node_tree.nodes.new("ShaderNodeSeparateColor")
    sep.name=name+"_SEPARATE"; sep.label=sep.name; sep.location=(x,y)
    mat.node_tree.links.new(texture_node.outputs["Color"], sep.inputs["Color"])
    source=sep.outputs[channel]
    if invert:
        inv=mat.node_tree.nodes.new("ShaderNodeMath")
        inv.operation="SUBTRACT"; inv.name=name+"_ONE_MINUS"; inv.label=inv.name; inv.location=(x+180,y)
        inv.inputs[0].default_value=1.0
        mat.node_tree.links.new(source, inv.inputs[1])
        source=inv.outputs[0]
    comb=mat.node_tree.nodes.new("ShaderNodeCombineColor")
    comb.name=name+"_RGB"; comb.label=comb.name; comb.location=(x+360,y)
    for socket in ("Red","Green","Blue"):
        mat.node_tree.links.new(source, comb.inputs[socket])
    return comb

def math_binary(mat, op, a, b=None, value_b=None, name="D1_MATH", x=0, y=0):
    n=mat.node_tree.nodes.new("ShaderNodeMath")
    n.operation=op; n.name=name; n.label=name; n.location=(x,y)
    mat.node_tree.links.new(a,n.inputs[0])
    if b is not None: mat.node_tree.links.new(b,n.inputs[1])
    elif value_b is not None: n.inputs[1].default_value=float(value_b)
    return n

def enable_cutout(mat, bsdf, alpha_socket, name, threshold=1e-6):
    # All current source-closed cutout families below use a native kill/discard
    # decision. Convert their proved surviving coverage into a binary Blender alpha.
    cut=math_binary(mat,"GREATER_THAN",alpha_socket,value_b=threshold,name=name+"_CUTOUT",x=300,y=-300)
    mat.node_tree.links.new(cut.outputs[0],bsdf.inputs["Alpha"])
    if hasattr(mat,"surface_render_method"):
        try: mat.surface_render_method="DITHERED"
        except Exception: pass
    if hasattr(mat,"blend_method"):
        for mode in ("HASHED","CLIP","BLEND"):
            try:
                mat.blend_method=mode
                break
            except Exception: pass
    if hasattr(mat,"alpha_threshold"):
        try: mat.alpha_threshold=0.5
        except Exception: pass
    mat["d1_native_alpha_test_applied"]=True
    mat["d1_native_alpha_test_threshold_proxy"]=float(threshold)
    return cut

def palette_control_coverage(mat, n0, n1, n5, name):
    # q0=.2375+r*(r-.2375); q1=q0+g*(g-q0); q2=q1+b*(b-q1);
    # coverage=t1.a*q2. This is exact current-state arithmetic for
    # 808762E1/80876577; the eventual binary kill is coverage > current threshold 0.
    r=channel_socket(mat,n0,"Red",name+"_R",-900,520)
    g=channel_socket(mat,n0,"Green",name+"_G",-900,450)
    b=channel_socket(mat,n5,"Blue",name+"_B",-900,-650)
    rp=math_binary(mat,"SUBTRACT",r,value_b=0.23750001192092896,name=name+"_R_MINUS_P",x=-650,y=520)
    rr=math_binary(mat,"MULTIPLY",r,rp.outputs[0],name=name+"_R_TERM",x=-470,y=520)
    q0=mat.node_tree.nodes.new("ShaderNodeMath"); q0.operation="ADD"; q0.name=name+"_Q0"; q0.location=(-290,520); q0.inputs[0].default_value=0.23750001192092896; mat.node_tree.links.new(rr.outputs[0],q0.inputs[1])
    gq=math_binary(mat,"SUBTRACT",g,q0.outputs[0],name=name+"_G_MINUS_Q0",x=-110,y=460)
    gt=math_binary(mat,"MULTIPLY",g,gq.outputs[0],name=name+"_G_TERM",x=70,y=460)
    q1=mat.node_tree.nodes.new("ShaderNodeMath"); q1.operation="ADD"; q1.name=name+"_Q1"; q1.location=(250,460); mat.node_tree.links.new(q0.outputs[0],q1.inputs[0]); mat.node_tree.links.new(gt.outputs[0],q1.inputs[1])
    bq=math_binary(mat,"SUBTRACT",b,q1.outputs[0],name=name+"_B_MINUS_Q1",x=-110,y=360)
    bt=math_binary(mat,"MULTIPLY",b,bq.outputs[0],name=name+"_B_TERM",x=70,y=360)
    q2=mat.node_tree.nodes.new("ShaderNodeMath"); q2.operation="ADD"; q2.name=name+"_Q2"; q2.location=(250,360); mat.node_tree.links.new(q1.outputs[0],q2.inputs[0]); mat.node_tree.links.new(bt.outputs[0],q2.inputs[1])
    cov=mat.node_tree.nodes.new("ShaderNodeMath"); cov.operation="MULTIPLY"; cov.name=name+"_COVERAGE"; cov.location=(430,320); mat.node_tree.links.new(n1.outputs["Alpha"],cov.inputs[0]); mat.node_tree.links.new(q2.outputs[0],cov.inputs[1])
    return cov.outputs[0]

def neutralize_imported_animation(arms):
    active=[]
    muted_tracks=0
    for arm in arms:
        ad=arm.animation_data
        if ad is not None:
            if ad.action is not None:
                active.append(ad.action.name)
            ad.action=None
            for tr in ad.nla_tracks:
                tr.mute=True
                muted_tracks += 1
        arm.data.pose_position="POSE"
        for pb in arm.pose.bones:
            pb.matrix_basis.identity()
    bpy.context.scene.frame_set(0)
    bpy.context.view_layer.update()
    return active, muted_tracks

def build_material(meta:dict, mat):
    ps=meta["ps"]; bsdf=clear_nodes(mat); links=mat.node_tree.links
    t0=ps_binding(meta,0); t1=ps_binding(meta,1); t2=ps_binding(meta,2); t3=ps_binding(meta,3)
    t4=ps_binding(meta,4); t5=ps_binding(meta,5); t6=ps_binding(meta,6); t7=ps_binding(meta,7)
    status="UNRESOLVED_FAIL_CLOSED"
    visible_tag=None

    if ps in {"808762E1","80876577"} and all((t0,t1,t2,t3,t4,t5)):
        pa=(0.03551533818244934,0.03768035024404526,0.04031895846128464)
        pc=(0.020570652559399605,0.021824637427926064,0.023352932184934616)
        out=build_three_branch_palette_surface(mat,(t0,t1,t2,t3,t4,t5),pa,pa,pc,4.594789981842041,"D1_NATIVE_PALETTE")
        if out:
            links.new(out.outputs["Color"],bsdf.inputs["Base Color"])
            visible_tag=f"native_palette({t0},{t1},{t2},{t3},{t4},{t5})"
            status="SOURCE_CLOSED_CURRENT_RGB_EXACT" if ps=="808762E1" else "SOURCE_CLOSED_PALETTE_SURFACE_PROXY"
            # Reuse the exact control/surface nodes already present in the graph.
            n0=mat.node_tree.nodes.get("D1_NATIVE_PALETTE_CONTROL_T0")
            n1=mat.node_tree.nodes.get("D1_NATIVE_PALETTE_SURFACE_T1")
            n5=mat.node_tree.nodes.get("D1_NATIVE_PALETTE_CONTROL_T5")
            if n0 and n1 and n5:
                cov=palette_control_coverage(mat,n0,n1,n5,"D1_NATIVE_PALETTE")
                enable_cutout(mat,bsdf,cov,"D1_NATIVE_PALETTE",0.0)
        if t6:
            nn=normal_node(mat,t6)
            if nn: links.new(nn.outputs["Normal"],bsdf.inputs["Normal"])
        mat["d1_control_texture_t0_never_basecolor"]=True

    elif ps=="80876566" and t0:
        n0=tex_node(mat,t0,"D1_NATIVE_80876566_T0",-700,180)
        if n0:
            P=(0.02038198709487915,0.024305766448378563,0.029087860137224197)
            out=scaled_color(mat,n0.outputs["Color"],tuple(4*x for x in P),"D1_NATIVE_80876566_PALETTE",50,160)
            links.new(out.outputs["Color"],bsdf.inputs["Base Color"])
            visible_tag=f"{t0}*4P"
            status="SOURCE_CLOSED_CURRENT_RGB_EXACT"
        if t1:
            nn=normal_node(mat,t1)
            if nn: links.new(nn.outputs["Normal"],bsdf.inputs["Normal"])

    elif ps=="80876537" and t0:
        n0=tex_node(mat,t0,"D1_NATIVE_80876537_T0",-700,180)
        if n0:
            P=(0.04633677378296852,0.0552571602165699,0.06612884998321533)
            out=scaled_color(mat,n0.outputs["Color"],tuple(4*x for x in P),"D1_NATIVE_80876537_PALETTE",50,160)
            links.new(out.outputs["Color"],bsdf.inputs["Base Color"])
            visible_tag=f"{t0}*4P"
            status="SOURCE_CLOSED_SURVIVING_RGB_EXACT"
            if t1:
                mask=tex_node(mat,t1,"D1_NATIVE_80876537_COVERAGE_T1",-700,-80,noncolor=True)
                if mask: enable_cutout(mat,bsdf,mask.outputs["Alpha"],"D1_NATIVE_80876537",0.0)
        if t2:
            nn=normal_node(mat,t2)
            if nn: links.new(nn.outputs["Normal"],bsdf.inputs["Normal"])

    elif ps=="809D8351" and all((t0,t1,t4)):
        n0=tex_node(mat,t0,"D1_NATIVE_809D8351_T0",-900,220)
        n1=tex_node(mat,t1,"D1_NATIVE_809D8351_T1",-900,40)
        n4=tex_node(mat,t4,"D1_NATIVE_809D8351_T4",-900,-180,noncolor=True)
        if n0 and n1 and n4:
            prod=multiply_color_sockets(mat,n0.outputs["Color"],n1.outputs["Color"],"D1_NATIVE_809D8351_C",-520,150)
            K=4.594789981842041
            cs=scaled_color(mat,prod.outputs["Color"],(K,K,K),"D1_NATIVE_809D8351_CS",-260,150)
            P=(0.03551533818244934,0.03768035024404526,0.04031895846128464)
            branch=scaled_color(mat,cs.outputs["Color"],tuple(4*x for x in P),"D1_NATIVE_809D8351_BRANCH",-20,-10)
            fac=channel_socket(mat,n4,"Red","D1_NATIVE_809D8351_T4R",-500,-230)
            out=mix_color_sockets(mat,fac,cs.outputs["Color"],branch.outputs["Color"],"D1_NATIVE_809D8351_LERP",250,120)
            links.new(out.outputs["Color"],bsdf.inputs["Base Color"])
            visible_tag=f"lerp({K}*{t0}*{t1},palette,{t4}.r)"
            status="SOURCE_CLOSED_CURRENT_RGB_EXACT"
        if t2:
            nn=normal_node(mat,t2)
            if nn: links.new(nn.outputs["Normal"],bsdf.inputs["Normal"])

    elif ps in DIRECT_T0 and t0:
        n0=tex_node(mat,t0,"D1_INSTRUCTION_PROVEN_SURFACE_T0",-650,180)
        if n0:
            links.new(n0.outputs["Color"],bsdf.inputs["Base Color"])
            visible_tag=t0
            status="SOURCE_CLOSED_SURFACE_INPUT_PROXY"
            # Exact current proofs for these families kill lanes from t0 alpha with
            # current threshold 0. Carry the cutout into Blender; reflection remains
            # separately proxied.
            if ps in {"8087645C","8087656A"}:
                enable_cutout(mat,bsdf,n0.outputs["Alpha"],"D1_NATIVE_"+ps,0.0)
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
            if ps=="8087656A":
                enable_cutout(mat,bsdf,a.outputs["Alpha"],"D1_NATIVE_8087656A",0.0)
        # These families use dual/detail normals; use the first exact normal contributor
        # only when a derived portable normal exists and mark this as incomplete.
        normal_tag=t2
        if normal_tag:
            nn=normal_node(mat,normal_tag)
            if nn: links.new(nn.outputs["Normal"],bsdf.inputs["Normal"])

    elif ps in PALETTE_T1 and t1:
        # These families prove t1 as the RGB surface multiplier/atlas while t0 is
        # selector/control data. Reconstructing the full palette/reflection equation
        # is a separate gate, but exposing t1 is strictly safer than a guessed PBR map.
        n1=tex_node(mat,t1,"D1_PROVEN_SURFACE_ATLAS_T1",-650,180)
        if n1:
            links.new(n1.outputs["Color"],bsdf.inputs["Base Color"])
            visible_tag=t1
            status="PROVEN_SURFACE_ATLAS_PALETTE_PENDING"
        mat["d1_forbidden_visible_texture_t0"]=t0 or ""
        mat["d1_control_texture_t0_never_basecolor"]=True
        if ps=="80876579":
            mat["d1_80876579_control_texture_never_basecolor"]=True

    elif ps in SCALAR_MOD_T0_T2 and t0 and t2:
        n0=tex_node(mat,t0,"D1_PROVEN_SURFACE_T0",-700,180)
        n2=tex_node(mat,t2,"D1_PROVEN_SURFACE_SCALAR_T2",-700,-40,noncolor=True)
        if n0 and n2:
            s=scalar_rgb(mat,n2,"Red",False,"D1_T2_SURFACE_SCALAR",-340,-40)
            mul=multiply_rgb(mat,n0,s,"D1_NATIVE_T0_TIMES_T2R",140,140)
            links.new(mul.outputs["Color"],bsdf.inputs["Base Color"])
            visible_tag=f"{t0}*{t2}.r"
            status="SOURCE_CLOSED_SURFACE_SCALAR_PROXY"

    elif ps in SUBTRACT_MASK_T0_T1 and t0 and t1:
        n0=tex_node(mat,t0,"D1_PROVEN_SURFACE_T0",-700,180)
        n1=tex_node(mat,t1,"D1_PROVEN_SUBTRACTIVE_MASK_T1",-700,-40,noncolor=True)
        if n0 and n1:
            s=scalar_rgb(mat,n1,"Red",True,"D1_ONE_MINUS_T1R",-340,-40)
            mul=multiply_rgb(mat,n0,s,"D1_NATIVE_T0_TIMES_ONE_MINUS_T1R",140,140)
            links.new(mul.outputs["Color"],bsdf.inputs["Base Color"])
            visible_tag=f"{t0}*(1-{t1}.r)"
            status="SOURCE_CLOSED_SUBTRACTIVE_MASK_PROXY"
            # Native 809D836C uses t0.a in its pre-color rejection path. The exact
            # view-dependent 0.23 threshold remains pending, but zero-alpha texels
            # are unambiguously discarded and must not become opaque cards.
            enable_cutout(mat,bsdf,n0.outputs["Alpha"],"D1_NATIVE_809D836C_ZERO_ALPHA",0.0)

    elif ps in CONSTANT_BLACK:
        bsdf.inputs["Base Color"].default_value=(0.0,0.0,0.0,1.0)
        visible_tag="CURRENT_NATIVE_CONSTANT_BLACK"
        status="SOURCE_CLOSED_CONSTANT_RGB_EXACT"

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

def select_diagnostic_preview_pose(scene, arm, imported, actions, candidate_limit=20):
    """Choose one sane low-motion target-native Action for presentation only.

    This reuses the already validated Tower V4 scorer:
    1) score every exact imported Action on this exact Xur armature;
    2) keep only finite/sane pose transforms;
    3) run evaluated-deformed-mesh bounds gates on the lowest-motion candidates;
    4) assign the first candidate that passes.

    No action name/state semantic is inferred and no Action datablock is deleted.
    """
    scored=[]
    for act in actions:
        try:
            scored.append(posev4.score_action(scene,arm,act))
        except Exception as ex:
            scored.append({'action':act.name,'pose_sane':False,'score':1e30,'error':repr(ex)})
    sane=sorted((r for r in scored if r.get('pose_sane')),key=lambda r:(r['score'],r['action']))
    if not sane:
        raise RuntimeError("Xur: no pose-sane selector-owned Action")

    byname={x.name:x for x in actions}
    trials=[]
    chosen=None
    for row in sane[:candidate_limit]:
        act=byname[row['action']]
        try:
            gate=posev4.bbox_gate(scene,arm,imported,act)
        except Exception as ex:
            gate={'action':act.name,'deformed_mesh_sane':False,'error':repr(ex)}
        trials.append(gate)
        if gate.get('deformed_mesh_sane'):
            chosen=(row,gate,act)
            break
    if chosen is None:
        raise RuntimeError(f"Xur: no deformed-mesh-sane Action among {min(candidate_limit,len(sane))} low-motion candidates")

    score,gate,act=chosen
    slot=posev4.assign_action(arm,act)
    arm.data.pose_position='POSE'

    # Pick the sampled frame with the smallest evaluated actor bounding-box volume.
    # This avoids arbitrary start-frame extremes while remaining entirely within
    # the exact target-native clip.
    deps=bpy.context.evaluated_depsgraph_get()
    samples=[]
    for frame in posev4.sample_frames(act,7):
        scene.frame_set(frame); bpy.context.view_layer.update()
        bb=posev4.combined_bbox(imported,deps)
        d=bb['dimensions']; volume=max(float(d[0]),1e-9)*max(float(d[1]),1e-9)*max(float(d[2]),1e-9)
        samples.append({'frame':int(frame),'bbox':bb,'volume':volume})
    chosen_sample=min(samples,key=lambda r:(r['volume'],abs(r['frame']-(sum(x['frame'] for x in samples)/len(samples)))))
    scene.frame_set(chosen_sample['frame']); bpy.context.view_layer.update()

    arm['d1PreviewAction']=act.name
    arm['d1PreviewActionSlot']=slot
    arm['d1PreviewActionPolicy']='LOW_MOTION_TARGET_NATIVE_DIAGNOSTIC_NOT_RETAIL_IDLE'
    arm['d1PreviewFrame']=int(chosen_sample['frame'])
    return {
        'policy':'LOW_MOTION_TARGET_NATIVE_DIAGNOSTIC_NOT_RETAIL_IDLE',
        'action':act.name,
        'slot_identifier':slot,
        'frame':int(chosen_sample['frame']),
        'score':score,
        'mesh_gate':gate,
        'candidate_limit':candidate_limit,
        'pose_sane_action_count':len(sane),
        'tested_mesh_candidate_count':len(trials),
        'mesh_gate_trials':trials,
        'preview_frame_samples':samples,
    }

def upright_root(imported, source_basis_fixed: bool):
    root=bpy.data.objects.new("XUR_D1_TO_BLENDER_ROOT",None)
    bpy.context.scene.collection.objects.link(root)
    roots=[o for o in imported if o.parent not in set(imported)]
    for o in roots:
        mw=o.matrix_world.copy(); o.parent=root; o.matrix_world=mw
    root.rotation_mode="XYZ"
    if source_basis_fixed:
        # The source GLB already undoes the parser [y,z,x] articulated domain and
        # carries the native D1 Z-up -> glTF Y-up wrapper. Blender's glTF importer
        # then performs the normal glTF->Blender basis conversion. Do not rotate twice.
        root.rotation_euler.x=0.0
        root["d1_basis_adapter"]="SOURCE_GLB_STANDALONE_ARTICULATED_BASIS_FIXED"
    else:
        # Legacy fallback retained only for diagnostics; this fixes display orientation
        # but cannot repair parser-space joints/IBMs.
        root.rotation_euler.x=-math.pi/2
        root["d1_basis_adapter"]="LEGACY_DISPLAY_ONLY_ROT_X_NEG_90"
    return root

def stage_camera(arm):
    # Use the skeleton for the optical center because it is the stable actor domain.
    # The prior mesh-union framing admitted long/hidden mesh bounds and made Xur too
    # small in frame. A 24% skeleton margin is enough for hood, coat and feet.
    skel=[]
    if arm.animation_data is not None and arm.animation_data.action is not None and arm.data.pose_position=='POSE':
        for pb in arm.pose.bones:
            skel.append(arm.matrix_world @ pb.head)
            skel.append(arm.matrix_world @ pb.tail)
    else:
        for b in arm.data.bones:
            skel.append(arm.matrix_world @ b.head_local)
            skel.append(arm.matrix_world @ b.tail_local)
    if not skel: raise RuntimeError("no Xur skeleton points")
    mn=Vector((min(p.x for p in skel),min(p.y for p in skel),min(p.z for p in skel)))
    mx=Vector((max(p.x for p in skel),max(p.y for p in skel),max(p.z for p in skel)))
    c=(mn+mx)*0.5
    size=mx-mn
    e=max(size.x,size.y,size.z,1.0)

    world=bpy.data.worlds.new("XUR_PREVIEW_WORLD"); world.use_nodes=True
    bg=world.node_tree.nodes.get("Background"); bg.inputs["Color"].default_value=(0.018,0.021,0.027,1); bg.inputs["Strength"].default_value=0.18
    bpy.context.scene.world=world
    for name,off,energy,size_factor in [
        ("XUR_KEY",(0.75,0.85,0.85),750,0.48),
        ("XUR_FILL",(-0.65,0.25,0.30),320,0.40),
        ("XUR_RIM",(-0.30,-0.75,0.65),850,0.34),
    ]:
        ld=bpy.data.lights.new(name,"AREA"); ld.energy=energy; ld.shape="DISK"; ld.size=e*size_factor
        lo=bpy.data.objects.new(name,ld); lo.location=c+Vector(off)*e
        lo.rotation_euler=(c-lo.location).to_track_quat("-Z","Y").to_euler()
        bpy.context.scene.collection.objects.link(lo)

    # The previous diagonal was confirmed by render to be Xur's rear three-quarter.
    # Flip the horizontal direction to expose the face/hood/front garment.
    cd=bpy.data.cameras.new("XUR_PREVIEW_CAMERA")
    cam=bpy.data.objects.new("XUR_PREVIEW_CAMERA",cd)
    bpy.context.scene.collection.objects.link(cam)
    view=Vector((1.0,0.62,0.045)).normalized()
    cam.location=c+view*(e*1.62)
    cam.rotation_euler=(c-cam.location).to_track_quat("-Z","Y").to_euler()
    cd.lens=55
    bpy.context.scene.camera=cam
    bpy.context.scene["d1PreviewCameraPolicy"]="SKELETON_CENTERED_FRONT_THREE_QUARTER_V2"

def main():
    a=cli(); doc=glb_json(a.input); metadata=mat_meta(doc)
    source_basis_fixed=bool(((doc.get("asset") or {}).get("extras") or {}).get("d1_standalone_articulated_basis_fix"))
    if not source_basis_fixed:
        raise RuntimeError("Xur input is missing the proven standalone articulated basis repair")
    if len(metadata)!=54: raise RuntimeError(f"expected 54 exact Xur materials, got {len(metadata)}")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    before=set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(a.input.resolve()), import_pack_images=True)
    imported=[o for o in bpy.data.objects if o not in before]
    hydrated_native_images,unmarked_image_count=hydrate_embedded_native_images(a.input,doc)
    arms=[o for o in imported if o.type=="ARMATURE"]
    if len(arms)!=1: raise RuntimeError(f"expected one Xur armature, got {len(arms)}")
    root=upright_root(imported,source_basis_fixed)
    root["d1_identity"]="Xur/46C55854/80C88CEF"
    root["d1_material_selection"]="CORPUS_CALIBRATED_VISUAL_ADAPTER"
    root["d1_E6_E7_E8_live_selection_proven"]=False

    rows=[]; counts={}
    for tag,meta in sorted(metadata.items()):
        mat=find_imported_material(tag)
        st=build_material(meta,mat)
        counts[st]=counts.get(st,0)+1
        rows.append({"material":tag,"vs":meta["vs"],"ps":meta["ps"],"semantic_class":SEMANTIC_CLASS.get(meta["ps"],"UNRESOLVED"),"status":st})

    # Preserve all 267 exact selector-owned Actions. Clear whatever arbitrary
    # state the glTF importer selected, then deliberately choose one low-motion,
    # target-native, evaluated-mesh-sane Action for presentation only.
    actions=list(bpy.data.actions)
    for act in actions: act.use_fake_user=True
    imported_active_actions, muted_nla_tracks = neutralize_imported_animation(arms)
    preview_pose=select_diagnostic_preview_pose(bpy.context.scene,arms[0],imported,actions,candidate_limit=20)
    bpy.context.scene["d1_selector_owned_action_count"]=len(actions)
    bpy.context.scene["d1_runtime_default_action_selected"]=False
    bpy.context.scene["d1_preview_action_selected"]=True
    bpy.context.scene["d1_preview_action_policy"]=preview_pose["policy"]
    bpy.context.scene["d1_native_material_semantics_fail_closed"]=True
    bpy.context.scene["d1_full_retail_equivalence_claimed"]=False

    readme=bpy.data.texts.new("XUR_NATIVE_MASTER_README")
    readme.write("Xur native-semantic Blender master.\n")
    readme.write("Geometry/skin/actions come from the calibrated 80C88CEF carrier.\n")
    readme.write("Material nodes use only instruction-proven visible surface inputs.\n")
    readme.write("80876579 t0 control data is explicitly forbidden from visible base color.\n")
    readme.write("Full reflection/palette/runtime-global equations remain marked pending where inputs are not carrier-resident.\n")
    readme.write("The corpus-calibrated external-material choice is an adapter; E6/E7/E8 retail live selection is still unproven.\n")
    readme.write("One low-motion selector-owned Action is assigned only as a sanity-gated diagnostic preview pose. It is NOT claimed to be Xur's retail idle/default.\n")

    stage_camera(arms[0])
    sc=bpy.context.scene
    try: sc.render.engine="BLENDER_EEVEE_NEXT"
    except Exception: pass
    sc.render.resolution_x=900; sc.render.resolution_y=1200; sc.render.resolution_percentage=100
    sc.render.image_settings.file_format="PNG"; sc.render.filepath=str(a.preview.resolve())
    sc.frame_start=int(math.floor(float(arms[0].animation_data.action.frame_range[0])))
    sc.frame_end=max(sc.frame_start+1,int(math.ceil(float(arms[0].animation_data.action.frame_range[1]))))
    sc.frame_set(int(preview_pose["frame"])); bpy.context.view_layer.update()
    for im in bpy.data.images:
        if im.source=="FILE" and im.packed_file is None:
            try: im.pack()
            except Exception: pass
    a.output.parent.mkdir(parents=True,exist_ok=True); a.preview.parent.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(a.output.resolve()))
    bpy.ops.render.render(write_still=True)

    rep={
        "schema_version":1,
        "status":"D1_XUR_BLENDER_NATIVE_MASTER_V2_COMPLETE",
        "input":str(a.input),"input_sha256":sha256(a.input),
        "output":str(a.output),"output_sha256":sha256(a.output),"output_bytes":a.output.stat().st_size,
        "preview":str(a.preview),"preview_sha256":sha256(a.preview),
        "material_count":len(metadata),"action_count":len(actions),"armature_count":len(arms),
        "material_status_counts":counts,"materials":rows,
        "hydrated_native_image_count":hydrated_native_images,
        "unmarked_image_count":unmarked_image_count,
        "packed_image_count":sum(1 for im in bpy.data.images if im.packed_file is not None),
        "imported_active_actions_cleared":imported_active_actions,
        "muted_nla_track_count":muted_nla_tracks,
        "startup_pose":"LOW_MOTION_TARGET_NATIVE_DIAGNOSTIC_NOT_RETAIL_IDLE",
        "diagnostic_preview_pose":preview_pose,
        "basis_adapter":"source GLB parser-basis repair + native D1 Z-up -> glTF Y-up wrapper -> Blender glTF import",
        "source_basis_fix_proven":source_basis_fixed,
        "runtime_material_selection_proven":False,
        "runtime_default_action_selected":False,
        "full_native_equation_claimed":False,
        "policy":"Fail-closed Blender reconstruction. Source-closed shader semantics choose visible inputs; unresolved runtime/global/palette/reflection portions are labeled rather than guessed."
    }
    a.report.parent.mkdir(parents=True,exist_ok=True); a.report.write_text(json.dumps(rep,indent=2)+"\n")
    print(json.dumps({k:rep[k] for k in ["status","material_count","action_count","hydrated_native_image_count","material_status_counts","output_sha256","preview_sha256"]},indent=2))

if __name__=="__main__": main()
