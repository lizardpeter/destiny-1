#!/usr/bin/env python3
"""Skin and animate a combined D1 Guardian equipment GLB from exact retail bytes.

The input is the combined static GLB emitted by d1_remote_model_export.py. Each
geometry name encodes the originating s_entity_model, mesh index, and retail
index range. This tool reconstructs that source range, recovers the exact source
vertex indices, decodes D1 ROI inline skinning from the original primary vertex
stream, and writes JOINTS_0/WEIGHTS_0 for every exported primitive.

Supported D1 inline forms (old_weights absent):
  * stride 0x0C: ordinary W >= 0 is a rigid bone; W == +/-0x7FFF means
    bytes 8,9 are two indices and bytes 10,11 are two U8 weights.
  * stride 0x10: bytes 8..11 are four U8 weights and bytes 12..15 four indices.

No missing or malformed influence is repaired. Weight sums must equal 255 and
all nonzero indices must fit the target skeleton. The exact D1 skeleton bind
pose and exact retargeted animation are then serialized into one glTF skin.
"""
from __future__ import annotations

import argparse
import io
import json
import re
import struct
import sys
import tempfile
from pathlib import Path

import numpy as np
from pygltflib import GLTF2, Node, Skin, BufferView, Accessor, Animation, AnimationSampler, AnimationChannel, AnimationChannelTarget

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from d1_entry_extract import EntryReader
from d1_entity_model_probe import parse_model
from d1_entity_model_export import decode_indices, primitive_faces, index_is32
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_investment_parent_probe import RemoteLogicalPackage
from d1_remote_model_export import MultiPackageReader
from d1_split_tar_extract import SplitHttpTar
from d1_gltf_bind_rigid_animation import append_accessor

FLOAT=5126
UNSIGNED_SHORT=5123
ARRAY_BUFFER=34962
NAME_RE=re.compile(r'(?P<tag>[0-9A-F]{8})_mesh(?P<mesh>\d+)_range(?P<off>\d+)_(?P<count>\d+)',re.I)
SENTINELS={32767,-32767}


def read_linked_multi(r,by,h):
    e=by[h.upper()]; head=r.entry(e['index']); pe=by.get(e['reference'].upper())
    if pe is None: raise KeyError(f'no payload for {h} -> {e["reference"]}')
    return e,head,pe,r.entry(pe['index'])


