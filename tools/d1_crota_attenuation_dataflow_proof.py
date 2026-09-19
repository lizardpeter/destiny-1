#!/usr/bin/env python3
"""Fail-closed Crota attenuation dataflow proof from frozen retail evidence."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from PIL import Image

PAIRS={
 'proc_a':('8108E7A9','8108E955','8108E7AB','8108E958'),
 'proc_b':('8108E7B2','8108E955','8108E7B4','8108E958'),
 'atlas_a':('8108E7AA','8108E956','8108E7AC','8108E959'),
 'atlas_b':('8108E7B3','8108E956','8108E7B5','8108E959'),
 'detail':('8108E7B1','8108E953','809DD1DC','80AAE1CD'),
}
TEX={'8108E7B6':'BC4','80AACF2A':'BC1','80AAD0E1':'BC5','8108E951':'BC1','8108E952':'BC1'}
A958=['image_sample    v[4:5]','dmask:3','image_sample    v4,','image_sample    v5,','image_sample    v6,','image_sample    v2,','exp             mrt0']
A959=['image_sample    v2, v[2:5]','dmask:8','v_mul_f32       v0, v3, v3','v_mad_f32       v1, v0, s4, v1 clamp','v_mul_f32       v0, v1, v1 clamp','v_mac_f32       v1, s0, v0','v_mul_f32       v0, v2, v1','exp             mrt0']
ACONST=['v_mov_b32       v0, 0','v_mov_b32       v1, 1.0','exp             mrt0']

def norm(x):return str(x).upper().removeprefix('0X').zfill(8)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def png_stats(root,h):
 hits=sorted(root.glob(f'{h}_*.png'))
 if len(hits)!=1:raise ValueError(f'{h}: expected one PNG, got {[x.name for x in hits]}')
 p=hits[0];im=Image.open(p).convert('RGBA');ex=[list(x) for x in im.getextrema()]
 return {'file':p.name,'sha256':sha(p),'size':list(im.size),'format':TEX[h],
         'rgba_extrema':ex,'alpha_constant':ex[3][0] if ex[3][0]==ex[3][1] else None,
         'varying_channels':[c for c,(lo,hi) in zip('rgba',ex) if lo!=hi]}

def ps(r):
 p=r['dependencies']['pixel']
 return {'shader':norm(p['shader']['tag_hash']),
         'textures':[norm(x['texture']) for x in p.get('textures',[])],
         'samplers':[str(x['raw_hex']).lower() for x in (p.get('samplers') or {}).get('items',[])],
         'tfx':str((p.get('tfx_bytecode') or {}).get('bytes_hex') or '').lower(),
         'vec4':norm((p.get('vector4_container') or {}).get('tag_hash','FFFFFFFF'))}

def usage(by,h):
 r=by[norm(h)]
 if int(r.get('unmatched_image_instruction_count',-1))!=0:raise ValueError(f'{h}: unresolved image provenance')
 ins=[]
 for x in r.get('instructions',[]):
  ts=sorted({int(y['texture_index']) for y in x.get('resources',[]) if y.get('texture_index') is not None})
  ss=sorted({int(y['sampler_index']) for y in x.get('samplers',[]) if y.get('sampler_index') is not None})
  ins.append({'address':x.get('address'),'texture_indices':ts,'sampler_indices':ss,
              'dmask_channels':x.get('dmask_channels'),'assembly':x.get('assembly')})
 return {'used_texture_indices':[int(x) for x in r.get('used_texture_indices',[])],
         'image_instruction_count':int(r.get('image_instruction_count',0)),'instructions':ins}

def anchors(text,want,label,v):
 for x in want:
  if x not in text:v.append(f'{label}: missing native anchor {x!r}')

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--material-dependencies',type=Path,required=True)
 ap.add_argument('--image-usage',type=Path,required=True)
 ap.add_argument('--disasm-dir',type=Path,required=True)
 ap.add_argument('--texture-dir',type=Path,required=True)
 ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
 md=json.loads(a.material_dependencies.read_text());iu=json.loads(a.image_usage.read_text());v=[]
 if md.get('status')!='D1_REMOTE_ACTIVITY_MATERIAL_DEPENDENCY_CLOSURE_COMPLETE' or md.get('violations'):v.append('material dependency input not exact')
 if iu.get('status')!='D1_GCN_IMAGE_RESOURCE_USAGE_EXACT' or int(iu.get('unmatched_image_instruction_count',-1))!=0:v.append('image usage input not exact')
 bm={norm(x['material']):x for x in md.get('rows',[])};bs={norm(x['shader']):x for x in iu.get('shaders',[])}
 tx={}
 for h in TEX:
  try:
   tx[h]=png_stats(a.texture_dir,h)
   if tx[h]['alpha_constant']!=255:v.append(f'{h}: decoded alpha not constant 255')
  except Exception as e:v.append(str(e))
 rows=[]
 for name,(cm,csh,am,ash) in PAIRS.items():
  try:
   cr,ar=bm[cm],bm[am]
   if cr.get('violations') or ar.get('violations'):raise ValueError('material row violations')
   cp,apx=ps(cr),ps(ar)
   if cp['shader']!=csh or apx['shader']!=ash:raise ValueError('pixel shader identity drift')
   if int(cr['material_fields']['unk20'])!=0x88 or int(ar['material_fields']['unk20'])!=0x88:raise ValueError('blend selector drift')
   rows.append({'name':name,'color_material':cm,'attenuation_material':am,'color_shader':csh,'attenuation_shader':ash,
     'same_vertex_shader':norm(cr['dependencies']['vertex']['shader']['tag_hash'])==norm(ar['dependencies']['vertex']['shader']['tag_hash']),
     'same_texture_sequence':cp['textures']==apx['textures'],'same_sampler_records':cp['samplers']==apx['samplers'],
     'same_tfx':cp['tfx']==apx['tfx'],'color_vec4':cp['vec4'],'attenuation_vec4':apx['vec4'],
     'color_usage':usage(bs,csh),'attenuation_usage':usage(bs,ash)})
  except Exception as e:v.append(f'{name}: {e}')
 asm={}
 for h in ('8108E958','8108E959','80AAE1CD'):
  p=a.disasm_dir/f'PS_{h}_GFX700.s';asm[h]=p.read_text(errors='replace') if p.exists() else ''
  if not asm[h]:v.append(f'{h}: disassembly absent')
 anchors(asm['8108E958'],A958,'8108E958',v);anchors(asm['8108E959'],A959,'8108E959',v);anchors(asm['80AAE1CD'],ACONST,'80AAE1CD',v)
 u958=usage(bs,'8108E958');u959=usage(bs,'8108E959')
 got958={x['texture_indices'][0]:x['dmask_channels'] for x in u958['instructions'] if len(x['texture_indices'])==1}
 got959={x['texture_indices'][0]:x['dmask_channels'] for x in u959['instructions'] if len(x['texture_indices'])==1}
 exp958={0:'x',1:'w',2:'w',3:'xy',4:'w'}
 if got958!=exp958:v.append(f'8108E958 dmask drift {got958}')
 if got959!={0:'w'}:v.append(f'8108E959 dmask drift {got959}')
 out={'schema':'d1_crota_attenuation_dataflow_proof/v1',
  'status':'D1_CROTA_ATTENUATION_DATAFLOW_REDUCED_EXACT' if not v and len(rows)==5 else 'D1_CROTA_ATTENUATION_DATAFLOW_PARTIAL',
  'material_pairs':rows,'texture_pixel_evidence':tx,
  'procedural_8108E958':{
   'access_masks':exp958,'constant_samples':{'t1.w':1.0,'t2.w':1.0,'t4.w':1.0},
   'constant_sample_evidence':'t1/t2/t4 all bind 80AACF2A; exact decoded BC1 alpha is 255 everywhere',
   'varying_texture_inputs':['t0.x = 8108E7B6 BC4 scalar','t3.xy = 80AAD0E1 BC5 RG'],
   'remaining_inputs':['native interpolants','material/constant-buffer values'],
   'correction':'R10 attenuation 0.58*BC4+0.08 is not native-exact because native 8108E958 also consumes varying BC5 t3.xy and nontexture inputs.'},
  'atlas_8108E959':{
   'access_masks':{0:'w'},'texture_alpha':'t0.w = 1.0 exactly; 8108E951 decoded alpha is 255 everywhere',
   'symbolic_dataflow':{'delta':'(s6-v3, s5-v4, s4-v5)','d':'dot(normalize(delta), second native 3-component interpolant)',
     'u':'clamp(s4*d^2+s5)','q':'clamp(u^2)','A':'t0.w*(s6+s0*q) = s6+s0*q','mrt0':'RGB=0; alpha=A'},
   'correction':'R10 fixed 0.34 is not atlas-alpha-derived. Native attenuation is interpolant/constant driven after t0.w collapses to 1.',
   'constant_values':'WITHHELD pending exact attenuation partner vector-state recovery'},
  'detail_80AAE1CD':{'image_instruction_count':0,'native_output':'RGB=0; alpha=1.0',
   'blend_state8_rgb_consequence':'Source.rgb + Destination.rgb*(1-Source.a) => 0 for RGB if this pass executes on a destination',
   'pass_order':'WITHHELD'},
  'withheld':['native pass order/draw ownership','semantic names for pixel interpolants','numeric 8108E958/959 attenuation ranges','single-pass Blender equivalence'],
  'violations':v,
  'policy':'Promotes only exact resource identity, GCN anchors and decoded retail pixel facts; visual proxy constants are not engine semantics.'}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'status':out['status'],'pair_count':len(rows),'958':out['procedural_8108E958'],'959':out['atlas_8108E959'],'violations':v},indent=2))
 return 0 if out['status']=='D1_CROTA_ATTENUATION_DATAFLOW_REDUCED_EXACT' else 2
if __name__=='__main__':raise SystemExit(main())
