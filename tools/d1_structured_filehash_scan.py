#!/usr/bin/env python3
"""Conservative cross-package FileHash candidate scan for D1 structured Tiger tags.

D1 v24 TagHash/FileHash construction is byte-validated in spec/D1_TIGER_PACKAGE_v24.md:
    0x80800000 + (package_id << 13) + entry_index

This tool scans *aligned little-endian dwords* in resident type-16 structured payloads,
and retains only values whose decoded package id is present in an explicit archive
package-id allowlist.  A hit is still only a serialized FileHash-shaped literal.  It
is strong dependency-triage evidence, but does NOT by itself establish the semantic
role of the referenced resource.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, struct, sys
from collections import Counter, defaultdict
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from d1_entry_extract import EntryReader

BASE=0x80800000
ENTRY_MASK=0x1FFF


def decode_filehash(v:int):
    if v < BASE: return None
    d=v-BASE
    return d >> 13, d & ENTRY_MASK


def read_ids(path:Path)->set[int]:
    out=set()
    for raw in path.read_text().splitlines():
        s=raw.strip().upper().removeprefix('0X')
        if not s or s.startswith('#'): continue
        out.add(int(s,16))
    return out


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--snapshot',type=Path,action='append',required=True)
    ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('--valid-package-ids',type=Path,required=True,
                    help='one hexadecimal archive package id per line')
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--max-payload',type=int,default=8*1024*1024)
    args=ap.parse_args(); args.out.mkdir(parents=True,exist_ok=True)

    valid=read_ids(args.valid_package_ids)
    readers=[]
    for p in args.snapshot:
        r=EntryReader(p.resolve(),args.runtime); readers.append((p.resolve(),r))

    hits=[]; target_packages=Counter(); source_classes=Counter(); pair_counts=Counter()
    payload_errors=[]; payloads_scanned=0; dwords_scanned=0
    seen_payloads=set()

    for si,(p,r) in enumerate(readers):
        for e in r.entries:
            if int(e['type']) != 16 or not r.available(e['index']) or int(e['file_size']) > args.max_payload:
                continue
            try: b=r.entry(e['index'])
            except Exception as ex:
                payload_errors.append({'snapshot':p.name,'entry_index':int(e['index']),'tag_hash':e['tag_hash'].upper(),'error':repr(ex)})
                continue
            sha=hashlib.sha256(b).hexdigest()
            # The exact same structured payload repeated in multiple patch snapshots adds
            # no new dependency literals. Preserve one scan and record its source snapshot.
            dedup_key=(e['tag_hash'].upper(),sha)
            if dedup_key in seen_payloads: continue
            seen_payloads.add(dedup_key); payloads_scanned+=1
            source_ref=e['reference'].upper(); local_pkg=int(r.h['pkg_id'])
            grouped=defaultdict(list)
            for off in range(0,len(b)-3,4):
                dwords_scanned+=1
                v=struct.unpack_from('<I',b,off)[0]
                dec=decode_filehash(v)
                if dec is None: continue
                pkg,idx=dec
                if pkg not in valid: continue
                grouped[(v,pkg,idx)].append(off)
            for (v,pkg,idx),offs in grouped.items():
                target_packages[f'{pkg:04X}'] += len(offs)
                source_classes[source_ref] += len(offs)
                pair_counts[(f'{local_pkg:04X}',f'{pkg:04X}')] += len(offs)
                hits.append({
                    'source_snapshot':p.name,
                    'source_package_id':f'{local_pkg:04X}',
                    'source_entry_index':int(e['index']),
                    'source_tag_hash':e['tag_hash'].upper(),
                    'source_reference':source_ref,
                    'source_payload_sha256':sha,
                    'literal_filehash':f'{v:08X}',
                    'target_package_id':f'{pkg:04X}',
                    'target_entry_index':idx,
                    'count':len(offs),
                    'aligned_offsets':offs,
                    'is_same_package':pkg==local_pkg,
                    'evidence_kind':'aligned_filehash_literal_archive_package_id_validated',
                    'semantic_policy':'serialized FileHash-shaped co-reference/dependency candidate only; target role and ownership not inferred'
                })

    summary={
        'snapshot_count':len(readers),'valid_archive_package_id_count':len(valid),
        'unique_structured_payloads_scanned':payloads_scanned,'aligned_dwords_scanned':dwords_scanned,
        'literal_records':len(hits),'literal_occurrences':sum(x['count'] for x in hits),
        'distinct_target_package_ids':len(target_packages),'payload_error_count':len(payload_errors),
        'target_package_hit_counts':dict(target_packages.most_common()),
        'source_reference_hit_counts':dict(source_classes.most_common()),
        'source_target_package_hit_counts':[
            {'source_package_id':a,'target_package_id':b,'count':n}
            for (a,b),n in pair_counts.most_common()
        ],
    }
    report={'summary':summary,'hits':hits,'payload_errors':payload_errors,'policy':{
        'hash_formula':'0x80800000 + (package_id << 13) + entry_index',
        'alignment':'4-byte aligned little-endian dwords only',
        'validation':'decoded package id must exist in explicit archive package-id allowlist',
        'semantics':'hit is a candidate serialized dependency/co-reference, not an ownership or placement assignment'
    }}
    (args.out/'structured_filehash_scan.json').write_text(json.dumps(report,indent=2)+'\n')
    with (args.out/'structured_filehash_hits.csv').open('w',newline='') as f:
        fields=['source_snapshot','source_package_id','source_entry_index','source_tag_hash','source_reference','literal_filehash','target_package_id','target_entry_index','count','aligned_offsets','is_same_package','evidence_kind','semantic_policy']
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for x in hits:
            q={k:x[k] for k in fields};q['aligned_offsets']=';'.join(hex(v) for v in q['aligned_offsets']);w.writerow(q)
    print(json.dumps(summary,indent=2))
    return 0

if __name__=='__main__': raise SystemExit(main())
