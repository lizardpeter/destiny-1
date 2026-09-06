#!/usr/bin/env python3
from __future__ import annotations
import argparse, ctypes, hashlib, json, os, struct, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from d1_pkg_probe import BLOCK_SIZE, parse_header, parse_entries, parse_blocks, read_table, patch_path
from d1_oodle_probe import Oodle3

RAW_QUANTUM=0x4000

def _align_up(v:int,a:int)->int: return ((v+a-1)//a)*a

class EntryReader:
    def __init__(self,pkg:Path,runtime:Path):
        self.pkg=pkg.resolve(); self.oodle=Oodle3(runtime); self.cache={}
        with self.pkg.open('rb') as f:
            self.h=parse_header(f)
            self.entries=parse_entries(read_table(f,self.h['entry_table_offset'],self.h['entry_table_count'],16),self.h['pkg_id'])
            self.blocks=parse_blocks(read_table(f,self.h['block_table_offset'],self.h['block_table_count'],32))
        self.block_used_end=[0]*len(self.blocks)
        for e in self.entries:
            remaining=int(e['file_size']); bi=int(e['starting_block']); off=int(e['starting_block_offset'])
            while remaining>0 and bi<len(self.blocks):
                n=min(remaining,BLOCK_SIZE-off); self.block_used_end[bi]=max(self.block_used_end[bi],off+n)
                remaining-=n; bi+=1; off=0
    def expected_raw_len(self,i:int)->int:
        used=self.block_used_end[i]
        return BLOCK_SIZE if used<=0 else min(BLOCK_SIZE,_align_up(used,RAW_QUANTUM))
    def block(self,i:int)->bytes:
        if i in self.cache:return self.cache[i]
        b=self.blocks[i]; owner=patch_path(self.pkg,b['patch_id'])
        if not owner.exists(): raise FileNotFoundError(str(owner))
        with owner.open('rb') as f:f.seek(b['offset']); raw=f.read(b['size'])
        if hashlib.sha1(raw).hexdigest()!=b['sha1']:raise RuntimeError(f'block {i} sha1 mismatch')
        if b['compressed']:
            expected=self.expected_raw_len(i); dec=self.oodle.decompress(raw,raw_capacity=expected)
            if len(dec)!=expected: raise RuntimeError(f'block {i} decoded {len(dec)} bytes, expected {expected}')
        else: dec=raw
        if len(dec)>BLOCK_SIZE:raise RuntimeError(f'block {i} oversized')
        if len(dec)<BLOCK_SIZE:dec=dec+b'\0'*(BLOCK_SIZE-len(dec))
        self.cache[i]=dec; return dec
    def entry(self,i:int)->bytes:
        e=self.entries[i]; remaining=e['file_size']; bi=e['starting_block']; off=e['starting_block_offset']; out=bytearray()
        while remaining:
            blk=self.block(bi); n=min(remaining,BLOCK_SIZE-off); out+=blk[off:off+n]; remaining-=n; bi+=1; off=0
        return bytes(out)
    def available(self,i:int)->bool:
        e=self.entries[i]; span=e['starting_block_offset']+e['file_size']; count=max(1,(span+BLOCK_SIZE-1)//BLOCK_SIZE)
        return all(patch_path(self.pkg,self.blocks[b]['patch_id']).exists() for b in range(e['starting_block'],e['starting_block']+count))

def u16(b,o): return struct.unpack_from('<H',b,o)[0]
def s16(b,o): return struct.unpack_from('<h',b,o)[0]
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def s32(b,o): return struct.unpack_from('<i',b,o)[0]
def u64(b,o): return struct.unpack_from('<Q',b,o)[0]

def decode_known(e,b,platform):
    t,s=e['type'],e['subtype']; d={'index':e['index'],'tag_hash':e['tag_hash'],'type':t,'subtype':s,'size':len(b),'reference':e['reference'],'entry_b':e['entry_b'],'sha256':hashlib.sha256(b).hexdigest(),'prefix':b[:64].hex()}
    if (t,s)==(32,4) and len(b)>=12:
        d['kind']='VertexBufferHeader'; d.update(data_size=u32(b,0),stride=s16(b,4),vertex_type=s16(b,6),marker=s32(b,8),marker_hex=f'{u32(b,8):08X}')
    elif (t,s)==(32,6) and len(b)>=24:
        d['kind']='IndexBufferHeader'; d.update(unk00=b[0],is32bit=bool(b[1]),unk02=s16(b,2),zeros04=s32(b,4),data_size=u64(b,8),marker=s32(b,16),marker_hex=f'{u32(b,16):08X}',zeros14=s32(b,20))
    elif (t,s)==(32,1):
        d['kind']='Texture2DHeader'
        if platform=='PS4' and len(b)>=0x3c:
            d.update(data_size=u32(b,0),unk4=b[4],unk5=b[5],surface_format_raw=u16(b,6),surface_format=(u16(b,6)>>4)&0x3f,magic=f'{u32(b,0x24):08X}',width=u16(b,0x28),height=u16(b,0x2a),depth=u16(b,0x2c),array_size=u16(b,0x2e),flags1=f'{u32(b,0x30):08X}',flags2=f'{u32(b,0x34):08X}',flags3=f'{u32(b,0x38):08X}')
        elif platform=='XboxOne' and len(b)>=0x38:
            d.update(dxgi_format=u32(b,0),tile_mode=u32(b,4),magic=f'{u32(b,0x2c):08X}',width=u16(b,0x30),height=u16(b,0x32),depth=u16(b,0x34),array_size=u16(b,0x36),flags1=f'{u32(b,0x38):08X}' if len(b)>=0x3c else None,flags2=f'{u32(b,0x3c):08X}' if len(b)>=0x40 else None,flags3=f'{u32(b,0x40):08X}' if len(b)>=0x44 else None)
    elif (t,s)==(32,2):
        d['kind']='TextureCubeHeader'
        if platform=='PS4' and len(b)>=0x3c:
            d.update(data_size=u32(b,0),unk4=b[4],unk5=b[5],surface_format_raw=u16(b,6),surface_format=(u16(b,6)>>4)&0x3f,magic=f'{u32(b,0x24):08X}',width=u16(b,0x28),height=u16(b,0x2a),depth=u16(b,0x2c),array_size=u16(b,0x2e),flags1=f'{u32(b,0x30):08X}',flags2=f'{u32(b,0x34):08X}',flags3=f'{u32(b,0x38):08X}')
        elif platform=='XboxOne' and len(b)>=0x38:
            d.update(dxgi_format=u32(b,0),tile_mode=u32(b,4),magic=f'{u32(b,0x2c):08X}',width=u16(b,0x30),height=u16(b,0x32),depth=u16(b,0x34),array_size=u16(b,0x36),flags1=f'{u32(b,0x38):08X}' if len(b)>=0x3c else None,flags2=f'{u32(b,0x3c):08X}' if len(b)>=0x40 else None,flags3=f'{u32(b,0x40):08X}' if len(b)>=0x44 else None)
    elif (t,s)==(32,7) and len(b)>=16:
        d['kind']='GpuSubtype7Header'; d.update(word0=f'{u32(b,0):08X}',word1=f'{u32(b,4):08X}',unit_count=u32(b,8),derived_data_size=u32(b,8)*16,marker=f'{u32(b,12):08X}')
    elif (t,s)==(32,8):
        d['kind']='PixelShaderHeader'
        if len(b)>=4:
            d.update(packed0=f'{u32(b,0):08X}',embedded_data_size=u32(b,0)&0x00ffffff,packed0_high8=(u32(b,0)>>24)&0xff)
    elif (t,s)==(16,0): d['kind']='Tag'
    return d

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('pkg',type=Path); ap.add_argument('--runtime',type=Path,required=True); ap.add_argument('--types',nargs='*'); ap.add_argument('--all-available',action='store_true'); ap.add_argument('--entry',type=int,action='append'); ap.add_argument('--tag-hash',action='append'); ap.add_argument('-o','--output',type=Path); ap.add_argument('--dump-dir',type=Path)
    a=ap.parse_args(); r=EntryReader(a.pkg,a.runtime); wanted=None
    if a.types:
        wanted=set()
        for x in a.types:
            t,s=x.split(':');wanted.add((int(t,0),int(s,0)))
    by_hash={e['tag_hash'].upper():e for e in r.entries}
    if a.entry and a.tag_hash:
        raise SystemExit('--entry and --tag-hash are mutually exclusive')
    missing_hashes=[]
    if a.entry:
        inds=a.entry
    elif a.tag_hash:
        inds=[]
        for raw in a.tag_hash:
            h=raw.upper().removeprefix('0X'); e=by_hash.get(h)
            if e is None: missing_hashes.append(h)
            elif wanted is None or (e['type'],e['subtype']) in wanted: inds.append(e['index'])
    else:
        inds=[e['index'] for e in r.entries if (wanted is None or (e['type'],e['subtype']) in wanted)]
    out=[]; unavailable=[]; errors=[]
    for i in inds:
        if not r.available(i): unavailable.append(i); continue
        try:
            b=r.entry(i); d=decode_known(r.entries[i],b,r.h['platform']); out.append(d)
            if a.dump_dir:
                a.dump_dir.mkdir(parents=True,exist_ok=True); (a.dump_dir/f"{r.entries[i]['tag_hash']}_{i:04d}_{r.entries[i]['type']}_{r.entries[i]['subtype']}.bin").write_bytes(b)
        except Exception as ex: errors.append({'index':i,'error':repr(ex)})
    rep={'package':str(r.pkg),'platform':r.h['platform'],'pkg_id':r.h['pkg_id'],'selected':len(inds),'decoded':len(out),'missing_tag_hashes':missing_hashes,'unavailable':unavailable,'errors':errors,'entries':out}
    text=json.dumps(rep,indent=2)
    if a.output:a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(text+'\n');print('wrote',a.output)
    else:print(text)
if __name__=='__main__':main()
