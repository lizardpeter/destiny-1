#!/usr/bin/env python3
"""Fail-closed VGPR register/lane write frontier over the exact D1 GFX7 corpus."""
from __future__ import annotations
import argparse,collections,json,re
from pathlib import Path
import d1_gcn_vgpr_machine_semantics_v1 as sem

SCHEMA='d1_gcn_vgpr_machine_frontier/v1'
STATUS='D1_GCN_VGPR_MACHINE_FRONTIER_EXACT'
EXPECTED_PROGRAMS=26464
EXPECTED_INSTRUCTIONS=4896165
EXPECTED={
 'vgpr_def_instruction_count':3690362,
 'vgpr_def_entry_count':3864039,
 'vgpr_use_instruction_count':3561612,
 'vgpr_use_entry_count':6469818,
 'programs_with_vgpr_defs':26464,
 'programs_with_vgpr_uses':26464,
 'exec_masked_def_instruction_count':3680926,
 'exec_masked_def_entry_count':3854603,
 'single_lane_unmasked_instruction_count':9436,
 'single_lane_unmasked_def_entry_count':9436,
 'dynamic_vgpr_source_instruction_count':6,
 'max_vgpr_index':251,
}
EXPECTED_DEF_WIDTH_HIST={1:3603865,2:32444,3:20926,4:33127}
EXPECTED_USE_WIDTH_HIST={1:1383421,2:1600347,3:425673,4:152171}
EXPECTED_DEF_OPCODE_COUNTS={
'buffer_load_dword':40,'ds_read2_b32':401,'ds_read_b32':89,'ds_swizzle_b32':9556,'image_gather4_lz':6,'image_gather4_lz_o':2,'image_get_lod':2953,'image_get_resinfo':48,'image_load_mip':6623,'image_sample':98786,'image_sample_d':150,'image_sample_l':2953,'image_sample_lz':3941,'image_sample_lz_o':4,'tbuffer_load_format_xyz':4,'tbuffer_load_format_xyzw':10085,'v_add_f32':185521,'v_add_i32':6796,'v_and_b32':7949,'v_ceil_f32':30,'v_cndmask_b32':114066,'v_cos_f32':7880,'v_cubeid_f32':2914,'v_cubema_f32':2914,'v_cubesc_f32':2914,'v_cubetc_f32':2914,'v_cvt_f32_i32':5352,'v_cvt_f32_u32':1246,'v_cvt_i32_f32':16789,'v_cvt_pknorm_u16_f32':2,'v_cvt_pkrtz_f16_f32':53798,'v_cvt_u32_f32':692,'v_exp_f32':23611,'v_floor_f32':8531,'v_fract_f32':45835,'v_interp_mov_f32':6,'v_interp_p1_f32':212682,'v_interp_p2_f32':212682,'v_log_f32':22218,'v_lshl_b64':47,'v_lshlrev_b32':11149,'v_lshrrev_b32':7,'v_mac_f32':648490,'v_mac_legacy_f32':60924,'v_mad_f32':169034,'v_mad_i32_i24':4,'v_mad_legacy_f32':23896,'v_madak_f32':39748,'v_madmk_f32':35037,'v_max_f32':73007,'v_max_i32':64,'v_max_legacy_f32':15,'v_min3_f32':1,'v_min_f32':5816,'v_mov_b32':359705,'v_movrels_b32':6,'v_mul_f32':749175,'v_mul_hi_u32':1,'v_mul_i32_i24':46,'v_mul_legacy_f32':123272,'v_mul_lo_i32':40,'v_mul_lo_u32':2202,'v_or_b32':7888,'v_rcp_f32':28293,'v_rndne_f32':8243,'v_rsq_clamp_f32':30510,'v_rsq_f32':497,'v_sin_f32':5939,'v_sqrt_f32':23066,'v_sub_f32':141365,'v_sub_i32':4725,'v_subrev_f32':55728,'v_trunc_f32':3,'v_writelane_b32':9436}
VREG=re.compile(r'^v(\d+)$')
VRANGE=re.compile(r'^v\[(\d+):(\d+)\]$')

