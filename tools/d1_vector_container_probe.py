#!/usr/bin/env python3
"""Probe final-era Destiny 1 material Vector4 constant resources.

Two retail representations are currently proven:

PS4 ROI
    material VS/PSVector4Container FileHash
      -> FileEntry type 32, subtype 7, 16-byte GPU-resource header
      -> FileEntry.Reference raw payload

    The header's u32 at +0x08 is the vec4 unit count and the linked payload
    size is exactly unit_count * 16 across the validated corpus.

Xbox One ROI
    material VS/PSVector4Container FileHash
      -> structured class 0x80801AA5

    The structured resource has a fixed 0x30-byte header followed by N raw
    vec4 values.

The probe preserves IEEE-754 interpretations and exact u32 words so constants
can be compared without losing bit-level evidence.
"""
from __future__ import annotations
import argparse, collections, json, math, struct, sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from d1_entry_extract import EntryReader

VECTOR_CONTAINER_CLASS='80801AA5'
XBOX_HEADER_SIZE=0x30
PS4_HEADER_SIZE=0x10
VEC4_SIZE=0x10
ARRAY_CLASS=0x80800184
ELEMENT_CLASS=0x80800009

def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def u64(b,o): return struct.unpack_from('<Q',b,o)[0]

def safe_float(v: float):
    if math.isfinite(v):
        return v
    if math.isnan(v):
        return 'nan'
    return 'inf' if v > 0 else '-inf'

def decode_vec4_payload(b: bytes, base_offset: int = 0) -> list[dict]:
    if len(b)%VEC4_SIZE:
        raise ValueError(f'vec4 payload size {len(b)} is not 16-byte aligned')
    values=[]
    for i in range(len(b)//VEC4_SIZE):
        o=i*VEC4_SIZE
        raw=struct.unpack_from('<4I',b,o)
        flt=struct.unpack_from('<4f',b,o)
        values.append({
            'index':i,
            'offset':base_offset+o,
            'float4':[safe_float(x) for x in flt],
            'u32_hex':[f'{x:08X}' for x in raw],
        })
    return values

def parse_xbox_vector_container(b: bytes) -> dict:
    if len(b)<XBOX_HEADER_SIZE:
        raise ValueError(f'vector container shorter than {XBOX_HEADER_SIZE:#x}')
    payload=len(b)-XBOX_HEADER_SIZE
    d={
        'representation':'XboxStructured80801AA5',
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
    d['vectors']=decode_vec4_payload(b[XBOX_HEADER_SIZE:],XBOX_HEADER_SIZE) if d['vector_count'] is not None else []
    return d

def xbox_count_from_metadata_size(size:int)->int|None:
    payload=size-XBOX_HEADER_SIZE
    return payload//VEC4_SIZE if size>=XBOX_HEADER_SIZE and payload%VEC4_SIZE==0 else None

def parse_ps4_gpu_header(r: EntryReader, e: dict, by_hash: dict[str,dict]) -> dict:
    b=r.entry(e['index'])
    if len(b)<PS4_HEADER_SIZE:
        raise ValueError(f'PS4 subtype-7 header shorter than {PS4_HEADER_SIZE:#x}')
    count=u32(b,0x08)
    target=by_hash.get(e['reference'].upper())
    d={
        'representation':'PS4GpuSubtype7Header',
        'actual_header_size':len(b),
        'word0':f'{u32(b,0x00):08X}',
        'word1':f'{u32(b,0x04):08X}',
        'unit_count':count,
        'vector_count':count,
        'marker':f'{u32(b,0x0c):08X}',
        'payload_reference':e['reference'],
        'expected_payload_size':count*VEC4_SIZE,
    }
    if target is None:
        d['payload_local_entry']=None
        d['checks']={'header_size_16':len(b)==PS4_HEADER_SIZE,'payload_entry_resolved':False}
        d['vectors']=[]
        return d
    d['payload_local_entry']={
        'tag_hash':target['tag_hash'],'entry_index':target['index'],'type':target['type'],'subtype':target['subtype'],
        'size':target['file_size'],'reference':target['reference'],'available':r.available(target['index'])
    }
    checks={
        'header_size_16':len(b)==PS4_HEADER_SIZE,
        'payload_entry_resolved':True,
        'payload_size_matches_unit_count':target['file_size']==count*VEC4_SIZE,
        'payload_vec4_aligned':target['file_size']%VEC4_SIZE==0,
    }
    if r.available(target['index']):
        payload=r.entry(target['index'])
        checks['actual_payload_size_matches_unit_count']=len(payload)==count*VEC4_SIZE
        d['vectors']=decode_vec4_payload(payload)
    else:
        checks['actual_payload_size_matches_unit_count']=False
        d['vectors']=[]
    d['checks']=checks
    return d

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('pkg',type=Path); ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('--tag-hash',action='append')
    ap.add_argument('-o','--output',type=Path)
    a=ap.parse_args(); r=EntryReader(a.pkg,a.runtime)
    wanted={h.upper().removeprefix('0X') for h in a.tag_hash or []}
    by_hash={e['tag_hash'].upper():e for e in r.entries}
    rows=[]; counts=collections.Counter(); inv=collections.Counter()

    for e in r.entries:
        h=e['tag_hash'].upper()
        if wanted and h not in wanted: continue

        is_ps4 = r.h['platform']=='PS4' and e['type']==32 and e['subtype']==7
        is_xbox = e['type']==16 and e['subtype']==0 and e['reference'].upper()==VECTOR_CONTAINER_CLASS
        if not (is_ps4 or is_xbox): continue

        row={'tag_hash':e['tag_hash'],'entry_index':e['index'],'type':e['type'],'subtype':e['subtype'],
             'size':e['file_size'],'reference':e['reference'],'available':r.available(e['index'])}
        if is_xbox:
            row['metadata_vector_count']=xbox_count_from_metadata_size(e['file_size'])
        if row['available']:
            try:
                if is_ps4:
                    row.update(parse_ps4_gpu_header(r,e,by_hash))
                else:
                    row.update(parse_xbox_vector_container(r.entry(e['index'])))
                counts[row.get('vector_count')]+=1
                for k,v in row.get('checks',{}).items():
                    if v: inv[k]+=1
            except Exception as ex:
                row['error']=repr(ex)
        rows.append(row)

    # If explicit hashes were requested, make missing selections visible rather than silently returning zero rows.
    seen={x['tag_hash'].upper() for x in rows}
    for h in sorted(wanted-seen):
        rows.append({'tag_hash':h,'missing_or_wrong_representation':True})

    resident=[x for x in rows if x.get('available')]
    rep={
        'package':str(r.pkg),'platform':r.h['platform'],'xbox_class_hash':VECTOR_CONTAINER_CLASS,
        'total_entries':len(rows),'resident_entries':len(resident),
        'vector_count_distribution':{str(k):v for k,v in sorted(counts.items(),key=lambda kv:(str(kv[0])))},
        'validated_check_counts':dict(sorted(inv.items())),
        'rows':rows,
    }
    text=json.dumps(rep,indent=2)
    if a.output:
        a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(text+'\n'); print('wrote',a.output)
    else: print(text)
if __name__=='__main__':main()