def decode_skin(payload:bytes,stride:int,node_count:int):
    if stride not in (0x0C,0x10): raise ValueError(f'unsupported Guardian skin primary stride {stride:#x}')
    if len(payload)%stride: raise ValueError(f'payload size {len(payload)} not divisible by {stride}')
    n=len(payload)//stride
    joints=np.zeros((n,4),dtype='<u2'); weights=np.zeros((n,4),dtype='<f4')
    modes={'rigid':0,'inline2':0,'inline4':0}
    raw_weight_sums=[]; bone_domain=set()
    for vi,off in enumerate(range(0,len(payload),stride)):
        wpos=struct.unpack_from('<h',payload,off+6)[0]
        if stride==0x0C:
            if wpos in SENTINELS:
                inds=list(payload[off+8:off+10]); vals=list(payload[off+10:off+12]); modes['inline2']+=1
            elif wpos>=0:
                inds=[wpos,0,0,0];vals=[255,0,0,0];modes['rigid']+=1
            else:
                raise ValueError(f'negative non-sentinel position W {wpos} at vertex {vi}')
        else:
            vals=list(payload[off+8:off+12]);inds=list(payload[off+12:off+16]);modes['inline4']+=1
        if sum(vals)!=255: raise ValueError(f'weight sum {sum(vals)} != 255 at vertex {vi}: indices={inds} weights={vals}')
        raw_weight_sums.append(sum(vals))
        for k,(j,w) in enumerate(zip(inds,vals)):
            if w==0:
                joints[vi,k]=0;weights[vi,k]=0.0
                continue
            if not (0<=j<node_count): raise ValueError(f'nonzero bone index {j} outside {node_count} at vertex {vi}')
            joints[vi,k]=j;weights[vi,k]=w/255.0;bone_domain.add(j)
    return joints,weights,{'vertex_count':n,'modes':modes,'bone_domain':sorted(bone_domain),'weight_sum_min':min(raw_weight_sums),'weight_sum_max':max(raw_weight_sums)}


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('input_glb',type=Path)
    ap.add_argument('--model-report',type=Path,required=True)
    ap.add_argument('--member-catalog',type=Path,action='append',required=True)
    ap.add_argument('--base-url',required=True);ap.add_argument('--part-count',type=int,default=10)
    ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('--animation-pkg',type=Path,required=True);ap.add_argument('--parser-root',type=Path,required=True)
    ap.add_argument('--skeleton',required=True);ap.add_argument('--rig',required=True);ap.add_argument('--clip',required=True)
    ap.add_argument('--animation-name');ap.add_argument('--fps',type=float,default=30.0)
    ap.add_argument('--out',type=Path,required=True);ap.add_argument('--report',type=Path,required=True)
    a=ap.parse_args()

    model_report=json.loads(a.model_report.read_text())
    model_tags={x['tag_hash'].upper() for x in model_report['models']}
    catalogs=load_catalogs(a.member_catalog)
    arc=SplitHttpTar([f"{a.base_url.rstrip('/')}/packages.tar.{i:03d}" for i in range(1,a.part_count+1)],retries=6,timeout=90)
    views={pkg:RemoteLogicalPackage(arc,fam,a.runtime) for pkg,fam in sorted(catalogs.items())}
    rr=MultiPackageReader(views); by={e['tag_hash'].upper():e for e in rr.entries}

    # Animation/skeleton decode from exact local logical package.
    sys.path.insert(0,str(a.parser_root.resolve()))
    from tag.game_version import Game_Version
    from tag_readers.read_skeleton import read_skeleton,transform_to_np_matrix
    from tag_readers.read_rig import read_runtime_rig
    from tag_readers.read_animation import read_animation
    from animation_decoding.decode_animation import decode_animation
    from runtime_rig.rig_retarget import rig_retarget
    from animation_export.convert_animation_object_to_local import convert_obj_to_local
    from matrix_operations.numpy_matrix_operations import np_decompose_matrix
    from fnv_hashes.bones_names import convert_hash_to_bungie_name

    ar=EntryReader(a.animation_pkg,a.runtime); aby={e['tag_hash'].upper():e for e in ar.entries};ver=Game_Version.D1_ROI
    skh=a.skeleton.upper().removeprefix('0X');righ=a.rig.upper().removeprefix('0X');cliph=a.clip.upper().removeprefix('0X')
    sk=read_skeleton(io.BytesIO(ar.entry(aby[skh]['index'])),ver);rig=read_runtime_rig(io.BytesIO(ar.entry(aby[righ]['index'])),ver)
    with tempfile.NamedTemporaryFile() as f:
        f.write(ar.entry(aby[cliph]['index']));f.flush();f.seek(0);anim=read_animation(f,ver)
    decoded=decode_animation(anim);retargeted=rig_retarget(anim,decoded,sk,rig);local=convert_obj_to_local(anim,retargeted,sk)
    node_count=len(sk.node_defs);control_count=len(rig.controls_relations);h=anim.animation_header
    if int(h.node_count)!=node_count or int(h.rig_control_count)!=control_count or len(local)!=node_count:
        raise ValueError('skeleton/rig/clip dimensions do not match')

    # Cache every selected source model, source index payload, and full primary skin arrays.
    model_cache={}; source_cache={}
    for tag in sorted(model_tags):
        e=by[tag]; m=parse_model(rr.entry(e['index']),'PS4');model_cache[tag]=m
        for mi,mesh in enumerate(m['meshes']):
            vhe,vhh,vpe,vpd=read_linked_multi(rr,by,mesh['vertices1']);stride=struct.unpack_from('<h',vhh,4)[0]
            joints,weights,smeta=decode_skin(vpd,stride,node_count)
            ie,ih,ipe,idata=read_linked_multi(rr,by,mesh['indices']);is32=index_is32(ih);inds=decode_indices(idata,is32)
            ranges={}
            for p in mesh['parts']:
                key=(p['index_offset'],p['index_count']);ranges.setdefault(key,set()).add(p['primitive_type'])
            source_cache[(tag,mi)]={'joints':joints,'weights':weights,'skin_meta':smeta,'indices':inds,'is32':is32,'ranges':ranges}

    g=GLTF2().load_binary(str(a.input_glb));blob=bytearray(g.binary_blob() or b'')
    if len(g.buffers)!=1: raise ValueError('expected one-buffer combined GLB')
    original_node_count=len(g.nodes);original_mesh_count=len(g.meshes)
    bind_rows=[];total_vertices=0;seen_models=set()
    for gm in g.meshes[:original_mesh_count]:
        name=gm.name or ''
        mat=NAME_RE.search(name)
        if mat is None: raise ValueError(f'cannot recover retail source from combined mesh name {name!r}')
        tag=mat.group('tag').upper();mi=int(mat.group('mesh'));off=int(mat.group('off'));count=int(mat.group('count'))
        if tag not in model_tags: raise ValueError(f'combined mesh source {tag} absent from model report')
        sc=source_cache[(tag,mi)]; prim_types=sc['ranges'].get((off,count))
        if not prim_types or len(prim_types)!=1: raise ValueError(f'{tag} mesh {mi} range {off}/{count}: ambiguous primitive type {prim_types}')
        ptype=next(iter(prim_types));sl=sc['indices'][off:off+count];faces=primitive_faces(sl,ptype,sc['is32'])
        used=np.unique(faces.reshape(-1))
        if len(gm.primitives)!=1: raise ValueError(f'{name}: expected one GLB primitive, got {len(gm.primitives)}')
        prim=gm.primitives[0];pos_count=int(g.accessors[prim.attributes.POSITION].count)
        if pos_count!=len(used): raise ValueError(f'{name}: GLB/source vertex count {pos_count}/{len(used)}')
        j=sc['joints'][used];w=sc['weights'][used]
        jacc=append_accessor(g,blob,j,component_type=UNSIGNED_SHORT,accessor_type='VEC4',target=ARRAY_BUFFER)
        wacc=append_accessor(g,blob,w,component_type=FLOAT,accessor_type='VEC4',target=ARRAY_BUFFER)
        prim.attributes.JOINTS_0=jacc;prim.attributes.WEIGHTS_0=wacc
        total_vertices+=len(used);seen_models.add(tag)
        bind_rows.append({'gltf_mesh':name,'model':tag,'source_mesh':mi,'index_offset':off,'index_count':count,'primitive_type':ptype,
                          'source_vertex_count':len(used),'source_vertex_min':int(used.min()),'source_vertex_max':int(used.max()),
                          'bone_domain':sorted(set(int(x) for x in j[w>0]))})
    if seen_models!=model_tags: raise ValueError(f'combined GLB model coverage {seen_models} != expected {model_tags}')

    # Shared exact D1 bind skeleton.
    world=[transform_to_np_matrix(x) for x in sk.default_obj_space_tr];inv_world=[transform_to_np_matrix(x) for x in sk.default_inv_obj_space_tr]
    bone_nodes=[];bone_names=[]
    for i,nd in enumerate(sk.node_defs):
        parent=int(nd.parent_node_index);mat=inv_world[parent]@world[i] if parent>=0 else world[i]
        scale,rot,trans=np_decompose_matrix(mat);name=convert_hash_to_bungie_name(int(nd.bone_hash)) or f'{int(nd.bone_hash)&0xffffffff:08X}'
        if name in bone_names:name=f'{name}_{int(nd.bone_hash)&0xffffffff:08X}'
        bone_names.append(name);idx=len(g.nodes);bone_nodes.append(idx)
        g.nodes.append(Node(name=name,children=[],translation=[float(x) for x in trans],rotation=[float(x) for x in rot.as_quat()],scale=[float(x) for x in scale],extras={'d1BoneIndex':i,'d1BoneHash':f'{int(nd.bone_hash)&0xffffffff:08X}'}))
    root_idx=len(g.nodes);g.nodes.append(Node(name='D1_Guardian_Skeleton',children=[],translation=[0,0,0],rotation=[0,0,0,1],scale=[1,1,1],extras={'d1Skeleton':skh,'d1RuntimeRig':righ}))
    for i,nd in enumerate(sk.node_defs):
        parent=int(nd.parent_node_index)
        (g.nodes[bone_nodes[parent]].children if parent>=0 else g.nodes[root_idx].children).append(bone_nodes[i])
    ibm=np.stack([np.asarray(m.T,dtype='<f4') for m in inv_world],axis=0);ibm_acc=append_accessor(g,blob,ibm,component_type=FLOAT,accessor_type='MAT4')
    skin_idx=len(g.skins);g.skins.append(Skin(joints=bone_nodes,inverseBindMatrices=ibm_acc,skeleton=root_idx,name=f'D1_{skh}_skin'))
    mesh_node_count=0
    for n in g.nodes[:original_node_count]:
        if n.mesh is not None:n.skin=skin_idx;mesh_node_count+=1

    # Exact retargeted local animation.
    channels=[];samplers=[]
    for bi,track in enumerate(local):
        for path,values,kind in (('translation',track.translations,'VEC3'),('rotation',track.rotations,'VEC4'),('scale',track.scales,'VEC3')):
            arr=np.asarray(values,dtype='<f4')
            if arr.size==0:continue
            if arr.ndim!=2:arr=arr.reshape((-1,4 if kind=='VEC4' else 3))
            times=(np.arange(arr.shape[0],dtype='<f4')/a.fps).astype('<f4')
            tacc=append_accessor(g,blob,times,component_type=FLOAT,accessor_type='SCALAR',with_minmax=True);vacc=append_accessor(g,blob,arr,component_type=FLOAT,accessor_type=kind)
            si=len(samplers);samplers.append(AnimationSampler(input=tacc,output=vacc,interpolation='LINEAR'));channels.append(AnimationChannel(sampler=si,target=AnimationChannelTarget(node=bone_nodes[bi],path=path)))
    aname=a.animation_name or f'D1_{cliph}';g.animations.append(Animation(name=aname,channels=channels,samplers=samplers,extras={'d1Clip':cliph,'d1FrameCount':int(h.frame_count),'d1Fps':a.fps}))
    scene_idx=g.scene or 0;roots=list(g.scenes[scene_idx].nodes or []);roots.append(root_idx);g.scenes[scene_idx].nodes=roots
    g.extras={**(g.extras or {}),'d1GuardianSkinProof':{'skeleton':skh,'runtimeRig':righ,'clip':cliph,'modelTags':sorted(model_tags),'policy':'All JOINTS_0/WEIGHTS_0 reconstructed from exact D1 primary vertex bytes; no influence synthesized.'}}
    g.buffers[0].byteLength=len(blob);g.set_binary_blob(bytes(blob));a.out.parent.mkdir(parents=True,exist_ok=True);g.save_binary(str(a.out))
    rep={'schema':'d1_guardian_combined_skin_animation/v1','input':str(a.input_glb),'output':str(a.out),'output_bytes':a.out.stat().st_size,
         'models':sorted(model_tags),'model_count':len(model_tags),'original_mesh_count':original_mesh_count,'bound_mesh_node_count':mesh_node_count,
         'bound_primitive_count':len(bind_rows),'bound_vertex_count':total_vertices,'skin_joint_count':node_count,'runtime_rig_control_count':control_count,
         'clip':cliph,'clip_frame_count':int(h.frame_count),'decoded_track_count':len(decoded),'retargeted_track_count':len(retargeted),'local_track_count':len(local),
         'animation_channel_count':len(channels),'animation_sampler_count':len(samplers),'binding':bind_rows,
         'policy':'Every exported primitive is mapped back to its exact retail model/mesh/index range. Skin influences come from exact source vertices and must validate before serialization.'}
    a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(rep,indent=2)+'\n');print(json.dumps({k:v for k,v in rep.items() if k!='binding'},indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