def build(ir_dir:Path):
 violations=[];paths=sorted(ir_dir.glob('*.json'));tot=collections.Counter();defops=collections.Counter();defentries=collections.Counter();useops=collections.Counter();useentries=collections.Counter();dh=collections.Counter();uh=collections.Counter();writelanes=collections.Counter();examples={};total_ins=0;maxidx=-1
 if len(paths)!=EXPECTED_PROGRAMS:violations.append(f'ir_file_count:{len(paths)}!={EXPECTED_PROGRAMS}')
 for p in paths:
  sha=p.stem.lower();d=json.loads(p.read_text());ins=d.get('instructions') or [];total_ins+=len(ins);pd=pu=False
  if d.get('status')!='D1_GCN_STRUCTURAL_IR_COMPLETE':violations.append(f'ir_status:{sha}:{d.get("status")!r}')
  if (d.get('parse_accounting') or {}).get('status')!='D1_GCN_STRUCTURAL_PARSE_ACCOUNTING_EXACT':violations.append(f'parse_status:{sha}')
  for x in ins:
   defs=x.get('defs') or [];uses=x.get('uses') or []
   if any(VRANGE.fullmatch(z) for z in defs):violations.append(f'range_def_not_normalized:{sha}:{x["index"]}')
   if any(VRANGE.fullmatch(z) for z in uses):violations.append(f'range_use_not_normalized:{sha}:{x["index"]}')
   vd=[z for z in defs if VREG.fullmatch(z)];vu=[z for z in uses if VREG.fullmatch(z)]
   if vd:
    pd=True;tot['vgpr_def_instruction_count']+=1;tot['vgpr_def_entry_count']+=len(vd);dh[len(vd)]+=1;defops[x['opcode']]+=1;defentries[x['opcode']]+=len(vd)
    if x['opcode'] not in sem.VGPR_DEF_OPCODES:violations.append(f'unregistered_vgpr_def_opcode:{sha}:{x["index"]}:{x["opcode"]}')
    beh=sem.behavior(x['opcode']) if x['opcode'] in sem.VGPR_DEF_OPCODES else None
    if beh and beh['write_behavior']=='SINGLE_LANE_UNMASKED':tot['single_lane_unmasked_instruction_count']+=1;tot['single_lane_unmasked_def_entry_count']+=len(vd)
    elif beh:tot['exec_masked_def_instruction_count']+=1;tot['exec_masked_def_entry_count']+=len(vd)
    if x['opcode'] in sem.DYNAMIC_SOURCE:tot['dynamic_vgpr_source_instruction_count']+=1
    for z in vd:maxidx=max(maxidx,int(z[1:]))
    examples.setdefault(('def',x['opcode']),{'gcn_sha256':sha,'instruction':x['index'],'address':x['address_hex'],'opcode':x['opcode'],'operands':x.get('operands') or [],'defs':vd,'uses':vu})
   if vu:
    pu=True;tot['vgpr_use_instruction_count']+=1;tot['vgpr_use_entry_count']+=len(vu);uh[len(vu)]+=1;useops[x['opcode']]+=1;useentries[x['opcode']]+=len(vu)
    for z in vu:maxidx=max(maxidx,int(z[1:]))
   if x['opcode']=='v_writelane_b32':
    a=x.get('operands') or []
    if len(vd)!=1 or len(a)<3:violations.append(f'writelane_shape:{sha}:{x["index"]}:{a!r}:{vd!r}')
    else:
     try:lane=int(a[2],0)
     except Exception:violations.append(f'writelane_nonliteral_lane:{sha}:{x["index"]}:{a[2]}');lane=None
     if lane is not None:
      writelanes[lane]+=1
      if not 0<=lane<64:violations.append(f'writelane_lane_oob:{sha}:{x["index"]}:{lane}')
     if vu:violations.append(f'writelane_structural_vgpr_use_unexpected:{sha}:{x["index"]}:{vu}')
   if x['opcode']=='v_movrels_b32':
    a=x.get('operands') or []
    if len(vd)!=1 or len(vu)!=1 or len(a)<2:violations.append(f'movrels_shape:{sha}:{x["index"]}:{a!r}:{vd!r}:{vu!r}')
  tot['programs_with_vgpr_defs']+=int(pd);tot['programs_with_vgpr_uses']+=int(pu)
 if total_ins!=EXPECTED_INSTRUCTIONS:violations.append(f'instruction_count:{total_ins}!={EXPECTED_INSTRUCTIONS}')
 tot['max_vgpr_index']=maxidx
 for k,w in EXPECTED.items():
  if tot[k]!=w:violations.append(f'{k}:{tot[k]}!={w}')
 for k in EXPECTED:tot.setdefault(k,0)
 if dict(sorted(dh.items()))!=EXPECTED_DEF_WIDTH_HIST:violations.append(f'def_width_hist:{dict(dh)}')
 if dict(sorted(uh.items()))!=EXPECTED_USE_WIDTH_HIST:violations.append(f'use_width_hist:{dict(uh)}')
 if dict(sorted(defops.items()))!=EXPECTED_DEF_OPCODE_COUNTS:violations.append('def_opcode_histogram_mismatch')
 if set(defops)!=sem.VGPR_DEF_OPCODES:violations.append(f'def_opcode_set:{sorted(defops)}')
 if set(writelanes)!=(set(range(40))):violations.append(f'writelane_lane_set:{sorted(writelanes)}')
 return {
  'schema':SCHEMA,'status':STATUS if not violations else 'D1_GCN_VGPR_MACHINE_FRONTIER_WITH_VIOLATIONS','sources':{'ir_dir':str(ir_dir),'machine_semantics_status':sem.STATUS},
  'coverage':{'exact_program_count':len(paths),'exact_instruction_count':total_ins,**dict(sorted(tot.items())),
   'vgpr_def_width_histogram':{str(k):v for k,v in sorted(dh.items())},'vgpr_use_width_histogram':{str(k):v for k,v in sorted(uh.items())},
   'vgpr_def_opcode_counts':dict(sorted(defops.items())),'vgpr_def_entry_opcode_counts':dict(sorted(defentries.items())),
   'vgpr_use_opcode_count':len(useops),'vgpr_use_opcode_counts':dict(sorted(useops.items())),'vgpr_use_entry_opcode_counts':dict(sorted(useentries.items())),
   'writelane_literal_lane_counts':{str(k):v for k,v in sorted(writelanes.items())},'shader_expression_semantic_promotions':0},
  'examples':[v for _,v in sorted(examples.items())],'violations':violations,
  'semantic_boundary':{'vgpr_destination_lane_mutation':'SOURCE_CLOSED','ordinary_vector_exec_gating':'SOURCE_CLOSED','v_writelane_exec_exception':'SOURCE_CLOSED','v_movrels_dynamic_source':'SOURCE_CLOSED_IDENTITY','vgpr_value_semantics':'WITHHELD','lane_aware_vgpr_ssa':'NEXT_GATE','shader_expression_semantics':'WITHHELD','shader_expression_semantic_promotions':0},
  'policy':'The exact VGPR destination/use surface is enumerated register-by-register. Ordinary vector destination writes are EXEC-gated, V_WRITELANE_B32 is explicitly unmasked and changes one literal-selected lane, and V_MOVRELS_B32 carries an explicit M0-indexed dynamic source boundary. No arithmetic or shader meaning is inferred.'
 }

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--ir-dir',type=Path,required=True);ap.add_argument('-o','--output',type=Path,required=True);a=ap.parse_args();o=build(a.ir_dir);a.output.write_text(json.dumps(o,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':o['status'],'coverage':{k:o['coverage'][k] for k in ['exact_program_count','exact_instruction_count',*EXPECTED]},'violation_count':len(o['violations'])},indent=2));return 0 if not o['violations'] else 2
if __name__=='__main__':raise SystemExit(main())
