#!/usr/bin/env python3
"""Recover exact D1 StringHash preimages from current package payload text.

D1 StringHash is source-documented as FNV1-32 (MontagueM/Charm TigerHash.cs).
This scanner extracts printable null-terminated / bounded ASCII-UTF8 runs from
resident structured payloads and supports two loss-preserving discovery modes:

1. --target HASH: emit only runs whose exact FNV1-32 equals a requested hash.
2. --contains TEXT: emit printable runs containing the requested substring and
   report the exact FNV1-32 of that complete serialized run.

The substring mode is useful when the semantic dev vocabulary is known but the
StringHash is not. It never assigns a nearby hash: the emitted StringHash is the
FNV1 of the exact serialized run itself. At least one --target or --contains is
required. Binary payloads remain remote.
"""
from __future__ import annotations
import argparse,collections,json,sys
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
 ap.add_argument('--target',action='append',default=[]);ap.add_argument('--contains',action='append',default=[])
 ap.add_argument('--member-catalog',type=Path,action='append',required=True)
 ap.add_argument('--base-url',required=True);ap.add_argument('--part-count',type=int,default=10);ap.add_argument('--runtime',type=Path,required=True)
 ap.add_argument('--min-len',type=int,default=2);ap.add_argument('--max-len',type=int,default=256);ap.add_argument('--max-entry-size',type=int,default=8_000_000)
 ap.add_argument('--case-sensitive',action='store_true',help='Apply --contains with exact case instead of ASCII case-insensitive matching.')
 ap.add_argument('-o','--output',type=Path,required=True);a=ap.parse_args()
 if not a.target and not a.contains:ap.error('at least one --target or --contains is required')
 targets={int(norm(x),16):norm(x) for x in a.target};contains=list(dict.fromkeys(a.contains));cats=load_catalogs(a.member_catalog)
 needles=[x.encode('utf-8') for x in contains]
 if not a.case_sensitive:needles=[x.lower() for x in needles]
 arc=SplitHttpTar([f"{a.base_url.rstrip('/')}/packages.tar.{i:03d}" for i in range(1,a.part_count+1)],retries=6,timeout=90)
 r=LazyExactHashResolver(arc,cats,a.runtime);hits=[];errors=[];scanned_entries=0;scanned_runs=0
 seen=set()
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
    scanned_runs+=1;h=fnv1(bs);matched_targets=[];matched_contains=[]
    if h in targets:matched_targets.append(targets[h])
    cmp=bs if a.case_sensitive else bs.lower()
    for raw,needle in zip(contains,needles):
     if needle in cmp:matched_contains.append(raw)
    if not matched_targets and not matched_contains:continue
    try:s=bs.decode('utf-8')
    except UnicodeDecodeError:continue
    key=(pkg,int(e['index']),off,bs)
    if key in seen:continue
    seen.add(key)
    row={'string_hash':f'{h:08X}','preimage':s,'preimage_hex':bs.hex(),'matched_targets':matched_targets,'matched_contains':matched_contains,
         'package_id':f'{pkg:04X}','source_tag_hash':e['tag_hash'].upper(),'source_reference':e['reference'].upper(),'entry_index':int(e['index']),'byte_offset':off}
    hits.append(row)
    print('STRING',f'{h:08X}',repr(s),'MATCH_TARGETS',matched_targets,'MATCH_CONTAINS',matched_contains,'PKG',f'{pkg:04X}','SOURCE',e['tag_hash'].upper(),'CLASS',e['reference'].upper(),'OFFSET',hex(off),flush=True)
 target_counts=collections.Counter(x for r0 in hits for x in r0['matched_targets'])
 contains_counts=collections.Counter(x for r0 in hits for x in r0['matched_contains'])
 out={'schema':'d1_remote_stringhash_preimage_scan/v2','status':'D1_STRINGHASH_PREIMAGE_SCAN_COMPLETE' if not errors else 'D1_STRINGHASH_PREIMAGE_SCAN_PARTIAL',
      'targets':[f'{x:08X}' for x in targets],'contains':contains,'case_sensitive':a.case_sensitive,
      'package_ids':[f'{x:04X}' for x in dict.fromkeys(a.package_id)],'scanned_structured_entries':scanned_entries,'scanned_printable_runs':scanned_runs,
      'hit_counts':dict(target_counts),'contains_hit_counts':dict(contains_counts),'hits':hits,'errors':errors,
      'hash_algorithm':'FNV1-32, offset_basis=0x811C9DC5, prime=0x01000193, multiply-then-XOR per byte',
      'source':'MontagueM/Charm Tiger/TigerHash.cs pinned source documents StringHash as FNV1-32',
      'policy':'Target mode requires exact FNV1 equality. Contains mode discovers exact serialized printable runs and reports each complete run\'s exact FNV1; it does not assign a nearby or partial-string hash. Absence is a bounded negative result.'}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n')
 print('STATUS',out['status'],'ENTRIES',scanned_entries,'RUNS',scanned_runs,'TARGET_HITS',dict(target_counts),'CONTAINS_HITS',dict(contains_counts),'ERRORS',len(errors));return 0 if not errors else 2
if __name__=='__main__':raise SystemExit(main())
