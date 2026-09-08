#!/usr/bin/env python3
"""Fail-closed current-state semantics for simple three-NPC PS tail families.

Covers:
  * 80AAE185: no textures; MRT0 RGB is exact material b0[0:2].
  * 808768AF: one exact RGB texture; MRT0 RGB is the sampled t0 RGB.

No deferred-lighting or generic PBR equivalence is claimed.
"""
from __future__ import annotations
import argparse,json,math
from pathlib import Path

FAMILIES={
 '80AAE185':{
   'native':'80AAE186','native_sha':'c9fcf8f7f58e5875a15a395cfe2e9a590e93091d82aa138e7b87634a591e1bc5',
   'gcn_sha':'9a20082363bc3403eebb33d8a20624211392104e29787fac51c1d558a8419c18','gcn_bytes':196,
   'materials':['80876546','809DE906'],'primitive_count':8,
   'usage':[('ImmConstBuffer',0,4)],'image':[],
   'material_cb':{
      '80876546':[0.0,0.0,0.0,1.0],
      '809DE906':[0.05087608844041824,0.05087608844041824,0.05087608844041824,1.0],
   },
 },
 '808768AF':{
   'native':'808768B3','native_sha':'501888dc8c848abd0cc4b87d974605c6ede714d92454d1a9dc40f42163cdaf10',
   'gcn_sha':'ae7453e071d8b17f01fca90684809f2e889f010fc945f6a96773cfcae00ab0fd','gcn_bytes':268,
   'materials':['808768BA'],'primitive_count':8,
   'usage':[('PtrExtendedUserData',1,2),('ImmResource',0,4),('ImmSampler',1,12),('ImmConstBuffer',0,16)],
   'image':[('image_sample',0,1,7)],
   'texture':'80AB04CB','tfx_hex':'49004721','tfx_sha':'0d3273c455043be5c75716dd23a520f925d07f26c210f16cbf454f1d5fc6af7b',
   'cb_raw':['00000000000000000000000000000000','00000000000000000000000000000000','00000000000000000000000000000000','00000000000000000000000000000000','0000803fb3b2b23d0000b0410000b041'],
   'sampler':'80AAE177','sampler_sha':'2c670016bbb70b68bd2f69dd4a30145bf7d61a47c1bf4c3acba8321b46976ecb',
 },
}
ANCHORS={
 '80AAE185':[
   's_buffer_load_dwordx4 s[0:3], s[4:7], 0x0',
   'v_rsq_clamp_f32 v5, v5',
   'v_mad_f32       v2, v2, s3, 0.5 clamp',
   'v_mov_b32       v1, s0','v_mov_b32       v6, s1','v_mov_b32       v7, s2',
   'exp             mrt1, v2, v2, v3, v3 compr','exp             mrt0, v1, v1, v0, v0 done compr vm',
 ],
 '808768AF':[
   'image_sample    v[2:4], v[2:5], s[4:11], s[12:15] dmask:7',
   's_buffer_load_dwordx2 s[0:1], s[0:3], 0x10',
   'v_mac_f32       v8, s0, v9','v_madak_f32     v5, v8, v5, 0x3f000000',
   'exp             mrt1, v1, v1, v5, v5 compr','exp             mrt0, v1, v1, v0, v0 done compr vm',
 ],
}

