#!/usr/bin/env python3
from __future__ import annotations
import argparse, copy, hashlib, json, math, struct
from pathlib import Path
import numpy as np

COMP_DT={5120:np.int8,5121:np.uint8,5122:np.int16,5123:np.uint16,5125:np.uint32,5126:np.float32}
TYPE_N={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}
P=np.array([[0.,1.,0.,0.],[0.,0.,1.,0.],[1.,0.,0.,0.],[0.,0.,0.,1.]],dtype=np.float64)
PINV=P.T

def load_json(path:Path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def read_glb(path:Path):
    raw=path.read_bytes(); magic,ver,total=struct.unpack_from('<4sII',raw,0)
    if magic!=b'glTF' or ver!=2 or total!=len(raw): raise ValueError('invalid GLB')
    off=12; chunks=[]
    while off<total:
        ln,typ=struct.unpack_from('<II',raw,off); off+=8
        chunks.append((typ,raw[off:off+ln])); off+=ln
    if not chunks or chunks[0][0]!=0x4E4F534A: raise ValueError('missing JSON chunk')
    g=json.loads(chunks[0][1].decode('utf-8').rstrip('\x00 '))
    b=chunks[1][1] if len(chunks)>1 and chunks[1][0]==0x004E4942 else b''
    return g,b

def accessor(g,b,idx):
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

def quat_matrix(q):
    x,y,z,w=map(float,q); n=x*x+y*y+z*z+w*w
    if n<=0: raise ValueError('zero quaternion')
    s=2.0/n; xx=x*x*s; yy=y*y*s; zz=z*z*s; xy=x*y*s; xz=x*z*s; yz=y*z*s; wx=w*x*s; wy=w*y*s; wz=w*z*s
    return np.array([[1-(yy+zz),xy-wz,xz+wy,0],[xy+wz,1-(xx+zz),yz-wx,0],[xz-wy,yz+wx,1-(xx+yy),0],[0,0,0,1]],dtype=np.float64)

def srt_matrix(scale,q,t):
    M=quat_matrix(q); M[:3,:3]*=float(scale); M[:3,3]=np.asarray(t,dtype=np.float64); return M

def matrix_quat(R):
    m=np.asarray(R,dtype=np.float64); tr=float(np.trace(m))
    if tr>0:
        s=math.sqrt(tr+1.0)*2; w=0.25*s; x=(m[2,1]-m[1,2])/s; y=(m[0,2]-m[2,0])/s; z=(m[1,0]-m[0,1])/s
    elif m[0,0]>m[1,1] and m[0,0]>m[2,2]:
        s=math.sqrt(1+m[0,0]-m[1,1]-m[2,2])*2; w=(m[2,1]-m[1,2])/s; x=0.25*s; y=(m[0,1]+m[1,0])/s; z=(m[0,2]+m[2,0])/s
    elif m[1,1]>m[2,2]:
        s=math.sqrt(1+m[1,1]-m[0,0]-m[2,2])*2; w=(m[0,2]-m[2,0])/s; x=(m[0,1]+m[1,0])/s; y=0.25*s; z=(m[1,2]+m[2,1])/s
    else:
        s=math.sqrt(1+m[2,2]-m[0,0]-m[1,1])*2; w=(m[1,0]-m[0,1])/s; x=(m[0,2]+m[2,0])/s; y=(m[1,2]+m[2,1])/s; z=0.25*s
    q=np.array([x,y,z,w],dtype=np.float64); q/=np.linalg.norm(q)
    if q[3]<0: q=-q
    return q

def decompose_uniform(M):
    t=M[:3,3].copy(); A=M[:3,:3]; scales=np.linalg.norm(A,axis=0); s=float(scales.mean())
    if not np.allclose(scales,s,atol=2e-5,rtol=2e-5): raise ValueError(f'nonuniform scale {scales}')
    R=A/s
    if np.linalg.det(R)<0: raise ValueError('reflection in bind transform')
    if not np.allclose(R.T@R,np.eye(3),atol=3e-5): raise ValueError('non-orthonormal bind rotation')
    return t,matrix_quat(R),np.array([s,s,s],dtype=np.float64)

def append_view(g,buf:bytearray,payload:bytes,target=None):
    while len(buf)%4: buf.append(0)
    off=len(buf); buf.extend(payload)
    bv={'buffer':0,'byteOffset':off,'byteLength':len(payload)}
    if target is not None: bv['target']=target
    g.setdefault('bufferViews',[]).append(bv)
    return len(g['bufferViews'])-1

def append_accessor(g,buf,arr,typ,component=5126,minmax=False):
    if component!=5126: raise ValueError('only FLOAT append implemented')
    a=np.asarray(arr,dtype='<f4')
    bv=append_view(g,buf,a.tobytes(order='C'))
    rec={'bufferView':bv,'byteOffset':0,'componentType':component,'count':len(a),'type':typ}
    if minmax:
        flat=a.reshape(len(a),-1); rec['min']=flat.min(0).astype(float).tolist(); rec['max']=flat.max(0).astype(float).tolist()
    g.setdefault('accessors',[]).append(rec); return len(g['accessors'])-1

def write_glb(path:Path,g,buf:bytearray):
    g['buffers']=[{'byteLength':len(buf)}]
    jb=json.dumps(g,separators=(',',':'),ensure_ascii=False).encode('utf-8')
    while len(jb)%4: jb+=b' '
    bb=bytes(buf)
    while len(bb)%4: bb+=b'\0'
    total=12+8+len(jb)+8+len(bb)
    out=struct.pack('<4sII',b'glTF',2,total)+struct.pack('<II',len(jb),0x4E4F534A)+jb+struct.pack('<II',len(bb),0x004E4942)+bb
    path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(out)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--input-glb',type=Path,required=True)
    ap.add_argument('--skeleton',type=Path,required=True)
    ap.add_argument('--animation',type=Path,required=True)
    ap.add_argument('--fps',type=float,default=30.0)
    ap.add_argument('--report',type=Path,required=True)
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args()
    if a.fps<=0: raise ValueError('fps must be positive')
    g,b=read_glb(a.input_glb); sk=load_json(a.skeleton); aa=load_json(a.animation)
    if len(aa)!=1: raise ValueError('expected exactly one published animation')
    anim=aa[0]; d=sk['definition']; nodes=d['nodes']
    if len(nodes)!=72 or len(d['default_object_space_transforms'])!=72 or len(d['default_inverse_object_space_transforms'])!=72: raise ValueError('published skeleton must have 72 transforms/nodes')
    if anim.get('node_count')!=72 or anim.get('rig_control_count')!=72: raise ValueError('published animation must be 72/72')
    frame_count=int(anim['frame_count'])
    if frame_count!=len(anim['animated_bone_data']['transform_stream_header']['streams']['frames']): raise ValueError('animation frame count mismatch')
    basis=(g.get('extras') or {}).get('d1TigerMeshBasis')
    if not basis: raise ValueError('input GLB lacks d1TigerMeshBasis evidence')
    old_root=[i for i,n in enumerate(g.get('nodes',[])) if n.get('name')=='D1_Guardian_Skeleton']
    if len(old_root)!=1: raise ValueError(f'expected one old D1_Guardian_Skeleton root, got {old_root}')
    old_root=old_root[0]
    mesh_prefix=max((i for i,n in enumerate(g['nodes']) if n.get('mesh') is not None),default=-1)+1
    if any(n.get('mesh') is not None for n in g['nodes'][mesh_prefix:]): raise ValueError('mesh node appears after skeleton suffix')
    if old_root < mesh_prefix: raise ValueError('old skeleton root overlaps mesh prefix')
    joint_domain=set(); weighted_vertices=0
    for n in g['nodes'][:mesh_prefix]:
        mi=n.get('mesh')
        if mi is None: continue
        for p in g['meshes'][mi]['primitives']:
            attrs=p.get('attributes') or {}
            if 'JOINTS_0' not in attrs or 'WEIGHTS_0' not in attrs: raise ValueError('mesh primitive lacks exact source skin attributes')
            j=accessor(g,b,attrs['JOINTS_0']); w=accessor(g,b,attrs['WEIGHTS_0']).astype(np.float64)
            if j.shape!=w.shape or j.shape[1]!=4: raise ValueError('unexpected skin accessor shape')
            nz=w>0
            joint_domain.update(int(x) for x in j[nz].tolist()); weighted_vertices+=len(j)
            if np.any(j[nz]>=72): raise ValueError('source joint outside published 72 palette')
            if not np.allclose(w.sum(1),1.0,atol=2e-5): raise ValueError('exported weights do not sum to one')
    if not {27,28}.issubset(joint_domain): raise ValueError('expected shoulder twist fixup source indices 27/28 absent')
    keep_nodes=copy.deepcopy(g['nodes'][:mesh_prefix]); g['nodes']=keep_nodes
    scene=g['scenes'][g.get('scene',0)]; scene['nodes']=[i for i in scene.get('nodes',[]) if i<mesh_prefix]
    g.pop('skins',None); g.pop('animations',None)
    globals_g=[]; ibms=[]; inv_errors=[]
    for tr,itr in zip(d['default_object_space_transforms'],d['default_inverse_object_space_transforms']):
        M=P@srt_matrix(tr['ts'][3],tr['r'],tr['ts'][:3])@PINV
        IM=P@srt_matrix(itr['ts'][3],itr['r'],itr['ts'][:3])@PINV
        globals_g.append(M); ibms.append(IM); inv_errors.append(float(np.max(np.abs(M@IM-np.eye(4)))))
    if max(inv_errors)>1e-4: raise ValueError(f'published inverse bind mismatch {max(inv_errors)}')
    joint_nodes=[]; base=len(g['nodes'])
    for i,node in enumerate(nodes):
        p=int(node['parent_node_index']); L=globals_g[i] if p<0 else ibms[p]@globals_g[i]
        t,q,s=decompose_uniform(L)
        rec={'name':node['name']['string'],'translation':t.astype(float).tolist(),'rotation':q.astype(float).tolist(),'scale':s.astype(float).tolist(),
             'extras':{'d1PublishedPlayerBoneIndex':i,'d1PublishedPlayerBoneHash':int(node['name']['hash'])}}
        g['nodes'].append(rec); joint_nodes.append(base+i)
    for i,node in enumerate(nodes):
        p=int(node['parent_node_index'])
        if p>=0: g['nodes'][base+p].setdefault('children',[]).append(base+i)
    wrapper=len(g['nodes']); g['nodes'].append({'name':'D1_Bungie_Published_Player_Skeleton','children':[base],
        'extras':{'source':'/common/destiny_content/animations/destiny_player_skeleton.js','nodeCount':72}})
    scene.setdefault('nodes',[]).append(wrapper)
    buf=bytearray(b)
    ibm_arr=np.asarray(ibms,dtype=np.float32).transpose(0,2,1).reshape(72,16)
    ibm_acc=append_accessor(g,buf,ibm_arr,'MAT4')
    g['skins']=[{'name':'D1_Bungie_Published_Player_Skin','inverseBindMatrices':ibm_acc,'joints':joint_nodes,'skeleton':base,
                 'extras':{'jointPalette':'exact published D1 player-preview 72-node order'}}]
    for n in g['nodes'][:mesh_prefix]:
        if n.get('mesh') is not None: n['skin']=0
        else: n.pop('skin',None)
    sb=anim['static_bone_data']; ab=anim['animated_bone_data']; sf=sb['transform_stream_header']['streams']['frames'][0]; afs=ab['transform_stream_header']['streams']['frames']
    sm={c:{int(n):i for i,n in enumerate(sb[c+'_control_map'])} for c in ('scale','rotation','translation')}
    am={c:{int(n):i for i,n in enumerate(ab[c+'_control_map'])} for c in ('scale','rotation','translation')}
    for c in ('scale','rotation','translation'):
        if set(sm[c])|set(am[c]) != set(range(72)) or set(sm[c])&set(am[c]): raise ValueError(f'{c} static/animated maps do not partition 72 nodes')
    times=(np.arange(frame_count,dtype=np.float32)/np.float32(a.fps)).reshape(-1,1)
    time_acc=append_accessor(g,buf,times,'SCALAR',minmax=True)
    rotations=[[] for _ in range(72)]; translations=[[] for _ in range(72)]; scales=[[] for _ in range(72)]
    for af in afs:
        for i in range(72):
            sc=sf['scales'][sm['scale'][i]] if i in sm['scale'] else af['scales'][am['scale'][i]]
            q=sf['rotations'][sm['rotation'][i]] if i in sm['rotation'] else af['rotations'][am['rotation'][i]]
            t=sf['translations'][sm['translation'][i]] if i in sm['translation'] else af['translations'][am['translation'][i]]
            scales[i].append([float(sc)]*3)
            rotations[i].append([float(q[1]),float(q[2]),float(q[0]),float(q[3])])
            translations[i].append([float(t[1]),float(t[2]),float(t[0])])
    samplers=[]; channels=[]
    for i in range(72):
        for path,vals,typ in [('translation',translations[i],'VEC3'),('rotation',rotations[i],'VEC4'),('scale',scales[i],'VEC3')]:
            outacc=append_accessor(g,buf,np.asarray(vals,dtype=np.float32),typ)
            si=len(samplers); samplers.append({'input':time_acc,'output':outacc,'interpolation':'LINEAR'}); channels.append({'sampler':si,'target':{'node':base+i,'path':path}})
    g['animations']=[{'name':'D1_Bungie_Published_Player_Preview_Animation','samplers':samplers,'channels':channels,
        'extras':{'source':'/common/destiny_content/animations/destiny_player_animation.js','sourceFrameCount':frame_count,
                  'durationInFrames':anim.get('duration_in_frames'),'serializationFps':a.fps,
                  'fpsPolicy':'glTF seconds require a cadence; 30 fps mirrors the archived viewer nominal behavior of +0.5 source frame per requestAnimationFrame at 60 Hz'}}]
    ex=g.setdefault('extras',{})
    ex['d1BungiePublishedPlayerPreview']={'skeletonSha256':hashlib.sha256(a.skeleton.read_bytes()).hexdigest(),
        'animationSha256':hashlib.sha256(a.animation.read_bytes()).hexdigest(),'nodeCount':72,'animationFrames':frame_count,
        'sourceJointDomain':sorted(joint_domain),'weightedExportVertices':weighted_vertices,
        'semantics':'Exact PS4 Spektar JOINTS/WEIGHTS interpreted in exact Bungie published 72-node player-preview palette. This does not claim a byte-identical PS4 runtime skeleton owner.'}
    write_glb(a.output,g,buf)
    rep={'schema':'d1_bungie_published_player_preview_bind/v1','input':str(a.input_glb),'output':str(a.output),
         'output_bytes':a.output.stat().st_size,'output_sha256':hashlib.sha256(a.output.read_bytes()).hexdigest(),
         'skeleton_nodes':72,'source_joint_domain':sorted(joint_domain),'weighted_export_vertices':weighted_vertices,
         'max_bind_inverse_error':max(inv_errors),'animation_frames':frame_count,'animation_channels':len(channels),'animation_samplers':len(samplers),
         'serialization_fps':a.fps,'shoulder_fixup_indices':{'27':nodes[27]['name'],'28':nodes[28]['name']},
         'policy':'No raw joint index is remapped to a different semantic. Exact source indices are evaluated against the exact published 72-node player-preview palette. Old 67-node diagnostic skeleton/animation are removed.'}
    a.report.parent.mkdir(parents=True,exist_ok=True); a.report.write_text(json.dumps(rep,indent=2)+'\n')
    print(json.dumps(rep,indent=2))
if __name__=='__main__': main()
