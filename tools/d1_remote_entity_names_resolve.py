#!/usr/bin/env python3
"""Resolve D1 s_entity candidate name resources through exact retail GlobalStrings.

Consumes one or more reports from d1_crota_raid_candidate_probe.py (the format is
intentionally generic enough for future NPC/enemy candidate reports). Specific-name
StringHashes come directly from the validated EntityResource parser. Generic-name
resources first point to class 808013F3 tags; their underlying StringHash is at
+0x0C per the source-mapped D1 Entity.Load path.

GlobalStrings are located only by exact class 80800550 in caller-selected verified
package families. ActivityGlobalStrings (+0x68) and CharacterNames (+0xE8) are
then parsed using the source-crosschecked D1 LocalizedStrings layouts. Collisions
are preserved. No package/name/appearance heuristic participates.
"""
from __future__ import annotations

import argparse
import collections
import json
import struct
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))

from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_investment_parent_probe import RemoteLogicalPackage
from d1_split_tar_extract import SplitHttpTar
from d1_investment_arrangement_probe import filehash_pkg_index

GLOBAL_CONTAINER='80800550'
LOCALIZED_STRINGS='8080035A'
LOCALIZED_DATA='808008BE'
GENERIC_NAME_TAG_CLASS='808013F3'
NULLS={'00000000','FFFFFFFF'}


def norm(x): return str(x).upper().removeprefix('0X').zfill(8)
def hx(v): return f'{v:08X}'
def u16(b,o): return struct.unpack_from('<H',b,o)[0]
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def i32(b,o): return struct.unpack_from('<i',b,o)[0]
def i64(b,o): return struct.unpack_from('<q',b,o)[0]

def package_of(h): return filehash_pkg_index(int(norm(h),16))[0]


def dyn(b,off,stride):
    if off+0x10>len(b): return {'ok':False,'error':'descriptor_oob'}
    count=i32(b,off);rel=i64(b,off+8);absolute=off+8+rel+0x10;end=absolute+max(count,0)*stride
    return {'ok':count>=0 and (count==0 or (absolute>=0 and end<=len(b))),
            'count':count,'absolute':absolute,'end':end,'stride':stride,'relative':rel}

def relptr(b,off):
    if off+8>len(b): return {'ok':False,'error':'pointer_oob'}
    rel=i64(b,off);absolute=off+rel
    return {'ok':0<=absolute<=len(b),'relative':rel,'absolute':absolute}


class Resolver:
    def __init__(self,arc,catalogs,runtime):
        self.arc=arc;self.catalogs=catalogs;self.runtime=runtime;self.views={};self.maps={}
    def view(self,pkg):
        if pkg not in self.catalogs: raise KeyError(f'package {pkg:04X} absent from verified catalog')
        if pkg not in self.views:self.views[pkg]=RemoteLogicalPackage(self.arc,self.catalogs[pkg],self.runtime)
        return self.views[pkg]
    def map(self,pkg):
        if pkg not in self.maps:self.maps[pkg]={e['tag_hash'].upper():e for e in self.view(pkg).entries}
        return self.maps[pkg]
    def locate(self,h):
        h=norm(h);pkg=package_of(h);e=self.map(pkg).get(h)
        if e is None:raise KeyError(f'{h} absent from exact package {pkg:04X}')
        return self.view(pkg),e
    def bytes(self,h):
        v,e=self.locate(h);return v,e,v.entry(e['index'])


def decode_part_bytes(raw,cipher_shift):
    if cipher_shift==0:return raw.decode('utf-8','replace')
    out=[];i=0
    while i<len(raw):
        v=raw[i]
        if 0xC0<=v<=0xDF and i+2<=len(raw):
            out.append(raw[i:i+2].decode('utf-8','replace'));i+=2
        elif 0xE0<=v<=0xEF and i+3<=len(raw):
            chunk=raw[i:i+3];s=chunk.decode('utf-8','replace')
            out.append(chr((ord(s)+cipher_shift)&0x10FFFF) if len(s)==1 and s!='\ufffd' else s);i+=3
        else:
            out.append(bytes([((v+cipher_shift)&0xFF)]).decode('utf-8','replace'));i+=1
    return ''.join(out)


