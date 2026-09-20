#!/usr/bin/env python3
"""Audit and preserve Crota's exact fourth tangent-storage lane from retail streams.

The current Crota stride-pair decoder intentionally returns tangent xyz only.
Retail secondary streams nevertheless contain an adjacent fourth signed-normalized
int16 lane in the exact tangent storage block:

  mesh0/mesh1 secondary stride 0x14: int16x4 at +0x0C
  mesh2       secondary stride 0x10: int16x4 at +0x08

This audit proves the raw domain and triangle consistency and verifies that xyz
exactly matches the existing source decoder. It does NOT yet claim that raw W is
the native VS handedness input or standard glTF TANGENT.w; fetch-layout evidence
remains the separate bridge.
"""
from __future__ import annotations
import argparse,collections,json
from pathlib import Path
import numpy as np

from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_split_tar_extract import SplitHttpTar
from d1_remote_activity_placements import RemoteCorpus
from d1_entity_model_probe import parse_model
from d1_entity_model_corpus_export import linked,norm
from d1_entity_model_export import hdr_stride,index_is32,decode_indices,primitive_faces
from d1_crota_visual_union_export import (
    CROTA_MODEL,ENTITY_MODEL_CLASS,visual_union_ranges,decode_crota_mesh_pair,
    decode_crota_full_tangent_storage,
)

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--material-bindings',type=Path,required=True)
 ap.add_argument('--member-catalog',type=Path,action='append',required=True)
 ap.add_argument('--base-url',required=True);ap.add_argument('--part-count',type=int,default=10)
 ap.add_argument('--runtime',type=Path,required=True)
 ap.add_argument('--model',default=CROTA_MODEL);ap.add_argument('--parent',default='8108E4BA')
 ap.add_argument('--out',type=Path,required=True)
 a=ap.parse_args();v=[]

 modelh=norm(a.model);parent=norm(a.parent)
 bd=json.loads(a.material_bindings.read_text())
 hits=[x for x in bd.get('bindings',[]) if norm(x.get('model'))==modelh and norm(x.get('parent_resource'))==parent]
 if len(hits)!=1:v.append(f'expected one exact material binding, got {len(hits)}');binding=None
 else:binding=hits[0]
 if binding and (not binding.get('validation_ok') or binding.get('violations')):v.append('material binding invalid')

 cats=load_catalogs(a.member_catalog)
 arc=SplitHttpTar([f'{a.base_url.rstrip("/")}/packages.tar.{i:03d}' for i in range(1,a.part_count+1)],retries=6,timeout=90)
 c=RemoteCorpus(arc,cats,a.runtime)
 meta=c.entry_meta(modelh);payload,src=c.payload(modelh)
 if meta is None or payload is None or norm(meta.get('reference',''))!=ENTITY_MODEL_CLASS:
  v.append('Crota model unavailable/wrong class');model={'meshes':[]}
 else:model=parse_model(payload,'PS4')
 ranges,_=visual_union_ranges(model,binding) if binding and model.get('meshes') else ([],[])

 allw=collections.Counter();usedw=collections.Counter();rows=[];mixed=[]
 for mi,mesh in enumerate(model.get('meshes',[])):
  try:
   lr0,h0,_,d0=linked(c,mesh['vertices1']);s0=hdr_stride(h0)
   lr1,h1,_,d1=linked(c,mesh['vertices2']);s1=hdr_stride(h1)
   pos,uv,nrm,tan3,col,layout=decode_crota_mesh_pair(mi,mesh,d0,s0,d1,s1)
   raw4,dec4,off=decode_crota_full_tangent_storage(mi,d1,s1,bool(layout['primary_uv']))
   if tan3 is None or tan3.shape!=(len(dec4),3):raise ValueError(f'tangent xyz shape {None if tan3 is None else tan3.shape}')
   err=float(np.max(np.abs(tan3-dec4[:,:3]))) if len(dec4) else 0.0
   if err!=0.0:v.append(f'mesh{mi}: full tangent xyz != existing decoder, maxerr={err}')
   wc=collections.Counter(int(x) for x in raw4[:,3].tolist());allw.update(wc)
   used=set()
   lri,ih,_,idata=linked(c,mesh['indices']);inds=decode_indices(idata,index_is32(ih))
   for rr in [x for x in ranges if int(x['mesh_index'])==mi]:
    faces=primitive_faces(inds[int(rr['index_offset']):int(rr['index_offset'])+int(rr['index_count'])],
                          int(rr['primitive_type']),index_is32(ih))
    if len(faces):
     used.update(int(x) for x in np.unique(faces))
     for fi,face in enumerate(faces):
      ww=raw4[np.asarray(face,dtype=np.int64),3]
      if not np.all(ww==ww[0]) and len(mixed)<64:
       mixed.append({'mesh_index':mi,'range_offset':int(rr['index_offset']),'face_index':fi,
                     'source_indices':[int(x) for x in face],'raw_tangent_w':[int(x) for x in ww]})
   uw=raw4[np.asarray(sorted(used),dtype=np.int64),3] if used else np.empty((0,),dtype=np.int16)
   uwc=collections.Counter(int(x) for x in uw.tolist());usedw.update(uwc)
   rows.append({
    'mesh_index':mi,'primary_stride':s0,'secondary_stride':s1,'row_mode':layout['row_mode'],
    'primary_uv':bool(layout['primary_uv']),'secondary_uv':bool(layout['secondary_uv']),
    'tangent_storage_byte_offset':off,'tangent_storage_type':'SNORM16x4',
    'vertex_count':len(raw4),'selected_range_vertex_count':len(used),
    'raw_tangent_w_counts':{str(k):n for k,n in sorted(wc.items())},
    'selected_range_raw_tangent_w_counts':{str(k):n for k,n in sorted(uwc.items())},
    'decoded_tangent_w_min':float(dec4[:,3].min()) if len(dec4) else None,
    'decoded_tangent_w_max':float(dec4[:,3].max()) if len(dec4) else None,
    'xyz_decoder_max_abs_error':err,
    'vertices1':lr0,'vertices2':lr1,
   })
  except Exception as ex:v.append(f'mesh{mi}: {ex}')

 sign_only=bool(allw) and set(allw)<= {-32767,32767}
 used_sign_only=bool(usedw) and set(usedw)<= {-32767,32767}
 if not sign_only:v.append(f'full Crota raw tangent-W domain not +/-32767: {sorted(allw)}')
 if not used_sign_only:v.append(f'selected-range tangent-W domain not +/-32767: {sorted(usedw)}')
 out={
  'schema':'d1_crota_tangent_storage_audit/v1',
  'status':'D1_CROTA_TANGENT_STORAGE_EXACT' if len(rows)==3 and not v else 'D1_CROTA_TANGENT_STORAGE_PARTIAL',
  'model':modelh,'model_source':str(src) if src else None,
  'mesh_count':len(rows),'rows':rows,
  'raw_tangent_w_counts':{str(k):n for k,n in sorted(allw.items())},
  'selected_range_raw_tangent_w_counts':{str(k):n for k,n in sorted(usedw.items())},
  'all_raw_tangent_w_exact_sign_domain':sign_only,
  'selected_range_raw_tangent_w_exact_sign_domain':used_sign_only,
  'mixed_raw_tangent_w_triangle_count':len(mixed),'mixed_triangle_examples':mixed,
  'violations':v,
  'semantic_boundary':{
   'tangent_storage_xyzw':'EXACT_RETAIL_SECONDARY_STREAM_SNORM16X4',
   'xyz_matches_existing_decoder':'EXACT',
   'raw_w_domain':'EXACT',
   'raw_w_equals_native_VS_handedness':'WITHHELD_PENDING_FETCH_LAYOUT',
   'raw_w_equals_standard_gltf_tangent_w':'WITHHELD_PENDING_NATIVE_TO_GLTF_BASIS_PROOF',
  },
  'policy':'The fourth source lane is preserved and audited byte-for-byte. Its exact +/-32767 domain is not by itself sufficient to identify it with the separately proven post-fetch native handedness lane.',
 }
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'status':out['status'],'raw_w':out['raw_tangent_w_counts'],
                   'selected_w':out['selected_range_raw_tangent_w_counts'],
                   'mixed_triangles':len(mixed),'rows':rows,'violations':v},indent=2))
 return 0 if out['status']=='D1_CROTA_TANGENT_STORAGE_EXACT' else 2

if __name__=='__main__':raise SystemExit(main())
