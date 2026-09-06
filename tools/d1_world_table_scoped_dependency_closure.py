#!/usr/bin/env python3
"""Close dependencies needed to validate a D1 world's table-scoped common layer.

The source-driven static target plan identifies the SStaticMapData carriers. Their
serialized decal/common records can be parsed even when referenced EntityModel or
occlusion resources are not yet present. This closure therefore:

1. validates every planned table-scoped and baked control SStaticMapData;
2. harvests exact serialized occlusion, direct-D1-child and EntityModel TagHashes;
3. derives only those FileHash package IDs;
4. recovers the exact current package families through the archive-wide index;
5. reruns until ``d1_world_table_scoped_decal_census`` is complete.

This closes *identity/structural* dependencies for the common layer. EntityModel
vertex/material/texture dependencies are intentionally a later geometry stage.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from d1_world_activity_manifest_dependency_plan import filehash_package_id
from d1_world_static_map_decal_validate import validate_static_map
from d1_tower_map_schema_validate import Corpus

NULLS={'00000000','FFFFFFFF'}
PKG_RX=re.compile(r'_([0-9A-Fa-f]{4})_[0-9]+\.pkg$',re.I)


def norm(x): return str(x).upper().removeprefix('0X').zfill(8)
def pid_hash(h): return f'{filehash_package_id(norm(h)):04x}'
def pid_name(name):
    m=PKG_RX.search(Path(name).name)
    return m.group(1).lower() if m else None

def snapshots(root:Path): return sorted(p.resolve() for p in root.glob('*.pkg') if p.is_file())

def recover(index:Path,plist:Path,pkgdir:Path,required:set[str],have:set[str],work:Path,n:int)->list[str]:
    new=sorted({x.lower().zfill(4) for x in required}-have)
    if not new:return []
    report=work/f'recovery_{n:02d}.json';stdout=work/f'recovery_{n:02d}.stdout.txt'
    cmd=[sys.executable,str(HERE/'d1_recover_indexed_package_families.py'),'--index',str(index),'--package-list',str(plist),'--out-dir',str(pkgdir),'--report',str(report)]
    for p in new:cmd+=['--package-id',p]
    cp=subprocess.run(cmd,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);stdout.write_text(cp.stdout)
    if cp.returncode:raise RuntimeError(f'indexed recovery failed rc={cp.returncode}; see {stdout}')
    have.update(new);return new

def run_census(pkgdir:Path,runtime:Path,plan:Path,out:Path,validation:Path,stdout:Path)->int:
    cmd=[sys.executable,str(HERE/'d1_world_table_scoped_decal_census.py')]
    for p in snapshots(pkgdir):cmd+=['--snapshot',str(p)]
    cmd+=['--runtime',str(runtime),'--target-plan',str(plan),'--out',str(out),'--validation-dir',str(validation)]
    cp=subprocess.run(cmd,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);stdout.write_text(cp.stdout)
    if not out.exists():raise RuntimeError(f'common census emitted no JSON; see {stdout}')
    return cp.returncode

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--index',type=Path,required=True);ap.add_argument('--package-list',type=Path,required=True)
    ap.add_argument('--target-plan',type=Path,required=True);ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('--package-dir',type=Path,required=True);ap.add_argument('--work-dir',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True);ap.add_argument('--report',type=Path,required=True)
    ap.add_argument('--max-passes',type=int,default=8);a=ap.parse_args()
    plan=json.loads(a.target_plan.read_text())
    if plan.get('status')!='D1_WORLD_STATIC_MAP_TARGET_PLAN_COMPLETE':raise SystemExit('target plan incomplete')
    targets=list(plan.get('targets',[]));a.package_dir.mkdir(parents=True,exist_ok=True);a.work_dir.mkdir(parents=True,exist_ok=True)
    have={p for p in (pid_name(x.name) for x in snapshots(a.package_dir)) if p};required=set(have);passes=[];recovery_no=0;final=None;stop=None
    for t in targets:
        h=norm(t.get('static_map_data'))
        if h not in NULLS:required.add(pid_hash(h))
    added=recover(a.index,a.package_list,a.package_dir,required,have,a.work_dir,recovery_no);recovery_no+=int(bool(added))

    for n in range(a.max_passes):
        c=Corpus(snapshots(a.package_dir),a.runtime.resolve());deps=[];before=set(required)
        for i,t in enumerate(targets):
            sm=norm(t.get('static_map_data'));r=validate_static_map(c,sm)
            row={'target_index':i,'role':t.get('role'),'static_map_data':sm,'validation_ok':r.get('ok'),'discovered':[]}
            occ=(r.get('occlusion_bounds') or {}).get('hash')
            if occ and norm(occ) not in NULLS:
                h=norm(occ);required.add(pid_hash(h));row['discovered'].append({'kind':'occlusion_bounds','hash':h,'package_id':pid_hash(h)})
            raw=r.get('d1_static_map_raw')
            if raw and norm(raw) not in NULLS:
                h=norm(raw);required.add(pid_hash(h));row['discovered'].append({'kind':'d1_static_map','hash':h,'package_id':pid_hash(h)})
            for d in r.get('decals',[]):
                for m in d.get('models',[]):
                    h=norm(m.get('hash'))
                    if h in NULLS:continue
                    required.add(pid_hash(h));row['discovered'].append({'kind':'entity_model','hash':h,'package_id':pid_hash(h),'reference_matches':m.get('reference_matches')})
            deps.append(row)
        new=recover(a.index,a.package_list,a.package_dir,required,have,a.work_dir,recovery_no);recovery_no+=int(bool(new))
        census=a.work_dir/f'census_{n:02d}.json';validation=a.work_dir/f'validation_{n:02d}';stdout=a.work_dir/f'census_{n:02d}.stdout.txt'
        rc=run_census(a.package_dir,a.runtime,a.target_plan,census,validation,stdout);d=json.loads(census.read_text());final=d
        passes.append({'pass':n,'new_package_ids':new,'new_required_package_ids':sorted(required-before),'dependencies':deps,'census_returncode':rc,'census_status':d.get('status'),'violations':d.get('violations',[]),'table_scoped_records':d.get('table_scoped_materialized_record_count'),'export_ready_records':d.get('table_scoped_export_ready_singleton_records'),'unique_entity_models':d.get('table_scoped_unique_entity_models')})
        if d.get('status')=='D1_WORLD_TABLE_SCOPED_DECAL_CENSUS_COMPLETE':stop='closed_table_scoped_dependency_census';break
        if not (new or required-before):stop='partial_no_dependency_progress';break
    else:stop='max_passes_reached'
    if final is None:raise RuntimeError('census never ran')
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(final,indent=2)+'\n')
    closed=final.get('status')=='D1_WORLD_TABLE_SCOPED_DECAL_CENSUS_COMPLETE'
    report={'schema_version':1,'status':'D1_WORLD_TABLE_SCOPED_DEPENDENCY_CLOSURE_COMPLETE' if closed else 'D1_WORLD_TABLE_SCOPED_DEPENDENCY_CLOSURE_PARTIAL','stop_reason':stop,'target_count':len(targets),'final_package_ids':sorted(have),'required_package_ids':sorted(required),'final_census_summary':{k:final.get(k) for k in ('status','target_count','validated_target_count','table_scoped_target_count','table_scoped_decal_records','table_scoped_unique_entity_models','table_scoped_materialized_record_count','table_scoped_export_ready_singleton_records','baked_target_count','violations')},'passes':passes,'policy':'Only TagHashes serialized inside source-driven SStaticMapData targets produce package dependencies. This stage closes common-layer identity/structure, not EntityModel geometry or shader semantics.'}
    a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ('status','stop_reason','final_package_ids','final_census_summary')},indent=2));return 0 if closed else 2
if __name__=='__main__':raise SystemExit(main())
