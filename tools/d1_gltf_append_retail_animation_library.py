#!/usr/bin/env python3
"""Append exact retail D1 animations to an already-skinned GLB without rebinding it.

This is the production bridge between a source-proven D1 skin checkpoint and a
source-proven cross-package animation graph. The input GLB must already contain a
skin whose joint order/hashes exactly match the supplied retail skeleton. This tool
never changes geometry, materials, JOINTS_0/WEIGHTS_0, inverse bind matrices, skin
membership, or existing node transforms.

For every requested clip it requires:
  * the exact 80802C0E control selects the clip;
  * the exact runtime-rig class pair is 808008B2 -> 8080099B;
  * the clip runtime-component fingerprint exactly equals the rig fingerprint;
  * clip header dimensions equal skeleton nodes / runtime controls;
  * decode_animation yields exactly the runtime-control domain;
  * rig_retarget expands that domain to exactly the skeleton-node domain;
  * local conversion produces exactly one track per skeleton node.

Only then are LINEAR glTF animation channels appended to the existing skin joints.
State/action names are preserved only when exact StringHash preimages are known.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import sys
import tempfile
from pathlib import Path

import numpy as np
from pygltflib import (
    GLTF2, BufferView, Accessor, Animation, AnimationSampler,
    AnimationChannel, AnimationChannelTarget,
)

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))

from d1_animation_control_state_map import decode_control
from d1_animation_retarget_probe import component_rows
from d1_character_family_census import RUNTIME_RIG_DISCRIMINATOR,RUNTIME_RIG_INFO
from d1_entity_resource_probe import parse_resource
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_model_tgxm_signature_match import LazyExactHashResolver
from d1_split_tar_extract import SplitHttpTar

FLOAT=5126


def norm(s:str)->str:
    return s.upper().removeprefix('0X').zfill(8)


def align4(buf:bytearray)->None:
    while len(buf)&3:buf.append(0)


def append_accessor(g:GLTF2,blob:bytearray,data:np.ndarray,*,accessor_type:str,with_minmax:bool=False)->int:
    data=np.ascontiguousarray(data,dtype='<f4')
    align4(blob);off=len(blob);raw=data.tobytes(order='C');blob.extend(raw)
    vi=len(g.bufferViews);g.bufferViews.append(BufferView(buffer=0,byteOffset=off,byteLength=len(raw)))
    count=int(data.shape[0]);acc=Accessor(bufferView=vi,byteOffset=0,componentType=FLOAT,count=count,type=accessor_type)
    if with_minmax:
        if accessor_type=='SCALAR':
            acc.min=[float(np.min(data))];acc.max=[float(np.max(data))]
        else:
            acc.min=[float(x) for x in np.min(data,axis=0)];acc.max=[float(x) for x in np.max(data,axis=0)]
    ai=len(g.accessors);g.accessors.append(acc);return ai


def read_animation_filebacked(read_animation,payload:bytes,version):
    with tempfile.NamedTemporaryFile() as f:
        f.write(payload);f.flush();f.seek(0)
        return read_animation(f,version)


def selected_by_control(control:dict)->dict[str,list[dict]]:
    out={}
    for state in control['state_table']['records']:
        for item in state['selected_animations']:
            out.setdefault(item['tag_hash'].upper(),[]).append({
                'record_index':state['record_index'],'state_hash':state['state_hash'],
                'state_name':state.get('state_name'),'scalar_f32':state['scalar_f32'],
                'packed_selection':state['packed_selection'],
            })
    return out


def node_extra_int(extras:dict|None,*keys:str)->int|None:
    if not isinstance(extras,dict):return None
    for k in keys:
        if k in extras:
            try:return int(extras[k])
            except Exception:return None
    return None


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('input_glb',type=Path)
    ap.add_argument('--member-catalog',type=Path,action='append',required=True)
    ap.add_argument('--base-url',default='https://crypt.cohae.dev/destiny/ps4/packages/latest')
    ap.add_argument('--part-count',type=int,default=10)
    ap.add_argument('--runtime',type=Path,required=True);ap.add_argument('--parser-root',type=Path,required=True)
    ap.add_argument('--skeleton',required=True);ap.add_argument('--rig',required=True);ap.add_argument('--control',required=True)
    ap.add_argument('--clip',action='append',required=True)
    ap.add_argument('--name',action='append',default=[])
    ap.add_argument('--fps',type=float,default=30.0)
    ap.add_argument('--skin-index',type=int,default=0)
    ap.add_argument('--out',type=Path,required=True);ap.add_argument('--report',type=Path,required=True)
    a=ap.parse_args()

    sh,rh,ch=map(norm,(a.skeleton,a.rig,a.control));clips=list(dict.fromkeys(norm(x) for x in a.clip))
    cats=load_catalogs(a.member_catalog)
    arc=SplitHttpTar([f"{a.base_url.rstrip('/')}/packages.tar.{i:03d}" for i in range(1,a.part_count+1)],retries=6,timeout=90)
    resolver=LazyExactHashResolver(arc,cats,a.runtime)
    _sv,se,sb=resolver.bytes(sh);_rv,re,rb=resolver.bytes(rh);_cv,ce,cb=resolver.bytes(ch)

    outer=parse_resource(rb,'PS4');u10=(outer.get('unk10') or {}).get('class_hash');u18=(outer.get('unk18') or {}).get('class_hash')
    if (u10,u18)!=(RUNTIME_RIG_DISCRIMINATOR,RUNTIME_RIG_INFO):
        raise ValueError(f'{rh}: runtime-rig class pair {u10}->{u18} != {RUNTIME_RIG_DISCRIMINATOR}->{RUNTIME_RIG_INFO}')
    control=decode_control(cb,None,a.name);selected=selected_by_control(control)
    missing=[h for h in clips if h not in selected]
    if missing:raise ValueError(f'clips not selected by exact control {ch}: {missing}')

    sys.path.insert(0,str(a.parser_root.resolve()))
    from tag.game_version import Game_Version
    from tag_readers.read_skeleton import read_skeleton
    from tag_readers.read_rig import read_runtime_rig
    from tag_readers.read_animation import read_animation
    from animation_decoding.decode_animation import decode_animation
    from runtime_rig.rig_retarget import rig_retarget,calc_control_limit
    from animation_export.convert_animation_object_to_local import convert_obj_to_local

    ver=Game_Version.D1_ROI;sk=read_skeleton(io.BytesIO(sb),ver);rig=read_runtime_rig(io.BytesIO(rb),ver)
    node_count=len(sk.node_defs);control_count=len(rig.controls_relations);components=component_rows(rig.rig_components)
    if node_count<=0 or control_count<=0:raise ValueError('empty skeleton/runtime rig')

    input_sha=hashlib.sha256(a.input_glb.read_bytes()).hexdigest()
    g=GLTF2().load_binary(str(a.input_glb))
    if len(g.buffers)!=1:raise ValueError(f'expected one-buffer GLB, found {len(g.buffers)}')
    if not (0<=a.skin_index<len(g.skins)):raise ValueError(f'skin index {a.skin_index} outside {len(g.skins)} skins')
    skin=g.skins[a.skin_index];joints=list(skin.joints or [])
    if len(joints)!=node_count:raise ValueError(f'input skin joints {len(joints)} != retail skeleton nodes {node_count}')

    # Exact palette validation. The current player checkpoint stores both index/hash
    # on each joint node. Hash is authoritative; index prevents accidental reorder.
    palette=[]
    for i,(joint,nd) in enumerate(zip(joints,sk.node_defs)):
        if not (0<=int(joint)<len(g.nodes)):raise ValueError(f'skin joint node {joint} out of GLB node range')
        node=g.nodes[int(joint)];ex=node.extras if isinstance(node.extras,dict) else {}
        gi=node_extra_int(ex,'d1PublishedPlayerBoneIndex','d1BoneIndex')
        gh=node_extra_int(ex,'d1PublishedPlayerBoneHash','d1BoneHash')
        expected=int(nd.bone_hash)&0xffffffff
        if gi is None or gi!=i:raise ValueError(f'joint slot {i}: GLB bone index marker {gi!r} != {i}')
        if gh is None or (gh&0xffffffff)!=expected:
            raise ValueError(f'joint slot {i}: GLB bone hash {gh!r} != retail {expected:08X}')
        palette.append({'slot':i,'gltf_node':int(joint),'bone_hash':f'{expected:08X}','name':node.name})

    extras=g.extras if isinstance(g.extras,dict) else {}
    ident=extras.get('d1RetailPlayerSkeletonIdentity') if isinstance(extras,dict) else None
    if isinstance(ident,dict) and ident.get('tagHash') and norm(str(ident['tagHash']))!=sh:
        raise ValueError(f'input GLB pins retail skeleton {ident.get("tagHash")}, requested {sh}')

    blob=bytearray(g.binary_blob() or b'');orig_blob=len(blob);orig_counts={
        'nodes':len(g.nodes),'meshes':len(g.meshes),'skins':len(g.skins),'materials':len(g.materials),
        'animations':len(g.animations),'accessors':len(g.accessors),'buffer_views':len(g.bufferViews)}
    existing_names={x.name for x in g.animations if x.name}
    rows=[]
    for cliph in clips:
        _v,e,b=resolver.bytes(cliph);anim=read_animation_filebacked(read_animation,b,ver);hdr=anim.animation_header
        clip_components=component_rows(anim.runtime_rig_components);limit=int(calc_control_limit(rig,anim.runtime_rig_components))
        if clip_components!=components:raise ValueError(f'{cliph}: runtime component fingerprint mismatch')
        if int(hdr.node_count)!=node_count:raise ValueError(f'{cliph}: node count {hdr.node_count} != {node_count}')
        if int(hdr.rig_control_count)!=control_count:raise ValueError(f'{cliph}: rig controls {hdr.rig_control_count} != {control_count}')
        if limit!=control_count:raise ValueError(f'{cliph}: native control limit {limit} != {control_count}')
        decoded=decode_animation(anim);ret=rig_retarget(anim,decoded,sk,rig);local=convert_obj_to_local(anim,ret,sk)
        if len(decoded)!=control_count or len(ret)!=node_count or len(local)!=node_count:
            raise ValueError(f'{cliph}: control/node track domains {len(decoded)}/{len(ret)}/{len(local)} != {control_count}/{node_count}/{node_count}')

        samplers=[];channels=[];time_accessors={};path_counts={'translation':0,'rotation':0,'scale':0};frame_sets={k:set() for k in path_counts}
        for bi,track in enumerate(local):
            target_node=joints[bi]
            for path,values,kind in (('translation',track.translations,'VEC3'),('rotation',track.rotations,'VEC4'),('scale',track.scales,'VEC3')):
                arr=np.asarray(values,dtype='<f4')
                if arr.size==0:continue
                if arr.ndim!=2:arr=arr.reshape((-1,4 if kind=='VEC4' else 3))
                n=int(arr.shape[0]);frame_sets[path].add(n);path_counts[path]+=1
                if n not in time_accessors:
                    times=(np.arange(n,dtype='<f4')/float(a.fps)).astype('<f4')
                    time_accessors[n]=append_accessor(g,blob,times,accessor_type='SCALAR',with_minmax=True)
                vacc=append_accessor(g,blob,arr,accessor_type=kind)
                si=len(samplers);samplers.append(AnimationSampler(input=time_accessors[n],output=vacc,interpolation='LINEAR'))
                channels.append(AnimationChannel(sampler=si,target=AnimationChannelTarget(node=int(target_node),path=path)))
        state_rows=selected[cliph]
        state_label=next((x.get('state_name') for x in state_rows if x.get('state_name')),None)
        anim_name=f'D1_{cliph}' if not state_label else f'D1_{state_label}_{cliph}'
        if anim_name in existing_names:raise ValueError(f'duplicate animation name {anim_name}')
        existing_names.add(anim_name)
        g.animations.append(Animation(name=anim_name,samplers=samplers,channels=channels,extras={
            'd1Clip':cliph,'d1Skeleton':sh,'d1RuntimeRig':rh,'d1AnimationControl':ch,
            'd1FrameCount':int(hdr.frame_count),'d1Fps':float(a.fps),'d1SelectedByStates':state_rows,
            'd1DecodedDomain':'runtime_controls','d1DecodedTrackCount':len(decoded),
            'd1RetargetedDomain':'skeleton_nodes','d1RetargetedTrackCount':len(ret)}))
        rows.append({'clip_tag_hash':cliph,'entry_index':int(e['index']),'frame_count':int(hdr.frame_count),
                     'animation_name':anim_name,'selected_by_control_states':state_rows,
                     'decoded_track_count':len(decoded),'retargeted_track_count':len(ret),'local_track_count':len(local),
                     'channel_count':len(channels),'sampler_count':len(samplers),'shared_time_accessor_count':len(time_accessors),
                     'path_node_counts':path_counts,'path_frame_count_sets':{k:sorted(v) for k,v in frame_sets.items()}})

    extras=g.extras if isinstance(g.extras,dict) else {}
    extras['d1AnimationPolicy']='Exact retail control-selected animations appended; no motion/name inference. Existing skin/geometry/materials untouched.'
    extras['d1RetailAnimationLibrary']={
        'skeleton':sh,'runtimeRig':rh,'control':ch,'clipCount':len(rows),
        'clips':[{'clip':x['clip_tag_hash'],'name':x['animation_name'],'states':x['selected_by_control_states']} for x in rows],
        'decodedDomain':'runtime_controls','retargetedDomain':'skeleton_nodes'}
    g.extras=extras;g.buffers[0].byteLength=len(blob);g.set_binary_blob(bytes(blob))
    a.out.parent.mkdir(parents=True,exist_ok=True);g.save_binary(str(a.out));output_sha=hashlib.sha256(a.out.read_bytes()).hexdigest()

    final_counts={'nodes':len(g.nodes),'meshes':len(g.meshes),'skins':len(g.skins),'materials':len(g.materials),
                  'animations':len(g.animations),'accessors':len(g.accessors),'buffer_views':len(g.bufferViews)}
    for k in ('nodes','meshes','skins','materials'):
        if final_counts[k]!=orig_counts[k]:raise ValueError(f'non-destructive invariant changed {k}: {orig_counts[k]} -> {final_counts[k]}')
    rep={'schema':'d1_gltf_append_retail_animation_library/v1','input':str(a.input_glb),'input_sha256':input_sha,
         'output':str(a.out),'output_sha256':output_sha,'output_bytes':a.out.stat().st_size,
         'skeleton':{'tag_hash':sh,'entry_index':int(se['index']),'node_count':node_count},
         'runtime_rig':{'tag_hash':rh,'entry_index':int(re['index']),'control_count':control_count,'components':components},
         'control':{'tag_hash':ch,'entry_index':int(ce['index']),'animation_count':control['animation_list']['count'],
                    'state_count':control['state_table']['count'],'unique_selected_clip_count':len(selected)},
         'skin_index':a.skin_index,'skin_name':skin.name,'palette':palette,
         'original_counts':orig_counts,'final_counts':final_counts,'original_binary_bytes':orig_blob,'final_binary_bytes':len(blob),
         'appended_animation_count':len(rows),'animations':rows,
         'policy':'Input skin palette is hash/index matched against the exact retail skeleton. Geometry/material/skin/bind data are not modified. Only exact control-selected, runtime-component-matched, parser-retargeted local animation tracks are appended.'}
    a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(rep,indent=2)+'\n')
    print(json.dumps({k:rep[k] for k in ('output_sha256','output_bytes','skeleton','runtime_rig','control','original_counts','final_counts','appended_animation_count')},indent=2))
    return 0

if __name__=='__main__':raise SystemExit(main())
