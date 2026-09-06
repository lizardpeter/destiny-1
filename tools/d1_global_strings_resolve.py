#!/usr/bin/env python3
"""Resolve D1 entity StringHashes through the retail GlobalStrings banks.

Pinned Charm path (50d36ee1f9ecadad7522504c20b1f3f9c97e30af):

GlobalStrings.Initialise() for DESTINY1_RISE_OF_IRON
  enumerates S50058080 / raw 50058080 / canonical 80800550
    +0x68 LocalizedStrings ActivityGlobalStrings
    +0xE8 LocalizedStrings CharacterNames

LocalizedStrings / raw 5A038080 / canonical 8080035A
  +0x08 SortedDynamicArray<SStringHash>, stride 0x04
  +0x18 LocalizedStringsData EnglishStringsData

LocalizedStringsData / raw BE088080 / canonical 808008BE
  +0x08 DynamicArray<SStringPart>, stride 0x20
  +0x38 DynamicArray<SStringCharacter>, stride 0x01
  +0x48 DynamicArray<SStringPartDefinition>, stride 0x10

SStringPart
  +0x08 RelativePointer -> UTF-8/string-part bytes
  +0x14 ushort ByteLength
  +0x16 ushort StringLength
  +0x18 ushort CipherShift

SStringPartDefinition
  +0x00 RelativePointer -> first SStringPart record
  +0x08 int64 PartCount

This tool intentionally resolves only requested StringHashes by default. It keeps
all hash-collision candidates with their exact source bank instead of flattening
multiple retail strings to one guessed identity.
"""
from __future__ import annotations

import argparse
import json
import struct
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import d1_tower_map_schema_validate_v5 as v5

GLOBAL_CONTAINER = '80800550'
LOCALIZED_STRINGS = '8080035A'
LOCALIZED_DATA = '808008BE'
NULLS = {'00000000', 'FFFFFFFF'}
PINNED_SOURCE = (
    'MontagueM/Charm@50d36ee1f9ecadad7522504c20b1f3f9c97e30af '
    'Tiger/GlobalStrings.cs + Tiger/Schema/Strings/LocalizedStrings.cs + '
    'Tiger/Schema/Strings/LocalizedStringsStructs.cs + Tiger/SchemaTypes.cs'
)


def norm(x): return str(x).upper().removeprefix('0X').zfill(8)
def hx(v): return f'{v:08X}'
def u16(b,o): return struct.unpack_from('<H',b,o)[0]
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def i32(b,o): return struct.unpack_from('<i',b,o)[0]
def i64(b,o): return struct.unpack_from('<q',b,o)[0]


def dyn(b: bytes, off: int, stride: int) -> dict:
    if off + 0x10 > len(b):
        return {'ok':False,'field_offset':off,'error':'descriptor_oob'}
    count=i32(b,off); unk=u32(b,off+4); rel=i64(b,off+8)
    absolute=off+8+rel+0x10
    end=absolute+max(count,0)*stride
    pointer_bounds_ok=absolute>=0 and end<=len(b)
    ok=count>=0 and (count==0 or pointer_bounds_ok)
    return {'ok':ok,'field_offset':off,'count':count,'unknown04':unk,'relative':rel,
            'absolute':absolute,'end':end,'stride':stride,'payload_size':len(b),
            'serialized_pointer_bounds_ok':pointer_bounds_ok,
            'zero_count_no_dereference':count==0}


def relptr(b: bytes, off: int) -> dict:
    if off+8>len(b): return {'ok':False,'field_offset':off,'error':'pointer_oob'}
    rel=i64(b,off); absolute=off+rel
    return {'ok':absolute>=0 and absolute<=len(b),'field_offset':off,'relative':rel,'absolute':absolute}


def class_meta(c,h,expected=None):
    h=norm(h);m=c.entry_meta(h)
    return {'hash':h,'meta':m,'exists':m is not None,'expected_class':expected,
            'class_matches':bool(m and (expected is None or norm(m.get('reference',''))==expected)),
            'is_null_sentinel':h in NULLS}


