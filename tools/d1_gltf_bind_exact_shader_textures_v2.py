#!/usr/bin/env python3
"""Loss-preserving D1 world texture binder, including native cubemaps.

This supersedes the first direct-binder checkpoint by treating one D1 Texture
TagHash as one glTF texture resource even when the native resource is a cubemap.
2D resources embed their decoded PNG directly. A six-face cubemap is represented
as one deterministic horizontal 6-face PNG atlas, with storage face indices,
per-face SHA-256 values, dimensions and native header metadata retained in extras.
The atlas is lossless with respect to the six decoded face images and can be split
back into face0..face5 exactly at pixel level. No axis convention is invented.

All native shader t# relationships are retained in material extras. Portable glTF
base/normal slots are only a preview view; non-PBR resources remain embedded.
"""
from __future__ import annotations

import argparse, copy, hashlib, io, json, re
from collections import defaultdict
from pathlib import Path
import numpy as np
from PIL import Image
from d1_gltf_layer_merge import read_glb, write_glb

MAT_RE=re.compile(r'(?:TigerMaterial_|D1_)([0-9A-Fa-f]{8})')


def hbytes(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def hfile(p:Path)->str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''):h.update(b)
    return h.hexdigest()


def append_blob(doc,bin_data,payload,name):
    aligned=(len(bin_data)+3)&~3
    if aligned!=len(bin_data):bin_data+=b'\0'*(aligned-len(bin_data))
    off=len(bin_data); idx=len(doc.setdefault('bufferViews',[]))
    doc['bufferViews'].append({'buffer':0,'byteOffset':off,'byteLength':len(payload),'name':name})
    return idx,bin_data+payload


def verify_png(data:bytes):
    with Image.open(io.BytesIO(data)) as im: im.verify()


def encode_png(im:Image.Image)->bytes:
    b=io.BytesIO();im.save(b,format='PNG',optimize=False,compress_level=9);return b.getvalue()


def load_native_image(tag:str,rec:dict,root:Path):
    """Return one PNG representation and reversible metadata for one D1 TagHash."""
    rel=rec.get('png')
    if rel:
        p=root/rel
        if not p.exists():raise FileNotFoundError(str(p))
        data=p.read_bytes();verify_png(data)
        return data,{'representation':'decoded_2d_png','manifest_png':rel,'png_sha256':hbytes(data)}

    faces=rec.get('faces') or []
    if len(faces)==6 and all(f.get('png') for f in faces):
        ims=[];face_meta=[];size=None
        for expected,f in enumerate(sorted(faces,key=lambda x:int(x['face']))):
            fi=int(f['face'])
            if fi!=expected:raise ValueError(f'{tag}: cubemap storage face sequence is not 0..5')
            p=root/f['png']
            if not p.exists():raise FileNotFoundError(str(p))
            raw=p.read_bytes();verify_png(raw)
            with Image.open(io.BytesIO(raw)) as im:
                rgba=im.convert('RGBA'); rgba.load()
            if size is None:size=rgba.size
            if rgba.size!=size:raise ValueError(f'{tag}: cubemap faces differ in dimensions')
            ims.append(rgba)
            face_meta.append({'storage_face':fi,'manifest_png':f['png'],'png_sha256':hbytes(raw),'width':rgba.width,'height':rgba.height})
        w,h=size;atlas=Image.new('RGBA',(w*6,h))
        for i,im in enumerate(ims):atlas.paste(im,(i*w,0))
        data=encode_png(atlas)
        return data,{
            'representation':'decoded_cubemap_horizontal_face_atlas',
            'storage_face_count':6,
            'storage_face_order':[0,1,2,3,4,5],
            'atlas_layout':'face0|face1|face2|face3|face4|face5',
            'face_width':w,'face_height':h,'atlas_width':w*6,'atlas_height':h,
            'faces':face_meta,'atlas_png_sha256':hbytes(data),
            'axis_mapping':'UNASSIGNED_STORAGE_ORDER_ONLY',
        }
    raise FileNotFoundError(f'{tag}: no decodable 2D PNG or complete six-face cubemap PNG set')


def bc5_normal(data:bytes)->bytes:
    with Image.open(io.BytesIO(data)) as im:a=np.asarray(im.convert('RGB'),dtype=np.float32)/255.0
    x=a[...,0]*2-1;y=a[...,1]*2-1;z=np.sqrt(np.maximum(0,1-x*x-y*y))
    out=np.stack((x*.5+.5,y*.5+.5,z*.5+.5),axis=-1)
    return encode_png(Image.fromarray(np.clip(out*255+.5,0,255).astype(np.uint8),'RGB'))


