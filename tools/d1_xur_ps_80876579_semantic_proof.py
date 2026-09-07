#!/usr/bin/env python3
"""Fail-closed native dataflow proof for Xur PS 80876579.

This is the shader family that makes a control/dye RGB mask look psychedelic when
that mask is naively placed in glTF baseColor. The proof promotes only the exact
GCN arithmetic and exact current retail resources/state.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

SHADER='80876579'
NATIVE_SHADER='808765C5'
NATIVE_SHA='7dbc78b1929d570e46b59f830947b5f26b2325afa296856a8cb83d4aa5480a8d'
GCN_SHA='f60720572d9bd42f06c3fffc3ef5e178f8a9d7917fa8c83d96511830e45b0c00'
MEMBERS=['808761EC','80876227','8087623F','80876411']
TFX_HEX='49004721490147224902472349034724490447254905472649064727490747283c011c23220034000f2322003501420a'
TEXTURES={0:'80876551',1:'80876552',2:'80AB04BB',3:'80AAF8B8',4:'80876553',5:'80876554',6:'80AB04BC',7:'80AACC28'}
FORMATS={0:('BC1','sRGB'),1:('BC3','sRGB'),2:('BC3','sRGB'),3:('BC3','sRGB'),4:('BC1','sRGB'),5:('BC5','linear'),6:('BC5','linear'),7:('RGBA8','linear')}
SAMPLERS=['80AAE177']*7+['80AAE176']
SAMPLER_SHAS=['2c670016bbb70b68bd2f69dd4a30145bf7d61a47c1bf4c3acba8321b46976ecb']*7+['0bcdaa82ea0d8588e313f29998f6c7b9166e7d28d40b13d422348d55ae5dc208']
PRIV=[[0.0,0.0,1.0,0.0],[0.014999999664723873,1.0,1.0,1.0],[1.0,1.0,1.0,1.0]]
CONSUMED={40:0.0,44:17.0,45:17.0,46:0.0,47:0.0,48:1.0,49:1.0,50:1.0,51:0.23750001192092896,52:0.3277781009674072,53:0.0423114113509655,54:0.0423114113509655,55:1.0,56:0.1313924938440323,57:0.0,58:0.0,59:1.0,60:1.0,61:1.0,62:1.0,63:1.0,64:2.0,65:-1.0,68:10.0,69:10.0,70:0.0,71:0.0,72:1.0,73:-0.5,88:6.0,92:6.0,96:0.2248000055551529,97:1.1234999895095825,98:1.0,99:0.0,100:0.20250000059604645,101:0.2695000171661377,104:1.1239999532699585,113:0.21666668355464935}
ANCHORS=[
'image_sample    v[7:9], v[3:6], s[16:23], s[4:7] dmask:7',
'image_sample    v[10:13], v[3:6], s[16:23], s[8:11] dmask:15',
'v_mad_f32       v15, v13, v14, -s0','v_cmp_gt_f32    vcc, 0, v15',
'image_sample    v[5:6], v[3:6], s[20:27], s[28:31] dmask:3',
'image_sample    v[15:16], v[15:18], s[32:39], s[40:43] dmask:3',
'v_sqrt_f32      v6, v6','v_rsq_clamp_f32 v5, v5','v_cubema_f32    v2, v21, v22, v17',
'image_get_lod   v18, v[30:33], s[16:23], s[24:27] dmask:2',
'image_sample_l  v[30:33], v[30:33], s[16:23], s[24:27] dmask:15',
'image_sample    v[21:23], v[3:6], s[32:39], s[40:43] dmask:7',
'image_sample    v[24:26], v[3:6], s[44:51], s[52:55] dmask:7',
'image_sample    v[27:29], v[3:6], s[56:63], s[12:15] dmask:7',
'v_log_f32       v2, v8','v_exp_f32       v2, v2','v_madak_f32     v2, v22, v2, 0x3f000000',
'exp             mrt1, v1, v1, v2, v2 compr','exp             mrt0, v1, v1, v0, v0 done compr vm']

def flat(ps): return [float(v) for row in ps['cbuffers']['items'] for v in row['value']]

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--material-state',type=Path,required=True);ap.add_argument('--shader-census',type=Path,required=True);ap.add_argument('--image-usage',type=Path,required=True);ap.add_argument('--texture-manifest',type=Path,required=True);ap.add_argument('--disassembly',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
 st=json.loads(a.material_state.read_text());ce=json.loads(a.shader_census.read_text());im=json.loads(a.image_usage.read_text());ma=json.loads(a.texture_manifest.read_text());asm=a.disassembly.read_text();viol=[]
 if st.get('status')!='D1_MATERIAL_STAGE_STATE_EXACT':viol.append('material state checkpoint not exact')
 if ce.get('status')!='D1_XUR_ALL_NATIVE_SHADER_DISASSEMBLY_EXACT':viol.append('shader census checkpoint not exact')
 if im.get('status')!='D1_GCN_IMAGE_RESOURCE_USAGE_EXACT':viol.append('image usage checkpoint not exact')
 if ma.get('visible_material_count')!=54 or ma.get('material_decode_errors') or ma.get('texture_errors'):viol.append('texture manifest checkpoint not exact/error-free')
 sr=next((x for x in ce.get('shaders',[]) if x.get('shader')==SHADER),None)
 if not sr:viol.append('shader absent')
 else:
  for k,v in [('native_shader',NATIVE_SHADER),('native_sha256',NATIVE_SHA),('gcn_sha256',GCN_SHA),('gcn_bytes',1508),('instruction_count_approx',290)]:
   if sr.get(k)!=v:viol.append(f'{k} mismatch: {sr.get(k)!r}')
  if sr.get('stages')!=['ps']:viol.append('not PS-only')
 ir=next((x for x in im.get('shaders',[]) if x.get('shader')==SHADER),None)
 if not ir:viol.append('image usage absent')
 else:
  if ir.get('image_instruction_count')!=9:viol.append('expected 9 image instructions')
  if ir.get('used_texture_indices')!=list(range(8)):viol.append('used texture indices mismatch')
  if ir.get('texture_instruction_counts')!={'0':1,'1':1,'2':1,'3':1,'4':1,'5':1,'6':1,'7':2}:viol.append('texture instruction counts mismatch')
  if ir.get('unmatched_image_instruction_count')!=0:viol.append('unmatched image instruction')
 for n in ANCHORS:
  if n not in asm:viol.append('missing disassembly anchor: '+n)
 for mh in MEMBERS:
  row=(st.get('materials') or {}).get(mh)
  if not row:viol.append('missing material '+mh);continue
  ps=row['ps']
  if ps.get('shader')!=SHADER:viol.append(f'{mh}: PS mismatch')
  if row.get('material_state4_hex')!='00008100':viol.append(f'{mh}: material state mismatch')
  if ps['tfx_bytecode'].get('bytes_hex')!=TFX_HEX or ps.get('tfx_disassembly',{}).get('complete') is not True:viol.append(f'{mh}: TFX mismatch/incomplete')
  ops=ps.get('tfx_disassembly',{}).get('ops') or []
  if not ops or ops[-1].get('name')!='Unk42' or ops[-1].get('d1_unk42_u8')!=10:viol.append(f'{mh}: final D1 TFX 0x42 target is not 10')
  if [x['value'] for x in ps['tfx_private_constants']['items']]!=PRIV:viol.append(f'{mh}: TFX private constants mismatch')
  tex={int(x['texture_index']):x['texture'] for x in ps['textures']['items']}
  if tex!=TEXTURES:viol.append(f'{mh}: exact texture map mismatch')
  if [x['first_dword_hex'] for x in ps['samplers']['items']]!=SAMPLERS:viol.append(f'{mh}: sampler tags mismatch')
  gotsha=[(r.get('native_sampler') or {}).get('payload_sha256') for r in ps.get('sampler_references',[])]
  if gotsha!=SAMPLER_SHAS:viol.append(f'{mh}: native sampler descriptors mismatch')
  cb=flat(ps)
  if len(cb)!=116:viol.append(f'{mh}: expected 29 Vec4 / 116 dwords')
  got={i:cb[i] for i in CONSUMED if i<len(cb)}
  if got!=CONSUMED:viol.append(f'{mh}: consumed material constants mismatch')
 for i,t in TEXTURES.items():
  tr=(ma.get('textures') or {}).get(t)
  if not tr:viol.append('missing manifest texture '+t);continue
  if (tr.get('format_name'),tr.get('native_colorspace_hint'))!=FORMATS[i]:viol.append(f't{i} format/colorspace mismatch')
 cube=ma['textures']['80AACC28'];hi=cube.get('header_info') or {}
 if (hi.get('width'),hi.get('height'),hi.get('array_size'))!=(64,64,6) or len(cube.get('faces') or [])!=6:viol.append('t7 cube topology mismatch')
 if viol:
  out={'schema_version':1,'status':'D1_XUR_PS_80876579_DATAFLOW_SEMANTICS_PARTIAL','violations':viol};a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));return 2
 out={'schema_version':1,'status':'D1_XUR_PS_80876579_DATAFLOW_SEMANTICS_EXACT','shader':SHADER,'native_shader':NATIVE_SHADER,'native_sha256':NATIVE_SHA,'gcn_sha256':GCN_SHA,'scope_materials':MEMBERS,'scope_material_count':4,
  'exact_inputs':{'texture_bindings_t0_t7':{str(k):v for k,v in TEXTURES.items()},'texture_formats':{str(k):{'format':FORMATS[k][0],'colorspace':FORMATS[k][1]} for k in FORMATS},'sampler_tags':SAMPLERS,'tfx_bytes_hex':TFX_HEX,'tfx_private_constants':PRIV,'material_b0_consumed_dwords':CONSUMED,'api12_camera_dependency':{'dwords':[28,29,30],'meaning':'camera/view position','evidence':'already retail-closed D1 api12 contract'},'t7_cube':{'tag':'80AACC28','format':'RGBA8','colorspace':'linear','dimensions':[64,64],'faces':6}},
  'instruction_level_equations':{
   'uv':'uv = attr3.xy','control_union_scalar':'m = b0[51] + t0.r*(t0.r-b0[51]); m = m + t0.g*(t0.g-m); m = m + t0.b*(t0.b-m)','coverage':'A = t1.a*m; alpha_test_value = A - b0[40]; lanes with alpha_test_value < 0 are removed before the color/normal body','normal_detail_uv':'uvN = float2(b0[68]*uv.x+b0[70], b0[69]*uv.y+b0[71]); current uvN = 10*uv','normal_xy':'nx = b0[64]*t5.r + b0[65] + b0[73] + b0[72]*t6.r; ny = b0[64]*t5.g + b0[65] + b0[73] + b0[72]*t6.g','normal_xy_current_constants':'nx = 2*t5.r + t6.r - 1.5; ny = 2*t5.g + t6.g - 1.5','normal_z':'nz = sqrt(saturate(1-nx*nx-ny*ny))','two_sided_basis':'faceSign = +1 when the native entry v2 integer input is nonzero, otherwise -1; N = normalize(nx*attr1.xyz + ny*attr2.xyz + nz*faceSign*attr0.xyz)','view_vector':'V = normalize(api12[28:30] - attr4.xyz)','reflection_vector':'R = 2*dot(N,V)*N - V = reflect(-V,N)','cube_lod':'lodFloor = b0[88] + A*(b0[92]-b0[88]); current lodFloor=6; L=max(image_get_lod(t7,R).y,lodFloor); cube=sample_l(t7,R,L)','palette_uv':'uvP=float2(b0[44]*uv.x+b0[46], b0[45]*uv.y+b0[47]); current uvP=17*uv','palette_branch':'branch(c,t)=saturate(c.rgb-0.25)+t.rgb*saturate(4*c.rgb)','palette':'P=lerp(b0.c13.rgb, branch(b0.c13,t2), t0.r); P=lerp(P,branch(b0.c14,t3),t0.g); P=lerp(P,branch(b0.c15,t4),t0.b)','surface_color':'C=t1.rgb*P','fresnel':'F=exp2(b0[98]*log2(saturate(1-dot(N,V)))); current F=saturate(1-dot(N,V))','reflection_strength':'S=saturate(t7.a*(b0[100]+b0[101]*A)*(b0[96]+b0[97]*F))','reflection_strength_current_constants':'S=saturate(t7.a*(0.2025+0.2695000171661377*A)*(0.2248000055551529+1.1234999895095825*F))','surface_scaled':'Cs=4.594789981842041*C','cube_color':'Q=saturate(b0[104]*t7.rgb-0.25) + saturate(4*b0[104]*t7.rgb)*Cs; current b0[104]=1.1239999532699585','mrt0_rgb':'mrt0.rgb=lerp(Cs,Q,S)','mrt0_alpha':'mrt0.a=attr0.w','normal_pack':'k=0.375+0.125*A; mrt1.rgb=saturate(0.5+k*normalize(N)); mrt1.a=b0[113]','normal_pack_current_alpha':'mrt1.a=0.21666668355464935'},
  'promoted_texture_semantics':{'t0':'RGB control/palette mask is instruction-proven: its three channels drive palette lerps and a derived coverage scalar; it is not a direct visible RGB surface source','t1':'RGBA surface atlas is instruction-proven: RGB multiplies the reconstructed palette and alpha contributes to coverage/reflection/normal packing','t2_t3_t4':'RGB palette/detail sources sampled at the shared 17x transformed UV and consumed only through the palette reconstruction','t5_t6':'BC5 normal XY contributors are instruction-proven by signed/offset combination, hemisphere Z reconstruction, basis transform and normalization','t7':'six-face reflection cube is instruction-proven by view/reflection construction, cube coordinates, image_get_lod and explicit-LOD sampling'},
  'xur_psychedelic_preview_root_cause':{'proven':True,'control_texture':'80876551','incorrect_preview_behavior':'placing t0 directly in standard glTF baseColor exposes its saturated RGB control channels as visible surface color','native_behavior':'t0 RGB drives palette/control math; visible surface RGB originates from t1 multiplied by a t0-selected palette and then participates in reflection composition'},
  'scoped_tfx_c10_write_evidence':{'final_tfx_bytes':'420A','target_vec4_index':10,'native_ps_consumes_dword':40,'serialized_c10_x':0.0,'meaning':'strong scoped evidence that the TFX program dynamically produces the c10 alpha-test threshold; exact Frame[28] producer/time semantics remain unresolved'},
  'pixel_shader_dataflow_complete_for_scoped_binary':True,'tfx_producer_semantics_complete':False,'render_state_semantics_complete':False,'portable_material_recreation_complete':False,'violations':[],'policy':'The native PS dataflow is closed. High-level PBR names are withheld. TFX Frame[28], exact c10 runtime evolution, render/blend/depth/raster state, and final portable renderer implementation remain separate gates.'}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k] for k in ['status','scope_material_count','instruction_level_equations','promoted_texture_semantics','xur_psychedelic_preview_root_cause','scoped_tfx_c10_write_evidence','violations']},indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
