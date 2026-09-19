#!/usr/bin/env python3
"""Prove exact alpha domains for D1 BC1 textures from retail DDS block bytes.

The D1 texture artifact already source-closes texture header, backing FileHash,
linearized payload SHA256 and DDS export SHA256.  This tool revalidates that
identity, parses the exact DXT1 blocks, and counts use of transparent palette
index 3 in three-color mode (color0 <= color1).

For BC1/DXT1:
* four-color mode (color0 > color1): all four palette entries have alpha 1;
* three-color mode (color0 <= color1): only palette index 3 has alpha 0.

Therefore alpha is source-proven constant 1 exactly when no texel selects index 3
from a three-color block.  No RGB role or material semantic is inferred.
"""
from __future__ import annotations
import argparse, hashlib, json, struct
from pathlib import Path

DDS_MAGIC=b'DDS '
DDS_HEADER_BYTES=128
DXT1=b'DXT1'

def sha256_bytes(b:bytes)->str:
    return hashlib.sha256(b).hexdigest()

def norm(x)->str:
    return str(x).upper().removeprefix('0X').zfill(8)

def manifest_row(man:dict,h:str)->dict:
    rows=[x for x in man.get('rows',[]) if norm(x.get('texture'))==h]
    if len(rows)!=1:
        raise ValueError(f'{h}: expected one manifest row, got {len(rows)}')
    return rows[0]

def dds_file(row:dict,root:Path)->Path:
    fs=[x for x in row.get('files',[]) if x.get('kind')=='dds']
    if len(fs)!=1:
        raise ValueError(f"{row.get('texture')}: expected one DDS file, got {len(fs)}")
    p=root/fs[0]['path']
    if not p.is_file():
        raise FileNotFoundError(p)
    raw=p.read_bytes()
    if len(raw)!=int(fs[0]['bytes']):
        raise ValueError(f'{p}: byte length drift {len(raw)} != {fs[0]["bytes"]}')
    got=sha256_bytes(raw)
    if got!=str(fs[0]['sha256']).lower():
        raise ValueError(f'{p}: DDS SHA drift {got} != {fs[0]["sha256"]}')
    return p

def scan_bc1(path:Path,row:dict)->dict:
    raw=path.read_bytes()
    if len(raw)<DDS_HEADER_BYTES or raw[:4]!=DDS_MAGIC:
        raise ValueError(f'{path}: not a DDS file')
    fourcc=raw[84:88]
    if fourcc!=DXT1:
        raise ValueError(f'{path}: expected DXT1 FourCC, got {fourcc!r}')
    w=struct.unpack_from('<I',raw,16)[0]
    h=struct.unpack_from('<I',raw,12)[0]
    hi=row.get('header_info') or {}
    if (w,h)!=(int(hi.get('width',-1)),int(hi.get('height',-1))):
        raise ValueError(f'{path}: dimensions {(w,h)} != manifest {(hi.get("width"),hi.get("height"))}')
    if str(row.get('format_name'))!='BC1':
        raise ValueError(f"{path}: manifest format {row.get('format_name')} != BC1")
    payload=raw[DDS_HEADER_BYTES:]
    bw=(w+3)//4; bh=(h+3)//4; expected=bw*bh*8
    if len(payload)!=expected:
        raise ValueError(f'{path}: BC1 payload bytes {len(payload)} != {expected}')

    blocks=bw*bh
    three=0; four=0; transparent_blocks=0; transparent_texels=0
    three_index3_hist={}
    for off in range(0,len(payload),8):
        c0,c1,idx=struct.unpack_from('<HHI',payload,off)
        if c0>c1:
            four+=1
            continue
        three+=1
        n3=0
        for i in range(16):
            if ((idx>>(2*i))&3)==3:
                n3+=1
        if n3:
            transparent_blocks+=1
            transparent_texels+=n3
            three_index3_hist[str(n3)]=three_index3_hist.get(str(n3),0)+1
    if blocks!=three+four:
        raise AssertionError('block accounting failure')
    alpha_domain=[1.0] if transparent_texels==0 else [0.0,1.0]
    return {
        'width':w,'height':h,'block_count':blocks,
        'four_color_block_count':four,
        'three_color_block_count':three,
        'three_color_transparent_index_block_count':transparent_blocks,
        'transparent_texel_count':transparent_texels,
        'three_color_transparent_texels_per_block_histogram':three_index3_hist,
        'alpha_domain':alpha_domain,
        'alpha_exact_one':transparent_texels==0,
    }

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--manifest',type=Path,required=True)
    ap.add_argument('--texture-root',type=Path,required=True)
    ap.add_argument('--texture',action='append',required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()

    man=json.loads(a.manifest.read_text())
    violations=[];rows=[]
    if man.get('status') not in ('D1_CROTA_TEXTURE_EXPORT_COMPLETE','D1_TEXTURE_EXPORT_COMPLETE'):
        # Historical artifact schema/status variants are accepted only if it is
        # otherwise violation-free and every selected row revalidates below.
        if man.get('violations'):
            violations.append(f"texture manifest status/violations not clean: {man.get('status')}")
    if man.get('violations'):
        violations.append(f"texture manifest violations: {man.get('violations')}")

    for rawh in a.texture:
        h=norm(rawh)
        try:
            mr=manifest_row(man,h)
            p=dds_file(mr,a.texture_root)
            s=scan_bc1(p,mr)
            rows.append({
                'texture':h,
                'dds_path':str(p),
                'dds_sha256':sha256_bytes(p.read_bytes()),
                'backing_hash':norm(mr.get('backing_hash')),
                'backing_sha256':str(mr.get('backing_sha256')),
                'linear_sha256':str(mr.get('linear_sha256')),
                'format_name':mr.get('format_name'),
                **s,
            })
        except Exception as ex:
            violations.append(f'{h}: {ex}')

    out={
        'schema':'d1_bc1_alpha_domain_proof/v1',
        'status':'D1_BC1_ALPHA_DOMAIN_EXACT' if len(rows)==len(a.texture) and not violations else 'D1_BC1_ALPHA_DOMAIN_PARTIAL',
        'texture_count':len(rows),'textures':rows,'violations':violations,
        'semantic_boundary':{
            'bc1_alpha_domain':'EXACT_FROM_DXT1_BLOCK_BYTES',
            'rgb_semantic':'WITHHELD',
            'material_role':'WITHHELD',
        },
        'policy':'Alpha domain is derived only from exact DXT1 endpoint ordering and 2-bit palette indices after manifest/DDS hash revalidation. PNG decoding is not evidence for this promotion.',
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({
        'status':out['status'],
        'textures':[{
            'texture':x['texture'],'blocks':x['block_count'],
            'three_color_blocks':x['three_color_block_count'],
            'transparent_blocks':x['three_color_transparent_index_block_count'],
            'transparent_texels':x['transparent_texel_count'],
            'alpha_domain':x['alpha_domain'],
        } for x in rows],
        'violations':violations,
    },indent=2))
    return 0 if out['status']=='D1_BC1_ALPHA_DOMAIN_EXACT' else 2

if __name__=='__main__':
    raise SystemExit(main())