def usage(inv):
    out=defaultdict(list)
    for mh,m in sorted((inv.get('materials') or {}).items()):
        ps=m.get('pixel_shader')
        for b in m.get('bindings',[]):
            tag=str(b.get('texture') or '').upper()
            if not tag:continue
            out[tag].append({'material':mh.upper(),'pixel_shader':ps,'texture_index':int(b.get('texture_index',-1)),
                             'resource_class':b.get('resource_class'),'proven_role':b.get('proven_role'),
                             'evidence_status':b.get('evidence_status'),'preview_role':b.get('preview_role')})
    return dict(out)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--input-glb',type=Path,required=True);ap.add_argument('--manifest',type=Path,required=True)
    ap.add_argument('--roles',type=Path,required=True);ap.add_argument('--texture-dir',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True);ap.add_argument('--report',type=Path,required=True)
    ap.add_argument('--include-medium-base',action='store_true');ap.add_argument('--bind-normal-candidates',action='store_true')
    ap.add_argument('--expect-exact-textures',type=int);ap.add_argument('--expect-derived-normals',type=int)
    a=ap.parse_args()
    man=json.loads(a.manifest.read_text()); inv=json.loads(a.roles.read_text())
    tex=man.get('textures') or {}; sem=inv.get('materials') or {}; uses=usage(inv); tags=sorted(uses)
    absent=sorted(set(tags)-set(tex))
    if absent:raise SystemExit('inventory tags absent from manifest: '+','.join(absent))
    if a.expect_exact_textures is not None and len(tags)!=a.expect_exact_textures:raise SystemExit(f'exact texture count {len(tags)} != {a.expect_exact_textures}')

    src,srcbin=read_glb(a.input_glb);doc=copy.deepcopy(src);bindata=srcbin
    base={k:len(src.get(k,[])) for k in ('bufferViews','images','textures','materials','meshes','nodes','accessors')}
    indices={};rows=[];repr_counts=defaultdict(int)
    for tag in tags:
        rec=tex[tag];png,rep=load_native_image(tag,rec,a.texture_dir);repr_counts[rep['representation']]+=1
        us=uses[tag];classes=sorted({str(x['resource_class']) for x in us if x.get('resource_class')});roles=sorted({str(x['proven_role']) for x in us if x.get('proven_role')})
        bvi,bindata=append_blob(doc,bindata,png,f'D1_TEXTURE_{tag}_PNG')
        ii=len(doc.setdefault('images',[]));extra={'d1_taghash':tag,'d1_native_texture_resource':True,'d1_format_name':rec.get('format_name'),
            'd1_header_info':rec.get('header_info'),'d1_resource_classes':classes,'d1_proven_roles':roles,'d1_shader_bindings':us,
            'd1_glb_representation':rep,'d1_embedded_png_sha256':hbytes(png)}
        doc['images'].append({'name':f'D1_TEXTURE_{tag}','mimeType':'image/png','bufferView':bvi,'extras':extra})
        ti=len(doc.setdefault('textures',[]));doc['textures'].append({'name':f'D1_TEXTURE_{tag}','source':ii,'extras':{
            'd1_taghash':tag,'d1_native_texture_resource':True,'d1_resource_classes':classes,'d1_proven_roles':roles,'d1_representation':rep['representation']}})
        indices[tag]=ti;rows.append({'tag':tag,'texture_index':ti,'image_index':ii,'buffer_view':bvi,'png_bytes':len(png),'png_sha256':hbytes(png),
                                     'representation':rep,'resource_classes':classes,'proven_roles':roles,'usage_count':len(us)})

    allowed={'PROVEN','STRONG_FORMAT_CANDIDATE'}
    if a.include_medium_base:allowed.add('MEDIUM_PREVIEW_CANDIDATE')
    nallowed={'PROVEN'}
    if a.bind_normal_candidates:nallowed.add('STRONG_FORMAT_CANDIDATE')
    needed=sorted({str(m.get('preview_normal')).upper() for m in sem.values() if m.get('preview_normal') and m.get('preview_normal_confidence') in nallowed and m.get('preview_base_color') and m.get('preview_base_confidence') in allowed})
    nidx={};nrows=[]
    for tag in needed:
        rec=tex[tag]
        # Portable normals must be 2D BC5 resources, never cubemap atlases.
        if not rec.get('png'):raise SystemExit(f'{tag}: selected portable normal is not a 2D PNG resource')
        p=a.texture_dir/rec['png'];raw=p.read_bytes();derived=bc5_normal(raw)
        bvi,bindata=append_blob(doc,bindata,derived,f'D1_DERIVED_NORMAL_{tag}_PNG');ii=len(doc.setdefault('images',[]))
        doc['images'].append({'name':f'D1_DERIVED_NORMAL_{tag}','mimeType':'image/png','bufferView':bvi,'extras':{
            'd1_source_taghash':tag,'d1_derived_portable_normal':True,'d1_derivation':'BC5/RG XY -> signed XY -> reconstruct +Z -> RGB','d1_png_sha256':hbytes(derived)}})
        ti=len(doc.setdefault('textures',[]));doc['textures'].append({'name':f'D1_DERIVED_NORMAL_{tag}','source':ii,'extras':{'d1_source_taghash':tag,'d1_derived_portable_normal':True}})
        nidx[tag]=ti;nrows.append({'source_tag':tag,'texture_index':ti,'image_index':ii,'buffer_view':bvi,'png_bytes':len(derived),'png_sha256':hbytes(derived)})
    if a.expect_derived_normals is not None and len(nrows)!=a.expect_derived_normals:raise SystemExit(f'derived normal count {len(nrows)} != {a.expect_derived_normals}')

    seen=set();mrows=[];base_bound=normal_bound=0
    for mi,m in enumerate(doc.get('materials',[])):
        mm=MAT_RE.search(str(m.get('name') or ''))
        if not mm:continue
        mh=mm.group(1).upper();seen.add(mh);s=sem.get(mh)
        if not s:continue
        conf=s.get('preview_base_confidence','NONE');bt=str(s.get('preview_base_color') or '').upper() if conf in allowed else ''
        nc=s.get('preview_normal_confidence','NONE');nt=str(s.get('preview_normal') or '').upper() if nc in nallowed and bt else ''
        native=[]
        for b in s.get('bindings',[]):
            t=str(b.get('texture') or '').upper();native.append({'t':int(b.get('texture_index',-1)),'taghash':t,'exact_texture_index':indices.get(t),
                 'resource_class':b.get('resource_class'),'proven_role':b.get('proven_role'),'evidence_status':b.get('evidence_status'),'preview_role':b.get('preview_role')})
        ex=m.setdefault('extras',{});ex.update({'d1_material_taghash':mh,'d1_pixel_shader':s.get('pixel_shader'),'d1_native_texture_bindings':native,
                                               'd1_preview_base_confidence':conf,'d1_preview_normal_confidence':nc})
        if bt:
            pbr=m.setdefault('pbrMetallicRoughness',{});pbr['baseColorTexture']={'index':indices[bt]};pbr['metallicFactor']=0.;pbr['roughnessFactor']=1.;m['alphaMode']='OPAQUE';base_bound+=1
            if nt:m['normalTexture']={'index':nidx[nt]};normal_bound+=1
        mrows.append({'material_index':mi,'material':mh,'pixel_shader':s.get('pixel_shader'),'base_texture':bt or None,'base_confidence':conf,'normal_texture':nt or None,'normal_confidence':nc,'native_binding_count':len(native)})
    missing=sorted(set(sem)-seen)
    if missing:raise SystemExit('inventory materials absent from input GLB: '+','.join(missing))

    doc.setdefault('asset',{'version':'2.0'}).setdefault('extras',{})['d1_exact_shader_texture_corpus']={
        'native_texture_tag_count':len(rows),'derived_portable_normal_count':len(nrows),'representation_counts':dict(repr_counts),
        'policy':'One glTF texture per D1 Texture TagHash. 2D tags use decoded PNG; cubemap tags use reversible face0..face5 horizontal atlases. Native t# metadata remains authoritative.'}
    a.out.parent.mkdir(parents=True,exist_ok=True);write_glb(a.out,doc,bindata);chk,chkbin=read_glb(a.out)
    if chkbin[:len(srcbin)]!=srcbin:raise SystemExit('input BIN is not exact output prefix')
    for k in ('accessors','meshes','nodes'):
        if chk.get(k,[])!=src.get(k,[]):raise SystemExit(f'input {k} changed')
    final={k:len(chk.get(k,[])) for k in ('bufferViews','images','textures','materials','meshes','nodes','accessors')}
    expect=base['images']+len(rows)+len(nrows)
    if final['images']!=expect or final['textures']!=base['textures']+len(rows)+len(nrows):raise SystemExit(f'resource count mismatch {final}')
    rep={'schema_version':2,'status':'D1_GLTF_EXACT_SHADER_TEXTURE_RESOURCES_BOUND','input_glb':str(a.input_glb),'input_sha256':hfile(a.input_glb),
         'output_glb':str(a.out),'output_sha256':hfile(a.out),'output_bytes':a.out.stat().st_size,'base_counts':base,'final_counts':final,
         'exact_source_texture_count':len(rows),'derived_portable_normal_count':len(nrows),'representation_counts':dict(repr_counts),
         'portable_base_bound_material_count':base_bound,'portable_normal_bound_material_count':normal_bound,'source_textures':rows,'derived_normals':nrows,'materials':mrows,
         'policy':'All 50 D1 material texture TagHashes survive as one named glTF resource each, including four reversible cubemap atlases. Portable bindings never replace native shader/t# metadata.'}
    a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(rep,indent=2)+'\n')
    print(json.dumps({k:rep[k] for k in ('status','exact_source_texture_count','derived_portable_normal_count','representation_counts','portable_base_bound_material_count','portable_normal_bound_material_count','final_counts','output_bytes','output_sha256')},indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
