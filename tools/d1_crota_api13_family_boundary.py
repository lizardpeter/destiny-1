#!/usr/bin/env python3
"""Prove the shared API13[6:7] boundary across Crota color shader families.

Consumes exact GCN constant-buffer provenance and exact terminal RGB/alpha slices.
The result classifies API13 dependency by native shader family without assigning an
engine semantic to API13.

For the three high-detail color shaders every terminal RGB channel depends on
API13 dwords 6 and 7. The paired computed-alpha shaders do not carry API13 into
terminal alpha. This is a producer-boundary fact, not a lighting/exposure label.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

COLOR=('8108E953','8108E955','8108E956')
ALPHA=('8108E958','8108E959')

def norm(x):return str(x).upper().removeprefix('0X').zfill(8)

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--cbuffer-usage',type=Path,required=True)
 ap.add_argument('--rgb-slice',type=Path,required=True)
 ap.add_argument('--alpha-slice',type=Path,required=True)
 ap.add_argument('--out',type=Path,required=True)
 a=ap.parse_args()
 cb=json.loads(a.cbuffer_usage.read_text());rgb=json.loads(a.rgb_slice.read_text());al=json.loads(a.alpha_slice.read_text());v=[];rows=[]
 if cb.get('status')!='D1_GCN_CBUFFER_USAGE_EXACT' or cb.get('missing_usage'):v.append('cbuffer usage not exact')
 if rgb.get('status')!='D1_GCN_TERMINAL_RGB_SLICE_EXACT' or rgb.get('violations'):v.append('RGB slice not exact')
 if al.get('status')!='D1_GCN_TERMINAL_ALPHA_SLICE_EXACT' or al.get('violations'):v.append('alpha slice not exact')
 cby={norm(x['shader']):x for x in cb.get('shaders',[])}
 rby={norm(x['shader']):x for x in rgb.get('shaders',[])}
 aby={norm(x['shader']):x for x in al.get('shaders',[])}

 for sh in COLOR:
  try:
   cr=cby[sh];sr=rby[sh]
   usage=[int(x) for x in (cr.get('api_slot_read_dwords') or {}).get('13',[])]
   if usage!=[6,7]:raise ValueError(f'{sh}: full API13 read set {usage} != [6,7]')
   channels={}
   for ch in 'RGB':
    dws=[int(x) for x in ((sr['channels'][ch]['value_slice'].get('cbuffer_dwords') or {}).get('13',[]))]
    if dws!=[6,7]:raise ValueError(f'{sh}:{ch}: terminal API13 dependency {dws} != [6,7]')
    channels[ch]=dws
   rows.append({'shader':sh,'family':'COLOR_RGB','full_shader_api13_dwords':usage,
                'terminal_channels_api13_dwords':channels,'terminal_api13_required':True})
  except Exception as ex:v.append(str(ex))

 for sh in ALPHA:
  try:
   cr=cby[sh];sr=aby[sh]
   usage=[int(x) for x in (cr.get('api_slot_read_dwords') or {}).get('13',[])]
   terminal=[int(x) for x in ((sr.get('value_slice') or {}).get('cbuffer_dwords') or {}).get('13',[])]
   if terminal:raise ValueError(f'{sh}: terminal alpha unexpectedly depends on API13 {terminal}')
   rows.append({'shader':sh,'family':'COMPUTED_ALPHA_PARTNER','full_shader_api13_dwords':usage,
                'terminal_alpha_api13_dwords':terminal,'terminal_api13_required':False})
  except Exception as ex:v.append(str(ex))

 out={
  'schema':'d1_crota_api13_family_boundary/v1',
  'status':'D1_CROTA_API13_FAMILY_BOUNDARY_EXACT' if len(rows)==5 and not v else 'D1_CROTA_API13_FAMILY_BOUNDARY_PARTIAL',
  'rows':rows,'violations':v,
  'shared_color_terminal_dwords':[6,7],
  'observed_boundary':'API13[6:7] reaches every terminal RGB channel of PS8108E953/955/956; API13 does not reach terminal alpha of PS8108E958/959.',
  'semantic_boundary':{
   'API13_slot_and_dwords':'EXACT_SONY_USER_DATA_PROVENANCE',
   'terminal_dependency':'EXACT_NATIVE_DATAFLOW_SLICE',
   'API13_engine_semantic':'WITHHELD',
   'lighting_exposure_gain_interpretation':'WITHHELD',
  },
  'policy':'The repeated color-only dependency is promoted only as a structural runtime/global input boundary. No physical or engine name is inferred from the shared usage.',
 }
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'status':out['status'],'rows':rows,'violations':v},indent=2))
 return 0 if out['status']=='D1_CROTA_API13_FAMILY_BOUNDARY_EXACT' else 2

if __name__=='__main__':raise SystemExit(main())
