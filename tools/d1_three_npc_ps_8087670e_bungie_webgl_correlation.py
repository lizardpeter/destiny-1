#!/usr/bin/env python3
"""Fail-closed semantic correlation between native D1 PS 8087670E and Bungie.net GearShader.

This proof is deliberately asymmetric:
- retail PS4 GCN/material data remains authoritative for the native program;
- Bungie.net's developer-supplied unminified WebGL renderer is used only to
  source-correlate algebra/semantic positions that match exactly;
- WebGL texture units, `hasGearDyeTextures`, and runtime resource ownership are
  NOT promoted to native PS4 bindings without an independent native join.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

GEAR_BLOB='ec1e0e395795959723067f60c6456bed6966b7a3'
RENDERABLE_BLOB='363d935a7a4a7812a9a580f88b01377185b6cb79'
VISUAL_SHA='3d40c61f40d52fe1915baa38115989a2cf7ff01679235d8b77e1711f5b1731ff'
TARGET_PS='8087670E'
TARGET_MATERIALS={'808766B2','808766B6'}
TARGET_RANGES={
 '80C88434_mesh2_range0_231':('808766B2',2,0,1,'80876960',True),
 '80C88434_mesh2_range272_1021':('808766B2',2,2,1,'80876960',True),
 '80C88434_mesh3_range0_458':('808766B6',3,0,1,'8087695C',False),
 '80C88434_mesh3_range571_339':('808766B6',3,2,3,'8087695C',False),
 '80C88434_mesh3_range911_3255':('808766B6',3,3,1,'8087695C',False),
}

def git_blob_sha(b:bytes)->str:
    return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()

def norm(x): return str(x).upper().removeprefix('0X').zfill(8)

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--blend-proof',type=Path,required=True)
    ap.add_argument('--model-report',type=Path,required=True)
    ap.add_argument('--bungie-gear-shader',type=Path,required=True)
    ap.add_argument('--bungie-renderable',type=Path,required=True)
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args(); violations=[]
    blend=json.loads(a.blend_proof.read_text())
    model=json.loads(a.model_report.read_text())
    gb=a.bungie_gear_shader.read_bytes(); rb=a.bungie_renderable.read_bytes()
    gear=gb.decode('utf-8'); renderable=rb.decode('utf-8')

    if blend.get('status')!='D1_TOWER_PS_8087670E_BLEND_FACTOR_EXACT': violations.append('native blend proof not exact')
    if blend.get('shader')!=TARGET_PS: violations.append('native shader mismatch')
    if set(blend.get('scope_materials',[]))!=TARGET_MATERIALS: violations.append('native material scope mismatch')
    if git_blob_sha(gb)!=GEAR_BLOB: violations.append('Bungie GearShader blob mismatch')
    if git_blob_sha(rb)!=RENDERABLE_BLOB: violations.append('Bungie Renderable blob mismatch')
    if hashlib.sha256(a.model_report.read_bytes()).hexdigest()!=VISUAL_SHA: violations.append('pinned visual report SHA mismatch')

    web_anchors=[
      'return front * saturate(back * 4.0) + saturate(back - 0.25);',
      'vec4 color_diffuse = pow(texture2D(u_texture_diffuse, v_texcoord), ',
      'vec2 normal_sample_raw = texture2D(u_texture_normal, v_texcoord).xy;',
      'normal_sample = normal_sample * 2.0 - 1.0;',
      'vec4 color_dye_diffuse_texture = texture2D(u_texture_dye_diffuse, v_texcoord2);',
      'color_diffuse = blend_overlay(color_dye_diffuse, color_diffuse);',
      'vec4 color_dye_normal = texture2D(u_texture_dye_normal, v_texcoord2);',
      'color_dye_normal = color_dye_normal * 2.0 - 1.0;',
      'normal_sample = normal_sample + color_dye_normal.xy;',
      'vec4 color_gearstack = texture2D(u_texture_gearstack, v_texcoord);',
      'blend_overlay(color_diffuse, u_change_color),',
      'color_gearstack.r);',
      '// if (hasGearDyeTextures)',
      '// hasGearDyeTextures : hasGearDyeTextures',
    ]
    for x in web_anchors:
        if x not in gear: violations.append('missing GearShader anchor: '+x)
    render_anchors=[
      'var hasTexcoord2 = false;',
      'if (shaderValueName === "a_texcoord2")',
      'hasTexcoord2 = true;',
      'this.hasTexcoord2 = hasTexcoord2;',
      'this.hasTexcoord2,',
    ]
    for x in render_anchors:
        if x not in renderable: violations.append('missing Renderable anchor: '+x)

    target=next((x for x in model.get('models',[]) if norm(x.get('model'))=='80C88434'),None)
    if target is None: violations.append('80C88434 absent from visual report'); rows=[]
    else:
        rows=[x for x in target.get('ranges',[]) if x.get('name') in TARGET_RANGES]
        if len(rows)!=5: violations.append(f'expected 5 target ranges, got {len(rows)}')
        got={}
        for r in rows:
            parts=r.get('parts') or []
            if len(parts)!=1: violations.append(f"{r.get('name')}: expected one part"); continue
            p=parts[0]; mi=r.get('material_info') or {}
            vs=norm(mi.get('vertex_shader','FFFFFFFF')) if isinstance(mi.get('vertex_shader'),str) else f"{int(mi.get('vertex_shader',0))&0xffffffff:08X}"
            got[r['name']] = (norm(r.get('material')),int(r.get('mesh_index')),
                              int(p.get('part_index')),int(p.get('lod')),vs,bool(r.get('has_uv')))
        for name,expect in TARGET_RANGES.items():
            if got.get(name)!=expect: violations.append(f'{name}: native range tuple mismatch {got.get(name)!r} != {expect!r}')

    eq=blend.get('instruction_level_equations',{})
    expected_eq={
      'primary_normal_xy':'n0.xy = 2*t1.xy - 1',
      'detail_combined_normal_xy':'n1.xy = n0.xy + 2*t5.xy - 1',
      'material_local_rgb_branch':'P = lerp(t0.rgb, saturate(t0.rgb-0.25) + float3(0.22316759824752808)*saturate(4*t0.rgb), t3.r)',
      't4_rgb_branch':'Q = saturate(t0.rgb-0.25) + t4.rgb*saturate(4*t0.rgb)',
      'surface_branch_blend':'surface = lerp(P,Q,f)',
    }
    for k,v in expected_eq.items():
        if eq.get(k)!=v: violations.append(f'native equation mismatch {k}')

    if violations:
        out={'schema_version':1,'status':'D1_PS_8087670E_BUNGIE_WEBGL_CORRELATION_PARTIAL','violations':violations}
    else:
        out={
          'schema_version':1,
          'status':'D1_PS_8087670E_BUNGIE_WEBGL_CORRELATION_EXACT',
          'violations':[],
          'native_shader':TARGET_PS,
          'native_gcn_sha256':blend['gcn_sha256'],
          'bungie_source':{
            'repository':'DestinyDevs/BungieNetPlatform',
            'commit':'a96f233d133d7d61c0c7a8d80fbb054b33a2343e',
            'gear_shader_git_blob':GEAR_BLOB,
            'renderable_git_blob':RENDERABLE_BLOB,
            'provenance':'unminified Bungie.net source archive; semantic correlation only, not PS4 binding ownership',
          },
          'exact_semantic_correlations':{
            'overlay_primitive':'Both lineages use front*saturate(back*4)+saturate(back-0.25).',
            'base_diffuse':'Native t0 occupies the same base-color algebra position as Bungie WebGL u_texture_diffuse in the change-color branch.',
            'change_color_mask':'Native t3.r occupies the same final lerp-mask position as Bungie WebGL color_gearstack.r.',
            'change_color_vector':'Native constant float3(0.22316759824752808) occupies the same overlay-front semantic position as Bungie WebGL u_change_color for P.',
            'base_normal':'Native 2*t1.xy-1 matches Bungie WebGL base normal unpack shape.',
            'optional_normal_structure':'Native optional path adds 2*t5.xy-1 to the base XY normal; Bungie WebGL optional dye-normal lineage has the same unpack-and-add structure. Texture identity is not promoted.',
          },
          'native_range_crosscheck':{
            '808766B2':{'vertex_shader':'80876960','range_count':2,'exporter_has_uv':True},
            '808766B6':{'vertex_shader':'8087695C','range_count':3,'exporter_has_uv':False},
            'consequence':'A simple native f == WebGL hasTexcoord2 mapping is rejected: both materials share PS/API15 selector while their exported source-UV state differs.',
          },
          'withheld_joins':{
            't4_equals_webgl_dye_diffuse':False,
            't5_equals_webgl_dye_normal':False,
            'api15_f_equals_webgl_hasGearDyeTextures':False,
            'reason':'The WebGL source uses a separate renderer/material interface and its hasGearDyeTextures shader gating is commented out in the pinned build; no native PS4 resource-producer join exists yet.',
          },
          'gates':{
            't0_base_diffuse_semantic_correlated':True,
            't3_r_change_color_mask_semantic_correlated':True,
            'native_constant_change_color_position_correlated':True,
            'normal_optional_path_structurally_correlated':True,
            'runtime_t4_binding_closed':False,
            'api15_c0_w_runtime_value_closed':False,
            'final_shader_color_closed':False,
          },
          'policy':'Promote only exact equation/semantic-position matches. Do not transfer WebGL texture-unit identity, hasGearDyeTextures state, or resource ownership onto the native PS4 renderer.',
        }
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out if violations else {k:out[k] for k in ('status','exact_semantic_correlations','native_range_crosscheck','withheld_joins','gates','violations')},indent=2))
    return 2 if violations else 0

if __name__=='__main__': raise SystemExit(main())
