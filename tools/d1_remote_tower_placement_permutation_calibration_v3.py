#!/usr/bin/env python3
"""Run the placement/model-switch calibration across every SD912 table in Tower.

This is a discovery wrapper around the corrected v2 calibration.  It enumerates
all source-typed SD9128080 entries from the exact logical views of caller-selected
Tower package families, then hands those exact TagHashes to the unchanged
fail-closed calibration core.
"""
from __future__ import annotations

import argparse, sys
from pathlib import Path

import d1_remote_tower_placement_permutation_calibration_v2 as corrected
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_investment_parent_probe import RemoteLogicalPackage
from d1_split_tar_extract import SplitHttpTar

base = corrected.base


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--scan-package-id',action='append',type=lambda x:int(x,0),required=True)
    ap.add_argument('--member-catalog',type=Path,action='append',required=True)
    ap.add_argument('--base-url',required=True)
    ap.add_argument('--part-count',type=int,default=10)
    ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args()

    cats=load_catalogs(a.member_catalog)
    missing=[p for p in a.scan_package_id if p not in cats]
    if missing:raise SystemExit('missing verified catalogs: '+','.join(f'{p:04X}' for p in missing))
    arc=SplitHttpTar([f'{a.base_url.rstrip("/")}/packages.tar.{i:03d}' for i in range(1,a.part_count+1)],retries=6,timeout=90)
    owners=[]
    for pkg in dict.fromkeys(a.scan_package_id):
        view=RemoteLogicalPackage(arc,cats[pkg],a.runtime)
        hits=[e['tag_hash'].upper() for e in view.entries if e.get('reference','').upper()==base.SD912]
        owners.extend(hits)
        print('SD912_PACKAGE',f'{pkg:04X}','COUNT',len(hits),'TAGS',hits,flush=True)
    owners=list(dict.fromkeys(owners))
    if not owners:raise SystemExit('no SD912 scripted tables found in requested package views')

    argv=['d1_remote_tower_placement_permutation_calibration_v2.py']
    for h in owners:argv += ['--scripted-owner',h]
    for p in a.member_catalog:argv += ['--member-catalog',str(p)]
    argv += ['--base-url',a.base_url,'--part-count',str(a.part_count),'--runtime',str(a.runtime),'-o',str(a.output)]
    print('CALIBRATING_SD912_OWNER_COUNT',len(owners),flush=True)
    sys.argv=argv
    return base.main()

if __name__=='__main__':raise SystemExit(main())
