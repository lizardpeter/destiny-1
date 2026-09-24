#!/usr/bin/env python3
"""Build an exact remote package-member catalog for a known FileHash target set.

Unlike d1_remote_activity_index.py, this does not index the entire D1 archive.
Each target FileHash already encodes its Tiger package id. We filter packages.txt
for only those ordinary package families, locate those physical members in the
split TAR, validate each package header against the encoded filename/package id,
and emit the same d1_remote_package_member_catalog/v1 schema consumed by
RemoteCorpus.

No semantic ownership is inferred from filenames; filenames are used only to
select physical generations of package ids already dictated by the FileHashes.
"""
from __future__ import annotations
import argparse,hashlib,json,re,sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from d1_filehash import package_hex
from d1_pkg_probe import parse_header
from d1_split_tar_extract import SplitHttpTar

RX=re.compile(r'_([0-9A-Fa-f]{4})_([0-9]+)\.pkg$',re.I)

def norm(x): return str(x).upper().removeprefix('0X').zfill(8)

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--package-list',type=Path,required=True)
    ap.add_argument('--target-hash',action='append',default=[])
    ap.add_argument('--target-hash-list',type=Path)
    ap.add_argument('--base-url',required=True)
    ap.add_argument('--part-count',type=int,default=10)
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args()

    hashes={norm(x) for x in a.target_hash}
    if a.target_hash_list:
        hashes|={norm(x) for x in a.target_hash_list.read_text().split() if x.strip()}
    if not hashes: raise SystemExit('no target hashes')
    pids=sorted({package_hex(h).upper() for h in hashes})
    pset=set(pids)

    raw=a.package_list.read_bytes(); list_sha=hashlib.sha256(raw).hexdigest()
    wanted={}
    excluded_matching=[]
    for line in raw.decode('utf-8',errors='replace').splitlines():
        name=Path(line.strip()).name
        if not name.lower().endswith('.pkg'): continue
        m=RX.search(name)
        if m and m.group(1).upper() in pset:
            wanted[name]=(m.group(1).upper(),int(m.group(2)))
        elif any(f'_{pid.lower()}_' in name.lower() for pid in pids):
            excluded_matching.append(name)
    by_pid={pid:[] for pid in pids}
    for n,(pid,gen) in wanted.items(): by_pid[pid].append((gen,n))
    missing=[pid for pid,v in by_pid.items() if not v]
    if missing: raise SystemExit(f'target package ids absent from ordinary packages.txt namespace: {missing}')

    base=a.base_url.rstrip('/')
    arc=SplitHttpTar([f'{base}/packages.tar.{i:03d}' for i in range(1,a.part_count+1)],retries=6,timeout=90)
    found,headers=arc.find(set(wanted))
    missing_names=sorted(set(wanted)-set(found))
    if missing_names: raise SystemExit(f'{len(missing_names)} targeted package members not found: {missing_names[:20]}')

    families={pid:[] for pid in pids}; violations=[]
    for name,(pid,gen) in sorted(wanted.items()):
        loc=found[name]; size=int(loc['size'])
        if size<0x140:
            violations.append(f'{name}:short:{size}'); continue
        hb=arc.read_at(int(loc['data_offset']),0x140)
        h=parse_header(__import__('io').BytesIO(hb))
        header_pid=f"{int(h['pkg_id']):04X}"
        if header_pid!=pid: violations.append(f'{name}:header_package:{header_pid}!={pid}')
        families[pid].append({
            'name':name,
            'data_offset':int(loc['data_offset']),
            'size':size,
            'tar_header_offset':int(loc['header_offset']),
            'filename_generation':gen,
            'header_patch_id':int(h['patch_id']),
        })
    for pid,rows in families.items():
        rows.sort(key=lambda r:(r['header_patch_id'],r['filename_generation'],r['name']))
        if not rows: violations.append(f'{pid}:no_valid_members')
    if violations: raise SystemExit('; '.join(violations[:20]))

    out={
      'schema':'d1_remote_package_member_catalog/v1',
      'scope':'target_filehash_package_families',
      'source':'packages.txt + split-TAR sparse target-family walk',
      'packages_txt_sha256':list_sha,
      'target_hash_count':len(hashes),
      'target_hashes':sorted(hashes),
      'target_package_ids':pids,
      'physical_member_count':sum(len(v) for v in families.values()),
      'package_family_count':len(families),
      'excluded_locale_or_variant_matching_member_count':len(excluded_matching),
      'excluded_locale_or_variant_matching_members':sorted(excluded_matching),
      'tar_headers_scanned_until_all_targets_found':headers,
      'families':families,
      'policy':'Package ids come only from the source-validated banked D1 FileHash decoder. packages.txt filenames identify physical generations only. Every selected physical member header is re-read from the retail split TAR and its Tiger package id must match the FileHash-derived package id.'
    }
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ['target_hash_count','target_package_ids','physical_member_count','package_family_count','tar_headers_scanned_until_all_targets_found','packages_txt_sha256']},indent=2))
    return 0
if __name__=='__main__': raise SystemExit(main())
