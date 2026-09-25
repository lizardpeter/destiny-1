#!/usr/bin/env python3
"""Static map generator for a user-supplied oo2core_3_win64.dll.

Emits PE metadata, sections, exports, imports and selected Oodle strings.
The DLL itself is never committed.
"""
from __future__ import annotations
import argparse, hashlib, json, struct
from pathlib import Path

u16=lambda b,o: struct.unpack_from("<H",b,o)[0]
u32=lambda b,o: struct.unpack_from("<I",b,o)[0]
u64=lambda b,o: struct.unpack_from("<Q",b,o)[0]

def cstr(b,off):
    end=b.find(b"\0",off)
    if end<0: end=len(b)
    return b[off:end].decode("ascii","replace")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("dll",type=Path)
    ap.add_argument("-o","--output",type=Path)
    a=ap.parse_args()
    data=a.dll.read_bytes()
    if data[:2] != b"MZ": raise SystemExit("not MZ")
    pe=u32(data,0x3c)
    if data[pe:pe+4] != b"PE\0\0": raise SystemExit("not PE")
    coff=pe+4
    machine,nsects,stamp,_,_,opt_size,chars=struct.unpack_from("<HHIIIHH",data,coff)
    opt=coff+20
    if u16(data,opt) != 0x20b: raise SystemExit("expected PE32+")
    image_base=u64(data,opt+24)
    entry_rva=u32(data,opt+16)
    size_image=u32(data,opt+56)
    ndirs=u32(data,opt+108)
    dirs=[(u32(data,opt+112+i*8),u32(data,opt+116+i*8)) for i in range(min(ndirs,16))]
    sec_off=opt+opt_size
    sections=[]
    for i in range(nsects):
        o=sec_off+i*40
        name=data[o:o+8].split(b"\0",1)[0].decode("ascii","replace")
        vsize,rva,raw_size,raw_offset=struct.unpack_from("<IIII",data,o+8)
        sections.append(dict(name=name,virtual_size=vsize,rva=rva,raw_size=raw_size,raw_offset=raw_offset,characteristics=u32(data,o+36)))
    def rva_off(rva):
        for s in sections:
            if s["rva"] <= rva < s["rva"]+max(s["virtual_size"],s["raw_size"]):
                return s["raw_offset"]+(rva-s["rva"])
        raise ValueError(f"unmapped RVA {rva:#x}")

    exports=[]
    if dirs and dirs[0][0]:
        o=rva_off(dirs[0][0])
        fields=struct.unpack_from("<IIHHIIIIIII",data,o)
        _,_,_,_,_,base,nfunc,nname,funcs_rva,names_rva,ords_rva=fields
        funcs=rva_off(funcs_rva); names=rva_off(names_rva); ords=rva_off(ords_rva)
        by_index={}
        for i in range(nname):
            by_index[u16(data,ords+2*i)]=cstr(data,rva_off(u32(data,names+4*i)))
        for i in range(nfunc):
            rva=u32(data,funcs+4*i)
            exports.append(dict(ordinal=base+i,rva=rva,va=image_base+rva,name=by_index.get(i)))

    imports=[]
    if len(dirs)>1 and dirs[1][0]:
        io=rva_off(dirs[1][0])
        while True:
            oft,tstamp,fchain,name_rva,ft=struct.unpack_from("<IIIII",data,io)
            if not any((oft,tstamp,fchain,name_rva,ft)): break
            dll=cstr(data,rva_off(name_rva))
            to=rva_off(oft or ft)
            symbols=[]; i=0
            while True:
                v=u64(data,to+8*i)
                if not v: break
                if v & (1<<63):
                    symbols.append(dict(ordinal=v & 0xffff))
                else:
                    ho=rva_off(v)
                    symbols.append(dict(hint=u16(data,ho),name=cstr(data,ho+2)))
                i+=1
            imports.append(dict(dll=dll,symbols=symbols))
            io+=20

    needles=(b"OodleLZ_",b"Kraken",b"Mermaid",b"Selkie",b"BitKnit",b"Akkorokamui",b"newLZ_",b"corruption")
    markers=[]
    for s in sections:
        if s["name"] not in (".rdata",".data"): continue
        lo=s["raw_offset"]; hi=lo+s["raw_size"]; i=lo
        while i<hi:
            if 32 <= data[i] < 127:
                j=i
                while j<hi and 32 <= data[j] < 127: j+=1
                raw=data[i:j]
                if len(raw)>=4 and any(n in raw for n in needles):
                    rva=s["rva"]+(i-lo)
                    markers.append(dict(text=raw.decode("ascii","replace"),file_offset=i,rva=rva,va=image_base+rva))
                i=max(j+1,i+1)
            else:
                i+=1

    out=dict(file=a.dll.name,size=len(data),sha256=hashlib.sha256(data).hexdigest(),machine=machine,timestamp=stamp,characteristics=chars,image_base=image_base,entry_rva=entry_rva,entry_va=image_base+entry_rva,size_of_image=size_image,sections=sections,exports=exports,imports=imports,markers=markers)
    text=json.dumps(out,indent=2,sort_keys=True)
    if a.output:
        a.output.parent.mkdir(parents=True,exist_ok=True)
        a.output.write_text(text+"\n",encoding="utf-8")
    else:
        print(text)
    return 0

if __name__=="__main__":
    raise SystemExit(main())
