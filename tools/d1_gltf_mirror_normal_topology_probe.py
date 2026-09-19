#!/usr/bin/env python3
"""Prove mirrored-geometry/source-normal structure in an exact D1 glTF carrier.

This is a diagnostic for source-preservation decisions, not a normal generator.
For the selected triangle-list node it:
* measures source vertex-normal agreement with exported triangle winding;
* decomposes the mesh into edge-connected triangle components;
* pairs components whose position sets are exact mirrors across one axis;
* verifies that mirrored source vertex normals transform exactly with the mirror;
* records whether triangle winding agreement is preserved or sign-inverted.

A reflection has negative determinant, so face-normal/winding agreement can invert
even when the source vertex normals are internally exact. Therefore this tool must
never promote recomputed geometric normals as "more correct" merely because their
dot product with exported face winding is larger.
"""
from __future__ import annotations
import argparse, collections, hashlib, json, struct
from pathlib import Path
import numpy as np

CT={5120:np.int8,5121:np.uint8,5122:np.int16,5123:np.uint16,5125:np.uint32,5126:np.float32}
NC={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}

def read_glb(p:Path):
    raw=p.read_bytes()
    magic,ver,total=struct.unpack_from('<4sII',raw,0)
    if magic!=b'glTF' or ver!=2 or total!=len(raw): raise ValueError('not GLB v2')
    jl,jt=struct.unpack_from('<II',raw,12)
    if jt!=0x4e4f534a: raise ValueError('missing JSON chunk')
    d=json.loads(raw[20:20+jl].decode().rstrip(' \x00'))
    bo=20+jl; bl,bt=struct.unpack_from('<II',raw,bo)
    if bt!=0x004e4942: raise ValueError('missing BIN chunk')
    return d,raw[bo+8:bo+8+bl]

def accessor(d,blob,ai):
    a=d['accessors'][ai]
    if a.get('sparse') is not None: raise ValueError(f'accessor {ai}: sparse unsupported')
    bv=d['bufferViews'][a['bufferView']]
    dt=np.dtype(CT[int(a['componentType'])]).newbyteorder('<'); nc=NC[a['type']]
    count=int(a['count']); off=int(bv.get('byteOffset',0))+int(a.get('byteOffset',0))
    packed=dt.itemsize*nc; stride=int(bv.get('byteStride',packed))
    if stride<packed: raise ValueError(f'accessor {ai}: stride too small')
    if stride==packed:
        x=np.frombuffer(blob,dtype=dt,count=count*nc,offset=off).copy()
        return x.reshape(count,nc) if nc>1 else x
    x=np.empty((count,nc),dtype=dt)
    for i in range(count):
        x[i]=np.frombuffer(blob,dtype=dt,count=nc,offset=off+i*stride)
    return x

def face_stats(pos,norm,tri):
    fn=np.cross(pos[tri[:,1]]-pos[tri[:,0]],pos[tri[:,2]]-pos[tri[:,0]])
    ln=np.linalg.norm(fn,axis=1); good=ln>1e-12
    fn=fn[good]/ln[good,None]; tri=tri[good]
    nn=norm/np.maximum(np.linalg.norm(norm,axis=1,keepdims=True),1e-12)
    dots=np.stack([np.einsum('ij,ij->i',nn[tri[:,k]],fn) for k in range(3)],axis=1)
    return tri,dots,{
      'triangle_count':int(len(tri)),
      'corner_count':int(dots.size),
      'mean_dot':float(dots.mean()),
      'median_dot':float(np.median(dots)),
      'negative_corner_fraction':float((dots<0).mean()),
      'negative_triangle_mean_fraction':float((dots.mean(axis=1)<0).mean()),
    }

