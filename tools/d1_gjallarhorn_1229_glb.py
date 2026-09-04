#!/usr/bin/env python3
"""Build a proof-oriented D1 ROI PS4 Gjallarhorn GLB from art arrangement 1229.

Retail-byte chain:
  D471D331 -> ArtArrangement 1229 -> six EntityParents -> six s_entity records
  -> six model EntityResources -> six s_entity_model records (eight mesh records).

No geometry, attachment transforms, skin weights, or material semantics are
invented. LOD1 only. Repeated native material-pass rows addressing the same
strip range are emitted once and preserved as provenance. Some ROI package
patch snapshots contain Oodle blocks that are unreadable or corrupt while the
same retail entry is intact in an earlier snapshot, so geometry resources are
resolved newest-to-oldest and vertex candidates must also pass the native
buffer-header stride invariant before they are accepted.
"""
from __future__ import annotations

import argparse, base64, json, re, struct, sys
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
    '80A743A6':'80A743A4', '80A73BAB':'80A73BA9', '80A72202':'80A72200',
    '80A7317B':'80A73179', '80A73256':'80A73254', '80A73D13':'80A73D11',
}
AUX_MATERIALS={'80AAE10B','80AAE10C'}
FLOAT=5126; UNSIGNED_INT=5125; ARRAY_BUFFER=34962; ELEMENT_ARRAY_BUFFER=34963


def snorm16(a):
    x=np.asarray(a,dtype=np.float32)/32767.0
    return np.maximum(x,-1.0)


def tiger_to_gltf_xyz(a): return np.ascontiguousarray(a[:,[1,2,0]])


def strip_to_triangles(vals):
    out=[]; strip=[]
    for raw in vals.tolist():
        v=int(raw)
        if v==0xFFFF: strip=[]; continue
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
        q=a.reshape((a.shape[0],-1)); acc.min=[float(x) for x in q.min(axis=0)]; acc.max=[float(x) for x in q.max(axis=0)]
    g.accessors.append(acc); return ai


def by_hash(reader): return {e['tag_hash'].upper():e for e in reader.entries}


def patch_number(path):
    m=re.search(r'_(\d+)\.pkg$',path.name)
    return int(m.group(1)) if m else -1


def reader_family(seed,runtime):
    m=re.match(r'^(.*)_\d+\.pkg$',seed.name)
    if not m:
        r=EntryReader(seed,runtime); return [(r,by_hash(r))]
    paths=sorted(seed.parent.glob(m.group(1)+'_*.pkg'),key=patch_number,reverse=True)
    out=[]
    for p in paths:
        try:
            r=EntryReader(p,runtime); out.append((r,by_hash(r)))
        except Exception:
            pass
    if not out: raise RuntimeError(f'no readable package snapshots for {seed}')
    return out


def entry_bytes(reader,table,tag):
    e=table[tag.upper()]
    if not reader.available(e['index']): raise RuntimeError(f'{tag} unavailable in {reader.pkg.name}')
    return reader.entry(e['index'])


def linked_payload(reader_sets,tag,kind=None):
    pkg,_=filehash_pkg_index(int(tag,16)); candidates=reader_sets.get(pkg)
    if not candidates: raise KeyError(f'{tag} belongs to unprovided logical package {pkg:04X}')
    errors=[]
    for r,t in candidates:
        e=t.get(tag.upper())
        if e is None: continue
        ref=e['reference'].upper()
        if ref not in t: continue
        try:
            h=entry_bytes(r,t,tag); p=entry_bytes(r,t,ref)
            stride=None
            if kind=='vertex':
                if len(h)<6: raise RuntimeError(f'vertex header too short: {len(h)}')
                stride=struct.unpack_from('<h',h,4)[0]
                if stride<6 or stride>128 or stride%2:
                    raise RuntimeError(f'invalid vertex stride {stride}')
                if len(p)%stride:
                    raise RuntimeError(f'payload {len(p)} not divisible by vertex stride {stride}')
            source={'header_tag':tag,'payload_tag':ref,'header_reference':ref,'package_id':f'{pkg:04X}','snapshot':r.pkg.name}
            if stride is not None: source['validated_stride']=stride
            return h,p,source
        except Exception as ex:
            errors.append({'snapshot':r.pkg.name,'error':repr(ex)})
    raise RuntimeError(f'could not recover {tag} in package {pkg:04X}: {errors}')


def load_model(model_dir,tag):
    p=model_dir/f'{tag}.bin'
    if not p.exists(): raise FileNotFoundError(p)
    b=p.read_bytes(); return parse_model(b,'PS4'),b


def choose_display_material(candidates):
    real=sorted(set(candidates)-AUX_MATERIALS)
    return (real[0],real) if real else (sorted(candidates)[0],[])


