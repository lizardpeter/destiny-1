#!/usr/bin/env python3
"""Recursively close package dependencies discovered by D1 texture extraction.

This driver turns d1_world_material_texture_export.py into a self-closing stage:

  material selector + initial exact package corpus
      -> exact material/texture export
      -> read missing_texture_package_ids
      -> recover only those current physical package families
      -> rerun until missing_texture_package_ids == {}

Missing package IDs are produced by serialized D1 Texture FileHashes/backing
references inside the exporter.  They are never inferred from filenames or from
visual appearance.  Checked-in member catalogs and prior reports may provide exact
current physical offsets/SHA-256s; if a required family has no complete matching
catalog, only that family is discovered by scanning the public split TAR.

This is intentionally generic so character/NPC/world exporters do not need a new
hard-coded workflow every time an otherwise complete material set crosses into a
new texture package namespace.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from d1_tower_recover_articulated_visual_corpus import (
    current_families, ingest_catalog, ingest_prior_report, pid
)
from d1_split_tar_extract import SplitHttpTar


def run_export(snapshots:list[Path],runtime:Path,visual_json:list[Path],out_dir:Path,stdout_path:Path)->dict:
    if out_dir.exists(): shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True,exist_ok=True)
    cmd=[sys.executable,str(HERE/'d1_world_material_texture_export.py')]
    for p in snapshots:cmd+=['--snapshot',str(p)]
    cmd+=['--runtime',str(runtime)]
    for p in visual_json:cmd+=['--visual-json',str(p)]
    cmd+=['--out',str(out_dir)]
    cp=subprocess.run(cmd,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    stdout_path.parent.mkdir(parents=True,exist_ok=True)
    stdout_path.write_text(cp.stdout)
    # Exporter can legitimately return nonzero while reporting missing packages.
    manifest=out_dir/'material_texture_manifest.json'
    if not manifest.exists():
        raise RuntimeError(f'texture exporter emitted no manifest (rc={cp.returncode}); see {stdout_path}')
    return json.loads(manifest.read_text())


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--snapshot',type=Path,action='append',required=True)
    ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('--visual-json',type=Path,action='append',required=True)
    ap.add_argument('--package-list',type=Path,required=True)
    ap.add_argument('--prior-report',type=Path,action='append',default=[])
    ap.add_argument('--member-catalog',type=Path,action='append',default=[])
    ap.add_argument('--expansion-dir',type=Path,required=True)
    ap.add_argument('--work-dir',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True,help='Final closed texture-export directory')
    ap.add_argument('--report',type=Path,required=True)
    ap.add_argument('--base-url',default='https://crypt.cohae.dev/destiny/ps4/packages/latest')
    ap.add_argument('--part-count',type=int,default=10)
    ap.add_argument('--max-passes',type=int,default=8)
    a=ap.parse_args()

    initial=[p.resolve() for p in a.snapshot]
    snapshots=list(initial)
    present_ids={x for x in (pid(p.name) for p in snapshots) if x}
    current=current_families(a.package_list)
    locations={};provenance=[]
    for p in a.prior_report:ingest_prior_report(p,locations,provenance)
    for p in a.member_catalog:ingest_catalog(p,locations,provenance)
    a.expansion_dir.mkdir(parents=True,exist_ok=True);a.work_dir.mkdir(parents=True,exist_ok=True)
    archive=SplitHttpTar([f'{a.base_url.rstrip("/")}/packages.tar.{i:03d}' for i in range(1,a.part_count+1)],retries=6,timeout=120)

    passes=[];recovered=[];final_manifest=None;stop=None
    for i in range(a.max_passes):
        pass_dir=a.work_dir/f'pass_{i:02d}'
        manifest=run_export(snapshots,a.runtime.resolve(),[p.resolve() for p in a.visual_json],pass_dir,a.work_dir/f'pass_{i:02d}.stdout.txt')
        final_manifest=manifest
        missing_raw=manifest.get('missing_texture_package_ids') or {}
        missing_ids=sorted(str(x).lower().removeprefix('0x').zfill(4) for x in missing_raw)
        new_ids=[x for x in missing_ids if x not in present_ids]
        row={'pass':i,'snapshot_count':len(snapshots),'present_package_ids':sorted(present_ids),
             'visible_material_count':manifest.get('visible_material_count'),'unique_texture_tags':manifest.get('unique_texture_tags'),
             'decoded_texture_tags':manifest.get('decoded_texture_tags'),'texture_errors':manifest.get('texture_errors'),
             'missing_texture_package_ids':missing_raw,'new_package_ids':new_ids,'recovered_members':[],'family_modes':{},
             'manifest':str(pass_dir/'material_texture_manifest.json')}
        passes.append(row)
        if not missing_ids:
            stop='closed_zero_missing_texture_packages';break
        if not new_ids:
            stop='missing_texture_packages_already_present_no_progress';break
        absent=[x for x in new_ids if x not in current]
        if absent:raise RuntimeError(f'FileHash-derived package ids absent from current packages.txt: {absent}')

        scan_names=set();family_infos={}
        for package_id in new_ids:
            names=current[package_id]
            located=sorted(n for n in names if n in locations)
            extra=sorted(n for n,r in locations.items() if r['package_id']==package_id and n not in names)
            if located==names and not extra:
                row['family_modes'][package_id]='validated_prior_exact_current_family_membership'
                family_infos[package_id]={n:locations[n] for n in names}
            else:
                row['family_modes'][package_id]='current_family_split_tar_scan'
                scan_names.update(names)
        scanned={};headers=0
        if scan_names:
            scanned,headers=archive.find(scan_names)
            missing=sorted(scan_names-set(scanned))
            if missing:raise RuntimeError(f'current texture dependency family members not found: {missing}')
        row['tar_headers_scanned']=headers

        for package_id in new_ids:
            for name in current[package_id]:
                if row['family_modes'][package_id]=='current_family_split_tar_scan':
                    info=scanned[name];off=int(info['data_offset']);size=int(info['size']);expected=None;source='current_split_tar_scan'
                else:
                    info=family_infos[package_id][name];off=int(info['data_offset']);size=int(info['size']);expected=info.get('sha256');source=info.get('source')
                dst=a.expansion_dir/name
                got=archive.copy_to(off,size,dst)
                if expected and got.lower()!=expected.lower():raise RuntimeError(f'{name}: SHA mismatch {got} != {expected}')
                member={'pass':i,'package_id':package_id,'name':name,'data_offset':off,'size':size,'sha256':got,
                        'expected_sha256':expected,'location_source':source,'family_mode':row['family_modes'][package_id],
                        'selection_basis':'d1_world_material_texture_export.missing_texture_package_ids'}
                recovered.append(member);row['recovered_members'].append(member);snapshots.append(dst.resolve())
        present_ids.update(new_ids)
    else:stop='max_passes_reached'

    if final_manifest is None:raise RuntimeError('no texture export pass ran')
    final_missing=final_manifest.get('missing_texture_package_ids') or {}
    closed=not final_missing and int(final_manifest.get('texture_errors') or 0)==0 and int(final_manifest.get('material_decode_errors') or 0)==0
    if a.out.exists():shutil.rmtree(a.out)
    last=a.work_dir/f'pass_{len(passes)-1:02d}'
    shutil.copytree(last,a.out)
    report={'schema_version':1,'status':'D1_WORLD_TEXTURE_DEPENDENCY_CLOSURE_COMPLETE' if closed else 'D1_WORLD_TEXTURE_DEPENDENCY_CLOSURE_PARTIAL',
            'stop_reason':stop,'initial_snapshot_count':len(initial),'final_snapshot_count':len(snapshots),
            'initial_package_ids':sorted({x for x in (pid(p.name) for p in initial) if x}),'final_package_ids':sorted(present_ids),
            'recovered_package_ids':sorted({r['package_id'] for r in recovered}),'recovered_member_count':len(recovered),'recovered_members':recovered,
            'provenance_sources':provenance,'passes':passes,'final_manifest_summary':{
                k:final_manifest.get(k) for k in ('visible_material_count','material_decode_errors','unique_texture_tags','decoded_texture_tags','texture_errors','png_outputs','missing_texture_package_ids')},
            'policy':'Package expansion is driven only by exact exporter-reported missing texture FileHash package IDs. Complete current family membership is verified before pinned offsets are reused; otherwise only that family is scanned. No visual or filename semantic guess is permitted.'}
    a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ('status','stop_reason','initial_snapshot_count','final_snapshot_count','recovered_package_ids','recovered_member_count','final_manifest_summary')},indent=2))
    return 0 if closed else 2

if __name__=='__main__':raise SystemExit(main())
