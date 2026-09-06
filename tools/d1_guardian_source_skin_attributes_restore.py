#!/usr/bin/env python3
"""Restore exact D1 JOINTS_0/WEIGHTS_0 to exported component ranges.

Unlike d1_guardian_combined_skin_animation.py this tool stops at source skin
attributes. It does not choose a skeleton, runtime rig, or animation. Each scene
mesh range is mapped back to exact retail index/vertex bytes, and the decoded
inline D1 weights are appended losslessly to the GLB.
"""
from __future__ import annotations

import argparse, json, re, struct, sys
from pathlib import Path
import numpy as np
from pygltflib import GLTF2

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from d1_entity_model_probe import parse_model
from d1_entity_model_export import decode_indices, primitive_faces, index_is32
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_investment_parent_probe import RemoteLogicalPackage
from d1_remote_model_export import MultiPackageReader
from d1_split_tar_extract import SplitHttpTar
from d1_guardian_combined_skin_animation import read_linked_multi, decode_skin
from d1_gltf_bind_rigid_animation import append_accessor

NAME_RE=re.compile(r'(?P<tag>[0-9A-F]{8})_mesh(?P<mesh>\d+)_range(?P<off>\d+)_(?P<count>\d+)',re.I)
FLOAT=5126
UNSIGNED_SHORT=5123
ARRAY_BUFFER=34962


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('input_glb',type=Path)
    ap.add_argument('--member-catalog',type=Path,action='append',required=True)
    ap.add_argument('--base-url',required=True)
    ap.add_argument('--part-count',type=int,default=10)
    ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('--node-count',type=int,required=True)
    ap.add_argument('--report',type=Path,required=True)
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args()
    if a.node_count<=0:raise ValueError('node-count must be positive')

    catalogs=load_catalogs(a.member_catalog)
    arc=SplitHttpTar([f"{a.base_url.rstrip('/')}/packages.tar.{i:03d}" for i in range(1,a.part_count+1)],retries=6,timeout=90)
    views={pkg:RemoteLogicalPackage(arc,fam,a.runtime) for pkg,fam in sorted(catalogs.items())}
    rr=MultiPackageReader(views);by={e['tag_hash'].upper():e for e in rr.entries}

    g=GLTF2().load_binary(str(a.input_glb));blob=bytearray(g.binary_blob() or b'')
    scene=g.scenes[g.scene or 0];active_nodes=set(scene.nodes or [])
    requests=[]
    for ni in sorted(active_nodes):
        n=g.nodes[ni]
        if n.mesh is None:continue
        name=(g.meshes[n.mesh].name or n.name or '')
        m=NAME_RE.search(name)
        if m is None:raise ValueError(f'active mesh node {name!r} lacks source range identity')
        requests.append((ni,n.mesh,m.group('tag').upper(),int(m.group('mesh')),int(m.group('off')),int(m.group('count')),name))
    if not requests:raise ValueError('no active source range nodes')

    tags=sorted({x[2] for x in requests});models={};cache={}
    for tag in tags:
        e=by.get(tag)
        if e is None:raise KeyError(f'{tag}: model absent from selected catalogs')
        models[tag]=parse_model(rr.entry(e['index']),'PS4')
    for tag,model in models.items():
        for mi,mesh in enumerate(model['meshes']):
            _,head,_,payload=read_linked_multi(rr,by,mesh['vertices1']);stride=struct.unpack_from('<h',head,4)[0]
            joints,weights,smeta=decode_skin(payload,stride,a.node_count)
            _,ih,_,idata=read_linked_multi(rr,by,mesh['indices']);is32=index_is32(ih);inds=decode_indices(idata,is32)
            ranges={}
            for p in mesh['parts']:
                ranges.setdefault((int(p['index_offset']),int(p['index_count'])),set()).add(int(p['primitive_type']))
            cache[(tag,mi)]={'joints':joints,'weights':weights,'meta':smeta,'indices':inds,'is32':is32,'ranges':ranges}

    rows=[];all_bones=set();total=0
    for ni,gmi,tag,mi,off,count,name in requests:
        sc=cache[(tag,mi)];ptypes=sc['ranges'].get((off,count))
        if not ptypes or len(ptypes)!=1:raise ValueError(f'{name}: ambiguous primitive type {ptypes}')
        ptype=next(iter(ptypes));sl=sc['indices'][off:off+count];faces=primitive_faces(sl,ptype,sc['is32']);used=np.unique(faces.reshape(-1))
        mesh=g.meshes[gmi]
        if len(mesh.primitives)!=1:raise ValueError(f'{name}: expected one primitive')
        prim=mesh.primitives[0];pc=int(g.accessors[prim.attributes.POSITION].count)
        if pc!=len(used):raise ValueError(f'{name}: GLB/source used vertex count {pc}/{len(used)}')
        j=sc['joints'][used];w=sc['weights'][used]
        jacc=append_accessor(g,blob,j,component_type=UNSIGNED_SHORT,accessor_type='VEC4',target=ARRAY_BUFFER)
        wacc=append_accessor(g,blob,w,component_type=FLOAT,accessor_type='VEC4',target=ARRAY_BUFFER)
        prim.attributes.JOINTS_0=jacc;prim.attributes.WEIGHTS_0=wacc
        bones=sorted(set(int(x) for x in j[w>0]));all_bones.update(bones);total+=len(used)
        mesh.extras={**(mesh.extras or {}),'d1ExactSourceSkin':{'sourceModel':tag,'sourceMesh':mi,'indexOffset':off,'indexCount':count,'boneDomain':bones}}
        rows.append({'mesh':name,'source_model':tag,'source_mesh':mi,'index_offset':off,'index_count':count,'primitive_type':ptype,'vertex_count':len(used),'bone_domain':bones})

    g.extras={**(g.extras or {}),'d1ExactSourceSkinAttributes':{'nodeCountLimit':a.node_count,'activePrimitiveCount':len(rows),'boneDomain':sorted(all_bones),'policy':'JOINTS_0/WEIGHTS_0 restored only from exact D1 primary vertex bytes; no skeleton, rig or animation selected.'}}
    g.buffers[0].byteLength=len(blob);g.set_binary_blob(bytes(blob));a.output.parent.mkdir(parents=True,exist_ok=True);g.save_binary(str(a.output))
    rep={'schema':'d1_guardian_source_skin_attributes_restore/v1','input':str(a.input_glb),'output':str(a.output),'output_bytes':a.output.stat().st_size,'active_primitive_count':len(rows),'bound_vertex_count':total,'node_count_limit':a.node_count,'bone_domain':sorted(all_bones),'ranges':rows,'policy':'Source-only skin attributes; no animation or skeleton identity inferred.'}
    a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(rep,indent=2)+'\n');print(json.dumps(rep,indent=2));return 0

if __name__=='__main__':raise SystemExit(main())
