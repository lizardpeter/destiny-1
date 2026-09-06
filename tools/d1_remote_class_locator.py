#!/usr/bin/env python3
"""Locate exact D1 file-entry Reference classes across verified package families.

Reads only current logical package headers/entry tables through HTTP ranges. No asset
payload is decompressed. Useful for discovering infrastructure classes such as
GlobalStrings without relying on filenames.
"""
from __future__ import annotations
import argparse,collections,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_investment_parent_probe import RemoteLogicalPackage
from d1_split_tar_extract import SplitHttpTar

def norm(x):return str(x).upper().removeprefix('0X').zfill(8)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--member-catalog',type=Path,action='append',required=True)
 ap.add_argument('--reference',action='append',required=True);ap.add_argument('--base-url',required=True);ap.add_argument('--part-count',type=int,default=10)
 ap.add_argument('--runtime',type=Path,required=True);ap.add_argument('--package-id',action='append',type=lambda x:int(x,0),default=[]);ap.add_argument('-o','--output',type=Path,required=True);a=ap.parse_args()
 targets={norm(x) for x in a.reference};cats=load_catalogs(a.member_catalog);pkgs=list(dict.fromkeys(a.package_id)) if a.package_id else sorted(cats)
 arc=SplitHttpTar([f"{a.base_url.rstrip('/')}/packages.tar.{i:03d}" for i in range(1,a.part_count+1)],retries=6,timeout=90)
 hits=[];errors=[];counts=collections.Counter()
 for n,pkg in enumerate(pkgs,1):
  if pkg not in cats:errors.append({'package_id':f'{pkg:04X}','error':'absent_from_catalog'});continue
  try:
   v=RemoteLogicalPackage(arc,cats[pkg],a.runtime);local=collections.Counter(e['reference'].upper() for e in v.entries)
   for ref in targets:
    if local.get(ref):
     rows=[{'tag_hash':e['tag_hash'].upper(),'entry_index':int(e['index']),'type':int(e['type']),'subtype':int(e['subtype']),'file_size':int(e['file_size'])} for e in v.entries if e['reference'].upper()==ref]
     hits.append({'package_id':f'{pkg:04X}','logical_view':v.view.name,'reference':ref,'count':len(rows),'entries':rows});counts[ref]+=len(rows)
  except Exception as ex:errors.append({'package_id':f'{pkg:04X}','error':repr(ex)})
  if n%50==0:print('SCANNED',n,'/',len(pkgs),'HIT_PACKAGES',len(hits),'ERRORS',len(errors),flush=True)
 out={'schema':'d1_remote_class_locator/v1','scanned_package_count':len(pkgs),'target_references':sorted(targets),'hit_package_count':len(hits),'occurrence_counts':dict(counts),'hits':hits,'errors':errors,'policy':'Reference identity is read only from current logical Tiger entry tables; no filename or payload inference.'}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k not in ('hits','errors')},indent=2));
 for h in hits:print('HIT',h['package_id'],h['logical_view'],h['reference'],[x['tag_hash'] for x in h['entries']])
 return 0
if __name__=='__main__':raise SystemExit(main())
