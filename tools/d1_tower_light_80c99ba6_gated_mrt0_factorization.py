#!/usr/bin/env python3
"""Fail-closed gated terminal MRT0 factorization for singleton Tower light PS 80C99BA6.

Exact native tail:
    Q = clamp(q_in*API0[48] + API0[49])
    R = clamp(-r_in*API0[72] + API0[73])
    B = b_gate^2
    P = exact native clamped scalar
    V.rgb = API0[44:46] + API0[76:78]*(P*t2.y) + API0[40:42]*B
    K = API0[80] * Q^2 * R
    G = exact API0[88:91] linear plane
    MRT0.rgb = V.rgb*K if G > 0 else 0
    MRT0.a = 0

The q/r/b/P/g inputs remain exact native symbolic intermediates. Renderer resource
human semantics are withheld.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

SHADER='80C99BA6'
NATIVE='80C99C02'
NATIVE_SHA='2d9b6010975acd43026aab08d1bb3ecfba951231c8471fb744adab53798425a2'
GCN_SHA='bfd085c59152b00fcb631510aaf203c54e11965354d37956213e88045551668d'
GCN_BYTES=1000
EXPECTED_TERMINAL='0000000003DC'
DEAD_API0=[31,39,43,47,71,79,85]

def norm(x):return str(x).upper().removeprefix('0X').zfill(8)

def main():
    ap=argparse.ArgumentParser()
    for n in ('material-manifest','shader-report','image-usage','cbuffer-usage','terminal-mrt0','disasm','out'):
        ap.add_argument('--'+n,type=Path,required=True)
    a=ap.parse_args();v=[]
    m=json.loads(a.material_manifest.read_text())
    s=json.loads(a.shader_report.read_text())
    i=json.loads(a.image_usage.read_text())
    c=json.loads(a.cbuffer_usage.read_text())
    t=json.loads(a.terminal_mrt0.read_text())
    asm=a.disasm.read_text(errors='replace')

    if m.get('status')!='D1_WORLD_LIGHT_MATERIAL_MANIFEST_COMPLETE':v.append('material manifest not exact')
    mats=(m.get('pixel_shader_materials') or {}).get(SHADER,[])
    if int((m.get('pixel_shader_frequency') or {}).get(SHADER,-1))!=1 or len(mats)!=1:
        v.append('frequency/material count drift')
    if any(int((m.get('materials') or {}).get(x,{}).get('ps_texture_count',-1))!=0 for x in mats):
        v.append('serialized PS texture binding unexpectedly present')

    sr=next((x for x in s.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
    if s.get('status')!='D1_WORLD_PIXEL_SHADER_GCN_EXACT' or not sr:
        v.append('shader report not exact/present')
    else:
        for k,z in {'native_shader':NATIVE,'native_sha256':NATIVE_SHA,'gcn_sha256':GCN_SHA,'gcn_bytes':GCN_BYTES}.items():
            if sr.get(k)!=z:v.append(f'{k} drift {sr.get(k)!r} != {z!r}')

    ir=next((x for x in i.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
    expected_img=[
        ('000000000040','image_load_mip',[1],'x'),
        ('000000000048','image_sample',[0],'xyzw'),
        ('000000000234','image_sample_lz',[2],'xy'),
        ('000000000244','image_sample_lz',[3],'x'),
    ]
    got=[] if not ir else [(x['address'],x['opcode'],[q['texture_index'] for q in x.get('resources',[])],x['dmask_channels']) for x in ir.get('instructions',[])]
    if i.get('status')!='D1_GCN_IMAGE_RESOURCE_USAGE_EXACT' or got!=expected_img:
        v.append(f'image provenance drift {got!r}')

    cr=next((x for x in c.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
    expected_loads={
        '00000000024C':(0,[68,69,70,71],[12,13,14,15]),
        '000000000250':(0,[48,49],[2,3]),
        '000000000254':(0,[72,73],[16,17]),
        '000000000258':(0,[88,89,90,91],[20,21,22,23]),
        '00000000025C':(0,[44,45,46,47],[24,25,26,27]),
        '000000000264':(0,[76,77,78,79],[28,29,30,31]),
        '000000000268':(0,[40,41,42,43],[32,33,34,35]),
        '000000000278':(0,[80],[1]),
        '00000000027C':(0,[85],[4]),
    }
    if c.get('status')!='D1_GCN_CBUFFER_USAGE_EXACT' or not cr:
        v.append('cbuffer usage not exact/present')
    else:
        by={x.get('address'):x for x in cr.get('loads',[])}
        for addr,(api,dw,dst) in expected_loads.items():
            q=by.get(addr)
            if not q or q.get('api_slot')!=api or q.get('dword_indices')!=dw or q.get('destination')!=dst:
                v.append(f'{addr}: cbuffer provenance drift {q}')

    tr=next((x for x in t.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
    if t.get('status')!='D1_GCN_TERMINAL_MRT0_DEPENDENCY_CENSUS_EXACT' or not tr:
        v.append('terminal MRT0 slice not exact/present')
    else:
        if tr.get('terminal_mrt0_export_address')!=EXPECTED_TERMINAL or not tr.get('terminal_mrt0_compressed'):
            v.append('terminal export identity drift')
        if tr.get('terminal_mrt0_operands')!=['v1','v1','v0','v0']:
            v.append(f'terminal operands drift {tr.get("terminal_mrt0_operands")}')

        family={(0,x,'000000000048') for x in 'xyz'}|{(1,'x','000000000040'),(2,'y','000000000234')}
        expected_cb={
            'R':[12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,32,36,37,38,40,44,48,49,68,69,70,72,73,76,80,88,89,90,91],
            'G':[12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,32,36,37,38,41,45,48,49,68,69,70,72,73,77,80,88,89,90,91],
            'B':[12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,32,36,37,38,42,46,48,49,68,69,70,72,73,78,80,88,89,90,91],
        }
        for ch in 'RGB':
            q=tr['channels'][ch]['value_slice']
            tex={(int(x['texture_index']),x['channel'],x['sample_address']) for x in q.get('texture_sample_channels',[])}
            if tex!=family:v.append(f'{ch}: terminal texture leaf drift {sorted(tex)}')
            if q.get('cbuffer_dwords')!={'0':expected_cb[ch]}:
                v.append(f'{ch}: exact cbuffer leaf set drift {q.get("cbuffer_dwords")}')
            if q.get('unknown_registers')!=['v2','v3']:
                v.append(f'{ch}: native input frontier drift {q.get("unknown_registers")}')

        aq=tr['channels']['A']['value_slice']
        if aq.get('literals')!=['0'] or aq.get('texture_sample_channels') or aq.get('cbuffer_dwords') or aq.get('unknown_registers'):
            v.append(f'alpha is not exact zero-only {aq}')

        union=tr.get('mrt0_value_union') or {}
        alltex={(int(x['texture_index']),x['channel']) for x in union.get('texture_sample_channels',[])}
        if (0,'w') in alltex:v.append('t0 alpha reaches MRT0')
        if (2,'x') in alltex:v.append('t2.x reaches MRT0')
        if any(x[0]==3 for x in alltex):v.append('t3 reaches MRT0')
        api0=set((union.get('cbuffer_dwords') or {}).get('0',[]))
        for dead in DEAD_API0:
            if dead in api0:v.append(f'API0[{dead}] reaches MRT0')
        if '12' in (union.get('cbuffer_dwords') or {}):v.append('API12 reaches MRT0')

    anchors=[
        '/*0000000002bc: d2820807 041c0509*/ v_mad_f32       v7, v9, s2, v7 clamp',
        '/*0000000002cc: d2820801 04060105*/ v_mad_f32       v1, v5, v0, v1 clamp',
        '/*0000000002e8: 100a0f07         */ v_mul_f32       v5, v7, v7',
        '/*0000000002ec: d2820809 2424210e*/ v_mad_f32       v9, -v14, s16, v9 clamp',
        '/*0000000002fc: 10022701         */ v_mul_f32       v1, v1, v19',
        '/*00000000030c: d2060806 0001e106*/ v_add_f32       v6, v6, 0.5 clamp',
        '/*000000000324: 3e0e021c         */ v_mac_f32       v7, s28, v1',
        '/*000000000328: 3e14021d         */ v_mac_f32       v10, s29, v1',
        '/*00000000032c: 3e16021e         */ v_mac_f32       v11, s30, v1',
        '/*000000000330: 10020d06         */ v_mul_f32       v1, v6, v6',
        '/*000000000348: 3e0e0220         */ v_mac_f32       v7, s32, v1',
        '/*00000000034c: 3e140221         */ v_mac_f32       v10, s33, v1',
        '/*000000000350: 3e160222         */ v_mac_f32       v11, s34, v1',
        '/*000000000360: 10000a01         */ v_mul_f32       v0, s1, v5',
        '/*000000000368: 06040617         */ v_add_f32       v2, s23, v3',
        '/*00000000036c: 10060107         */ v_mul_f32       v3, v7, v0',
        '/*000000000370: 100a010a         */ v_mul_f32       v5, v10, v0',
        '/*000000000374: 1000010b         */ v_mul_f32       v0, v11, v0',
        '/*000000000384: 7c0c0480         */ v_cmp_ge_f32    vcc, 0, v2',
        '/*000000000388: d2000000 01a90100*/ v_cndmask_b32   v0, v0, 0, vcc',
        '/*000000000390: d2000002 01a90105*/ v_cndmask_b32   v2, v5, 0, vcc',
        '/*000000000398: d2000003 01a90103*/ v_cndmask_b32   v3, v3, 0, vcc',
        '/*0000000003d4: 5e020503         */ v_cvt_pkrtz_f16_f32 v1, v3, v2',
        '/*0000000003d8: 5e000d00         */ v_cvt_pkrtz_f16_f32 v0, v0, v6',
        '/*0000000003dc: f8001c0f 00000001*/ exp             mrt0, v1, v1, v0, v0 done compr vm',
    ]
    missing=[x for x in anchors if x not in asm]
    if missing:v.append(f'missing native anchors {missing}')

    out={
        'schema':'d1_tower_light_80c99ba6_gated_mrt0_factorization/v1',
        'status':'D1_TOWER_LIGHT_80C99BA6_GATED_MRT0_FACTORIZATION_EXACT' if not v else 'D1_TOWER_LIGHT_80C99BA6_GATED_MRT0_FACTORIZATION_PARTIAL',
        'shader':SHADER,'native_shader':NATIVE,'gcn_sha256':GCN_SHA,
        'instance_count':1,'unique_material_count':len(mats),
        'exact_tail_symbols':{
            'Q':'v7 after 0x2BC = clamp(q_in*API0[48]+API0[49])',
            'R':'v9 after 0x2EC = clamp(-r_in*API0[72]+API0[73])',
            'P':'v1 after 0x2CC = exact native clamped scalar',
            'T':'t2.y sampled at 0x234',
            'B':'v1 after 0x330 = (v6@0x30C)^2',
            'G':'v2 after 0x368 = exact API0[88:91] linear plane',
        },
        'exact_terminal_equation':{
            'vector_pre_scale':'V.rgb = API0[44:46].rgb + API0[76:78].rgb*(P*t2.y) + API0[40:42].rgb*B',
            'scalar_scale':'K = API0[80] * Q^2 * R',
            'gate':'G > 0',
            'mrt0_rgb':'V.rgb * K if G > 0 else (0,0,0)',
            'mrt0_a':'0',
            'vector_form':'MRT0.rgb = [API0[44:46] + API0[76:78]*(P*t2.y) + API0[40:42]*B] * API0[80] * Q^2 * R when G > 0, else 0',
        },
        'predicate_proof':{
            'compare':'v_cmp_ge_f32 vcc, 0, G',
            'zero_selected_when':'G <= 0',
            'kept_when':'G > 0',
        },
        'native_input_frontier':['v2','v3'],
        'renderer_texture_value_frontier':['t0.rgb','t1.x','t2.y'],
        'negative_proof':{
            't0_alpha_reaches_mrt0':False,
            't2_x_reaches_mrt0':False,
            't3_reaches_mrt0':False,
            **{f'api0_dword{d}_reaches_mrt0':False for d in DEAD_API0},
            'api12_reaches_mrt0':False,
        },
        'mrt1_boundary':'SHADER_WRITES_MRT1_BUT_THIS PROOF REDUCES MRT0 ONLY',
        'semantic_boundary':{
            'terminal_arithmetic_and_gate':'EXACT_NATIVE_GCN',
            'renderer_resource_human_semantics':'WITHHELD',
            'symbols_Q_R_P_B_G_human_semantics':'WITHHELD',
            'mrt1_semantics':'WITHHELD',
            'portable_light_model_mapping':'WITHHELD',
        },
        'violations':v,
        'policy':'Exact native GCN terminal arithmetic and predicate only. Renderer resources and upstream native intermediates remain unnamed without primary evidence.',
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'status':out['status'],'equation':out['exact_terminal_equation'],'negative_proof':out['negative_proof'],'violations':v},indent=2))
    return 0 if not v else 2

if __name__=='__main__':raise SystemExit(main())
