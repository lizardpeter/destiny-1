#!/usr/bin/env python3
"""Decode the D1 ROI 80802C0E animation-control action/state selector table.

This parser was originally calibrated on retail PS4 rocket-launcher control
80AA3CC9 and has since been generalized across the sibling CA0/CA1/CA2 controls.
It deliberately exposes the binary structure separately from semantic naming:

  +0x08 u32 animation-list count
  +0x10 relative pointer to a dynamic-array header
       header+0x00 repeats count
       header+0x08 element-class tag
       header+0x10 FileHash[count]

  +0x68 u32 selector-record count
  +0x70 relative pointer to a dynamic-array header
       header+0x00 repeats count
       header+0x08 element-class tag
       header+0x10 selector records, 0x20 bytes each

Selector record fields used here:
  +0x10 u32 state/action StringHash (FNV1 lowercase in known D1 data)
  +0x14 f32 transition/duration-like scalar (semantic name intentionally unset)
  +0x18 u32 packed selection: high16=count, low16=start index

Ordinary selections require start+count to stay inside the animation list. Retail
CA0 also proves one explicit empty selector encoding: packed 0x0000FFFF means
count=0/start=0xFFFF and selects no clips. It is preserved as an
``empty_sentinel`` rather than rejected as an out-of-range array slice.
"""
from __future__ import annotations
import argparse,json,struct,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from d1_entry_extract import EntryReader
from d1_fnv1_action_probe import DEFAULTS,fnv1

CONTROL_REF='80802C0E'
CLIP_REF='808005A1'
EMPTY_SELECTION_SENTINEL=0x0000FFFF

def _u32(b,o): return struct.unpack_from('<I',b,o)[0]
def _f32(b,o): return struct.unpack_from('<f',b,o)[0]

def _rel_array(b,count_off,ptr_off):
    count=_u32(b,count_off)
    rel=_u32(b,ptr_off)
    hdr=ptr_off+rel
    if hdr<0 or hdr+0x10>len(b): raise ValueError(f'array header out of range: 0x{hdr:X}')
    repeated=_u32(b,hdr)
    if repeated!=count: raise ValueError(f'count mismatch field={count} header={repeated} at 0x{hdr:X}')
    elem_class=_u32(b,hdr+8)
    return count,hdr,hdr+0x10,elem_class

def decode_control(payload:bytes,reader:EntryReader|None=None,names:list[str]|None=None):
    if len(payload)<0x80: raise ValueError('control payload too small')
    anim_count,anim_hdr,anim_data,anim_elem_class=_rel_array(payload,0x08,0x10)
    state_count,state_hdr,state_data,state_elem_class=_rel_array(payload,0x68,0x70)
    if anim_data+4*anim_count>len(payload): raise ValueError('animation list exceeds payload')
    if state_data+0x20*state_count>len(payload): raise ValueError('state table exceeds payload')
    hash_to_name={fnv1(s):s for s in (names or DEFAULTS)}
    by_hash={int(e['tag_hash'],16):e for e in reader.entries} if reader is not None else {}
    animations=[]
    for i in range(anim_count):
        h=_u32(payload,anim_data+i*4); tag=f'{h:08X}'
        row={'index':i,'tag_hash':tag}
        e=by_hash.get(h)
        if e is not None:
            row['entry']={'index':e['index'],'reference':e['reference'].upper(),'type':e['type'],'subtype':e['subtype'],'size':e['file_size']}
        animations.append(row)
    states=[]
    invalid=[]
    empty_sentinels=0
    for i in range(state_count):
        base=state_data+i*0x20
        h=_u32(payload,base+0x10); packed=_u32(payload,base+0x18)
        count=(packed>>16)&0xffff; start=packed&0xffff
        is_empty_sentinel=packed==EMPTY_SELECTION_SENTINEL
        range_valid=is_empty_sentinel or start+count<=len(animations)
        if is_empty_sentinel:
            selected=[]
            selection_kind='empty_sentinel'
            empty_sentinels+=1
        elif range_valid:
            selected=animations[start:start+count]
            selection_kind='range'
        else:
            selected=[]
            selection_kind='invalid_range'
            invalid.append({'record_index':i,'state_hash':f'{h:08X}','packed_selection':f'{packed:08X}','selection_start':start,'selection_count':count})
        states.append({
            'record_index':i,'record_offset':base,'state_hash':f'{h:08X}',
            'state_name':hash_to_name.get(h),'scalar_f32':_f32(payload,base+0x14),
            'packed_selection':f'{packed:08X}','selection_count':count,'selection_start':start,
            'selection_kind':selection_kind,'selection_range_valid':range_valid,
            'selected_animations':selected,
        })
    if invalid:
        raise ValueError(f'{len(invalid)} selector ranges exceed animation list: {invalid[:3]}')
    return {
        'animation_list':{'count':anim_count,'header_offset':anim_hdr,'data_offset':anim_data,'element_class':f'{anim_elem_class:08X}','items':animations},
        'state_table':{'count':state_count,'header_offset':state_hdr,'data_offset':state_data,'element_class':f'{state_elem_class:08X}','record_stride':0x20,'empty_sentinel_count':empty_sentinels,'records':states},
        'evidence_policy':'FileHash list, state hashes, packed count/start indices, selected ranges, and the retail-proven 0x0000FFFF empty sentinel are binary decoded. Names appear only when exact FNV1 preimages are known. scalar_f32 semantics are intentionally not named.',
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('pkg',type=Path)
    ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('--control-tag',required=True)
    ap.add_argument('--name',action='append',default=[])
    ap.add_argument('-o','--output',type=Path)
    a=ap.parse_args()
    r=EntryReader(a.pkg,a.runtime); tag=a.control_tag.upper(); h=int(tag,16)
    by_hash={int(e['tag_hash'],16):e for e in r.entries}
    e=by_hash.get(h)
    if e is None: raise SystemExit(f'{tag} is not present in package {r.h["pkg_id"]:04X}')
    idx=e['index']
    if e['tag_hash'].upper()!=tag: raise SystemExit(f'entry mismatch: expected {tag}, got {e["tag_hash"]}')
    if e['reference'].upper()!=CONTROL_REF: raise SystemExit(f'{tag} ref {e["reference"]}, expected {CONTROL_REF}')
    names=list(dict.fromkeys(DEFAULTS+a.name))
    out={'control':{'tag_hash':tag,'index':idx,'reference':e['reference'].upper(),'size':e['file_size']},
         **decode_control(r.entry(idx),r,names)}
    text=json.dumps(out,indent=2)
    if a.output:
        a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(text+'\n');print('wrote',a.output)
    else:print(text)
if __name__=='__main__': main()
