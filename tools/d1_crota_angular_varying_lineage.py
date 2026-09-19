#!/usr/bin/env python3
"""Trace Crota angular pixel inputs back to exact vertex export producers.

The terminal RGB/alpha equations repeatedly consume attr0.xyz and attr2.xyz.
d1_gnm_vs_ps_linkage proves raw GNM semantic-ID linkage from each PS attr index
to a VS param index. d1_crota_vs_signed_cross_export independently proves that
VS param2.xyz is a signed scalar times cross(param0.xyz,param1.xyz).

This join records those exact relationships. It deliberately does not rename any
param/attr as normal, tangent, bitangent, position, view direction, or lighting.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

COLOR_PS={'8108E953','8108E955','8108E956'}
ATTEN_PS={'8108E958','8108E959'}

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--linkage',type=Path,required=True)
 ap.add_argument('--signed-cross',type=Path,required=True)
 ap.add_argument('--out',type=Path,required=True)
 a=ap.parse_args()
 l=json.loads(a.linkage.read_text());x=json.loads(a.signed_cross.read_text());v=[];rows=[]
 if l.get('status')!='D1_GNM_VS_PS_LINKAGE_EXACT' or l.get('violations'):v.append('GNM linkage not exact')
 if x.get('status')!='D1_CROTA_VS_SIGNED_CROSS_EXPORT_EXACT' or x.get('violations'):v.append('signed-cross proof not exact')
 cross={r['vertex_shader']:r for r in x.get('shaders',[])}
 for q in l.get('links',[]):
  ps=q.get('pixel_shader');vs=q.get('vertex_shader')
  if ps not in COLOR_PS|ATTEN_PS:continue
  by={int(r['attr_index']):r for r in q.get('consumed_linkage',[])}
  if 0 not in by or 2 not in by:
   v.append(f'{vs}:{ps}: attr0/attr2 not both consumed');continue
  cr=cross.get(vs)
  if not cr:v.append(f'{vs}:{ps}: signed-cross VS row missing');continue
  parts=[]
  for ai in (0,2):
   z=by[ai];pi=z.get('vs_param_index')
   parts.append({
    'ps_attr_index':ai,'raw_gnm_semantic_id':int(z['semantic']),
    'vs_param_index':None if pi is None else int(pi),
    'vs_export_f16':z.get('vs_export_f16'),
    'ps_default_value':int(z['ps_default_value']),
    'ps_flat':bool(z['ps_flat']),'ps_linear':bool(z['ps_linear']),'ps_custom':bool(z['ps_custom']),
    'is_signed_cross_export_param2':pi==2,
   })
  rows.append({
   'vertex_shader':vs,'pixel_shader':ps,
   'terminal_equation_family':'COLOR' if ps in COLOR_PS else 'ATTENUATION',
   'angular_inputs':parts,
   'signed_cross_relation':cr['export_relation'],
   'signed_cross_factor_semantic':'WITHHELD',
   'vector_semantics':'WITHHELD',
  })
 out={
  'schema':'d1_crota_angular_varying_lineage/v1',
  'status':'D1_CROTA_ANGULAR_VARYING_LINEAGE_EXACT' if rows and not v else 'D1_CROTA_ANGULAR_VARYING_LINEAGE_PARTIAL',
  'link_count':len(rows),'links':rows,'violations':v,
  'semantic_boundary':{
   'PS_attr_to_VS_param':'EXACT_RAW_GNM_SEMANTIC_ID_LINKAGE',
   'VS_param2_signed_cross_relation':'EXACT_NATIVE_GCN_REGISTER_IDENTITY',
   'normal_tangent_bitangent_position_labels':'WITHHELD',
   'API12_vector_semantic':'WITHHELD',
  },
  'policy':'This proof closes producer identity for attr0/attr2 and recognizes the already-proven param2 signed-cross export when linked. Familiar graphics interpretations are not promoted without independent fetch/semantic evidence.',
 }
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'status':out['status'],'links':[(r['vertex_shader'],r['pixel_shader'],[(x['ps_attr_index'],x['raw_gnm_semantic_id'],x['vs_param_index'],x['is_signed_cross_export_param2']) for x in r['angular_inputs']]) for r in rows],'violations':v},indent=2))
 return 0 if out['status']=='D1_CROTA_ANGULAR_VARYING_LINEAGE_EXACT' else 2

if __name__=='__main__':raise SystemExit(main())
