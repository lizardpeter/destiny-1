#!/usr/bin/env python3
"""Build a proof-oriented D1 ROI PS4 Gjallarhorn GLB from art arrangement 1229.

The visual selection is retail-byte proven:
  Inventory D471D331 (Year 3 Gjallarhorn) -> ArtArrangement 1229
  ArtArrangement 1229 -> six EntityParents -> six s_entity visual entities
  each entity -> EntityResource(model) -> one s_entity_model.

This exporter intentionally does not invent attachment transforms, skin weights,
or material semantics.  Each model's own Tiger model scale/translation is applied
and the six models are emitted together in their shared model coordinate space.
Only LOD1 index ranges are exported.  Duplicate material-pass rows that address
the same strip range are emitted once and retained as provenance in extras.
"""
from __future__ import annotations

import argparse, base64, json, struct, sys
from pathlib import Path
import numpy as np
from pygltflib import (
    GLTF2, Asset, Scene, Node, Mesh, Primitive, Attributes,
    Buffer, BufferView, Accessor, Material, PbrMetallicRoughness,
)

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from d1_entry_extract import EntryReader
from d1_entity_model_probe import parse_model
from d1_investment_arrangement_probe import filehash_pkg_index

ARRANGEMENT=1229
MODEL_TO_ENTITY={
    '80A743A6':'80A743A4',
    '80A73BAB':'80A73BA9',
    '80A72202':'80A72200',
    '80A7317B':'80A73179',
    '80A73256':'80A73254',
    '80A73D13':'80A73D11',
}
AUX_MATERIALS={'80AAE10B','80AAE10C'}
FLOAT=5126
UNSIGNED_INT=5125
ARRAY_BUFFER=34962
ELEMENT_ARRAY_BUFFER=34963


def snorm16(a):
    x=np.asarray(a,dtype=np.float32)/32767.0
    return np.maximum(x,-1.0)


def tiger_to_gltf_xyz(a):
    return np.ascontiguousarray(a[:,[1,2,0]])


def strip_to_triangles(vals):
    out=[]; strip=[]
    for raw in vals.tolist():
        v=int(raw)
        if v==0xFFFF:
            strip=[]; continue
        strip.append(v)
        if len(strip)<3: continue
        a,b,c=strip[-3],strip[-2],strip[-1]
        if (len(strip)-3)&1: a,b=b,a
        if a!=b and b!=c and a!=c: out.append((a,b,c))
    return np.asarray(out,dtype=np.uint32).reshape((-1,3))


def append_buffer(g,payload):
    i=len(g.buffers)
    g.buffers.append(Buffer(byteLength=len(payload),uri='data:application/octet-stream;base64,'+base64.b64encode(payload).decode('ascii')))
    return i


def append_accessor(g,a,ctype,atype,target=None,minmax=False):
    a=np.ascontiguousarray(a); payload=a.tobytes(); bi=append_buffer(g,payload)
    bvi=len(g.bufferViews); g.bufferViews.append(BufferView(buffer=bi,byteOffset=0,byteLength=len(payload),target=target))
    ai=len(g.accessors); acc=Accessor(bufferView=bvi,byteOffset=0,componentType=ctype,count=int(a.shape[0]),type=atype)
    if minmax:
        q=a.reshape((a.shape[0],-1)); acc.min=[float(x) for x in q.min(axis=0)];acc.max=[float(x) for x in q.max(axis=0)]
    g.accessors.append(acc); return ai


def by_hash(reader): return {e['tag_hash'].upper():e for e in reader.entries}


def entry_bytes(reader, table, tag):
    e=table[tag.upper()]
    if not reader.available(e['index']): raise RuntimeError(f'{tag} unavailable in {reader.pkg.name}')
    return reader.entry(e['index'])


def linked_payload(readers,tables,tag):
    pkg,_=filehash_pkg_index(int(tag,16)); r=readers[pkg]; t=tables[pkg]; e=t[tag]
    h=entry_bytes(r,t,tag); ref=e['reference'].upper()
    pe=t.get(ref)
    if pe is None: raise KeyError(f'{tag} -> payload {ref} absent in logical pkg {pkg:04X}')
    p=entry_bytes(r,t,ref)
    return h,p,{'header_tag':tag,'payload_tag':ref,'header_reference':e['reference'].upper()}


