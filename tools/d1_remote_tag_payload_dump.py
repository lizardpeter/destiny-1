#!/usr/bin/env python3
"""Dump exact D1 tag payloads from the universal remote PS4 corpus.

This is a deliberately semantics-free evidence helper. Each requested FileHash is
resolved through the verified universal member catalog, its exact decompressed
payload is written byte-for-byte, and package/class metadata is recorded. No
pointer interpretation or appearance meaning is inferred here.
"""
from __future__ import annotations
import argparse, hashlib, json, sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_activity_placements import RemoteCorpus
from d1_split_tar_extract import SplitHttpTar


def norm(x): return str(x).upper().removeprefix('0X').zfill(8)

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--tag',action='append',required=True)
    ap.add_argument('--member-catalog',type=Path,action='append',required=True)
    ap.add_argument('--base-url',required=True)
    ap.add_argument('--part-count',type=int,default=10)
    ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('--out-dir',type=Path,required=True)
    ap.add_argument('--report',type=Path,required=True)
    a=ap.parse_args()
    catalogs=load_catalogs(a.member_catalog)
    base=a.base_url.rstrip('/')
    arc=SplitHttpTar([f'{base}/packages.tar.{i:03d}' for i in range(1,a.part_count+1)],retries=6,timeout=90)
    c=RemoteCorpus(arc,catalogs,a.runtime)
    a.out_dir.mkdir(parents=True,exist_ok=True)
    rows=[];viol=[]
    for h in sorted({norm(x) for x in a.tag}):
        meta=c.entry_meta(h)
        row={'tag_hash':h,'meta':meta,'violations':[]}
        try: payload,src=c.payload(h)
        except Exception as ex:
            payload=None;src=None;row['violations'].append('payload:'+repr(ex))
        row['payload_source']=src
        if meta is None: row['violations'].append('meta_unavailable')
        if payload is not None:
            out=a.out_dir/f'{h}.bin';out.write_bytes(payload)
            row.update({'file':str(out),'bytes':len(payload),'sha256':hashlib.sha256(payload).hexdigest()})
        if row['violations']: viol.extend(f'{h}:{x}' for x in row['violations'])
        rows.append(row)
    rep={'schema_version':1,'status':'D1_REMOTE_TAG_PAYLOAD_DUMP_COMPLETE' if not viol else 'D1_REMOTE_TAG_PAYLOAD_DUMP_WITH_VIOLATIONS','tag_count':len(rows),'tags':rows,'violations':viol,'policy':'Exact retail payload extraction only; no semantic interpretation.'}
    a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(rep,indent=2)+'\n')
    print('STATUS',rep['status'],'TAGS',len(rows),'VIOLATIONS',len(viol))
    for r in rows: print(r['tag_hash'],r.get('bytes'),r.get('sha256'),r.get('payload_source'))
    return 0 if not viol else 2
if __name__=='__main__': raise SystemExit(main())
