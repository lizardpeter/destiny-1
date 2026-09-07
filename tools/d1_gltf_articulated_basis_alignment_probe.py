#!/usr/bin/env python3
"""Measure final-world mesh and skeleton dominant axes in a skinned D1 GLB.

This is intentionally independent of inverse-bind identity.  A mesh and skeleton can
cancel each other's basis error algebraically while still occupy different physical
axes in Blender.  The probe transforms actual POSITION accessors and joint origins
through the final node hierarchy, reports their bounds/spans, and compares dominant
axes.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
from d1_gltf_layer_merge import read_glb
from d1_gltf_skin_bind_identity_probe import accessor,globals_

AXES='XYZ'

def bounds(points):
    x=np.asarray(points,dtype=np.float64)
    if x.size==0: raise ValueError('empty point set')
    lo=x.min(axis=0); hi=x.max(axis=0); span=hi-lo; axis=AXES[int(np.argmax(span))]
    return {'min':[float(v) for v in lo],'max':[float(v) for v in hi],'span':[float(v) for v in span],'dominant_axis':axis}

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument('glb',type=Path); ap.add_argument('--model',required=True)
    ap.add_argument('--expect-mesh-axis',choices=list(AXES)); ap.add_argument('--expect-joint-axis',choices=list(AXES))
    ap.add_argument('--allow-mismatch',action='store_true'); ap.add_argument('-o','--output',type=Path,required=True); a=ap.parse_args()
    model=a.model.upper(); doc,bin_data=read_glb(a.glb); G=globals_(doc); nodes=doc.get('nodes',[])
    matches=[]
    for si,s in enumerate(doc.get('skins',[])):
        root=int(s['skeleton']); ex=nodes[root].get('extras') or {}
        if str(ex.get('d1Model','')).upper()==model: matches.append((si,s))
    if len(matches)!=1: raise ValueError(f'expected exactly one skin for {model}, found {len(matches)}')
    si,skin=matches[0]

    mesh_points=[]; mesh_nodes=[]; pos_accessors=set()
    for ni,n in enumerate(nodes):
        if n.get('mesh') is None or n.get('skin') is None or int(n['skin'])!=si: continue
        mesh_nodes.append(ni); M=G[ni]; mesh=doc['meshes'][int(n['mesh'])]
        for p in mesh.get('primitives',[]):
            ai=int((p.get('attributes') or {})['POSITION']); pos_accessors.add(ai); xyz=accessor(doc,bin_data,ai).astype(np.float64)
            hom=np.concatenate([xyz,np.ones((len(xyz),1),dtype=np.float64)],axis=1); mesh_points.append((M@hom.T).T[:,:3])
    if not mesh_points: raise ValueError('no skinned mesh POSITION data')
    mesh_b=bounds(np.concatenate(mesh_points,axis=0))
    joint_xyz=np.asarray([G[int(j)][:3,3] for j in skin['joints']],dtype=np.float64); joint_b=bounds(joint_xyz)

    violations=[]
    if a.expect_mesh_axis and mesh_b['dominant_axis']!=a.expect_mesh_axis: violations.append(f"mesh dominant axis {mesh_b['dominant_axis']} != {a.expect_mesh_axis}")
    if a.expect_joint_axis and joint_b['dominant_axis']!=a.expect_joint_axis: violations.append(f"joint dominant axis {joint_b['dominant_axis']} != {a.expect_joint_axis}")
    aligned=mesh_b['dominant_axis']==joint_b['dominant_axis']
    if not aligned and not a.allow_mismatch: violations.append(f"mesh/joint dominant axes differ: {mesh_b['dominant_axis']} vs {joint_b['dominant_axis']}")
    status='D1_GLTF_ARTICULATED_BASIS_ALIGNMENT_COMPLETE' if not violations else 'D1_GLTF_ARTICULATED_BASIS_ALIGNMENT_FAILED'
    out={'schema_version':1,'status':status,'glb':str(a.glb),'model':model,'skin_index':si,'skinned_mesh_node_count':len(mesh_nodes),
         'position_accessor_count':len(pos_accessors),'joint_count':len(skin['joints']),'mesh_bounds':mesh_b,'joint_bounds':joint_b,
         'dominant_axes_aligned':aligned,'allow_mismatch':bool(a.allow_mismatch),'violations':violations,
         'policy':'Final-world physical bounds only; does not infer correctness from inverseBindMatrix cancellation.'}
    a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2))
    return 0 if not violations else 2
if __name__=='__main__': raise SystemExit(main())
