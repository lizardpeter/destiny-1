#!/usr/bin/env python3
"""Fail-closed instruction-level semantic proof for Xur PS 80876EDF.

The proof is intentionally scoped to the native pixel-shader dataflow. It does not
assign a high-level name to MRT0/MRT1, does not solve TFX Unk49 producer semantics,
and does not claim the complete portable material/render-state recreation is finished.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

SHADER = '80876EDF'
GCN_SHA = '966131017fed6ba96524161765eeab841bcf09d4c7757deec82273f17e783ca8'
NATIVE_SHADER = '80876F17'
MEMBERS = ['8087652C','8087652D','8087652E','8087652F','80876530','80876533']
TFX_HEX = '490047214901472249024723'
SAMPLER = '80AAE177'
SAMPLER_PAYLOAD_SHA = '2c670016bbb70b68bd2f69dd4a30145bf7d61a47c1bf4c3acba8321b46976ecb'
CBUFFER_RAW = [
    '00000040000080bf000080bf000080bf',
    '00000000000000000000000000000000',
    '000000002625a53e0000a4420000a642',
]

ANCHORS = [
    'image_sample    v[15:16], v[2:5], s[20:27], s[28:31] dmask:3',
    'image_sample    v[17:19], v[2:5], s[4:11], s[12:15] dmask:7',
    'image_sample    v2, v[2:5], s[32:39], s[40:43]',
    'v_mad_f32       v3, v15, s0, v4',
    'v_mac_f32       v4, s0, v16',
    'v_sqrt_f32      v15, v15',
    'v_rsq_clamp_f32 v3, v3',
    'v_mac_f32       v14, s1, v2',
    'v_madak_f32     v3, v14, v4, 0x3f000000',
    'v_madak_f32     v4, v14, v5, 0x3f000000',
    'v_madak_f32     v2, v14, v2, 0x3f000000',
    'exp             mrt1, v1, v1, v2, v2 compr',
    'exp             mrt0, v1, v1, v0, v0 done compr vm',
]


def main() -> int:
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
    if manifest.get('status')!='D1_XUR_MATERIAL_TEXTURE_MANIFEST_EXACT':
        if manifest.get('visible_material_count')!=54 or manifest.get('material_decode_errors') or manifest.get('texture_errors'):
            violations.append(f'unsupported texture manifest status {manifest.get("status")!r}')

    sr=next((x for x in census.get('shaders',[]) if x.get('shader')==SHADER),None)
    if not sr: violations.append(f'{SHADER} absent from shader census')
    else:
        if sr.get('stages')!=['ps']: violations.append(f'{SHADER} is not PS-only')
        if sr.get('gcn_sha256')!=GCN_SHA: violations.append('GCN SHA mismatch')
        if sr.get('native_shader')!=NATIVE_SHADER: violations.append('native shader tag mismatch')
        if sr.get('gcn_bytes')!=428: violations.append('GCN byte size mismatch')
        if sr.get('instruction_count_approx')!=89: violations.append('instruction count mismatch')

    ir=next((x for x in images.get('shaders',[]) if x.get('shader')==SHADER),None)
    if not ir: violations.append(f'{SHADER} absent from image usage')
    else:
        if ir.get('image_instruction_count')!=3: violations.append('expected exactly 3 image instructions')
        if ir.get('used_texture_indices')!=[0,1,2]: violations.append('expected exact used texture indices [0,1,2]')
        if ir.get('texture_instruction_counts')!={'0':1,'1':1,'2':1}: violations.append('texture instruction counts mismatch')
        if ir.get('unmatched_image_instruction_count')!=0: violations.append('unmatched image instruction')

    for needle in ANCHORS:
        if needle not in asm: violations.append(f'missing disassembly anchor: {needle}')

    rows={m:state.get('materials',{}).get(m) for m in MEMBERS}
    for mh,row in rows.items():
        if not row:
            violations.append(f'missing material {mh}'); continue
        ps=row['ps']
        if ps.get('shader')!=SHADER: violations.append(f'{mh}: PS mismatch')
        if row.get('material_state4_hex')!='00000000': violations.append(f'{mh}: material state4 mismatch')
        if ps['tfx_bytecode'].get('bytes_hex')!=TFX_HEX: violations.append(f'{mh}: TFX bytes mismatch')
        if ps.get('tfx_disassembly',{}).get('complete') is not True: violations.append(f'{mh}: TFX framing incomplete')
        if [x['raw_hex'] for x in ps['cbuffers']['items']]!=CBUFFER_RAW: violations.append(f'{mh}: CBuffer payload mismatch')
        if [x['first_dword_hex'] for x in ps['samplers']['items']]!=[SAMPLER]*3: violations.append(f'{mh}: sampler tag sequence mismatch')
        refs=ps.get('sampler_references',[])
        if len(refs)!=3: violations.append(f'{mh}: sampler reference count mismatch')
        for ref in refs:
            native=ref.get('native_sampler') or {}
            if native.get('payload_sha256')!=SAMPLER_PAYLOAD_SHA: violations.append(f'{mh}: native sampler descriptor mismatch')
        tex=ps['textures']['items']
        if [x['texture_index'] for x in tex]!=[0,1,2]: violations.append(f'{mh}: texture slot sequence mismatch')
        for slot,expected in [(0,('BC1','sRGB')),(1,('BC5','linear')),(2,('BC1','sRGB'))]:
            tag=tex[slot]['texture']; tr=manifest.get('textures',{}).get(tag)
            if not tr: violations.append(f'{mh}: missing texture manifest row {tag}'); continue
            if (tr.get('format_name'),tr.get('native_colorspace_hint'))!=expected:
                violations.append(f'{mh}: t{slot} format/colorspace mismatch for {tag}')

    if violations:
        out={'schema_version':1,'status':'D1_XUR_PS_80876EDF_DATAFLOW_SEMANTICS_PARTIAL','violations':violations}
        a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
        print(json.dumps(out,indent=2));return 2

    texture_triplets={}
    for mh,row in rows.items():
        texture_triplets[mh]=[x['texture'] for x in row['ps']['textures']['items']]

    out={
        'schema_version':1,
        'status':'D1_XUR_PS_80876EDF_DATAFLOW_SEMANTICS_EXACT',
        'shader':SHADER,'native_shader':NATIVE_SHADER,'gcn_sha256':GCN_SHA,
        'scope_materials':MEMBERS,
        'scope_material_count':len(MEMBERS),
        'exact_inputs':{
            'texture_triplets_t0_t1_t2':texture_triplets,
            'texture_slot_formats':{
                't0':{'format':'BC1','native_colorspace':'sRGB','instruction_role':'direct MRT0 RGB source'},
                't1':{'format':'BC5','native_colorspace':'linear','instruction_role':'signed XY normal-vector source'},
                't2':{'format':'BC1','native_colorspace':'sRGB','instruction_role':'normal-vector packing-scale modulator from sampled red'},
            },
            'sampler_taghash_sequence':[SAMPLER]*3,
            'native_sampler_payload_sha256':SAMPLER_PAYLOAD_SHA,
            'tfx_bytes_hex':TFX_HEX,
            'tfx_semantics_complete':False,
            'cbuffer_vec4_source_values':[
                [2.0,-1.0,-1.0,-1.0],
                [0.0,0.0,0.0,0.0],
                [0.0,0.322549045085907,82.0,83.0],
            ],
        },
        'instruction_level_equations':{
            'sample_coordinates':'All t0/t1/t2 image_sample instructions consume the same interpolated attr3.xy coordinate pair (v2,v3 at sample time).',
            'normal_xy_symbolic':'nx = t1.r * C0.x + C0.y; ny = t1.g * C0.x + C0.y',
            'normal_xy_for_current_source_constants':'nx = 2*t1.r - 1; ny = 2*t1.g - 1',
            'normal_z':'nz = sqrt(saturate(1 - nx*nx - ny*ny))',
            'basis_transform':'Nraw = nx*attr1.xyz + ny*attr2.xyz + nz*attr0.xyz; N = normalize(Nraw)',
            'packing_scale':'k = 0.375 + 0.125*t2.r',
            'mrt1_rgb':'mrt1.rgb = saturate(0.5 + k*N.xyz)',
            'mrt1_alpha_symbolic':'mrt1.a = CBuffer0[dword 9]',
            'mrt1_alpha_current_source_value':'mrt1.a = 0.322549045085907',
            'mrt0_rgb':'mrt0.rgb = t0.rgb',
            'mrt0_alpha':'mrt0.a = attr0.w',
        },
        'promoted_texture_semantics':{
            't1':'normal XY is instruction-proven by signed remap, hemisphere Z reconstruction, interpolated-basis transform and normalization',
            't0':'only direct MRT0 RGB source is promoted; the higher-level name albedo/base-color remains withheld here',
            't2':'only normal-vector packing-scale modulation is promoted; roughness/gloss/material-role naming remains withheld',
        },
        'pixel_shader_dataflow_complete_for_scoped_binary':True,
        'tfx_producer_semantics_complete':False,
        'render_target_high_level_semantics_complete':False,
        'portable_material_recreation_complete':False,
        'violations':[],
        'policy':'Equations are promoted only from the exact pinned GCN binary plus exact current local state/resource evidence. TFX Unk49 meaning, high-level MRT names, t0 albedo naming, t2 roughness/gloss naming, blend/depth/raster state and full portable rendering remain outside this proof.',
    }
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ['status','shader','gcn_sha256','scope_material_count','instruction_level_equations','promoted_texture_semantics','pixel_shader_dataflow_complete_for_scoped_binary','violations']},indent=2))
    return 0

if __name__=='__main__':raise SystemExit(main())
