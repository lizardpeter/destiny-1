#!/usr/bin/env python3
"""Fail-closed algebraic texture-role proof for D1 Tower common PS 80CA0F50.

The proof is intentionally semantic-conservative. It promotes only roles that are
forced by native GCN dataflow. It does not call any source albedo/normal/PBR.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path

SHADER='80CA0F50'
NATIVE_SHADER='80CA0F54'
NATIVE_SHA='fe478898a946ccfe848ca5715e5a8b45802b5e7dfe997aeeb067f92f125e66ae'
GCN_SHA='9285c9d5e22fac8917a5430bae251be441b1fe68bc99b976e51b268ee7b56141'
MATERIALS=['80C99CE9','80CA0F46']
TEXTURES={0:'80CA0F31',1:'80CA0F32',2:'80CA0F31'}
EXPECTED_IMAGE=[
    ('00000000005C','image_sample',1,2,7),
    ('000000000064','image_sample',0,1,7),
    ('000000000070','image_sample',2,3,7),
]
EXPECTED_CHANNELS={
    'R':{'0':[8,12,20,24,28,32,36,40],'13':[6,7],
         'samples':[(0,'x','000000000064'),(1,'x','00000000005C'),(2,'x','000000000070')]},
    'G':{'0':[9,13,21,25,29,33,37,40],'13':[6,7],
         'samples':[(0,'y','000000000064'),(1,'y','00000000005C'),(2,'y','000000000070')]},
    'B':{'0':[10,14,22,26,30,34,38,40],'13':[6,7],
         'samples':[(0,'z','000000000064'),(1,'z','00000000005C'),(2,'z','000000000070')]},
}
ANCHORS=[
    'v_mad_f32       v4, v9, s20, v1',
    'v_mad_f32       v5, v10, s21, v3',
    'image_sample    v[3:5], v[4:7], s[24:31], s[32:35] dmask:7',
    'image_sample    v[6:8], v[9:12], s[4:11], s[12:15] dmask:7',
    'image_sample    v[0:2], v[9:12], s[36:43], s[20:23] dmask:7',
    'v_mul_f32       v3, s4, v3',
    'v_mul_f32       v3, s8, v3',
    'v_mul_f32       v3, s12, v3',
    'v_mul_f32       v3, s20, v3',
    'v_mul_f32       v10, s24, v9',
    'v_mul_f32       v6, s28, v6',
    'v_mul_f32       v0, v0, v3',
    'v_mul_f32       v3, s1, v10',
    'v_mac_f32       v0, s16, v6',
    'v_mul_f32       v3, s0, v3',
    'v_mul_f32       v0, v0, v3',
    'v_mov_b32       v3, 0',
    'v_cvt_pkrtz_f16_f32 v0, v0, v1',
    'v_cvt_pkrtz_f16_f32 v1, v2, v3',
    'exp             mrt0, v0, v0, v1, v1 done compr vm',
]
ROLES={
    0:'surface_rgb_additive_branch_pre_global_scale',
    1:'surface_rgb_affine_uv_multiplicative_modulation_of_t2',
    2:'surface_rgb_multiplicative_branch_with_t1',
}

def norm(x): return str(x).upper().removeprefix('0X').zfill(8)

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--extract-report',type=Path,required=True)
    ap.add_argument('--image-usage',type=Path,required=True)
    ap.add_argument('--cbuffer-usage',type=Path,required=True)
    ap.add_argument('--mrt0-deps',type=Path,required=True)
    ap.add_argument('--manifest',type=Path,required=True)
    ap.add_argument('--disassembly',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()

    ex=json.loads(a.extract_report.read_text())
    im=json.loads(a.image_usage.read_text())
    cb=json.loads(a.cbuffer_usage.read_text())
    de=json.loads(a.mrt0_deps.read_text())
    ma=json.loads(a.manifest.read_text())
    asm=a.disassembly.read_text(errors='replace')
    viol=[]

    if ex.get('status')!='D1_WORLD_PIXEL_SHADER_GCN_EXACT': viol.append('shader extraction report not exact')
    if im.get('status')!='D1_GCN_IMAGE_RESOURCE_USAGE_EXACT': viol.append('image usage report not exact')
    if cb.get('status')!='D1_GCN_CBUFFER_USAGE_EXACT': viol.append('cbuffer usage report not exact')
    if de.get('status')!='D1_GCN_TERMINAL_MRT0_DEPENDENCY_CENSUS_EXACT': viol.append('terminal dependency report not exact')
    if ma.get('material_decode_errors') or ma.get('texture_errors'): viol.append('material/texture manifest has decode errors')

    sr=next((x for x in ex.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
    if not sr: viol.append('shader absent from extraction report')
    else:
        checks={
            'native_shader':NATIVE_SHADER,'native_sha256':NATIVE_SHA,'gcn_sha256':GCN_SHA,
            'gcn_bytes':344,'visible_material_count':2,
        }
        for k,v in checks.items():
            if sr.get(k)!=v: viol.append(f'{k} mismatch: {sr.get(k)!r}')
        slots=[(x.get('usage_name'),int(x.get('api_slot',-1)),int(x.get('start_register',-1))) for x in sr.get('usage',{}).get('slots',[])]
        expected_slots=[
            ('PtrExtendedUserData',1,2),('ImmResource',0,4),('ImmSampler',1,12),
            ('ImmResource',1,16),('ImmResource',2,24),('ImmSampler',2,32),
            ('ImmSampler',3,36),('ImmConstBuffer',0,40),('ImmConstBuffer',13,44),
        ]
        if slots!=expected_slots: viol.append(f'user-data usage mismatch: {slots!r}')

    ir=next((x for x in im.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
    if not ir: viol.append('image usage absent')
    else:
        got=[]
        for row in ir.get('instructions',[]):
            rr=row.get('resources') or []; ss=row.get('samplers') or []
            got.append((row.get('address'),row.get('opcode'),rr[0].get('texture_index') if len(rr)==1 else None,
                        ss[0].get('sampler_index') if len(ss)==1 else None,row.get('dmask')))
        if got!=EXPECTED_IMAGE: viol.append(f'image sequence mismatch: {got!r}')
        if ir.get('used_texture_indices')!=[0,1,2] or ir.get('unmatched_image_instruction_count')!=0:
            viol.append('image provenance incomplete')

    cr=next((x for x in cb.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
    if not cr: viol.append('cbuffer usage absent')
    else:
        if cr.get('unresolved_load_count')!=0: viol.append('unresolved cbuffer load')
        reads=cr.get('api_slot_read_dwords') or {}
        if reads.get('13')!=[6,7]: viol.append(f'API13 read set mismatch: {reads.get("13")!r}')
        for need in [8,9,10,12,13,14,20,21,22,24,25,26,28,29,30,32,33,34,36,37,38,40]:
            if need not in reads.get('0',[]): viol.append(f'API0 dword {need} missing')

    dr=next((x for x in de.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
    if not dr: viol.append('MRT0 dependency row absent')
    else:
        if dr.get('terminal_mrt0_compressed') is not True or dr.get('terminal_mrt0_operands')!=['v0','v0','v1','v1']:
            viol.append('terminal MRT0 export shape mismatch')
        for ch,exp in EXPECTED_CHANNELS.items():
            got=(dr.get('channels') or {}).get(ch,{}).get('value_slice') or {}
            if got.get('unknown_registers')!=[]: viol.append(f'{ch}: unknown terminal register dependency')
            if got.get('interpolants')!=[]: viol.append(f'{ch}: unexpected direct terminal interpolant')
            cbuf=got.get('cbuffer_dwords') or {}
            if cbuf.get('0')!=exp['0'] or cbuf.get('13')!=exp['13']:
                viol.append(f'{ch}: cbuffer dependency mismatch: {cbuf!r}')
            samples=[(int(x['texture_index']),x['channel'],x['sample_address']) for x in got.get('texture_sample_channels',[])]
            if samples!=exp['samples']: viol.append(f'{ch}: texture dependency mismatch: {samples!r}')
        av=(dr.get('channels') or {}).get('A',{}).get('value_slice') or {}
        if av.get('literals')!=['0'] or av.get('texture_sample_channels') or av.get('cbuffer_dwords') or av.get('unknown_registers'):
            viol.append(f'alpha is not exact literal zero: {av!r}')

    for needle in ANCHORS:
        if needle not in asm: viol.append('missing assembly anchor: '+needle)
    cursor=0
    for needle in ANCHORS:
        pos=asm.find(needle,cursor)
        if pos<0:
            viol.append('assembly anchors are not in exact dataflow order')
            break
        cursor=pos+len(needle)

    mats=ma.get('materials') or {}
    for mh in MATERIALS:
        mr=mats.get(mh)
        if not mr: viol.append('missing material '+mh); continue
        if norm(mr.get('pixel_shader'))!=SHADER: viol.append(f'{mh}: PS mismatch')
        bindings={int(x['texture_index']):norm(x['texture']) for x in mr.get('ps_texture_tags',[])}
        if bindings!=TEXTURES: viol.append(f'{mh}: texture bindings mismatch: {bindings!r}')
        if (mr.get('tfx') or {}).get('ps',{}).get('bytes_hex')!='490047214901472249024723340034013c01003402031a23030e4204':
            viol.append(f'{mh}: PS TFX bytecode mismatch')
        samplers=(mr.get('samplers') or {}).get('ps',{}).get('items',[])
        if [x.get('first_dword_hex') for x in samplers]!=['80AAE177']*3: viol.append(f'{mh}: sampler tags mismatch')
    for tag,fmt,w,h in [('80CA0F31','BC3',512,512),('80CA0F32','BC1',64,64)]:
        tr=(ma.get('textures') or {}).get(tag)
        if not tr: viol.append('missing texture '+tag); continue
        hi=tr.get('header_info') or {}
        if tr.get('format_name')!=fmt or tr.get('native_colorspace_hint')!='sRGB' or (hi.get('width'),hi.get('height'))!=(w,h):
            viol.append(f'{tag}: format/colorspace/dimensions mismatch')

    if viol:
        out={'schema':'d1_tower_common_ps_80ca0f50_semantic_proof/v1','status':'D1_TOWER_COMMON_PS_80CA0F50_SEMANTICS_PARTIAL','shader':SHADER,'violations':viol}
        a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));return 2

    equation={
        'uv0':'uv = attr0.xy',
        't1_uv':'uv1 = (api0[16]*uv.x + api0[18], api0[17]*uv.y + api0[19])',
        't1_branch_rgb':'B1 = t1.rgb * api0[20:22] * api0[24:26] * api0[28:30] * api0[32:34]',
        't0_branch_rgb':'B0 = t0.rgb * api0[8:10] * api0[12:14]',
        'pre_global_rgb':'P = t2.rgb * B1 + B0',
        'global_rgb_scale':'G = api13[6] * api13[7] * api0[40] * api0[36:38]',
        'mrt0_rgb':'MRT0.rgb = P * G',
        'mrt0_alpha':'MRT0.a = 0',
    }
    out={
        'schema':'d1_tower_common_ps_80ca0f50_semantic_proof/v1',
        'status':'D1_TOWER_COMMON_PS_80CA0F50_SEMANTICS_EXACT',
        'shader':SHADER,'native_shader':NATIVE_SHADER,'native_sha256':NATIVE_SHA,'gcn_sha256':GCN_SHA,
        'materials':MATERIALS,'texture_bindings':{str(k):v for k,v in TEXTURES.items()},
        'instruction_level_equation':equation,
        'promoted_texture_roles':{str(k):v for k,v in ROLES.items()},
        'portable_base_color_safe':False,
        'alpha_exact_zero':True,
        'semantic_boundary':'Roles are algebraic native-GCN roles only. No albedo/normal/PBR label is inferred. API0/API13 producer meanings remain separate.',
        'violations':[],
    }
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2));return 0

if __name__=='__main__': raise SystemExit(main())
