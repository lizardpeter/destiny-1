#!/usr/bin/env python3
"""Prove exact Crota texture-channel facts used by native attenuation shaders.

The input is the frozen exact retail texture-export artifact. DDS bytes are
re-hashed against its manifest before inspection.

For BC1, alpha=0 is possible only in three-color mode (color0 <= color1) when a
texel selects palette index 3. Therefore an exact census of every DXT1 block can
prove that sampled alpha is identically 1 without relying on PNG conversion.

For BC4, this tool records exact encoded endpoint/index coverage and a decoded
8-bit scalar-domain census. It does not assign a material semantic to that scalar.
"""
from __future__ import annotations
import argparse, collections, hashlib, json, struct
from pathlib import Path

BC1_TAGS=('80AACF2A','8108E951','8108E952')
BC4_TAG='8108E7B6'

def sha256(p:Path)->str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''): h.update(b)
    return h.hexdigest()

def manifest_row(man,tag):
    rows=[x for x in man.get('rows',[]) if str(x.get('texture','')).upper()==tag]
    if len(rows)!=1: raise ValueError(f'{tag}: expected one manifest row, got {len(rows)}')
    return rows[0]

def dds_path(root:Path,row:dict)->Path:
    fs=[x for x in row.get('files',[]) if x.get('kind')=='dds']
    if len(fs)!=1: raise ValueError(f"{row.get('texture')}: expected one DDS file")
    p=root/fs[0]['path']
    if not p.exists(): raise FileNotFoundError(p)
    got=sha256(p)
    if got!=fs[0]['sha256']: raise ValueError(f"{row.get('texture')}: DDS sha drift {got}")
    return p

def dds_payload(p:Path,fourcc:bytes)->bytes:
    b=p.read_bytes()
    if len(b)<128 or b[:4]!=b'DDS ': raise ValueError(f'{p}: invalid DDS')
    if b[84:88]!=fourcc: raise ValueError(f'{p}: fourcc {b[84:88]!r} != {fourcc!r}')
    return b[128:]

def bc1_alpha_proof(data:bytes)->dict:
    if len(data)%8: raise ValueError('BC1 payload not 8-byte aligned')
    tm=0; opaque=0; transparent_index_texels=0; indexed_texels=0
    for off in range(0,len(data),8):
        c0,c1,idx=struct.unpack_from('<HHI',data,off)
        if c0<=c1:
            tm+=1
            for k in range(16):
                if ((idx>>(2*k))&3)==3: transparent_index_texels+=1
        else:
            opaque+=1
        indexed_texels+=16
    return {
        'block_count':len(data)//8,
        'three_color_mode_block_count':tm,
        'four_color_mode_block_count':opaque,
        'texel_count':indexed_texels,
        'transparent_palette_index_texel_count':transparent_index_texels,
        'alpha_u8_domain':[255] if transparent_index_texels==0 else [0,255],
        'sample_alpha_constant_one':transparent_index_texels==0,
        'proof_rule':'DXT1 alpha can be zero only when color0<=color1 and palette index 3 is selected.',
    }

def bc4_palette(a0:int,a1:int)->list[int]:
    # Integer-domain BC4 UNORM palette, rounded to nearest integer for census.
    if a0>a1:
        return [a0,a1]+[round(((7-i)*a0+i*a1)/7) for i in range(1,7)]
    return [a0,a1]+[round(((5-i)*a0+i*a1)/5) for i in range(1,5)]+[0,255]

