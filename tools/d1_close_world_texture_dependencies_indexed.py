#!/usr/bin/env python3
"""Close D1 material texture dependencies using the archive-wide package index.

This is the map-generic counterpart to the earlier Tower texture closure.  Given an
already recovered world/geometry package corpus and one or more visual-material
selectors, it repeatedly runs the exact material/texture exporter. Any
``missing_texture_package_ids`` are direct consequences of serialized texture
FileHashes. Those families are recovered by exact byte ranges from the global
Activity/package index, then extraction repeats until every referenced texture is
reconstructed.

There is no split-TAR header scan, map-specific catalog, filename semantic guess,
or hard-coded texture package family.
"""
from __future__ import annotations

import argparse,json,shutil,subprocess,sys
from pathlib import Path

HERE=Path(__file__).resolve().parent


def snaps(roots:list[Path])->list[Path]:
    out={}
    for root in roots:
        if not root.exists():continue
        for p in root.glob('*.pkg'):
            if p.is_file():out[p.name]=p.resolve()
    return [out[k] for k in sorted(out)]


def run_export(roots,runtime,selectors,outdir,stdout):
    if outdir.exists():shutil.rmtree(outdir)
    outdir.mkdir(parents=True,exist_ok=True)
    cmd=[sys.executable,str(HERE/'d1_world_material_texture_export.py')]
    for p in snaps(roots):cmd+=['--snapshot',str(p)]
    cmd+=['--runtime',str(runtime)]
    for p in selectors:cmd+=['--visual-json',str(p)]
    cmd+=['--out',str(outdir)]
    cp=subprocess.run(cmd,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);stdout.write_text(cp.stdout)
    mf=outdir/'material_texture_manifest.json'
    if not mf.exists():raise RuntimeError(f'texture exporter emitted no manifest rc={cp.returncode}; see {stdout}')
    return cp.returncode,json.loads(mf.read_text())


def recover(index,plist,ids,outdir,report,stdout):
    cmd=[sys.executable,str(HERE/'d1_recover_indexed_package_families.py'),'--index',str(index),'--package-list',str(plist),'--out-dir',str(outdir),'--report',str(report)]
    for p in sorted(ids):cmd+=['--package-id',p]
    cp=subprocess.run(cmd,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);stdout.write_text(cp.stdout)
    if cp.returncode:raise RuntimeError(f'indexed texture-family recovery failed rc={cp.returncode}; see {stdout}')
    return json.loads(report.read_text())


def main()->int:
    ap=argparse.ArgumentParser();ap.add_argument('--snapshot-dir',type=Path,action='append',required=True)
    ap.add_argument('--runtime',type=Path,required=True);ap.add_argument('--visual-json',type=Path,action='append',required=True)
    ap.add_argument('--index',type=Path,required=True);ap.add_argument('--package-list',type=Path,required=True)
    ap.add_argument('--expansion-dir',type=Path,required=True);ap.add_argument('--work-dir',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True);ap.add_argument('--report',type=Path,required=True);ap.add_argument('--max-passes',type=int,default=8);a=ap.parse_args()
    a.expansion_dir.mkdir(parents=True,exist_ok=True);a.work_dir.mkdir(parents=True,exist_ok=True)
    roots=[p.resolve() for p in a.snapshot_dir]+[a.expansion_dir.resolve()]
    recovered_ids=set();passes=[];final=None;stop=None
    for n in range(a.max_passes):
        passdir=a.work_dir/f'pass_{n:02d}';rc,m=run_export(roots,a.runtime.resolve(),[p.resolve() for p in a.visual_json],passdir,a.work_dir/f'pass_{n:02d}.stdout.txt');final=m
        missing={str(x).lower().removeprefix('0x').zfill(4) for x in (m.get('missing_texture_package_ids') or {})}
        new=missing-recovered_ids
        row={'pass':n,'export_returncode':rc,'snapshot_count':len(snaps(roots)),'visible_material_count':m.get('visible_material_count'),'material_decode_errors':m.get('material_decode_errors'),'unique_texture_tags':m.get('unique_texture_tags'),'decoded_texture_tags':m.get('decoded_texture_tags'),'texture_errors':m.get('texture_errors'),'missing_texture_package_ids':m.get('missing_texture_package_ids') or {},'new_package_ids':sorted(new)};passes.append(row)
        if not missing and int(m.get('texture_errors') or 0)==0 and int(m.get('material_decode_errors') or 0)==0:
            stop='closed_zero_missing_texture_dependencies';break
        if not new:
            stop='partial_no_new_texture_package_progress';break
        rr=recover(a.index,a.package_list,new,a.expansion_dir,a.work_dir/f'recovery_{n:02d}.json',a.work_dir/f'recovery_{n:02d}.stdout.txt')
        row['recovery_status']=rr.get('status');row['recovered_member_count']=rr.get('member_count');recovered_ids.update(new)
    else:stop='max_passes_reached'
    if final is None:raise RuntimeError('no export pass ran')
    last=a.work_dir/f'pass_{len(passes)-1:02d}'
    if a.out.exists():shutil.rmtree(a.out)
    shutil.copytree(last,a.out)
    closed=not (final.get('missing_texture_package_ids') or {}) and int(final.get('texture_errors') or 0)==0 and int(final.get('material_decode_errors') or 0)==0
    report={'schema_version':1,'status':'D1_INDEXED_WORLD_TEXTURE_DEPENDENCY_CLOSURE_COMPLETE' if closed else 'D1_INDEXED_WORLD_TEXTURE_DEPENDENCY_CLOSURE_PARTIAL','stop_reason':stop,'recovered_package_ids':sorted(recovered_ids),'recovered_package_family_count':len(recovered_ids),'passes':passes,'final_manifest_summary':{k:final.get(k) for k in ('visible_material_count','material_decode_errors','unique_texture_tags','decoded_texture_tags','texture_errors','png_outputs','missing_texture_package_ids')},'policy':'All recovered texture package IDs are emitted by exact serialized material texture FileHashes. Physical family ranges come from the exact archive-wide package index; no map-specific catalogs or TAR discovery scans are used.'}
    a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ('status','stop_reason','recovered_package_ids','final_manifest_summary')},indent=2));return 0 if closed else 2
if __name__=='__main__':raise SystemExit(main())
