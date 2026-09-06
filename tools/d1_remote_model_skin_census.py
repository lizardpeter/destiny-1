#!/usr/bin/env python3
"""Census exact inline D1 ROI skin data for a retail PS4 s_entity_model.

This is a read-only proof tool. It resolves the model and linked primary/index
buffers by encoded Tiger FileHash across caller-supplied verified package
catalogs, applies the already source-closed D1 inline skin layouts, and reports
joint domains for the full mesh and for stage-0/highest-detail rendered parts.

No skeleton identity is assumed. --node-count is optional and, when supplied,
acts only as a compatibility assertion on every nonzero decoded joint index.
"""
from __future__ import annotations
import argparse, json, struct, sys
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))

from d1_entity_model_export import decode_indices, index_is32, primitive_faces
from d1_entity_model_probe import parse_model
from d1_guardian_stage_part_material_resolve import HIGHEST_LODS
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_model_tgxm_signature_match import LazyExactHashResolver
from d1_split_tar_extract import SplitHttpTar

SENTINELS={32767,-32767}


def norm(s:str)->str: return s.upper().removeprefix('0X').zfill(8)

def stride_from_header(h:bytes)->int: return struct.unpack_from('<h',h,4)[0]

def decode_skin_unbounded(payload:bytes,stride:int,node_count:int|None):
    if stride not in (0x0C,0x10): raise ValueError(f'unsupported D1 skin primary stride {stride:#x}')
    if len(payload)%stride: raise ValueError(f'payload size {len(payload)} not divisible by {stride}')
    n=len(payload)//stride
    joints=np.zeros((n,4),dtype=np.uint16); raw_weights=np.zeros((n,4),dtype=np.uint8)
    modes={'rigid':0,'inline2':0,'inline4':0}; domain=set()
    for vi,off in enumerate(range(0,len(payload),stride)):
        wpos=struct.unpack_from('<h',payload,off+6)[0]
        if stride==0x0C:
            if wpos in SENTINELS:
                inds=list(payload[off+8:off+10])+[0,0]; vals=list(payload[off+10:off+12])+[0,0]; modes['inline2']+=1
            elif wpos>=0:
                inds=[wpos,0,0,0]; vals=[255,0,0,0]; modes['rigid']+=1
            else:
                raise ValueError(f'negative non-sentinel position W {wpos} at vertex {vi}')
        else:
            vals=list(payload[off+8:off+12]); inds=list(payload[off+12:off+16]); modes['inline4']+=1
        if sum(vals)!=255: raise ValueError(f'vertex {vi}: raw weights sum {sum(vals)}, expected 255')
        for k,(j,w) in enumerate(zip(inds,vals)):
            if not w: continue
            if node_count is not None and j>=node_count:
                raise ValueError(f'vertex {vi}: nonzero joint {j} outside asserted node_count {node_count}')
            joints[vi,k]=j; raw_weights[vi,k]=w; domain.add(int(j))
    return joints,raw_weights,{'vertex_count':n,'modes':modes,'bone_domain':sorted(domain),'bone_domain_max':max(domain) if domain else None}

def linked(resolver,h):
    _v,e,head=resolver.bytes(norm(h)); ph=norm(e['reference']); _pv,pe,payload=resolver.bytes(ph)
    return head,payload,{'header_hash':norm(h),'payload_hash':ph,'payload_size':len(payload),'payload_entry_size':int(pe['file_size'])}

