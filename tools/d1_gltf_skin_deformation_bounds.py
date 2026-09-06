#!/usr/bin/env python3
"""Independently evaluate glTF skin deformation at exact animation keyframes.

This validator reads the serialized GLB rather than the source parser state. It is
intended to catch coordinate-basis, joint-palette, inverse-bind and animation-node
wiring failures that can otherwise produce plausible metadata but exploded meshes.
"""
from __future__ import annotations
import argparse,json,struct
from pathlib import Path
import numpy as np

COMP_DT={5120:np.int8,5121:np.uint8,5122:np.int16,5123:np.uint16,5125:np.uint32,5126:np.float32}
TYPE_N={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}

def read_glb(path:Path):
    raw=path.read_bytes(); magic,ver,total=struct.unpack_from('<4sII',raw,0)
    if magic!=b'glTF' or ver!=2 or total!=len(raw): raise ValueError('invalid GLB')
    off=12; chunks=[]
    while off<total:
        ln,typ=struct.unpack_from('<II',raw,off); off+=8; chunks.append((typ,raw[off:off+ln])); off+=ln
    g=json.loads(chunks[0][1].decode('utf-8').rstrip('\x00 ')); b=chunks[1][1]
    return g,b

def acc(g,b,idx):
    a=g['accessors'][idx]
    if a.get('sparse'): raise ValueError('sparse accessor unsupported')
    bv=g['bufferViews'][a['bufferView']]; dt=np.dtype(COMP_DT[a['componentType']]); n=TYPE_N[a['type']]
    base=bv.get('byteOffset',0)+a.get('byteOffset',0); stride=bv.get('byteStride',dt.itemsize*n); count=a['count']
    if stride==dt.itemsize*n:
        x=np.frombuffer(b,dtype=dt,count=count*n,offset=base).copy().reshape(count,n)
    else:
        x=np.empty((count,n),dtype=dt)
        for i in range(count): x[i]=np.frombuffer(b,dtype=dt,count=n,offset=base+i*stride)
    return x

def qmat(q):
    x,y,z,w=map(float,q); n=x*x+y*y+z*z+w*w
    if n<=0: raise ValueError('zero quaternion')
    s=2/n; xx=x*x*s; yy=y*y*s; zz=z*z*s; xy=x*y*s; xz=x*z*s; yz=y*z*s; wx=w*x*s; wy=w*y*s; wz=w*z*s
    M=np.eye(4); M[:3,:3]=[[1-(yy+zz),xy-wz,xz+wy],[xy+wz,1-(xx+zz),yz-wx],[xz-wy,yz+wx,1-(xx+yy)]]; return M

def trs(n):
    if 'matrix' in n: return np.asarray(n['matrix'],dtype=float).reshape(4,4).T
    M=qmat(n.get('rotation',[0,0,0,1])); s=np.asarray(n.get('scale',[1,1,1]),float); M[:3,:3]=M[:3,:3]@np.diag(s); M[:3,3]=np.asarray(n.get('translation',[0,0,0]),float); return M

def parents(g):
    p=[-1]*len(g['nodes'])
    for i,n in enumerate(g['nodes']):
        for c in n.get('children',[]):
            if p[c]!=-1: raise ValueError(f'node {c} has multiple parents')
            p[c]=i
    return p

def globals_from_locals(local,p):
    G=[None]*len(local)
    def one(i):
        if G[i] is None: G[i]=local[i] if p[i]<0 else one(p[i])@local[i]
        return G[i]
    for i in range(len(local)): one(i)
    return G

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('glb',type=Path); ap.add_argument('--frame',action='append',type=int,default=[]); ap.add_argument('-o','--output',type=Path,required=True); a=ap.parse_args()
    g,b=read_glb(a.glb)
    if len(g.get('skins',[]))!=1 or len(g.get('animations',[]))!=1: raise ValueError('expected one skin and one animation')
    skin=g['skins'][0]; joints=skin['joints']; ib=acc(g,b,skin['inverseBindMatrices']).reshape(len(joints),4,4).transpose(0,2,1).astype(float)
    p=parents(g); base_local=[trs(n) for n in g['nodes']]; base_global=globals_from_locals(base_local,p)
    bind_err=max(float(np.max(np.abs(base_global[joints[k]]@ib[k]-np.eye(4)))) for k in range(len(joints)))
    anim=g['animations'][0]; sam=anim['samplers']; chans=anim['channels']
    # Require a common exact keyframe count and LINEAR tracks for this validation path.
    frame_count=None; tracks={}
    for ch in chans:
        s=sam[ch['sampler']]
        if s.get('interpolation','LINEAR')!='LINEAR': raise ValueError('validator only accepts LINEAR tracks')
        times=acc(g,b,s['input']).reshape(-1); vals=acc(g,b,s['output'])
        if frame_count is None: frame_count=len(times)
        if len(times)!=frame_count or len(vals)!=frame_count: raise ValueError('animation track length mismatch')
        tracks[(ch['target']['node'],ch['target']['path'])]=vals
    frames=a.frame or [0,frame_count-1]
    for f in frames:
        if not 0<=f<frame_count: raise ValueError(f'frame {f} outside 0..{frame_count-1}')
    # Mesh nodes in this diagnostic must be identity world nodes; this keeps the CPU skin equation unambiguous.
    mesh_nodes=[i for i,n in enumerate(g['nodes']) if n.get('mesh') is not None and n.get('skin')==0]
    for i in mesh_nodes:
        if not np.allclose(base_global[i],np.eye(4),atol=1e-6): raise ValueError(f'mesh node {i} has nonidentity transform')
    rows=[]
    for f in frames:
        local=[]
        for i,n in enumerate(g['nodes']):
            nn=dict(n)
            for path in ('translation','rotation','scale'):
                v=tracks.get((i,path))
                if v is not None: nn[path]=v[f].astype(float).tolist()
            local.append(trs(nn))
        G=globals_from_locals(local,p); mn=np.array([np.inf]*3); mx=np.array([-np.inf]*3); verts=0
        for ni in mesh_nodes:
            mi=g['nodes'][ni]['mesh']
            for prim in g['meshes'][mi]['primitives']:
                at=prim['attributes']; pos=acc(g,b,at['POSITION']).astype(float); ji=acc(g,b,at['JOINTS_0']).astype(int); wt=acc(g,b,at['WEIGHTS_0']).astype(float)
                hp=np.c_[pos,np.ones(len(pos))]; out=np.zeros((len(pos),4),float)
                for lane in range(4):
                    w=wt[:,lane]; nz=w!=0
                    if not np.any(nz): continue
                    for j in np.unique(ji[nz,lane]):
                        m=nz & (ji[:,lane]==j); T=G[joints[j]]@ib[j]; out[m]+=w[m,None]*(hp[m]@T.T)
                pts=out[:,:3]; mn=np.minimum(mn,pts.min(0)); mx=np.maximum(mx,pts.max(0)); verts+=len(pts)
        rows.append({'frame':f,'min':mn.tolist(),'max':mx.tolist(),'span':(mx-mn).tolist(),'vertices':verts})
        print('frame',f,'min',mn,'max',mx,'span',mx-mn,'vertices',verts)
    report={'schema':'d1_gltf_skin_deformation_bounds/v1','glb':str(a.glb),'skin_joint_count':len(joints),'animation_frame_count':frame_count,'bind_identity_max_error':bind_err,'samples':rows}
    a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(report,indent=2)+'\n')
    print('bind identity max error',bind_err)
if __name__=='__main__': main()