def decode_part_bytes(raw: bytes, cipher_shift: int) -> str:
    # Reproduce the D1-era Charm decode behavior. The common case is shift 0.
    if cipher_shift == 0:
        return raw.decode('utf-8','replace')
    out=[];i=0
    while i<len(raw):
        v=raw[i]
        if 0xC0<=v<=0xDF and i+2<=len(raw):
            chunk=raw[i:i+2]
            out.append(chunk.decode('utf-8','replace'))
            i+=2
        elif 0xE0<=v<=0xEF and i+3<=len(raw):
            chunk=raw[i:i+3]
            s=chunk.decode('utf-8','replace')
            if len(s)==1 and s!='\ufffd':
                out.append(chr((ord(s)+cipher_shift)&0x10FFFF))
            else:
                out.append(s)
            i+=3
        else:
            out.append(bytes([((v+cipher_shift)&0xFF)]).decode('utf-8','replace'))
            i+=1
    return ''.join(out)


def parse_string_part(data: bytes, parts: dict, index: int) -> dict:
    off=parts['absolute']+index*0x20
    if off<0 or off+0x20>len(data):
        return {'index':index,'ok':False,'error':'part_record_oob'}
    p=relptr(data,off+0x08);bl=u16(data,off+0x14);sl=u16(data,off+0x16);shift=u16(data,off+0x18)
    row={'index':index,'record_offset':off,'data_pointer':p,'byte_length':bl,'string_length':sl,'cipher_shift':shift}
    absolute=p.get('absolute')
    if not p.get('ok') or absolute is None or absolute+bl>len(data):
        row['ok']=False;row['error']='part_bytes_oob';return row
    raw=data[absolute:absolute+bl]
    row['raw_hex']=raw.hex();row['decoded']=decode_part_bytes(raw,shift);row['ok']=True
    return row


def parse_localized_data(c,h,hashes,target_set):
    h=norm(h);m=class_meta(c,h,LOCALIZED_DATA);b,src=c.payload(h)
    out={'hash':h,'target':m,'payload_source':src,'hits':[],'violations':[]}
    if not m['class_matches'] or b is None:
        out['violations'].append('localized_data_missing_class_or_payload');return out
    if len(b)<0x58:
        out['violations'].append('localized_data_shorter_than_0x58');return out
    parts=dyn(b,0x08,0x20);chars=dyn(b,0x38,0x01);combos=dyn(b,0x48,0x10)
    out['string_parts_array']=parts;out['string_characters_array']=chars;out['string_combinations_array']=combos
    if not parts['ok']:out['violations'].append('string_parts_bounds')
    if not chars['ok']:out['violations'].append('string_characters_bounds')
    if not combos['ok']:out['violations'].append('string_combinations_bounds')
    if out['violations']:return out
    out['hash_count']=len(hashes);out['combination_count']=combos['count'];out['counts_match']=len(hashes)==combos['count']
    if not out['counts_match']:
        out['violations'].append('hash_combination_count_mismatch')
    n=min(len(hashes),combos['count'])
    for index in range(n):
        sh=hashes[index]
        if target_set and sh not in target_set:continue
        co=combos['absolute']+index*0x10
        start=relptr(b,co);part_count=i64(b,co+8)
        hit={'index':index,'string_hash':sh,'combination_offset':co,'start_part_pointer':start,'part_count':part_count,'parts':[],'ok':True}
        if part_count<0 or not start.get('ok'):
            hit['ok']=False;hit['error']='combination_pointer_or_count_invalid';out['hits'].append(hit);continue
        delta=start['absolute']-parts['absolute']
        if delta<0 or delta%0x20:
            hit['ok']=False;hit['error']='combination_start_not_in_parts_array';out['hits'].append(hit);continue
        start_index=delta//0x20;hit['start_part_index']=start_index
        if start_index+part_count>parts['count']:
            hit['ok']=False;hit['error']='combination_part_range_oob';out['hits'].append(hit);continue
        pieces=[]
        for j in range(part_count):
            pr=parse_string_part(b,parts,start_index+j);hit['parts'].append(pr)
            if not pr.get('ok'):hit['ok']=False
            else:pieces.append(pr['decoded'])
        if hit['ok']:hit['string']=''.join(pieces)
        out['hits'].append(hit)
    return out


