#!/usr/bin/env python3
"""Export D1 ROI s_entity_model geometry through a cross-package Tiger Corpus.

The historical entity-model exporter was intentionally package-local.  That is
insufficient for maps: Tower's binary-confirmed embedded model layer routinely
stores model headers in a destination package while vertex/index resources live
in shared architecture/global packages.

This exporter keeps the existing byte-decoder conventions but resolves every
TagHash through the v5 class-stable, serialized-coverage-sized Corpus.  Its
default selection matches the source-crosschecked D1 map-decal call:

    Model.Load(ExportDetailLevel.MostDetailed, null, true)

which means:
  * LOD category in {0,1,2,3,10} (ELod.IsHighestLevel), and
  * an inline D1 material with both VS and PS, and material.Unk20 != 0.

Parts that use an external variant shader are not guessed because the map-decal
caller supplies no parent EntityResource.  Null secondary vertex buffers are
accepted and produce position-only geometry rather than failing the model.

The canonical report preserves source hashes, selected/rejected parts, strides,
material flags and every decode error.  glTF is only an adapter.
"""
from __future__ import annotations

import argparse, json, math, struct, sys, traceback
from collections import Counter
from pathlib import Path

import numpy as np
import trimesh

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import d1_tower_map_schema_validate_v5 as v5
from d1_entity_model_probe import parse_model
from d1_entity_model_export import primitive_faces, snorm16, hdr_stride, index_is32

ENTITY_MODEL_CLASS='80801AB5'
MATERIAL_CLASS='80801AD7'
HIGHEST_LODS={0,1,2,3,10}
NULLS={'00000000','FFFFFFFF'}


def norm(h): return str(h).upper().removeprefix('0X').zfill(8)
def u16(b,o): return struct.unpack_from('<H',b,o)[0]
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def bounds(a):
    if a is None or len(a)==0: return None
    return {'min':[float(x) for x in np.min(a,axis=0)],'max':[float(x) for x in np.max(a,axis=0)]}


def linked(c,h):
    h=norm(h)
    if h in NULLS: return {'hash':h,'null':True},None,None,None
    meta=c.entry_meta(h); head,src=c.payload(h)
    if meta is None or head is None:
        raise KeyError(f'header {h} unavailable')
    ref=norm(meta.get('reference','FFFFFFFF'))
    if ref in NULLS: raise KeyError(f'header {h} has null backing {ref}')
    pmeta=c.entry_meta(ref); data,psrc=c.payload(ref)
    if pmeta is None or data is None:
        raise KeyError(f'backing {h}->{ref} unavailable')
    return {'hash':h,'meta':meta,'source':src,'backing':ref,'backing_meta':pmeta,'backing_source':psrc},head,pmeta,data


