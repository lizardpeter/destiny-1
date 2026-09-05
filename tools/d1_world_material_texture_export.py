#!/usr/bin/env python3
"""Export exact D1 ROI material texture dependencies for world/static scenes.

This is intentionally a generic world/map stage rather than a Tower-specific
texture guesser. It consumes the material hashes already selected by a visual
scene and preserves the exact material -> shader stage -> t# -> Texture TagHash
relationship. Texture headers/backing can resolve across package namespaces via
the same current-generation Corpus used by the map validator.

What this tool proves/exports:
- exact visible material hashes;
- exact vertex/pixel shader hashes;
- exact VS/PS TextureIndex (shader t#) bindings;
- PS4 ROI Texture2D headers and backing chains;
- deswizzled DDS and PNG for BC1/BC2/BC3/BC4/BC5/RGBA8 when present.

What it does NOT do yet:
- guess that arbitrary t0 is always albedo;
- flatten every shader family into generic PBR semantics;
- bake per-instance D1 UV transforms into glTF meshes.

Those are deliberately separate adapter stages so the eventual all-world exporter
can remain lossless and shader-correct.
"""
from __future__ import annotations
import argparse, hashlib, json, struct, sys
from collections import Counter, defaultdict
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import d1_tower_map_schema_validate_v5 as v5
from d1_material_decode import parse_material
from d1_texture_export import (
    decode_header, expected_base_size, unswizzle_ps4, make_dds, FORMAT_NAME
)
from d1_dds_to_png import decode_dds

MAT_CLASS='80801AD7'

# Only roles independently proven by exact native GCN dataflow are named here.
# The Tower families below were promoted after complete top-40 disassembly and
# Sony InputUsageSlot -> native descriptor provenance recovery.  See
# notes/TOWER_TOP_SHADER_DATAFLOW.md.  Everything else remains exact t# without
# a semantic guess.
KNOWN_PIXEL_SHADER_ROLES={
    '80AAE14B': {
        0:'surface_rgb', 1:'primary_normal_rg', 2:'detail_normal_rg',
        3:'environment_cubemap', 4:'surface_alpha_reflection_control'
    },
    '816CE0A8': {0:'height_pre_displacement',1:'displaced_image'},

    # Common Tower deferred surface family: t0 RGB reaches MRT0; t0 alpha sets
    # deferred-normal packing magnitude; t1.xy is decoded as a tangent-space
    # two-component normal with reconstructed +Z.
    '809DF9A4': {0:'surface_rgb_alpha_deferred_normal_control',1:'primary_normal_rg'},
    '80AADCB3': {0:'surface_rgb_alpha_deferred_normal_control',1:'primary_normal_rg'},

    # Common Tower colored-surface family: t0 RGB reaches MRT0.  t1 is sampled
    # only with dmask:Y and changes only the deferred normal-vector packing
    # magnitude (0.375 + 0.125*t1.y); it is not a second color map.
    '8093EB1E': {0:'surface_rgb',1:'deferred_normal_magnitude_control_y'},
    '80AAE1C6': {0:'surface_rgb',1:'deferred_normal_magnitude_control_y'},

    # Simple Tower surface pass: t0 RGB goes directly to MRT0; MRT1 is built
    # solely from the interpolated geometric normal.
    '80AADC40': {0:'surface_rgb'},
}

# D1 Rise of Iron PS4 ROI stores a GCN surface format in the texture header.
# Public Tiger/Charm GcnSurfaceFormatExtensions maps BC1/2/3/7 to DXGI *_SRGB,
# while BC4/BC5 and Format8_8_8_8 map to linear UNORM.  Keep this as a storage
# interpretation hint, separate from shader semantic role: a BC3 can still be a
# packed control texture even though the resource's native format is sRGB.
ROI_COLORSPACE_HINT={
    'BC1':'sRGB','BC2':'sRGB','BC3':'sRGB','BC7':'sRGB',
    'BC4':'linear','BC5':'linear','RGBA8':'linear',
}
ROI_COLORSPACE_EVIDENCE='SOURCE_CORRELATED_GCN_SURFACE_TO_DXGI'


def norm(h:str)->str:
    return h.upper().removeprefix('0X').zfill(8)


def pkg_id_from_tag(h:str)->str|None:
    try:
        x=int(norm(h),16)
    except Exception:
        return None
    if x<0x80800000: return None
    return f'{((x-0x80800000)>>13)&0xFFFF:04x}'


