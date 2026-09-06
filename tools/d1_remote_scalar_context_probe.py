#!/usr/bin/env python3
"""Record exact byte context around selected u32 scalar values in D1 tag payloads.

This tool is deliberately schema-agnostic. It is useful when a known StringHash or other
32-bit semantic anchor has been found in a resource but its field meaning is not yet typed.
For every aligned occurrence it preserves raw bytes, nearby aligned u32 values, and which
nearby values independently resolve as current FileHashes through the verified catalog.

A scalar match is evidence of equality only. This tool never assigns field semantics.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from d1_crota_raid_candidate_probe import LazyExactHashResolver
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_split_tar_extract import SplitHttpTar

NULLS={'00000000','FFFFFFFF'}

def norm(x):
    s=str(x).upper().removeprefix('0X').zfill(8); int(s,16); return s

def ascii_runs(b:bytes,base:int,min_len:int=4):
    out=[]; start=None
    for i,v in enumerate(b+b'\0'):
        if 0x20<=v<0x7f:
            if start is None:start=i
        else:
            if start is not None and i-start>=min_len:
                out.append({'offset':base+start,'string':b[start:i].decode('ascii','replace')})
            start=None
    return out

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--tag-hash',action='append',required=True)
    ap.add_argument('--scalar-u32',action='append',required=True)
    ap.add_argument('--radius',type=int,default=64)
    ap.add_argument('--member-catalog',type=Path,action='append',required=True)
    ap.add_argument('--base-url',required=True);ap.add_argument('--part-count',type=int,default=10)
    ap.add_argument('--runtime',type=Path,required=True);ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args()
    if a.radius<0:raise ValueError('radius must be non-negative')
    tags=list(dict.fromkeys(norm(x) for x in a.tag_hash));scalars=list(dict.fromkeys(norm(x) for x in a.scalar_u32))
    scalar_int={s:int(s,16) for s in scalars}
    cats=load_catalogs(a.member_catalog);base=a.base_url.rstrip('/')
    arc=SplitHttpTar([f'{base}/packages.tar.{i:03d}' for i in range(1,a.part_count+1)],retries=6,timeout=90)
    r=LazyExactHashResolver(arc,cats,a.runtime)
    rows=[];viol=[]
    for h in tags:
        row={'tag_hash':h,'scalar_occurrences':{},'violations':[]}
        try:view,e=r.locate(h);b=view.entry(e['index'])
        except Exception as ex:
            row['violations'].append('locate_or_payload:'+repr(ex));rows.append(row);continue
        row['package_id']=f"{int(view.h['pkg_id']):04X}"
        row['entry']={k:e[k] for k in ('index','tag_hash','reference','type','subtype','file_size')}
        row['entry']['tag_hash']=row['entry']['tag_hash'].upper();row['entry']['reference']=row['entry']['reference'].upper()
        row['payload_size']=len(b);row['payload_sha256']=hashlib.sha256(b).hexdigest()
        for sh,sv in scalar_int.items():
            occ=[]
            for off in range(0,len(b)-3,4):
                if struct.unpack_from('<I',b,off)[0]!=sv:continue
                start=max(0,off-a.radius);end=min(len(b),off+4+a.radius)
                # Align decoded neighboring words to the payload's dword grid.
                ustart=(start+3)&~3;uend=end-(end%4)
                words=[]
                for wo in range(ustart,uend,4):
                    v=struct.unpack_from('<I',b,wo)[0];vh=f'{v:08X}'
                    resolved=None
                    if vh not in NULLS:
                        try:vv,ve=r.locate(vh)
                        except Exception:pass
                        else:
                            resolved={'package_id':f"{int(vv.h['pkg_id']):04X}",'reference':ve['reference'].upper(),
                                      'type':int(ve['type']),'subtype':int(ve['subtype']),'file_size':int(ve['file_size'])}
                    words.append({'offset':wo,'relative_to_scalar':wo-off,'value':vh,'resolved_filehash':resolved})
                region=b[start:end]
                occ.append({'offset':off,'offset_hex':f'0x{off:X}','start':start,'end':end,
                            'bytes_hex':region.hex(),'ascii_runs':ascii_runs(region,start),'aligned_u32':words})
            row['scalar_occurrences'][sh]=occ
        rows.append(row);viol.extend(f'{h}:{x}' for x in row['violations'])
    out={'schema':'d1_remote_scalar_context_probe/v1','status':'D1_SCALAR_CONTEXT_EXACT' if not viol else 'D1_SCALAR_CONTEXT_PARTIAL',
         'scalar_u32':scalars,'radius':a.radius,'entries':rows,'violations':viol,
         'policy':'Scalar equality and byte offsets are exact. Nearby FileHash resolutions are exact independent catalog lookups. No scalar field meaning is inferred.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n')
    for row in rows:
        print('TAG',row['tag_hash'],'PKG',row.get('package_id'),'REF',(row.get('entry') or {}).get('reference'),'SIZE',row.get('payload_size'))
        for sh,occ in row.get('scalar_occurrences',{}).items():
            print(' SCALAR',sh,'OCCURRENCES',[x['offset_hex'] for x in occ])
            for x in occ:
                near=[(w['relative_to_scalar'],w['value'],(w['resolved_filehash'] or {}).get('reference')) for w in x['aligned_u32'] if w['resolved_filehash']]
                print('  CONTEXT',x['offset_hex'],'ASCII',[(s['offset'],s['string']) for s in x['ascii_runs']],'RESOLVED_NEAR',near)
    print('STATUS',out['status'],'VIOLATIONS',viol)
    return 0 if not viol else 2

if __name__=='__main__':raise SystemExit(main())
