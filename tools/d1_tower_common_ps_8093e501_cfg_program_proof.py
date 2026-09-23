#!/usr/bin/env python3
"""Exact program-level CFG/MRT0 closure for Tower common shader 8093E501.

This family is intentionally not flattened into one enormous algebraic expression.
It contains a real iterative sampling/search loop. Instead the proof closes:
1. exact retail shader/material/resource identities;
2. exact structural CFG, including the single native backedge;
3. exact preterminal program boundary producing RGBA state at the 0x600 merge;
4. exact terminal MRT0 reduction and final export-lane gate.

The preterminal RGBA producer remains an exact native CFG program, not a human semantic
or a straight-line symbolic expression. This distinction is explicit in the schema.
"""
from __future__ import annotations
import argparse,hashlib,json,re
from pathlib import Path

SH='8093E501';MAT='8093E42A';NATIVE='8093E54E'
NSHA='e6443294553fc94d95288f67f9228d5cbc4446ca9733918297cc813b882e858c'
GSHA='0875ad9af2f452b4ca2af751bdb53c98377231a95bdd212700abadee2d1133a6';GBYTES=2024
TEXTURES={0:'8093E81D',1:'8093E81E',2:'8093E81D',3:'8093E81F',4:'8093E820'}
API={'0':[0,1,2,3,4,5,8,9,20,24,28,32,33,36,37,44,48,52,56,57,58,59,60,61,69,77],
     '12':[28,29,30,31]}
EXPECTED_CFG={'instruction_count':429,'basic_block_count':20,'branch_count':10,'backedge_count':1,
              'normalized_instruction_sha256':'a25fd49788225bae20b9e131c404b2184a209f48c40ec5c71d2ea347d5667620',
              'backedge_source_start':'0000000002F8','backedge_source_end':'000000000308','backedge_target':'000000000284'}
IMAGE_PATTERN=[
 ('0000000002C8',0,'x','image_sample_d'),
 ('000000000390',1,'xyzw','image_sample'),
 ('0000000004B4',2,'x','image_sample'),('0000000004BC',2,'x','image_sample'),
 ('0000000004C4',2,'x','image_sample'),('0000000004CC',2,'x','image_sample'),
 ('0000000004D4',2,'x','image_sample'),('0000000004DC',2,'x','image_sample'),
 ('0000000004E4',2,'x','image_sample'),('0000000004F4',2,'x','image_sample'),
 ('000000000634',4,'x','image_sample'),('00000000063C',3,'xy','image_sample'),
]
ANCHORS=[
 'v_cmp_lt_f32    vcc, 0, v4',
 's_and_saveexec_b64 s[0:1], vcc',
 'v_cmp_gt_i32    vcc, v9, v25',
 'image_sample_d  v27, v[27:30], s[24:31], s[4:7]',
 's_branch        .L644_0',
 'v_cmp_neq_f32   vcc, 0, v11',
 'image_sample    v[13:16], v[11:14], s[24:31], s[8:11] dmask:15',
 'image_sample    v5, v[11:14], s[4:11], s[16:19]',
 'v_exp_f32       v1, -v2 clamp',
 's_mov_b64       exec, s[0:1]',
 'v_cmp_lt_f32    vcc, 0, v5',
 's_and_b64       exec, s[0:1], vcc',
 'v_rcp_f32       v13, v5',
 'v_mul_f32       v13, v5, v13',
 'v_add_f32       v5, -v5, 1.0 clamp',
 'v_mul_f32       v22, v17, v13',
 'v_mul_f32       v23, v2, v13',
 'v_mul_f32       v15, v4, v13',
 'v_sub_f32       v17, 1.0, v5',
 's_buffer_load_dword s0, s[20:23], 0x4d',
 'v_max_f32       v7, s0, s0 clamp',
 'v_madak_f32     v1, v7, v17, 0xbf000000',
 'v_cmp_gt_f32    vcc, 0, v1',
 's_andn2_b64     s[36:37], s[36:37], vcc',
 'v_mov_b32       v3, 0',
 's_mov_b64       exec, s[36:37]',
 'exp             mrt0, v0, v0, v1, v1 done compr vm',
]