def resolve_chain(c, h:str, max_depth:int=4):
    cur=norm(h); out=[]; seen=set()
    for _ in range(max_depth):
        if cur in seen: break
        seen.add(cur)
        meta=c.entry_meta(cur)
        payload,src=c.payload(cur)
        out.append({'hash':cur,'meta':meta,'source':src,'payload':payload})
        if not meta: break
        nxt=norm(meta.get('reference','FFFFFFFF'))
        if nxt=='FFFFFFFF' or c.entry_meta(nxt) is None: break
        cur=nxt
    return out


def export_texture(c, th:str, outdir:Path):
    th=norm(th)
    outdir.mkdir(parents=True,exist_ok=True)
    chain=resolve_chain(c,th)
    row={'texture':th,'package_id':pkg_id_from_tag(th),
         'chain':[{'hash':x['hash'],'meta':x['meta'],'source':x['source'],
                   'payload_bytes':None if x['payload'] is None else len(x['payload'])} for x in chain]}
    if not chain or chain[0]['payload'] is None:
        row['error']='texture header unavailable'; return row
    hb=chain[0]['payload']
    try:
        hdr=decode_header(hb)
    except Exception as ex:
        row['error']=f'header decode failed: {ex!r}'; return row
    row['header_info']=hdr

    expected=expected_base_size(hdr['width'],hdr['height'],hdr['surface_format'],hdr['array_size'])
    # The last reachable payload in the normal D1 chain is the full-resolution
    # backing. Prefer the deepest payload large enough for the top-level surface.
    backing=None
    for x in reversed(chain[1:]):
        if x['payload'] is not None and (expected is None or len(x['payload'])>=expected):
            backing=x; break
    if backing is None:
        row['error']='full-resolution backing unavailable'
        return row
    raw=backing['payload']
    if expected is not None: raw=raw[:expected]
    swizzled=((hdr['flags1']&0xC00)!=0x400) or hdr['array_size']==6
    try:
        linear=unswizzle_ps4(raw,hdr['width'],hdr['height'],hdr['array_size'],hdr['surface_format']) if swizzled else raw
    except Exception as ex:
        row['error']=f'unswizzle failed: {ex!r}'; return row

    fmt=FORMAT_NAME.get(hdr['surface_format'],f'GCN{hdr["surface_format"]:02X}')
    stem=f'{th}_{hdr["width"]}x{hdr["height"]}_{fmt}'
    row.update({
        'format_name':fmt,
        'native_colorspace_hint':ROI_COLORSPACE_HINT.get(fmt,'unknown'),
        'native_colorspace_evidence':ROI_COLORSPACE_EVIDENCE,
        'backing_hash':backing['hash'],'backing_bytes':len(raw),'unswizzled':swizzled,
    })
    files=[]
    try:
        if hdr['array_size']==1:
            dds=make_dds(linear,hdr['width'],hdr['height'],hdr['surface_format'])
            dp=outdir/(stem+'.dds'); dp.write_bytes(dds); files.append(dp.name)
            try:
                im=decode_dds(dp); pp=outdir/(stem+'.png'); im.save(pp); files.append(pp.name)
                row['png']=pp.name
            except Exception as ex:
                row['png_error']=repr(ex)
            row['dds']=dp.name
        elif hdr['array_size']==6:
            per=expected_base_size(hdr['width'],hdr['height'],hdr['surface_format'],1)
            if per is None or len(linear)<per*6: raise ValueError('cubemap face sizing failed')
            faces=[]
            for i in range(6):
                fb=linear[i*per:(i+1)*per]
                dds=make_dds(fb,hdr['width'],hdr['height'],hdr['surface_format'])
                dp=outdir/f'{stem}_face{i}.dds';dp.write_bytes(dds);files.append(dp.name)
                fr={'face':i,'dds':dp.name}
                try:
                    im=decode_dds(dp);pp=outdir/f'{stem}_face{i}.png';im.save(pp);files.append(pp.name);fr['png']=pp.name
                except Exception as ex: fr['png_error']=repr(ex)
                faces.append(fr)
            row['faces']=faces
        else:
            row['error']=f'unsupported array_size={hdr["array_size"]}'
    except Exception as ex:
        row['error']=f'file export failed: {ex!r}'
    row['files']=files
    return row


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--snapshot',type=Path,action='append',required=True)
    ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('--visual-json',type=Path,action='append',required=True,
                    help='visual sidecar(s) containing materials[hash].visual')
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=True)

    c=v5.v3.base.Corpus([p.resolve() for p in a.snapshot],a.runtime.resolve())
    visible=set()
    for p in a.visual_json:
        d=json.loads(p.read_text())
        for h,r in d.get('materials',{}).items():
            if r.get('visual'): visible.add(norm(h))

    materials={};texture_refs=defaultdict(list);shader_freq=Counter();errors=[]
    for mh in sorted(visible):
        meta=c.entry_meta(mh);b,src=c.payload(mh)
        rec={'material':mh,'meta':meta,'source':src}
        if not meta or norm(meta.get('reference',''))!=MAT_CLASS or b is None:
            rec['error']='material unavailable/non-80801AD7';errors.append(rec);materials[mh]=rec;continue
        try:
            parsed=parse_material(b,'PS4')
            vs_items=list(parsed['vs_textures']['items'])
            ps_items=list(parsed['ps_textures']['items'])
            # Preserve a stable flattened manifest view for existing world tools,
            # while retaining the current material parser's structured records.
            rec.update({
                'file_size':parsed['declared_file_size'],
                'declared_file_size':parsed['declared_file_size'],
                'actual_file_size':parsed['actual_file_size'],
                'unk08':parsed['unk08'],
                'unk0c':parsed['unk0c'],
                'unk10':parsed['unk10'],
                'vertex_shader':norm(parsed['vertex_shader']),
                'pixel_shader':norm(parsed['pixel_shader']),
                'vs_texture_count':parsed['vs_textures']['count'],
                'ps_texture_count':parsed['ps_textures']['count'],
                'textures':[{'stage':'vs',**x} for x in vs_items]+[{'stage':'ps',**x} for x in ps_items],
                'vs_texture_tags':vs_items,
                'ps_texture_tags':ps_items,
                'constants':{
                    'vs_vector4_container':norm(parsed['vs_vector4_container']),
                    'ps_vector4_container':norm(parsed['ps_vector4_container']),
                },
                'samplers':{'vs':parsed['vs_samplers'],'ps':parsed['ps_samplers']},
                'tfx':{'vs':parsed['vs_tfx_bytecode'],'ps':parsed['ps_tfx_bytecode']},
                'parsed_material_schema':'d1_material_decode.parse_material/PS4',
            })
            bindings=[]
            ps=norm(parsed['pixel_shader']);shader_freq[ps]+=1
            for stage,items in [('vs',vs_items),('ps',ps_items)]:
                for tr in items:
                    th=norm(tr['texture']);idx=int(tr['texture_index'])
                    role=KNOWN_PIXEL_SHADER_ROLES.get(ps,{}).get(idx) if stage=='ps' else None
                    br={'stage':stage,'texture_index':idx,'texture':th}
                    if role:
                        br['semantic_role']=role;br['semantic_status']='PROVEN'
                    bindings.append(br)
                    texture_refs[th].append({'material':mh,'stage':stage,'texture_index':idx,'pixel_shader':ps,'role':role})
            rec['bindings']=bindings
        except Exception as ex:
            rec['error']=repr(ex);errors.append(rec)
        materials[mh]=rec

    textures={}
    unique=sorted(texture_refs)
    for i,th in enumerate(unique,1):
        print(f'TEXTURE {i}/{len(unique)} {th}',flush=True)
        textures[th]=export_texture(c,th,a.out/'textures')
    missing=[h for h,r in textures.items() if r.get('error')]
    missing_pkg=Counter(pkg_id_from_tag(h) for h in missing)
    report={
        'schema_version':1,'status':'D1_WORLD_VISIBLE_MATERIAL_TEXTURE_EXPORT',
        'visible_material_count':len(visible),'material_decode_errors':len(errors),
        'unique_texture_tags':len(unique),'decoded_texture_tags':len(unique)-len(missing),
        'texture_errors':len(missing),
        'png_outputs':sum(1 for r in textures.values() if r.get('png'))+sum(len([f for f in r.get('faces',[]) if f.get('png')]) for r in textures.values()),
        'missing_texture_package_ids':dict(sorted((k,v) for k,v in missing_pkg.items() if k is not None)),
        'pixel_shader_frequency':dict(shader_freq.most_common()),
        'materials':materials,'texture_references':dict(texture_refs),'textures':textures,
        'policy':'Exact material/shader/register/texture relationships are preserved. Texture semantic roles are only named for independently instruction-proven shader families; all others remain t#.',
    }
    (a.out/'material_texture_manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ('visible_material_count','material_decode_errors','unique_texture_tags','decoded_texture_tags','texture_errors','png_outputs','missing_texture_package_ids')},indent=2))
    return 0

if __name__=='__main__': raise SystemExit(main())
