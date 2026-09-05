#!/usr/bin/env python3
"""Export exact D1 PS4 textures through verified remote package catalogs.

This adapts the validated d1_texture_export implementation to the same
MultiPackageReader used by Guardian geometry. Requested texture headers are
resolved by exact Tiger FileHash across verified logical package families, and
the existing texture exporter follows their serialized streamed/backing chain.

Before bulk export, every requested header/stream/backing chain is read once and
recorded in a fail-closed preflight report. This makes an incomplete or wrong
physical patch-generation catalog identify the exact FileHash/package stage
instead of failing opaquely inside a large texture batch.

It can read texture hashes directly from a d1_remote_texture_plate_probe report.
No neighboring-package or filename inference is performed.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))

from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_investment_parent_probe import RemoteLogicalPackage
from d1_remote_model_export import MultiPackageReader
from d1_split_tar_extract import SplitHttpTar
from d1_texture_export import export_reader


def norm(v:str)->str:
    v=v.upper().removeprefix('0X').zfill(8);int(v,16);return v


def entry_desc(e:dict|None)->dict|None:
    if e is None:return None
    return {
        'tag_hash':e['tag_hash'].upper(),
        'reference':e['reference'].upper(),
        'type':e['type'],'subtype':e['subtype'],'declared_file_size':e['file_size'],
        'source_package_id':f"{int(e.get('_source_package_id')):04X}" if e.get('_source_package_id') is not None else None,
        'source_file_index':e.get('_source_file_index'),
        'synthetic_index':e['index'],
    }


def preflight(r:MultiPackageReader,by:dict[str,dict],wanted:list[str])->dict:
    rows=[];failures=[]
    for h in sorted(wanted):
        he=by[h];row={'header':entry_desc(he),'stages':[]}
        try:
            hb=r.entry(he['index'])
            row['stages'].append({'stage':'header','entry':entry_desc(he),'bytes':len(hb),'ok':True})
        except Exception as ex:
            row['stages'].append({'stage':'header','entry':entry_desc(he),'ok':False,'error':repr(ex)})
            row['error_stage']='header';row['error']=repr(ex);failures.append(row);rows.append(row);continue

        mid=by.get(he['reference'].upper())
        if mid is None:
            row['error_stage']='stream';row['error']=f"stream {he['reference'].upper()} absent from catalog views"
            row['stages'].append({'stage':'stream','entry':None,'tag_hash':he['reference'].upper(),'ok':False,'error':row['error']})
            failures.append(row);rows.append(row);continue
        try:
            mb=r.entry(mid['index'])
            row['stages'].append({'stage':'stream','entry':entry_desc(mid),'bytes':len(mb),'ok':True})
        except Exception as ex:
            row['stages'].append({'stage':'stream','entry':entry_desc(mid),'ok':False,'error':repr(ex)})
            row['error_stage']='stream';row['error']=repr(ex);failures.append(row);rows.append(row);continue

        nxt=mid['reference'].upper();back=by.get(nxt)
        if back is None:
            # d1_texture_export intentionally accepts the stream itself as the
            # backing when there is no second serialized tag hop.
            back=mid
        try:
            bb=r.entry(back['index'])
            row['stages'].append({'stage':'backing','entry':entry_desc(back),'bytes':len(bb),'ok':True})
        except Exception as ex:
            row['stages'].append({'stage':'backing','entry':entry_desc(back),'ok':False,'error':repr(ex)})
            row['error_stage']='backing';row['error']=repr(ex);failures.append(row);rows.append(row);continue
        rows.append(row)
    return {
        'schema':'d1_remote_texture_preflight/v1','requested_count':len(wanted),
        'success_count':len(rows)-len(failures),'failure_count':len(failures),
        'rows':rows,'failures':failures,
        'policy':'Every requested texture header and its exact serialized stream/backing FileHash chain is physically read before bulk export; exceptions retain exact source package and file index.'
    }


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--plate-report',type=Path)
    ap.add_argument('--tag-hash',action='append',default=[])
    ap.add_argument('--member-catalog',type=Path,action='append',required=True)
    ap.add_argument('--base-url',required=True);ap.add_argument('--part-count',type=int,default=10)
    ap.add_argument('--runtime',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()

    wanted=[]
    if a.plate_report:
        p=json.loads(a.plate_report.read_text())
        for h in p.get('source_texture_hashes',[]):
            h=norm(h)
            if h not in wanted:wanted.append(h)
    for h in a.tag_hash:
        h=norm(h)
        if h not in wanted:wanted.append(h)
    if not wanted:raise SystemExit('no texture hashes requested')

    catalogs=load_catalogs(a.member_catalog);base=a.base_url.rstrip('/')
    arc=SplitHttpTar([f'{base}/packages.tar.{i:03d}' for i in range(1,a.part_count+1)],retries=6,timeout=90)
    views={pkg:RemoteLogicalPackage(arc,fam,a.runtime) for pkg,fam in sorted(catalogs.items())}
    r=MultiPackageReader(views)
    by={e['tag_hash'].upper():e for e in r.entries}
    missing=[h for h in wanted if h not in by]
    if missing:raise SystemExit(f'requested texture headers absent from supplied catalogs: {missing}')

    a.out.mkdir(parents=True,exist_ok=True)
    pf=preflight(r,by,wanted)
    (a.out/'remote_texture_preflight.json').write_text(json.dumps(pf,indent=2)+'\n')
    print('PREFLIGHT',pf['success_count'],'/',pf['requested_count'],'success; failures',pf['failure_count'],flush=True)
    for f in pf['failures']:
        h=f['header']['tag_hash'];pkg=f['header']['source_package_id'];idx=f['header']['source_file_index']
        print('PREFLIGHT_FAILURE',h,'header_pkg',pkg,'header_index',idx,'stage',f['error_stage'],f['error'],flush=True)
        for s in f['stages']:
            e=s.get('entry') or {}
            print(' ',s['stage'],e.get('tag_hash'),e.get('source_package_id'),e.get('source_file_index'),'ok',s['ok'],s.get('error',''),flush=True)
    if pf['failure_count']:
        raise SystemExit(f"remote texture preflight failed for {pf['failure_count']}/{pf['requested_count']} requested textures")

    rep=export_reader(r,a.out,tag_hashes=wanted,dependencies=[])
    manifest={
        'schema':'d1_remote_texture_export/v1',
        'requested_texture_hashes':wanted,
        'requested_count':len(wanted),
        'resolved_count':rep.get('texture_count'),
        'missing_requested':rep.get('missing_requested'),
        'textures':rep.get('textures',[]),
        'catalog_package_ids':[f'{x:04X}' for x in sorted(catalogs)],
        'preflight':'remote_texture_preflight.json',
        'policy':'Requested texture FileHashes and all serialized backing references are resolved only through exact hashes across verified logical package catalogs.',
    }
    (a.out/'remote_texture_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({k:v for k,v in manifest.items() if k!='textures'},indent=2))
    for x in manifest['textures']:
        print(x.get('header'),'->',x.get('png'),'owner',x.get('owner_package'),'backing',x.get('backing'))
    if manifest['missing_requested'] or manifest['resolved_count']!=len(wanted):
        raise SystemExit(f"texture export incomplete: {manifest['resolved_count']}/{len(wanted)}")
    bad=[x for x in manifest['textures'] if not x.get('png') or x.get('png_error')]
    if bad:raise SystemExit(f'{len(bad)} requested textures did not produce PNGs')
    return 0

if __name__=='__main__':raise SystemExit(main())
