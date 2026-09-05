#!/usr/bin/env python3
"""Resolve D1/Tiger raw StringHash values against a supplied wordlist.

QuickTag source independently establishes that Tiger raw-string lookup uses 32-bit
FNV-1 (offset basis 0x811C9DC5, prime 0x01000193). This helper hashes arbitrary
newline-delimited candidate strings and reports exact requested values.

A match proves the candidate string hashes to the value; collisions remain possible,
so semantic use should still be cross-checked against skeleton topology/context.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

FNV1_BASE=0x811C9DC5
FNV1_PRIME=0x01000193

def fnv1(data:bytes)->int:
    h=FNV1_BASE
    for b in data:
        h=((h*FNV1_PRIME)&0xffffffff)^b
    return h

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('wordlist',type=Path)
    ap.add_argument('--target',action='append',required=True)
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args()
    targets={int(x.removeprefix('0x').removeprefix('0X'),16):x.removeprefix('0x').removeprefix('0X').upper() for x in a.target}
    hits={h:[] for h in targets.values()}
    count=0
    with a.wordlist.open('r',encoding='utf-8',errors='replace') as f:
        for line in f:
            s=line.rstrip('\r\n')
            if not s: continue
            count+=1
            v=fnv1(s.encode('utf-8'))
            if v in targets: hits[targets[v]].append(s)
    rep={'schema':'d1_stringhash_wordlist_resolve/v1','algorithm':'FNV1-32','wordlist':str(a.wordlist),
         'candidate_count':count,'targets':list(targets.values()),'hits':hits,
         'resolved_target_count':sum(bool(x) for x in hits.values())}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(rep,indent=2)+'\n')
    print(json.dumps({'candidate_count':count,'resolved_target_count':rep['resolved_target_count'],
                      'hits':{k:v for k,v in hits.items() if v}},indent=2))
    return 0
if __name__=='__main__': raise SystemExit(main())
