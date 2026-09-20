#!/usr/bin/env python3
"""Extract exact Crota material ↔ VS/PS ↔ source vertex-layout facts from a GLB carrier.

The Crota R7/R8 carriers preserve exact source-material metadata and the D1 ROI
stride-pair layout selected by the source decoder. This tool records, per active
color surface:
* exact material / vertex shader / pixel shader IDs;
* source mesh index and part/range;
* primary/secondary strides;
* whether the source decoder obtained exported TEXCOORD_0 from primary or
  secondary stream;
* the glTF accessor indices for position/normal/tangent/texcoord.

This is a geometry/export provenance proof only. It does not equate any PS GNM
attr or VS raw semantic ID with TEXCOORD_0; that requires the independent shader
lineage join.
"""
from __future__ import annotations
import argparse,json,struct
from pathlib import Path

COLOR={'8108E7A9','8108E7AA','8108E7B1','8108E7B2','8108E7B3'}
EXPECTED_PS={
 '8108E7A9':'8108E955','8108E7B2':'8108E955',
 '8108E7AA':'8108E956','8108E7B3':'8108E956',
 '8108E7B1':'8108E953',
}
EXPECTED_VS={
 '8108E7A9':'809DE9AB','8108E7AA':'809DE9AB',
 '8108E7B1':'809DF743','8108E7B2':'809DF743','8108E7B3':'809DF743',
}

def read_glb(p):
 b=p.read_bytes()
 if len(b)<20:raise ValueError('short GLB')
 magic,ver,total=struct.unpack_from('<4sII',b,0)
 if magic!=b'glTF' or ver!=2 or total!=len(b):raise ValueError('not exact GLB v2')
 jl,jt=struct.unpack_from('<II',b,12)
 if jt!=0x4e4f534a:raise ValueError('missing JSON chunk')
 return json.loads(b[20:20+jl].decode().rstrip(' \x00'))

