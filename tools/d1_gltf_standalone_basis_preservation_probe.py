#!/usr/bin/env python3
"""Prove that a standalone articulated basis repair changed only basis domains.

The source/fixed pair must retain all visual resource JSON, all embedded image bytes,
all mesh-node JSON, all accessor metadata, and every accessor payload except the one
skin inverseBindMatrices accessor and animation output accessors.  Animation channel/
sampler structure and pre-existing extras are also preserved.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from d1_gltf_layer_merge import read_glb
from d1_gltf_skin_bind_identity_probe import accessor


def sha(p:Path)->str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''): h.update(b)
    return h.hexdigest()


def bvbytes(doc,blob,bvi):
    v=doc['bufferViews'][bvi]; o=int(v.get('byteOffset',0)); n=int(v['byteLength']); return blob[o:o+n]


def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument('--source',type=Path,required=True); ap.add_argument('--fixed',type=Path,required=True)
    ap.add_argument('--model',required=True); ap.add_argument('-o','--output',type=Path,required=True); a=ap.parse_args(); model=a.model.upper()
    src,sbin=read_glb(a.source); dst,dbin=read_glb(a.fixed); violations=[]
    def ck(cond,msg):
        if not cond: violations.append(msg)

    for k in ('materials','textures','images','meshes','skins','accessors','bufferViews','samplers'):
        ck(src.get(k)==dst.get(k),f'{k}_json_changed')
    ck(len(sbin)==len(dbin),f'bin_length:{len(sbin)}!={len(dbin)}')

    mesh_nodes=[i for i,n in enumerate(src.get('nodes',[])) if n.get('mesh') is not None and n.get('skin') is not None]
    for i in mesh_nodes: ck(i<len(dst.get('nodes',[])) and src['nodes'][i]==dst['nodes'][i],f'mesh_node_{i}_json_changed')

    ck(len(src.get('animations',[]))==len(dst.get('animations',[])),'animation_count_changed')
    for i,(x,y) in enumerate(zip(src.get('animations',[]),dst.get('animations',[]))):
        xx={k:v for k,v in x.items() if k!='extras'}; yy={k:v for k,v in y.items() if k!='extras'}
        ck(xx==yy,f'animation_{i}_structure_changed')
        old=x.get('extras') or {}; new=y.get('extras') or {}
        for k,v in old.items(): ck(new.get(k)==v,f'animation_{i}_old_extra_{k}_changed')
        ck(new.get('d1BasisDomainModel')==model,f'animation_{i}_basis_model_missing')
        ck(new.get('d1ParserBasisUndone') is True,f'animation_{i}_basis_flag_missing')

    skins=src.get('skins',[]); ck(len(skins)==1,f'expected_one_skin_found_{len(skins)}')
    mutable=set()
    if skins: mutable.add(int(skins[0]['inverseBindMatrices']))
    for anim in src.get('animations',[]):
        for sam in anim.get('samplers',[]): mutable.add(int(sam['output']))
    protected=0; protected_changed=[]
    if src.get('accessors')==dst.get('accessors') and len(sbin)==len(dbin):
        for ai in range(len(src.get('accessors',[]))):
            if ai in mutable: continue
            xs=accessor(src,sbin,ai); xd=accessor(dst,dbin,ai)
            if not (xs.dtype==xd.dtype and xs.shape==xd.shape and xs.tobytes()==xd.tobytes()): protected_changed.append(ai)
            protected+=1
    ck(not protected_changed,f'protected_accessors_changed:{protected_changed[:16]}')

    image_changed=[]
    if src.get('images')==dst.get('images') and src.get('bufferViews')==dst.get('bufferViews'):
        for i,img in enumerate(src.get('images',[])):
            if 'bufferView' in img and bvbytes(src,sbin,int(img['bufferView']))!=bvbytes(dst,dbin,int(img['bufferView'])): image_changed.append(i)
    ck(not image_changed,f'image_payloads_changed:{image_changed[:16]}')

    scene=dst.get('scenes',[{}])[int(dst.get('scene',0))]; roots=[int(x) for x in scene.get('nodes',[])]
    ck(len(roots)==1,f'fixed_scene_root_count:{len(roots)}')
    root_extra={}
    if len(roots)==1 and roots[0]<len(dst.get('nodes',[])): root_extra=dst['nodes'][roots[0]].get('extras') or {}
    ck(root_extra.get('d1BasisAdapter')=='native D1 Z-up -> glTF Y-up','fixed_basis_root_marker_missing')

    status='D1_GLTF_STANDALONE_BASIS_PRESERVATION_COMPLETE' if not violations else 'D1_GLTF_STANDALONE_BASIS_PRESERVATION_FAILED'
    out={'schema_version':1,'status':status,'source':str(a.source),'source_sha256':sha(a.source),'fixed':str(a.fixed),'fixed_sha256':sha(a.fixed),
         'fixed_bytes':a.fixed.stat().st_size,'model':model,'counts':{k:len(src.get(k,[])) for k in ('nodes','meshes','materials','textures','images','skins','animations','accessors','bufferViews')},
         'fixed_node_count':len(dst.get('nodes',[])),'mesh_node_count':len(mesh_nodes),'mutable_basis_accessor_count':len(mutable),'protected_accessor_count':protected,
         'bin_byte_length_unchanged':len(sbin)==len(dbin),'visual_resource_json_unchanged':all(src.get(k)==dst.get(k) for k in ('materials','textures','images','meshes','skins','accessors','bufferViews','samplers')),
         'embedded_image_bytes_unchanged':not image_changed,'mesh_node_json_unchanged':not any(x.startswith('mesh_node_') for x in violations),
         'violations':violations,'policy':'Only IBM + animation output payloads, joint TRS, animation basis metadata, and one scene basis root may differ; all portable visual resources remain exact.'}
    a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2)); return 0 if not violations else 2
if __name__=='__main__': raise SystemExit(main())