def bc4_scalar_census(data:bytes)->dict:
    if len(data)%8: raise ValueError('BC4 payload not 8-byte aligned')
    hist=collections.Counter(); mode_gt=0; mode_le=0
    endpoint_hist=collections.Counter()
    for off in range(0,len(data),8):
        a0,a1=data[off],data[off+1]
        endpoint_hist[(a0,a1)]+=1
        if a0>a1: mode_gt+=1
        else: mode_le+=1
        pal=bc4_palette(a0,a1)
        idx=int.from_bytes(data[off+2:off+8],'little')
        for k in range(16): hist[pal[(idx>>(3*k))&7]]+=1
    n=sum(hist.values())
    return {
        'block_count':len(data)//8,
        'endpoint0_gt_endpoint1_block_count':mode_gt,
        'endpoint0_le_endpoint1_block_count':mode_le,
        'texel_count':n,
        'preview_decoder_u8_min':min(hist) if hist else None,
        'preview_decoder_u8_max':max(hist) if hist else None,
        'preview_decoder_u8_unique_value_count':len(hist),
        'preview_decoder_u8_zero_count':hist.get(0,0),
        'preview_decoder_u8_255_count':hist.get(255,0),
        'preview_decoder_u8_mean':(sum(v*n0 for v,n0 in hist.items())/n if n else None),
        'semantic':'UNNAMED_BC4_SCALAR_CHANNEL',
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--texture-manifest',type=Path,required=True)
    ap.add_argument('--texture-root',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    man=json.loads(a.texture_manifest.read_text())
    violations=[];rows={}
    if man.get('schema')!='d1_remote_activity_texture_export/v1' or man.get('status')!='D1_REMOTE_ACTIVITY_TEXTURE_EXPORT_COMPLETE' or man.get('violations'):
        violations.append('texture export manifest is not exact complete')
    for tag in BC1_TAGS:
        try:
            r=manifest_row(man,tag)
            hi=r.get('header_info') or {}
            if hi.get('format_name')!='BC1': raise ValueError(f"format {hi.get('format_name')}")
            p=dds_path(a.texture_root,r)
            proof=bc1_alpha_proof(dds_payload(p,b'DXT1'))
            rows[tag]={
                'texture':tag,'format':'BC1','width':int(hi['width']),'height':int(hi['height']),
                'linear_sha256':r.get('linear_sha256'),'dds_sha256':sha256(p),**proof,
            }
        except Exception as ex: violations.append(f'{tag}: {ex}')
    try:
        r=manifest_row(man,BC4_TAG); hi=r.get('header_info') or {}
        if hi.get('format_name')!='BC4': raise ValueError(f"format {hi.get('format_name')}")
        p=dds_path(a.texture_root,r)
        rows[BC4_TAG]={
            'texture':BC4_TAG,'format':'BC4','width':int(hi['width']),'height':int(hi['height']),
            'linear_sha256':r.get('linear_sha256'),'dds_sha256':sha256(p),
            **bc4_scalar_census(dds_payload(p,b'ATI1')),
        }
    except Exception as ex: violations.append(f'{BC4_TAG}: {ex}')
    alpha_one=sorted(k for k,v in rows.items() if v.get('sample_alpha_constant_one'))
    out={
        'schema':'d1_crota_texture_channel_proof/v1',
        'status':'D1_CROTA_TEXTURE_CHANNEL_PROOF_EXACT' if len(rows)==4 and not violations else 'D1_CROTA_TEXTURE_CHANNEL_PROOF_PARTIAL',
        'textures':rows,
        'bc1_sample_alpha_constant_one_textures':alpha_one,
        'violations':violations,
        'semantic_boundary':{
            'BC1_alpha':'EXACT_DXT1_BLOCK_PROOF',
            'BC4_encoded_blocks':'EXACT_ENDPOINT_AND_INDEX_BYTES',
            'BC4_preview_decoder_census':'DETERMINISTIC_EXPORTER_EQUIVALENT_NOT_GPU_BIT_EXACT',
            'BC4_gpu_sample_numeric_values':'WITHHELD',
            'BC4_material_meaning':'WITHHELD',
        },
        'policy':'DDS files are manifest-hash-verified. BC1 alpha constancy is proven from exact DXT1 endpoint/index bytes, independent of PNG decoding. BC4 endpoint/index bytes are exact; its u8 census follows the deterministic exporter preview convention and is not asserted bit-identical to PS4 sampling. The channel remains semantically unnamed.',
    }
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'status':out['status'],'alpha_one':alpha_one,
                      'bc4':rows.get(BC4_TAG),'violations':violations},indent=2))
    return 0 if out['status']=='D1_CROTA_TEXTURE_CHANNEL_PROOF_EXACT' else 2

if __name__=='__main__':raise SystemExit(main())
