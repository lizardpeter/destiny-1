#!/usr/bin/env python3
"""Sparse aligned-dword backlink scan across a D1 logical package family.

Used to test explicit cross-package ownership/binding hypotheses without downloading
whole package members. By default it scans resident structured (type 16/subtype 0)
entries up to a caller-selected size ceiling and reports exact 4-byte-aligned target
hash occurrences. A hit proves serialization of the supplied FileHash/TagHash value;
a miss does not prove absence of an indirect/indexed relationship.
"""
from __future__ import annotations
import argparse,collections,json,struct,sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from d1_remote_investment_parent_probe import RemoteLogicalPackage,parse_member
from d1_split_tar_extract import SplitHttpTar


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--package-id',type=lambda x:int(x,0),required=True)
    ap.add_argument('--base-url',required=True)
    ap.add_argument('--part-count',type=int,default=10)
    ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('--member',action='append',type=parse_member,required=True)
    ap.add_argument('--target',action='append',required=True)
    ap.add_argument('--max-entry-size',type=int,default=2_000_000)
    ap.add_argument('--reference',action='append',default=[],help='optional class/reference filter')
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args()
    if any(m.pkg_id!=a.package_id for m in a.member): raise SystemExit('member package mismatch')
    members={m.patch_id:m for m in a.member}
    arc=SplitHttpTar([f"{a.base_url.rstrip('/')}/packages.tar.{i:03d}" for i in range(1,a.part_count+1)],retries=6,timeout=90)
    r=RemoteLogicalPackage(arc,members,a.runtime)
    targets={int(x.removeprefix('0x').removeprefix('0X'),16):x.removeprefix('0x').removeprefix('0X').upper() for x in a.target}
    ref_filter={x.removeprefix('0x').removeprefix('0X').upper() for x in a.reference}
    hits=[]; errors=[]; scanned=0; skipped_size=0; skipped_ref=0
    by_target=collections.Counter()
    for e in r.entries:
        if e['type']!=16 or e['subtype']!=0: continue
        if int(e['file_size'])>a.max_entry_size: skipped_size+=1; continue
        ref=e['reference'].upper()
        if ref_filter and ref not in ref_filter: skipped_ref+=1; continue
        try: b=r.entry(e['index'])
        except Exception as ex:
            errors.append({'tag_hash':e['tag_hash'].upper(),'entry_index':e['index'],'reference':ref,'error':repr(ex)}); continue
        scanned+=1
        end=len(b)-(len(b)%4)
        found=collections.defaultdict(list)
        for off in range(0,end,4):
            v=struct.unpack_from('<I',b,off)[0]
            if v in targets: found[targets[v]].append(off)
        if found:
            row={'source_tag_hash':e['tag_hash'].upper(),'entry_index':e['index'],'reference':ref,'size':e['file_size'],
                 'targets':{h:offs for h,offs in sorted(found.items())}}
            hits.append(row)
            for h,offs in found.items(): by_target[h]+=len(offs)
    rep={'schema':'d1_remote_target_backlinks/v1','package_id':f'{a.package_id:04X}','logical_view':r.view.name,
         'targets':list(targets.values()),'scanned_structured_entries':scanned,'skipped_size':skipped_size,'skipped_reference_filter':skipped_ref,
         'hit_source_count':len(hits),'occurrences_by_target':dict(by_target),'hits':hits,'errors':errors,
         'policy':'Hits are exact aligned serialized values. Zero hits only rules out this literal representation in the scanned payload set; indexed/indirect relations remain possible.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(rep,indent=2)+'\n')
    print(json.dumps({k:rep[k] for k in ('package_id','logical_view','scanned_structured_entries','hit_source_count','occurrences_by_target')},indent=2))
    return 0
if __name__=='__main__': raise SystemExit(main())
