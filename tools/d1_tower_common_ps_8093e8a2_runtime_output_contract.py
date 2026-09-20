#!/usr/bin/env python3
"""Fail-closed runtime-resource output contract for Tower common PS 8093E8A2.

The two authored Tower materials using this shader serialize no PS textures,
no PS samplers, and no PS TFX bytecode. Native GCN consumes runtime t10.x and
constant buffers API0/API9/API12. MRT0 RGB is literal zero; only alpha carries
the computed renderer/pass result.

No human pass name is inferred.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
SHADER='8093E8A2';NATIVE='8093E8B1'
NATIVE_SHA='155cf6b3a8d3b5966be04bb9b5aa1bdcd0909af16546f328f66a7a50e2b72413'
GCN_SHA='58d9e8bcc24e6aac65f5e92b079a0544d54291375e037792d83a818426b72168'
GCN_BYTES=372
MATERIALS={'8093E88E':'8093E8A3','80C98E7D':'80C991D7'}
EXPECTED_CBUFFERS={'0':[16,17,20,21,27,31],'9':[0,1],'12':[24,25,26,27,28,29,30,31,48,49,50,51]}
EXPECTED_TERMINAL='000000000168'

def norm(x):return str(x).upper().removeprefix('0X').zfill(8)
def main()->int:
 ap=argparse.ArgumentParser()
 for n in ('manifest','shader-report','image-usage','cbuffer-usage','terminal-mrt0','disasm','out'):ap.add_argument('--'+n,type=Path,required=True)
 a=ap.parse_args();v=[]
 m=json.loads(a.manifest.read_text());s=json.loads(a.shader_report.read_text());i=json.loads(a.image_usage.read_text());c=json.loads(a.cbuffer_usage.read_text());t=json.loads(a.terminal_mrt0.read_text());asm=a.disasm.read_text(errors='replace')
 if m.get('material_decode_errors') or m.get('texture_errors'):v.append('common manifest decode error')
 found={}
 for mh,r in (m.get('materials') or {}).items():
  if norm(r.get('pixel_shader',''))==SHADER:found[norm(mh)]=r
 if set(found)!=set(MATERIALS):v.append(f'material set drift {sorted(found)}')
 for mh,container in MATERIALS.items():
  r=found.get(mh)
  if not r:continue
  if r.get('ps_texture_count')!=0 or r.get('ps_texture_tags') or r.get('bindings'):v.append(f'{mh}: serialized PS texture unexpectedly present')
  if ((r.get('samplers') or {}).get('ps') or {}).get('count')!=0:v.append(f'{mh}: PS sampler unexpectedly present')
  if ((r.get('tfx') or {}).get('ps') or {}).get('count')!=0:v.append(f'{mh}: PS TFX bytecode unexpectedly present')
  if norm(((r.get('constants') or {}).get('ps_vector4_container'))) != container:v.append(f'{mh}: PS Vector4 container drift')
 sr=next((x for x in s.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
 if s.get('status')!='D1_WORLD_PIXEL_SHADER_GCN_EXACT' or not sr:v.append('shader report not exact/present')
 else:
  for k,z in {'visible_material_count':2,'native_shader':NATIVE,'native_sha256':NATIVE_SHA,'gcn_sha256':GCN_SHA,'gcn_bytes':GCN_BYTES}.items():
   if sr.get(k)!=z:v.append(f'{k} drift {sr.get(k)!r} != {z!r}')
  slots=[(x.get('usage_name'),int(x.get('api_slot',-1)),int(x.get('start_register',-1))) for x in sr.get('usage',{}).get('slots',[])]
  exp=[('PtrExtendedUserData',1,2),('ImmResource',10,4),('ImmConstBuffer',0,12),('ImmConstBuffer',9,16),('ImmConstBuffer',12,20)]
  if slots!=exp:v.append(f'user-data slot contract drift {slots!r}')
 ir=next((x for x in i.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
 if i.get('status')!='D1_GCN_IMAGE_RESOURCE_USAGE_EXACT' or not ir:v.append('image usage not exact/present')
 else:
  got=[(x['address'],x['opcode'],[q['texture_index'] for q in x.get('resources',[])],x['dmask_channels']) for x in ir.get('instructions',[])]
  if got!=[('000000000040','image_load_mip',[10],'x')]:v.append(f'runtime image contract drift {got!r}')
  if ir.get('unmatched_image_instruction_count')!=0:v.append('runtime image provenance unresolved')
 cr=next((x for x in c.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
 if c.get('status')!='D1_GCN_CBUFFER_USAGE_EXACT' or not cr:v.append('cbuffer usage not exact/present')
 else:
  if cr.get('unresolved_load_count')!=0:v.append('unresolved cbuffer load')
  if cr.get('api_slot_read_dwords')!=EXPECTED_CBUFFERS:v.append(f'cbuffer read contract drift {cr.get("api_slot_read_dwords")!r}')
 tr=next((x for x in t.get('shaders',[]) if norm(x.get('shader'))==SHADER),None)
 if t.get('status')!='D1_GCN_TERMINAL_MRT0_DEPENDENCY_CENSUS_EXACT' or not tr:v.append('terminal MRT0 slice not exact/present')
 else:
  if tr.get('terminal_mrt0_export_address')!=EXPECTED_TERMINAL or not tr.get('terminal_mrt0_compressed'):v.append('terminal export identity drift')
  if tr.get('terminal_mrt0_operands')!=['v2','v2','v0','v0']:v.append('terminal operand drift')
  for ch in 'RGB':
   q=tr['channels'][ch]['value_slice']
   if q.get('literals')!=['0'] or q.get('cbuffer_dwords') or q.get('texture_sample_channels') or q.get('interpolants') or q.get('unknown_registers'):v.append(f'{ch}: not exact literal-zero output')
  aq=tr['channels']['A']['value_slice']
  if aq.get('unknown_registers'):v.append(f'alpha has unknown register leaves {aq.get("unknown_registers")}')
  if aq.get('cbuffer_dwords')!={'0':[16,17,20,21,27,31],'9':[0,1],'12':[24,25,26,28,29,30]}:v.append(f'alpha cbuffer leaves drift {aq.get("cbuffer_dwords")}')
  if aq.get('texture_sample_channels')!=[{'texture_index':10,'channel':'x','sample_address':'000000000040'}]:v.append(f'alpha runtime texture leaf drift {aq.get("texture_sample_channels")}')
  if aq.get('interpolants')!=['attr0.x','attr0.y','attr0.z','attr1.x','attr1.y','attr1.z']:v.append(f'alpha interpolant leaves drift {aq.get("interpolants")}')
 for needle in [
  '/*000000000040: f0041100 00010202*/ image_load_mip  v2, v[2:5], s[4:11] unorm',
  '/*00000000015c: 7e000280         */ v_mov_b32       v0, 0',
  '/*000000000160: 5e040100         */ v_cvt_pkrtz_f16_f32 v2, v0, v0',
  '/*000000000164: 5e000300         */ v_cvt_pkrtz_f16_f32 v0, v0, v1',
  '/*000000000168: f8001c0f 00000002*/ exp             mrt0, v2, v2, v0, v0 done compr vm',
 ]:
  if needle not in asm:v.append('missing exact native anchor: '+needle)
 out={
  'schema':'d1_tower_common_ps_8093e8a2_runtime_output_contract/v1',
  'status':'D1_TOWER_COMMON_PS_8093E8A2_RUNTIME_OUTPUT_CONTRACT_EXACT' if not v else 'D1_TOWER_COMMON_PS_8093E8A2_RUNTIME_OUTPUT_CONTRACT_PARTIAL',
  'shader':SHADER,'native_shader':NATIVE,'gcn_sha256':GCN_SHA,'materials':sorted(MATERIALS),
  'authored_material_ps_texture_role_status':'NOT_APPLICABLE_NO_SERIALIZED_PS_TEXTURES',
  'runtime_resource_contract':{'t10':'one exact image_load_mip x-channel read at 0x40','human_semantics':'WITHHELD'},
  'mrt0_contract':{'rgb':'(0,0,0) exact literals','alpha':'computed from runtime t10.x + API0/API9/API12 + attr0.xyz + attr1.xyz'},
  'semantic_boundary':{'pass_identity':'WITHHELD','runtime_t10_human_semantics':'WITHHELD','api_constant_human_semantics':'WITHHELD','portable_render_pass_mapping':'WITHHELD'},
  'violations':v,
  'policy':'This closes authored-vs-runtime resource ownership and native MRT0 channel behavior only. It does not name the render pass or the runtime resource.',
 }
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));return 0 if not v else 2
if __name__=='__main__':raise SystemExit(main())
