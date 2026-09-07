#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from pathlib import Path

FAMILIES={
 '8087688C':{
  'native':'80876891','gcn':'63f5479f10e58f07dd891f29aef0a0bea640cb4890d80ea447c4422d51d51bf1','bytes':372,'inst':80,
  'members':['808762D7','808764CC','808767B0','808767B3'],'tfx':'4900472149014722','cb_count':1,'tex_count':2,
  'formats':[('mixed_srgb',None),('BC5','linear')],
  'anchors':['image_sample    v[4:5], v[2:5], s[20:27], s[0:3] dmask:3','image_sample    v[6:8], v[2:5], s[4:11], s[12:15] dmask:7','v_mad_f32       v3, v4, s16, v2','v_sqrt_f32      v4, v4','v_rsq_clamp_f32 v3, v3','v_mad_f32       v3, v4, s0, 0.5 clamp','exp             mrt1, v1, v1, v2, v2 compr','exp             mrt0, v1, v1, v0, v0 done compr vm'],
  'kind':'constant_pack',
 },
 '80AADCB3':{
  'native':'80AADCB4','gcn':'cf5f9064a00c0e099fa0981262ded869775ac82e58487c3ce75f3452fb8a15ab','bytes':420,'inst':88,
  'members':['80876545','80876547','80876548','80876863','80876864'],'tfx':'4900472149014722','cb_count':3,'tex_count':2,
  'formats':[('mixed_srgb',None),('BC5','linear')],
  'anchors':['image_sample    v[4:5], v[2:5], s[16:23], s[24:27] dmask:3','image_sample    v[6:9], v[2:5], s[4:11], s[12:15] dmask:15','v_mad_f32       v3, v4, s4, v2','v_sqrt_f32      v4, v4','v_rsq_clamp_f32 v3, v3','v_mac_f32       v3, s4, v9','s_buffer_load_dword s0, s[0:3], 0x9','exp             mrt1, v1, v1, v2, v2 compr','exp             mrt0, v1, v1, v0, v0 done compr vm'],
  'kind':'base_alpha_pack',
 },
 '80AAE1C7':{
  'native':'80AAE1C8','gcn':'6c9b8513d1a067fbf304b0fe0bc3f112a278718315c628d60b270925e085f24c','bytes':428,'inst':89,
  'members':['808764CF','808767B2','80876867'],'tfx':'490047214901472249024723','cb_count':3,'tex_count':3,
  'formats':[('BC1','sRGB'),('BC5','linear'),('BC4','linear')],
  'anchors':['image_sample    v[15:16], v[2:5], s[20:27], s[28:31] dmask:3','image_sample    v[17:19], v[2:5], s[4:11], s[12:15] dmask:7','image_sample    v2, v[2:5], s[32:39], s[40:43] dmask:8','v_mad_f32       v3, v15, s0, v4','v_sqrt_f32      v15, v15','v_rsq_clamp_f32 v3, v3','v_mac_f32       v14, s1, v2','s_buffer_load_dword s2, s[16:19], 0x9','exp             mrt1, v1, v1, v2, v2 compr','exp             mrt0, v1, v1, v0, v0 done compr vm'],
  'kind':'scalar_mask_pack',
 },
}
SAMPLER='80AAE177'; SAMPLER_SHA='2c670016bbb70b68bd2f69dd4a30145bf7d61a47c1bf4c3acba8321b46976ecb'

