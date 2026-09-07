#!/usr/bin/env python3
"""Repair basis composition for a standalone D1 articulated glTF export.

The pinned tiger-animation-parser converts native Tiger/D1 vectors internally as
    parser = [raw_y, raw_z, raw_x]
for its Three.js-oriented animation path, while extracted D1 mesh geometry remains
in native Z-up model space.  A file assembled from both domains can therefore have
perfectly self-consistent inverse bind matrices and still show the armature on a
different physical axis from the visible mesh in Blender.

This adapter is deliberately narrow and fail-closed:
  1. undo the parser-only basis on one selected skin's joint local TRS,
     inverseBindMatrices, and every animation output targeting those joints;
  2. wrap the complete standalone actor in the established native D1 Z-up -> glTF
     Y-up adapter [x,y,z] -> [x,z,-y].

Mesh vertex/index/UV/JOINTS_0/WEIGHTS_0 bytes, materials, textures, images,
animation times, clip identity and topology are not changed.
"""
from __future__ import annotations

import argparse, hashlib, json, math
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation

from d1_gltf_layer_merge import read_glb, write_glb
from d1_gltf_skin_bind_identity_probe import accessor, node_local

# parser p = P @ raw, p=[raw_y, raw_z, raw_x]
P=np.array([[0.,1.,0.,0.],[0.,0.,1.,0.],[1.,0.,0.,0.],[0.,0.,0.,1.]],dtype=np.float64)
PI=P.T
# native D1 Z-up -> glTF Y-up, row-major mathematical form
Q=np.array([[1.,0.,0.,0.],[0.,0.,1.,0.],[0.,-1.,0.,0.],[0.,0.,0.,1.]],dtype=np.float64)


def sha256_file(p:Path)->str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''): h.update(b)
    return h.hexdigest()


def decompose(M:np.ndarray):
    t=M[:3,3].copy(); A=M[:3,:3].copy(); s=np.linalg.norm(A,axis=0)
    if np.any(s<1e-12): raise ValueError('zero scale during basis conversion')
    R=A/s
    if np.linalg.det(R)<0:
        k=int(np.argmax(np.abs(s))); s[k]*=-1.; R[:,k]*=-1.
    return t,Rotation.from_matrix(R).as_quat(),s


