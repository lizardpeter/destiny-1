#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from pathlib import Path
HEADERS={'8087695B':'8087695D','809DE9AB':'809DE9AC'}
NATIVE_SHA='33742b027c679824ecfb7660ed6589cad985aa3f0ef10f691dc29c6233cd12b5'
GCN='24392dbd8f217a832456372a8d9c24d3ef365ab5a0b8bcd362882ca845052964'
MEMBERS=['808761E0','808762D5','8087640F','80876410','80876411','8087642C','8087642D','808764C9','808764CA','80876508','8087652A','808767AE','808767AF','80C885F2']
COUNTS={'8087695B':13,'809DE9AB':1}
USAGE=[('SubPtrFetchShader',0,0),('PtrVertexBufferTable',0,2),('PtrExtendedUserData',1,6),('ImmConstBuffer',10,8),('ImmConstBuffer',11,12),('ImmConstBuffer',12,16)]
ANCHORS=['v_lshlrev_b32   v0, 1, v12','v_lshlrev_b32   v1, 1, v13','v_lshlrev_b32   v2, 1, v14','v_lshlrev_b32   v3, 1, v15','v_cmp_le_f32    vcc, 0, v7','v_cndmask_b32   v7, -v9, v9, vcc','v_cmp_le_f32    vcc, 0, v18','v_cndmask_b32   v10, -v10, v10, vcc','v_cmp_ge_f32    s[0:1], v19, 0','v_cndmask_b32   v11, -v11, v11, s[0:1]','tbuffer_load_format_xyzw v[40:43], v1, s[8:11], 0 idxen format:[32_32_32_32,float]','tbuffer_load_format_xyzw v[44:47], v0, s[8:11], 0 idxen format:[32_32_32_32,float]','tbuffer_load_format_xyzw v[48:51], v2, s[8:11], 0 idxen format:[32_32_32_32,float]','tbuffer_load_format_xyzw v[0:3], v3, s[8:11], 0 idxen format:[32_32_32_32,float]','s_buffer_load_dwordx4 s[0:3], s[12:15], 0x14','s_buffer_load_dwordx4 s[0:3], s[12:15], 0x1c','s_buffer_load_dwordx4 s[4:7], s[12:15], 0x18','exp             param0, v20, v21, v22, v0','exp             param1, v24, v25, v26, v26','exp             param2, v1, v2, v3, v8','exp             param3, v4, v7, v4, v7','exp             param4, v33, v5, v6, v8']
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--material-state',type=Path,required=True);ap.add_argument('--shader-census',type=Path,required=True);ap.add_argument('--disassembly',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();s=json.loads(a.material_state.read_text());c=json.loads(a.shader_census.read_text());asm=a.disassembly.read_text();viol=[]
 if s.get('status')!='D1_MATERIAL_STAGE_STATE_EXACT':viol.append('state not exact')
 if c.get('status')!='D1_XUR_ALL_NATIVE_SHADER_DISASSEMBLY_EXACT':viol.append('census not exact')
 by={x['shader']:x for x in c['shaders']}
 for h,n in HEADERS.items():
  r=by.get(h)
  if not r:viol.append(f'missing {h}');continue
  for k,e in [('native_shader',n),('native_sha256',NATIVE_SHA),('gcn_sha256',GCN),('gcn_bytes',1052),('instruction_count_approx',198)]:
   if r.get(k)!=e:viol.append(f'{h}: {k} mismatch')
  if r.get('stages')!=['vs']:viol.append(f'{h}: not VS-only')
  got=[(x['usage_name'],x['api_slot'],x['start_register']) for x in r['usage']['slots']]
  if got!=USAGE:viol.append(f'{h}: usage mismatch')
 for n in ANCHORS:
  if n not in asm:viol.append(f'missing anchor {n}')
 got=[];counts={h:0 for h in HEADERS}
 for m,row in s['materials'].items():
  h=row['vs']['shader']
  if h in HEADERS:
   got.append(m);counts[h]+=1;vs=row['vs']
   if vs['tfx_bytecode']['bytes_hex']!='' or vs['tfx_private_constants']['count'] or vs['cbuffers']['count'] or vs['textures']['count'] or vs['samplers']['count']:viol.append(f'{m}: unexpected local VS state')
   if vs['tfx_disassembly']['complete'] is not True:viol.append(f'{m}: TFX framing incomplete')
 if sorted(got)!=sorted(MEMBERS):viol.append(f'member set mismatch {sorted(got)!r}')
 if counts!=COUNTS:viol.append(f'header counts mismatch {counts!r}')
 if viol:out={'schema_version':1,'status':'D1_XUR_VS_24392DBD_FOUR_INFLUENCE_DQ_PARTIAL','violations':viol}
 else:out={'schema_version':1,'status':'D1_XUR_VS_24392DBD_FOUR_INFLUENCE_DQ_EXACT','shader_headers':sorted(HEADERS),'native_shader_tags':HEADERS,'native_payload_sha256':NATIVE_SHA,'gcn_sha256':GCN,'scope_materials':MEMBERS,'scope_material_count':14,'header_material_counts':counts,'post_fetch_register_roles':{'v4_v5_v6':'source position xyz','v8_v9_v10_v11':'four post-fetch blend weights; their source encoding is not assigned here','v12_v13_v14_v15':'four transform-palette indices','v16_v17':'source UV pair','v20_v21_v22':'source normal xyz','v24_v25_v26':'source tangent xyz','v27':'tangent-basis handedness multiplier'},'instruction_level_equations':{'palette_records':'for i=0..3: qi=api10[2*index_i]; di=api10[2*index_i+1]','hemisphere_alignment':'q0 is reference; for i=1..3, if dot(q0,qi)<0 then wi=-wi','dual_quaternion_blend':'Qraw=sum_i(wi*qi); inv=1/length(Qraw); Q=Qraw*inv; D=sum_i(wi*di)*inv','position_decode':'p=api11[20:22]+api11[23]*source_position','translation':'translation=2*(D*conjugate(Q)).xyz','skinned_position':'P=rotate(Q,p)+translation','normal_tangent':'N=rotate(Q,source_normal); T=rotate(Q,source_tangent); B=handedness*cross(N,T)','clip_position':'pos0=extended_matrix_col0*P.x+extended_matrix_col1*P.y+extended_matrix_col2*P.z+extended_matrix_col3','normal_scalar':'a=saturate(dot(api11[28:30],N)+api11[31])','uv':'uv=(api11[26]+api11[24]*source_uv.x, api11[27]+api11[25]*source_uv.y)','exports':'param0=float4(N,a); param1=float4(T.xyz,T.z); param2=float4(B,1); param3=float4(uv,uv); param4=float4(P,1)'},'promoted_skinning_semantics':{'influence_count':4,'hemisphere_correction':'weights 1..3 are independently sign-corrected against q0 using quaternion dot products before blend','palette':'each of four indices selects consecutive api10 real+dual float4 records','normalization':'all four real quaternions are blended, normalized once, and the dual blend is scaled by the same reciprocal length'},'dual_quaternion_skinning_dataflow_complete_for_scoped_binary':True,'fetch_shader_weight_encoding_complete':False,'fetch_shader_source_layout_complete':False,'global_buffer_engine_names_complete':False,'portable_skinning_recreation_complete':False,'violations':[],'policy':'Post-fetch four-influence dual-quaternion skinning and the param0..param4 contract are exact. Fetch-shader byte offsets/formats and the pre-main-shader encoding/normalization of the four weight lanes remain withheld.'}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out if viol else {k:out[k] for k in ['status','scope_material_count','header_material_counts','instruction_level_equations','promoted_skinning_semantics','violations']},indent=2));return 2 if viol else 0
if __name__=='__main__':raise SystemExit(main())
