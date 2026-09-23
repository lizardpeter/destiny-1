#!/usr/bin/env python3
"""Fail-closed gated terminal MRT0 factorization for Tower light PS 80CA0296.

Exact native arithmetic only:
    Q = clamp(q_in * API0[32] + API0[33])
    H = clamp(-h_in * API0[72] + API0[73])
    L = clamp(l_a*l_b + l_c)
    G = API0[88]*g0 + API0[89]*g1 + API0[90]*g2 + API0[91]
    BASE.rgb = API0[76:78] * Q^2 * H * API0[80] * L * t2.y * t3.rgb
    MRT0.rgb = BASE.rgb if G > 0 else 0
    MRT0.a = 0

t3 is not a renderer-only input for this family: all 12 exact Tower light
materials serialize t3, with 10 binding 80CA0256 and 2 binding 80C99AE8.
The human role of those textures remains withheld.
"""
from __future__ import annotations
import argparse,collections,json
from pathlib import Path

SHADER='80CA0296';NATIVE='80CA02EA'
NATIVE_SHA='2c6440d51972889455f44316d20833a5bb6bbd892d4a06bf0d7dfb5ec27fa355'
GCN_SHA='b51ab4bdae471612e54b49f198d8ac0eebafdfd97bcf6edb349516e68c90d815'
GCN_BYTES=944;EXPECTED_INSTANCES=12;EXPECTED_MATERIALS=12;EXPECTED_TERMINAL='0000000003A4'
EXPECTED_T3_TEXTURE_HIST={'80CA0256':10,'80C99AE8':2}

ANCHORS=[
 '/*000000000234: f09c0300 01061213*/ image_sample_lz v[18:19], v[19:22], s[24:31], s[32:35] dmask:3',
 '/*000000000248: f0800700 00021410*/ image_sample    v[20:22], v[16:19], s[8:15], s[0:3] dmask:7',
 '/*000000000250: c2800544         */ s_buffer_load_dwordx4 s[0:3], s[4:7], 0x44',
 '/*000000000254: c2440520         */ s_buffer_load_dwordx2 s[8:9], s[4:7], 0x20',
 '/*000000000258: c2450548         */ s_buffer_load_dwordx2 s[10:11], s[4:7], 0x48',
 '/*00000000025c: c2860558         */ s_buffer_load_dwordx4 s[12:15], s[4:7], 0x58',
 '/*000000000268: c288054c         */ s_buffer_load_dwordx4 s[16:19], s[4:7], 0x4c',
 '/*00000000027c: c2010550         */ s_buffer_load_dword s2, s[4:7], 0x50',
 '/*000000000294: d282080b 042c1109*/ v_mad_f32       v11, v9, s8, v11 clamp',
 '/*0000000002b0: c2000555         */ s_buffer_load_dword s0, s[4:7], 0x55',
 '/*0000000002b4: 100c170b         */ v_mul_f32       v6, v11, v11',
 '/*0000000002b8: d2820807 241c150d*/ v_mad_f32       v7, -v13, s10, v7 clamp',
 '/*0000000002c0: d2820801 04060105*/ v_mad_f32       v1, v5, v0, v1 clamp',
 '/*0000000002d0: 10080f06         */ v_mul_f32       v4, v6, v7',
 '/*0000000002d4: 1006060d         */ v_mul_f32       v3, s13, v3',
 '/*0000000002e0: 100a0810         */ v_mul_f32       v5, s16, v4',
 '/*0000000002e4: 100c0811         */ v_mul_f32       v6, s17, v4',
 '/*0000000002e8: 10080812         */ v_mul_f32       v4, s18, v4',
 '/*0000000002ec: 3e06180c         */ v_mac_f32       v3, s12, v12',
 '/*0000000002f0: 10022701         */ v_mul_f32       v1, v1, v19',
 '/*000000000304: 100a0a02         */ v_mul_f32       v5, s2, v5',
 '/*000000000308: 100c0c02         */ v_mul_f32       v6, s2, v6',
 '/*00000000030c: 10080802         */ v_mul_f32       v4, s2, v4',
 '/*000000000310: 3e06040e         */ v_mac_f32       v3, s14, v2',
 '/*000000000330: 0606060f         */ v_add_f32       v3, s15, v3',
 '/*000000000334: 10040514         */ v_mul_f32       v2, v20, v2',
 '/*000000000338: 100a0b15         */ v_mul_f32       v5, v21, v5',
 '/*00000000033c: 10020316         */ v_mul_f32       v1, v22, v1',
 '/*00000000034c: 7c0c0680         */ v_cmp_ge_f32    vcc, 0, v3',
 '/*000000000350: d2000001 01a90101*/ v_cndmask_b32   v1, v1, 0, vcc',
 '/*000000000358: d2000003 01a90105*/ v_cndmask_b32   v3, v5, 0, vcc',
 '/*000000000360: d2000002 01a90102*/ v_cndmask_b32   v2, v2, 0, vcc',
 '/*00000000039c: 5e000702         */ v_cvt_pkrtz_f16_f32 v0, v2, v3',
 '/*0000000003a0: 5e020d01         */ v_cvt_pkrtz_f16_f32 v1, v1, v6',
 '/*0000000003a4: f8001c0f 00000100*/ exp             mrt0, v0, v0, v1, v1 done compr vm',
]

