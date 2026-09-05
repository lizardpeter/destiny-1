#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, math, struct, sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import d1_tower_map_schema_validate_v5 as v5

STATIC_TABLE='80801A90'

def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def i32(b,o): return struct.unpack_from('<i',b,o)[0]
def i64(b,o): return struct.unpack_from('<q',b,o)[0]
def hx(x): return f'{x:08X}'

def dyn4(b,off,c):
    if off+16>len(b): return None
    count=i32(b,off); unk=u32(b,off+4); rel=i64(b,off+8)
    absolute=off+8+rel+0x10
    end=absolute+max(count,0)*4
    ok=count>=0 and absolute>=0 and end<=len(b)
    vals=[]
    classes=[]
    if ok and count<=10000:
        vals=[hx(u32(b,absolute+i*4)) for i in range(count)]
        classes=[(c.entry_meta(h) or {}).get('reference') for h in vals]
    return {'offset':off,'count':count,'unknown04':unk,'relative':rel,'absolute':absolute,'end':end,'ok':ok,'values':vals[:128],
            'all_static_table': bool(vals) and all(x==STATIC_TABLE for x in classes),
            'resolved_count':sum(x is not None for x in classes),'static_table_count':sum(x==STATIC_TABLE for x in classes)}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--snapshot',type=Path,action='append',required=True)
    ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('--tag-hash',action='append',required=True)
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args(); c=v5.v3.base.Corpus([p.resolve() for p in a.snapshot],a.runtime.resolve())
    rows=[]
    for raw in a.tag_hash:
        h=raw.upper().removeprefix('0X'); b,src=c.payload(h); meta=c.entry_meta(h)
        r={'hash':h,'meta':meta,'source':src}
        if b is None:
            r['error']='payload unavailable'; rows.append(r); continue
        r['payload_size']=len(b)
        r['hex_0_d8']=b[:0xD8].hex()
        r['dwords']=[{'offset':o,'hex':hx(u32(b,o)),'u32':u32(b,o),'i32':i32(b,o),'target':c.entry_meta(hx(u32(b,o)))} for o in range(0,min(len(b),0xD8),4)]
        r['dynamic_array_scan']=[x for off in range(0x08,min(len(b)-15,0xC9),8) if (x:=dyn4(b,off,c)) and x['ok']]
        # Source-layout interpretation at canonical offsets.
        if len(b)>=0x90:
            ic=i32(b,0x20); th=hx(u32(b,0x24)); r['canonical']={'instance_count':ic,'instance_transforms':th,'transform_target':c.entry_meta(th)}
            expected=max(ic,0)*0x40
            candidates=[]
            for hh,occ in c.occ.items():
                m=c.entry_meta(hh)
                if m and m.get('size')==expected:
                    pb,ps=c.payload(hh)
                    if pb is not None:
                        finite=all(math.isfinite(struct.unpack_from('<f',pb,o)[0]) for o in range(0,len(pb),4))
                        candidates.append({'hash':hh,'meta':m,'payload_source':ps,'all_finite_f32':finite})
            r['transform_size_candidates']=candidates
        rows.append(r)
    out={'status':'D1_STATIC_MAP_D1_LAYOUT_PROBE','static_table_class':STATIC_TABLE,'rows':rows}
    a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'rows':[{'hash':r['hash'],'payload_size':r.get('payload_size'),'canonical':r.get('canonical'),
      'plausible_dyn4':[{'offset':x['offset'],'count':x['count'],'static_table_count':x['static_table_count']} for x in r.get('dynamic_array_scan',[])] ,
      'transform_size_candidates':len(r.get('transform_size_candidates',[]))} for r in rows]},indent=2))
if __name__=='__main__': main()
