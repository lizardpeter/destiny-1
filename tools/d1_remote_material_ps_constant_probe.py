#!/usr/bin/env python3
"""Resolve exact D1 PS4 material pixel constants from the universal remote corpus.

This is the remote counterpart of d1_material_ps_constant_resolve.py. Requested
material FileHashes are routed through the verified universal member catalog;
serialized PS TFX constants, PS CBuffers and optional subtype-7 external Vector4
containers are decoded by the already source-closed material resolver. No material,
constant, or texture role is inferred here.
"""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_activity_placements import RemoteCorpus
from d1_split_tar_extract import SplitHttpTar
from d1_material_ps_constant_resolve import resolve_material,norm


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--tag-hash',action='append',required=True)
    ap.add_argument('--member-catalog',type=Path,action='append',required=True)
    ap.add_argument('--base-url',required=True);ap.add_argument('--part-count',type=int,default=10)
    ap.add_argument('--runtime',type=Path,required=True);ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args()
    catalogs=load_catalogs(a.member_catalog)
    base=a.base_url.rstrip('/')
    arc=SplitHttpTar([f'{base}/packages.tar.{i:03d}' for i in range(1,a.part_count+1)],retries=6,timeout=90)
    c=RemoteCorpus(arc,catalogs,a.runtime)
    wanted=list(dict.fromkeys(norm(h) for h in a.tag_hash))
    rows={h:resolve_material(c,h) for h in wanted}
    errors=[h for h,r in rows.items() if r.get('error')]
    relations={}
    shader_families={}
    for h,r in rows.items():
        rel=r.get('vector_storage_relation','error');relations[rel]=relations.get(rel,0)+1
        ps=r.get('pixel_shader'); shader_families.setdefault(ps,[]).append(h)
    out={'schema':'d1_remote_material_ps_constant_probe/v1',
         'status':'D1_REMOTE_PS_MATERIAL_CONSTANTS_EXACT' if not errors else 'D1_REMOTE_PS_MATERIAL_CONSTANTS_PARTIAL',
         'requested_materials':wanted,'selected_material_count':len(rows),'error_count':len(errors),'error_materials':errors,
         'vector_storage_relation_counts':relations,'pixel_shader_materials':shader_families,'materials':rows,
         'closed_offsets':{'ps_tfx_bytecode':'0x2D0','ps_tfx_constants':'0x2E0','ps_samplers':'0x2F0','ps_cbuffers':'0x300','ps_vector4_container':'0x32C'},
         'policy':'Exact universal-catalog FileHash routing plus source-closed PS4 ROI material/Vector4 layouts. Raw float/u32 constants are canonical; semantic names require native shader dataflow proof.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n')
    print('STATUS',out['status'],'MATERIALS',len(rows),'ERRORS',len(errors),'RELATIONS',relations)
    for h,r in rows.items():
        print('MATERIAL',h,'VS',r.get('vertex_shader'),'PS',r.get('pixel_shader'),'PS_VEC4',r.get('ps_vector4_container'),
              'TFX_CONSTS',(r.get('ps_tfx_constants') or {}).get('count'),'CBUFFERS',(r.get('ps_cbuffers') or {}).get('count'),
              'RELATION',r.get('vector_storage_relation'),'ERROR',r.get('error'))
    return 0 if not errors else 2
if __name__=='__main__':raise SystemExit(main())