def main():
 ap=argparse.ArgumentParser();ap.add_argument('glb',type=Path);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
 d=read_glb(a.glb);v=[];rows=[]
 scene=d['scenes'][int(d.get('scene',0))]
 active=set(scene.get('nodes',[]))
 # Active content is under a root adapter in the portable carrier.
 frontier=list(active);reachable=set()
 while frontier:
  i=frontier.pop()
  if i in reachable:continue
  reachable.add(i);frontier.extend(d['nodes'][i].get('children',[]))
 mats=d.get('materials') or []
 for ni,n in enumerate(d.get('nodes',[])):
  if ni not in reachable or n.get('mesh') is None:continue
  mesh=d['meshes'][int(n['mesh'])];me=mesh.get('extras') or {}
  if len(mesh.get('primitives',[]))!=1:v.append(f'node {ni}: primitive count !=1');continue
  pr=mesh['primitives'][0];mi=pr.get('material')
  if mi is None or int(mi)>=len(mats):v.append(f'node {ni}: material unavailable');continue
  mx=mats[int(mi)].get('extras') or {};mh=str(mx.get('d1_material_taghash') or me.get('material') or '').upper()
  if mh not in COLOR:continue
  layout=me.get('d1_roi_stride_pair_layout') or {}
  attrs=pr.get('attributes') or {}
  for req in ('POSITION','NORMAL','_D1_TANGENT','TEXCOORD_0'):
   if req not in attrs:v.append(f'{mh}: missing {req}')
  vs=str(mx.get('d1_vertex_shader') or '').upper();ps=str(mx.get('d1_pixel_shader') or '').upper()
  if vs!=EXPECTED_VS[mh]:v.append(f'{mh}: VS {vs} != {EXPECTED_VS[mh]}')
  if ps!=EXPECTED_PS[mh]:v.append(f'{mh}: PS {ps} != {EXPECTED_PS[mh]}')
  pu=bool(layout.get('primary_uv'));su=bool(layout.get('secondary_uv'))
  if pu==su:v.append(f'{mh}: expected exactly one source UV stream, got primary={pu} secondary={su}')
  rows.append({
   'node_index':ni,'node_name':n.get('name'),'material':mh,
   'vertex_shader':vs,'pixel_shader':ps,
   'source_mesh_index':int(me.get('mesh_index')),
   'source_part_indices':[int(x) for x in me.get('part_indices',[])],
   'source_index_offset':int(me.get('index_offset')),
   'source_index_count':int(me.get('index_count')),
   'row_mode':layout.get('row_mode'),
   'primary_stride':int(layout.get('primary_stride')),
   'secondary_stride':int(layout.get('secondary_stride')),
   'exported_texcoord0_source':'PRIMARY_STREAM' if pu else 'SECONDARY_STREAM',
   'accessors':{k:int(attrs[k]) for k in ('POSITION','NORMAL','_D1_TANGENT','TEXCOORD_0') if k in attrs},
  })
 rows.sort(key=lambda x:(x['source_mesh_index'],x['source_index_offset'],x['material']))
 proc=[x for x in rows if x['pixel_shader']=='8108E955']
 if len(rows)!=6:v.append(f'active exact color surface count {len(rows)} != 6')
 if len(proc)!=3:v.append(f'active 8108E955 surface count {len(proc)} != 3')
 # The two procedural material identities occur across two source mesh/layout families.
 proc_materials={x['material'] for x in proc}
 if proc_materials!={'8108E7A9','8108E7B2'}:v.append(f'8108E955 material set drift {sorted(proc_materials)}')
 fam={(x['material'],x['vertex_shader'],x['source_mesh_index'],x['exported_texcoord0_source'],x['primary_stride'],x['secondary_stride']) for x in proc}
 expected={
   ('8108E7A9','809DE9AB',0,'SECONDARY_STREAM',16,20),
   ('8108E7B2','809DF743',2,'PRIMARY_STREAM',12,16),
 }
 # 8108E7B2 has two visible ranges; collapse duplicates before comparing.
 got={(mh,vs,mi,uv,p,s) for mh,vs,mi,uv,p,s in fam}
 if got!=expected:v.append(f'procedural source-layout families drift {sorted(got)} != {sorted(expected)}')
 out={
  'schema':'d1_crota_glb_material_vertex_layout/v1',
  'status':'D1_CROTA_GLB_MATERIAL_VERTEX_LAYOUT_EXACT' if not v else 'D1_CROTA_GLB_MATERIAL_VERTEX_LAYOUT_PARTIAL',
  'input':str(a.glb),'active_color_surface_count':len(rows),'rows':rows,
  'procedural_8108E955_source_layout_families':[
   {'material':x[0],'vertex_shader':x[1],'source_mesh_index':x[2],
    'exported_texcoord0_source':x[3],'primary_stride':x[4],'secondary_stride':x[5]}
   for x in sorted(got)
  ],
  'violations':v,
  'semantic_boundary':{
   'material_shader_ids':'EXACT_CARRIER_SOURCE_METADATA',
   'source_mesh_and_stride_pair':'EXACT_CARRIER_SOURCE_METADATA',
   'exported_TEXCOORD_0_source_stream':'EXACT_SOURCE_DECODER_METADATA',
   'PS_attr1_or_VS_raw_semantic_equals_TEXCOORD_0':'WITHHELD_PENDING_SHADER_LINEAGE_JOIN',
  },
  'policy':'The carrier records which decoded source stream supplied exported TEXCOORD_0, but shader GNM semantic IDs are a separate evidence domain. This report deliberately does not infer that attr1 is UV.',
 }
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'status':out['status'],'procedural':out['procedural_8108E955_source_layout_families'],'rows':rows,'violations':v},indent=2))
 return 0 if out['status']=='D1_CROTA_GLB_MATERIAL_VERTEX_LAYOUT_EXACT' else 2

if __name__=='__main__':raise SystemExit(main())
