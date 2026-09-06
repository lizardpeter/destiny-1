#!/usr/bin/env python3
"""Measure bind-space spatial alignment between skinned geometry and skeleton joints.

A glTF can satisfy the formal inverse-bind identity while still deforming badly if the
source geometry and skeleton were placed in different model coordinate spaces, or if
vertex joint indices address the wrong bones.  This probe uses the final GLB itself:

* aggregates POSITION vertices by JOINTS_0/WEIGHTS_0 influence for one model;
* expresses joint bind positions in skeleton-root local/model space;
* compares each influenced joint with the weighted centroid and AABB of vertices
  assigned to it;
* reports skeleton bounds versus geometry bounds and per-joint distances.

It is diagnostic: closeness is not itself proof of semantic joint identity.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
from d1_gltf_layer_merge import read_glb
from d1_gltf_skin_bind_identity_probe import accessor,globals_,node_local


def main():
    ap=argparse.ArgumentParser();ap.add_argument('glb',type=Path);ap.add_argument('--model',required=True);ap.add_argument('-o','--output',type=Path,required=True);a=ap.parse_args()
    model=a.model.upper();doc,b=read_glb(a.glb);G=globals_(doc);nodes=doc.get('nodes',[]);skins=doc.get('skins',[])
    mesh_nodes=[(i,n) for i,n in enumerate(nodes) if n.get('mesh') is not None and n.get('skin') is not None and str((n.get('extras') or {}).get('d1Model','')).upper()==model]
    if not mesh_nodes:raise SystemExit(f'no skinned nodes for {model}')
    # One placement is enough because model meshes are shared and every placement has the same skeleton bind.
    first_skin=int(mesh_nodes[0][1]['skin']);skin=skins[first_skin];root=int(skin['skeleton']);root_inv=np.linalg.inv(G[root]);joints=[int(x) for x in skin['joints']]
    joint_pos=np.stack([(root_inv@G[j])[:3,3] for j in joints],axis=0)
    # Avoid replaying the same shared mesh once per placement.
    unique_meshes={int(n['mesh']):n for _,n in mesh_nodes}
    sumw=np.zeros(len(joints),dtype=np.float64);sumpos=np.zeros((len(joints),3),dtype=np.float64);mins=np.full((len(joints),3),np.inf);maxs=np.full((len(joints),3),-np.inf);refs=np.zeros(len(joints),dtype=np.int64)
    geom_min=np.full(3,np.inf);geom_max=np.full(3,-np.inf);vertex_total=0
    for mi,n in sorted(unique_meshes.items()):
        mesh=doc['meshes'][mi]
        for p in mesh.get('primitives',[]):
            attrs=p['attributes'];pos=accessor(doc,b,attrs['POSITION']).astype(np.float64);ji=accessor(doc,b,attrs['JOINTS_0']).astype(np.int64);wt=accessor(doc,b,attrs['WEIGHTS_0']).astype(np.float64)
            vertex_total+=len(pos);geom_min=np.minimum(geom_min,pos.min(axis=0));geom_max=np.maximum(geom_max,pos.max(axis=0))
            for lane in range(4):
                for vi,(j,w) in enumerate(zip(ji[:,lane],wt[:,lane])):
                    if w<=0:continue
                    if not 0<=j<len(joints):raise SystemExit(f'mesh {mi}: joint ordinal {j} OOB')
                    sumw[j]+=w;sumpos[j]+=pos[vi]*w;refs[j]+=1;mins[j]=np.minimum(mins[j],pos[vi]);maxs[j]=np.maximum(maxs[j],pos[vi])
    rows=[];dist=[]
    for j in range(len(joints)):
        n=nodes[joints[j]];ex=n.get('extras') or {};jp=joint_pos[j]
        if sumw[j]>0:
            c=sumpos[j]/sumw[j];d=float(np.linalg.norm(c-jp));dist.append(d);inside=bool(np.all(jp>=mins[j]) and np.all(jp<=maxs[j]));aabb_distance=float(np.linalg.norm(np.maximum(np.maximum(mins[j]-jp,jp-maxs[j]),0.0)))
            row={'joint_ordinal':j,'joint_node':joints[j],'name':n.get('name'),'bone_hash':ex.get('d1BoneHash'),'joint_position':jp.tolist(),'weight_sum':float(sumw[j]),'influence_references':int(refs[j]),'weighted_vertex_centroid':c.tolist(),'centroid_distance':d,'influenced_vertex_aabb':[mins[j].tolist(),maxs[j].tolist()],'joint_inside_influenced_aabb':inside,'distance_to_influenced_aabb':aabb_distance}
        else:
            row={'joint_ordinal':j,'joint_node':joints[j],'name':n.get('name'),'bone_hash':ex.get('d1BoneHash'),'joint_position':jp.tolist(),'weight_sum':0.0,'influence_references':0}
        rows.append(row)
    skmin=joint_pos.min(axis=0);skmax=joint_pos.max(axis=0)
    out={'schema_version':1,'status':'D1_GLTF_SKIN_GEOMETRY_ALIGNMENT_DIAGNOSTIC_COMPLETE','model':model,'tested_mesh_variants':len(unique_meshes),'placement_mesh_nodes':len(mesh_nodes),'vertex_instances_aggregated':vertex_total,'joint_count':len(joints),'geometry_bounds':[geom_min.tolist(),geom_max.tolist()],'skeleton_joint_bounds':[skmin.tolist(),skmax.tolist()],'geometry_extent':(geom_max-geom_min).tolist(),'skeleton_extent':(skmax-skmin).tolist(),'influenced_joint_count':sum(x['weight_sum']>0 for x in rows),'centroid_distance_min':None if not dist else min(dist),'centroid_distance_median':None if not dist else float(np.median(dist)),'centroid_distance_max':None if not dist else max(dist),'joints':rows,'policy':'Spatial diagnostic only. It detects coordinate-space or gross joint-index mismatch but does not infer semantic bone names from proximity.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k] for k in ('status','tested_mesh_variants','placement_mesh_nodes','vertex_instances_aggregated','joint_count','geometry_bounds','skeleton_joint_bounds','geometry_extent','skeleton_extent','influenced_joint_count','centroid_distance_min','centroid_distance_median','centroid_distance_max')},indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