def stage0_parts(mesh):
    offsets=mesh.get('stage_part_offsets_source_derived') or mesh.get('stage_part_offsets')
    if not offsets or len(offsets)<2: raise ValueError('mesh lacks decoded stage-part boundaries')
    a,b=int(offsets[0]),int(offsets[1]); parts=mesh['parts']
    if a<0 or b<a or b>len(parts): raise ValueError(f'invalid stage0 bounds {a}/{b}/{len(parts)}')
    return [(pi,p) for pi,p in enumerate(parts[a:b],start=a) if int(p['lod']) in HIGHEST_LODS]

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument('--model',required=True)
    ap.add_argument('--member-catalog',type=Path,action='append',required=True)
    ap.add_argument('--base-url',required=True);ap.add_argument('--part-count',type=int,default=10)
    ap.add_argument('--runtime',type=Path,required=True);ap.add_argument('--node-count',type=int)
    ap.add_argument('-o','--output',type=Path,required=True); a=ap.parse_args()
    tag=norm(a.model); catalogs=load_catalogs(a.member_catalog)
    arc=SplitHttpTar([f"{a.base_url.rstrip('/')}/packages.tar.{i:03d}" for i in range(1,a.part_count+1)],retries=6,timeout=90)
    resolver=LazyExactHashResolver(arc,catalogs,a.runtime)
    _mv,me,mb=resolver.bytes(tag); model=parse_model(mb,'PS4')
    meshes=[]; global_domain=set(); active_domain=set()
    for mi,m in enumerate(model['meshes']):
        vh,vp,vmeta=linked(resolver,m['vertices1']); stride=stride_from_header(vh)
        joints,weights,smeta=decode_skin_unbounded(vp,stride,a.node_count)
        ih,ip,imeta=linked(resolver,m['indices']); is32=index_is32(ih); inds=decode_indices(ip,is32)
        full_domain=set(smeta['bone_domain']); global_domain|=full_domain
        selected=[]; mesh_active_domain=set(); active_vertex_union=set()
        for pi,p in stage0_parts(m):
            off=int(p['index_offset']);count=int(p['index_count']);ptype=int(p['primitive_type'])
            sl=inds[off:off+count]
            if len(sl)!=count: raise ValueError(f'mesh {mi} part {pi}: short index slice')
            faces=primitive_faces(sl,ptype,is32)
            used=np.unique(faces.reshape(-1)) if len(faces) else np.empty((0,),dtype=np.int64)
            if len(used) and int(used.max())>=len(joints): raise ValueError(f'mesh {mi} part {pi}: source vertex out of range')
            d=sorted({int(j) for vi in used for j,w in zip(joints[vi],weights[vi]) if int(w)>0})
            mesh_active_domain.update(d); active_vertex_union.update(int(x) for x in used)
            selected.append({'part_index':pi,'lod':int(p['lod']),'index_offset':off,'index_count':count,'primitive_type':ptype,
                             'triangle_count':int(len(faces)),'unique_source_vertex_count':int(len(used)),'bone_domain':d,
                             'material':p.get('material')})
        active_domain|=mesh_active_domain
        meshes.append({'mesh_index':mi,'primary_stride':stride,'vertex_buffer':vmeta,'index_buffer':imeta,
                       'full_skin':smeta,'stage0_highest_part_count':len(selected),'stage0_highest_parts':selected,
                       'stage0_highest_unique_source_vertex_count':len(active_vertex_union),
                       'stage0_highest_bone_domain':sorted(mesh_active_domain)})
    rep={'schema':'d1_remote_model_skin_census/v1','model_tag_hash':tag,'model_entry_size':int(me['file_size']),
         'model_mesh_count':len(model['meshes']),'asserted_node_count':a.node_count,'full_model_bone_domain':sorted(global_domain),
         'stage0_highest_bone_domain':sorted(active_domain),'meshes':meshes,
         'policy':'Joint indices and U8 weights are decoded only from the source-closed D1 ROI primary-stream layouts. Stage selection uses decoded stage 0 plus the existing source-backed highest-LOD set. No joint names or skeleton identity are inferred.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(rep,indent=2)+'\n')
    print('MODEL',tag,'MESHES',len(meshes),'FULL_DOMAIN',sorted(global_domain),'ACTIVE_DOMAIN',sorted(active_domain),'ASSERT_NODE_COUNT',a.node_count)
    for m in meshes: print('MESH',m['mesh_index'],'STRIDE',hex(m['primary_stride']),'VERTS',m['full_skin']['vertex_count'],'MODES',m['full_skin']['modes'],'ACTIVE_PARTS',m['stage0_highest_part_count'],'ACTIVE_DOMAIN',m['stage0_highest_bone_domain'])
    return 0

if __name__=='__main__': raise SystemExit(main())
