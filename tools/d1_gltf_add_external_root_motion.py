#!/usr/bin/env python3
"""Bake one source skeleton joint's relative world motion onto a target GLB root.

This is for D1 assets whose visible object has its own internal rig but whose broader
first-person/world motion comes from a separate parent skeleton/socket. The target GLB
is left structurally intact below a new root. The source joint motion is evaluated
through its complete animated ancestor chain and rebased to the source animation's
first sample, so no character-space bind offset is imposed on the standalone asset.

No motion is synthesized: the output root animation is an exact TRS decomposition of
  source_world(t) @ inverse(source_world(t0)).
"""
from __future__ import annotations
import argparse,json,math
from pathlib import Path
import numpy as np
from d1_gltf_bake_rigid_weapon_motion import (
    read_glb,write_glb,animation_tracks,source_chain,eval_world,
    append_f32_accessor,trs_matrix,decompose,qnorm,
)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('target',type=Path)
    ap.add_argument('motion_source',type=Path)
    ap.add_argument('--source-node',type=int,required=True)
    ap.add_argument('--source-animation')
    ap.add_argument('--animation-name',required=True)
    ap.add_argument('--root-name',default='ExternalMotionRoot')
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--report',type=Path,required=True)
    a=ap.parse_args()

    tj,tb=read_glb(a.target); sj,sb=read_glb(a.motion_source)
    if a.source_node<0 or a.source_node>=len(sj.get('nodes',[])): raise ValueError('source node out of range')
    sanims=sj.get('animations',[])
    if a.source_animation is None:
        if len(sanims)!=1: raise ValueError('motion source has !=1 animations; specify --source-animation')
        sa=sanims[0]
    else:
        matches=[x for x in sanims if x.get('name')==a.source_animation]
        if len(matches)!=1: raise ValueError(f'animation name {a.source_animation!r} matched {len(matches)}')
        sa=matches[0]
    tracks,times=animation_tracks(sj,sb,sa)
    if len(times)<1: raise ValueError('source animation has no TRS samples')
    chain=source_chain(sj,a.source_node)
    mats=[]
    for t in times:
        tt,qq,ss=eval_world(sj,chain,tracks,float(t)); mats.append(trs_matrix(tt,qq,ss))
    inv0=np.linalg.inv(mats[0])
    T=[];Q=[];S=[]
    for m in mats:
        # World-space delta from source bind/sample-0 pose.
        d=m@inv0
        tt,qq,ss=decompose(d);T.append(tt);Q.append(qq);S.append(ss)
    T=np.asarray(T,dtype=np.float32);Q=np.asarray(Q,dtype=np.float32);S=np.asarray(S,dtype=np.float32)
    # Quaternion sign continuity is representation-only and does not alter rotations.
    for i in range(1,len(Q)):
        if float(np.dot(Q[i-1],Q[i]))<0:Q[i]*=-1
    assert np.linalg.norm(T[0])<1e-5
    assert abs(abs(float(Q[0,3]))-1.0)<1e-4
    assert np.linalg.norm(S[0]-1.0)<1e-5

    scene_i=int(tj.get('scene',0)); old_roots=list(tj['scenes'][scene_i].get('nodes',[]))
    root_i=len(tj.setdefault('nodes',[]))
    tj['nodes'].append({'name':a.root_name,'children':old_roots,
                        'extras':{'d1ExternalMotionSource':str(a.motion_source.name),
                                  'sourceAnimation':sa.get('name'),'sourceNode':a.source_node,
                                  'sourceNodeName':sj['nodes'][a.source_node].get('name'),
                                  'method':'source_world(t) * inverse(source_world(t0)); exact evaluated TRS'}})
    tj['scenes'][scene_i]['nodes']=[root_i]

    ti=append_f32_accessor(tj,tb,np.asarray(times,dtype=np.float32).reshape(-1,1),'SCALAR',minmax=True)
    ta=append_f32_accessor(tj,tb,T,'VEC3');qa=append_f32_accessor(tj,tb,Q,'VEC4');sa_i=append_f32_accessor(tj,tb,S,'VEC3')
    anim={'name':a.animation_name,'samplers':[
              {'input':ti,'output':ta,'interpolation':'LINEAR'},
              {'input':ti,'output':qa,'interpolation':'LINEAR'},
              {'input':ti,'output':sa_i,'interpolation':'LINEAR'}],
          'channels':[
              {'sampler':0,'target':{'node':root_i,'path':'translation'}},
              {'sampler':1,'target':{'node':root_i,'path':'rotation'}},
              {'sampler':2,'target':{'node':root_i,'path':'scale'}}],
          'extras':{'d1SourceAnimation':sa.get('name'),'d1SourceJointNode':a.source_node,
                    'd1SourceJointName':sj['nodes'][a.source_node].get('name'),'rebasedToFirstSample':True}}
    tj.setdefault('animations',[]).append(anim)
    tj.setdefault('extras',{})['d1ExternalRootMotion']={'rootNode':root_i,'animation':a.animation_name,
        'sourceAnimation':sa.get('name'),'sourceNode':a.source_node,'sourceNodeName':sj['nodes'][a.source_node].get('name'),
        'targetOriginalRoots':old_roots,'motionInvented':False}
    write_glb(a.out,tj,tb)

    q0=Q[0]/max(float(np.linalg.norm(Q[0])),1e-12); qn=Q/np.maximum(np.linalg.norm(Q,axis=1,keepdims=True),1e-12)
    rd=np.degrees(2*np.arccos(np.clip(np.abs(qn@q0),0,1)))
    report={'output':str(a.out),'output_bytes':a.out.stat().st_size,'root_node':root_i,'old_scene_roots':old_roots,
            'source_node':a.source_node,'source_node_name':sj['nodes'][a.source_node].get('name'),'source_chain':chain,
            'source_animation':sa.get('name'),'output_animation':a.animation_name,'sample_count':len(times),
            'duration_s':float(times[-1]-times[0]),'max_translation':float(np.linalg.norm(T,axis=1).max()),
            'max_rotation_deg':float(rd.max()),'max_scale_delta':float(np.linalg.norm(S-1.0,axis=1).max()),
            'policy':'Exact source-joint world delta rebased to first sample; no synthesized motion.'}
    a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