def flat(ps): return [float(v) for x in ps['cbuffers']['items'] for v in x['value']]

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--material-state',type=Path,required=True);ap.add_argument('--shader-census',type=Path,required=True);ap.add_argument('--image-usage',type=Path,required=True);ap.add_argument('--texture-manifest',type=Path,required=True);ap.add_argument('--disasm-dir',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
 state=json.loads(a.material_state.read_text()); census=json.loads(a.shader_census.read_text()); images=json.loads(a.image_usage.read_text()); manifest=json.loads(a.texture_manifest.read_text()); violations=[]
 if state.get('status')!='D1_MATERIAL_STAGE_STATE_EXACT':violations.append('material state checkpoint not exact')
 if census.get('status')!='D1_XUR_ALL_NATIVE_SHADER_DISASSEMBLY_EXACT':violations.append('shader census checkpoint not exact')
 if images.get('status')!='D1_GCN_IMAGE_RESOURCE_USAGE_EXACT':violations.append('image usage checkpoint not exact')
 if manifest.get('visible_material_count')!=54 or manifest.get('material_decode_errors') or manifest.get('texture_errors'):violations.append('texture manifest not exact/error-free 54-material checkpoint')
 cby={x['shader']:x for x in census['shaders']}; iby={x['shader']:x for x in images['shaders']}; results=[]
 for sh,f in FAMILIES.items():
  sr=cby.get(sh); ir=iby.get(sh); asm=(a.disasm_dir/f'PS_{sh}.s').read_text()
  if not sr:violations.append(f'{sh}: missing census');continue
  for k,v in [('native_shader',f['native']),('gcn_sha256',f['gcn']),('gcn_bytes',f['bytes']),('instruction_count_approx',f['inst'])]:
   if sr.get(k)!=v: violations.append(f'{sh}: {k} mismatch')
  if sr.get('stages')!=['ps']:violations.append(f'{sh}: not PS-only')
  if not ir:violations.append(f'{sh}: missing image usage');continue
  if ir.get('image_instruction_count')!=f['tex_count'] or ir.get('used_texture_indices')!=list(range(f['tex_count'])) or ir.get('unmatched_image_instruction_count')!=0:violations.append(f'{sh}: image usage mismatch')
  for needle in f['anchors']:
   if needle not in asm:violations.append(f'{sh}: missing anchor {needle}')
  got=sorted(m for m,r in state['materials'].items() if r['ps']['shader']==sh)
  if got!=sorted(f['members']):violations.append(f'{sh}: member set mismatch')
  per={}
  for mh in f['members']:
   ps=state['materials'][mh]['ps']; cb=flat(ps)
   if ps['tfx_bytecode']['bytes_hex']!=f['tfx'] or ps['tfx_disassembly']['complete'] is not True:violations.append(f'{mh}: TFX mismatch/incomplete')
   if ps['cbuffers']['count']!=f['cb_count']:violations.append(f'{mh}: CBuffer count mismatch')
   if ps['textures']['count']!=f['tex_count']:violations.append(f'{mh}: texture count mismatch')
   if [x['first_dword_hex'] for x in ps['samplers']['items']]!=[SAMPLER]*f['tex_count']:violations.append(f'{mh}: sampler tags mismatch')
   if [(x.get('native_sampler') or {}).get('payload_sha256') for x in ps['sampler_references']]!=[SAMPLER_SHA]*f['tex_count']:violations.append(f'{mh}: native sampler payload mismatch')
   tags=[x['texture'] for x in ps['textures']['items']]
   for i,tag in enumerate(tags):
    tr=manifest['textures'].get(tag)
    if not tr:violations.append(f'{mh}: missing texture {tag}');continue
    ef,ec=f['formats'][i]
    if ef=='mixed_srgb':
     if tr.get('format_name') not in ('BC1','BC3') or tr.get('native_colorspace_hint')!='sRGB':violations.append(f'{mh}: t{i} expected BC1/BC3 sRGB')
    elif (tr.get('format_name'),tr.get('native_colorspace_hint'))!=(ef,ec):violations.append(f'{mh}: t{i} format/colorspace mismatch')
   if len(cb)<2 or cb[0]!=2.0 or cb[1]!=-1.0:violations.append(f'{mh}: normal remap constants mismatch')
   if f['kind']=='constant_pack':
    vals={'k':0.375,'mrt1_alpha':0.0}
   elif f['kind']=='base_alpha_pack':
    if len(cb)<=9:violations.append(f'{mh}: missing b0[9]'); a9=None
    else:a9=cb[9]
    vals={'k':'0.375 + 0.125*t0.a','mrt1_alpha':a9}
   else:
    if len(cb)<=9:violations.append(f'{mh}: missing b0[9]'); a9=None
    else:a9=cb[9]
    vals={'k':'0.375 + 0.125*t2.native_w','mrt1_alpha':a9}
   per[mh]={'textures':tags,**vals}
  eq={'normal_xy':'nx=2*t1.r-1; ny=2*t1.g-1','normal_z':'nz=sqrt(saturate(1-nx*nx-ny*ny))','basis':'N=normalize(nx*attr1.xyz + ny*attr2.xyz + nz*attr0.xyz)','mrt0_rgb':'mrt0.rgb=t0.rgb','mrt0_alpha':'mrt0.a=attr0.w'}
  if f['kind']=='constant_pack':eq.update({'packing_scale':'k=0.375','mrt1':'mrt1.rgb=saturate(0.5+k*N); mrt1.a=0'})
  elif f['kind']=='base_alpha_pack':eq.update({'packing_scale':'k=0.375+0.125*t0.a','mrt1':'mrt1.rgb=saturate(0.5+k*N); mrt1.a=b0[9]'})
  else:eq.update({'packing_scale':'k=0.375+0.125*t2.native_w','mrt1':'mrt1.rgb=saturate(0.5+k*N); mrt1.a=b0[9]'})
  results.append({'shader':sh,'native_shader':f['native'],'gcn_sha256':f['gcn'],'materials':f['members'],'material_count':len(f['members']),'equations':eq,'per_material_parameters':per,'pixel_shader_dataflow_complete_for_scoped_binary':True})
 if violations:
  out={'schema_version':1,'status':'D1_XUR_DIRECT_RGB_NORMAL_PS_FAMILIES_PARTIAL','violations':violations}
 else:
  out={'schema_version':1,'status':'D1_XUR_DIRECT_RGB_NORMAL_PS_FAMILIES_EXACT','proofs':results,'family_count':len(results),'material_coverage_count':sum(x['material_count'] for x in results),'gcn_sha256':sorted(x['gcn_sha256'] for x in results),'promoted_semantics':{'t1':'instruction-proven signed XY normal source for all three families','t0':'instruction-proven direct MRT0 RGB source; high-level albedo/base-color naming withheld','80AADCB3_t0_alpha':'instruction-proven normal packing-scale modulator','80AAE1C7_t2_native_w':'instruction-proven normal packing-scale modulator from the native W-selected sample component'},'portable_material_recreation_complete':False,'render_state_semantics_complete':False,'violations':[]}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out if violations else {k:out[k] for k in ['status','family_count','material_coverage_count','gcn_sha256','promoted_semantics','violations']},indent=2));return 2 if violations else 0
if __name__=='__main__':raise SystemExit(main())