def load_model(model_dir,tag):
    p=model_dir/f'{tag}.bin'
    if not p.exists(): raise FileNotFoundError(p)
    b=p.read_bytes(); return parse_model(b,'PS4'),b


def choose_display_material(candidates):
    real=sorted(set(candidates)-AUX_MATERIALS)
    if real: return real[0],real
    return sorted(candidates)[0],[]


def decode_mesh(readers,tables,mesh,model_tag,mesh_index):
    h0,p0,s0=linked_payload(readers,tables,mesh['vertices1'])
    h1,p1,s1=linked_payload(readers,tables,mesh['vertices2'])
    hi,pi,si=linked_payload(readers,tables,mesh['indices'])
    stride0=struct.unpack_from('<h',h0,4)[0]; stride1=struct.unpack_from('<h',h1,4)[0]
    if stride0<6 or stride0%2 or stride1<10 or stride1%2:
        raise RuntimeError(f'{model_tag} mesh{mesh_index}: unsupported strides {stride0}/{stride1}')
    r0=np.frombuffer(p0,dtype='<i2').reshape((-1,stride0//2))
    r1=np.frombuffer(p1,dtype='<i2').reshape((-1,stride1//2))
    if len(r0)!=len(r1): raise RuntimeError(f'{model_tag} mesh{mesh_index}: vertex stream mismatch {len(r0)}/{len(r1)}')
    scale=np.asarray(mesh['model_scale'][:3],dtype=np.float32); trans=np.asarray(mesh['model_translation'][:3],dtype=np.float32)
    pos=tiger_to_gltf_xyz(snorm16(r0[:,:3])*scale+trans).astype(np.float32)
    uv=(snorm16(r1[:,:2])*np.asarray(mesh['texcoord_scale'],dtype=np.float32)+np.asarray(mesh['texcoord_translation'],dtype=np.float32)).astype(np.float32)
    nt=snorm16(r1[:,2:5]); nl=np.linalg.norm(nt,axis=1,keepdims=True); nt=np.divide(nt,np.maximum(nl,1e-8)); nor=tiger_to_gltf_xyz(nt).astype(np.float32)
    src=np.frombuffer(pi,dtype='<u2')

    groups={}
    for part in mesh['parts']:
        if int(part['lod'])!=1 or int(part['primitive_type'])!=5: continue
        key=(int(part['index_offset']),int(part['index_count']))
        groups.setdefault(key,[]).append(part)
    prims=[]
    for (off,count),parts in sorted(groups.items()):
        tri=strip_to_triangles(src[off:off+count])
        mats=[p['material'].upper() for p in parts]
        display,real=choose_display_material(mats)
        prims.append({'off':off,'count':count,'tri':tri,'materials':sorted(set(mats)),'display_material':display,'real_materials':real})
    rep={
      'model_tag':model_tag,'mesh_index':mesh_index,'vertex_count':len(pos),'stride0':stride0,'stride1':stride1,
      'model_scale':mesh['model_scale'],'model_translation':mesh['model_translation'],
      'buffers':[s0,s1,si],
      'lod1_ranges':[{'offset':x['off'],'count':x['count'],'triangles':len(x['tri']),'materials':x['materials'],'display_material':x['display_material']} for x in prims],
      'lod1_triangles':sum(len(x['tri']) for x in prims),
    }
    return {'pos':pos,'uv':uv,'nor':nor,'prims':prims},rep


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--pkg-011c',type=Path,required=True)
    ap.add_argument('--pkg-0139',type=Path,required=True)
    ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('--model-dir',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--report',type=Path,required=True)
    a=ap.parse_args()

    readers={0x011C:EntryReader(a.pkg_011c,a.runtime),0x0139:EntryReader(a.pkg_0139,a.runtime)}
    tables={k:by_hash(v) for k,v in readers.items()}
    g=GLTF2(asset=Asset(version='2.0',generator='destiny-1 Gjallarhorn art arrangement 1229 proof exporter'))
    g.scenes=[Scene(nodes=[0])]; g.scene=0; g.nodes=[Node(name='Gjallarhorn_1229_PresentationRoot',children=[])]
    g.meshes=[];g.materials=[];g.buffers=[];g.bufferViews=[];g.accessors=[]
    mat_index={}
    reports=[]; all_pos=[]

    def material_index(h,all_native):
        h=h.upper()
        if h not in mat_index:
            i=len(g.materials);mat_index[h]=i
            g.materials.append(Material(name=f'D1_{h}_PORTABLE_NEUTRAL',pbrMetallicRoughness=PbrMetallicRoughness(baseColorFactor=[0.72,0.72,0.72,1.0],metallicFactor=0.0,roughnessFactor=0.72),extras={'d1DisplayMaterial':h,'nativeMaterialCandidates':all_native,'policy':'neutral portable placeholder; native material textures/shader binding not yet mapped in this fixture'}))
        return mat_index[h]

    for tag,entity in MODEL_TO_ENTITY.items():
        model,mb=load_model(a.model_dir,tag)
        native_mesh_nodes=[]; mrep={'model_tag':tag,'entity':entity,'model_size':len(mb),'mesh_count':model['mesh_count'],'meshes':[]}
        for mi,mesh in enumerate(model['meshes']):
            dec,rep=decode_mesh(readers,tables,mesh,tag,mi);mrep['meshes'].append(rep);all_pos.append(dec['pos'])
            pa=append_accessor(g,dec['pos'],FLOAT,'VEC3',ARRAY_BUFFER,True);na=append_accessor(g,dec['nor'],FLOAT,'VEC3',ARRAY_BUFFER);ua=append_accessor(g,dec['uv'],FLOAT,'VEC2',ARRAY_BUFFER)
            gps=[]
            for pr in dec['prims']:
                ia=append_accessor(g,pr['tri'].reshape(-1),UNSIGNED_INT,'SCALAR',ELEMENT_ARRAY_BUFFER)
                gps.append(Primitive(attributes=Attributes(POSITION=pa,NORMAL=na,TEXCOORD_0=ua),indices=ia,material=material_index(pr['display_material'],pr['materials']),mode=4,extras={'d1IndexOffset':pr['off'],'d1IndexCount':pr['count'],'nativeMaterialCandidates':pr['materials'],'nativeRealMaterialCandidates':pr['real_materials']}))
            mesh_i=len(g.meshes);g.meshes.append(Mesh(name=f'{tag}_mesh{mi}',primitives=gps,extras={'d1Model':tag,'d1Entity':entity,'d1MeshIndex':mi}))
            node_i=len(g.nodes);g.nodes.append(Node(name=f'{tag}_mesh{mi}',mesh=mesh_i,extras={'d1Model':tag,'d1Entity':entity}));native_mesh_nodes.append(node_i)
        model_node=len(g.nodes);g.nodes.append(Node(name=f'{tag}_Entity_{entity}',children=native_mesh_nodes,extras={'d1Model':tag,'d1Entity':entity,'artArrangement':ARRANGEMENT}));g.nodes[0].children.append(model_node)
        reports.append(mrep)

    P=np.vstack(all_pos); pmin=P.min(axis=0);pmax=P.max(axis=0);center=(pmin+pmax)/2
    g.nodes[0].translation=[float(-x) for x in center]
    total_tri=sum(x['lod1_triangles'] for m in reports for x in m['meshes'])
    g.extras={'d1Gjallarhorn':{'inventoryItemHashYear3':'D471D331','artArrangementIndex':1229,'weaponPatternIndex':39,'entityCount':6,'modelCount':6,'models':list(MODEL_TO_ENTITY),'presentationTranslation':[-float(x) for x in center],'nativeAssemblyPolicy':'six retail-selected models in their own shared model coordinates; no invented attachment transform','materialPolicy':'neutral placeholders retain exact native material hashes in extras'}}
    a.out.parent.mkdir(parents=True,exist_ok=True);g.save_binary(str(a.out))
    report={'inventory_item':'D471D331','arrangement':1229,'weapon_pattern':39,'models':reports,'total_lod1_triangles':int(total_tri),'bbox_min':pmin.tolist(),'bbox_max':pmax.tolist(),'bbox_center':center.tolist(),'output':str(a.out),'output_bytes':a.out.stat().st_size}
    a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'models':len(reports),'triangles':int(total_tri),'bbox_min':pmin.tolist(),'bbox_max':pmax.tolist(),'bytes':a.out.stat().st_size},indent=2))

if __name__=='__main__':main()
