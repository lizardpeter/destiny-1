#!/usr/bin/env python3
"""Blender-native Crota R10 material rebuild.

The carrier GLB preserves exact D1 resources. This Blender-targeted adapter selects
only the six source-closed color surfaces and builds a portable inspection closure
from Crota's paired 0x88 evidence:

    Destination * (1 - partner_alpha) + color_RGB

The blend equation and paired shader outputs are exact. Native draw/pass order is
still WITHHELD, so the combined Blender closure is explicitly an inspection
reconstruction rather than a source-closed claim about framebuffer ordering.

Native evidence:
* PS 8108E953/955/956 export RGB contribution with A=0;
* PS 80AAE1CD/8108E958/959 export RGB=0 with alpha;
* material state 0x88 = Source + Destination*(1-SourceAlpha);
* for current PS8108E959 partner materials, exact retail BC1 blocks + exact
  material coefficients reduce terminal alpha to 1.0;
* for current PS8108E958 partner materials, BC1 alpha inputs are exact 1.0 and
  m27=m48=0, reducing terminal alpha to the BC4 t0.x scalar only.

The three serialized prepass mesh objects using materials 8108E667/8108E66B are
preserved in the carrier artifact but deliberately removed from the Blender scene.
They overlap the color surfaces and caused visible z-fighting in earlier previews.
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

import bpy
from mathutils import Vector

MAT_PROC = {'D1_8108E7A9', 'D1_8108E7B2'}
MAT_ATLAS = {'D1_8108E7AA', 'D1_8108E7B3'}
MAT_DETAIL = {'D1_8108E7B1'}
ACTIVE = MAT_PROC | MAT_ATLAS | MAT_DETAIL
PROC_EXACT_NORMALIZED_GAIN = (0.18661969900131226, 1.0, 0.8700880408287048, 1.0)
DETAIL_EXACT_RGB_VECTOR = (0.22183096408843994, 1.0, 0.9177990555763245, 1.0)
ATLAS_EXACT_STATIC_RGB_VECTOR = (0.3931313157081604, 0.6766623854637146, 0.6658802032470703, 1.0)
ATLAS_EXACT_ANGULAR_BIAS = (0.0003782951971516013, 0.008264296688139439, 0.0054319994524121284)
ATLAS_EXACT_ANGULAR_SLOPE = (0.9996216893196106, 0.9917356967926025, 0.9945679903030396)
# These defaults exist only so a source-closed carrier can be inspected in Blender
# without a live D1 renderer.  Their node names and material metadata keep the
# unresolved API12/API13 inputs explicit rather than baking them into a tint/gain.
PREVIEW_UNRESOLVED_ANGULAR_DEFAULT = 1.0
PREVIEW_UNRESOLVED_API13_PRODUCT_DEFAULT = 1.0


def args_after_double_dash():
    argv = sys.argv
    argv = argv[argv.index('--') + 1:] if '--' in argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--preview', type=Path, required=True)
    ap.add_argument('--mode', choices=('bind','anim'), required=True)
    return ap.parse_args(argv)


def find_exact_image(tag: str):
    exact = f'D1_TEXTURE_{tag.upper()}'
    im = bpy.data.images.get(exact)
    if im is not None:
        return im
    hits = [x for x in bpy.data.images if x.name == exact or x.name.startswith(exact + '.')]
    if len(hits) != 1:
        raise RuntimeError(f'expected exact Blender image {exact}, got {[x.name for x in bpy.data.images]}')
    return hits[0]


def find_control_image():
    # The carrier contains an RGB preview made by bit-exact replication of the
    # decoded BC4 scalar R lane into R/G/B. Blender drops the otherwise-unreferenced
    # raw BC4 PNG during GLB import. This image is scalar-equivalent and therefore
    # safe for scalar control math; it is never treated as retail RGB/albedo.
    exact = 'D1_PREVIEW_SCALAR_RGB_8108E7B6'
    im = bpy.data.images.get(exact)
    if im is None:
        hits = [x for x in bpy.data.images if x.name == exact or x.name.startswith(exact + '.')]
        if len(hits) != 1:
            raise RuntimeError(f'expected scalar-equivalent control image {exact}, got {[x.name for x in bpy.data.images]}')
        im = hits[0]
    return im


def material_names(obj):
    return {slot.material.name.upper() for slot in obj.material_slots if slot.material}


def clean_scene_import(path: Path):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(path))

    removed = []
    for obj in list(bpy.context.scene.objects):
        if obj.type == 'ARMATURE':
            obj.data.display_type = 'STICK'
            obj.show_in_front = False
            obj.hide_set(True)
            obj.hide_render = True
            continue
        if obj.type != 'MESH':
            continue
        mats = material_names(obj)
        if not mats or not (mats & ACTIVE):
            removed.append({'object': obj.name, 'materials': sorted(mats)})
            bpy.data.objects.remove(obj, do_unlink=True)

    visible = [o for o in bpy.context.scene.objects if o.type == 'MESH' and not o.hide_get()]
    if len(visible) != 6:
        raise RuntimeError(f'expected exactly six Crota color mesh objects after prepass removal, got {[(o.name, sorted(material_names(o))) for o in visible]}')
    used = set().union(*(material_names(o) for o in visible))
    if used != ACTIVE:
        raise RuntimeError(f'visible Crota material set drift: {sorted(used)}')
    print('CROTA_R10_SCENE_FILTER', json.dumps({'removed': removed, 'visible': [o.name for o in visible]}, sort_keys=True))


def set_blend_compat(mat):
    if hasattr(mat, 'blend_method'):
        try: mat.blend_method = 'BLEND'
        except Exception: pass
    if hasattr(mat, 'shadow_method'):
        try: mat.shadow_method = 'NONE'
        except Exception: pass
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
    n.name = name; n.label = name; n.image = image; n.location = (x, y)
    n.interpolation = 'Linear'
    return n


def add_rgb(nodes, rgba, name, x, y):
    n = nodes.new('ShaderNodeRGB'); n.name=name; n.label=name; n.location=(x,y)
    n.outputs['Color'].default_value = rgba
    return n


def add_value(nodes, value, name, x, y):
    n=nodes.new('ShaderNodeValue'); n.name=name; n.label=name; n.location=(x,y)
    n.outputs[0].default_value=float(value); return n


def add_math(nodes, operation, name, x, y, *, a=None, b=None, clamp=False):
    n=nodes.new('ShaderNodeMath'); n.operation=operation; n.name=name; n.label=name; n.location=(x,y)
    if a is not None: n.inputs[0].default_value=float(a)
    if b is not None: n.inputs[1].default_value=float(b)
    if hasattr(n,'use_clamp'): n.use_clamp=bool(clamp)
    return n


def add_unresolved_runtime_value(nodes, value, name, x, y):
    n=add_value(nodes,value,name,x,y)
    n.label=name + ' (PREVIEW DEFAULT; D1 LIVE VALUE WITHHELD)'
    return n


def build_rgb_affine_scalar(nodes, links, scalar_socket, bias, slope, prefix, x, y):
    """Build exact per-channel bias + slope*scalar using stable Blender Math/RGB nodes."""
    comb=nodes.new('ShaderNodeCombineRGB'); comb.name=prefix+'_COMBINE'; comb.label=prefix+'_COMBINE'; comb.location=(x+360,y)
    for lane,(b,m) in enumerate(zip(bias,slope)):
        mul=add_math(nodes,'MULTIPLY',f'{prefix}_SLOPE_{lane}',x,y-110*lane,b=float(m))
        links.new(scalar_socket,mul.inputs[0])
        add=add_math(nodes,'ADD',f'{prefix}_BIAS_{lane}',x+180,y-110*lane,b=float(b))
        links.new(mul.outputs[0],add.inputs[0])
        links.new(add.outputs[0],comb.inputs[lane])
    return comb.outputs[0]


def build_exact_runtime_scaled_strength(nodes, links, material_scalar, angular_socket, api13_socket, prefix, x, y):
    mul0=add_math(nodes,'MULTIPLY',prefix+'_MATERIAL_X_ANGULAR',x,y,b=float(material_scalar))
    links.new(angular_socket,mul0.inputs[0])
    mul1=add_math(nodes,'MULTIPLY',prefix+'_X_API13',x+180,y)
    links.new(mul0.outputs[0],mul1.inputs[0]); links.new(api13_socket,mul1.inputs[1])
    return mul1.outputs[0]


def build_proc_color_rgb(nodes, links, scalar_socket, repeated_sample_socket, partner_alpha_socket, angular_u_socket, api13_socket):
    """Portable equation replay of material-specialized PS8108E955 terminal RGB.

    Exact source facts:
      t1 == t2 == t4 == S for selected Crota materials because all three use
      texture 80AACF2A, the same native sampler, and first two coordinate lanes
      (0,0); t3 is dead for the t4 coordinate after exact zero multipliers.
      t1.w=t2.w=t4.w=1; m8..m10=(0.373239398,2,1.740176082),
      m11=1,m12=6,m13=-4.499999523,m24..26=1,m52..54=1,m56=55.

    Blender's image filtering is used to evaluate S at the source-proven coordinate
    and wrap/bilinear mode.  That filtered numeric value is a portable replay, not
    claimed bit-identical to PS4 texture-unit rounding.
    """
    # Shared G = clamp(-4.499999523 + 6*(1-t0.x)).
    one_minus=add_math(nodes,'SUBTRACT','D1_EXACT_955_ONE_MINUS_T0X',-520,-250,a=1.0)
    links.new(scalar_socket,one_minus.inputs[1])
    gmul=add_math(nodes,'MULTIPLY','D1_EXACT_955_M12_X',-350,-250,b=6.0)
    links.new(one_minus.outputs[0],gmul.inputs[0])
    gadd=add_math(nodes,'ADD','D1_EXACT_955_PLUS_M13',-180,-250,b=-4.499999523162842)
    links.new(gmul.outputs[0],gadd.inputs[0])
    g=add_math(nodes,'MULTIPLY','D1_EXACT_955_G_CLAMP',-10,-250,b=1.0,clamp=True)
    links.new(gadd.outputs[0],g.inputs[0])

    # R = 0.6 + 9.4*U.
    rscale=add_math(nodes,'MULTIPLY','D1_EXACT_955_R_9P4U',-520,-390,b=9.399999618530273)
    links.new(angular_u_socket,rscale.inputs[0])
    radd=add_math(nodes,'ADD','D1_EXACT_955_R_PLUS_0P6',-350,-390,b=0.6000000238418579)
    links.new(rscale.outputs[0],radd.inputs[0])

    sep=nodes.new('ShaderNodeSeparateRGB'); sep.name='D1_PORTABLE_955_REPEAT_SAMPLE_SEPARATE'; sep.label=sep.name; sep.location=(-520,120)
    links.new(repeated_sample_socket,sep.inputs['Image'])
    combine=nodes.new('ShaderNodeCombineRGB'); combine.name='D1_EXACT_955_RGB_COMBINE'; combine.label=combine.name; combine.location=(930,150)

    gains=(0.3732393980026245,2.0,1.7401760816574097)
    lanes=('R','G','B')
    for i,(lane,gain) in enumerate(zip(lanes,gains)):
        y=190-170*i
        s=sep.outputs[lane]
        p=add_math(nodes,'MULTIPLY',f'D1_EXACT_955_{lane}_S_SQUARED',-330,y,clamp=True)
        links.new(s,p.inputs[0]); links.new(s,p.inputs[1])
        qmul=add_math(nodes,'MULTIPLY',f'D1_EXACT_955_{lane}_Q_9P4P',-160,y,b=9.399999618530273)
        links.new(p.outputs[0],qmul.inputs[0])
        q=add_math(nodes,'ADD',f'D1_EXACT_955_{lane}_Q_PLUS_0P6',10,y,b=0.6000000238418579)
        links.new(qmul.outputs[0],q.inputs[0])
        qr=add_math(nodes,'MULTIPLY',f'D1_EXACT_955_{lane}_Q_X_R',180,y)
        links.new(q.outputs[0],qr.inputs[0]); links.new(radd.outputs[0],qr.inputs[1])
        fs=add_math(nodes,'MULTIPLY',f'D1_EXACT_955_{lane}_F_SCALE',350,y,b=0.010300000198185444)
        links.new(qr.outputs[0],fs.inputs[0])
        f=add_math(nodes,'ADD',f'D1_EXACT_955_{lane}_F_BIAS_CLAMP',520,y,b=-0.05999999865889549,clamp=True)
        links.new(fs.outputs[0],f.inputs[0])

        oms=add_math(nodes,'SUBTRACT',f'D1_EXACT_955_{lane}_ONE_MINUS_S',-330,y-85,a=1.0)
        links.new(s,oms.inputs[1])
        sq=add_math(nodes,'MULTIPLY',f'D1_EXACT_955_{lane}_ONE_MINUS_S_SQ',-160,y-85)
        links.new(oms.outputs[0],sq.inputs[0]); links.new(oms.outputs[0],sq.inputs[1])
        hs=add_math(nodes,'MULTIPLY',f'D1_EXACT_955_{lane}_H_NEG_0P4',10,y-85,b=-0.4000000059604645)
        links.new(sq.outputs[0],hs.inputs[0])
        h=add_math(nodes,'ADD',f'D1_EXACT_955_{lane}_H_PLUS_0P08',180,y-85,b=0.07999999821186066)
        links.new(hs.outputs[0],h.inputs[0])
        hc=add_math(nodes,'MULTIPLY',f'D1_EXACT_955_{lane}_H_CLAMP',350,y-85,b=1.0,clamp=True)
        links.new(h.outputs[0],hc.inputs[0])
        hterm=add_math(nodes,'MULTIPLY',f'D1_EXACT_955_{lane}_HCLAMP_X_H',520,y-85)
        links.new(hc.outputs[0],hterm.inputs[0]); links.new(h.outputs[0],hterm.inputs[1])

        gf=add_math(nodes,'MULTIPLY',f'D1_EXACT_955_{lane}_G_X_F',690,y)
        links.new(g.outputs[0],gf.inputs[0]); links.new(f.outputs[0],gf.inputs[1])
        gfc=add_math(nodes,'MULTIPLY',f'D1_EXACT_955_{lane}_GF_CLAMP',860,y,b=1.0,clamp=True)
        links.new(gf.outputs[0],gfc.inputs[0])
        csum=add_math(nodes,'ADD',f'D1_EXACT_955_{lane}_C',1030,y)
        links.new(gfc.outputs[0],csum.inputs[0]); links.new(hterm.outputs[0],csum.inputs[1])

        gainn=add_math(nodes,'MULTIPLY',f'D1_EXACT_955_{lane}_GAIN',1200,y,b=gain)
        links.new(csum.outputs[0],gainn.inputs[0])
        abase=add_math(nodes,'MULTIPLY',f'D1_EXACT_955_{lane}_X_A_BASE',1370,y)
        links.new(gainn.outputs[0],abase.inputs[0]); links.new(partner_alpha_socket,abase.inputs[1])
        m56=add_math(nodes,'MULTIPLY',f'D1_EXACT_955_{lane}_X_M56',1540,y,b=55.0)
        links.new(abase.outputs[0],m56.inputs[0])
        runtime=add_math(nodes,'MULTIPLY',f'D1_EXACT_955_{lane}_X_API13',1710,y)
        links.new(m56.outputs[0],runtime.inputs[0]); links.new(api13_socket,runtime.inputs[1])
        links.new(runtime.outputs[0],combine.inputs[lane])
    return combine.outputs['Image']


def build_proc_partner_alpha(nodes, links, scalar_socket):
    """Portable replay of the exact material-specialized PS8108E958 alpha equation.

    Exact source closure established before this adapter:
      t1.w=t2.w=t4.w=1 from retail BC1 block alpha domains;
      m11=1, m12=6, m13=-4.499999523162842,
      m23=1, m27=0, m48=0.
    Thus API12/dot input is dead and only BC4 t0.x remains varying.

    Blender Math nodes evaluate in Blender's numeric domain, so the node network is
    source-equation faithful but is not claimed bit-identical to PS4 GCN rounding.
    """
    one_minus=add_math(nodes,'SUBTRACT','D1_EXACT_958_ONE_MINUS_T0X',-520,-230,a=1.0)
    links.new(scalar_socket,one_minus.inputs[1])
    gmul=add_math(nodes,'MULTIPLY','D1_EXACT_958_M12_X',-330,-230,b=6.0)
    links.new(one_minus.outputs[0],gmul.inputs[0])
    gadd=add_math(nodes,'ADD','D1_EXACT_958_PLUS_M13',-150,-230,b=-4.499999523162842)
    links.new(gmul.outputs[0],gadd.inputs[0])
    gclamp=add_math(nodes,'MULTIPLY','D1_EXACT_958_G_CLAMP',30,-230,b=1.0,clamp=True)
    links.new(gadd.outputs[0],gclamp.inputs[0])

    # F after exact substitutions: both multiplicative 0.6+9.4 terms receive 1.
    f0=add_value(nodes,0.6000000238418579,'D1_958_LITERAL_0P6',-520,-410)
    f1=add_value(nodes,9.399999618530273,'D1_958_LITERAL_9P4',-520,-460)
    fsum=add_math(nodes,'ADD','D1_EXACT_958_FACTOR_TEN',-330,-430)
    links.new(f0.outputs[0],fsum.inputs[0]); links.new(f1.outputs[0],fsum.inputs[1])
    fsq=add_math(nodes,'MULTIPLY','D1_EXACT_958_FACTOR_PRODUCT',-150,-430)
    links.new(fsum.outputs[0],fsq.inputs[0]); links.new(fsum.outputs[0],fsq.inputs[1])
    fscale=add_math(nodes,'MULTIPLY','D1_EXACT_958_SCALE_0P0103',30,-430,b=0.010300000198185444)
    links.new(fsq.outputs[0],fscale.inputs[0])
    fbias=add_math(nodes,'ADD','D1_EXACT_958_BIAS_MINUS_0P06',210,-430,b=-0.05999999865889549,clamp=True)
    links.new(fscale.outputs[0],fbias.inputs[0])

    gf=add_math(nodes,'MULTIPLY','D1_EXACT_958_G_TIMES_F',210,-230)
    links.new(gclamp.outputs[0],gf.inputs[0]); links.new(fbias.outputs[0],gf.inputs[1])
    gfclamp=add_math(nodes,'MULTIPLY','D1_EXACT_958_GF_CLAMP',390,-230,b=1.0,clamp=True)
    links.new(gf.outputs[0],gfclamp.inputs[0])

    # H = 0.08 exactly at the specialized symbolic level because m48=0,t4.w=1.
    h=add_value(nodes,0.07999999821186066,'D1_EXACT_958_H',210,-570)
    hsq=add_math(nodes,'MULTIPLY','D1_EXACT_958_H_SQUARED',390,-570)
    links.new(h.outputs[0],hsq.inputs[0]); links.new(h.outputs[0],hsq.inputs[1])
    alpha=add_math(nodes,'ADD','D1_EXACT_958_SPECIALIZED_ALPHA',580,-300,clamp=True)
    links.new(gfclamp.outputs[0],alpha.inputs[0]); links.new(hsq.outputs[0],alpha.inputs[1])
    return alpha.outputs[0]


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
    tex_control = find_control_image()
    tex_atlas = find_exact_image('8108E951')
    tex_detail = find_exact_image('8108E952')

    if tag in MAT_PROC:
        t = add_tex(nodes, tex_control, 'D1_SCALAR_EQUIVALENT_8108E7B6_CONTROL', -1180,260)
        # Native PS8108E955 samples t0 on PS attr1.xy. Exact registered Crota VS
        # programs prove attr1=param1=transformed tangent T, so using Blender's
        # default UV here is incorrect. Until native DQ-transformed tangent is
        # available per fragment in this portable material, expose the coordinate
        # as an explicit preview proxy rather than silently substituting UV.
        tangent_coord=nodes.new('ShaderNodeCombineXYZ')
        tangent_coord.name='D1_PROXY_955_TRANSFORMED_TANGENT_XY'
        tangent_coord.label='D1_PROXY_955_TRANSFORMED_TANGENT_XY (LIVE PER-VERTEX VALUE WITHHELD)'
        tangent_coord.location=(-1400,300)
        tangent_coord.inputs['X'].default_value=0.0
        tangent_coord.inputs['Y'].default_value=0.0
        tangent_coord.inputs['Z'].default_value=0.0
        links.new(tangent_coord.outputs['Vector'],t.inputs['Vector'])
        if hasattr(t,'extension'): t.extension='REPEAT'
        tex_repeat=find_exact_image('80AACF2A')
        s=add_tex(nodes,tex_repeat,'D1_PORTABLE_955_REPEATED_BC1_SAMPLE_AT_ZERO',-1180,80)
        s.interpolation='Linear'
        if hasattr(s,'extension'): s.extension='REPEAT'
        zero=nodes.new('ShaderNodeCombineXYZ'); zero.name='D1_EXACT_955_ZERO_COORDINATE'; zero.label=zero.name; zero.location=(-1360,20)
        zero.inputs['X'].default_value=0.0; zero.inputs['Y'].default_value=0.0; zero.inputs['Z'].default_value=0.0
        links.new(zero.outputs['Vector'],s.inputs['Vector'])
        angular=add_unresolved_runtime_value(nodes,PREVIEW_UNRESOLVED_ANGULAR_DEFAULT,'D1_PROXY_955_ANGULAR_U',-1180,-120)
        api13=add_unresolved_runtime_value(nodes,PREVIEW_UNRESOLVED_API13_PRODUCT_DEFAULT,'D1_PROXY_API13_RGB_SCALE',-1180,-200)
        partner_alpha=build_proc_partner_alpha(nodes,links,t.outputs['Color'])
        links.new(partner_alpha,mix.inputs['Fac'])
        proc_rgb=build_proc_color_rgb(nodes,links,t.outputs['Color'],s.outputs['Color'],partner_alpha,angular.outputs[0],api13.outputs[0])
        links.new(proc_rgb,emission.inputs['Color'])
        emission.inputs['Strength'].default_value=1.0
        proxy='PS8108E955_EXACT_MATERIAL_SPECIALIZED_EQUATION_WITH_PORTABLE_BILINEAR_REPEAT_SAMPLE_AND_EXPLICIT_API12_API13_PREVIEW_INPUTS + PS8108E958_EXACT_MATERIAL_SPECIALIZED_BC4_ALPHA'
        mat['d1_r10_color_shader']='8108E955'
        mat['d1_r10_color_exact_normalized_gain']=list(PROC_EXACT_NORMALIZED_GAIN[:3])
        mat['d1_r10_color_exact_material_scalar']=55.0
        mat['d1_r10_color_repeated_sample_relation']='t1=t2=t4=S from texture 80AACF2A, same sampler, first two encoded coordinate lanes (0,0)'
        mat['d1_r10_color_t3_coordinate_effect']='DEAD_FOR_T4_COORDINATE_AFTER_EXACT_ZERO_MULTIPLIERS'
        mat['d1_r10_color_remaining_runtime']='D1_PROXY_955_TRANSFORMED_TANGENT_XY := native DQ-transformed tangent XY for t0 BC4 coordinate; D1_PROXY_955_ANGULAR_U := clamp(-1.25*d*d+1.25), d depends on API12[28:30]+N/B; D1_PROXY_API13_RGB_SCALE := API13[6]*API13[7]; live values WITHHELD'
        mat['d1_r10_color_coordinate_semantic']='PS8108E955 t0 first two coordinate lanes = TRANSFORMED_TANGENT_XY (exact post-fetch VS interface proof)'
        mat['d1_r10_color_preview_proxy']='D1_PROXY_955_TRANSFORMED_TANGENT_XY defaults to (0,0), D1_PROXY_955_ANGULAR_U=1, D1_PROXY_API13_RGB_SCALE=1; no false UV substitution; ramp and 1.65 gain removed'
        mat['d1_r10_color_equation_replay']='per-channel native specialized PS8108E955 equation; exact material constants; repeated S sample; m56=55; API13 product explicit'
        mat['d1_r10_portable_filter_boundary']='S coordinate/sampler state is exact; Blender Linear+REPEAT filtered numeric result is not claimed PS4 bit-identical'
        mat['d1_r10_t0_coordinate_portable_replay']='WITHHELD_NATIVE_DQ_TRANSFORMED_TANGENT_NOT_AVAILABLE_TO_CURRENT_BLENDER_MATERIAL'
    elif tag in MAT_ATLAS:
        t=add_tex(nodes,tex_atlas,'D1_EXACT_8108E951_COLOR_ATLAS',-920,230)
        angular=add_unresolved_runtime_value(nodes,PREVIEW_UNRESOLVED_ANGULAR_DEFAULT,'D1_PROXY_956_ANGULAR_V',-920,-40)
        api13=add_unresolved_runtime_value(nodes,PREVIEW_UNRESOLVED_API13_PRODUCT_DEFAULT,'D1_PROXY_API13_RGB_SCALE',-920,-120)
        angular_rgb=build_rgb_affine_scalar(
            nodes,links,angular.outputs[0],
            ATLAS_EXACT_ANGULAR_BIAS,ATLAS_EXACT_ANGULAR_SLOPE,
            'D1_EXACT_956_ANGULAR_RGB',-700,40)
        mult0=nodes.new('ShaderNodeVectorMath'); mult0.operation='MULTIPLY'; mult0.name='D1_EXACT_956_TEXTURE_X_ANGULAR'; mult0.location=(-120,230)
        links.new(t.outputs['Color'],mult0.inputs[0]); links.new(angular_rgb,mult0.inputs[1])
        static=add_rgb(nodes,ATLAS_EXACT_STATIC_RGB_VECTOR,'D1_EXACT_956_STATIC_RGB_VECTOR',-120,60)
        mult1=nodes.new('ShaderNodeVectorMath'); mult1.operation='MULTIPLY'; mult1.name='D1_EXACT_956_X_STATIC_RGB'; mult1.location=(70,230)
        links.new(mult0.outputs['Vector'],mult1.inputs[0]); links.new(static.outputs['Color'],mult1.inputs[1])
        links.new(mult1.outputs['Vector'],emission.inputs['Color'])
        one=add_value(nodes,1.0,'D1_EXACT_956_ANGULAR_STRENGTH_ONE',-300,-70)
        strength=build_exact_runtime_scaled_strength(nodes,links,18.0,one.outputs[0],api13.outputs[0],'D1_EXACT_956_RGB_SCALE',-80,-80)
        links.new(strength,emission.inputs['Strength'])
        a=add_value(nodes,1.0,'D1_EXACT_8108E959_PARTNER_ALPHA_ONE',-120,-220); links.new(a.outputs[0],mix.inputs['Fac'])
        proxy='PS8108E956_EXACT_MATERIAL_SPECIALIZED_RGB_WITH_EXPLICIT_API12_ANGULAR_AND_API13_PREVIEW_INPUTS + PS8108E959_EXACT_CURRENT_MATERIAL_ALPHA_ONE'
        mat['d1_r10_color_shader']='8108E956'
        mat['d1_r10_color_exact_static_rgb_vector']=list(ATLAS_EXACT_STATIC_RGB_VECTOR[:3])
        mat['d1_r10_color_exact_angular_bias']=list(ATLAS_EXACT_ANGULAR_BIAS)
        mat['d1_r10_color_exact_angular_slope']=list(ATLAS_EXACT_ANGULAR_SLOPE)
        mat['d1_r10_color_exact_material_scalar']=18.0
        mat['d1_r10_color_remaining_runtime']='D1_PROXY_956_ANGULAR_V := native V from API12[28:30]+attr0/attr2; D1_PROXY_API13_RGB_SCALE := API13[6]*API13[7]; both live values WITHHELD'
        mat['d1_r10_color_preview_proxy']='ONLY D1_PROXY_956_ANGULAR_V=1 and D1_PROXY_API13_RGB_SCALE=1; tint and 2.2 gain removed'
        mat['d1_r10_color_equation_replay']='t0.rgb * (bias+slope*V) * staticRGB * 18 * API13[6]*API13[7]'
    elif tag in MAT_DETAIL:
        t=add_tex(nodes,tex_detail,'D1_EXACT_8108E952_DETAIL_COLOR',-920,220)
        exact_rgb=add_rgb(nodes,DETAIL_EXACT_RGB_VECTOR,'D1_EXACT_953_MATERIAL_RGB_VECTOR',-720,40)
        mult=nodes.new('ShaderNodeVectorMath'); mult.operation='MULTIPLY'; mult.name='D1_EXACT_953_TEXTURE_X_MATERIAL_RGB'; mult.location=(-430,210)
        links.new(t.outputs['Color'],mult.inputs[0]); links.new(exact_rgb.outputs['Color'],mult.inputs[1]); links.new(mult.outputs['Vector'],emission.inputs['Color'])
        angular=add_unresolved_runtime_value(nodes,PREVIEW_UNRESOLVED_ANGULAR_DEFAULT,'D1_PROXY_953_ANGULAR_U',-720,-110)
        api13=add_unresolved_runtime_value(nodes,PREVIEW_UNRESOLVED_API13_PRODUCT_DEFAULT,'D1_PROXY_API13_RGB_SCALE',-720,-190)
        strength=build_exact_runtime_scaled_strength(nodes,links,9.0,angular.outputs[0],api13.outputs[0],'D1_EXACT_953_RGB_SCALE',-390,-100)
        links.new(strength,emission.inputs['Strength'])
        a=add_value(nodes,1.0,'D1_EXACT_80AAE1CD_PARTNER_ALPHA_ONE',-120,-220); links.new(a.outputs[0],mix.inputs['Fac'])
        proxy='PS8108E953_EXACT_MATERIAL_SPECIALIZED_RGB_WITH_EXPLICIT_API12_ANGULAR_AND_API13_PREVIEW_INPUTS + 80AAE1CD_EXACT_BLACK_ALPHA_ONE'
        mat['d1_r10_color_shader']='8108E953'
        mat['d1_r10_color_exact_material_rgb_vector']=list(DETAIL_EXACT_RGB_VECTOR[:3])
        mat['d1_r10_color_exact_material_scalar']=9.0
        mat['d1_r10_color_remaining_runtime']='D1_PROXY_953_ANGULAR_U := clamp(d*d), d depends on API12[28:30]+attr0/attr2; D1_PROXY_API13_RGB_SCALE := API13[6]*API13[7]; live values WITHHELD'
        mat['d1_r10_color_preview_proxy']='ONLY D1_PROXY_953_ANGULAR_U=1 and D1_PROXY_API13_RGB_SCALE=1; arbitrary emission strength 2.0 removed'
        mat['d1_r10_color_equation_replay']='t0.rgb * materialRGB * U * 9 * API13[6]*API13[7]'
    else:
        raise RuntimeError(tag)

    mat.diffuse_color = (0.04,0.65,0.45,0.35)
    mat['d1_r10_blend_equation_exact']='Source + Destination*(1-SourceAlpha)'
    mat['d1_r10_partner_alpha_input']='SOURCE_CLOSED_FOR_SELECTED_RETAIL_MATERIAL'
    mat['d1_r10_native_pass_order']='WITHHELD'
    mat['d1_r10_blender_closure']='PORTABLE_INSPECTION_ASSUMPTION: attenuation then color'
    mat['d1_r10_proxy']=proxy


def rebuild_materials():
    found=[]
    for mat in list(bpy.data.materials):
        if mat.name.upper() in ACTIVE:
            build_native_material(mat); found.append(mat.name.upper())
    if set(found) != ACTIVE:
        raise RuntimeError(f'active material mismatch: {found}')


def add_stage_and_camera():
    world=bpy.data.worlds.new('D1_CROTA_DARK_WORLD'); world.use_nodes=True
    bg=world.node_tree.nodes.get('Background'); bg.inputs['Color'].default_value=(0.006,0.009,0.008,1); bg.inputs['Strength'].default_value=0.12
    bpy.context.scene.world=world

    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH' and not o.hide_get()]
    pts=[o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
    if not pts: raise RuntimeError('no visible Crota meshes')
    mn=Vector((min(p.x for p in pts),min(p.y for p in pts),min(p.z for p in pts)))
    mx=Vector((max(p.x for p in pts),max(p.y for p in pts),max(p.z for p in pts)))
    center=(mn+mx)*0.5; extent=max((mx-mn).length,1.0)
    cam_data=bpy.data.cameras.new('CROTA_PREVIEW_CAMERA'); cam=bpy.data.objects.new('CROTA_PREVIEW_CAMERA',cam_data); bpy.context.scene.collection.objects.link(cam)
    cam.location=center+Vector((extent*0.15,-extent*1.15,extent*0.05))
    cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler(); cam_data.lens=58; bpy.context.scene.camera=cam

    for name,loc,energy,size in [
        ('KEY',center+Vector((-extent*0.45,-extent*0.55,extent*0.55)),500,extent*0.45),
        ('RIM',center+Vector((extent*0.65,extent*0.25,extent*0.35)),700,extent*0.35),
    ]:
        ld=bpy.data.lights.new(name,'AREA'); ld.energy=energy; ld.shape='DISK'; ld.size=size
        lo=bpy.data.objects.new(name,ld); lo.location=loc; lo.rotation_euler=(center-loc).to_track_quat('-Z','Y').to_euler(); bpy.context.scene.collection.objects.link(lo)


def configure_render(preview: Path):
    sc=bpy.context.scene
    for engine in ('BLENDER_EEVEE_NEXT','BLENDER_EEVEE'):
        try: sc.render.engine=engine; break
        except Exception: pass
    sc.render.resolution_x=900; sc.render.resolution_y=1100; sc.render.resolution_percentage=100
    sc.render.image_settings.file_format='PNG'; sc.render.filepath=str(preview); sc.render.film_transparent=False


def save_and_render(output:Path, preview:Path, mode:str):
    sc=bpy.context.scene
    if mode=='anim': sc.frame_start=1; sc.frame_end=61; sc.frame_set(1)
    else: sc.frame_start=1; sc.frame_end=1; sc.frame_set(1)
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
        'visible_crota_meshes':6,
        'materials':sorted(ACTIVE),
        'blend_equation_exact':'Source + Destination*(1-SourceAlpha)',
        'partner_alpha_specialization':'SOURCE_CLOSED_FOR_SELECTED_RETAIL_MATERIALS',
        'native_pass_order':'WITHHELD',
        'implementation':'portable inspection closure assumes attenuation then color; partner alpha inputs are exact',
        'frame_range':[bpy.context.scene.frame_start,bpy.context.scene.frame_end],
    },indent=2))

if __name__=='__main__': main()