def norm(x):return str(x).upper().removeprefix('0X').zfill(8)

def main()->int:
 ap=argparse.ArgumentParser()
 for n in ('material-manifest','shader-report','image-usage','cbuffer-usage','terminal-mrt0','disasm','out'):
  ap.add_argument('--'+n,type=Path,required=True)
 a=ap.parse_args();v=[]
 m=json.loads(a.material_manifest.read_text());s=json.loads(a.shader_report.read_text())
 i=json.loads(a.image_usage.read_text());c=json.loads(a.cbuffer_usage.read_text())
 t=json.loads(a.terminal_mrt0.read_text());asm=a.disasm.read_text(errors='replace')

 if m.get('status')!='D1_WORLD_LIGHT_MATERIAL_MANIFEST_COMPLETE':v.append('material manifest not exact')
 if int((m.get('pixel_shader_frequency') or {}).get(SHADER,-1))!=EXPECTED_INSTANCES:v.append('instance count drift')
 mats=(m.get('pixel_shader_materials') or {}).get(SHADER,[])
 if len(mats)!=EXPECTED_MATERIALS:v.append(f'unique material count drift {len(mats)} != {EXPECTED_MATERIALS}')

 tex_hist=collections.Counter()
 for mh in mats:
  mr=(m.get('materials') or {}).get(mh,{})
  binds=[x for x in mr.get('bindings',[]) if x.get('stage')=='ps']
  if int(mr.get('ps_texture_count',-1))!=1 or len(binds)!=1:
   v.append(f'{mh}: expected exactly one serialized PS texture binding, got {binds}')
   continue
  b=binds[0]
  if int(b.get('texture_index',-1))!=3:v.append(f'{mh}: serialized texture index {b.get("texture_index")} != 3')
  tex_hist[norm(b.get('texture'))]+=1
 if dict(sorted(tex_hist.items()))!=EXPECTED_T3_TEXTURE_HIST:
  v.append(f't3 texture histogram drift {dict(sorted(tex_hist.items()))} != {EXPECTED_T3_TEXTURE_HIST}')

 sr=next((x for x in s.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
 if s.get('status')!='D1_WORLD_PIXEL_SHADER_GCN_EXACT' or not sr:v.append('shader report not exact/present')
 else:
  for k,z in {'native_shader':NATIVE,'native_sha256':NATIVE_SHA,'gcn_sha256':GCN_SHA,'gcn_bytes':GCN_BYTES}.items():
   if sr.get(k)!=z:v.append(f'{k} drift {sr.get(k)!r} != {z!r}')

 ir=next((x for x in i.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
 if i.get('status')!='D1_GCN_IMAGE_RESOURCE_USAGE_EXACT' or not ir:v.append('image usage not exact/present')
 else:
  got=[(x['address'],x['opcode'],[q['texture_index'] for q in x.get('resources',[])],x['dmask_channels']) for x in ir.get('instructions',[])]
  exp=[
   ('000000000040','image_load_mip',[1],'x'),
   ('000000000048','image_sample',[0],'xyzw'),
   ('000000000234','image_sample_lz',[2],'xy'),
   ('000000000248','image_sample',[3],'xyz'),
  ]
  if got!=exp:v.append(f'image instruction scope drift {got!r}')

 cr=next((x for x in c.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
 if c.get('status')!='D1_GCN_CBUFFER_USAGE_EXACT' or not cr:v.append('cbuffer usage not exact/present')
 else:
  by={x.get('address'):x for x in cr.get('loads',[])}
  expected={
   '000000000250':(0,[68,69,70,71],[0,1,2,3]),
   '000000000254':(0,[32,33],[8,9]),
   '000000000258':(0,[72,73],[10,11]),
   '00000000025C':(0,[88,89,90,91],[12,13,14,15]),
   '000000000268':(0,[76,77,78,79],[16,17,18,19]),
   '00000000027C':(0,[80],[2]),
   '0000000002B0':(0,[85],[0]),
  }
  for addr,(api,dw,dst) in expected.items():
   q=by.get(addr)
   if not q or q.get('api_slot')!=api or q.get('dword_indices')!=dw or q.get('destination')!=dst:
    v.append(f'{addr}: cbuffer provenance drift {q}')

 tr=next((x for x in t.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
 if t.get('status')!='D1_GCN_TERMINAL_MRT0_DEPENDENCY_CENSUS_EXACT' or not tr:v.append('terminal MRT0 slice not exact/present')
 else:
  if tr.get('terminal_mrt0_export_address')!=EXPECTED_TERMINAL or not tr.get('terminal_mrt0_compressed'):
   v.append('terminal export identity drift')
  if tr.get('terminal_mrt0_operands')!=['v0','v0','v1','v1']:v.append('terminal operands drift')
  expected_tex={(0,x,'000000000048') for x in 'xyz'}|{
   (1,'x','000000000040'),(2,'y','000000000234'),
   (3,'x','000000000248'),(3,'y','000000000248'),(3,'z','000000000248'),
  }
  for ch,colordw,t3ch in [('R',76,'x'),('G',77,'y'),('B',78,'z')]:
   q=tr['channels'][ch]['value_slice']
   tex={(int(x['texture_index']),x['channel'],x['sample_address']) for x in q.get('texture_sample_channels',[])}
   # Each color lane must include its own t3 channel and the shared renderer leaves.
   required_tex={(0,x,'000000000048') for x in 'xyz'}|{(1,'x','000000000040'),(2,'y','000000000234'),(3,t3ch,'000000000248')}
   if tex!=required_tex:v.append(f'{ch}: terminal texture leaf drift {sorted(tex)}')
   cb={str(k):set(z) for k,z in q.get('cbuffer_dwords',{}).items()}
   if set(cb)-{'0'}:v.append(f'{ch}: unexpected non-API0 MRT0 cbuffer leaves {cb}')
   required={32,33,72,73,colordw,80,88,89,90,91}
   if not required.issubset(cb.get('0',set())):
    v.append(f'{ch}: terminal coefficient leaves missing {sorted(required-cb.get("0",set()))}')
   if 79 in cb.get('0',set()) or 85 in cb.get('0',set()):
    v.append(f'{ch}: MRT1-only coefficient leaked into MRT0 {cb}')
  aq=tr['channels']['A']['value_slice']
  if aq.get('literals')!=['0'] or aq.get('texture_sample_channels') or aq.get('cbuffer_dwords') or aq.get('unknown_registers'):
   v.append(f'alpha is not exact zero-only {aq}')
  union=tr.get('mrt0_value_union') or {}
  alltex={(int(x['texture_index']),x['channel']) for x in union.get('texture_sample_channels',[])}
  if (0,'w') in alltex or (2,'x') in alltex:v.append(f'dead sampled channel reached MRT0 unexpectedly {sorted(alltex)}')
  if '12' in (union.get('cbuffer_dwords') or {}):v.append('API12 unexpectedly reaches MRT0')
  api0=set((union.get('cbuffer_dwords') or {}).get('0',[]))
  if 79 in api0 or 85 in api0:v.append(f'MRT1-only coefficient reached MRT0 {sorted(api0)}')

 missing=[x for x in ANCHORS if x not in asm]
 if missing:v.append(f'missing exact native anchors {missing}')

 out={
  'schema':'d1_tower_light_80ca0296_gated_mrt0_factorization/v1',
  'status':'D1_TOWER_LIGHT_80CA0296_GATED_MRT0_FACTORIZATION_EXACT' if not v else 'D1_TOWER_LIGHT_80CA0296_GATED_MRT0_FACTORIZATION_PARTIAL',
  'shader':SHADER,'native_shader':NATIVE,'gcn_sha256':GCN_SHA,
  'instance_count':EXPECTED_INSTANCES,'unique_material_count':len(mats),
  'serialized_t3_texture_histogram':dict(sorted(tex_hist.items())),
  'exact_tail_symbols':{
   'Q':'v11 after 0x294 = clamp(q_in*API0[32]+API0[33])',
   'H':'v7 after 0x2B8 = clamp(-h_in*API0[72]+API0[73])',
   'L':'v1 after 0x2C0 = clamp(l_a*l_b+l_c)',
   'C':'API0[76:78].rgb','S':'API0[80]','T':'t2.y',
   'M':'t3.rgb',
   'G':'API0[88]*g0 + API0[89]*g1 + API0[90]*g2 + API0[91]',
  },
  'exact_terminal_equation':{
   'base_rgb':'API0[76:78].rgb * Q^2 * H * API0[80] * L * t2.y * t3.rgb',
   'gate':'G > 0',
   'mrt0_rgb':'BASE.rgb if G > 0 else (0,0,0)',
   'mrt0_a':'0',
   'vector_form':'MRT0.rgb = API0[76:78].rgb * Q^2 * H * API0[80] * L * t2.y * t3.rgb when G > 0, else 0',
  },
  'predicate_proof':{'compare':'v_cmp_ge_f32 vcc, 0, G','false_when':'G <= 0','kept_when':'G > 0'},
  'negative_proof':{
   't0_alpha_reaches_mrt0':False,'t2_x_reaches_mrt0':False,
   'api0_dword79_reaches_mrt0':False,'api0_dword85_reaches_mrt0':False,
   'api12_reaches_mrt0':False,
  },
  'semantic_boundary':{
   'terminal_arithmetic':'EXACT_NATIVE_GCN',
   'serialized_t3_binding':'EXACT_FOR_ALL_12_FAMILY_MATERIALS',
   'serialized_t3_texture_role':'WITHHELD',
   'renderer_t0_t1_t2_human_semantics':'WITHHELD',
   'symbols_Q_H_L_G_human_semantics':'WITHHELD',
   'portable_light_model_mapping':'WITHHELD',
  },
  'violations':v,
  'policy':'Exact native GCN arithmetic and material binding identity only. t3 is proven serialized but its human role is not inferred; renderer inputs and native symbolic intermediates remain unnamed.',
 }
 a.out.parent.mkdir(parents=True,exist_ok=True)
 a.out.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'status':out['status'],'equation':out['exact_terminal_equation'],'t3_histogram':out['serialized_t3_texture_histogram'],'violations':v},indent=2))
 return 0 if not v else 2

if __name__=='__main__':raise SystemExit(main())
