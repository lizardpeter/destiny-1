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

def transform_uv(uv,uvscale,uvtrans):
    if uv is None: return None
    uv=np.asarray(uv,dtype=np.float32)
    return np.column_stack((uv[:,0]*uvscale[0]+uvtrans[0], uv[:,1]*(-uvscale[1])+1.0-uvtrans[1])).astype(np.float32)

def decode_vb0_uv(data,stride,uvscale,uvtrans):
    """Decode D1 ROI UV0 that is resident in the primary position stream.

    For dynamic D1 mesh stride 0x0C the fourth int16 is position W. If W is
    +/-0x7FFF, bytes 8..11 are inline two-bone skin data and UV0 is absent from
    this stream. Otherwise bytes 8..11 are UV0. A mixed sentinel/non-sentinel
    stream would make one UV list structurally inconsistent, so it is rejected
    rather than guessed.
    """
    if stride!=0x0c: return None
    if len(data)%stride: raise ValueError(f'buffer0 byte count {len(data)} not divisible by stride {stride:#x}')
    raw=np.frombuffer(data,dtype='<i2').reshape((-1,6))
    w=raw[:,3]
    sentinel=np.logical_or(w==32767,w==-32767)
    if np.all(sentinel): return None
    if np.any(sentinel):
        raise ValueError('mixed +/-0x7FFF and ordinary position-W values in one D1 0x0C primary stream; UV0 source is ambiguous')
    return transform_uv(snorm16(raw[:,4:6]),uvscale,uvtrans)

def decode_vb1(data,stride,uvscale,uvtrans,primary_uv_exists=False,other_stride=-1):
    """Decode D1 ROI secondary vertex data with stream-pair UV state.

    Charm's ROI path keeps whether UV0 was already populated by buffer0. This
    matters for 0x14 and 0x18 secondary streams: with a pre-existing primary UV
    they begin with normal/tangent data instead of another UV0. The old generic
    exporter always assumed UV0 began buffer1, which is wrong for rigid Guardian
    0x0C primary meshes.
    """
    n=len(data)//stride
    raw=np.frombuffer(data,dtype='<i2').reshape(n,stride//2)
    uv=norm=None; tangent=None; color=None
    if stride==0x0c:
        if primary_uv_exists:
            raise ValueError('D1 stream pair exposes UV0 in both primary 0x0C and secondary 0x0C; refusing ambiguous UV set')
        uv=snorm16(raw[:,:2]); norm=snorm16(raw[:,2:5])
    elif stride==0x14:
        if primary_uv_exists:
            norm=snorm16(raw[:,0:3]); tangent=snorm16(raw[:,4:7])
            # Final four bytes are the D1 colour-slot lane in this layout.
            color=np.frombuffer(data,dtype=np.uint8).reshape(n,stride)[:,16:20].astype(np.float32)/255.0
        else:
            uv=snorm16(raw[:,:2]); norm=snorm16(raw[:,2:5]); tangent=snorm16(raw[:,6:9])
    elif stride==0x18:
        if other_stride==0x0c and primary_uv_exists:
            # D1 ROI _uvExists branch: normal + tangent + final unresolved/colour lane.
            norm=snorm16(raw[:,0:3]); tangent=snorm16(raw[:,4:7])
        else:
            # When buffer0 did not supply UV0 (including inline-skinned 0x0C and
            # 0x10 primary streams), the 0x18 secondary stream starts with UV0.
            uv=snorm16(raw[:,:2]); norm=snorm16(raw[:,2:5]); tangent=snorm16(raw[:,6:9])
    elif stride==0x04:
        if primary_uv_exists:
            raise ValueError('D1 stream pair exposes UV0 in both primary 0x0C and secondary 0x04; refusing ambiguous UV set')
        uv=snorm16(raw[:,:2])
    elif stride==0x08:
        norm=snorm16(raw[:,:3])
    elif stride==0x10:
        norm=snorm16(raw[:,:3]); tangent=snorm16(raw[:,4:7])
    else:
        raise ValueError(f'unsupported D1 buffer1 stride {stride:#x}')
    uv=transform_uv(uv,uvscale,uvtrans)
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
        primary_uv=decode_vb0_uv(v1d,s0,mesh['texcoord_scale'],mesh['texcoord_translation'])
        secondary_uv,norm,tan,color=decode_vb1(v2d,s1,mesh['texcoord_scale'],mesh['texcoord_translation'],primary_uv_exists=primary_uv is not None,other_stride=s0)
        if primary_uv is not None and secondary_uv is not None:
            raise ValueError(f'mesh {mi}: both vertex streams produced UV0')
        uv=primary_uv if primary_uv is not None else secondary_uv
        uv_source='primary' if primary_uv is not None else ('secondary' if secondary_uv is not None else None)
        if len(pos)!=len(v2d)//s1: raise ValueError(f'mesh {mi}: vertex stream count mismatch')
        if uv is not None and len(uv)!=len(pos): raise ValueError(f'mesh {mi}: UV/position count mismatch')
        inds=decode_indices(idata,is32)
        ranges={}
        for pi,p in enumerate(mesh['parts']):
            key=(p['index_offset'],p['index_count'],p['primitive_type'])
            ranges.setdefault(key,[]).append((pi,p))
        if not unique_ranges:
            ranges={(p['index_offset'],p['index_count'],p['primitive_type'],pi):[(pi,p)] for pi,p in enumerate(mesh['parts'])}
        mrep={'mesh_index':mi,'model_scale':mesh['model_scale'],'model_translation':mesh['model_translation'],'texcoord_scale':mesh['texcoord_scale'],'texcoord_translation':mesh['texcoord_translation'],'uv_source':uv_source,'uv_bounds':bounds2(uv),'vertices1':mesh['vertices1'],'vertices2':mesh['vertices2'],'indices':mesh['indices'],'vertex_count':len(pos),'vertex_stride0':s0,'vertex_stride1':s1,'index_width_bits':32 if is32 else 16,'stage_part_offsets':mesh.get('stage_part_offsets'),'stage_code':mesh.get('stage_code'),'primitive_groups':[]}
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
            tm.metadata={'model_tag_hash':th,'mesh_index':mi,'source_vertex_indices':used.tolist(),'candidate_materials':materials,'part_indices':[pi for pi,_ in candidates],'lod_values':sorted(set(p['lod'] for _,p in candidates)),'index_offset':off,'index_count':count,'primitive_type':prim,'uv_source':uv_source}
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
