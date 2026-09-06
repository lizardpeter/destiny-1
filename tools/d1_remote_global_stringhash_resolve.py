#!/usr/bin/env python3
"""Resolve exact D1 StringHashes through verified retail GlobalStrings banks.

Inputs may be raw StringHashes and/or source-mapped generic-name tags
(class 0x808013F3). Generic-name tags are converted to their underlying
StringHash from +0x0C, matching the source-mapped D1 Entity.Load path.

The resolver scans only caller-selected verified package families for exact
0x80800550 GlobalStrings containers, then parses ActivityGlobalStrings and
CharacterNames through the already source-crosschecked D1 localized-string
layouts. Collisions are preserved. No guessing or fuzzy string matching occurs.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
if str(HERE) not in sys.path: sys.path.insert(0,str(HERE))

from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_entity_names_resolve import (
    GLOBAL_CONTAINER, GENERIC_NAME_TAG_CLASS, NULLS, Resolver,
    hx, norm, resolve_localized, u32,
)
from d1_split_tar_extract import SplitHttpTar


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--string-hash',action='append',default=[])
    ap.add_argument('--generic-name-tag',action='append',default=[])
    ap.add_argument('--global-package-id',type=lambda x:int(x,0),action='append',required=True)
    ap.add_argument('--member-catalog',type=Path,action='append',required=True)
    ap.add_argument('--base-url',required=True)
    ap.add_argument('--part-count',type=int,default=10)
    ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args()
    if not a.string_hash and not a.generic_name_tag:
        raise SystemExit('at least one --string-hash or --generic-name-tag is required')

    catalogs=load_catalogs(a.member_catalog)
    arc=SplitHttpTar([f"{a.base_url.rstrip('/')}/packages.tar.{i:03d}" for i in range(1,a.part_count+1)],retries=6,timeout=90)
    res=Resolver(arc,catalogs,a.runtime)

    targets={norm(x) for x in a.string_hash}
    generic_map={}
    violations=[]
    for raw in a.generic_name_tag:
        tag=norm(raw)
        try:
            _v,e,b=res.bytes(tag)
            if e['reference'].upper()!=GENERIC_NAME_TAG_CLASS:
                raise ValueError(f'{tag}: class {e["reference"].upper()} != {GENERIC_NAME_TAG_CLASS}')
            if len(b)<0x10: raise ValueError(f'{tag}: payload shorter than 0x10')
            sh=hx(u32(b,0x0C))
            generic_map[tag]=sh
            targets.add(sh)
            print('GENERIC_NAME_TAG',tag,'STRING_HASH',sh)
        except Exception as ex:
            violations.append({'generic_name_tag':tag,'error':repr(ex)})

    targets.discard('811C9DC5')
    package_ids=list(dict.fromkeys(a.global_package_id))
    containers=[];hits=[];scan_errors=[]
    for pkg in package_ids:
        try: view=res.view(pkg)
        except Exception as ex:
            scan_errors.append({'package_id':f'{pkg:04X}','error':repr(ex)}); continue
        for e in view.entries:
            if e['reference'].upper()!=GLOBAL_CONTAINER: continue
            ch=e['tag_hash'].upper()
            try:
                b=view.entry(e['index'])
                if len(b)<0xEC: raise ValueError('global container shorter than 0xEC')
                activity=hx(u32(b,0x68)); characters=hx(u32(b,0xE8))
                row={'package_id':f'{pkg:04X}','container':ch,'activity_global_strings':activity,'character_names':characters}
                containers.append(row)
                for kind,h in [('activity_global_strings',activity),('character_names',characters)]:
                    if h in NULLS: continue
                    try: hits.extend(resolve_localized(res,h,targets,kind,ch))
                    except Exception as ex: row.setdefault('bank_errors',[]).append({'kind':kind,'hash':h,'error':repr(ex)})
            except Exception as ex:
                scan_errors.append({'package_id':f'{pkg:04X}','container':ch,'error':repr(ex)})

    resolved={h:[] for h in sorted(targets)}
    for x in hits:
        if x.get('ok') and x.get('string') is not None:
            resolved.setdefault(x['string_hash'],[]).append(x)
    unresolved=[h for h in sorted(targets) if not resolved.get(h)]
    report={
        'schema':'d1_remote_global_stringhash_resolve/v1',
        'generic_name_tag_to_string_hash':generic_map,
        'target_string_hashes':sorted(targets),
        'global_package_ids':[f'{x:04X}' for x in package_ids],
        'global_container_count':len(containers),
        'global_containers':containers,
        'resolved':resolved,
        'unresolved_target_hashes':unresolved,
        'violation_count':len(violations),
        'violations':violations,
        'scan_errors':scan_errors,
        'policy':'Generic-name tag +0x0C and localized string structures are source-mapped D1 fields. Only exact StringHash equality is accepted; collisions are preserved.',
    }
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(report,indent=2)+'\n')
    print('TARGETS',sorted(targets),'UNRESOLVED',unresolved,'VIOLATIONS',violations)
    for h,rows in resolved.items():
        for r in rows: print('RESOLVED',h,repr(r.get('string')),'BANK',r.get('bank_kind'),'CONTAINER',r.get('container'))
    return 0 if not violations else 2

if __name__=='__main__': raise SystemExit(main())
