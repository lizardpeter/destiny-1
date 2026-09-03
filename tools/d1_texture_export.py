#!/usr/bin/env python3
"""Destiny 1 Rise of Iron PS4 texture exporter.

Follows the observed Tiger texture chain
    32:1 header -> 65:1 streamed mip record -> 5:1 full-resolution backing
and exports faithful linearized DDS plus PNG.
"""
from __future__ import annotations
import argparse, io, json, struct, sys
from pathlib import Path

try:
    from PIL import Image
except Exception:
    Image = None

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from d1_entry_extract import EntryReader

GCN_BC1=0x23; GCN_BC2=0x24; GCN_BC3=0x25; GCN_BC4=0x26; GCN_BC5=0x27
GCN_RGBA8=0x0A
COMPRESSED={GCN_BC1,GCN_BC2,GCN_BC3,GCN_BC4,GCN_BC5,0x28,0x29}
BLOCK_SIZE={GCN_BC1:8,GCN_BC4:8,GCN_BC2:16,GCN_BC3:16,GCN_BC5:16,0x28:16,0x29:16}
BPP={0x01:8,0x02:16,0x03:16,0x04:32,0x05:32,0x06:32,0x07:32,0x08:32,0x09:32,0x0A:32,0x0B:64,0x0C:64,0x0D:96,0x0E:128}
FORMAT_NAME={GCN_BC1:'BC1',GCN_BC2:'BC2',GCN_BC3:'BC3',GCN_BC4:'BC4',GCN_BC5:'BC5',GCN_RGBA8:'RGBA8'}

def u16(b,o): return struct.unpack_from('<H',b,o)[0]
def u32(b,o): return struct.unpack_from('<I',b,o)[0]

def morton(t:int,sx:int=8,sy:int=8)->int:
    num1=num2=1; num3=t; num4=sx; num5=sy; num6=num7=0
    while num4>1 or num5>1:
        if num4>1:
            num6 += num2*(num3&1); num3 >>= 1; num2 *= 2; num4 >>= 1
        if num5>1:
            num7 += num1*(num3&1); num3 >>= 1; num1 *= 2; num5 >>= 1
    return num7*sx+num6

def ceil_pow2(x:int)->int:
    return 1 if x<=1 else 1<<(x-1).bit_length()

