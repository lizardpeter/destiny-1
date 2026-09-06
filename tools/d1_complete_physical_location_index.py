#!/usr/bin/env python3
"""Complete the D1 PS4 physical package-location catalog by scanning only known gaps.

The published Activity index retained exact TAR locations for the 1,275 ordinary
``..._XXXX_generation.pkg`` members, while the current packages.txt contains 2,105
physical .pkg members total. The omitted members are localized cinematic variants
and nine bootstrap/UI special variants.

Because TAR is sequential, every omitted member must lie either between two retained
members or after the final retained member. This tool treats each retained member's
exact aligned end and the next retained header as a bounded gap, validates every TAR
header encountered there, and jumps over payloads by recorded size. Payload bodies
are never downloaded.

Success requires the union of retained + recovered basenames to equal packages.txt
exactly. Thus the result is a complete physical-location ledger without rewalking
already indexed TAR headers.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

from d1_split_tar_extract import SplitHttpTar,tar_header_checksum_ok,tar_name,parse_tar_number,BLOCK

BASE_RX=re.compile(r'_([0-9A-Fa-f]{4})_([0-9]+)\.pkg$',re.I)
LOCALE_RX=re.compile(r'_([0-9A-Fa-f]{4})_([A-Za-z0-9]+)_([0-9]+)\.pkg$',re.I)


def aligned_member_end(header_offset:int,size:int)->int:
    return header_offset+BLOCK+((size+BLOCK-1)//BLOCK)*BLOCK


def namespace(name:str)->dict:
    if m:=BASE_RX.search(name):
        return {'kind':'base','package_id':m.group(1).upper(),'generation':int(m.group(2)),'locale':None}
    if m:=LOCALE_RX.search(name):
        return {'kind':'localized','package_id':m.group(1).upper(),'generation':int(m.group(3)),'locale':m.group(2).lower()}
    return {'kind':'special','package_id':None,'generation':None,'locale':None}


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--activity-index',type=Path,required=True)
    ap.add_argument('--package-list',type=Path,required=True)
    ap.add_argument('--base-url',default='https://crypt.cohae.dev/destiny/ps4/packages/latest')
    ap.add_argument('--part-count',type=int,default=10)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--retries',type=int,default=6);ap.add_argument('--timeout',type=int,default=120)
    a=ap.parse_args()

    src=json.loads(a.activity_index.read_text())
    if int(src.get('schema_version',0))!=2 or src.get('status')!='D1_REMOTE_ACTIVITY_INDEX_COMPLETE':
        raise ValueError('source is not a complete Activity index v2')
    package_bytes=a.package_list.read_bytes();package_sha=hashlib.sha256(package_bytes).hexdigest()
    if package_sha!=str((src.get('source') or {}).get('package_list_sha256') or '').lower():
        raise ValueError('packages.txt SHA does not match source Activity index')
    wanted={Path(x.strip()).name for x in package_bytes.decode('utf-8',errors='replace').splitlines()
            if x.strip().lower().endswith('.pkg')}
    if not wanted:raise ValueError('empty package list')

    known={};known_rows=[]
    for pkg,rows in (src.get('package_families') or {}).items():
        for row in rows:
            name=Path(str(row['name'])).name;off=int(row['tar_header_offset']);size=int(row['size']);do=int(row['data_offset'])
            if do!=off+BLOCK:raise ValueError(f'{name}: source data/header delta != 512')
            if name in known:raise ValueError(f'duplicate retained package {name}')
            rec={'name':name,'archive_name':name,'tar_header_offset':off,'data_offset':do,'size':size,
                 'source':'retained_activity_index',**namespace(name)}
            known[name]=rec;known_rows.append(rec)
    known_rows.sort(key=lambda x:x['tar_header_offset'])
    if set(known)-wanted:raise ValueError(f'Activity index contains names absent from packages.txt: {sorted(set(known)-wanted)[:20]}')

    base=a.base_url.rstrip('/');arc=SplitHttpTar([f'{base}/packages.tar.{i:03d}' for i in range(1,a.part_count+1)],retries=a.retries,timeout=a.timeout)
    source_sizes=[int(x) for x in (src.get('source') or {}).get('part_sizes',[])]
    if source_sizes and arc.sizes!=source_sizes:raise ValueError(f'split TAR part sizes changed: {arc.sizes} != {source_sizes}')
    if int((src.get('source') or {}).get('logical_split_tar_bytes',arc.logical_size))!=arc.logical_size:
        raise ValueError('logical split TAR size changed from source Activity index')

    recovered={};gap_rows=[];headers_read=0
    for i,row in enumerate(known_rows):
        start=aligned_member_end(int(row['tar_header_offset']),int(row['size']))
        end=int(known_rows[i+1]['tar_header_offset']) if i+1<len(known_rows) else arc.logical_size
        if start>end:raise ValueError(f'overlapping retained members at {row["name"]}')
        if start==end:continue
        off=start;members=[];zero_headers=0
        while off+BLOCK<=end:
            h=arc.read_at(off,BLOCK);headers_read+=1
            if h==b'\0'*BLOCK:
                zero_headers+=1;off+=BLOCK
                if off<end and i+1<len(known_rows):
                    raise ValueError(f'unexpected zero TAR header inside bounded gap 0x{start:X}..0x{end:X}')
                continue
            zero_headers=0
            if h[257:262]!=b'ustar':raise ValueError(f'invalid TAR magic at 0x{off:X} in gap 0x{start:X}..0x{end:X}')
            if not tar_header_checksum_ok(h):raise ValueError(f'TAR checksum mismatch at 0x{off:X}')
            archive_name=tar_name(h);name=Path(archive_name).name;size=parse_tar_number(h[124:136])
            nxt=aligned_member_end(off,size)
            if nxt>end:raise ValueError(f'{name}: member span 0x{off:X}..0x{nxt:X} crosses known gap end 0x{end:X}')
            if name in known or name in recovered:raise ValueError(f'duplicate recovered/known TAR member {name}')
            if name not in wanted:raise ValueError(f'TAR member {name!r} at 0x{off:X} absent from exact packages.txt')
            rec={'name':name,'archive_name':archive_name,'tar_header_offset':off,'data_offset':off+BLOCK,'size':size,
                 'source':'gap_recovery',**namespace(name)}
            recovered[name]=rec;members.append(rec);off=nxt
        if off!=end:raise ValueError(f'gap walk ended 0x{off:X}, expected 0x{end:X}')
        gap_rows.append({'start':start,'end':end,'byte_span':end-start,'recovered_member_count':len(members),
                         'recovered_names':[x['name'] for x in members],'zero_header_count':zero_headers})

    combined={**known,**recovered};missing=sorted(wanted-set(combined));extra=sorted(set(combined)-wanted)
    if missing or extra:raise ValueError(f'complete catalog mismatch missing={missing[:30]} extra={extra[:30]}')
    ordered=sorted(combined.values(),key=lambda x:x['tar_header_offset'])
    if len(ordered)!=len(wanted):raise ValueError('combined physical-member count mismatch')
    kinds=Counter(x['kind'] for x in ordered);langs=Counter(x['locale'] for x in ordered if x['locale'])

    # Prove exact continuous TAR ordering between every consecutive physical package.
    discontinuities=[]
    for x,y in zip(ordered,ordered[1:]):
        expected=aligned_member_end(int(x['tar_header_offset']),int(x['size']))
        if expected!=int(y['tar_header_offset']):discontinuities.append((x['name'],expected,y['name'],y['tar_header_offset']))
    if discontinuities:raise ValueError(f'physical package sequence still has gaps: {discontinuities[:10]}')
    tail=aligned_member_end(int(ordered[-1]['tar_header_offset']),int(ordered[-1]['size']))
    trailing=arc.logical_size-tail
    if trailing not in (0,1024):raise ValueError(f'unexpected trailing TAR bytes after final package: {trailing}')

    rep={
      'schema':'d1_complete_physical_location_index/v1','status':'D1_COMPLETE_PHYSICAL_LOCATION_INDEX_EXACT',
      'source':{'activity_index':str(a.activity_index),'activity_index_sha256':hashlib.sha256(a.activity_index.read_bytes()).hexdigest(),
                'package_list':str(a.package_list),'package_list_sha256':package_sha,'base_url':base,'part_count':a.part_count,
                'part_sizes':arc.sizes,'logical_split_tar_bytes':arc.logical_size},
      'counts':{'packages_txt_members':len(wanted),'retained_activity_members':len(known),'gap_recovered_members':len(recovered),
                'complete_physical_members':len(ordered),'gap_count':sum(1 for g in gap_rows if g['byte_span']>0),
                'gap_tar_headers_read':headers_read,'namespace_counts':dict(kinds),'locale_counts':dict(sorted(langs.items()))},
      'trailing_zero_tar_bytes':trailing,'gaps':gap_rows,'members':ordered,
      'policy':'Physical TAR location evidence only. Every recovered header passed ustar magic/checksum validation inside an exact gap bounded by retained package locations, and the final basename set equals packages.txt exactly. Locale variants remain distinct physical namespaces and are not collapsed by package id.'
    }
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(rep,indent=2)+'\n')
    print(json.dumps({'status':rep['status'],**rep['counts'],'trailing_zero_tar_bytes':trailing},indent=2))
    return 0

if __name__=='__main__':raise SystemExit(main())
