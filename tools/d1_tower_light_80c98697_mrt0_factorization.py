#!/usr/bin/env python3
"""Fail-closed terminal MRT0 factorization for singleton Tower light PS 80C98697.

This shader also writes MRT1.  The proof below isolates MRT0 only and deliberately
keeps several upstream geometric/native scalar branches anonymous while proving the
exact final factorization, texture leaves, cbuffer leaves, and dead inputs.

No human semantic is assigned to renderer textures, native input VGPRs, gates, or
MRT1 behavior.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

SHADER='80C98697'
NATIVE='80C987AC'
NATIVE_SHA='017533849b4130cc5033aaa419e96831c866ee0473d2ea51724ea5e89415c9ee'
GCN_SHA='e4e89e21b1fd25f031ada92efc2df3319368080b623f45fd5d274c1446f923b2'
GCN_BYTES=1236
EXPECTED_TERMINAL='0000000004C8'
EXPECTED_IMAGE=[
    ('000000000040','image_load_mip',[1],'x'),
    ('000000000048','image_sample',[0],'xyzw'),
    ('0000000002D4','image_sample_lz',[3],'x'),
    ('0000000002E8','image_sample_lz',[2],'xy'),
    ('0000000002FC','image_sample_lz',[3],'x'),
    ('00000000030C','image_sample_lz',[3],'x'),
]
EXPECTED_LOADS={
    '000000000018':(12,[48,49,50,51],[16,17,18,19]),
    '000000000058':(0,[24,25,26,27],[8,9,10,11]),
    '00000000005C':(0,[12,13,14,15],[12,13,14,15]),
    '000000000060':(0,[16,17,18,19],[16,17,18,19]),
    '000000000064':(0,[20,21,22,23],[20,21,22,23]),
    '000000000068':(0,[28,29,30,31],[24,25,26,27]),
    '0000000000AC':(0,[60,61,62,63],[8,9,10,11]),
    '0000000000DC':(0,[48,49,50,51],[12,13,14,15]),
    '0000000000F4':(0,[36,37,38,39],[16,17,18,19]),
    '0000000001E8':(0,[56],[0]),
    '000000000248':(0,[44],[1]),
    '000000000274':(0,[32],[2]),
    '00000000031C':(0,[68,69],[10,11]),
    '000000000320':(0,[64,65,66,67],[20,21,22,23]),
    '000000000330':(0,[88,89,90,91],[24,25,26,27]),
    '000000000350':(0,[52,53,54,55],[28,29,30,31]),
    '000000000370':(0,[40,41,42,43],[32,33,34,35]),
    '000000000374':(0,[92],[0]),
    '000000000378':(0,[97],[3]),
}
DEAD_API0=[31,39,43,51,55,63,67,91,97]

def norm(x):return str(x).upper().removeprefix('0X').zfill(8)

def main():
    ap=argparse.ArgumentParser()
    for n in ('material-manifest','shader-report','image-usage','cbuffer-usage','terminal-mrt0','disasm','out'):
        ap.add_argument('--'+n,type=Path,required=True)
    a=ap.parse_args()
    v=[]
    m=json.loads(a.material_manifest.read_text())
    s=json.loads(a.shader_report.read_text())
    i=json.loads(a.image_usage.read_text())
    c=json.loads(a.cbuffer_usage.read_text())
    t=json.loads(a.terminal_mrt0.read_text())
    asm=a.disasm.read_text(errors='replace')

    mats=(m.get('pixel_shader_materials') or {}).get(SHADER,[])
    if int((m.get('pixel_shader_frequency') or {}).get(SHADER,-1))!=1 or len(mats)!=1:
        v.append('frequency/material count drift')
    if any(int((m.get('materials') or {}).get(x,{}).get('ps_texture_count',-1))!=0 for x in mats):
        v.append('serialized PS texture binding unexpectedly present')

    sr=next((x for x in s.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
    if not sr or s.get('status')!='D1_WORLD_PIXEL_SHADER_GCN_EXACT':
        v.append('shader report not exact')
    else:
        for k,z in {
            'native_shader':NATIVE,
            'native_sha256':NATIVE_SHA,
            'gcn_sha256':GCN_SHA,
            'gcn_bytes':GCN_BYTES,
        }.items():
            if sr.get(k)!=z:v.append(f'{k} drift')

    ir=next((x for x in i.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
    gotimg=[] if not ir else [
        (x['address'],x['opcode'],[q['texture_index'] for q in x.get('resources',[])],x['dmask_channels'])
        for x in ir.get('instructions',[])
    ]
    if gotimg!=EXPECTED_IMAGE:v.append(f'image provenance drift {gotimg}')

    cr=next((x for x in c.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
    if not cr:
        v.append('cbuffer row missing')
    else:
        by={x['address']:x for x in cr.get('loads',[])}
        for addr,(api,dw,dst) in EXPECTED_LOADS.items():
            q=by.get(addr)
            if not q or q.get('api_slot')!=api or q.get('dword_indices')!=dw or q.get('destination')!=dst:
                v.append(f'{addr}: cbuffer drift {q}')

    tr=next((x for x in t.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
    if not tr or t.get('status')!='D1_GCN_TERMINAL_MRT0_DEPENDENCY_CENSUS_EXACT':
        v.append('terminal slice missing/not exact')
    else:
        if tr.get('terminal_mrt0_export_address')!=EXPECTED_TERMINAL:
            v.append('terminal export address drift')
        if tr.get('terminal_mrt0_operands')!=['v0','v0','v1','v1'] or not tr.get('terminal_mrt0_compressed'):
            v.append('terminal export operand/compression drift')

        texreq={
            (0,'x','000000000048'),
            (0,'y','000000000048'),
            (0,'z','000000000048'),
            (1,'x','000000000040'),
            (2,'y','0000000002E8'),
        }
        channel_coeff={'R':(64,88,52,40),'G':(65,89,53,41),'B':(66,90,54,42)}
        for ch,coeff in channel_coeff.items():
            q=tr['channels'][ch]['value_slice']
            tex={(int(x['texture_index']),x['channel'],x['sample_address']) for x in q.get('texture_sample_channels',[])}
            if tex!=texreq:v.append(f'{ch}: texture leaf drift {sorted(tex)}')
            cbq={str(k):set(z) for k,z in (q.get('cbuffer_dwords') or {}).items()}
            if set(cbq)-{'0'}:v.append(f'{ch}: non-API0 cbuffer reaches MRT0 {cbq}')
            req=set(coeff)|{12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,32,36,37,38,44,48,49,50,56,60,61,62,68,69,92}
            if not req.issubset(cbq.get('0',set())):v.append(f'{ch}: required cbuffer leaves missing {cbq}')
            if q.get('unknown_registers')!=['v2','v3']:
                v.append(f'{ch}: native input frontier drift {q.get("unknown_registers")}')

        aq=tr['channels']['A']['value_slice']
        if aq.get('literals')!=['0'] or aq.get('texture_sample_channels') or aq.get('cbuffer_dwords') or aq.get('unknown_registers'):
            v.append('alpha drift')

        union=tr.get('mrt0_value_union') or {}
        api0=set((union.get('cbuffer_dwords') or {}).get('0',[]))
        alltex={(int(x['texture_index']),x['channel'],x['sample_address']) for x in union.get('texture_sample_channels',[])}
        if (0,'w','000000000048') in alltex:v.append('t0 alpha reaches MRT0')
        if (2,'x','0000000002E8') in alltex:v.append('t2.x reaches MRT0')
        if any(x[0]==3 for x in alltex):v.append('t3 sample reaches MRT0')
        for dead in DEAD_API0:
            if dead in api0:v.append(f'API0[{dead}] reaches MRT0')
        if '12' in (union.get('cbuffer_dwords') or {}):v.append('API12 reaches MRT0')

    anchors=[
        '/*00000000037c: d2820801 04060105*/ v_mad_f32       v1, v5, v0, v1 clamp',
        '/*000000000388: d2060804 0001e10d*/ v_add_f32       v4, v13, 0.5 clamp',
        '/*0000000003ac: 10080904         */ v_mul_f32       v4, v4, v4',
        '/*0000000003d4: 10022501         */ v_mul_f32       v1, v1, v18',
        '/*0000000003dc: 10140814         */ v_mul_f32       v10, s20, v4',
        '/*0000000003e0: 10180815         */ v_mul_f32       v12, s21, v4',
        '/*0000000003e4: 10080816         */ v_mul_f32       v4, s22, v4',
        '/*0000000003f4: d206080b 0001e10b*/ v_add_f32       v11, v11, 0.5 clamp',
        '/*000000000408: d2820808 04201509*/ v_mad_f32       v8, v9, s10, v8 clamp',
        '/*000000000410: 1012170b         */ v_mul_f32       v9, v11, v11',
        '/*00000000042c: 3e140218         */ v_mac_f32       v10, s24, v1',
        '/*000000000430: 3e180219         */ v_mac_f32       v12, s25, v1',
        '/*000000000434: 3e08021a         */ v_mac_f32       v4, s26, v1',
        '/*000000000444: 10001108         */ v_mul_f32       v0, v8, v8',
        '/*000000000454: 3e14121c         */ v_mac_f32       v10, s28, v9',
        '/*000000000458: 3e18121d         */ v_mac_f32       v12, s29, v9',
        '/*00000000045c: 3e08121e         */ v_mac_f32       v4, s30, v9',
        '/*00000000046c: 3e140220         */ v_mac_f32       v10, s32, v1',
        '/*000000000470: 3e180221         */ v_mac_f32       v12, s33, v1',
        '/*000000000474: 3e080222         */ v_mac_f32       v4, s34, v1',
        '/*000000000484: 10020000         */ v_mul_f32       v1, s0, v0',
        '/*00000000048c: 1004030a         */ v_mul_f32       v2, v10, v1',
        '/*000000000490: 1006030c         */ v_mul_f32       v3, v12, v1',
        '/*000000000494: 10020304         */ v_mul_f32       v1, v4, v1',
        '/*0000000004c8: f8001c0f 00000100*/ exp             mrt0, v0, v0, v1, v1 done compr vm',
    ]
    miss=[x for x in anchors if x not in asm]
    if miss:v.append(f'missing anchors {miss}')

    out={
        'schema':'d1_tower_light_80c98697_mrt0_factorization/v1',
        'status':'D1_TOWER_LIGHT_80C98697_MRT0_FACTORIZATION_EXACT' if not v else 'D1_TOWER_LIGHT_80C98697_MRT0_FACTORIZATION_PARTIAL',
        'shader':SHADER,
        'instance_count':1,
        'unique_material_count':len(mats),
        'exact_terminal_equation':{
            'A':'G56^2, where G56 is the exact native clamped scalar in v4 at 0x388 before squaring at 0x3AC',
            'P':'exact native clamped scalar in v1 at 0x37C',
            'T':'t2.y sampled at 0x2E8',
            'B':'G44^2, where G44 is the exact native clamped scalar in v11 at 0x3F4 before squaring at 0x410',
            'H':'clamp(API0[68]*B + API0[69]) at 0x408',
            'vector_pre_scale':'V.rgb = API0[64:66].rgb*A + (API0[88:90].rgb + API0[40:42].rgb)*(P*T) + API0[52:54].rgb*B',
            'scalar_scale':'K = API0[92] * H^2',
            'mrt0_rgb':'MRT0.rgb = V.rgb * K',
            'mrt0_a':'0',
            'vector_form':'MRT0.rgb = [API0[64:66]*A + (API0[88:90]+API0[40:42])*(P*t2.y) + API0[52:54]*B] * API0[92] * H^2',
        },
        'native_input_frontier':['v2','v3'],
        'renderer_texture_value_frontier':['t0.rgb','t1.x','t2.y'],
        'negative_proof':{
            't0_alpha_reaches_mrt0':False,
            't2_x_reaches_mrt0':False,
            'any_t3_sample_reaches_mrt0':False,
            **{f'api0_dword{d}_reaches_mrt0':False for d in DEAD_API0},
            'api12_reaches_mrt0':False,
        },
        'mrt1_boundary':'SHADER_WRITES_MRT1_BUT_THIS_PROOF_DOES_NOT_ASSIGN_OR_REDUCE_MRT1_SEMANTICS',
        'semantic_boundary':{
            'terminal_arithmetic':'EXACT_NATIVE_GCN',
            'renderer_resource_human_semantics':'WITHHELD',
            'native_input_v2_v3_semantics':'WITHHELD',
            'upstream_gate_human_meanings':'WITHHELD',
            'mrt1_semantics':'WITHHELD',
        },
        'violations':v,
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'status':out['status'],'equation':out['exact_terminal_equation'],'negative_proof':out['negative_proof'],'violations':v},indent=2))
    return 0 if not v else 2

if __name__=='__main__':raise SystemExit(main())
