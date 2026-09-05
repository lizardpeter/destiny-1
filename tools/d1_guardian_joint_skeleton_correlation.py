#!/usr/bin/env python3
"""Correlate exact D1 Guardian rigid skin indices with one candidate skeleton.

Inputs:
  * d1_playable_guardian_entity_resource_resolve/v1 report;
  * exact masculine/feminine body role;
  * verified remote package catalogs for the selected s_entity_model and stream
    FileHashes;
  * one local, byte-validated D1 skeleton resource.

Only meshes with old_weights == FFFFFFFF are interpreted, using the retail-proven
D1 primary-stream int16 lane-3 rigid joint index. Weighted meshes are reported but
never guessed. Raw joint values are mapped directly to candidate skeleton node
indices solely for correlation; a good anatomical match is evidence, not an owner
edge by itself.
"""
from __future__ import annotations

import argparse
import collections
import io
import json
import struct
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))

from d1_entity_model_probe import parse_model
from d1_investment_arrangement_probe import filehash_pkg_index
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_investment_parent_probe import RemoteLogicalPackage
from d1_remote_model_export import MultiPackageReader, models_from_report
from d1_skeleton_probe import parse_skeleton_resource
from d1_entry_extract import EntryReader
from d1_split_tar_extract import SplitHttpTar


def get_multi_entry(multi: MultiPackageReader, tag: str):
    t=tag.upper()
    for e in multi.entries:
        if e['tag_hash'].upper()==t:
            return e,multi.entry(e['index'])
    raise KeyError(t)


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--report',type=Path,required=True)
    ap.add_argument('--body-role',choices=('masculine','feminine'),required=True)
    ap.add_argument('--member-catalog',type=Path,action='append',required=True)
    ap.add_argument('--base-url',required=True)
    ap.add_argument('--part-count',type=int,default=10)
    ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('--skeleton-pkg',type=Path,required=True)
    ap.add_argument('--skeleton',required=True)
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args()

    source=json.loads(a.report.read_text())
    selected=models_from_report(source,a.body_role)
    if not selected: raise SystemExit('no selected models')

    catalogs=load_catalogs(a.member_catalog)
    base=a.base_url.rstrip('/')
    arc=SplitHttpTar([f'{base}/packages.tar.{i:03d}' for i in range(1,a.part_count+1)],retries=6,timeout=90)
    views={pkg:RemoteLogicalPackage(arc,fam,a.runtime) for pkg,fam in sorted(catalogs.items())}
    multi=MultiPackageReader(views)
    by={e['tag_hash'].upper():e for e in multi.entries}

    sr=EntryReader(a.skeleton_pkg,a.runtime)
    se=next(e for e in sr.entries if e['tag_hash'].upper()==a.skeleton.upper().removeprefix('0X'))
    sk=parse_skeleton_resource(sr.entry(se['index']))
    bones=sk['skeleton_info']['bones']
    bone_hashes=[x['node_hash'] for x in bones]

    all_dist=collections.Counter(); rows=[]; weighted=0
    for sel in selected:
        tag=sel['tag_hash'].upper(); e,b=get_multi_entry(multi,tag)
        model=parse_model(b,'PS4')
        mdist=collections.Counter(); meshes=[]
        for mi,m in enumerate(model['meshes']):
            row={'mesh_index':mi,'old_weights':m['old_weights']}
            if m['old_weights'].upper()!='FFFFFFFF':
                row['representation']='weighted_unresolved'; weighted+=1; meshes.append(row); continue
            vh=by.get(m['vertices1'].upper())
            if not vh:
                row.update({'representation':'rigid','error':'primary vertex header unavailable'});meshes.append(row);continue
            vp=by.get(vh['reference'].upper())
            if not vp:
                row.update({'representation':'rigid','error':f"payload {vh['reference']} unavailable"});meshes.append(row);continue
            hb=multi.entry(vh['index']); pb=multi.entry(vp['index'])
            stride=struct.unpack_from('<h',hb,4)[0]
            if stride<8 or stride>128 or stride%2 or len(pb)%stride:
                raise RuntimeError(f'{tag} mesh {mi}: invalid primary stream stride/payload {stride}/{len(pb)}')
            vals=[struct.unpack_from('<h',pb,o+6)[0] for o in range(0,len(pb),stride)]
            dist=collections.Counter(vals); mdist.update(vals); all_dist.update(vals)
            mapped=[]
            for j,c in sorted(dist.items()):
                mapped.append({'joint_index':j,'vertex_count':c,
                               'candidate_bone_hash':bone_hashes[j] if 0<=j<len(bone_hashes) else None,
                               'candidate_node_in_range':0<=j<len(bone_hashes)})
            row.update({'representation':'rigid_primary_stream_lane3','stride':stride,'vertex_count':len(vals),
                        'joint_distribution':{str(k):v for k,v in sorted(dist.items())},
                        'candidate_skeleton_mapping':mapped})
            meshes.append(row)
        rows.append({**sel,'model_entry_index':e['index'],'mesh_count':model['mesh_count'],
                     'rigid_joint_distribution':{str(k):v for k,v in sorted(mdist.items())},
                     'rigid_joint_indices':sorted(mdist),'meshes':meshes})

    report={'schema':'d1_guardian_joint_skeleton_correlation/v1','body_role':a.body_role,
            'candidate_skeleton':a.skeleton.upper(),'candidate_skeleton_node_count':len(bones),
            'candidate_bone_hashes':bone_hashes,'selected_model_count':len(rows),
            'weighted_mesh_count':weighted,'aggregate_rigid_joint_distribution':{str(k):v for k,v in sorted(all_dist.items())},
            'aggregate_rigid_joint_indices':sorted(all_dist),'models':rows,
            'policy':'Only old_weights==FFFFFFFF meshes use the retail-proven lane-3 rigid joint index. Mapping those integer values directly to candidate skeleton nodes is a correlation test only; weighted meshes and semantic ownership remain unresolved unless separately proven.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n')
    print('candidate',a.skeleton.upper(),'nodes',len(bones),'aggregate joints',sorted(all_dist),'weighted meshes',weighted)
    for x in rows:
        name=(x.get('examples') or [{}])[0].get('name')
        print(name,x['tag_hash'],'joints',x['rigid_joint_indices'])
        for m in x['meshes']:
            if m.get('candidate_skeleton_mapping'):
                print(' mesh',m['mesh_index'],[(z['joint_index'],z['candidate_bone_hash'],z['vertex_count']) for z in m['candidate_skeleton_mapping']])
    return 0

if __name__=='__main__': raise SystemExit(main())
