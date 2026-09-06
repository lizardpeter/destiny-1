#!/usr/bin/env python3
"""Decode one exact D1 PS4 skeleton EntityResource through verified remote catalogs."""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_model_tgxm_signature_match import LazyExactHashResolver
from d1_skeleton_probe import parse_skeleton_resource
from d1_split_tar_extract import SplitHttpTar

def norm(s:str)->str:return s.upper().removeprefix('0X').zfill(8)

def main()->int:
    ap=argparse.ArgumentParser();ap.add_argument('--skeleton-resource',required=True)
    ap.add_argument('--member-catalog',type=Path,action='append',required=True)
    ap.add_argument('--base-url',required=True);ap.add_argument('--part-count',type=int,default=10)
    ap.add_argument('--runtime',type=Path,required=True);ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args();h=norm(a.skeleton_resource)
    cats=load_catalogs(a.member_catalog);arc=SplitHttpTar([f"{a.base_url.rstrip('/')}/packages.tar.{i:03d}" for i in range(1,a.part_count+1)],retries=6,timeout=90)
    resolver=LazyExactHashResolver(arc,cats,a.runtime);_v,e,b=resolver.bytes(h)
    d=parse_skeleton_resource(b);info=d['skeleton_info'];bones=info['bones']
    rep={'schema':'d1_remote_skeleton_resource_probe/v1','skeleton_resource_tag_hash':h,'entry_index':int(e['index']),'entry_size':int(e['file_size']),
         'node_count':info['node_hierarchy']['count'],'default_transform_count':info['default_object_space_transforms']['count'],
         'inverse_transform_count':info['default_inverse_object_space_transforms']['count'],'range_index_count':info['range_index_map']['count'],
         'inner_index_count':info['inner_index_map']['count'],'bone_hashes':[x['node_hash'] for x in bones],
         'parent_indices':[x['parent_node_index'] for x in bones],'bones':bones,'entity_resource':d['entity_resource'],
         'policy':'Hierarchy and transforms are decoded from the validated D1 skeleton EntityResource 808006BD -> 8080049A layout. No skeleton identity is inferred beyond the requested exact FileHash.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(rep,indent=2)+'\n')
    print('SKELETON_RESOURCE',h,'NODES',rep['node_count'],'HASHES',rep['bone_hashes'])
    return 0
if __name__=='__main__':raise SystemExit(main())
