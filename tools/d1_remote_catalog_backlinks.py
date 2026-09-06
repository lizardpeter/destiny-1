#!/usr/bin/env python3
"""Scan verified D1 logical package catalogs for exact aligned target-hash backlinks.

This is the multi-family counterpart to d1_remote_target_backlinks.py.  It is
intended for ownership/composition tracing after a concrete FileHash or TagHash
has already been proved.  Every hit is a literal aligned u32 occurrence in a
resident structured payload.  A hit alone does not assign field semantics; the
source entry class and byte offsets are emitted so a schema-specific parser can
close the edge next.
"""
from __future__ import annotations
import argparse, collections, json, struct, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_investment_parent_probe import RemoteLogicalPackage
from d1_split_tar_extract import SplitHttpTar


def norm(s:str)->str: return s.upper().removeprefix('0X').zfill(8)

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--scan-package-id',action='append',type=lambda x:int(x,0),required=True)
    ap.add_argument('--member-catalog',type=Path,action='append',required=True)
    ap.add_argument('--target',action='append',required=True)
    ap.add_argument('--reference',action='append',default=[])
    ap.add_argument('--max-entry-size',type=int,default=2_000_000)
    ap.add_argument('--base-url',required=True);ap.add_argument('--part-count',type=int,default=10)
    ap.add_argument('--runtime',type=Path,required=True);ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args()
    catalogs=load_catalogs(a.member_catalog); scan=list(dict.fromkeys(a.scan_package_id))
    missing=[x for x in scan if x not in catalogs]
    if missing: raise SystemExit('missing verified catalogs: '+','.join(f'{x:04X}' for x in missing))
    targets={int(norm(x),16):norm(x) for x in a.target}; refs={norm(x) for x in a.reference}
    arc=SplitHttpTar([f"{a.base_url.rstrip('/')}/packages.tar.{i:03d}" for i in range(1,a.part_count+1)],retries=6,timeout=90)
    hits=[];errors=[];package_reports=[];by_target=collections.Counter();by_ref=collections.Counter()
    for pkg in scan:
        r=RemoteLogicalPackage(arc,catalogs[pkg],a.runtime); scanned=sk_size=sk_ref=0;phits=0
        for e in r.entries:
            if e['type']!=16 or e['subtype']!=0: continue
            if int(e['file_size'])>a.max_entry_size: sk_size+=1;continue
            ref=e['reference'].upper()
            if refs and ref not in refs: sk_ref+=1;continue
            try:b=r.entry(e['index'])
            except Exception as ex:
                errors.append({'package_id':f'{pkg:04X}','source_tag_hash':e['tag_hash'].upper(),'entry_index':e['index'],'reference':ref,'error':repr(ex)});continue
            scanned+=1;found=collections.defaultdict(list);end=len(b)-(len(b)%4)
            for off in range(0,end,4):
                v=struct.unpack_from('<I',b,off)[0]
                if v in targets:found[targets[v]].append(off)
            if found:
                row={'package_id':f'{pkg:04X}','source_tag_hash':e['tag_hash'].upper(),'entry_index':e['index'],'reference':ref,'size':int(e['file_size']),'targets':{h:o for h,o in sorted(found.items())}}
                hits.append(row);phits+=1;by_ref[ref]+=1
                for h,o in found.items():by_target[h]+=len(o)
                print('BACKLINK',json.dumps(row,separators=(',',':')),flush=True)
        package_reports.append({'package_id':f'{pkg:04X}','logical_view':r.view.name,'scanned_structured_entries':scanned,'skipped_size':sk_size,'skipped_reference_filter':sk_ref,'hit_source_count':phits})
    rep={'schema':'d1_remote_catalog_backlinks/v1','scan_package_ids':[f'{x:04X}' for x in scan],'targets':list(targets.values()),'reference_filter':sorted(refs),'max_entry_size':a.max_entry_size,
         'package_reports':package_reports,'hit_source_count':len(hits),'occurrences_by_target':dict(by_target),'hit_sources_by_reference':dict(by_ref),'hits':hits,'error_count':len(errors),'errors':errors,
         'policy':'Every hit is an exact aligned serialized u32 occurrence. It proves literal serialization only; field meaning and ownership/composition semantics require schema-specific closure. A miss does not exclude indexed or indirect relations.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(rep,indent=2)+'\n')
    print('TARGETS',rep['targets'],'HIT_SOURCES',len(hits),'BY_TARGET',dict(by_target),'BY_REFERENCE',dict(by_ref),'ERRORS',len(errors))
    return 0
if __name__=='__main__':raise SystemExit(main())
