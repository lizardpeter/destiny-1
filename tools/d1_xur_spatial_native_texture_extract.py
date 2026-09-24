#!/usr/bin/env python3
"""Extract exact embedded native PNGs used by spatially selected Xur primitives.

Selection is based only on POSITION accessor bounds.  The output records material,
pixel-shader, slot ownership plus basic decoded PNG channel statistics.  No visual
or anatomical semantic is inferred from the spatial query.
"""
from __future__ import annotations
import argparse,hashlib,json,struct
from collections import defaultdict
from pathlib import Path
from PIL import Image
import io

JSON_CHUNK=0x4E4F534A
BIN_CHUNK=0x004E4942

def read_glb(path:Path):
    raw=path.read_bytes()
    if raw[:4]!=b'glTF' or struct.unpack_from('<I',raw,4)[0]!=2:
        raise ValueError('not glTF2 GLB')
    jl,jt=struct.unpack_from('<II',raw,12)
    if jt!=JSON_CHUNK: raise ValueError('first chunk is not JSON')
    doc=json.loads(raw[20:20+jl].decode('utf-8').rstrip(' \t\r\n\0'))
    bo=20+jl
    bl,bt=struct.unpack_from('<II',raw,bo)
    if bt!=BIN_CHUNK: raise ValueError('second chunk is not BIN')
    return raw,doc,raw[bo+8:bo+8+bl]

def image_stats(payload:bytes):
    im=Image.open(io.BytesIO(payload)).convert('RGBA')
    px=list(im.getdata()); n=len(px)
    sums=[sum(p[i] for p in px) for i in range(4)]
    mins=[min(p[i] for p in px) for i in range(4)]
    maxs=[max(p[i] for p in px) for i in range(4)]
    alpha0=sum(1 for p in px if p[3]==0)
    alpha_lt128=sum(1 for p in px if p[3]<128)
    white=sum(1 for p in px if p[0]>=240 and p[1]>=240 and p[2]>=240)
    black=sum(1 for p in px if p[0]<=15 and p[1]<=15 and p[2]<=15)
    return {'width':im.width,'height':im.height,'mode':'RGBA',
            'channel_min':mins,'channel_max':maxs,
            'channel_mean':[x/n for x in sums],
            'alpha_zero_fraction':alpha0/n,'alpha_lt_128_fraction':alpha_lt128/n,
            'near_white_rgb_fraction':white/n,'near_black_rgb_fraction':black/n}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('glb',type=Path)
    ap.add_argument('--min-z',type=float,default=1.8)
    ap.add_argument('--out-dir',type=Path,required=True)
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args()
    raw,d,blob=read_glb(a.glb); viol=[]
    mats=d.get('materials') or []; accs=d.get('accessors') or []
    selected=set(); prim_rows=[]
    for mi,mesh in enumerate(d.get('meshes') or []):
        for pi,p in enumerate(mesh.get('primitives') or []):
            pos=(p.get('attributes') or {}).get('POSITION')
            if pos is None: continue
            ac=accs[int(pos)]; mx=ac.get('max')
            if not (isinstance(mx,list) and len(mx)>=3): continue
            if float(mx[2]) < a.min_z: continue
            mati=int(p.get('material',-1))
            if not (0<=mati<len(mats)): continue
            selected.add(mati)
            ex=mats[mati].get('extras') or {}
            prim_rows.append({'mesh_index':mi,'mesh_name':mesh.get('name'),'primitive_index':pi,
                              'position_max_z':float(mx[2]),'material_index':mati,
                              'material':str(ex.get('d1_material_taghash') or '').upper(),
                              'pixel_shader':str(ex.get('d1_pixel_shader') or '').upper()})
    owners=defaultdict(list)
    selected_materials=[]
    for mi in sorted(selected):
        m=mats[mi]; ex=m.get('extras') or {}
        mh=str(ex.get('d1_material_taghash') or '').upper()
        ps=str(ex.get('d1_pixel_shader') or '').upper()
        bs=list(ex.get('d1_native_texture_bindings') or [])
        selected_materials.append({'material_index':mi,'material':mh,'pixel_shader':ps,'bindings':bs})
        for b in bs:
            tag=str(b.get('taghash') or '').upper()
            if tag: owners[tag].append({'material':mh,'pixel_shader':ps,'stage':b.get('stage'),'slot':b.get('t')})
    image_by_tag={}
    for ii,img in enumerate(d.get('images') or []):
        name=str(img.get('name') or '')
        ex=img.get('extras') or {}
        tag=str(ex.get('d1_texture_taghash') or '').upper()
        if not tag and name.upper().startswith('D1_TEXTURE_'):
            tag=name.upper().split('D1_TEXTURE_',1)[1].split('.',1)[0]
        if tag: image_by_tag.setdefault(tag,[]).append((ii,img))
    a.out_dir.mkdir(parents=True,exist_ok=True)
    tex_rows=[]
    for tag in sorted(owners):
        hits=image_by_tag.get(tag,[])
        if len(hits)!=1:
            viol.append(f'{tag}:image_cardinality:{len(hits)}')
            continue
        ii,img=hits[0]
        if img.get('mimeType')!='image/png' or 'bufferView' not in img:
            viol.append(f'{tag}:not_embedded_png');continue
        bv=d['bufferViews'][int(img['bufferView'])]
        off=int(bv.get('byteOffset',0)); n=int(bv['byteLength']); payload=blob[off:off+n]
        if len(payload)!=n or not payload.startswith(bytes.fromhex('89504e470d0a1a0a')):
            viol.append(f'{tag}:bad_png_payload');continue
        sha=hashlib.sha256(payload).hexdigest()
        fn=f'{tag}.png'; (a.out_dir/fn).write_bytes(payload)
        try: st=image_stats(payload)
        except Exception as ex:
            viol.append(f'{tag}:decode:{ex!r}');continue
        tex_rows.append({'tag':tag,'image_index':ii,'image_name':img.get('name'),'png_sha256':sha,
                         'bytes':n,'owners':owners[tag],**st})
    out={'schema_version':1,
         'status':'D1_XUR_SPATIAL_NATIVE_TEXTURE_EXTRACT_EXACT' if not viol else 'D1_XUR_SPATIAL_NATIVE_TEXTURE_EXTRACT_VIOLATIONS',
         'glb_sha256':hashlib.sha256(raw).hexdigest(),'min_z':a.min_z,
         'selected_primitive_count':len(prim_rows),'selected_material_count':len(selected),
         'selected_texture_count':len(owners),'extracted_texture_count':len(tex_rows),
         'selected_primitives':prim_rows,'selected_materials':selected_materials,'textures':tex_rows,
         'violations':viol,
         'policy':'Exact embedded PNG bytes and decoded pixel statistics for a numeric POSITION-max-Z selection only. No anatomy or shader semantic is inferred from appearance.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'status':out['status'],'selected_primitive_count':len(prim_rows),
      'selected_material_count':len(selected),'selected_texture_count':len(owners),
      'extracted_texture_count':len(tex_rows),
      'textures':[{'tag':r['tag'],'owners':r['owners'],'size':[r['width'],r['height']],
                   'alpha0':r['alpha_zero_fraction'],'alpha_lt128':r['alpha_lt_128_fraction'],
                   'white':r['near_white_rgb_fraction'],'black':r['near_black_rgb_fraction']} for r in tex_rows],
      'violations':viol},indent=2))
    return 0 if not viol else 2
if __name__=='__main__': raise SystemExit(main())