def primary_attrs(data,stride):
    n=len(data)//stride
    if n*stride!=len(data): raise ValueError(f'primary payload {len(data)} not divisible by stride {stride}')
    pos=uv=normal=tangent=color=None
    if stride in (0x08,0x0C,0x10,0x1C,0x20):
        raw=np.frombuffer(data,dtype='<i2').reshape(n,stride//2)
        pos=snorm16(raw[:,0:3])
        if stride==0x0C:
            # D1 dynamic stride 0x0C can be position+UV or position+2-bone
            # weights.  Defer the trailing 4 bytes unless another stream makes
            # the UV interpretation unambiguous.
            pass
        elif stride in (0x1C,0x20):
            uv=snorm16(raw[:,4:6])
            normal=snorm16(raw[:,6:9])
            tangent=snorm16(raw[:,10:13])
            if stride==0x20:
                color=np.frombuffer(data,dtype=np.uint8).reshape(n,stride)[:,28:32].astype(np.float32)/255.0
    elif stride==0x30:
        raw=np.frombuffer(data,dtype='<f4').reshape(n,12)
        pos=raw[:,0:3].astype(np.float32); normal=raw[:,4:7].astype(np.float32); tangent=raw[:,8:11].astype(np.float32)
    else:
        raise ValueError(f'unsupported D1 primary stride 0x{stride:X}')
    return pos,uv,normal,tangent,color


def secondary_attrs(data,stride,primary_uv_exists,other_stride):
    n=len(data)//stride
    if n*stride!=len(data): raise ValueError(f'secondary payload {len(data)} not divisible by stride {stride}')
    raw16=np.frombuffer(data,dtype='<i2').reshape(n,stride//2)
    raw8=np.frombuffer(data,dtype=np.uint8).reshape(n,stride)
    uv=normal=tangent=color=None
    if stride==0x04:
        uv=snorm16(raw16[:,0:2])
    elif stride==0x08:
        normal=snorm16(raw16[:,0:3])
    elif stride==0x0C:
        uv=snorm16(raw16[:,0:2]); normal=snorm16(raw16[:,2:5])
    elif stride==0x10:
        normal=snorm16(raw16[:,0:3]); tangent=snorm16(raw16[:,4:7])
    elif stride==0x14:
        if primary_uv_exists:
            normal=snorm16(raw16[:,0:3]); tangent=snorm16(raw16[:,4:7]); color=raw8[:,16:20].astype(np.float32)/255.0
        else:
            uv=snorm16(raw16[:,0:2]); normal=snorm16(raw16[:,2:5]); tangent=snorm16(raw16[:,6:9])
    elif stride==0x18:
        if other_stride==0x0C and primary_uv_exists:
            normal=snorm16(raw16[:,0:3]); tangent=snorm16(raw16[:,4:7])
            # Charm's D1 branch reads this tail as 4 int16s in this case; retain
            # it only as raw evidence rather than pretending it is RGBA8.
        else:
            uv=snorm16(raw16[:,0:2]); normal=snorm16(raw16[:,2:5]); tangent=snorm16(raw16[:,6:9]); color=raw8[:,20:24].astype(np.float32)/255.0
    elif stride==0x1C:
        uv=snorm16(raw16[:,0:2]); normal=snorm16(raw16[:,2:5]); tangent=snorm16(raw16[:,6:9]); color=raw8[:,20:24].astype(np.float32)/255.0
    else:
        raise ValueError(f'unsupported D1 secondary stride 0x{stride:X}')
    return uv,normal,tangent,color


def material_info(c,h):
    h=norm(h)
    out={'hash':h,'exists':False,'class_matches':False,'transparent_flag':None,'has_vs':False,'has_ps':False}
    if h in NULLS: return out
    m=c.entry_meta(h); b,src=c.payload(h)
    out['meta']=m;out['source']=src;out['exists']=m is not None and b is not None
    if not out['exists']: return out
    out['class_matches']=norm(m.get('reference',''))==MATERIAL_CLASS
    if len(b)>=0x2AC:
        out['unk08']=u32(b,0x08);out['unk20']=u16(b,0x20)
        out['transparent_flag']=out['unk20']!=0
        out['vertex_shader']=norm(u32(b,0x28));out['pixel_shader']=norm(u32(b,0x2A8))
        out['has_vs']=out['vertex_shader'] not in NULLS;out['has_ps']=out['pixel_shader'] not in NULLS
    return out


def part_selection(c,p,mode):
    lod=int(p['lod']);variant=int(p['variant_shader_index']);mh=norm(p['material'])
    info=material_info(c,mh) if variant==-1 else {'hash':mh,'external_variant':True,'variant_shader_index':variant}
    reasons=[]
    if mode in ('most-detailed','map-decal') and lod not in HIGHEST_LODS: reasons.append('not_highest_lod')
    if variant!=-1: reasons.append('external_variant_without_parent_resource')
    if variant==-1:
        if not info.get('exists'): reasons.append('material_unavailable')
        elif not info.get('class_matches'): reasons.append('material_class_mismatch')
        else:
            if not info.get('has_vs'): reasons.append('material_missing_vs')
            if not info.get('has_ps'): reasons.append('material_missing_ps')
            if mode=='map-decal' and not info.get('transparent_flag'): reasons.append('material_unk20_zero_not_transparent')
    return not reasons,reasons,info


def export_one(c,h,out_dir,mode='map-decal'):
    h=norm(h); meta=c.entry_meta(h); b,src=c.payload(h)
    rep={'model':h,'mode':mode,'meta':meta,'source':src,'errors':[],'meshes':[]}
    if meta is None or norm(meta.get('reference',''))!=ENTITY_MODEL_CLASS or b is None:
        raise ValueError(f'{h} not an available {ENTITY_MODEL_CLASS} model in Corpus')
    model=parse_model(b,'PS4'); rep['model_header']={k:model[k] for k in ('declared_file_size','actual_file_size','mesh_count','meshes_offset','unk20','unk30','unk_flags38')}
    scene=trimesh.Scene(); selected_parts=0; rejected_parts=0
    for mi,mesh in enumerate(model['meshes']):
        lr0,h0,_,d0=linked(c,mesh['vertices1']); s0=hdr_stride(h0); pos,uv0,n0,t0,col0=primary_attrs(d0,s0)
        lr1=h1=d1=None; s1=None; uv1=n1=t1=col1=None
        if norm(mesh['vertices2']) not in NULLS:
            lr1,h1,_,d1=linked(c,mesh['vertices2']); s1=hdr_stride(h1)
            uv1,n1,t1,col1=secondary_attrs(d1,s1,uv0 is not None,s0)
        lri,ih,_,idata=linked(c,mesh['indices']); is32=index_is32(ih); inds=np.frombuffer(idata,dtype='<u4' if is32 else '<u2').astype(np.int64)
        scale=np.asarray(mesh['model_scale'][:3],dtype=np.float32);trans=np.asarray(mesh['model_translation'][:3],dtype=np.float32)
        pos=(pos*scale+trans).astype(np.float32)
        uv=uv0 if uv0 is not None else uv1; normal=n0 if n0 is not None else n1; tangent=t0 if t0 is not None else t1; color=col0 if col0 is not None else col1
        if uv is not None:
            ts=np.asarray(mesh['texcoord_scale'],dtype=np.float32);tt=np.asarray(mesh['texcoord_translation'],dtype=np.float32)
            uv=np.column_stack((uv[:,0]*ts[0]+tt[0],uv[:,1]*(-ts[1])+1.0-tt[1])).astype(np.float32)
        if s1 is not None and len(pos)!=len(d1)//s1: raise ValueError(f'{h} mesh {mi}: stream vertex count mismatch')
        mrep={'mesh_index':mi,'vertices1':lr0,'vertices2':lr1,'indices':lri,'stride0':s0,'stride1':s1,'vertex_count':len(pos),'uv_bounds':bounds(uv),'parts':[]}
        selected=[]
        for pi,p in enumerate(mesh['parts']):
            keep,reasons,minfo=part_selection(c,p,mode)
            row={'part_index':pi,**p,'selected':keep,'rejection_reasons':reasons,'material_info':minfo}
            mrep['parts'].append(row)
            if keep: selected.append((pi,p,minfo));selected_parts+=1
            else: rejected_parts+=1
        # Preserve separate part records even when index ranges coincide because
        # D1 materials can differ on the same underlying triangle range.
        for pi,p,minfo in selected:
            off=int(p['index_offset']);count=int(p['index_count']);prim=int(p['primitive_type']);sl=inds[off:off+count]
            if len(sl)!=count: raise ValueError(f'{h} mesh {mi} part {pi}: short index range')
            facesg=primitive_faces(sl,prim,is32)
            if len(facesg)==0: continue
            if facesg.max()>=len(pos): raise ValueError(f'{h} mesh {mi} part {pi}: vertex index OOB')
            used,inv=np.unique(facesg.reshape(-1),return_inverse=True);faces=inv.reshape((-1,3));vv=pos[used]
            nn=normal[used] if normal is not None else None;uu=uv[used] if uv is not None else None
            mat=trimesh.visual.material.PBRMaterial(name=f'D1_{minfo["hash"]}')
            visual=trimesh.visual.TextureVisuals(uv=uu,material=mat) if uu is not None else trimesh.visual.ColorVisuals()
            tm=trimesh.Trimesh(vertices=vv,faces=faces,vertex_normals=nn,visual=visual,process=False,validate=False)
            name=f'{h}_mesh{mi}_part{pi}_lod{p["lod"]}'
            tm.metadata={'model':h,'mesh_index':mi,'part_index':pi,'material':minfo['hash'],'lod':p['lod'],'primitive_type':prim,'index_offset':off,'index_count':count}
            scene.add_geometry(tm,geom_name=name,node_name=name)
        rep['meshes'].append(mrep)
    rep['selected_part_count']=selected_parts;rep['rejected_part_count']=rejected_parts;rep['geometry_count']=len(scene.geometry);rep['bounds']=None if scene.bounds is None else scene.bounds.tolist()
    rep['triangle_count']=sum(len(g.faces) for g in scene.geometry.values())
    glb=out_dir/f'{h}.glb';js=out_dir/f'{h}.json';out_dir.mkdir(parents=True,exist_ok=True);scene.export(glb);rep['glb']=str(glb);js.write_text(json.dumps(rep,indent=2)+'\n')
    return rep


def main()->int:
    ap=argparse.ArgumentParser();ap.add_argument('--snapshot',type=Path,action='append',required=True);ap.add_argument('--runtime',type=Path,required=True);ap.add_argument('--model',action='append',required=True);ap.add_argument('--out-dir',type=Path,required=True);ap.add_argument('--mode',choices=('all','most-detailed','map-decal'),default='map-decal');ap.add_argument('--summary',type=Path)
    a=ap.parse_args();c=v5.v3.base.Corpus([p.resolve() for p in a.snapshot],a.runtime.resolve());rows=[]
    for i,h in enumerate(a.model,1):
        h=norm(h);print(f'MODEL {i}/{len(a.model)} {h}',flush=True)
        try:
            r=export_one(c,h,a.out_dir,a.mode);r['ok']=True
        except Exception as ex:
            r={'model':h,'ok':False,'error':repr(ex),'traceback':traceback.format_exc()};(a.out_dir/f'{h}.error.json').parent.mkdir(parents=True,exist_ok=True);(a.out_dir/f'{h}.error.json').write_text(json.dumps(r,indent=2)+'\n')
        rows.append(r)
    out={'schema_version':1,'status':'D1_ENTITY_MODEL_CORPUS_EXPORT' if all(r['ok'] for r in rows) else 'D1_ENTITY_MODEL_CORPUS_EXPORT_PARTIAL','mode':a.mode,'requested_models':len(rows),'exported_models':sum(r['ok'] for r in rows),'failed_models':sum(not r['ok'] for r in rows),'geometry_count':sum(r.get('geometry_count',0) for r in rows),'triangle_count':sum(r.get('triangle_count',0) for r in rows),'models':rows,'policy':'Cross-package v5 Corpus resolution; map-decal mode reproduces Charm D1 MostDetailed + transparentsOnly selection without guessing external parent materials.'}
    sp=a.summary or a.out_dir/'summary.json';sp.parent.mkdir(parents=True,exist_ok=True);sp.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k] for k in ('status','requested_models','exported_models','failed_models','geometry_count','triangle_count')},indent=2));return 0 if out['failed_models']==0 else 2

if __name__=='__main__': raise SystemExit(main())