def set_accessor(doc:dict,blob:bytearray,ai:int,data:np.ndarray)->None:
    a=doc['accessors'][ai]; bv=doc['bufferViews'][a['bufferView']]
    if int(a['componentType'])!=5126: raise ValueError(f'accessor {ai}: expected FLOAT')
    n={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}[a['type']]
    x=np.asarray(data,dtype='<f4')
    flat=np.stack([m.reshape(16,order='F') for m in x],axis=0) if a['type']=='MAT4' else x.reshape((int(a['count']),n))
    if flat.shape!=(int(a['count']),n): raise ValueError(f'accessor {ai}: bad shape {flat.shape}')
    base=int(bv.get('byteOffset',0))+int(a.get('byteOffset',0)); stride=int(bv.get('byteStride',4*n)); rowbytes=4*n
    if stride==rowbytes:
        raw=flat.tobytes(order='C'); blob[base:base+len(raw)]=raw
    else:
        for i,row in enumerate(flat):
            raw=row.astype('<f4',copy=False).tobytes(); blob[base+i*stride:base+i*stride+rowbytes]=raw


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('input_glb',type=Path)
    ap.add_argument('--model',required=True)
    ap.add_argument('--expect-skeleton')
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--report',type=Path,required=True)
    a=ap.parse_args(); model=a.model.upper(); expected=(a.expect_skeleton or '').upper() or None

    doc,source_bin=read_glb(a.input_glb); blob=bytearray(source_bin); nodes=doc.get('nodes',[]); skins=doc.get('skins',[])
    if (doc.get('asset',{}).get('extras',{}) or {}).get('d1_standalone_articulated_basis_fix'):
        raise ValueError('input is already marked basis-fixed')

    selected=[]
    for si,s in enumerate(skins):
        root=int(s['skeleton']); ex=nodes[root].get('extras') or {}
        if str(ex.get('d1Model','')).upper()==model: selected.append((si,s))
    if len(selected)!=1: raise ValueError(f'expected exactly one standalone skin for {model}, found {len(selected)}')
    si,skin=selected[0]; root=int(skin['skeleton']); rex=nodes[root].get('extras') or {}; skeleton=str(rex.get('d1Skeleton','')).upper()
    if expected and skeleton!=expected: raise ValueError(f'skeleton drift: {skeleton} != {expected}')

    joints=[int(x) for x in skin['joints']]; jointset=set(joints)
    if len(jointset)!=len(joints): raise ValueError('duplicate joint node in skin palette')
    mesh_nodes=[i for i,n in enumerate(nodes) if n.get('mesh') is not None and n.get('skin') is not None]
    wrong=[i for i in mesh_nodes if int(nodes[i]['skin'])!=si]
    if wrong: raise ValueError(f'other skinned domains in standalone input: {wrong[:16]}')
    if not mesh_nodes: raise ValueError('no skinned mesh nodes')

    # parser-space bind local matrices -> native D1 model-space bind local matrices
    for ji in joints:
        M=PI@node_local(nodes[ji])@P; t,q,s=decompose(M); n=nodes[ji]; n.pop('matrix',None)
        n['translation']=[float(x) for x in t]; n['rotation']=[float(x) for x in q]; n['scale']=[float(x) for x in s]

    ibm_ai=int(skin['inverseBindMatrices']); mats=accessor(doc,source_bin,ibm_ai).astype(np.float64)
    if mats.shape!=(len(joints),4,4): raise ValueError(f'IBM shape {mats.shape} != {len(joints)} joints')
    set_accessor(doc,blob,ibm_ai,np.stack([PI@m@P for m in mats]))

    # Transform each shared output accessor once.  Pass the live bytearray directly;
    # converting the ~267 MB BIN to bytes per channel would be catastrophically slow.
    transformed=set(); targeted_channels=0; all_channels=0; animation_rows=[]; p3=P[:3,:3]; pi3=PI[:3,:3]
    for ani,anim in enumerate(doc.get('animations',[])):
        targeted=0
        for ch in anim.get('channels',[]):
            all_channels+=1; node=int(ch['target']['node'])
            if node not in jointset: continue
            path=ch['target']['path']
            if path not in ('translation','rotation','scale'): raise ValueError(f'unsupported path {path}')
            sam=anim['samplers'][int(ch['sampler'])]; ai=int(sam['output']); key=(ai,path)
            if key not in transformed:
                vals=accessor(doc,blob,ai).astype(np.float64)
                if path in ('translation','scale'): new=vals[:,[2,0,1]]
                else:
                    R=Rotation.from_quat(vals).as_matrix(); new=Rotation.from_matrix(np.einsum('ij,njk,kl->nil',pi3,R,p3)).as_quat()
                set_accessor(doc,blob,ai,new); transformed.add(key)
            targeted+=1; targeted_channels+=1
        if targeted:
            anim.setdefault('extras',{})['d1BasisDomainModel']=model; anim['extras']['d1ParserBasisUndone']=True
            animation_rows.append({'animation_index':ani,'name':anim.get('name'),'targeted_channel_count':targeted})
    if targeted_channels!=all_channels:
        raise ValueError(f'standalone animation-domain mismatch: targeted {targeted_channels} of {all_channels} channels')

    scene=doc['scenes'][int(doc.get('scene',0))]; old_roots=[int(x) for x in scene.get('nodes',[])]
    if not old_roots: raise ValueError('scene has no roots')
    new_root=len(nodes); half=math.sqrt(.5)
    nodes.append({'name':f'D1_{model}_NATIVE_ZUP_TO_GLTF_YUP','rotation':[-half,0.,0.,half],'children':old_roots,
                  'extras':{'d1BasisAdapter':'native D1 Z-up -> glTF Y-up','d1RowMajorMatrix':Q.tolist(),'d1VectorMapping':'[x,y,z] -> [x,z,-y]'}})
    scene['nodes']=[new_root]

    fix={'schema':'d1_standalone_articulated_basis_fix/v1','model':model,'skeleton':skeleton,'skin_index':si,
         'joint_count':len(joints),'skinned_mesh_node_count':len(mesh_nodes),'animation_count':len(animation_rows),
         'animation_channel_count':targeted_channels,'animation_output_accessor_count':len(transformed),'inverse_bind_accessor':ibm_ai,
         'parser_basis_undone':'[x,y,z] -> [y,z,x]','native_to_gltf_world_adapter':'[x,y,z] -> [x,z,-y]',
         'world_adapter_root_node':new_root,'source_bin_byte_length':len(source_bin),
         'protected_domains':['mesh vertex/index/UV/JOINTS_0/WEIGHTS_0 bytes','materials/textures/images','animation time accessors and clip identity']}
    doc.setdefault('asset',{'version':'2.0'}).setdefault('extras',{})['d1_standalone_articulated_basis_fix']=fix

    a.out.parent.mkdir(parents=True,exist_ok=True); write_glb(a.out,doc,bytes(blob)); check,check_bin=read_glb(a.out)
    if len(check_bin)!=len(source_bin): raise ValueError('BIN byte length changed')
    if len(check.get('nodes',[]))!=len(nodes): raise ValueError('node count changed after round trip')
    rep={'schema_version':1,'status':'D1_STANDALONE_ARTICULATED_PARSER_AND_GLTF_BASIS_FIXED',
         'input':str(a.input_glb),'input_sha256':sha256_file(a.input_glb),'output':str(a.out),'output_sha256':sha256_file(a.out),'output_bytes':a.out.stat().st_size,
         'model':model,'skeleton':skeleton,'skin_index':si,'joint_count':len(joints),'skinned_mesh_node_count':len(mesh_nodes),
         'animation_count':len(animation_rows),'animation_channel_count':targeted_channels,'animation_output_accessor_count':len(transformed),
         'inverse_bind_accessor':ibm_ai,'old_scene_roots':old_roots,'new_scene_root':new_root,
         'source_bin_bytes':len(source_bin),'output_bin_bytes':len(check_bin),'bin_byte_length_unchanged':len(check_bin)==len(source_bin),
         'animation_rows':animation_rows,
         'policy':"Undo only tiger-animation-parser's [x,y,z]->[y,z,x] articulated basis, then wrap the standalone native-Z-up actor in the established D1->glTF Y-up adapter. Mesh/material/texture/weight/topology/action identity is not reinterpreted."}
    a.report.parent.mkdir(parents=True,exist_ok=True); a.report.write_text(json.dumps(rep,indent=2)+'\n')
    print(json.dumps({k:rep[k] for k in ('status','output_sha256','output_bytes','joint_count','skinned_mesh_node_count','animation_count','animation_channel_count','animation_output_accessor_count','bin_byte_length_unchanged')},indent=2))
    return 0

if __name__=='__main__': raise SystemExit(main())