def parse_localized(c,h,kind,target_set):
    h=norm(h);m=class_meta(c,h,LOCALIZED_STRINGS);b,src=c.payload(h)
    out={'kind':kind,'hash':h,'target':m,'payload_source':src,'violations':[],'hits':[]}
    if h in NULLS:
        out['violations'].append('null_localized_strings');return out
    if not m['class_matches'] or b is None:
        out['violations'].append('localized_strings_missing_class_or_payload');return out
    if len(b)<0x48:
        out['violations'].append('localized_strings_shorter_than_0x48');return out
    arr=dyn(b,0x08,4);out['string_hash_array']=arr
    if not arr['ok']:
        out['violations'].append('string_hash_array_bounds');return out
    hashes=[hx(u32(b,arr['absolute']+i*4)) for i in range(arr['count'])]
    out['string_hash_count']=len(hashes)
    english=hx(u32(b,0x18));out['english_strings_data']=class_meta(c,english,LOCALIZED_DATA)
    # Preserve all adjacent language slots as evidence without treating them as English.
    slots=[]
    for off in range(0x18,0x48,4):
        x=hx(u32(b,off));slots.append({'field_offset':off,**class_meta(c,x,LOCALIZED_DATA)})
    out['localized_data_slots']=slots
    if not out['english_strings_data']['class_matches']:
        out['violations'].append('english_strings_data_class_mismatch');return out
    data=parse_localized_data(c,english,hashes,target_set);out['localized_data']=data;out['hits']=data.get('hits',[])
    out['violations'].extend(data.get('violations',[]));return out


def parse_global_container(c,h,target_set):
    h=norm(h);m=class_meta(c,h,GLOBAL_CONTAINER);b,src=c.payload(h)
    out={'hash':h,'target':m,'payload_source':src,'banks':[],'violations':[]}
    if not m['class_matches'] or b is None:
        out['violations'].append('global_container_missing_class_or_payload');return out
    if len(b)<0xEC:
        out['violations'].append('global_container_shorter_than_0xEC');return out
    banks=[('activity_global_strings',hx(u32(b,0x68)),0x68),('character_names',hx(u32(b,0xE8)),0xE8)]
    for kind,bh,off in banks:
        row=parse_localized(c,bh,kind,target_set);row['container_field_offset']=off;out['banks'].append(row)
        out['violations'].extend(f'{kind}:{x}' for x in row.get('violations',[]))
    return out


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--snapshot',type=Path,action='append',required=True)
    ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('--entity-dependency-census',type=Path)
    ap.add_argument('--string-hash',action='append',default=[])
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    targets={norm(x) for x in a.string_hash}
    if a.entity_dependency_census:
        dep=json.loads(a.entity_dependency_census.read_text())
        targets.update(norm(x) for x in dep.get('entity_name_hash_reference_counts',{}))
    c=v5.v3.base.Corpus([p.resolve() for p in a.snapshot],a.runtime.resolve())
    roots=sorted({e['tag_hash'].upper() for _,_,_,e in c.occurrences_by_ref(GLOBAL_CONTAINER)})
    containers=[parse_global_container(c,h,targets) for h in roots]
    hitmap=defaultdict(list);viol=[];bank_counts=Counter()
    for gc in containers:
        viol.extend(f"{gc['hash']}:{x}" for x in gc.get('violations',[]))
        for bank in gc.get('banks',[]):
            bank_counts[bank['kind']]+=1
            for hit in bank.get('hits',[]):
                if hit.get('ok') and hit.get('string') is not None:
                    hitmap[hit['string_hash']].append({
                        'string':hit['string'],'container':gc['hash'],'bank_kind':bank['kind'],
                        'localized_strings':bank['hash'],'localized_data':bank.get('english_strings_data',{}).get('hash'),
                        'string_index':hit['index']})
    unresolved=sorted(h for h in targets if not hitmap.get(h))
    out={'schema_version':1,
         'status':'D1_GLOBAL_STRINGS_TARGETS_RESOLVED' if not unresolved and not viol else 'D1_GLOBAL_STRINGS_TARGETS_PARTIAL',
         'pinned_source':PINNED_SOURCE,'target_count':len(targets),'targets':sorted(targets),
         'global_container_count':len(containers),'bank_counts':dict(bank_counts),
         'resolved_target_count':sum(1 for h in targets if hitmap.get(h)),'unresolved_target_count':len(unresolved),
         'unresolved_targets':unresolved,'resolved_targets':{h:hitmap[h] for h in sorted(hitmap) if not targets or h in targets},
         'containers':containers,'violations':viol,
         'policy':'Only D1 GlobalStrings banks source-owned by S50058080 are used. Hash collisions remain multiple candidates with source-bank provenance.'}
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ('status','target_count','global_container_count','bank_counts','resolved_target_count','unresolved_target_count','unresolved_targets','violations')},indent=2))
    return 0 if out['status']=='D1_GLOBAL_STRINGS_TARGETS_RESOLVED' else 2

if __name__=='__main__':raise SystemExit(main())
