#!/usr/bin/env python3
"""Read complete exact D1 skeleton resources from remote logical package families.

Unlike the earlier census-oriented probe, this preserves hierarchy, both transform
arrays, RangeIndexMap and InnerIndexMap so a candidate can be identity-compared
to Bungie's published D1 player skeleton without compatibility assumptions.
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
    ap.add_argument('--base-url',required=True); ap.add_argument('--part-count',type=int,default=10)
    ap.add_argument('--runtime',type=Path,required=True); ap.add_argument('--member',action='append',type=parse_member,required=True)
    ap.add_argument('--tag-hash',action='append',required=True); ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args()
    if any(m.pkg_id!=a.package_id for m in a.member): raise SystemExit('member package mismatch')
    members={m.patch_id:m for m in a.member}
    arc=SplitHttpTar([f"{a.base_url.rstrip('/')}/packages.tar.{i:03d}" for i in range(1,a.part_count+1)],retries=6,timeout=90)
    r=RemoteLogicalPackage(arc,members,a.runtime); by={e['tag_hash'].upper():e for e in r.entries}
    rows=[]
    for raw in a.tag_hash:
        h=raw.removeprefix('0x').removeprefix('0X').upper(); e=by.get(h)
        if e is None:
            rows.append({'tag_hash':h,'missing':True}); continue
        try:
            b=r.entry(e['index']); sk=parse_skeleton_resource(b); info=sk['skeleton_info']
            rows.append({
                'tag_hash':h,'entry_index':e['index'],'size':e['file_size'],'reference':e['reference'].upper(),
                'node_hierarchy':info['node_hierarchy'],
                'bone_hashes':[x['node_hash'] for x in info.get('bones',[])],
                'default_object_space_transforms':info['default_object_space_transforms'],
                'default_inverse_object_space_transforms':info['default_inverse_object_space_transforms'],
                'range_index_map':info['range_index_map'],'inner_index_map':info['inner_index_map'],
                'count_invariants':info['count_invariants'],
            })
        except Exception as ex:
            rows.append({'tag_hash':h,'entry_index':e['index'],'reference':e['reference'].upper(),'error':repr(ex)})
    rep={'schema':'d1_remote_skeleton_exact_probe/v1','package_id':f'{a.package_id:04X}','logical_view':r.view.name,'skeletons':rows,
         'policy':'All hierarchy, transform and index-map values are decoded from the exact retail D1 EntitySkeleton resource. No candidate is promoted by node count or compatibility.'}
    a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(rep,indent=2)+'\n')
    for x in rows:
        print(x['tag_hash'],'nodes',(x.get('node_hierarchy') or {}).get('count'),'range',(x.get('range_index_map') or {}).get('count'),
              'inner',(x.get('inner_index_map') or {}).get('count'),'error',x.get('error'),'missing',x.get('missing'))
    return 0

if __name__=='__main__': raise SystemExit(main())
