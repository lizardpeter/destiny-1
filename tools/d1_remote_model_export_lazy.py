#!/usr/bin/env python3
"""Batch-export D1 s_entity_model geometry with lazy cross-package FileHash routing.

The historical remote model exporter materialized RemoteLogicalPackage views for
all supplied package families before exporting one model.  That is correct but too
expensive for the all-Guardian/all-character corpus.  This adapter preserves the
same validated d1_entity_model_export.export_model decoder while replacing its
hash map with an on-demand mapping:

  requested FileHash -> encoded Tiger package/index -> open only that package view

Vertex/index headers and payloads therefore pull additional package families only
when the exact serialized FileHash requires them.  No locality/name heuristic is
introduced.

It can consume d1_guardian_visual_export_plan/v1 directly and deterministic-shard
the unique model cache, or accept explicit --model hashes.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Mapping
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))

import d1_entity_model_export as core
from d1_investment_arrangement_probe import filehash_pkg_index
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_investment_parent_probe import RemoteLogicalPackage
from d1_split_tar_extract import SplitHttpTar


def norm(x:object)->str:return str(x).upper().removeprefix('0X').zfill(8)


class LazyHashMap(Mapping):
    def __init__(self,reader):self.reader=reader
    def __getitem__(self,key):
        x=self.reader.meta(norm(key))
        if x is None:raise KeyError(key)
        return x
    def get(self,key,default=None):
        x=self.reader.meta(norm(key));return default if x is None else x
    def __iter__(self):
        raise TypeError('lazy FileHash map is intentionally non-enumerable')
    def __len__(self):
        raise TypeError('lazy FileHash map has no materialized length')


class LazyFileHashReader:
    def __init__(self,arc,catalogs,runtime):
        self.arc=arc;self.catalogs=catalogs;self.runtime=runtime;self.views={};self._meta={}
        self.pkg=Path('remote_lazy_filehash_view.pkg');self.h={'platform':'PS4','pkg_id':-1}
        self.entries=[]  # never enumerated after core.byhash is patched below
    def view(self,pkg:int):
        if pkg not in self.catalogs:raise KeyError(f'package {pkg:04X} absent from supplied catalog')
        if pkg not in self.views:self.views[pkg]=RemoteLogicalPackage(self.arc,self.catalogs[pkg],self.runtime)
        return self.views[pkg]
    def meta(self,tag:str):
        tag=norm(tag)
        if tag in self._meta:return self._meta[tag]
        try:pkg,idx=filehash_pkg_index(int(tag,16))
        except Exception:return None
        if pkg not in self.catalogs:return None
        v=self.view(pkg)
        if idx>=len(v.entries):return None
        e=v.entries[idx]
        if norm(e['tag_hash'])!=tag:return None
        x=dict(e);x['_source_package_id']=pkg;x['_source_file_index']=int(e['index']);x['index']=int(tag,16)
        self._meta[tag]=x;return x
    def entry(self,synthetic_index:int)->bytes:
        tag=f'{int(synthetic_index)&0xffffffff:08X}';e=self.meta(tag)
        if e is None:raise KeyError(tag)
        return self.view(int(e['_source_package_id'])).entry(int(e['_source_file_index']))
    def available(self,synthetic_index:int)->bool:
        try:self.entry(synthetic_index);return True
        except (KeyError,FileNotFoundError):return False
    def byhash(self):return LazyHashMap(self)


def plan_models(doc:dict)->list[str]:
    if doc.get('schema')!='d1_guardian_visual_export_plan/v1':raise ValueError(f'unsupported plan schema {doc.get("schema")!r}')
    return sorted({norm(x['model_hash']) for x in doc.get('model_cache',[]) if x.get('model_hash')})


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--plan',type=Path)
    ap.add_argument('--model',action='append',default=[])
    ap.add_argument('--shard-index',type=int,default=0)
    ap.add_argument('--shard-size',type=int,default=50)
    ap.add_argument('--member-catalog',type=Path,action='append',required=True)
    ap.add_argument('--base-url',default='https://crypt.cohae.dev/destiny/ps4/packages/latest')
    ap.add_argument('--part-count',type=int,default=10)
    ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('--out-dir',type=Path,required=True)
    ap.add_argument('--report',type=Path,required=True)
    a=ap.parse_args()
    if a.shard_index<0 or a.shard_size<=0:raise ValueError('invalid shard')

    models=[]
    if a.plan:models.extend(plan_models(json.loads(a.plan.read_text())))
    models.extend(norm(x) for x in a.model)
    models=list(dict.fromkeys(models))
    if not models:raise SystemExit('no models selected')
    total=len(models);start=a.shard_index*a.shard_size;end=min(total,start+a.shard_size)
    selected=models[start:end]
    if not selected:raise ValueError(f'shard {a.shard_index} empty for {total} models at size {a.shard_size}')

    catalogs=load_catalogs(a.member_catalog)
    arc=SplitHttpTar([f"{a.base_url.rstrip('/')}/packages.tar.{i:03d}" for i in range(1,a.part_count+1)],retries=6,timeout=90)
    rr=LazyFileHashReader(arc,catalogs,a.runtime)
    old_byhash=core.byhash;core.byhash=lambda r:r.byhash() if hasattr(r,'byhash') else old_byhash(r)
    a.out_dir.mkdir(parents=True,exist_ok=True)
    rows=[];errors=[]
    try:
        for n,h in enumerate(selected,1):
            try:
                glb=a.out_dir/f'{h}.glb';jp=a.out_dir/f'{h}.json';rep=core.export_model(rr,h,glb,jp)
                rows.append({'model_hash':h,'glb':str(glb),'report':str(jp),'glb_bytes':glb.stat().st_size,
                             'mesh_count':rep['mesh_count'],'geometry_count':rep['geometry_count'],'triangle_count':rep['triangle_count'],
                             'package_families_touched':[f'{x:04X}' for x in sorted(rr.views)]})
            except Exception as ex:errors.append({'model_hash':h,'error':repr(ex)})
            print(f'MODELS {n}/{len(selected)} ok={len(rows)} errors={len(errors)} package_views={len(rr.views)}',flush=True)
    finally:core.byhash=old_byhash
    out={'schema':'d1_remote_model_export_lazy/v1','status':'D1_REMOTE_MODEL_EXPORT_LAZY_COMPLETE' if not errors else 'D1_REMOTE_MODEL_EXPORT_LAZY_PARTIAL',
         'total_plan_model_count':total,'shard_index':a.shard_index,'shard_size':a.shard_size,'shard_start':start,'shard_end_exclusive':end,
         'requested_model_count':len(selected),'exported_model_count':len(rows),'error_count':len(errors),
         'package_family_view_count':len(rr.views),'package_families_touched':[f'{x:04X}' for x in sorted(rr.views)],
         'models':rows,'errors':errors,
         'policy':'All cross-package resolution is driven by exact encoded Tiger FileHash package/index. Package views are opened lazily only when a serialized model/vertex/index dependency requires them; names and adjacency are not routing inputs.'}
    a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ('status','total_plan_model_count','shard_index','requested_model_count','exported_model_count','error_count','package_family_view_count','package_families_touched')},indent=2))
    return 0 if not errors else 2

if __name__=='__main__':raise SystemExit(main())
