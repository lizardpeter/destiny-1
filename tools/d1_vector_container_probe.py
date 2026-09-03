#!/usr/bin/env python3
"""Probe final-era D1 Xbox One pixel/vertex Vector4 container tags.

Observed Xbox material class 0x80801C32 references structured tag class
0x80801AA5 from VSVector4Container / PSVector4Container fields.  Real binary
corpus shows a fixed 0x30-byte container header followed by N raw vec4 values.
"""
from __future__ import annotations
import argparse, collections, json, struct, sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from d1_entry_extract import EntryReader

VECTOR_CONTAINER_CLASS='80801AA5'
HEADER_SIZE=0x30
VEC4_SIZE=0x10
ARRAY_CLASS=0x80800184
ELEMENT_CLASS=0x80800009

def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def u64(b,o): return struct.unpack_from('<Q',b,o)[0]

def parse_vector_container(b: bytes) -> dict:
    if len(b)<HEADER_SIZE:
        raise ValueError(f'vector container shorter than {HEADER_SIZE:#x}')
    payload=len(b)-HEADER_SIZE
    d={
        'actual_file_size':len(b),
        'declared_file_size':u64(b,0x00),
        'payload_size':u64(b,0x08),
        'stride':u64(b,0x10),
        'zero18':u32(b,0x18),
        'array_class':f'{u32(b,0x1c):08X}',
        'repeated_payload_size':u64(b,0x20),
        'element_class':f'{u32(b,0x28):08X}',
        'zero2c':u32(b,0x2c),
        'vector_count': payload//VEC4_SIZE if payload%VEC4_SIZE==0 else None,
    }
    d['checks']={
        'declared_file_size_exact':d['declared_file_size']==len(b),
        'payload_size_exact':d['payload_size']==payload,
        'stride_vec4':d['stride']==VEC4_SIZE,
        'zero18':d['zero18']==0,
        'array_class_80800184':d['array_class']==f'{ARRAY_CLASS:08X}',
        'repeated_payload_size_exact':d['repeated_payload_size']==payload,
        'element_class_80800009':d['element_class']==f'{ELEMENT_CLASS:08X}',
        'zero2c':d['zero2c']==0,
        'payload_vec4_aligned':payload%VEC4_SIZE==0,
    }
    return d

def count_from_metadata_size(size:int)->int|None:
    payload=size-HEADER_SIZE
    return payload//VEC4_SIZE if size>=HEADER_SIZE and payload%VEC4_SIZE==0 else None

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('pkg',type=Path); ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('--tag-hash',action='append')
    ap.add_argument('-o','--output',type=Path)
    a=ap.parse_args(); r=EntryReader(a.pkg,a.runtime)
    wanted={h.upper().removeprefix('0X') for h in a.tag_hash or []}
    rows=[]; counts=collections.Counter(); inv=collections.Counter()
    for e in r.entries:
        if e['type']!=16 or e['subtype']!=0 or e['reference'].upper()!=VECTOR_CONTAINER_CLASS: continue
        if wanted and e['tag_hash'].upper() not in wanted: continue
        row={'tag_hash':e['tag_hash'],'entry_index':e['index'],'size':e['file_size'],'available':r.available(e['index']),
             'metadata_vector_count':count_from_metadata_size(e['file_size'])}
        if row['available']:
            try:
                row.update(parse_vector_container(r.entry(e['index'])))
                counts[row['vector_count']]+=1
                for k,v in row['checks'].items():
                    if v: inv[k]+=1
            except Exception as ex: row['error']=repr(ex)
        rows.append(row)
    resident=[x for x in rows if x['available']]
    rep={'package':str(r.pkg),'platform':r.h['platform'],'class_hash':VECTOR_CONTAINER_CLASS,
         'total_entries':len(rows),'resident_entries':len(resident),
         'all_resident_invariants':{k:inv[k]==len(resident) for k in [
             'declared_file_size_exact','payload_size_exact','stride_vec4','zero18','array_class_80800184',
             'repeated_payload_size_exact','element_class_80800009','zero2c','payload_vec4_aligned']},
         'vector_count_distribution':{str(k):v for k,v in sorted(counts.items())},'rows':rows}
    text=json.dumps(rep,indent=2)
    if a.output:
        a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(text+'\n'); print('wrote',a.output)
    else: print(text)
if __name__=='__main__':main()
