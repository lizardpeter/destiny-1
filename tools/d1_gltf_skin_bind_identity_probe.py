#!/usr/bin/env python3
"""Prove glTF skin bind-pose matrix consistency for D1 articulated exports.

For every selected skinned mesh node and every joint, glTF bind pose should satisfy:

  inverse(mesh_global) @ joint_global @ inverseBindMatrix ~= identity

when the mesh node and skeleton root share the source placement transform and the
inverseBindMatrices are the source inverse object-space bind matrices.  This catches
double placement transforms, wrong joint hierarchy, wrong inverse-bind ordering, and
wrong MAT4 storage interpretation without depending on Blender.
"""
from __future__ import annotations
import argparse, json, math
from pathlib import Path
import numpy as np
from d1_gltf_layer_merge import read_glb

COMPONENT_DT={5126:np.dtype('<f4'),5123:np.dtype('<u2'),5125:np.dtype('<u4'),5121:np.dtype('u1')}
TYPE_N={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}

def node_local(n):
    if n.get('matrix') is not None:
        # glTF JSON matrix is a column-major flat list.
        return np.asarray(n['matrix'],dtype=np.float64).reshape((4,4),order='F')
    t=np.asarray(n.get('translation',[0,0,0]),dtype=np.float64);s=np.asarray(n.get('scale',[1,1,1]),dtype=np.float64);q=np.asarray(n.get('rotation',[0,0,0,1]),dtype=np.float64)
    x,y,z,w=q;R=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w),0],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w),0],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y),0],[0,0,0,1]],dtype=np.float64)
    M=R@np.diag([s[0],s[1],s[2],1.0]);M[:3,3]=t;return M

def parents(doc):
    p={}
    for i,n in enumerate(doc.get('nodes',[])):
        for c in n.get('children',[]) or []:
            if c in p:raise ValueError(f'node {c} has multiple parents {p[c]} and {i}')
            p[c]=i
    return p

def globals_(doc):
    ns=doc.get('nodes',[]);p=parents(doc);cache={}
    def one(i):
        if i in cache:return cache[i]
        L=node_local(ns[i]);cache[i]=one(p[i])@L if i in p else L;return cache[i]
    return [one(i) for i in range(len(ns))]

def accessor(doc,bin_data,ai):
    a=doc['accessors'][ai];bv=doc['bufferViews'][a['bufferView']];dt=COMPONENT_DT[a['componentType']];n=TYPE_N[a['type']];count=int(a['count']);off=int(bv.get('byteOffset',0))+int(a.get('byteOffset',0));stride=int(bv.get('byteStride',dt.itemsize*n));raw=memoryview(bin_data)
    if stride==dt.itemsize*n:
        x=np.frombuffer(raw,dtype=dt,count=count*n,offset=off).copy().reshape((count,n))
    else:
        x=np.empty((count,n),dtype=dt)
        for i in range(count):x[i]=np.frombuffer(raw,dtype=dt,count=n,offset=off+i*stride)
    if a['type']=='MAT4':return np.stack([row.reshape((4,4),order='F') for row in x.astype(np.float64)],axis=0)
    return x

def main():
    ap=argparse.ArgumentParser();ap.add_argument('glb',type=Path);ap.add_argument('--model',action='append',default=[]);ap.add_argument('--max-error',type=float,default=2e-5);ap.add_argument('-o','--output',type=Path,required=True);a=ap.parse_args()
    doc,b=read_glb(a.glb);G=globals_(doc);want={x.upper() for x in a.model};rows=[];worst=0.0;viol=[]
    skins=doc.get('skins',[]);ibms={}
    for si,s in enumerate(skins):
        mats=accessor(doc,b,s['inverseBindMatrices']);
        if len(mats)!=len(s['joints']):viol.append(f'skin {si}: IBM count {len(mats)} != joints {len(s["joints"])}')
        ibms[si]=mats
    for ni,n in enumerate(doc.get('nodes',[])):
        if n.get('skin') is None or n.get('mesh') is None:continue
        ex=n.get('extras') or {};model=str(ex.get('d1Model','')).upper()
        if want and model not in want:continue
        si=int(n['skin']);s=skins[si];mG=G[ni];invM=np.linalg.inv(mG);jr=[];mw=0.0
        for j,(ji,ibm) in enumerate(zip(s['joints'],ibms[si])):
            K=invM@G[int(ji)]@ibm;e=float(np.max(np.abs(K-np.eye(4))));mw=max(mw,e);worst=max(worst,e)
            if e>a.max_error:jr.append({'joint_ordinal':j,'joint_node':int(ji),'error':e,'matrix':K.tolist()})
        if jr:viol.append(f'node {ni} {n.get("name")}: {len(jr)} joints exceed {a.max_error}')
        rows.append({'node_index':ni,'node_name':n.get('name'),'model':model,'skin':si,'joint_count':len(s['joints']),'max_bind_identity_error':mw,'bad_joints':jr})
    out={'schema_version':1,'status':'D1_GLTF_SKIN_BIND_IDENTITY_COMPLETE' if not viol else 'D1_GLTF_SKIN_BIND_IDENTITY_FAILED','glb':str(a.glb),'models':sorted(want),'tested_skinned_mesh_nodes':len(rows),'skin_count':len(skins),'max_allowed_error':a.max_error,'max_observed_error':worst,'violations':viol,'nodes':rows,'policy':'Checks glTF bind-pose algebra directly from final node hierarchy and inverseBindMatrices. This is independent of Blender import behavior.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k] for k in ('status','tested_skinned_mesh_nodes','skin_count','max_allowed_error','max_observed_error','violations')},indent=2));return 0 if not viol else 2
if __name__=='__main__':raise SystemExit(main())