def unswizzle_ps4(data:bytes,width:int,height:int,array_size:int,gfmt:int)->bytes:
    compressed=gfmt in COMPRESSED
    pixel_block=4 if compressed else 1
    block_size=BLOCK_SIZE.get(gfmt, BPP.get(gfmt,0)//8)
    if not block_size: raise NotImplementedError(f'unsupported GCN surface format {gfmt:#x}')
    width_src=ceil_pow2(width) if compressed else width
    height_src=ceil_pow2(height) if compressed else height
    width_dest=width//pixel_block; height_dest=height//pixel_block
    htiles=(height_src//pixel_block+7)//8; wtiles=(width_src//pixel_block+7)//8
    out=bytearray(len(data)); src=0
    for ty in range(htiles):
        for tx in range(wtiles):
            for t in range(64):
                p=morton(t); y=ty*8+p//8; x=tx*8+p%8
                if x<width_dest and y<height_dest:
                    dst=block_size*(y*width_dest+x)
                    if src+block_size<=len(data) and dst+block_size<=len(out):
                        out[dst:dst+block_size]=data[src:src+block_size]
                src += block_size
    return bytes(out)

def expected_base_size(w:int,h:int,gfmt:int)->int|None:
    if gfmt in {GCN_BC1,GCN_BC4}: return w*h//2
    if gfmt in {GCN_BC2,GCN_BC3,GCN_BC5,0x28,0x29}: return w*h
    if gfmt in BPP: return w*h*(BPP[gfmt]//8)
    return None

def make_dds(data:bytes,w:int,h:int,gfmt:int)->bytes:
    DDSD_CAPS=1; DDSD_HEIGHT=2; DDSD_WIDTH=4; DDSD_PITCH=8; DDSD_PIXELFORMAT=0x1000; DDSD_LINEARSIZE=0x80000
    DDPF_ALPHAPIXELS=1; DDPF_FOURCC=4; DDPF_RGB=0x40; DDSCAPS_TEXTURE=0x1000
    fourcc={GCN_BC1:b'DXT1',GCN_BC2:b'DXT3',GCN_BC3:b'DXT5',GCN_BC4:b'ATI1',GCN_BC5:b'ATI2'}.get(gfmt)
    compressed=fourcc is not None
    if compressed:
        pf_flags=DDPF_FOURCC; rgbbits=0; masks=(0,0,0,0); pitch=len(data)
    elif gfmt==GCN_RGBA8:
        fourcc=b'\0\0\0\0'; pf_flags=DDPF_RGB|DDPF_ALPHAPIXELS; rgbbits=32
        masks=(0x000000FF,0x0000FF00,0x00FF0000,0xFF000000); pitch=w*4
    else:
        raise NotImplementedError(f'DDS wrapping for GCN {gfmt:#x}')
    flags=DDSD_CAPS|DDSD_HEIGHT|DDSD_WIDTH|DDSD_PIXELFORMAT|(DDSD_LINEARSIZE if compressed else DDSD_PITCH)
    hdr=bytearray(124)
    struct.pack_into('<I',hdr,0,124); struct.pack_into('<I',hdr,4,flags)
    struct.pack_into('<I',hdr,8,h); struct.pack_into('<I',hdr,12,w); struct.pack_into('<I',hdr,16,pitch)
    struct.pack_into('<I',hdr,72,32); struct.pack_into('<I',hdr,76,pf_flags); hdr[80:84]=fourcc
    struct.pack_into('<I',hdr,84,rgbbits)
    for off,val in zip((88,92,96,100),masks): struct.pack_into('<I',hdr,off,val)
    struct.pack_into('<I',hdr,104,DDSCAPS_TEXTURE)
    return b'DDS '+bytes(hdr)+data

def decode_header(b:bytes)->dict:
    if len(b)<0x3c: raise ValueError('short PS4 ROI texture header')
    raw=u16(b,6)
    return {'surface_format_raw':raw,'surface_format':(raw>>4)&0x3f,'magic':f'{u32(b,0x24):08X}',
            'width':u16(b,0x28),'height':u16(b,0x2a),'depth':u16(b,0x2c),'array_size':u16(b,0x2e),
            'flags1':u32(b,0x30),'flags2':u32(b,0x34),'flags3':u32(b,0x38)}

def follow_backing(by_hash:dict,header:dict):
    mid=by_hash.get(header['reference'].upper()); backing=mid
    if mid and mid['reference'].upper() in by_hash: backing=by_hash[mid['reference'].upper()]
    return mid,backing

def export_reader(r,outdir:Path,tag_hashes:list[str]|None=None)->dict:
    if r.h['platform']!='PS4': raise ValueError('this exporter currently targets D1 ROI PS4')
    outdir.mkdir(parents=True,exist_ok=True); by={e['tag_hash'].upper():e for e in r.entries}
    wanted={x.upper().removeprefix('0X') for x in tag_hashes or []}
    headers=[e for e in r.entries if (e['type'],e['subtype'])==(32,1) and (not wanted or e['tag_hash'].upper() in wanted)]
    rows=[]
    for e in headers:
        if not r.available(e['index']): rows.append({'header':e['tag_hash'],'available':False}); continue
        h=decode_header(r.entry(e['index'])); mid,backing=follow_backing(by,e)
        if not backing or not r.available(backing['index']):
            rows.append({'header':e['tag_hash'],'available':True,'error':'backing unavailable','header_info':h}); continue
        raw=r.entry(backing['index']); expected=expected_base_size(h['width'],h['height'],h['surface_format'])
        if expected and len(raw)>=expected: raw=raw[:expected]
        swizzled=((h['flags1']&0xC00)!=0x400) or h['array_size']==6
        linear=unswizzle_ps4(raw,h['width'],h['height'],h['array_size'],h['surface_format']) if swizzled else raw
        fmt_name=FORMAT_NAME.get(h['surface_format']) or ('GCN%02X' % h['surface_format'])
        stem=f"{e['tag_hash']}_{h['width']}x{h['height']}_{fmt_name}"
        dds=make_dds(linear,h['width'],h['height'],h['surface_format']); (outdir/(stem+'.dds')).write_bytes(dds)
        png_name=None; png_error=None
        if Image is not None:
            try:
                im=Image.open(io.BytesIO(dds)); im.load(); png_name=stem+'.png'; im.save(outdir/png_name)
            except Exception as ex: png_error=repr(ex)
        rows.append({'header':e['tag_hash'],'stream':mid['tag_hash'] if mid else None,'backing':backing['tag_hash'],
                     **h,'format_name':fmt_name,'backing_bytes':len(raw),'unswizzled':swizzled,
                     'dds':stem+'.dds','png':png_name,'png_error':png_error})
    rep={'package':str(r.pkg),'platform':r.h['platform'],'texture_count':len(rows),'textures':rows}
    (outdir/'texture_manifest.json').write_text(json.dumps(rep,indent=2)+'\n'); return rep

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('pkg',type=Path); ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('--tag-hash',action='append'); ap.add_argument('--out',type=Path,required=True); a=ap.parse_args()
    r=EntryReader(a.pkg,a.runtime); rep=export_reader(r,a.out,tag_hashes=a.tag_hash)
    print(json.dumps({'package':rep['package'],'texture_count':rep['texture_count'],'out':str(a.out)},indent=2))
if __name__=='__main__': main()
