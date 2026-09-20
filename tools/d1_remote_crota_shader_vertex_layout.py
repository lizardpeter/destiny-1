#!/usr/bin/env python3
"""Join exact Crota retail source vertex layouts to selected color shader families.

This is the source-package counterpart to d1_crota_glb_material_vertex_layout.py.
It reopens model 8108E5B7, uses the exact visual-union material binding, and runs
the pinned Crota D1 ROI stride-pair decoder directly on retail vertex streams.

For materials available in the exact material-stage report it records the
VS/PS IDs next to source mesh/range and primary/secondary UV storage.

This does NOT map a GNM VertexInputSemantic ID to a Tiger stream/fetch element.
That bridge still requires fetch/input-layout evidence.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_split_tar_extract import SplitHttpTar
from d1_remote_activity_placements import RemoteCorpus
from d1_entity_model_probe import parse_model
from d1_entity_model_corpus_export import linked,norm
from d1_entity_model_export import hdr_stride
from d1_crota_visual_union_export import (
    CROTA_MODEL,ENTITY_MODEL_CLASS,visual_union_ranges,decode_crota_mesh_pair,
)

COLOR={'8108E7A9','8108E7AA','8108E7B1','8108E7B2','8108E7B3'}

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--material-bindings',type=Path,required=True)
 ap.add_argument('--stage-state',type=Path,required=True)
 ap.add_argument('--member-catalog',type=Path,action='append',required=True)
 ap.add_argument('--base-url',required=True);ap.add_argument('--part-count',type=int,default=10)
 ap.add_argument('--runtime',type=Path,required=True)
 ap.add_argument('--model',default=CROTA_MODEL);ap.add_argument('--parent',default='8108E4BA')
 ap.add_argument('--out',type=Path,required=True)
 a=ap.parse_args();v=[]

 modelh=norm(a.model);parent=norm(a.parent)
 if modelh!=CROTA_MODEL:v.append(f'model {modelh} != {CROTA_MODEL}')
 bd=json.loads(a.material_bindings.read_text())
 if bd.get('status') not in ('D1_REMOTE_ACTIVITY_MODEL_MATERIAL_BINDINGS_COMPLETE','D1_WORLD_ENTITY_MODEL_MATERIAL_BINDINGS_COMPLETE'):
  v.append(f'material bindings not exact complete: {bd.get("status")}')
 hits=[x for x in bd.get('bindings',[]) if norm(x.get('model'))==modelh and norm(x.get('parent_resource'))==parent]
 if len(hits)!=1:v.append(f'expected one binding {modelh}/{parent}, got {len(hits)}');binding=None
 else:
  binding=hits[0]
  if not binding.get('validation_ok') or binding.get('violations'):v.append('material binding validation failed')

 st=json.loads(a.stage_state.read_text())
 if st.get('status')!='D1_MATERIAL_STAGE_STATE_EXACT' or st.get('violations'):v.append('stage state not exact')
 mats={norm(k):x for k,x in (st.get('materials') or {}).items()}

 cats=load_catalogs(a.member_catalog)
 arc=SplitHttpTar([f'{a.base_url.rstrip("/")}/packages.tar.{i:03d}' for i in range(1,a.part_count+1)],retries=6,timeout=90)
 c=RemoteCorpus(arc,cats,a.runtime)
 meta=c.entry_meta(modelh);payload,src=c.payload(modelh)
 if meta is None or payload is None or norm(meta.get('reference',''))!=ENTITY_MODEL_CLASS:
  v.append('Crota model unavailable/wrong class');model={'meshes':[]}
 else:model=parse_model(payload,'PS4')
 if len(model.get('meshes',[]))!=3:v.append(f'model mesh count {len(model.get("meshes",[]))} !=3')
 ranges,mesh_summaries=visual_union_ranges(model,binding) if binding is not None and model.get('meshes') else ([],[])

 layouts={}
 for mi,mesh in enumerate(model.get('meshes',[])):
  try:
   lr0,h0,_,d0=linked(c,mesh['vertices1']);s0=hdr_stride(h0)
   lr1,h1,_,d1=linked(c,mesh['vertices2']);s1=hdr_stride(h1)
   _,_,_,_,_,layout=decode_crota_mesh_pair(mi,mesh,d0,s0,d1,s1)
   layouts[mi]={
    **layout,
    'vertices1':lr0,'vertices2':lr1,
    'vertices1_taghash':norm(mesh['vertices1']),'vertices2_taghash':norm(mesh['vertices2']),
    'vertex_count':len(d0)//s0,
   }
  except Exception as ex:v.append(f'mesh {mi}: {ex}')

 rows=[]
 for rr in ranges:
  mh=norm(rr['material'])
  if mh not in COLOR:continue
  m=mats.get(mh)
  if not m or m.get('error'):
   v.append(f'{mh}: stage-state material missing/error');continue
  vs=norm((m.get('vs') or {}).get('shader'));ps=norm((m.get('ps') or {}).get('shader'))
  mi=int(rr['mesh_index']);layout=layouts.get(mi)
  if layout is None:v.append(f'{mh}: mesh {mi} layout missing');continue
  pu=bool(layout['primary_uv']);su=bool(layout['secondary_uv'])
  if pu==su:v.append(f'{mh}: UV stream ambiguity primary={pu} secondary={su}')
  rows.append({
    'material':mh,'vertex_shader':vs,'pixel_shader':ps,
    'source_mesh_index':mi,'source_part_indices':[int(x) for x in rr['part_indices']],
    'source_index_offset':int(rr['index_offset']),'source_index_count':int(rr['index_count']),
    'source_vertex_layout':layout,
    'exported_uv_source':'PRIMARY_STREAM' if pu else 'SECONDARY_STREAM',
  })

 proc=[x for x in rows if x['pixel_shader']=='8108E955']
 fam={(x['material'],x['vertex_shader'],x['source_mesh_index'],x['exported_uv_source'],
       int(x['source_vertex_layout']['primary_stride']),int(x['source_vertex_layout']['secondary_stride'])) for x in proc}
 expect={
   ('8108E7A9','809DE9AB',0,'SECONDARY_STREAM',16,20),
   ('8108E7B2','809DF743',2,'PRIMARY_STREAM',12,16),
 }
 if fam!=expect:v.append(f'8108E955 source layout families drift {sorted(fam)} != {sorted(expect)}')
 if len(rows)!=6:v.append(f'color source range count {len(rows)} !=6')

 out={
  'schema':'d1_crota_retail_shader_vertex_layout/v1',
  'status':'D1_CROTA_RETAIL_SHADER_VERTEX_LAYOUT_EXACT' if not v else 'D1_CROTA_RETAIL_SHADER_VERTEX_LAYOUT_PARTIAL',
  'model':modelh,'model_source':str(src) if src else None,
  'mesh_summaries':mesh_summaries,'mesh_layouts':{str(k):x for k,x in sorted(layouts.items())},
  'color_range_count':len(rows),'rows':rows,
  'procedural_8108E955_source_layout_families':[
   {'material':x[0],'vertex_shader':x[1],'source_mesh_index':x[2],
    'exported_uv_source':x[3],'primary_stride':x[4],'secondary_stride':x[5]}
   for x in sorted(fam)
  ],
  'violations':v,
  'semantic_boundary':{
   'retail_stream_bytes_and_stride_pair':'EXACT_SOURCE_PACKAGE',
   'material_to_VS_PS':'EXACT_MATERIAL_STAGE_STATE',
   'exported_UV_source_stream':'EXACT_CROTA_D1_ROI_STRIDE_PAIR_DECODER',
   'GNM_vertex_input_semantic_to_Tiger_stream_element':'WITHHELD_PENDING_FETCH_LAYOUT',
  },
  'policy':'This joins exact retail model streams and exact material shader IDs. UV storage is a source-decoder fact. A GNM vertex input semantic is not renamed UV until the missing fetch/input-layout bridge proves that mapping.',
 }
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'status':out['status'],'procedural':out['procedural_8108E955_source_layout_families'],
                   'mesh_layouts':out['mesh_layouts'],'violations':v},indent=2))
 return 0 if out['status']=='D1_CROTA_RETAIL_SHADER_VERTEX_LAYOUT_EXACT' else 2

if __name__=='__main__':raise SystemExit(main())
