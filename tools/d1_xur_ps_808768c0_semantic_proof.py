#!/usr/bin/env python3
"""Fail-closed instruction-level semantic proof for Xur PS 808768C0.

Closes the exact retail GCN arithmetic for the five current Xur materials using
this shader. Two of those materials serialize no texture_index 2 even though the
native GCN unconditionally samples resource-table index 2; that runtime/default
resource binding remains an explicit frontier rather than being guessed.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

SHADER='808768C0'
NATIVE_SHADER='808768C5'
NATIVE_SHA='4bf16d3a8eb0d04f4822042a711b7d04cc77f854c4052c0a5db75ff45fc8c937'
GCN_SHA='7d3c95a7d1ce0663ca1d2d715c55cc9e3936d581841c5c7a43ac706bca408fcf'
MEMBERS=['808762D5','8087642D','808764CA','80876688','808768BB']
WITH_T2=['808762D5','8087642D','808764CA']
WITHOUT_T2=['80876688','808768BB']
TFX_HEX='49004721490147224902472349034724490447254905472649064727'
SAMPLERS=['80AAE177','80AAE177','80AAE177','80AAE177','80AAE176','80AAE177','80AAE177']
SAMPLER_SHAS=[
'2c670016bbb70b68bd2f69dd4a30145bf7d61a47c1bf4c3acba8321b46976ecb',
'2c670016bbb70b68bd2f69dd4a30145bf7d61a47c1bf4c3acba8321b46976ecb',
'2c670016bbb70b68bd2f69dd4a30145bf7d61a47c1bf4c3acba8321b46976ecb',
'2c670016bbb70b68bd2f69dd4a30145bf7d61a47c1bf4c3acba8321b46976ecb',
'0bcdaa82ea0d8588e313f29998f6c7b9166e7d28d40b13d422348d55ae5dc208',
'2c670016bbb70b68bd2f69dd4a30145bf7d61a47c1bf4c3acba8321b46976ecb',
'2c670016bbb70b68bd2f69dd4a30145bf7d61a47c1bf4c3acba8321b46976ecb',
]
FIXED={1:'80AB04CD',3:'80AB04C1',4:'80AB04CF',5:'808768AD',6:'80876987'}
EXPECTED_T0={
'808762D5':'808763B7','8087642D':'80876458','808764CA':'808764E8','80876688':'80AAF8BE','808768BB':'80AB04CB'}
EXPECTED_T2={'808762D5':'808763B8','8087642D':'80876459','808764CA':'808764E9'}
ANCHORS=[
'image_sample    v[8:9], v[6:9], s[28:35], s[36:39] dmask:3',
'image_sample    v[4:5], v[4:7], s[40:47], s[48:51] dmask:3',
'v_sqrt_f32      v4, v4',
'v_rsq_clamp_f32 v8, v8',
'v_max_f32       v16, v13, v13 mul:2',
'v_mad_legacy_f32 v17, -v11, v4, v17',
'v_cubema_f32    v4, v17, v18, v16',
'image_get_lod   v11, v[27:30], s[20:27], s[44:47] dmask:2',
'image_sample_l  v[26:29], v[26:29], s[20:27], s[44:47] dmask:15',
'image_sample    v2, v[6:9], s[28:35], s[36:39] dmask:4',
'image_sample    v3, v[3:6], s[48:55], s[12:15]',
'v_log_f32       v4, v4','v_exp_f32       v4, v4',
'v_madak_f32     v6, v18, v6, 0x3f000000',
'exp             mrt1, v1, v1, v5, v5 compr',
'exp             mrt0, v1, v1, v0, v0 done compr vm',
]

def flat(ps):return [float(v) for row in ps['cbuffers']['items'] for v in row['value']]

def main():
 ap=argparse.ArgumentParser();
 ap.add_argument('--material-state',type=Path,required=True);ap.add_argument('--shader-census',type=Path,required=True)
 ap.add_argument('--image-usage',type=Path,required=True);ap.add_argument('--texture-manifest',type=Path,required=True)
 ap.add_argument('--disassembly',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
 state=json.loads(a.material_state.read_text());census=json.loads(a.shader_census.read_text());images=json.loads(a.image_usage.read_text());manifest=json.loads(a.texture_manifest.read_text());asm=a.disassembly.read_text();viol=[]
 if state.get('status')!='D1_MATERIAL_STAGE_STATE_EXACT':viol.append('material state checkpoint not exact')
 if census.get('status')!='D1_XUR_ALL_NATIVE_SHADER_DISASSEMBLY_EXACT':viol.append('shader census checkpoint not exact')
 if images.get('status')!='D1_GCN_IMAGE_RESOURCE_USAGE_EXACT':viol.append('image usage checkpoint not exact')
 if manifest.get('visible_material_count')!=54 or manifest.get('material_decode_errors') or manifest.get('texture_errors'):viol.append('texture manifest checkpoint not exact/error-free')
 sr=next((x for x in census.get('shaders',[]) if x.get('shader')==SHADER),None)
 if not sr:viol.append('shader absent')
 else:
  for k,v in [('native_shader',NATIVE_SHADER),('native_sha256',NATIVE_SHA),('gcn_sha256',GCN_SHA),('gcn_bytes',1088),('instruction_count_approx',226)]:
   if sr.get(k)!=v:viol.append(f'{k} mismatch: {sr.get(k)!r}')
  if sr.get('stages')!=['ps']:viol.append('not PS-only')
 ir=next((x for x in images.get('shaders',[]) if x.get('shader')==SHADER),None)
 if not ir:viol.append('image usage absent')
 else:
  if ir.get('image_instruction_count')!=8:viol.append('expected 8 image instructions')
  if ir.get('used_texture_indices')!=[0,1,2,3,4,5,6]:viol.append(f"used texture indices mismatch {ir.get('used_texture_indices')}")
  exp={'0':1,'1':1,'2':1,'3':1,'4':2,'5':1,'6':1}
  if ir.get('texture_instruction_counts')!=exp:viol.append('texture instruction counts mismatch')
  if ir.get('unmatched_image_instruction_count')!=0:viol.append('unmatched image instructions')
 for n in ANCHORS:
  if n not in asm:viol.append('missing disassembly anchor: '+n)
 consumed={};binding={}
 for mh in MEMBERS:
  row=state.get('materials',{}).get(mh)
  if not row:viol.append('missing material '+mh);continue
  ps=row['ps']
  if ps.get('shader')!=SHADER:viol.append(f'{mh}: PS mismatch')
  if row.get('material_state4_hex')!='00000000':viol.append(f'{mh}: state mismatch')
  if ps['tfx_bytecode'].get('bytes_hex')!=TFX_HEX:viol.append(f'{mh}: TFX mismatch')
  if ps.get('tfx_disassembly',{}).get('complete') is not True:viol.append(f'{mh}: TFX incomplete')
  if [x['first_dword_hex'] for x in ps['samplers']['items']]!=SAMPLERS:viol.append(f'{mh}: sampler tags mismatch')
  gotsh=[(r.get('native_sampler') or {}).get('payload_sha256') for r in ps.get('sampler_references',[])]
  if gotsh!=SAMPLER_SHAS:viol.append(f'{mh}: native sampler payload mismatch')
  tex={int(x['texture_index']):x['texture'] for x in ps['textures']['items']}
  if tex.get(0)!=EXPECTED_T0[mh]:viol.append(f'{mh}: t0 mismatch')
  for idx,tag in FIXED.items():
   if tex.get(idx)!=tag:viol.append(f'{mh}: t{idx} mismatch {tex.get(idx)} != {tag}')
  if mh in WITH_T2:
   if tex.get(2)!=EXPECTED_T2[mh]:viol.append(f'{mh}: t2 mismatch')
  else:
   if 2 in tex:viol.append(f'{mh}: expected serialized t2 absence')
  binding[mh]={str(k):v for k,v in sorted(tex.items())}
  cb=flat(ps)
  expected={8:2.0,9:-1.0,20:2.0,21:-1.0,36:1.0,40:0.0,44:-1.2999999523162842,45:2.299999952316284,48:8.0,49:8.0,50:0.0,51:0.0,52:0.0,53:0.4000000059604645,54:5.0,56:2.0,57:-1.0,60:0.9099999666213989,61:0.39000001549720764,81:0.051960788667201996}
  got={i:cb[i] for i in expected}
  if got!=expected:viol.append(f'{mh}: consumed constants mismatch {got!r}')
  consumed[mh]={'uv0_rows':[ps['cbuffers']['items'][0]['value'],ps['cbuffers']['items'][1]['value']], 'uv1_rows':[ps['cbuffers']['items'][3]['value'],ps['cbuffers']['items'][4]['value']], 'shared_dwords':got}
 fmt={1:('BC3','sRGB'),3:('BC5','linear'),4:('RGBA8','linear'),5:('RGBA8','linear'),6:('BC1','sRGB')}
 for mh,slots in binding.items():
  for ks,tag in slots.items():
   idx=int(ks);tr=manifest.get('textures',{}).get(tag)
   if not tr:viol.append(f'{mh}: missing texture manifest {tag}');continue
   if idx==0:
    if tr.get('native_colorspace_hint')!='sRGB' or tr.get('format_name') not in ('BC1','BC3'):viol.append(f'{mh}: t0 format/colorspace mismatch')
   elif idx in fmt:
    exp=fmt[idx]
    if (tr.get('format_name'),tr.get('native_colorspace_hint'))!=exp:viol.append(f'{mh}: t{idx} format mismatch {tag}')
 cube=manifest.get('textures',{}).get('80AB04CF') or {};hi=cube.get('header_info') or {}
 if (hi.get('width'),hi.get('height'),hi.get('array_size'))!=(16,16,6) or len(cube.get('faces') or [])!=6:viol.append('t4 cube resource topology mismatch')
 if viol:
  out={'schema_version':1,'status':'D1_XUR_PS_808768C0_DATAFLOW_SEMANTICS_PARTIAL','violations':viol};a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));return 2
 out={
 'schema_version':1,'status':'D1_XUR_PS_808768C0_DATAFLOW_SEMANTICS_EXACT','shader':SHADER,'native_shader':NATIVE_SHADER,'native_sha256':NATIVE_SHA,'gcn_sha256':GCN_SHA,
 'scope_materials':MEMBERS,'scope_material_count':5,'serialized_t2_bound_materials':WITH_T2,'serialized_t2_absent_materials':WITHOUT_T2,
 'exact_inputs':{'serialized_texture_bindings':binding,'consumed_material_b0':consumed,'api12_camera_dependency':{'dwords':[28,29,30],'meaning':'camera/view position','evidence':'same already-retail-closed D1 api12 contract used by Tower 809DCD66 and Xur 808764AA'},'t4_cube':{'tag':'80AB04CF','format':'RGBA8','colorspace':'linear','faces':6,'dimensions':[16,16]},'t5':{'tag':'808768AD','sampled_channel':'blue'},'t6':{'tag':'80876987','sampled_channel':'red'},'tfx_bytes_hex':TFX_HEX,'tfx_semantics_complete':False},
 'instruction_level_equations':{
  'uv_base':'uv = attr3.xy',
  'uv_transformed':'uvA = float2(b0[12]*uv.x + b0[13]*uv.y + b0[14], b0[16]*uv.x + b0[17]*uv.y + b0[18]); the current rows are the serialized c3/c4 vectors and differ by material',
  'combined_normal_xy_symbolic':'nx = b0[8]*t2.r + b0[9] + b0[21] + b0[20]*t3.r; ny = b0[8]*t2.g + b0[9] + b0[21] + b0[20]*t3.g',
  'combined_normal_xy_current_constants':'nx = 2*t2.r + 2*t3.r - 2; ny = 2*t2.g + 2*t3.g - 2',
  'normal_z':'nz = sqrt(saturate(1 - nx*nx - ny*ny))',
  'basis_transform':'Nraw = nx*attr1.xyz + ny*attr2.xyz + nz*attr0.xyz; N = normalize(Nraw)',
  'view_vector':'V = normalize(api12[28:30] - attr4.xyz)',
  'reflection_vector':'R = 2*dot(N,V)*N - V = reflect(-V,N)',
  'surface_samples':'C = t0.rgb * t1.rgb; A = 4.594789981842041 * t0.a * t1.a',
  'cube_lod':'Lfloor = b0[36] + saturate(b0[45]*A + b0[44])*(b0[36]-b0[40]); current Lfloor = 1 + saturate(2.3*A - 1.3); L = max(image_get_lod(t4,R).y,Lfloor)',
  'detail_uv':'uv6 = float2(b0[48]*uv.x+b0[50], b0[49]*uv.y+b0[51]); current uv6 = 8*uv',
  'fresnel_term':'F = exp2(b0[54] * log2(saturate(1-dot(N,V)))); current F = saturate(1-dot(N,V))^5',
  'cube_strength':'S = t4.a * (b0[56] + b0[57]*A) * (b0[52] + b0[53]*F); current S = t4.a * (2-A) * 0.4*F',
  'detail_scalar':'M = t5.b * t6.r',
  'mrt0_rgb':'mrt0.rgb = 4.594789981842041*C + (b0[61] + b0[60]*4.594789981842041*C) * t4.rgb * M * S',
  'mrt0_rgb_current_constants':'mrt0.rgb = 4.594789981842041*C + (0.39 + 0.91*4.594789981842041*C) * t4.rgb * (t5.b*t6.r) * t4.a * (2-A) * 0.4*F',
  'mrt0_alpha':'mrt0.a = attr0.w',
  'normal_packing_scale':'k = 0.375 + 0.125*A; mrt1.rgb = saturate(0.5 + k*N.xyz)',
  'mrt1_alpha':'mrt1.a = b0[81] = 0.051960788667201996',
 },
 'promoted_texture_semantics':{
  't2_and_t3':'both are instruction-proven normal XY contributors where t2 has a serialized binding; t3 is always the exact BC5 resource 80AB04C1',
  't0_and_t1':'their RGB product is the direct surface-color term and their alpha product drives reflection LOD/strength; high-level PBR naming remains withheld',
  't4':'six-face cube resource, sampled with reflected view vector and explicit LOD; RGB and alpha both affect MRT0',
  't5':'only sampled blue scalar is promoted','t6':'only sampled red scalar is promoted'},
 'runtime_default_texture_binding_frontier':{'texture_index':2,'affected_materials':WITHOUT_T2,'fact':'the native GCN unconditionally samples resource-table texture index 2 but these two retail materials serialize no texture_index 2 entry','not_promoted':'no neutral-normal/default texture identity is guessed; runtime descriptor completion must be source-closed separately'},
 'pixel_shader_dataflow_complete_for_scoped_binary':True,'serialized_texture_binding_complete_for_all_scoped_materials':False,'tfx_producer_semantics_complete':False,'render_state_semantics_complete':False,'portable_material_recreation_complete':False,'violations':[],
 'policy':'Exact GCN arithmetic is promoted for all five materials. The absent serialized t2 binding in two materials is preserved as a first-class runtime binding frontier, not filled by appearance or convention.'}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k] for k in ['status','scope_material_count','serialized_t2_bound_materials','serialized_t2_absent_materials','instruction_level_equations','runtime_default_texture_binding_frontier','violations']},indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
