#!/usr/bin/env python3
"""Fail-closed source proof for the final non-DS/non-image 808EE505 GCN opcodes."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

GEM5_REV='f5c5a6e390f55dd5984977815bf9d0bd05da6945'
PYRAMID_REV='3971186651618d966ebfee161a044d7817462c79'
FPPS4_REV='04cefd43e6fddd1ab033e7980cd356d14c964905'

REQ={
 'gem5_vop2':{
  'v_sub_f32':'D.f = S0.f - S1.f.',
  'v_subrev_f32':'D.f = S1.f - S0.f.',
  'v_cndmask_b32':'D.u = (VCC[i] ? S1.u : S0.u)',
  'v_madmk_f32':'D.f = S0.f * K + S1.f; K is a 32-bit inline constant.',
 },
 'gem5_vop1':{
  'v_sqrt_f32':'D.f = sqrt(S0.f).',
  'v_rsq_f32':'D.f = 1.0 / sqrt(S0.f). Reciprocal square root with IEEE rules.',
  'v_cvt_i32_f32':'D.i = (int)S0.f.',
  'v_cvt_f32_i32':'D.f = (float)S0.i.',
 },
 'gem5_sop1':{
  's_mov_b32':'D.u = S0.u.',
  's_mov_b64':'D.u64 = S0.u64.',
  's_wqm_b64':'D[i] = (S0[(i & ~3):(i | 3)] != 0);',
 },
 'gem5_sopp':{
  's_waitcnt':'Wait for the counts of outstanding lds, vector-memory and',
  's_cbranch_execz':'if (EXEC == 0) then PC = PC + signext(SIMM16 * 4) + 4;',
  's_endpgm':'End of program; terminate wavefront.',
 },
 'pyramid_gcn3':{
  'v_add_i32':'D.u = S0.u + S1.u; VCC=carry-out',
 },
 'fpps4_vopc':{
  'v_cmp_lg_i32':'V_CMP_LG_I32    :emit_V_CMP_32(Op.OpINotEqual             ,dtInt32,false);',
 },
}

EQUATIONS={
 'v_sub_f32':'D.f = S0.f - S1.f',
 'v_subrev_f32':'D.f = S1.f - S0.f',
 'v_cndmask_b32':'D.u = VCC[lane] ? S1.u : S0.u',
 'v_madmk_f32':'D.f = S0.f * K + S1.f; K is the encoded 32-bit inline constant',
 'v_sqrt_f32':'D.f = sqrt(S0.f)',
 'v_rsq_f32':'D.f = 1.0 / sqrt(S0.f), IEEE reciprocal-square-root rules',
 'v_cvt_i32_f32':'D.i = int(S0.f); out-of-range/infinity saturate; NaN -> 0',
 'v_cvt_f32_i32':'D.f = float(S0.i)',
 's_mov_b32':'D.u = S0.u',
 's_mov_b64':'D.u64 = S0.u64',
 's_wqm_b64':'D[i] = any(S0[(i&~3):(i|3)]); SCC = (D != 0)',
 's_waitcnt':'wait until VM/EXP/LGKM outstanding counts are <= encoded thresholds',
 's_cbranch_execz':'if EXEC == 0: PC = PC + signext(SIMM16*4) + 4; else NOP',
 's_endpgm':'terminate wavefront after implicit S_WAITCNT 0',
 'v_add_i32':'D.u = S0.u + S1.u; VCC = carry-out',
 'v_cmp_lg_i32':'VCC[lane] = (int32(S0) != int32(S1))',
}

SOURCES={
 'gem5_vop2':('gem5',GEM5_REV,'src/arch/amdgpu/vega/insts/vop2.cc'),
 'gem5_vop1':('gem5',GEM5_REV,'src/arch/amdgpu/vega/insts/vop1.cc'),
 'gem5_sop1':('gem5',GEM5_REV,'src/arch/amdgpu/vega/insts/sop1.cc'),
 'gem5_sopp':('gem5',GEM5_REV,'src/arch/amdgpu/vega/insts/sopp.cc'),
 'pyramid_gcn3':('Pyramid',PYRAMID_REV,'src/Wrapper/GCN3Decoder.cpp'),
 'fpps4_vopc':('fpPS4',FPPS4_REV,'spirv/emit_vopc.pas'),
}

def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()

def main()->int:
 ap=argparse.ArgumentParser()
 for k in SOURCES:ap.add_argument('--'+k.replace('_','-'),dest=k,type=Path,required=True)
 ap.add_argument('-o','--output',type=Path,required=True);a=ap.parse_args();viol=[];proof={}
 try:
  op_sem={};src_meta={}
  for key,(repo,rev,path) in SOURCES.items():
   p=getattr(a,key);text=p.read_text(errors='strict');digest=sha(p)
   src_meta[key]={'repository':repo,'revision':rev,'path':path,'sha256':digest,'byte_count':p.stat().st_size}
   for op,needle in REQ[key].items():
    assert needle in text,(key,op,needle)
    op_sem[op]={'equation':EQUATIONS[op],'source_key':key,'source_revision':rev,'source_file_sha256':digest,'source_required_text':needle}
  assert set(op_sem)=={'s_mov_b32','s_mov_b64','s_wqm_b64','s_waitcnt','s_cbranch_execz','s_endpgm','v_sub_f32','v_subrev_f32','v_sqrt_f32','v_rsq_f32','v_cvt_i32_f32','v_cvt_f32_i32','v_add_i32','v_cmp_lg_i32','v_cndmask_b32','v_madmk_f32'}
  proof={'schema_version':1,'status':'D1_GCN_REMAINING_CORE_SOURCE_SEMANTICS_EXACT','shader':'808EE505','sources':src_meta,'opcode_semantics':dict(sorted(op_sem.items())),'semantic_boundary':'OPCODE_OPERATION_EXACT_LIVE_RUNTIME_VALUES_NOT_CAPTURED','violations':[]}
 except Exception as e:
  viol=[repr(e)];proof={'schema_version':1,'status':'D1_GCN_REMAINING_CORE_SOURCE_SEMANTICS_PARTIAL','violations':viol}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps({'status':proof['status'],'opcode_count':len(proof.get('opcode_semantics',{})),'violations':viol},indent=2));return 0 if not viol else 2
if __name__=='__main__':raise SystemExit(main())
