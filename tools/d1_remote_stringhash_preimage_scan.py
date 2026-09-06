#!/usr/bin/env python3
"""Recover exact D1 StringHash preimages from current package payload text.

D1 StringHash is source-documented as FNV1-32 (MontagueM/Charm TigerHash.cs).
This scanner extracts printable null-terminated / bounded ASCII-UTF8 runs from
resident structured payloads and hashes the exact bytes. Only exact target hash
matches are emitted. It does not infer names from proximity.

This is intentionally a targeted forensic tool: callers provide package families
and one or more 32-bit StringHash targets. Binary payloads remain remote.
"""
from __future__ import annotations
import argparse,collections,json,string,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_crota_raid_candidate_probe import LazyExactHashResolver
from d1_split_tar_extract import SplitHttpTar

PRINTABLE=set(range(0x20,0x7F))

def norm(x):
 x=str(x).upper().removeprefix('0X').zfill(8);int(x,16);return x

def fnv1(bs:bytes)->int:
 h=0x811C9DC5
 for b in bs:
  h=((h*0x01000193)&0xFFFFFFFF)^b
 return h

def runs(b:bytes,min_len:int,max_len:int):
 start=None
 for i,x in enumerate(b+b'\x00'):
  if x in PRINTABLE:
   if start is None:start=i
  else:
   if start is not None:
    n=i-start
    if min_len<=n<=max_len:yield start,b[start:i]
    start=None

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--package-id',action='append',type=lambda x:int(x,0),required=True)
 ap.add_argument('--target',action='append',required=True);ap.add_argument('--member-catalog',type=Path,action='append',required=True)
 ap.add_argument('--base-url',required=True);ap.add_argument('--part-count',type=int,default=10);ap.add_argument('--runtime',type=Path,required=True)
 ap.add_argument('--min-len',type=int,default=2);ap.add_argument('--max-len',type=int,default=256);ap.add_argument('--max-entry-size',type=int,default=8_000_000)
 ap.add_argument('-o','--output',type=Path,required=True);a=ap.parse_args()
 targets={int(norm(x),16):norm(x) for x in a.target};cats=load_catalogs(a.member_catalog)
 arc=SplitHttpTar([f"{a.base_url.rstrip('/')}/packages.tar.{i:03d}" for i in range(1,a.part_count+1)],retries=6,timeout=90)
 r=LazyExactHashResolver(arc,cats,a.runtime);hits=[];errors=[];scanned_entries=0;scanned_runs=0
 for pkg in dict.fromkeys(a.package_id):
  try:view=r.view(pkg)
  except Exception as ex:errors.append({'package_id':f'{pkg:04X}','stage':'view','error':repr(ex)});continue
  for e in view.entries:
   if int(e.get('type',0))!=16 or int(e.get('subtype',0))!=0:continue
   if int(e.get('file_size',0))>a.max_entry_size:continue
   try:b=view.entry(e['index'])
   except Exception as ex:errors.append({'package_id':f'{pkg:04X}','entry':e['tag_hash'].upper(),'stage':'payload','error':repr(ex)});continue
   scanned_entries+=1
   for off,bs in runs(b,a.min_len,a.max_len):
    scanned_runs+=1;h=fnv1(bs)
    if h in targets:
     try:s=bs.decode('utf-8')
     except UnicodeDecodeError:continue
     hits.append({'target':targets[h],'preimage':s,'preimage_hex':bs.hex(),'package_id':f'{pkg:04X}','source_tag_hash':e['tag_hash'].upper(),'source_reference':e['reference'].upper(),'entry_index':int(e['index']),'byte_offset':off})
     print('PREIMAGE',targets[h],repr(s),'PKG',f'{pkg:04X}','SOURCE',e['tag_hash'].upper(),'CLASS',e['reference'].upper(),'OFFSET',hex(off),flush=True)
 counts=collections.Counter(x['target'] for x in hits)
 out={'schema':'d1_remote_stringhash_preimage_scan/v1','status':'D1_STRINGHASH_PREIMAGE_SCAN_COMPLETE' if not errors else 'D1_STRINGHASH_PREIMAGE_SCAN_PARTIAL','targets':[f'{x:08X}' for x in targets],'package_ids':[f'{x:04X}' for x in dict.fromkeys(a.package_id)],'scanned_structured_entries':scanned_entries,'scanned_printable_runs':scanned_runs,'hit_counts':dict(counts),'hits':hits,'errors':errors,
      'hash_algorithm':'FNV1-32, offset_basis=0x811C9DC5, prime=0x01000193, multiply-then-XOR per byte','source':'MontagueM/Charm Tiger/TigerHash.cs pinned source documents StringHash as FNV1-32','policy':'Only exact FNV1 equality of serialized printable byte runs is a preimage hit. Absence is a bounded negative result, not proof the preimage does not exist elsewhere.'}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n');print('STATUS',out['status'],'ENTRIES',scanned_entries,'RUNS',scanned_runs,'HITS',dict(counts),'ERRORS',len(errors));return 0 if not errors else 2
if __name__=='__main__':raise SystemExit(main())
