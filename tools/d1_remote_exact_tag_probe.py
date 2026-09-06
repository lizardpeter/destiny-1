#!/usr/bin/env python3
"""Probe arbitrary exact D1 PS4 Tiger tags through the verified universal catalog.

This is intentionally schema-agnostic. It is for unknown-class reversal and export
coverage, not semantic guessing. For each requested FileHash it records:
- exact package/entry metadata and payload SHA-256,
- printable source strings,
- every aligned 32-bit value that resolves to an exact Tiger entry,
- resolved target metadata including class/reference/type/subtype/size.

An aligned resolvable dword is evidence of a serialized value at that byte offset,
not automatically a typed field. Semantic promotion requires an independent schema
or source-mapped layout.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0,str(HERE))

from d1_crota_raid_candidate_probe import LazyExactHashResolver, meta_row, norm
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_split_tar_extract import SplitHttpTar


def printable_strings(payload: bytes, minimum: int) -> list[dict]:
    out=[]
    start=None
    for i,b in enumerate(payload+b'\0'):
        if 0x20 <= b < 0x7F:
            if start is None:
                start=i
        else:
            if start is not None and i-start >= minimum:
                out.append({'offset':start,'string':payload[start:i].decode('ascii','replace')})
            start=None
    return out


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--tag-hash',action='append',required=True)
    ap.add_argument('--member-catalog',action='append',type=Path,required=True)
    ap.add_argument('--base-url',required=True)
    ap.add_argument('--part-count',type=int,default=10)
    ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('--min-string',type=int,default=4)
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args()

    catalogs=load_catalogs(a.member_catalog)
    base=a.base_url.rstrip('/')
    arc=SplitHttpTar([f'{base}/packages.tar.{i:03d}' for i in range(1,a.part_count+1)],retries=6,timeout=90)
    resolver=LazyExactHashResolver(arc,catalogs,a.runtime)

    rows=[]
    violations=[]
    for raw in a.tag_hash:
        h=norm(raw)
        row={'tag_hash':h,'violations':[]}
        try:
            view,e=resolver.locate(h)
            payload=view.entry(e['index'])
            row['package_id']=f'{((int(h,16)-0x80800000)>>13)&0x7ff:04X}'
            row['logical_view']=view.view.name
            row['entry']=meta_row(e)
            row['payload_size']=len(payload)
            row['payload_sha256']=hashlib.sha256(payload).hexdigest()
            row['printable_strings']=printable_strings(payload,a.min_string)
            matches=[]
            for off in range(0,len(payload)-3,4):
                x=struct.unpack_from('<I',payload,off)[0]
                if x in (0,0xFFFFFFFF):
                    continue
                try:
                    _tv,te=resolver.locate(f'{x:08X}')
                except Exception:
                    continue
                matches.append({
                    'offset':off,
                    'tag_hash':f'{x:08X}',
                    'entry':meta_row(te),
                })
            row['aligned_resolved_tags']=matches
            row['aligned_resolved_tag_count']=len(matches)
        except Exception as ex:
            msg=repr(ex)
            row['violations'].append(msg)
            violations.append({'tag_hash':h,'error':msg})
        rows.append(row)

    report={
        'schema':'d1_remote_exact_tag_probe/v1',
        'status':'D1_EXACT_TAG_PROBE' if not violations else 'D1_EXACT_TAG_PROBE_WITH_VIOLATIONS',
        'entries':rows,
        'violation_count':len(violations),
        'violations':violations,
        'policy':(
            'Tag bytes and aligned dword offsets are exact retail evidence. Resolvable aligned dwords are not promoted '
            'to semantic fields without an independently validated class/layout parser.'
        ),
    }
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(report,indent=2)+'\n')
    for r in rows:
        print('TAG',r['tag_hash'],'ENTRY',r.get('entry'),'SHA256',r.get('payload_sha256'),
              'STRINGS',len(r.get('printable_strings',[])),'RESOLVED',r.get('aligned_resolved_tag_count'),
              'VIOLATIONS',r.get('violations'))
        for s in r.get('printable_strings',[]):
            print(' STRING',hex(s['offset']),repr(s['string']))
        for m in r.get('aligned_resolved_tags',[]):
            e=m['entry']
            print(' REF',hex(m['offset']),m['tag_hash'],e.get('reference'),e.get('type'),e.get('subtype'),e.get('file_size'))
    return 0 if not violations else 2

if __name__=='__main__':
    raise SystemExit(main())
