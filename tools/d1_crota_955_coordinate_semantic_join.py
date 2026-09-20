#!/usr/bin/env python3
"""Join PS8108E955 coordinate arithmetic to Crota's exact reused VS semantics.

Structural proof:
* material specialization reduces t3/t4/t1/t2 coordinates to exact zero;
* t0's first two coordinate lanes remain PS attr1.x/attr1.y.

Registered exact-GCN VS semantics:
* for both Crota VS families, PS attr1 links to VS param1;
* param1 is transformed tangent T.

Therefore the first two t0 coordinate lanes are transformed tangent X/Y for both
selected Crota 8108E955 material families. The fetch encoding of source tangent
remains a separate gate.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

MATS={'8108E7A9':'809DE9AB','8108E7B2':'809DF743'}

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--coordinate-specialization',type=Path,required=True)
 ap.add_argument('--vs-semantics',type=Path,required=True)
 ap.add_argument('--out',type=Path,required=True)
 a=ap.parse_args()
 co=json.loads(a.coordinate_specialization.read_text())
 vs=json.loads(a.vs_semantics.read_text());v=[];rows=[]
 if co.get('status')!='D1_CROTA_955_COORDINATE_SPECIALIZATION_EXACT' or co.get('violations'):
  v.append('coordinate specialization not exact')
 if vs.get('status')!='D1_CROTA_VS_SEMANTIC_REUSE_EXACT' or vs.get('violations'):
  v.append('VS semantic reuse not exact')
 sem={x['vertex_shader']:x for x in vs.get('procedural_8108E955_attr1_coordinate',[])}
 bymat={x['material']:x for x in co.get('rows',[])}
 for mh,vsh in MATS.items():
  try:
   r=bymat[mh];s=sem[vsh]
   cs=r['coordinate_specialization']
   if cs['t0']!='first two encoded coordinate lanes = attr1.x, attr1.y':
    raise ValueError(f't0 structural coordinate drift {cs["t0"]}')
   if s['coordinate_source']!='TRANSFORMED_TANGENT_XY':
    raise ValueError(f'VS semantic coordinate drift {s["coordinate_source"]}')
   eq=r['same_sample_equivalence']
   if eq['texture_indices']!=[1,2,4] or eq['same_first_two_encoded_coordinate_lanes']!=[0.0,0.0]:
    raise ValueError(f'repeated sample equivalence drift {eq}')
   if r['t3_terminal_value_effect']!='DEAD_FOR_T4_COORDINATE_AFTER_EXACT_ZERO_MULTIPLIERS':
    raise ValueError('t3 deadness drift')
   rows.append({
    'material':mh,'vertex_shader':vsh,'pixel_shader':'8108E955',
    't0_texture':'8108E7B6',
    't0_first_two_coordinate_lanes':'TRANSFORMED_TANGENT_XY',
    'ps_coordinate_source':'attr1.xy',
    'vs_param_source':'param1.xy',
    'raw_gnm_link_semantic_id':s['raw_gnm_link_semantic_id'],
    'repeated_bc1_sample_relation':'t1.rgba == t2.rgba == t4.rgba == S',
    'repeated_bc1_coordinate_first_two_lanes':[0.0,0.0],
    't3_terminal_value_effect':r['t3_terminal_value_effect'],
   })
  except Exception as ex:v.append(f'{mh}: {ex}')
 out={
  'schema':'d1_crota_955_coordinate_semantic_join/v1',
  'status':'D1_CROTA_955_COORDINATE_SEMANTIC_JOIN_EXACT' if len(rows)==2 and not v else 'D1_CROTA_955_COORDINATE_SEMANTIC_JOIN_PARTIAL',
  'rows':rows,'violations':v,
  'semantic_boundary':{
   't0_first_two_coordinate_lanes':'TRANSFORMED_TANGENT_XY_EXACT_POST_FETCH_INTERFACE',
   'source_tangent_fetch_offsets_formats':'WITHHELD',
   'source_tangent_storage':'SEPARATELY_AUDITED_SNORM16X4',
   'portable_Blender_tangent_coordinate_replay':'NOT_CLOSED_BY_THIS_JOIN',
  },
  'policy':'The tangent coordinate identity is a post-fetch/export-interface fact reused only from exact registered GCN programs. It does not identify source fetch offsets or prove a portable renderer reproduces native DQ-transformed tangent values.',
 }
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'status':out['status'],'rows':rows,'violations':v},indent=2))
 return 0 if out['status']=='D1_CROTA_955_COORDINATE_SEMANTIC_JOIN_EXACT' else 2

if __name__=='__main__':raise SystemExit(main())
