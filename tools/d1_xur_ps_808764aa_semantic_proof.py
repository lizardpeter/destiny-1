#!/usr/bin/env python3
"""Fail-closed instruction-level semantic proof for Xur PS 808764AA.

This proof promotes only equations and resource roles directly supported by the
exact native GCN binary plus exact Xur material-local state. The camera/view
meaning of api12[28:30] is reused from the already retail-closed D1 Tower
809DCD66 native proof; high-level PBR names and render-state semantics remain
withheld.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

SHADER='808764AA'
GCN_SHA='05eac4afa0c0e050b3f1237424cb984d20923f619d20066bccd333498e7c80f8'
NATIVE_SHADER='808764AD'
MEMBERS=['8087642F','808764CB','808764CD','808764CE']
TFX_HEX='490047214901472249024723'
SAMPLERS=['80AAE177','80AAE177','80AAE176']
SAMPLER_PAYLOAD_SHAS=[
 '2c670016bbb70b68bd2f69dd4a30145bf7d61a47c1bf4c3acba8321b46976ecb',
 '2c670016bbb70b68bd2f69dd4a30145bf7d61a47c1bf4c3acba8321b46976ecb',
 '0bcdaa82ea0d8588e313f29998f6c7b9166e7d28d40b13d422348d55ae5dc208',
]
TEXTURES={
 '8087642F':['8087645A','8087645B','80AACC28'],
 '808764CB':['808764EA','808764EB','80AACC28'],
 '808764CD':['808764EF','808764F0','80AACC28'],
 '808764CE':['808764F1','808764F2','80AACC28'],
}
# Full exact CBuffer payloads differ only in 808764CB c6.zw; those two dwords are
# not consumed by this GCN binary, but retaining the distinction keeps the proof
# pinned to the current retail local-state checkpoint.
CBUFFER_RAW_COMMON=[
 '00000040000080bf000080bf000080bf',
 '00000000000000000000000000000000',
 '00000000000000000000000000000000',
 '00000000000000000000000000000000',
 '000040400000803f0000803f0000803f',
 '000000000000803f0000803f0000803f',
 '00000000cdcc4c3d0000000000000000',
 '0000803f0000803f0000000000000000',
 '00000000000000000000000000000000',
 '0000003fa9a8a83c0000a0400000a040',
]
CBUFFER_RAW_808764CB=CBUFFER_RAW_COMMON.copy()
CBUFFER_RAW_808764CB[6]='00000000cdcc4c3d000080bf000080bf'
CBUFFER_BY_MATERIAL={m:CBUFFER_RAW_COMMON for m in MEMBERS}
CBUFFER_BY_MATERIAL['808764CB']=CBUFFER_RAW_808764CB

ANCHORS=[
 'image_sample    v[4:5], v[2:5], s[16:23], s[24:27] dmask:3',
 'v_mad_f32       v4, v4, s0, v6',
 'v_sqrt_f32      v5, v5',
 'v_rsq_clamp_f32 v4, v4',
 'v_mad_f32       v11, v14, v4, v11 mul:2',
 'v_cubema_f32    v5, v6, v13, v11',
 'v_cubetc_f32    v9, v6, v13, v11',
 'v_cubesc_f32    v10, v6, v13, v11',
 'v_cubeid_f32    v15, v6, v13, v11',
 'image_get_lod   v10, v[13:16], s[20:27], s[0:3] dmask:2',
 'image_sample_l  v[9:12], v[13:16], s[20:27], s[0:3] dmask:15',
 'image_sample    v[13:15], v[2:5], s[4:11], s[12:15] dmask:7',
 'v_madak_f32     v4, v5, v4, 0x3f000000',
 'exp             mrt1, v1, v1, v2, v2 compr',
 'exp             mrt0, v1, v1, v0, v0 done compr vm',
]


def flatten_cb(ps:dict)->list[float]:
    return [float(x) for row in ps['cbuffers']['items'] for x in row['value']]


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--material-state',type=Path,required=True)
    ap.add_argument('--shader-census',type=Path,required=True)
    ap.add_argument('--image-usage',type=Path,required=True)
    ap.add_argument('--texture-manifest',type=Path,required=True)
    ap.add_argument('--disassembly',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    state=json.loads(a.material_state.read_text())
    census=json.loads(a.shader_census.read_text())
    images=json.loads(a.image_usage.read_text())
    manifest=json.loads(a.texture_manifest.read_text())
    asm=a.disassembly.read_text()
    violations=[]

    if state.get('status')!='D1_MATERIAL_STAGE_STATE_EXACT': violations.append('material state checkpoint not exact')
    if census.get('status')!='D1_XUR_ALL_NATIVE_SHADER_DISASSEMBLY_EXACT': violations.append('shader census checkpoint not exact')
    if images.get('status')!='D1_GCN_IMAGE_RESOURCE_USAGE_EXACT': violations.append('image usage checkpoint not exact')
    if manifest.get('status')!='D1_XUR_EXACT_MATERIAL_TEXTURE_MANIFEST_SUBSET':
        violations.append(f'unsupported texture manifest status {manifest.get("status")!r}')
    if manifest.get('visible_material_count')!=54 or manifest.get('material_decode_errors') or manifest.get('texture_errors'):
        violations.append('texture manifest is not the exact 54-material error-free checkpoint')

    sr=next((x for x in census.get('shaders',[]) if x.get('shader')==SHADER),None)
    if not sr: violations.append(f'{SHADER} absent from shader census')
    else:
        if sr.get('stages')!=['ps']: violations.append(f'{SHADER} is not PS-only')
        if sr.get('gcn_sha256')!=GCN_SHA: violations.append('GCN SHA mismatch')
        if sr.get('native_shader')!=NATIVE_SHADER: violations.append('native shader tag mismatch')
        if sr.get('gcn_bytes')!=752: violations.append('GCN byte size mismatch')
        if sr.get('instruction_count_approx')!=155: violations.append('instruction count mismatch')
        slots=[(x.get('usage_name'),x.get('api_slot'),x.get('start_register')) for x in sr.get('usage',{}).get('slots',[])]
        expected=[
            ('PtrExtendedUserData',1,2),('ImmResource',0,4),('ImmSampler',1,12),
            ('ImmResource',1,16),('ImmResource',2,24),('ImmSampler',2,32),
            ('ImmSampler',3,36),('ImmConstBuffer',0,40),('ImmConstBuffer',12,44),
        ]
        if slots!=expected: violations.append(f'user-data usage mismatch: {slots!r}')

    ir=next((x for x in images.get('shaders',[]) if x.get('shader')==SHADER),None)
    if not ir: violations.append(f'{SHADER} absent from image usage')
    else:
        if ir.get('image_instruction_count')!=4: violations.append('expected exactly 4 image instructions')
        if ir.get('used_texture_indices')!=[0,1,2]: violations.append('expected exact used texture indices [0,1,2]')
        if ir.get('texture_instruction_counts')!={'0':1,'1':1,'2':2}: violations.append('texture instruction counts mismatch')
        if ir.get('image_opcodes')!={'image_sample':2,'image_get_lod':1,'image_sample_l':1}: violations.append('image opcode census mismatch')
        if ir.get('unmatched_image_instruction_count')!=0: violations.append('unmatched image instruction')

    for needle in ANCHORS:
        if needle not in asm: violations.append(f'missing disassembly anchor: {needle}')

    rows={m:state.get('materials',{}).get(m) for m in MEMBERS}
    consumed_values={}
    for mh,row in rows.items():
        if not row:
            violations.append(f'missing material {mh}'); continue
        ps=row['ps']
        if ps.get('shader')!=SHADER: violations.append(f'{mh}: PS mismatch')
        if row.get('material_state4_hex')!='00000000': violations.append(f'{mh}: material state4 mismatch')
        if ps['tfx_bytecode'].get('bytes_hex')!=TFX_HEX: violations.append(f'{mh}: TFX bytes mismatch')
        if ps.get('tfx_disassembly',{}).get('complete') is not True: violations.append(f'{mh}: TFX framing incomplete')
        if [x['raw_hex'] for x in ps['cbuffers']['items']]!=CBUFFER_BY_MATERIAL[mh]: violations.append(f'{mh}: full CBuffer payload mismatch')
        if [x['first_dword_hex'] for x in ps['samplers']['items']]!=SAMPLERS: violations.append(f'{mh}: sampler tag sequence mismatch')
        refs=ps.get('sampler_references',[])
        if len(refs)!=3: violations.append(f'{mh}: sampler reference count mismatch')
        else:
            got=[(r.get('native_sampler') or {}).get('payload_sha256') for r in refs]
            if got!=SAMPLER_PAYLOAD_SHAS: violations.append(f'{mh}: native sampler descriptor sequence mismatch')
        tex=ps['textures']['items']
        if [x['texture_index'] for x in tex]!=[0,1,2]: violations.append(f'{mh}: texture slot sequence mismatch')
        if [x['texture'] for x in tex]!=TEXTURES[mh]: violations.append(f'{mh}: texture TagHash sequence mismatch')
        for slot,expected in [(0,('BC1','sRGB')),(1,('BC5','linear')),(2,('RGBA8','linear'))]:
            tag=TEXTURES[mh][slot]; tr=manifest.get('textures',{}).get(tag)
            if not tr: violations.append(f'{mh}: missing texture manifest row {tag}'); continue
            if (tr.get('format_name'),tr.get('native_colorspace_hint'))!=expected:
                violations.append(f'{mh}: t{slot} format/colorspace mismatch for {tag}')
        cube=manifest.get('textures',{}).get('80AACC28') or {}
        hi=cube.get('header_info') or {}
        if (hi.get('width'),hi.get('height'),hi.get('depth'),hi.get('array_size'))!=(64,64,1,6):
            violations.append(f'{mh}: fixed t2 cube header mismatch')
        if len(cube.get('faces') or [])!=6: violations.append(f'{mh}: fixed t2 cube does not expose six faces')
        cb=flatten_cb(ps)
        needed={i:cb[i] for i in [0,1,16,20,24,25,28,29,36,37]}
        expected_needed={0:2.0,1:-1.0,16:3.0,20:0.0,24:0.0,25:0.05000000074505806,28:1.0,29:1.0,36:0.5,37:0.020588235929608345}
        if needed!=expected_needed: violations.append(f'{mh}: consumed CBuffer dwords mismatch: {needed!r}')
        consumed_values[mh]=needed

    if violations:
        out={'schema_version':1,'status':'D1_XUR_PS_808764AA_DATAFLOW_SEMANTICS_PARTIAL','violations':violations}
        a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
        print(json.dumps(out,indent=2));return 2

    out={
      'schema_version':1,
      'status':'D1_XUR_PS_808764AA_DATAFLOW_SEMANTICS_EXACT',
      'shader':SHADER,'native_shader':NATIVE_SHADER,'gcn_sha256':GCN_SHA,
      'scope_materials':MEMBERS,'scope_material_count':len(MEMBERS),
      'exact_inputs':{
        'texture_triplets_t0_t1_t2':TEXTURES,
        'texture_slot_formats':{
          't0':{'format':'BC1','native_colorspace':'sRGB','instruction_role':'surface RGB term used directly and again in the reflected-cube contribution'},
          't1':{'format':'BC5','native_colorspace':'linear','instruction_role':'signed XY normal-vector source'},
          't2':{'format':'RGBA8','native_colorspace':'linear','dimensions':[64,64],'array_size':6,'instruction_role':'six-face cube resource sampled from the reflected view vector; RGB and alpha both contribute to MRT0'},
        },
        'sampler_taghash_sequence':SAMPLERS,
        'native_sampler_payload_sha256_sequence':SAMPLER_PAYLOAD_SHAS,
        'tfx_bytes_hex':TFX_HEX,
        'tfx_semantics_complete':False,
        'consumed_material_b0_dwords':consumed_values,
        'api12_camera_semantics_dependency':{
          'dwords':[28,29,30],
          'meaning':'camera/view position',
          'evidence':'already retail-closed by notes/D1_TOWER_809DCD66_NATIVE_SHADER_PROOF.md using the same api12 dwords and attr4 world-position subtraction pattern',
        },
      },
      'instruction_level_equations':{
        'sample_coordinates':'t0 and t1 consume interpolated attr3.xy. t2 is addressed by native cube-coordinate instructions from the reflected view vector.',
        'normal_xy_symbolic':'nx = t1.r * b0[0] + b0[1]; ny = t1.g * b0[0] + b0[1]',
        'normal_xy_current_source_constants':'nx = 2*t1.r - 1; ny = 2*t1.g - 1',
        'normal_z':'nz = sqrt(saturate(1 - nx*nx - ny*ny))',
        'basis_transform':'Nraw = nx*attr1.xyz + ny*attr2.xyz + nz*attr0.xyz; N = normalize(Nraw)',
        'view_vector':'V = normalize(api12[28:30] - attr4.xyz)',
        'reflection_vector':'R = 2*dot(N,V)*N - V = reflect(-V,N)',
        'cube_lod_floor_symbolic':'lod_floor = b0[16] + b0[36]*(b0[20] - b0[16])',
        'cube_lod_floor_current_source_value':'lod_floor = 1.5',
        'cube_explicit_lod':'L = max(image_get_lod(t2, R).y, lod_floor); cube = sample_l(t2, R, L)',
        'reflection_strength_symbolic':'reflection_strength = cube.a * (b0[24] + b0[36]*b0[25])',
        'reflection_strength_current_source_constants':'reflection_strength = 0.025 * cube.a',
        'mrt0_rgb_symbolic':'mrt0.rgb = t0.rgb + (b0[29] + b0[28]*t0.rgb) * cube.rgb * reflection_strength',
        'mrt0_rgb_current_source_constants':'mrt0.rgb = t0.rgb + (1 + t0.rgb) * cube.rgb * cube.a * 0.025',
        'mrt0_alpha':'mrt0.a = attr0.w',
        'normal_packing_scale_symbolic':'k = b0[25] + 0.125*b0[36]',
        'normal_packing_scale_current_source_value':'k = 0.1125',
        'mrt1_rgb':'mrt1.rgb = saturate(0.5 + k*N.xyz)',
        'mrt1_alpha_symbolic':'mrt1.a = b0[37]',
        'mrt1_alpha_current_source_value':'mrt1.a = 0.020588235929608345',
      },
      'promoted_texture_semantics':{
        't1':'normal XY is instruction-proven by signed remap, hemisphere Z reconstruction, interpolated-basis transform and normalization',
        't2':'reflection cube lookup is instruction-proven by camera-to-world-position view construction, reflect(-V,N), native cube address generation, six-face resource shape, image_get_lod and explicit-LOD cube sampling',
        't0':'surface RGB source is instruction-proven; higher-level albedo/base-color naming remains withheld because the native output also adds a view-dependent cube term',
      },
      'pixel_shader_dataflow_complete_for_scoped_binary':True,
      'tfx_producer_semantics_complete':False,
      'render_target_high_level_semantics_complete':False,
      'portable_material_recreation_complete':False,
      'violations':[],
      'policy':'Equations are promoted only from the exact pinned GCN binary, exact current local state/resources, and the separately retail-closed api12 camera-position semantic. PBR naming, TFX Unk49 meaning, blend/depth/raster state, high-level MRT naming and full portable rendering remain outside this proof.',
    }
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ['status','shader','gcn_sha256','scope_material_count','instruction_level_equations','promoted_texture_semantics','pixel_shader_dataflow_complete_for_scoped_binary','violations']},indent=2))
    return 0

if __name__=='__main__': raise SystemExit(main())
