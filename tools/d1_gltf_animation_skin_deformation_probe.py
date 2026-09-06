#!/usr/bin/env python3
"""Numerically evaluate final glTF skinned animation deformation without Blender.

This isolates whether an apparently exploded NPC is already mathematically exploded in
the GLB, or whether the remaining issue is Blender armature/import presentation.  For
selected animations it evaluates frame 0, midpoint and final frame, applies glTF skinning
exactly in mesh-local space, and compares the deformed model AABB to the bind AABB.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
from d1_gltf_layer_merge import read_glb
from d1_gltf_skin_bind_identity_probe import accessor,node_local,parents


def trs(t,r,s):
    t=np.asarray(t,dtype=np.float64);r=np.asarray(r,dtype=np.float64);s=np.asarray(s,dtype=np.float64);x,y,z,w=r
    R=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w),0],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w),0],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y),0],[0,0,0,1]],dtype=np.float64)
    M=R@np.diag([s[0],s[1],s[2],1.0]);M[:3,3]=t;return M

def globals_from_locals(doc,locals_):
    p=parents(doc);cache={}
    def one(i):
        if i in cache:return cache[i]
        cache[i]=one(p[i])@locals_[i] if i in p else locals_[i];return cache[i]
    return [one(i) for i in range(len(locals_))]

def animation_frame_locals(doc,b,anim,frame):
    locals_=[node_local(n) for n in doc.get('nodes',[])]
    # Preserve default components when a channel omits one path.
    comp={}
    for ch in anim.get('channels',[]):
        si=int(ch['sampler']);sam=anim['samplers'][si];vals=accessor(doc,b,int(sam['output']));node=int(ch['target']['node']);path=ch['target']['path'];idx=min(frame,len(vals)-1);comp.setdefault(node,{})[path]=vals[idx].astype(np.float64)
    for ni,c in comp.items():
        n=doc['nodes'][ni];t=c.get('translation',np.asarray(n.get('translation',[0,0,0]),dtype=np.float64));r=c.get('rotation',np.asarray(n.get('rotation',[0,0,0,1]),dtype=np.float64));s=c.get('scale',np.asarray(n.get('scale',[1,1,1]),dtype=np.float64));locals_[ni]=trs(t,r,s)
    return locals_

def skin_model_frame(doc,b,G,model,world_id):
    ns=doc.get('nodes',[]);skins=doc.get('skins',[]);meshes=doc.get('meshes',[]);pts=[];per=[]
    for ni,n in enumerate(ns):
        ex=n.get('extras') or {}
        if n.get('mesh') is None or n.get('skin') is None or str(ex.get('d1Model','')).upper()!=model or str(ex.get('d1WorldID','')).upper()!=world_id:continue
        si=int(n['skin']);skin=skins[si];joints=[int(x) for x in skin['joints']];ibms=accessor(doc,b,int(skin['inverseBindMatrices']));invM=np.linalg.inv(G[ni]);local_pts=[]
        for p in meshes[int(n['mesh'])].get('primitives',[]):
            a=p['attributes'];pos=accessor(doc,b,a['POSITION']).astype(np.float64);ji=accessor(doc,b,a['JOINTS_0']).astype(np.int64);wt=accessor(doc,b,a['WEIGHTS_0']).astype(np.float64);h=np.column_stack([pos,np.ones(len(pos))]);out=np.zeros((len(pos),4),dtype=np.float64)
            for lane in range(4):
                for jordinal in np.unique(ji[:,lane]):
                    mask=(ji[:,lane]==jordinal)&(wt[:,lane]>0)
                    if not np.any(mask):continue
                    J=invM@G[joints[int(jordinal)]]@ibms[int(jordinal)];out[mask]+=((J@h[mask].T).T)*wt[mask,lane,None]
            local_pts.append(out[:,:3])
        if local_pts:
            q=np.concatenate(local_pts);pts.append(q);per.append({'node':ni,'name':n.get('name'),'min':q.min(axis=0).tolist(),'max':q.max(axis=0).tolist(),'extent':(q.max(axis=0)-q.min(axis=0)).tolist(),'vertex_count':len(q)})
    if not pts:raise ValueError(f'no skinned geometry for {model}/{world_id}')
    q=np.concatenate(pts);return {'min':q.min(axis=0),'max':q.max(axis=0),'extent':q.max(axis=0)-q.min(axis=0),'vertex_count':len(q),'nodes':per}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('glb',type=Path);ap.add_argument('--model',required=True);ap.add_argument('-o','--output',type=Path,required=True);a=ap.parse_args();model=a.model.upper();doc,b=read_glb(a.glb)
    animations=[x for x in doc.get('animations',[]) if str((x.get('extras') or {}).get('d1Model','')).upper()==model]
    if not animations:raise SystemExit(f'no animations for {model}')
    defaults=[node_local(n) for n in doc['nodes']];G0=globals_from_locals(doc,defaults);rows=[]
    for ai,anim in enumerate(doc.get('animations',[])):
        ex=anim.get('extras') or {}
        if str(ex.get('d1Model','')).upper()!=model:continue
        wid=str(ex.get('d1WorldID','')).upper();frames=int(ex.get('d1FrameCount',1));bind=skin_model_frame(doc,b,G0,model,wid);base_extent=bind['extent'];base_diag=float(np.linalg.norm(base_extent));frs=sorted(set([0,max(0,(frames-1)//2),max(0,frames-1)]));samples=[]
        for fi in frs:
            L=animation_frame_locals(doc,b,anim,fi);G=globals_from_locals(doc,L);s=skin_model_frame(doc,b,G,model,wid);diag=float(np.linalg.norm(s['extent']));samples.append({'frame':fi,'bounds':[s['min'].tolist(),s['max'].tolist()],'extent':s['extent'].tolist(),'diagonal':diag,'diagonal_ratio_to_bind':diag/base_diag if base_diag else None,'nodes':s['nodes']})
        rows.append({'animation_index':ai,'name':anim.get('name'),'world_id':wid,'clip':ex.get('d1OwnerSelectedClip') or ex.get('d1AnimationClip'),'frame_count':frames,'bind_bounds':[bind['min'].tolist(),bind['max'].tolist()],'bind_extent':base_extent.tolist(),'bind_diagonal':base_diag,'samples':samples})
    ratios=[s['diagonal_ratio_to_bind'] for r in rows for s in r['samples'] if s['diagonal_ratio_to_bind'] is not None]
    out={'schema_version':1,'status':'D1_GLTF_ANIMATION_SKIN_DEFORMATION_DIAGNOSTIC_COMPLETE','model':model,'animation_count':len(rows),'max_sample_diagonal_ratio_to_bind':max(ratios) if ratios else None,'animations':rows,'policy':'CPU evaluates the final GLB animation channels and glTF skin equation directly. Large expansion here means the GLB itself deforms incorrectly; normal bounds here with a broken Blender view points to import/action/armature presentation.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'status':out['status'],'model':model,'animation_count':len(rows),'max_sample_diagonal_ratio_to_bind':out['max_sample_diagonal_ratio_to_bind'],'animations':[{'name':r['name'],'world_id':r['world_id'],'clip':r['clip'],'frame_count':r['frame_count'],'bind_diagonal':r['bind_diagonal'],'samples':[{'frame':s['frame'],'diagonal':s['diagonal'],'ratio':s['diagonal_ratio_to_bind']} for s in r['samples']]} for r in rows]},indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