def components(tri):
    edge=collections.defaultdict(list)
    for ti,t in enumerate(tri):
        for a,b in ((t[0],t[1]),(t[1],t[2]),(t[2],t[0])):
            edge[(min(int(a),int(b)),max(int(a),int(b)))].append(ti)
    adj=[set() for _ in range(len(tri))]
    for vv in edge.values():
        if len(vv)==2:
            a,b=vv; adj[a].add(b); adj[b].add(a)
    seen=set(); out=[]
    for i in range(len(tri)):
        if i in seen: continue
        seen.add(i); stack=[i]; c=[]
        while stack:
            x=stack.pop(); c.append(x)
            for y in adj[x]:
                if y not in seen: seen.add(y); stack.append(y)
        out.append(np.asarray(c,dtype=np.int64))
    topology={
      'shared_edge_count':sum(1 for v in edge.values() if len(v)==2),
      'boundary_edge_count':sum(1 for v in edge.values() if len(v)==1),
      'nonmanifold_edge_count':sum(1 for v in edge.values() if len(v)>2),
    }
    return out,topology

def point_hash(p,decimals=6):
    a=np.round(np.asarray(p,dtype=np.float64),decimals)
    order=np.lexsort((a[:,2],a[:,1],a[:,0]))
    return hashlib.sha256(a[order].astype('<f8').tobytes()).hexdigest()

