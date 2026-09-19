#!/usr/bin/env python3
"""Prove exact signed-cross-product export structure in Crota vertex shaders."""
from __future__ import annotations
import argparse,json,re
from pathlib import Path

CASES={
 '809DE9AB':{
  'param0':'exp             param0, v20, v21, v22, v0',
  'param1':'exp             param1, v24, v25, v26, v26',
  'param2':'exp             param2, v1, v2, v3, v8',
  'one':'v_mov_b32       v8, 1.0',
  'anchors':[
   'v_mul_f32       v1, v22, v25',
   'v_mad_f32       v1, v21, v26, -v1',
   'v_mul_f32       v2, v20, v26',
   'v_mad_f32       v2, v22, v24, -v2',
   'v_mul_f32       v3, v21, v24',
   'v_mad_f32       v3, v20, v25, -v3',
   'v_mul_f32       v1, v27, v1',
   'v_mul_f32       v2, v27, v2',
   'v_mul_f32       v3, v27, v3',
  ],
  'a':['v20','v21','v22'],'b':['v24','v25','v26'],'factor':'v27',
 },
 '809DF743':{
  'param0':'exp             param0, v12, v13, v14, v0',
  'param1':'exp             param1, v16, v17, v18, v18',
  'param2':'exp             param2, v1, v2, v3, v8',
  'one':'v_mov_b32       v8, 1.0',
  'anchors':[
   'v_mul_f32       v1, v14, v17',
   'v_mad_f32       v1, v13, v18, -v1',
   'v_mul_f32       v2, v12, v18',
   'v_mad_f32       v2, v14, v16, -v2',
   'v_mul_f32       v3, v13, v16',
   'v_mad_f32       v3, v12, v17, -v3',
   'v_mul_f32       v1, v19, v1',
   'v_mul_f32       v2, v19, v2',
   'v_mul_f32       v3, v19, v3',
  ],
  'a':['v12','v13','v14'],'b':['v16','v17','v18'],'factor':'v19',
 },
}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--disasm-dir',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
 rows=[];violations=[]
 for h,q in CASES.items():
  p=a.disasm_dir/f'PS_{h}_GFX700.s'
  if not p.exists():p=a.disasm_dir/f'PS_{h}.s'
  if not p.exists():violations.append(f'{h}: disassembly absent');continue
  text=p.read_text(errors='replace')
  missing=[x for x in [q['param0'],q['param1'],q['param2'],q['one'],*q['anchors']] if x not in text]
  if missing:violations.append(f'{h}: missing anchors {missing}')
  rows.append({'vertex_shader':h,'vector_a_registers':q['a'],'vector_b_registers':q['b'],
               'signed_cross_factor_register':q['factor'],
               'export_relation':'param2.xyz = factor * cross(param0.xyz, param1.xyz); param2.w = 1.0',
               'factor_semantic':'WITHHELD','vector_semantics':'WITHHELD','missing_anchors':missing})
 out={'schema':'d1_crota_vs_signed_cross_export/v1',
      'status':'D1_CROTA_VS_SIGNED_CROSS_EXPORT_EXACT' if len(rows)==2 and not violations else 'D1_CROTA_VS_SIGNED_CROSS_EXPORT_PARTIAL',
      'shaders':rows,'violations':violations,
      'policy':'The signed-cross relation is an exact register-level identity. It does not name the vectors as tangent/normal/bitangent until independent semantic linkage proves that role.'}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
 return 0 if out['status']=='D1_CROTA_VS_SIGNED_CROSS_EXPORT_EXACT' else 2
if __name__=='__main__':raise SystemExit(main())
