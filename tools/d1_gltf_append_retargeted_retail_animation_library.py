#!/usr/bin/env python3
"""Append every exact control-selected D1 animation through the native retarget path.

This is the cross-rig production companion to d1_gltf_append_retail_animation_library.py.
It preserves the same fail-closed skin-palette and source-ownership rules, but does
NOT require a source clip to have the target skeleton/rig dimensions. Destiny 1's
retail runtime explicitly supports this case; compatibility is established by
executing the pinned native-equivalent path:

    decode_animation -> calc_control_limit -> rig_retarget -> convert_obj_to_local

Only FileHashes actually selected by decoded 80802C0E state records are promoted to
actions. The larger serialized animation-list bank is retained in the report but is
not silently exported as an actor action. No idle/default/startup state is invented.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import sys
from pathlib import Path

import numpy as np
from pygltflib import GLTF2, Animation, AnimationSampler, AnimationChannel, AnimationChannelTarget

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))

from d1_gltf_append_retail_animation_library import (
    norm, append_accessor, read_animation_filebacked, selected_by_control,
)
from d1_animation_control_state_map import decode_control
from d1_animation_retarget_probe import component_rows, common_component_prefix
from d1_character_family_census import RUNTIME_RIG_DISCRIMINATOR, RUNTIME_RIG_INFO
from d1_entity_resource_probe import parse_resource
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_model_tgxm_signature_match import LazyExactHashResolver
from d1_split_tar_extract import SplitHttpTar


def node_extra_int(extras:dict|None,*keys:str)->int|None:
    """Read integer GLB provenance markers without losing their exact encoding.

    Older player checkpoints used numeric JSON values while the spawned-actor skin
    binder deliberately stores 32-bit bone hashes as zero-padded hexadecimal strings
    such as ``E5685C1A``. Both encodings are exact; accept either and fail closed on
    anything else.
    """
    if not isinstance(extras,dict):return None
    for k in keys:
        if k not in extras:continue
        v=extras[k]
        try:
            if isinstance(v,str):
                s=v.strip()
                try:return int(s,0)
                except ValueError:return int(s,16)
            return int(v)
        except Exception:
            return None
    return None


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('input_glb',type=Path)
    ap.add_argument('--member-catalog',type=Path,action='append',required=True)
    ap.add_argument('--base-url',default='https://crypt.cohae.dev/destiny/ps4/packages/latest')
    ap.add_argument('--part-count',type=int,default=10)
    ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('--parser-root',type=Path,required=True)
    ap.add_argument('--skeleton',required=True)
    ap.add_argument('--rig',required=True)
    ap.add_argument('--control',required=True)
    ap.add_argument('--clip',action='append',default=[],help='Optional exact selected subset; omit to export every selector-selected unique clip')
    ap.add_argument('--name',action='append',default=[],help='Optional exact StringHash preimages only')
    ap.add_argument('--fps',type=float,default=30.0)
    ap.add_argument('--skin-index',type=int,default=0)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--report',type=Path,required=True)
    a=ap.parse_args()

    sh,rh,ch=map(norm,(a.skeleton,a.rig,a.control))
    cats=load_catalogs(a.member_catalog)
    arc=SplitHttpTar([f"{a.base_url.rstrip('/')}/packages.tar.{i:03d}" for i in range(1,a.part_count+1)],retries=6,timeout=90)
    resolver=LazyExactHashResolver(arc,cats,a.runtime)
    _sv,se,sb=resolver.bytes(sh);_rv,re,rb=resolver.bytes(rh);_cv,ce,cb=resolver.bytes(ch)

    outer=parse_resource(rb,'PS4')
    u10=(outer.get('unk10') or {}).get('class_hash');u18=(outer.get('unk18') or {}).get('class_hash')
    if (u10,u18)!=(RUNTIME_RIG_DISCRIMINATOR,RUNTIME_RIG_INFO):
        raise ValueError(f'{rh}: runtime-rig class pair {u10}->{u18} != {RUNTIME_RIG_DISCRIMINATOR}->{RUNTIME_RIG_INFO}')

    control=decode_control(cb,None,a.name)
    selected=selected_by_control(control)
    selected_hashes=sorted(selected)
    bank_hashes=[norm(x['tag_hash']) for x in control['animation_list']['items']]
    if a.clip:
        clips=list(dict.fromkeys(norm(x) for x in a.clip))
        missing=[h for h in clips if h not in selected]
        if missing:raise ValueError(f'clips not selected by exact control {ch}: {missing}')
    else:
        clips=selected_hashes
    if not clips:raise ValueError(f'{ch}: no selector-selected clips')

    sys.path.insert(0,str(a.parser_root.resolve()))
    from tag.game_version import Game_Version
    from tag_readers.read_skeleton import read_skeleton
    from tag_readers.read_rig import read_runtime_rig
    from tag_readers.read_animation import read_animation
    from animation_decoding.decode_animation import decode_animation
    from runtime_rig.rig_retarget import rig_retarget,calc_control_limit
    from animation_export.convert_animation_object_to_local import convert_obj_to_local

    ver=Game_Version.D1_ROI
    sk=read_skeleton(io.BytesIO(sb),ver);rig=read_runtime_rig(io.BytesIO(rb),ver)
    node_count=len(sk.node_defs);control_count=len(rig.controls_relations)
    target_components=component_rows(rig.rig_components)
    if node_count<=0 or control_count<=0:raise ValueError('empty skeleton/runtime rig')

    input_sha=hashlib.sha256(a.input_glb.read_bytes()).hexdigest()
    g=GLTF2().load_binary(str(a.input_glb))
    if len(g.buffers)!=1:raise ValueError(f'expected one-buffer GLB, found {len(g.buffers)}')
    if not (0<=a.skin_index<len(g.skins or [])):raise ValueError(f'skin index {a.skin_index} outside {len(g.skins or [])} skins')
    skin=g.skins[a.skin_index];joints=list(skin.joints or [])
    if len(joints)!=node_count:raise ValueError(f'input skin joints {len(joints)} != retail skeleton nodes {node_count}')

    palette=[]
    for i,(joint,nd) in enumerate(zip(joints,sk.node_defs)):
        if not (0<=int(joint)<len(g.nodes)):raise ValueError(f'skin joint node {joint} out of GLB node range')
        node=g.nodes[int(joint)];ex=node.extras if isinstance(node.extras,dict) else {}
        gi=node_extra_int(ex,'d1PublishedPlayerBoneIndex','d1BoneIndex')
        gh=node_extra_int(ex,'d1PublishedPlayerBoneHash','d1BoneHash')
        expected=int(nd.bone_hash)&0xffffffff
        if gi is None or gi!=i:raise ValueError(f'joint slot {i}: GLB bone index marker {gi!r} != {i}')
        if gh is None or (gh&0xffffffff)!=expected:raise ValueError(f'joint slot {i}: GLB bone hash {gh!r} != retail {expected:08X}')
        palette.append({'slot':i,'gltf_node':int(joint),'bone_hash':f'{expected:08X}','name':node.name})

    extras=g.extras if isinstance(g.extras,dict) else {}
    ident=extras.get('d1RetailPlayerSkeletonIdentity') if isinstance(extras,dict) else None
    if isinstance(ident,dict) and ident.get('tagHash') and norm(str(ident['tagHash']))!=sh:
        raise ValueError(f'input GLB pins retail skeleton {ident.get("tagHash")}, requested {sh}')

    blob=bytearray(g.binary_blob() or b'');orig_blob=len(blob)
    orig_counts={'nodes':len(g.nodes),'meshes':len(g.meshes),'skins':len(g.skins),'materials':len(g.materials),
                 'animations':len(g.animations or []),'accessors':len(g.accessors),'buffer_views':len(g.bufferViews)}
    if g.animations is None:g.animations=[]
    existing_names={x.name for x in g.animations if x.name}
    rows=[]

    for ni,cliph in enumerate(clips,1):
        _v,e,b=resolver.bytes(cliph)
        anim=read_animation_filebacked(read_animation,b,ver);hdr=anim.animation_header
        source_components=component_rows(anim.runtime_rig_components)
        prefix=common_component_prefix(target_components,source_components)
        limit=int(calc_control_limit(rig,anim.runtime_rig_components))
        if limit!=int(prefix['control_limit']):
            raise ValueError(f'{cliph}: native control limit {limit} != structural prefix {prefix["control_limit"]}')
        decoded=decode_animation(anim)
        ret=rig_retarget(anim,decoded,sk,rig)
        local=convert_obj_to_local(anim,ret,sk)
        if len(ret)!=node_count or len(local)!=node_count:
            raise ValueError(f'{cliph}: retarget/local node domains {len(ret)}/{len(local)} != target {node_count}')

        samplers=[];channels=[];time_accessors={}
        path_counts={'translation':0,'rotation':0,'scale':0};frame_sets={k:set() for k in path_counts}
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
        source_dims_exact=(int(hdr.node_count)==node_count and int(hdr.rig_control_count)==control_count and source_components==target_components)
        g.animations.append(Animation(name=anim_name,samplers=samplers,channels=channels,extras={
            'd1Clip':cliph,'d1Skeleton':sh,'d1RuntimeRig':rh,'d1AnimationControl':ch,
            'd1FrameCount':int(hdr.frame_count),'d1Fps':float(a.fps),'d1SelectedByStates':state_rows,
            'd1SourceNodeCount':int(hdr.node_count),'d1SourceRigControlCount':int(hdr.rig_control_count),
            'd1TargetNodeCount':node_count,'d1TargetRigControlCount':control_count,
            'd1NativeControlLimit':limit,'d1SourceDimensionsExact':source_dims_exact,
            'd1DecodedTrackCount':len(decoded),'d1RetargetedTrackCount':len(ret),
        }))
        rows.append({'clip_tag_hash':cliph,'entry_index':int(e['index']),'frame_count':int(hdr.frame_count),
                     'animation_name':anim_name,'selected_by_control_states':state_rows,
                     'source_node_count':int(hdr.node_count),'source_rig_control_count':int(hdr.rig_control_count),
                     'target_node_count':node_count,'target_rig_control_count':control_count,
                     'source_dimensions_exact':source_dims_exact,'native_control_limit':limit,'component_prefix':prefix,
                     'decoded_track_count':len(decoded),'retargeted_track_count':len(ret),'local_track_count':len(local),
                     'channel_count':len(channels),'sampler_count':len(samplers),'shared_time_accessor_count':len(time_accessors),
                     'path_node_counts':path_counts,'path_frame_count_sets':{k:sorted(v) for k,v in frame_sets.items()}})
        print('APPENDED',ni,'/',len(clips),cliph,'FRAMES',int(hdr.frame_count),'SOURCE',int(hdr.node_count),int(hdr.rig_control_count),'TARGET',node_count,control_count,'LIMIT',limit,'EXACT_DIMS',source_dims_exact,flush=True)

    extras=g.extras if isinstance(g.extras,dict) else {}
    extras['d1AnimationPolicy']='Only exact control-state-selected clips are actions. Cross-rig clips are passed through the pinned D1 native retarget/localization sequence. No default action or state-name inference.'
    extras['d1RetailAnimationLibrary']={
        'skeleton':sh,'runtimeRig':rh,'control':ch,'clipCount':len(rows),
        'animationListBankCount':len(bank_hashes),'selectorSelectedUniqueClipCount':len(selected_hashes),
        'unusedAnimationListBankHashes':sorted(set(bank_hashes)-set(selected_hashes)),
        'clips':[{'clip':x['clip_tag_hash'],'name':x['animation_name'],'states':x['selected_by_control_states']} for x in rows],
        'retargetMode':'decode_animation -> calc_control_limit -> rig_retarget -> convert_obj_to_local',
    }
    g.extras=extras;g.buffers[0].byteLength=len(blob);g.set_binary_blob(bytes(blob))
    a.out.parent.mkdir(parents=True,exist_ok=True);g.save_binary(str(a.out))
    output_sha=hashlib.sha256(a.out.read_bytes()).hexdigest()

    final_counts={'nodes':len(g.nodes),'meshes':len(g.meshes),'skins':len(g.skins),'materials':len(g.materials),
                  'animations':len(g.animations or []),'accessors':len(g.accessors),'buffer_views':len(g.bufferViews)}
    for k in ('nodes','meshes','skins','materials'):
        if final_counts[k]!=orig_counts[k]:raise ValueError(f'non-destructive invariant changed {k}: {orig_counts[k]} -> {final_counts[k]}')
    rep={'schema':'d1_gltf_append_retargeted_retail_animation_library/v1','status':'D1_GLTF_RETARGETED_RETAIL_ANIMATION_LIBRARY_APPENDED',
         'input':str(a.input_glb),'input_sha256':input_sha,'output':str(a.out),'output_sha256':output_sha,'output_bytes':a.out.stat().st_size,
         'skeleton':{'tag_hash':sh,'entry_index':int(se['index']),'node_count':node_count},
         'runtime_rig':{'tag_hash':rh,'entry_index':int(re['index']),'control_count':control_count,'components':target_components},
         'control':{'tag_hash':ch,'entry_index':int(ce['index']),'animation_list_bank_count':len(bank_hashes),
                    'state_count':control['state_table']['count'],'selector_selected_unique_clip_count':len(selected_hashes),
                    'unused_animation_list_bank_hashes':sorted(set(bank_hashes)-set(selected_hashes))},
         'requested_clip_mode':'explicit_subset' if a.clip else 'all_selector_selected_unique',
         'skin_index':a.skin_index,'skin_name':skin.name,'palette':palette,
         'original_counts':orig_counts,'final_counts':final_counts,'original_binary_bytes':orig_blob,'final_binary_bytes':len(blob),
         'appended_animation_count':len(rows),'exact_dimension_animation_count':sum(1 for x in rows if x['source_dimensions_exact']),
         'native_retarget_required_animation_count':sum(1 for x in rows if not x['source_dimensions_exact']),
         'animations':rows,
         'policy':'Input skin palette is exact hash/index matched to the retail target skeleton. Geometry/material/skin/bind data are immutable. Only exact control-state-selected FileHashes are appended, and every clip must execute successfully through the pinned D1 retarget/localization path.'}
    a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(rep,indent=2)+'\n')
    print(json.dumps({k:rep[k] for k in ('status','output_sha256','output_bytes','skeleton','runtime_rig','control','appended_animation_count','exact_dimension_animation_count','native_retarget_required_animation_count')},indent=2))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