def decode_mesh(reader_sets,mesh,model_tag,mesh_index):
    h0,p0,s0=linked_payload(reader_sets,mesh['vertices1'],'vertex')
    h1,p1,s1=linked_payload(reader_sets,mesh['vertices2'],'vertex')
    hi,pi,si=linked_payload(reader_sets,mesh['indices'],'index')
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
        groups.setdefault((int(part['index_offset']),int(part['index_count'])),[]).append(part)
    prims=[]
    for (off,count),parts in sorted(groups.items()):
        tri=strip_to_triangles(src[off:off+count]); mats=[p['material'].upper() for p in parts]
        display,real=choose_display_material(mats)
        prims.append({'off':off,'count':count,'tri':tri,'materials':sorted(set(mats)),'display_material':display,'real_materials':real})
    rep={
        'model_tag':model_tag,'mesh_index':mesh_index,'vertex_count':len(pos),'stride0':stride0,'stride1':stride1,
        'model_scale':mesh['model_scale'],'model_translation':mesh['model_translation'],'buffers':[s0,s1,si],
        'lod1_ranges':[{'offset':x['off'],'count':x['count'],'triangles':len(x['tri']),'materials':x['materials'],'display_material':x['display_material']} for x in prims],
        'lod1_triangles':sum(len(x['tri']) for x in prims),
    }
    return {'pos':pos,'uv':uv,'nor':nor,'prims':prims},rep


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--pkg-011c',type=Path,required=True); ap.add_argument('--pkg-011e',type=Path,required=True); ap.add_argument('--pkg-0139',type=Path,required=True)
    ap.add_argument('--runtime',type=Path,required=True); ap.add_argument('--model-dir',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True); ap.add_argument('--report',type=Path,required=True)
    a=ap.parse_args()

    reader_sets={0x011C:reader_family(a.pkg_011c,a.runtime),0x011E:reader_family(a.pkg_011e,a.runtime),0x0139:reader_family(a.pkg_0139,a.runtime)}
    g=GLTF2(asset=Asset(version='2.0',generator='destiny-1 Gjallarhorn arrangement 1229 proof exporter'))
    g.scenes=[Scene(nodes=[0])]; g.scene=0; g.nodes=[Node(name='Gjallarhorn_1229_PresentationRoot',children=[])]
    g.meshes=[]; g.materials=[]; g.buffers=[]; g.bufferViews=[]; g.accessors=[]
    mat_index={}; reports=[]; all_pos=[]

    def material_index(h,all_native):
        h=h.upper()
        if h not in mat_index:
            mat_index[h]=len(g.materials)
            g.materials.append(Material(name=f'D1_{h}_PORTABLE_NEUTRAL',pbrMetallicRoughness=PbrMetallicRoughness(baseColorFactor=[0.72,0.72,0.72,1.0],metallicFactor=0.0,roughnessFactor=0.72),extras={'d1DisplayMaterial':h,'nativeMaterialCandidates':all_native,'policy':'neutral placeholder; exact native material binding retained for follow-up'}))
        return mat_index[h]

    for tag,entity in MODEL_TO_ENTITY.items():
        model,mb=load_model(a.model_dir,tag); mesh_nodes=[]
        mrep={'model_tag':tag,'entity':entity,'model_size':len(mb),'mesh_count':model['mesh_count'],'meshes':[]}
        for mi,mesh in enumerate(model['meshes']):
            dec,rep=decode_mesh(reader_sets,mesh,tag,mi); mrep['meshes'].append(rep); all_pos.append(dec['pos'])
            pa=append_accessor(g,dec['pos'],FLOAT,'VEC3',ARRAY_BUFFER,True); na=append_accessor(g,dec['nor'],FLOAT,'VEC3',ARRAY_BUFFER); ua=append_accessor(g,dec['uv'],FLOAT,'VEC2',ARRAY_BUFFER)
            gps=[]
            for pr in dec['prims']:
                ia=append_accessor(g,pr['tri'].reshape(-1),UNSIGNED_INT,'SCALAR',ELEMENT_ARRAY_BUFFER)
                gps.append(Primitive(attributes=Attributes(POSITION=pa,NORMAL=na,TEXCOORD_0=ua),indices=ia,material=material_index(pr['display_material'],pr['materials']),mode=4,extras={'d1IndexOffset':pr['off'],'d1IndexCount':pr['count'],'nativeMaterialCandidates':pr['materials'],'nativeRealMaterialCandidates':pr['real_materials']}))
            mesh_i=len(g.meshes); g.meshes.append(Mesh(name=f'{tag}_mesh{mi}',primitives=gps,extras={'d1Model':tag,'d1Entity':entity,'d1MeshIndex':mi}))
            node_i=len(g.nodes); g.nodes.append(Node(name=f'{tag}_mesh{mi}',mesh=mesh_i,extras={'d1Model':tag,'d1Entity':entity})); mesh_nodes.append(node_i)
        model_node=len(g.nodes); g.nodes.append(Node(name=f'{tag}_Entity_{entity}',children=mesh_nodes,extras={'d1Model':tag,'d1Entity':entity,'artArrangement':ARRANGEMENT})); g.nodes[0].children.append(model_node); reports.append(mrep)

    P=np.vstack(all_pos); pmin=P.min(axis=0); pmax=P.max(axis=0); center=(pmin+pmax)/2
    g.nodes[0].translation=[float(-x) for x in center]
    total_tri=sum(x['lod1_triangles'] for m in reports for x in m['meshes'])
    g.extras={'d1Gjallarhorn':{'inventoryItemHashYear3':'D471D331','artArrangementIndex':1229,'weaponPatternIndex':39,'entityCount':6,'modelCount':6,'meshCount':8,'models':list(MODEL_TO_ENTITY),'geometryPackageIds':['011C','011E','0139'],'presentationTranslation':[-float(x) for x in center],'nativeAssemblyPolicy':'six retail-selected models in shared model coordinates; no invented attachment transform','materialPolicy':'neutral placeholders retain exact native material hashes'}}
    a.out.parent.mkdir(parents=True,exist_ok=True); g.save_binary(str(a.out))
    report={'inventory_item':'D471D331','arrangement':1229,'weapon_pattern':39,'models':reports,'total_lod1_triangles':int(total_tri),'bbox_min':pmin.tolist(),'bbox_max':pmax.tolist(),'bbox_center':center.tolist(),'output':str(a.out),'output_bytes':a.out.stat().st_size}
    a.report.parent.mkdir(parents=True,exist_ok=True); a.report.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'models':len(reports),'meshes':sum(x['mesh_count'] for x in reports),'triangles':int(total_tri),'bbox_min':pmin.tolist(),'bbox_max':pmax.tolist(),'bytes':a.out.stat().st_size},indent=2))

if __name__=='__main__': main()
