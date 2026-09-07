#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from pathlib import Path
SHADER='80876960';NATIVE='80876962';NATIVE_SHA='8a7ccc974ff0e86b1d84ad3596d3e83646b2490fc8e51a244522ae80de18f8ba';GCN='b045462d7896e5c5012e8587076f6c669455b35009c197cd1c50d4e7529a1ab6';MEMBERS=['80876545','808767B0','80876863']
USAGE=[('SubPtrFetchShader',0,0),('PtrVertexBufferTable',0,2),('PtrExtendedUserData',1,6),('ImmConstBuffer',10,8),('ImmConstBuffer',11,12),('ImmConstBuffer',12,16)]
ANCHORS=['v_cvt_f32_u32   v0, v10','v_cvt_f32_u32   v1, v11','v_mul_f32       v0, 0x3b808081, v0','v_lshlrev_b32   v2, 1, v8','v_lshlrev_b32   v3, 1, v9','v_cmp_le_f32    vcc, 0, v11','v_max_f32       v1, -v1, -v1','tbuffer_load_format_xyzw v[28:31], v3, s[8:11], 0 idxen format:[32_32_32_32,float]','tbuffer_load_format_xyzw v[32:35], v2, s[8:11], 0 idxen format:[32_32_32_32,float]','s_buffer_load_dwordx4 s[0:3], s[12:15], 0x14','s_buffer_load_dwordx4 s[0:3], s[12:15], 0x1c','s_buffer_load_dwordx4 s[4:7], s[12:15], 0x18','exp             param0, v16, v17, v18, v0','exp             param1, v20, v21, v22, v22','exp             param2, v1, v2, v3, v8','exp             param3, v4, v7, v4, v7','exp             param4, v27, v5, v6, v8']
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--material-state',type=Path,required=True);ap.add_argument('--shader-census',type=Path,required=True);ap.add_argument('--disassembly',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();state=json.loads(a.material_state.read_text());c=json.loads(a.shader_census.read_text());asm=a.disassembly.read_text();v=[]
 if state.get('status')!='D1_MATERIAL_STAGE_STATE_EXACT':v.append('state not exact')
 if c.get('status')!='D1_XUR_ALL_NATIVE_SHADER_DISASSEMBLY_EXACT':v.append('census not exact')
 r=next((x for x in c['shaders'] if x['shader']==SHADER),None)
 if not r:v.append('shader missing')
 else:
  for k,e in [('native_shader',NATIVE),('native_sha256',NATIVE_SHA),('gcn_sha256',GCN),('gcn_bytes',900),('instruction_count_approx',169)]:
   if r.get(k)!=e:v.append(f'{k} mismatch')
  if r.get('stages')!=['vs']:v.append('not VS-only')
  got=[(x['usage_name'],x['api_slot'],x['start_register']) for x in r['usage']['slots']]
  if got!=USAGE:v.append(f'usage mismatch {got!r}')
 for n in ANCHORS:
  if n not in asm:v.append(f'missing anchor {n}')
 gotm=sorted(m for m,x in state['materials'].items() if x['vs']['shader']==SHADER)
 if gotm!=sorted(MEMBERS):v.append(f'member set mismatch {gotm!r}')
 for m in MEMBERS:
  vs=state['materials'][m]['vs']
  if vs['tfx_bytecode']['bytes_hex']!='' or vs['tfx_private_constants']['count'] or vs['cbuffers']['count'] or vs['textures']['count'] or vs['samplers']['count']:v.append(f'{m}: unexpected local VS state')
  if vs['tfx_disassembly']['complete'] is not True:v.append(f'{m}: framing incomplete')
 if v:
  out={'schema_version':1,'status':'D1_XUR_VS_80876960_TWO_INFLUENCE_DQ_PARTIAL','violations':v}
 else:
  out={'schema_version':1,'status':'D1_XUR_VS_80876960_TWO_INFLUENCE_DQ_EXACT','shader':SHADER,'native_shader':NATIVE,'gcn_sha256':GCN,'scope_materials':MEMBERS,'scope_material_count':3,'post_fetch_register_roles':{'v4_v5_v6':'source position xyz','v8_v9':'two transform-palette indices','v10_v11':'two unsigned weight lanes, normalized by 1/255 before palette loads overwrite these registers','v12_v13':'source UV pair','v16_v17_v18':'source normal xyz','v20_v21_v22':'source tangent xyz','v23':'tangent-basis handedness multiplier'},'instruction_level_equations':{'weights':'w0=float(weight0_u32)/255; w1=float(weight1_u32)/255','palette_records':'q0=api10[2*index0]; d0=api10[2*index0+1]; q1=api10[2*index1]; d1=api10[2*index1+1]','hemisphere_alignment':'if dot(q0,q1)<0, w1=-w1','dual_quaternion_blend':'Qraw=w0*q0+w1*q1; inv=1/length(Qraw); Q=Qraw*inv; D=(w0*d0+w1*d1)*inv','position_decode':'p=api11[20:22]+api11[23]*source_position','translation':'translation=2*(D*conjugate(Q)).xyz','skinned_position':'P=rotate(Q,p)+translation','normal_tangent':'N=rotate(Q,source_normal); T=rotate(Q,source_tangent); B=handedness*cross(N,T)','clip_position':'pos0=extended_matrix_col0*P.x+extended_matrix_col1*P.y+extended_matrix_col2*P.z+extended_matrix_col3','normal_scalar':'a=saturate(dot(api11[28:30],N)+api11[31])','uv':'uv=(api11[26]+api11[24]*source_uv.x, api11[27]+api11[25]*source_uv.y)','exports':'param0=float4(N,a); param1=float4(T.xyz,T.z); param2=float4(B,1); param3=float4(uv,uv); param4=float4(P,1)'},'promoted_skinning_semantics':{'influence_count':2,'weights':'native integer lanes are normalized by exact float constant 1/255','hemisphere_correction':'second weight sign is conditionally flipped from quaternion dot-product sign before blending','palette':'each influence selects two consecutive api10 float4 records: real quaternion + dual quaternion record','normalization':'real and dual blends share the real-quaternion reciprocal length'},'dual_quaternion_skinning_dataflow_complete_for_scoped_binary':True,'fetch_shader_source_layout_complete':False,'global_buffer_engine_names_complete':False,'portable_skinning_recreation_complete':False,'violations':[],'policy':'Post-fetch two-influence DQ skinning is closed from exact native GCN. Fetch-shader byte offsets/formats and engine-facing api10/api11/api12 names remain withheld.'}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out if v else {k:out[k] for k in ['status','scope_material_count','instruction_level_equations','promoted_skinning_semantics','violations']},indent=2));return 2 if v else 0
if __name__=='__main__':raise SystemExit(main())