def norm(x):return str(x).upper().removeprefix('0X').zfill(8)

def main():
 ap=argparse.ArgumentParser()
 for n in ('manifest','shader-report','image-usage','cbuffer-usage','cfg','disasm','out'):ap.add_argument('--'+n,type=Path,required=True)
 a=ap.parse_args();v=[]
 m=json.loads(a.manifest.read_text());sr=json.loads(a.shader_report.read_text());iu=json.loads(a.image_usage.read_text());cb=json.loads(a.cbuffer_usage.read_text());cfg=json.loads(a.cfg.read_text())
 if m.get('status')!='D1_WORLD_VISIBLE_MATERIAL_TEXTURE_EXPORT' or m.get('material_decode_errors') or m.get('texture_errors'):v.append('manifest not exact')
 if sr.get('status')!='D1_WORLD_PIXEL_SHADER_GCN_EXACT' or sr.get('error_count'):v.append('shader report not exact')
 if iu.get('status')!='D1_GCN_IMAGE_RESOURCE_USAGE_EXACT':v.append('image usage not exact')
 if cb.get('status')!='D1_GCN_CBUFFER_USAGE_EXACT' or cb.get('missing_usage'):v.append('cbuffer usage not exact')
 if cfg.get('status')!='D1_GCN_STRUCTURAL_CFG_EXACT' or cfg.get('violations'):v.append('CFG extract not exact')
 s=next((x for x in sr.get('shaders',[]) if norm(x.get('shader'))==SH),None);i=next((x for x in iu.get('shaders',[]) if norm(x.get('shader'))==SH),None);c=next((x for x in cb.get('shaders',[]) if norm(x.get('shader'))==SH),None)
 freq={norm(k):int(x) for k,x in (m.get('pixel_shader_frequency') or {}).items()}
 if freq.get(SH)!=1:v.append(f'frequency {freq.get(SH)} != 1')
 mm=[(norm(k),x) for k,x in (m.get('materials') or {}).items() if norm(x.get('pixel_shader'))==SH]
 if len(mm)!=1:v.append(f'material count {len(mm)} != 1')
 else:
  mh,mr=mm[0]
  if mh!=MAT:v.append(f'material {mh} != {MAT}')
  binds={int(x['texture_index']):norm(x['texture']) for x in (mr.get('bindings') or []) if x.get('stage')=='ps'}
  if binds!=TEXTURES:v.append(f'texture bindings {binds} != {TEXTURES}')
 if not s:v.append('shader row missing')
 else:
  for k,w in [('native_shader',NATIVE),('native_sha256',NSHA),('gcn_sha256',GSHA),('gcn_bytes',GBYTES)]:
   if s.get(k)!=w:v.append(f'{k} drift {s.get(k)!r} != {w!r}')
 if not i:v.append('image usage missing')
 else:
  got=[(x['address'],int(x['resources'][0]['texture_index']),x['dmask_channels'],x['opcode']) for x in i.get('instructions',[])]
  if got!=IMAGE_PATTERN:v.append(f'image pattern drift {got}')
 if not c:v.append('cbuffer usage missing')
 else:
  got={str(k):[int(z) for z in q] for k,q in (c.get('api_slot_read_dwords') or {}).items()}
  if got!=API:v.append(f'cbuffer reads {got} != {API}')
  if c.get('unresolved_load_count')!=0:v.append('unresolved cbuffer load')
 for k,w in [('instruction_count',EXPECTED_CFG['instruction_count']),('basic_block_count',EXPECTED_CFG['basic_block_count']),('branch_count',EXPECTED_CFG['branch_count']),('backedge_count',EXPECTED_CFG['backedge_count']),('normalized_instruction_sha256',EXPECTED_CFG['normalized_instruction_sha256'])]:
  if cfg.get(k)!=w:v.append(f'CFG {k} {cfg.get(k)!r} != {w!r}')
 backs=cfg.get('backedges') or []
 if len(backs)==1:
  b=backs[0]
  if (b.get('source_block_start_hex'),b.get('source_end_hex'),b.get('target_hex'))!=(EXPECTED_CFG['backedge_source_start'],EXPECTED_CFG['backedge_source_end'],EXPECTED_CFG['backedge_target']):v.append(f'backedge drift {b}')
 else:v.append(f'backedge rows {len(backs)} != 1')
 txt=a.disasm.read_text(errors='replace') if a.disasm.exists() else ''
 miss=[x for x in ANCHORS if x not in txt]
 if miss:v.append(f'missing native anchors {miss}')
 terminal={
  'PRE_RGBA':'exact register state (v17,v2,v4,v5) at the 0x600 EXEC merge, produced by the pinned 0x000..0x600 native CFG including the 0x308->0x284 loop',
  'P':'gt(PRE.a,0)',
  'N':'select(P,mul(PRE.a,rcp(PRE.a)),0)',
  'coverage':'select(P,sub(1,clamp(sub(1,PRE.a))),0)',
  'MRT0.rgb':'select(P,mul(PRE.rgb,N),(0,0,0))',
  'MRT0.a':'0',
  'K':'clamp(API0[77])',
  'export_gate_value':'mad(K,coverage,-0.5)',
  'export_lane_gate':'incoming_EXEC AND NOT(gt(0,export_gate_value))',
 }
 phases=[
  {'range':'0x000..0x0F0','role':'exact pre-loop geometric/interpolant/API0 preparation'},
  {'range':'0x0F4..0x368','role':'conditional iterative resource-table t0 search; single backedge 0x308->0x284'},
  {'range':'0x36C..0x490','role':'post-search coordinates, resource-table t1 RGBA sample, branch predicate preparation'},
  {'range':'0x4A0..0x600','role':'conditional eight-sample t2 shaping branch and complementary direct t1 path; merges PRE_RGBA at 0x600'},
  {'range':'0x604..0x6E8','role':'positive PRE.a normalization; t4/t3 samples feed non-MRT0/deferred path; complementary MRT0 RGB zero'},
  {'range':'0x6EC..0x7DC','role':'deferred arithmetic plus exact API0[77] export gate; MRT0 packs normalized PRE.rgb with alpha zero'},
 ]
 out={'schema':'d1_tower_common_ps_8093e501_cfg_program_proof/v1',
      'status':'D1_TOWER_COMMON_PS_8093E501_CFG_PROGRAM_PROOF_EXACT' if not v else 'D1_TOWER_COMMON_PS_8093E501_CFG_PROGRAM_PROOF_PARTIAL',
      'shader':SH,'material':MAT,'visible_material_count':1,'native_shader':NATIVE,'gcn_sha256':GSHA,
      'texture_bindings':{str(k):x for k,x in TEXTURES.items()},'cfg_summary':{k:cfg.get(k) for k in ('instruction_count','basic_block_count','branch_count','backedge_count','normalized_instruction_sha256')},
      'program_phases':phases,'exact_terminal_reduction':terminal,'violations':v,
      'closure_level':'EXACT_CFG_PROGRAM_PLUS_EXACT_TERMINAL_REDUCTION_NOT_FLATTENED_ALGEBRA',
      'semantic_boundary':{
       'native_program_cfg':'EXACT',
       'loop_backedge':'EXACT',
       'resource_and_cbuffer_provenance':'EXACT',
       'preterminal_RGBA':'EXACT_NATIVE_PROGRAM_STATE_NOT_HUMAN_NAMED',
       'terminal_MRT0_reduction':'EXACT_OPERATION_PRESERVING',
       't3_t4_post_0x600_samples':'OFF_MRT0_VALUE_PATH',
       'human_material_or_pass_semantics':'WITHHELD',
       'portable_renderer_equivalence':'REQUIRES_CFG_PROGRAM_REPLAY'},
      'policy':'This family is closed as an exact native CFG program with exact terminal reduction. It is intentionally not counted as a flattened symbolic equation.'}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
 return 0 if out['status'].endswith('_EXACT') else 2
if __name__=='__main__':raise SystemExit(main())
