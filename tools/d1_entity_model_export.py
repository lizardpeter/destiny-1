#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, struct, sys
from pathlib import Path
import numpy as np
import trimesh

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from d1_entry_extract import EntryReader
from d1_entity_model_probe import parse_model


def snorm16(a):
    x=np.asarray(a,dtype=np.float32)/32767.0
    return np.maximum(x,-1.0)
def hdr_stride(h): return struct.unpack_from('<h',h,4)[0]
def index_is32(h): return bool(h[1])

def byhash(r): return {e['tag_hash'].upper():e for e in r.entries}

def read_linked(r, m, h):
    e=m[h.upper()]; head=r.entry(e['index']); pe=m.get(e['reference'].upper())
    if not pe: raise KeyError(f'no local payload for {h} -> {e["reference"]}')
    return e,head,pe,r.entry(pe['index'])

def decode_vb0(data,stride):
    n=len(data)//stride
    if stride not in (8,12,16,28,32): raise ValueError(f'unsupported D1 buffer0 stride {stride:#x}')
    raw=np.frombuffer(data,dtype='<i2').reshape(n,stride//2)
    return snorm16(raw[:,:3])

def decode_vb1(data,stride,uvscale,uvtrans):
    n=len(data)//stride
    raw=np.frombuffer(data,dtype='<i2').reshape(n,stride//2)
    uv=norm=None; tangent=None; color=None
    if stride==0x0c:
        uv=snorm16(raw[:,:2]); norm=snorm16(raw[:,2:5])
    elif stride in (0x14,0x18):
        # D1 bufferIndex=1, with no pre-existing UVs: UV + padded normal +
        # tangent. Retail 0x18 adds one final int16 pair after the tangent;
        # its semantic is intentionally left unresolved and is not consumed.
        uv=snorm16(raw[:,:2]); norm=snorm16(raw[:,2:5]); tangent=snorm16(raw[:,6:9])
    elif stride==0x04:
        uv=snorm16(raw[:,:2])
    elif stride==0x08:
        norm=snorm16(raw[:,:3])
    elif stride==0x10:
        norm=snorm16(raw[:,:3]); tangent=snorm16(raw[:,4:7])
    else:
        raise ValueError(f'unsupported D1 buffer1 stride {stride:#x}')
    if uv is not None:
        uv=np.column_stack((uv[:,0]*uvscale[0]+uvtrans[0], uv[:,1]*(-uvscale[1])+1.0-uvtrans[1])).astype(np.float32)
    return uv,norm,tangent,color

def decode_indices(data,is32):
    return np.frombuffer(data,dtype='<u4' if is32 else '<u2').astype(np.int64)

def triangle_list_faces(values):
    values=np.asarray(values,dtype=np.int64)
    if len(values)%3: raise ValueError(f'triangle-list index count {len(values)} is not divisible by 3')
    return values.reshape((-1,3))

def triangle_strip_faces(values,restart_value):
    """Convert a Tiger/D1 triangle strip to an explicit triangle list.

    Winding parity resets after a primitive-restart index. Degenerate strip
    triangles are discarded. This is the same conversion validated on retail
    PS4 Vex 816CE09A and is now shared by the generic exporter.
    """
    out=[]; strip=[]
    for raw in np.asarray(values,dtype=np.int64).tolist():
        if raw==restart_value:
            strip.clear(); continue
        strip.append(int(raw))
        if len(strip)<3: continue
        tri_no=len(strip)-3
        a,b,c=strip[-3],strip[-2],strip[-1]
        if tri_no&1: a,b=b,a
        if a!=b and b!=c and a!=c: out.append((a,b,c))
    return np.asarray(out,dtype=np.int64).reshape((-1,3)) if out else np.empty((0,3),dtype=np.int64)

def primitive_faces(values,primitive_type,is32):
    if primitive_type==3:
        return triangle_list_faces(values)
    if primitive_type==5:
        return triangle_strip_faces(values,0xffffffff if is32 else 0xffff)
    raise ValueError(f'unsupported D1 primitive type {primitive_type}')

def parse_tag_hash(s):
    s=s.upper().removeprefix('0X'); return s.zfill(8)

def bounds2(a):
    if a is None or len(a)==0: return None
    return {'min':[float(x) for x in np.min(a,axis=0)],'max':[float(x) for x in np.max(a,axis=0)]}

def export_model(r, tag_hash, out_glb, out_json=None, unique_ranges=True):
    m=byhash(r); th=parse_tag_hash(tag_hash)
    e=m.get(th)
    if not e or e['reference'].upper()!='80801AB5': raise ValueError(f'{th} is not a local s_entity_model')
    b=r.entry(e['index']); model=parse_model(b,r.h['platform'])
    scene=trimesh.Scene(); report={'source_package':str(r.pkg),'platform':r.h['platform'],'model_tag_hash':th,'model_entry_index':e['index'],'mesh_count':model['mesh_count'],'meshes':[]}
    for mi,mesh in enumerate(model['meshes']):
        v1e,v1h,v1pe,v1d=read_linked(r,m,mesh['vertices1']); v2e,v2h,v2pe,v2d=read_linked(r,m,mesh['vertices2']); ie,ih,ipe,idata=read_linked(r,m,mesh['indices'])
        s0=hdr_stride(v1h); s1=hdr_stride(v2h); is32=index_is32(ih)
        pos=decode_vb0(v1d,s0)
        scale=np.asarray(mesh['model_scale'][:3],dtype=np.float32); trans=np.asarray(mesh['model_translation'][:3],dtype=np.float32)
        pos=(pos*scale+trans).astype(np.float32)
        uv,norm,tan,color=decode_vb1(v2d,s1,mesh['texcoord_scale'],mesh['texcoord_translation'])
        if len(pos)!=len(v2d)//s1: raise ValueError(f'mesh {mi}: vertex stream count mismatch')
        inds=decode_indices(idata,is32)
        ranges={}
        for pi,p in enumerate(mesh['parts']):
            key=(p['index_offset'],p['index_count'],p['primitive_type'])
            ranges.setdefault(key,[]).append((pi,p))
        if not unique_ranges:
            ranges={(p['index_offset'],p['index_count'],p['primitive_type'],pi):[(pi,p)] for pi,p in enumerate(mesh['parts'])}
        mrep={'mesh_index':mi,'model_scale':mesh['model_scale'],'model_translation':mesh['model_translation'],'texcoord_scale':mesh['texcoord_scale'],'texcoord_translation':mesh['texcoord_translation'],'uv_bounds':bounds2(uv),'vertices1':mesh['vertices1'],'vertices2':mesh['vertices2'],'indices':mesh['indices'],'vertex_count':len(pos),'vertex_stride0':s0,'vertex_stride1':s1,'index_width_bits':32 if is32 else 16,'stage_part_offsets':mesh.get('stage_part_offsets'),'stage_code':mesh.get('stage_code'),'primitive_groups':[]}
        for gi,(key,candidates) in enumerate(ranges.items()):
            off,count,prim=key[:3]
            sl=inds[off:off+count]
            if len(sl)!=count: raise ValueError(f'mesh {mi} group {gi}: short index range')
            faces_global=primitive_faces(sl,prim,is32)
            if len(faces_global)==0: continue
            if faces_global.max()>=len(pos): raise ValueError(f'mesh {mi} group {gi}: index out of vertex range')
            used,inv=np.unique(faces_global.reshape(-1),return_inverse=True); faces=inv.reshape((-1,3))
            vv=pos[used]; nn=norm[used] if norm is not None else None; uu=uv[used] if uv is not None else None
            materials=[]
            for pi,p in candidates:
                if p['material'] not in materials: materials.append(p['material'])
            material=trimesh.visual.material.PBRMaterial(name='candidate_materials_'+'_'.join(materials[:3]))
            visual=trimesh.visual.TextureVisuals(uv=uu,material=material) if uu is not None else None
            tm=trimesh.Trimesh(vertices=vv,faces=faces,vertex_normals=nn,visual=visual,process=False,validate=False)
            name=f'{th}_mesh{mi}_range{off}_{count}'
            tm.metadata={'model_tag_hash':th,'mesh_index':mi,'source_vertex_indices':used.tolist(),'candidate_materials':materials,'part_indices':[pi for pi,_ in candidates],'lod_values':sorted(set(p['lod'] for _,p in candidates)),'index_offset':off,'index_count':count,'primitive_type':prim}
            scene.add_geometry(tm,geom_name=name,node_name=name)
            mrep['primitive_groups'].append({'name':name,'index_offset':off,'index_count':count,'primitive_type':prim,'triangle_count':len(faces_global),'unique_vertex_count':len(used),'candidate_materials':materials,'part_indices':[pi for pi,_ in candidates],'lod_values':sorted(set(p['lod'] for _,p in candidates))})
        report['meshes'].append(mrep)
    out_glb.parent.mkdir(parents=True,exist_ok=True); scene.export(out_glb)
    report['glb']=str(out_glb); report['geometry_count']=len(scene.geometry); report['triangle_count']=sum(g['triangle_count'] for m in report['meshes'] for g in m['primitive_groups']); report['bounds']=scene.bounds.tolist() if scene.bounds is not None else None
    if out_json is None: out_json=out_glb.with_suffix('.json')
    out_json.write_text(json.dumps(report,indent=2)+'\n')
    return report

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('pkg',type=Path); ap.add_argument('--runtime',type=Path,required=True); ap.add_argument('--tag-hash',required=True); ap.add_argument('--out',type=Path,required=True); ap.add_argument('--json',type=Path); ap.add_argument('--all-part-variants',action='store_true')
    a=ap.parse_args(); r=EntryReader(a.pkg,a.runtime); rep=export_model(r,a.tag_hash,a.out,a.json,unique_ranges=not a.all_part_variants); print(json.dumps(rep,indent=2))
if __name__=='__main__': main()
