#!/usr/bin/env python3
"""Read exact D1 skeleton resources from a remote logical package family.

This is the sparse HTTP-range counterpart of d1_skeleton_probe.py and preserves
node hierarchy, object-space transforms, RangeIndexMap and InnerIndexMap for a
caller-supplied skeleton FileHash/TagHash.
"""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from d1_remote_investment_parent_probe import RemoteLogicalPackage,parse_member
from d1_split_tar_extract import SplitHttpTar
from d1_skeleton_probe import parse_skeleton_resource


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--package-id',type=lambda x:int(x,0),required=True)
    ap.add_argument('--base-url',required=True);ap.add_argument('--part-count',type=int,default=10)
    ap.add_argument('--runtime',type=Path,required=True);ap.add_argument('--member',action='append',type=parse_member,required=True)
    ap.add_argument('--tag-hash',action='append',required=True);ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args();members={m.patch_id:m for m in a.member}
    if any(m.pkg_id!=a.package_id for m in a.member):raise SystemExit('member package mismatch')
    arc=SplitHttpTar([f"{a.base_url.rstrip('/')}/packages.tar.{i:03d}" for i in range(1,a.part_count+1)],retries=6,timeout=90)
    r=RemoteLogicalPackage(arc,members,a.runtime);by={e['tag_hash'].upper():e for e in r.entries}
    rows=[]
    for raw in a.tag_hash:
        h=raw.removeprefix('0x').removeprefix('0X').upper();e=by.get(h)
        if not e:
            rows.append({'tag_hash':h,'missing':True});continue
        try:
            b=r.entry(e['index']);sk=parse_skeleton_resource(b);info=sk['skeleton_info']
            rows.append({'tag_hash':h,'entry_index':e['index'],'size':e['file_size'],
                         'node_count':info['node_hierarchy']['count'],
                         'node_hierarchy':info['node_hierarchy']['items'],
                         'bone_hashes':[x['node_hash'] for x in info.get('bones',[])],
                         'range_index_map':info['range_index_map'],
                         'inner_index_map':info['inner_index_map'],
                         'count_invariants':info['count_invariants']})
        except Exception as ex:rows.append({'tag_hash':h,'entry_index':e['index'],'error':repr(ex)})
    rep={'schema':'d1_remote_skeleton_probe/v1','package_id':f'{a.package_id:04X}','logical_view':r.view.name,'skeletons':rows}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(rep,indent=2)+'\n')
    print(json.dumps([{'tag_hash':x['tag_hash'],'node_count':x.get('node_count'),'range_count':(x.get('range_index_map') or {}).get('count'),'inner_count':(x.get('inner_index_map') or {}).get('count'),'error':x.get('error')} for x in rows],indent=2))
    return 0
if __name__=='__main__':raise SystemExit(main())