def close(a,b,eps=2e-7): return math.isclose(float(a),float(b),rel_tol=0.0,abs_tol=eps)
def flat_cb(m): return [float(v) for row in m['ps']['cbuffers']['items'] for v in row['value']]

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--extract-report',type=Path,required=True);ap.add_argument('--image-usage',type=Path,required=True);ap.add_argument('--material-state',type=Path,required=True);ap.add_argument('--disasm-dir',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
 ext=json.loads(a.extract_report.read_text());iu=json.loads(a.image_usage.read_text());st=json.loads(a.material_state.read_text());viol=[]
 if ext.get('status')!='D1_WORLD_PIXEL_SHADER_GCN_EXACT':viol.append('extract checkpoint not exact')
 if iu.get('status')!='D1_GCN_IMAGE_RESOURCE_USAGE_EXACT':viol.append('image usage checkpoint not exact')
 if st.get('status')!='D1_MATERIAL_STAGE_STATE_EXACT' or st.get('violations'):viol.append('material state checkpoint not exact')
 rows={}
 for sh,f in FAMILIES.items():
  er=next((x for x in ext.get('shaders',[]) if x.get('shader')==sh),None); ir=next((x for x in iu.get('shaders',[]) if x.get('shader')==sh),None); asm=(a.disasm_dir/f'PS_{sh}.s').read_text()
  if not er:viol.append(f'{sh}: shader extraction row absent');continue
  for k,v in [('native_shader',f['native']),('native_sha256',f['native_sha']),('gcn_sha256',f['gcn_sha']),('gcn_bytes',f['gcn_bytes'])]:
   if er.get(k)!=v:viol.append(f'{sh}: {k} mismatch {er.get(k)!r}')
  slots=[(x.get('usage_name'),x.get('api_slot'),x.get('start_register')) for x in er.get('usage',{}).get('slots',[])]
  if slots!=f['usage']:viol.append(f'{sh}: usage mismatch {slots!r}')
  got=[]
  if ir:
   for x in ir.get('instructions',[]):
    rr=x.get('resources') or [];ss=x.get('samplers') or []
    got.append((x.get('opcode'),rr[0].get('texture_index') if len(rr)==1 else None,ss[0].get('sampler_index') if len(ss)==1 else None,x.get('dmask')))
   if ir.get('unmatched_image_instruction_count')!=0:viol.append(f'{sh}: unmatched image instruction')
  if got!=f['image']:viol.append(f'{sh}: image sequence mismatch {got!r}')
  for needle in ANCHORS[sh]:
   if needle not in asm:viol.append(f'{sh}: missing native anchor {needle}')
  sm=sorted((st.get('shader_materials',{}).get('ps',{}) or {}).get(sh,[]))
  if sm!=sorted(f['materials']):viol.append(f'{sh}: material set mismatch {sm!r}')
  if sh=='80AAE185':
   for mh,expected in f['material_cb'].items():
    m=st['materials'].get(mh)
    if not m:viol.append(f'{sh}: missing {mh}');continue
    ps=m['ps'];vals=flat_cb(m)
    if m.get('material_state4_hex')!='00000000':viol.append(f'{mh}: state mismatch')
    if ps.get('shader')!=sh or ps['tfx_bytecode'].get('bytes_hex')!='' or ps.get('tfx_disassembly',{}).get('complete') is not True:viol.append(f'{mh}: shader/empty TFX mismatch')
    if ps['textures']['items'] or ps['samplers']['items'] or ps['tfx_private_constants']['items']:viol.append(f'{mh}: expected texture/sampler/private-constant empty')
    if len(vals)!=4 or any(not close(x,y) for x,y in zip(vals,expected)):viol.append(f'{mh}: b0 mismatch {vals!r}')
   rows[sh]={'shader':sh,'visible_primitive_count':8,'scope_materials':f['materials'],'mrt0_rgb':'b0[0:2] per material','mrt0_alpha':'attr0.w','mrt1':'N=normalize(attr0.xyz); rgb=saturate(0.5+0.375*N); alpha=0','portable_color_kind':'CONSTANT_RGB_EXACT','material_rgb':{mh:v[:3] for mh,v in f['material_cb'].items()}}
  else:
   mh=f['materials'][0];m=st['materials'].get(mh)
   if not m:viol.append(f'{sh}: missing {mh}')
   else:
    ps=m['ps'];vals=flat_cb(m);tex={int(x['texture_index']):x['texture'].upper() for x in ps['textures']['items']}
    if m.get('material_state4_hex')!='00000000':viol.append(f'{mh}: state mismatch')
    if ps.get('shader')!=sh or ps.get('tfx_program_sha256')!=f['tfx_sha'] or ps['tfx_bytecode'].get('bytes_hex')!=f['tfx_hex'] or not ps.get('tfx_disassembly',{}).get('complete'):viol.append(f'{mh}: shader/TFX mismatch')
    if ps['tfx_private_constants']['items']:viol.append(f'{mh}: expected no TFX private constants')
    if [x['raw_hex'] for x in ps['cbuffers']['items']]!=f['cb_raw']:viol.append(f'{mh}: full b0 payload mismatch')
    if tex!={0:f['texture']}:viol.append(f'{mh}: texture map mismatch {tex!r}')
    if [x['first_dword_hex'] for x in ps['samplers']['items']]!=[f['sampler']]:viol.append(f'{mh}: sampler tag mismatch')
    shas=[(r.get('native_sampler') or {}).get('payload_sha256') for r in ps.get('sampler_references',[])]
    if shas!=[f['sampler_sha']]:viol.append(f'{mh}: native sampler mismatch')
    if len(vals)!=20 or not close(vals[16],1.0) or not close(vals[17],0.08725490421056747):viol.append(f'{mh}: b0[16:17] mismatch')
   rows[sh]={'shader':sh,'visible_primitive_count':8,'scope_materials':f['materials'],'texture_t0':f['texture'],'mrt0_rgb':'sample(t0,attr1.xy).rgb','mrt0_alpha':'attr0.w','mrt1':'N=normalize(attr0.xyz); k=0.375+0.125*b0[16]=0.5; rgb=saturate(0.5+k*N); alpha=b0[17]=0.08725490421056747','portable_color_kind':'DIRECT_TEXTURE_RGB_EXACT'}
 if viol:
  out={'schema_version':1,'status':'D1_TOWER_THREE_NPC_SIMPLE_TAIL_SEMANTICS_PARTIAL','violations':viol};a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));return 2
 out={'schema_version':1,'status':'D1_TOWER_THREE_NPC_SIMPLE_TAIL_SEMANTICS_EXACT','violations':[],'program_count':2,'visible_primitive_count':16,'families':rows,'gates':{'current_material_native_color_dataflow_closed':True,'portable_color_source_closed':True,'portable_blender_recreation_complete':False},'critical_correction':'80AAE185 needs no color texture at all; 808768AF is an instruction-proven direct RGB texture family. These are exact exceptions to any one-size-fits-all texture-role heuristic.','policy':'Exact native/current-state color source only; no deferred-lighting equivalence claim.'}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k] for k in ('status','visible_primitive_count','critical_correction','gates')},indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
