#!/usr/bin/env python3
"""Undo tiger-animation-parser's internal Tiger->Three.js basis on Tower skins.

The pinned parser intentionally converts raw Tiger/D1 coordinates

    [x, y, z] -> [y, z, x]

inside read_skeleton.transform_to_glm_mat4 and rig_retarget.  That is appropriate for
its standalone Three.js/glTF animation export, but the Tower articulated model geometry
remains in native D1 model space and its placement node already applies the separately
proven D1 Z-up -> glTF Y-up world adapter.  Reusing parser-space bind/animation data
under that placement therefore double-converts the skeleton basis.

This lossless adapter converts only the articulated skin domain back to native D1 model
space:
  * every skin joint local TRS;
  * every inverseBindMatrix;
  * every selected animation translation/rotation/scale output accessor.

Mesh positions, JOINTS_0/WEIGHTS_0, placement matrices, textures/materials, animation
times, topology and source action identity are unchanged.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation
from d1_gltf_layer_merge import read_glb,write_glb
from d1_gltf_skin_bind_identity_probe import accessor,node_local

# parser p = P @ raw, where p=[raw_y,raw_z,raw_x]
P=np.array([[0.,1.,0.,0.],[0.,0.,1.,0.],[1.,0.,0.,0.],[0.,0.,0.,1.]],dtype=np.float64)
PI=P.T
TARGET_MODELS={'80CA0CFC','80C7AF4C','80C7AE59'}

def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for x in iter(lambda:f.read(1<<20),b''):h.update(x)
    return h.hexdigest()

def decompose(M):
    t=M[:3,3].copy();A=M[:3,:3].copy();s=np.linalg.norm(A,axis=0)
    if np.any(s<1e-12):raise ValueError('zero scale during basis conversion')
    Rm=A/s
    if np.linalg.det(Rm)<0:
        k=int(np.argmax(s));s[k]*=-1;Rm[:,k]*=-1
    q=Rotation.from_matrix(Rm).as_quat()
    return t,q,s

def set_accessor(doc,blob,ai,data):
    a=doc['accessors'][ai];bv=doc['bufferViews'][a['bufferView']]
    if a['componentType']!=5126:raise ValueError(f'accessor {ai}: non-FLOAT output')
    n={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}[a['type']];x=np.asarray(data,dtype='<f4')
    if a['type']=='MAT4':flat=np.stack([m.reshape(16,order='F') for m in x],axis=0)
    else:flat=x.reshape((int(a['count']),n))
    if flat.shape!=(int(a['count']),n):raise ValueError(f'accessor {ai}: shape {flat.shape}')
    base=int(bv.get('byteOffset',0))+int(a.get('byteOffset',0));stride=int(bv.get('byteStride',4*n));raw=flat.tobytes(order='C')
    if stride==4*n:blob[base:base+len(raw)]=raw
    else:
        rowbytes=4*n
        for i,row in enumerate(flat):blob[base+i*stride:base+i*stride+rowbytes]=row.astype('<f4').tobytes()

def basis_matrix(M):return PI@M@P

def transform_node(n):
    M=node_local(n);R=basis_matrix(M);t,q,s=decompose(R);n.pop('matrix',None);n['translation']=[float(x) for x in t];n['rotation']=[float(x) for x in q];n['scale']=[float(x) for x in s]

def main():
    ap=argparse.ArgumentParser();ap.add_argument('input_glb',type=Path);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--report',type=Path,required=True);a=ap.parse_args();doc,bb=read_glb(a.input_glb);blob=bytearray(bb);nodes=doc.get('nodes',[]);skins=doc.get('skins',[])
    target_skins=[];joint_nodes=set();ibm_accessors=set();skin_rows=[]
    for si,s in enumerate(skins):
        root=int(s['skeleton']);ex=nodes[root].get('extras') or {};model=str(ex.get('d1Model','')).upper()
        if model not in TARGET_MODELS:continue
        target_skins.append(si);js=[int(x) for x in s['joints']];joint_nodes.update(js);ibm_accessors.add(int(s['inverseBindMatrices']));skin_rows.append({'skin_index':si,'model':model,'root':root,'joint_count':len(js),'inverse_bind_accessor':int(s['inverseBindMatrices'])})
    if len(target_skins)!=17:raise SystemExit(f'expected 17 E/F/G skins, found {len(target_skins)}')

    # Joint local bind nodes: parser basis -> raw D1 model basis.
    for ji in sorted(joint_nodes):transform_node(nodes[ji])

    # IBM mathematical matrices follow the same basis conjugation.
    for ai in sorted(ibm_accessors):
        mats=accessor(doc,bb,ai).astype(np.float64);new=np.stack([basis_matrix(m) for m in mats]);set_accessor(doc,blob,ai,new)

    # Animation output accessors can be shared by multiple placements of one clip.
    # Pure basis permutation lets each TRS component transform independently.
    transformed={};channel_rows=[]
    for ani,anim in enumerate(doc.get('animations',[])):
        ex=anim.get('extras') or {};model=str(ex.get('d1Model','')).upper()
        if model not in TARGET_MODELS:continue
        for ch in anim.get('channels',[]):
            node=int(ch['target']['node']);path=ch['target']['path'];sam=anim['samplers'][int(ch['sampler'])];ai=int(sam['output']);key=(ai,path)
            if key not in transformed:
                vals=accessor(doc,bytes(blob),ai).astype(np.float64)
                if path=='translation':new=vals[:,[2,0,1]]
                elif path=='scale':new=vals[:,[2,0,1]]
                elif path=='rotation':
                    new=[]
                    for q in vals:
                        M=np.eye(4);M[:3,:3]=Rotation.from_quat(q).as_matrix();Rm=basis_matrix(M)[:3,:3];new.append(Rotation.from_matrix(Rm).as_quat())
                    new=np.asarray(new,dtype=np.float64)
                else:raise ValueError(f'unsupported animation path {path}')
                set_accessor(doc,blob,ai,new);transformed[key]=True
            channel_rows.append({'animation_index':ani,'model':model,'target_node':node,'path':path,'output_accessor':ai})

    doc.setdefault('asset',{'version':'2.0'}).setdefault('extras',{})['d1_tiger_parser_basis_fix']={
      'parser_basis':'[x,y,z] -> [y,z,x]','restored_model_basis':'native D1/Tiger [x,y,z]',
      'target_models':sorted(TARGET_MODELS),'skin_count':len(target_skins),'joint_node_count':len(joint_nodes),
      'inverse_bind_accessor_count':len(ibm_accessors),'animation_output_accessor_count':len(transformed),
      'placement_matrices_changed':False,'mesh_vertex_data_changed':False,'weights_changed':False,'materials_changed':False}
    a.out.parent.mkdir(parents=True,exist_ok=True);write_glb(a.out,doc,bytes(blob))
    outdoc,outbin=read_glb(a.out)
    if len(outbin)!=len(bb):raise SystemExit('BIN byte length changed')
    rep={'schema_version':1,'status':'D1_TOWER_ARTICULATED_TIGER_PARSER_BASIS_FIXED','input':str(a.input_glb),'input_sha256':sha(a.input_glb),'output':str(a.out),'output_sha256':sha(a.out),'output_bytes':a.out.stat().st_size,'target_models':sorted(TARGET_MODELS),'skin_count':len(target_skins),'joint_node_count':len(joint_nodes),'inverse_bind_accessor_count':len(ibm_accessors),'animation_output_accessor_count':len(transformed),'bin_byte_length_unchanged':len(outbin)==len(bb),'skins':skin_rows,'animation_channel_count':len(channel_rows),'policy':'Undo only the parser-internal [x,y,z]->[y,z,x] basis on skeleton bind and animation data before the existing Tower placement adapter. Source mesh/weights/material/action identity remains unchanged.'}
    a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(rep,indent=2)+'\n');print(json.dumps({k:rep[k] for k in ('status','output_bytes','output_sha256','skin_count','joint_node_count','inverse_bind_accessor_count','animation_output_accessor_count','animation_channel_count')},indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