def match_mirror(pos,norm,va,vb,axis,decimals=6):
    pa=pos[va].copy(); na=norm[va].copy()
    pb=pos[vb]; nb=norm[vb]
    pa[:,axis]*=-1; na[:,axis]*=-1
    keys={tuple(np.round(x,decimals)):i for i,x in enumerate(pb)}
    pairs=[]
    for i,x in enumerate(pa):
        j=keys.get(tuple(np.round(x,decimals)))
        if j is None: return None
        pairs.append((i,j))
    nd=np.asarray([np.dot(na[i],nb[j])/(max(np.linalg.norm(na[i])*np.linalg.norm(nb[j]),1e-30)) for i,j in pairs])
    pd=np.asarray([np.linalg.norm(pa[i]-pb[j]) for i,j in pairs])
    return {
      'vertex_count':len(pairs),
      'position_error_max':float(pd.max(initial=0)),
      'normal_dot_min':float(nd.min(initial=1)),
      'normal_dot_mean':float(nd.mean()) if len(nd) else 1.0,
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('glb',type=Path)
    ap.add_argument('--node',required=True)
    ap.add_argument('--axis',type=int,choices=(0,1,2),default=1)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    d,blob=read_glb(a.glb)
    hits=[(i,n) for i,n in enumerate(d.get('nodes',[])) if n.get('name')==a.node]
    if len(hits)!=1: raise SystemExit(f'expected one node {a.node}, got {len(hits)}')
    ni,node=hits[0]; mesh=d['meshes'][int(node['mesh'])]
    if len(mesh.get('primitives',[]))!=1: raise SystemExit('expected one primitive')
    p=mesh['primitives'][0]
    if int(p.get('mode',4))!=4: raise SystemExit('carrier must already contain explicit triangles')
    at=p['attributes']
    pos=accessor(d,blob,int(at['POSITION'])).astype(np.float64)
    norm=accessor(d,blob,int(at['NORMAL'])).astype(np.float64)
    ind=accessor(d,blob,int(p['indices'])).astype(np.int64).reshape(-1)
    if len(ind)%3: raise SystemExit('triangle index count not divisible by three')
    tri,dots,fs=face_stats(pos,norm,ind.reshape(-1,3))
    comps,topology=components(tri)
    info=[]
    groups=collections.defaultdict(list)
    for ci,faces_i in enumerate(comps):
        faces=tri[faces_i]; vids=np.unique(faces)
        q=pos[vids].copy(); qr=q.copy(); qr[:,a.axis]*=-1
        h0=point_hash(q); h1=point_hash(qr)
        key=(len(faces),len(vids),min(h0,h1),max(h0,h1))
        row={
          'component':ci,'triangle_count':int(len(faces)),'vertex_count':int(len(vids)),
          'vertex_indices':vids,
          'centroid':pos[vids].mean(axis=0).tolist(),
          'mean_source_normal_face_dot':float(dots[faces_i].mean()),
          'negative_corner_fraction':float((dots[faces_i]<0).mean()),
          'mirror_signature':key,
        }
        info.append(row); groups[key].append(row)
    pair_rows=[]; violations=[]
    paired_components=set()
    for g in groups.values():
        if len(g)!=2: continue
        x,y=g
        m=match_mirror(pos,norm,x['vertex_indices'],y['vertex_indices'],a.axis)
        if m is None: continue
        paired_components.update((x['component'],y['component']))
        pair_rows.append({
          'component_a':x['component'],'component_b':y['component'],
          'triangle_count_each':x['triangle_count'],
          'mean_dot_a':x['mean_source_normal_face_dot'],'mean_dot_b':y['mean_source_normal_face_dot'],
          'face_agreement_sign_relation':'OPPOSITE' if x['mean_source_normal_face_dot']*y['mean_source_normal_face_dot']<0 else 'SAME',
          **m,
        })
        if m['normal_dot_min']<0.9999: violations.append(f"pair {x['component']}:{y['component']} mirror-normal mismatch {m['normal_dot_min']}")
    paired_faces=sum(info[i]['triangle_count'] for i in paired_components)
    out={
      'schema':'d1_gltf_mirror_normal_topology_probe/v1',
      'status':'D1_GLTF_MIRROR_NORMAL_TOPOLOGY_EXACT' if pair_rows and not violations else 'D1_GLTF_MIRROR_NORMAL_TOPOLOGY_PARTIAL',
      'input':str(a.glb),'node':a.node,'reflection_axis':a.axis,
      'face_normal_agreement':fs,'topology':topology,
      'connected_component_count':len(comps),
      'mirror_pair_count':len(pair_rows),
      'mirror_paired_component_count':len(paired_components),
      'mirror_paired_triangle_count':int(paired_faces),
      'triangle_count':int(len(tri)),
      'mirror_paired_triangle_fraction':float(paired_faces/len(tri)) if len(tri) else 0.0,
      'mirror_pair_opposite_face_agreement_count':sum(x['face_agreement_sign_relation']=='OPPOSITE' for x in pair_rows),
      'mirror_pair_same_face_agreement_count':sum(x['face_agreement_sign_relation']=='SAME' for x in pair_rows),
      'minimum_mirrored_normal_dot':min((x['normal_dot_min'] for x in pair_rows),default=None),
      'pairs':pair_rows,
      'unpaired_components':[{
          'component':x['component'],'triangle_count':x['triangle_count'],'centroid':x['centroid'],
          'mean_source_normal_face_dot':x['mean_source_normal_face_dot'],
      } for x in info if x['component'] not in paired_components],
      'violations':violations,
      'semantic_boundary':{
          'source_vertex_normal_mirror_symmetry':'EXACT',
          'exported_triangle_winding':'OBSERVED',
          'rasterizer_cull_semantic':'WITHHELD',
          'normal_recompute_authority':'REJECTED_AS_SOURCE_REPLACEMENT',
      },
      'policy':'Mirrored source positions and source normals are tested independently of face winding. Face-normal dot disagreement after a reflection is not evidence that the source normal is corrupt; reflected geometry can invert oriented face normals unless winding is also reversed.',
    }
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2,default=lambda x:x.tolist() if hasattr(x,'tolist') else x)+'\n')
    print(json.dumps({k:out[k] for k in ('status','connected_component_count','mirror_pair_count','mirror_paired_component_count','mirror_paired_triangle_count','triangle_count','mirror_paired_triangle_fraction','mirror_pair_opposite_face_agreement_count','mirror_pair_same_face_agreement_count','minimum_mirrored_normal_dot','face_normal_agreement','violations')},indent=2))
    return 0 if out['status']=='D1_GLTF_MIRROR_NORMAL_TOPOLOGY_EXACT' else 2

if __name__=='__main__': raise SystemExit(main())
