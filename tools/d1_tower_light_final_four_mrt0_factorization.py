#!/usr/bin/env python3
"""Close the final four singleton D1 Tower light pixel-shader MRT0 equations.

This proof is deliberately corpus-specific and fail-closed.  The four remaining
families are validated against exact retail shader identity, image-resource
provenance, ImmConstBuffer provenance, terminal MRT0 dependency slices, native
instruction anchors, material cardinality, and predicate structure.

No renderer-resource human meaning is assigned.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

def norm(x): return str(x).upper().removeprefix('0X').zfill(8)

TEXREQ={(0,'x','000000000048'),(0,'y','000000000048'),(0,'z','000000000048'),(1,'x','000000000040')}

CFG={
'80C99CB9':{
 'native':'80C99F16','native_sha':'4f169f2f1f2c3fe2bea50886b0d608c208b6696a4d7fcd0ad7c252d643ee2e5a',
 'gcn_sha':'495d7b3485d9f212fcb05b0aee736debf8fd1034dd79f806617c72b17d413cb2','gcn_bytes':1128,
 'terminal':'00000000045C','operands':['v1','v1','v0','v0'],'t2_addr':'000000000294','t3_addr':'0000000002A4',
 'images':[('000000000040','image_load_mip',[1],'x'),('000000000048','image_sample',[0],'xyzw'),('000000000294','image_sample_lz',[2],'xy'),('0000000002A4','image_sample_lz',[3],'x')],
 'loads':{
  '0000000002AC':(0,[76,77,78,79],[12,13,14,15]),'0000000002B0':(0,[56,57],[2,3]),
  '0000000002B4':(0,[104,105,106,107],[16,17,18,19]),'0000000002B8':(0,[108,109,110,111],[20,21,22,23]),
  '0000000002BC':(0,[88,89],[24,25]),'0000000002C0':(0,[52,53,54,55],[28,29,30,31]),
  '0000000002C8':(0,[92,93,94,95],[32,33,34,35]),'0000000002CC':(0,[48,49,50,51],[36,37,38,39]),
  '0000000002DC':(0,[96],[1]),'0000000002E0':(0,[101],[4]),
 },
 'channel':{'R':{52,92,48},'G':{53,93,49},'B':{54,94,50}},
 'common':{56,57,88,89,96,104,105,106,107,108,109,110,111},
 'anchors':[
  'v_mad_f32       v11, v0, s2, v11 clamp','v_mad_f32       v6, -v9, s24, v6 clamp',
  'v_add_f32       v8, v8, 0.5 clamp','v_mul_f32       v2, v8, v8',
  'v_mac_f32       v4, s32, v2','v_mac_f32       v4, s36, v2',
  'v_cmp_le_f32    s[0:1], v3, 0','v_cmp_ge_f32    vcc, 0, v7','s_or_b64        vcc, s[0:1], vcc',
  'exp             mrt0, v1, v1, v0, v0 done compr vm',
 ],
 'equation':{
  'vector_pre_scale':'V.rgb = API0[52:54].rgb + API0[92:94].rgb*(L*t2.y) + API0[48:50].rgb*P',
  'scalar_scale':'K = API0[96] * Q^2 * H','gate':'G0 > 0 AND G1 > 0',
  'mrt0_rgb':'V.rgb * K iff both gates are positive, else 0','mrt0_a':'0',
  'vector_form':'MRT0.rgb = (API0[52:54].rgb + API0[92:94].rgb*(L*t2.y) + API0[48:50].rgb*P) * API0[96] * Q^2 * H iff G0 > 0 and G1 > 0, else 0',
 },
 'symbols':{
  'Q':'clamp(q_in*API0[56]+API0[57])','H':'exact clamped native scalar including API0[88:89]',
  'L':'exact native clamped scalar reaching t2.y modulation','P':'clamp(p_native+0.5)^2',
  'G0':'API0[104:107] exact native linear plane','G1':'API0[108:111] exact native linear plane',
 },
 'predicate':'DUAL_OR_REJECTION'
},
'80C99CBA':{
 'native':'80C99F17','native_sha':'f5ff494b4e8fc7fd53d1c7d21720ef78257ecefd62f2e1311a2b1ad440a43e6c',
 'gcn_sha':'55e23e3de7667363e8a30e0ef5a6299420547f58e47480c0c0d6f16cf4e78ca3','gcn_bytes':1016,
 'terminal':'0000000003EC','operands':['v1','v1','v0','v0'],'t2_addr':'000000000244','t3_addr':'000000000238',
 'images':[('000000000040','image_load_mip',[1],'x'),('000000000048','image_sample',[0],'xyzw'),('000000000238','image_sample_lz',[3],'x'),('000000000244','image_sample_lz',[2],'xy')],
 'loads':{
  '00000000024C':(0,[64,65,66,67],[12,13,14,15]),'000000000250':(0,[44,45],[2,3]),
  '000000000254':(0,[84,85,86,87],[16,17,18,19]),'000000000258':(0,[88,89,90,91],[20,21,22,23]),
  '00000000025C':(0,[68,69],[24,25]),'000000000268':(0,[40,41,42,43],[28,29,30,31]),
  '000000000278':(0,[72,73,74,75],[32,33,34,35]),'00000000027C':(0,[76],[1]),'000000000280':(0,[81],[4]),
 },
 'channel':{'R':{40,72},'G':{41,73},'B':{42,74}},
 'common':{44,45,68,69,76,84,85,86,87,88,89,90,91},
 'anchors':[
  'v_mad_f32       v11, v9, s2, v11 clamp','v_mad_f32       v8, -v14, s24, v8 clamp',
  'v_add_f32       v4, v7, 0.5 clamp','v_mul_f32       v4, v4, v4',
  'v_mac_f32       v2, s32, v1','v_cmp_le_f32    s[0:1], v3, 0','v_cmp_ge_f32    vcc, 0, v6',
  's_or_b64        vcc, s[0:1], vcc','exp             mrt0, v1, v1, v0, v0 done compr vm',
 ],
 'equation':{
  'vector_pre_scale':'V.rgb = API0[40:42].rgb*P + API0[72:74].rgb*(L*t2.y)',
  'scalar_scale':'K = API0[76] * Q^2 * H','gate':'G0 > 0 AND G1 > 0',
  'mrt0_rgb':'V.rgb * K iff both gates are positive, else 0','mrt0_a':'0',
  'vector_form':'MRT0.rgb = (API0[40:42].rgb*P + API0[72:74].rgb*(L*t2.y)) * API0[76] * Q^2 * H iff G0 > 0 and G1 > 0, else 0',
 },
 'symbols':{
  'Q':'clamp(q_in*API0[44]+API0[45])','H':'clamp(-h_in*API0[68]+API0[69])',
  'L':'exact native clamped scalar reaching t2.y modulation','P':'clamp(p_native+0.5)^2',
  'G0':'API0[84:87] exact native linear plane','G1':'API0[88:91] exact native linear plane',
 },
 'predicate':'DUAL_OR_REJECTION'
},
'80C99CBB':{
 'native':'80C99F18','native_sha':'ac511b183e7e5c3befde3527f417140e4af5b46e028db4b74823b209c2c59dd5',
 'gcn_sha':'9d0261d0fd9b5427e82d83bc0cc2df61750d1425a5f9dcce1a8280d62a13a06d','gcn_bytes':720,
 'terminal':'0000000002C4','operands':['v2','v2','v0','v0'],'t2_addr':'0000000001D4','t3_addr':None,
 'images':[('000000000040','image_load_mip',[1],'x'),('000000000048','image_sample',[0],'xyzw'),('0000000001D4','image_sample_lz',[2],'y')],
 'loads':{
  '0000000001DC':(0,[36,37,38,39],[0,1,2,3]),'0000000001E0':(0,[64,65,66,67],[8,9,10,11]),
  '0000000001E8':(0,[32],[3]),'0000000001EC':(0,[44,45],[12,13]),'0000000001F0':(0,[68,69],[14,15]),
  '0000000001F8':(0,[40,41,42,43],[16,17,18,19]),'000000000204':(0,[72,73,74,75],[20,21,22,23]),
  '000000000208':(0,[76],[1]),
 },
 'channel':{'R':{40,72},'G':{41,73},'B':{42,74}},
 'common':{32,36,37,38,44,45,68,69,76},
 'anchors':[
  'v_mad_f32       v11, v9, s12, v11 clamp','v_add_f32       v4, v10, 0.5 clamp',
  'v_mad_f32       v3, -v8, s14, v3 clamp','v_mul_f32       v6, v11, v11',
  'v_mul_f32       v0, v4, v4','v_mac_f32       v2, s20, v1',
  'exp             mrt0, v2, v2, v0, v0 done compr vm',
 ],
 'equation':{
  'vector_pre_scale':'V.rgb = API0[40:42].rgb*U^2 + API0[72:74].rgb*(L*t2.y)',
  'scalar_scale':'K = API0[76] * Q^2 * H','mrt0_rgb':'MRT0.rgb = V.rgb * K','mrt0_a':'0',
  'vector_form':'MRT0.rgb = (API0[40:42].rgb*U^2 + API0[72:74].rgb*(L*t2.y)) * API0[76] * Q^2 * H',
 },
 'symbols':{
  'Q':'clamp(q_in*API0[44]+API0[45])','H':'clamp(-h_in*API0[68]+API0[69])',
  'L':'exact native clamped scalar reaching t2.y modulation','U':'exact native scalar clamped after +0.5; upstream arithmetic includes API0[32,36:38]',
 },
 'predicate':'NONE'
},
'80C99CBD':{
 'native':'80C99F1A','native_sha':'b426c9b95669330f7430250c7376b8d57911b463f83448801246d1c37a9dd481',
 'gcn_sha':'89a33de5c33318c22cb6efb9cf574949d58e48ae67fc82fa6dda76fb877a08f7','gcn_bytes':1044,
 'terminal':'000000000408','operands':['v1','v1','v0','v0'],'t2_addr':'0000000002A4','t3_addr':'000000000298',
 'images':[('000000000040','image_load_mip',[1],'x'),('000000000048','image_sample',[0],'xyzw'),('000000000298','image_sample_lz',[3],'x'),('0000000002A4','image_sample_lz',[2],'xy')],
 'loads':{
  '0000000002AC':(0,[52,53],[2,3]),'0000000002B0':(0,[100,101,102,103],[12,13,14,15]),
  '0000000002BC':(0,[48,49,50,51],[16,17,18,19]),'0000000002CC':(0,[88,89,90,91],[20,21,22,23]),
  '0000000002D0':(0,[92],[1]),'0000000002D4':(0,[97],[4]),
 },
 'channel':{'R':{48,88},'G':{49,89},'B':{50,90}},
 'common':{52,53,92,100,101,102,103},
 'anchors':[
  'v_mad_f32       v8, v1, s2, v8 clamp','v_add_f32       v5, v10, 0.5 clamp',
  'v_mul_f32       v5, v5, v5','v_mac_f32       v2, s20, v0',
  'v_cmp_ge_f32    vcc, 0, v3','exp             mrt0, v1, v1, v0, v0 done compr vm',
 ],
 'equation':{
  'vector_pre_scale':'V.rgb = API0[48:50].rgb*P + API0[88:90].rgb*(L*t2.y)',
  'scalar_scale':'K = API0[92] * Q^2','gate':'G > 0',
  'mrt0_rgb':'V.rgb * K if G > 0 else (0,0,0)','mrt0_a':'0',
  'vector_form':'MRT0.rgb = (API0[48:50].rgb*P + API0[88:90].rgb*(L*t2.y)) * API0[92] * Q^2 when G > 0, else 0',
 },
 'symbols':{
  'Q':'clamp(q_in*API0[52]+API0[53])','P':'clamp(p_native+0.5)^2',
  'L':'exact native clamped scalar reaching t2.y modulation','G':'API0[100:103] exact native linear plane',
 },
 'predicate':'SINGLE_REJECTION'
},
}

def main()->int:
 ap=argparse.ArgumentParser()
 for n in ('material-manifest','shader-report','image-usage','cbuffer-usage','terminal-mrt0','disasm-dir','out'):
  ap.add_argument('--'+n,type=Path,required=True)
 a=ap.parse_args()
 m=json.loads(a.material_manifest.read_text());s=json.loads(a.shader_report.read_text())
 iu=json.loads(a.image_usage.read_text());cb=json.loads(a.cbuffer_usage.read_text());tm=json.loads(a.terminal_mrt0.read_text())
 violations=[];rows=[]
 if m.get('status')!='D1_WORLD_LIGHT_MATERIAL_MANIFEST_COMPLETE':violations.append('material manifest not exact')
 if s.get('status')!='D1_WORLD_PIXEL_SHADER_GCN_EXACT' or s.get('error_count'):violations.append('shader report not exact')
 if iu.get('status')!='D1_GCN_IMAGE_RESOURCE_USAGE_EXACT':violations.append('image usage not exact')
 if cb.get('status')!='D1_GCN_CBUFFER_USAGE_EXACT' or cb.get('missing_usage'):violations.append('cbuffer usage not exact')
 if tm.get('status')!='D1_GCN_TERMINAL_MRT0_DEPENDENCY_CENSUS_EXACT':violations.append('terminal MRT0 census not exact')
 srby={norm(x.get('shader')):x for x in s.get('shaders',[])}
 iuby={norm(x.get('shader')):x for x in iu.get('shaders',[])}
 cbby={norm(x.get('shader')):x for x in cb.get('shaders',[])}
 tmby={norm(x.get('shader')):x for x in tm.get('shaders',[])}
 for sh,cfg in CFG.items():
  v=[]
  mats=(m.get('pixel_shader_materials') or {}).get(sh,[])
  if int((m.get('pixel_shader_frequency') or {}).get(sh,-1))!=1:v.append('instance count drift')
  if len(mats)!=1:v.append(f'unique material count drift {len(mats)} != 1')
  if any(int((m.get('materials') or {}).get(x,{}).get('ps_texture_count',-1))!=0 for x in mats):v.append('serialized PS texture binding unexpectedly present')
  sr=srby.get(sh)
  if not sr:v.append('shader report row missing')
  else:
   exp={'native_shader':cfg['native'],'native_sha256':cfg['native_sha'],'gcn_sha256':cfg['gcn_sha'],'gcn_bytes':cfg['gcn_bytes']}
   for k,z in exp.items():
    if sr.get(k)!=z:v.append(f'{k} drift {sr.get(k)!r} != {z!r}')
  ir=iuby.get(sh)
  if not ir:v.append('image usage row missing')
  else:
   got=[(x['address'],x['opcode'],[q['texture_index'] for q in x.get('resources',[])],x['dmask_channels']) for x in ir.get('instructions',[])]
   if got!=cfg['images']:v.append(f'image scope drift {got!r}')
  cr=cbby.get(sh)
  if not cr:v.append('cbuffer row missing')
  else:
   by={x.get('address'):x for x in cr.get('loads',[])}
   for addr,(api,dws,dst) in cfg['loads'].items():
    q=by.get(addr)
    if not q or q.get('api_slot')!=api or q.get('dword_indices')!=dws or q.get('destination')!=dst:
     v.append(f'{addr}: cbuffer provenance drift {q}')
  tr=tmby.get(sh)
  if not tr:v.append('terminal MRT0 row missing')
  else:
   if tr.get('terminal_mrt0_export_address')!=cfg['terminal'] or not tr.get('terminal_mrt0_compressed'):v.append('terminal export identity drift')
   if tr.get('terminal_mrt0_operands')!=cfg['operands']:v.append(f"terminal operands drift {tr.get('terminal_mrt0_operands')}")
   texreq=set(TEXREQ)|{(2,'y',cfg['t2_addr'])}
   for ch in 'RGB':
    q=tr['channels'][ch]['value_slice']
    tex={(int(x['texture_index']),x['channel'],x['sample_address']) for x in q.get('texture_sample_channels',[])}
    if tex!=texreq:v.append(f'{ch}: terminal texture leaf drift {sorted(tex)} != {sorted(texreq)}')
    cbs={str(k):set(z) for k,z in (q.get('cbuffer_dwords') or {}).items()}
    if set(cbs)-{'0'}:v.append(f'{ch}: non-API0 cbuffer reaches MRT0 {cbs}')
    req=set(cfg['common'])|set(cfg['channel'][ch])
    if not req.issubset(cbs.get('0',set())):v.append(f'{ch}: required coefficient leaves missing {sorted(req-cbs.get("0",set()))}')
   aq=tr['channels']['A']['value_slice']
   if aq.get('literals')!=['0'] or aq.get('texture_sample_channels') or aq.get('cbuffer_dwords') or aq.get('unknown_registers'):
    v.append(f'alpha is not exact zero-only {aq}')
   union=tr.get('mrt0_value_union') or {}
   alltex={(int(x['texture_index']),x['channel']) for x in union.get('texture_sample_channels',[])}
   if (0,'w') in alltex or (2,'x') in alltex:v.append(f'dead sampled channel reached MRT0 {sorted(alltex)}')
   if cfg['t3_addr'] and any(ti==3 for ti,_ in alltex):v.append('t3 reaches MRT0 unexpectedly')
   if '12' in (union.get('cbuffer_dwords') or {}):v.append('API12 reaches MRT0 unexpectedly')
  p=a.disasm_dir/f'PS_{sh}.s'
  if not p.exists():v.append(f'disassembly missing {p}')
  else:
   asm=p.read_text(errors='replace')
   miss=[x for x in cfg['anchors'] if x not in asm]
   if miss:v.append(f'missing native anchors {miss}')
  rows.append({
   'shader':sh,'native_shader':cfg['native'],'gcn_sha256':cfg['gcn_sha'],
   'instance_count':1,'unique_material_count':len(mats),
   'exact_tail_symbols':cfg['symbols'],'exact_terminal_equation':cfg['equation'],
   'predicate_class':cfg['predicate'],
   'negative_proof':{'t0_alpha_reaches_mrt0':False,'t2_x_reaches_mrt0':False,'t3_reaches_mrt0':False if cfg['t3_addr'] else None,'api12_reaches_mrt0':False},
   'violations':v,
  })
  violations.extend(f'{sh}: {x}' for x in v)
 out={
  'schema':'d1_tower_light_final_four_mrt0_factorization/v1',
  'status':'D1_TOWER_LIGHT_FINAL_FOUR_MRT0_FACTORIZATION_EXACT' if len(rows)==4 and not violations else 'D1_TOWER_LIGHT_FINAL_FOUR_MRT0_FACTORIZATION_PARTIAL',
  'shader_family_count':len(rows),'instance_count':sum(x['instance_count'] for x in rows),
  'rows':rows,'violations':violations,
  'semantic_boundary':{
   'terminal_arithmetic':'EXACT_NATIVE_GCN',
   'gate_predicates':'EXACT_NATIVE_GCN',
   'serialized_ps_texture_bindings':'NONE_FOR_ALL_FOUR_SINGLETON_MATERIALS',
   'renderer_resource_human_semantics':'WITHHELD',
   'portable_light_model_mapping':'WITHHELD',
  },
  'policy':'Exact retail native arithmetic only.  Structural equivalence to previously closed light families is used only after exact binary identity, provenance, terminal leaves and instruction anchors are independently validated.',
 }
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'status':out['status'],'rows':[{'shader':x['shader'],'equation':x['exact_terminal_equation'],'predicate':x['predicate_class'],'violations':x['violations']} for x in rows],'violations':violations},indent=2))
 return 0 if out['status']=='D1_TOWER_LIGHT_FINAL_FOUR_MRT0_FACTORIZATION_EXACT' else 2
if __name__=='__main__': raise SystemExit(main())