def parse_part(data,parts,index):
    off=parts['absolute']+index*0x20
    if off<0 or off+0x20>len(data):return {'ok':False,'error':'part_record_oob'}
    p=relptr(data,off+8);bl=u16(data,off+0x14);sl=u16(data,off+0x16);shift=u16(data,off+0x18)
    if not p.get('ok') or p['absolute']+bl>len(data):return {'ok':False,'error':'part_bytes_oob'}
    raw=data[p['absolute']:p['absolute']+bl]
    return {'ok':True,'decoded':decode_part_bytes(raw,shift),'byte_length':bl,'string_length':sl,'cipher_shift':shift}


def resolve_localized_data(res,data_hash,hashes,targets,bank,container):
    v,e,b=res.bytes(data_hash)
    if e['reference'].upper()!=LOCALIZED_DATA:raise ValueError(f'{data_hash}: expected {LOCALIZED_DATA}, got {e["reference"]}')
    parts=dyn(b,0x08,0x20);combos=dyn(b,0x48,0x10)
    if not parts['ok'] or not combos['ok']:raise ValueError(f'{data_hash}: localized data arrays invalid')
    n=min(len(hashes),combos['count']);hits=[]
    for i in range(n):
        sh=hashes[i]
        if sh not in targets:continue
        co=combos['absolute']+i*0x10;start=relptr(b,co);count=i64(b,co+8)
        row={'string_hash':sh,'bank_kind':bank,'container':container,'localized_data':norm(data_hash),'index':i,'part_count':count}
        if count<0 or not start.get('ok'):
            row['ok']=False;row['error']='combination_pointer_or_count_invalid';hits.append(row);continue
        delta=start['absolute']-parts['absolute']
        if delta<0 or delta%0x20 or delta//0x20+count>parts['count']:
            row['ok']=False;row['error']='combination_part_range_invalid';hits.append(row);continue
        pieces=[];ok=True
        for j in range(count):
            pr=parse_part(b,parts,delta//0x20+j)
            if not pr.get('ok'):ok=False;break
            pieces.append(pr['decoded'])
        row['ok']=ok
        if ok:row['string']=''.join(pieces)
        else:row['error']='string_part_decode_failed'
        hits.append(row)
    return hits


def resolve_localized(res,h,targets,bank,container):
    v,e,b=res.bytes(h)
    if e['reference'].upper()!=LOCALIZED_STRINGS:raise ValueError(f'{h}: expected {LOCALIZED_STRINGS}, got {e["reference"]}')
    arr=dyn(b,0x08,4)
    if not arr['ok']:raise ValueError(f'{h}: hash array invalid')
    hashes=[hx(u32(b,arr['absolute']+i*4)) for i in range(arr['count'])]
    data=hx(u32(b,0x18))
    return resolve_localized_data(res,data,hashes,targets,bank,container)


def collect_candidate_names(paths):
    entities={};specific=set();generic_tags=set()
    for path in paths:
        d=json.loads(path.read_text())
        for x in d.get('articulated_candidates',[]):
            eh=x['entity_hash'];rec=entities.setdefault(eh,{'entity_hash':eh,'package_id':x.get('package_id'),'models':x.get('embedded_models',[]),'skeletons':x.get('skeletons',[]),'specific_hashes':[],'generic_name_tags':[]})
            for r in x.get('resources',[]):
                er=r.get('entity_resource') or {};role=er.get('semantic_role')
                if role=='entity_name_specific' and er.get('entity_name_string_hash'):
                    h=norm(er['entity_name_string_hash']);specific.add(h);rec['specific_hashes'].append(h)
                elif role=='entity_name_generic' and er.get('entity_name_tag_hash'):
                    h=norm(er['entity_name_tag_hash']);generic_tags.add(h);rec['generic_name_tags'].append(h)
    return entities,specific,generic_tags


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--candidate-report',type=Path,action='append',required=True)
    ap.add_argument('--global-package-id',type=lambda x:int(x,0),action='append',required=True)
    ap.add_argument('--member-catalog',type=Path,action='append',required=True)
    ap.add_argument('--base-url',required=True);ap.add_argument('--part-count',type=int,default=10)
    ap.add_argument('--runtime',type=Path,required=True);ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args()
    entities,specific,generic_tags=collect_candidate_names(a.candidate_report)
    catalogs=load_catalogs(a.member_catalog);arc=SplitHttpTar([f"{a.base_url.rstrip('/')}/packages.tar.{i:03d}" for i in range(1,a.part_count+1)],retries=6,timeout=90)
    res=Resolver(arc,catalogs,a.runtime)

    generic_map={};generic_errors=[]
    for tag in sorted(generic_tags):
        try:
            v,e,b=res.bytes(tag)
            if e['reference'].upper()!=GENERIC_NAME_TAG_CLASS:raise ValueError(f'class {e["reference"]} != {GENERIC_NAME_TAG_CLASS}')
            if len(b)<0x10:raise ValueError('generic name tag shorter than 0x10')
            generic_map[tag]=hx(u32(b,0x0C))
        except Exception as ex:generic_errors.append({'tag_hash':tag,'error':repr(ex)})
    targets=set(specific)|set(generic_map.values());targets.discard('811C9DC5')

    containers=[];hits=[];scan_errors=[]
    for pkg in list(dict.fromkeys(a.global_package_id)):
        try:v=res.view(pkg)
        except Exception as ex:scan_errors.append({'package_id':f'{pkg:04X}','error':repr(ex)});continue
        for e in v.entries:
            if e['reference'].upper()!=GLOBAL_CONTAINER:continue
            ch=e['tag_hash'].upper()
            try:
                b=v.entry(e['index'])
                if len(b)<0xEC:raise ValueError('global container shorter than 0xEC')
                activity=hx(u32(b,0x68));characters=hx(u32(b,0xE8))
                row={'package_id':f'{pkg:04X}','container':ch,'activity_global_strings':activity,'character_names':characters}
                containers.append(row)
                for kind,h in [('activity_global_strings',activity),('character_names',characters)]:
                    if h in NULLS:continue
                    try:hrows=resolve_localized(res,h,targets,kind,ch);hits.extend(hrows)
                    except Exception as ex:row.setdefault('bank_errors',[]).append({'kind':kind,'hash':h,'error':repr(ex)})
            except Exception as ex:scan_errors.append({'package_id':f'{pkg:04X}','container':ch,'error':repr(ex)})

    by_hash=collections.defaultdict(list)
    for h in hits:
        if h.get('ok') and h.get('string') is not None:by_hash[h['string_hash']].append(h)
    out_entities=[]
    for eh,rec in sorted(entities.items()):
        names=[]
        for h in rec['specific_hashes']:
            names.append({'kind':'specific','string_hash':h,'resolved':by_hash.get(h,[])})
        for tag in rec['generic_name_tags']:
            sh=generic_map.get(tag)
            names.append({'kind':'generic','name_tag_hash':tag,'string_hash':sh,'resolved':by_hash.get(sh,[]) if sh else []})
        out_entities.append({**rec,'names':names})
    unresolved=sorted(h for h in targets if not by_hash.get(h))
    out={'schema':'d1_remote_entity_names_resolve/v1','candidate_report_count':len(a.candidate_report),'entity_count':len(out_entities),
         'specific_string_hashes':sorted(specific),'generic_name_tag_count':len(generic_tags),'generic_name_tag_to_string_hash':generic_map,
         'target_string_hashes':sorted(targets),'global_package_ids':[f'{x:04X}' for x in list(dict.fromkeys(a.global_package_id))],
         'global_container_count':len(containers),'global_containers':containers,'resolved_hit_count':len(hits),'unresolved_target_hashes':unresolved,
         'generic_tag_errors':generic_errors,'scan_errors':scan_errors,'entities':out_entities,
         'policy':'Specific/generic name edges are source-mapped D1 Entity.Load fields. Global string values come only from exact 80800550/8080035A/808008BE retail structures. Hash collisions are preserved.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n')
    print('ENTITIES',len(out_entities),'GENERIC_TAGS',len(generic_tags),'TARGETS',sorted(targets),'CONTAINERS',len(containers),'UNRESOLVED',unresolved)
    for x in out_entities:
        vals=[]
        for n in x['names']:
            vals.extend(y['string'] for y in n.get('resolved',[]) if y.get('string') is not None)
        if vals:print('ENTITY_NAME',x['entity_hash'],x['models'],[(s.get('resource_hash'),s.get('node_count')) for s in x['skeletons']],vals)
    return 0

if __name__=='__main__':raise SystemExit(main())
