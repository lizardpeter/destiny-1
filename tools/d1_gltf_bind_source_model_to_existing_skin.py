#!/usr/bin/env python3
"""Attach scene-reachable source mesh nodes to an already proven glTF skin.

Used after loss-preserving layer merge when an appended D1 component already
contains exact JOINTS_0/WEIGHTS_0 but intentionally carried no skeleton of its
own. The caller supplies the exact source model tag and existing skin index.

Only nodes reachable from the active glTF scene are eligible. Dormant serialized
LOD/pass nodes intentionally omitted from the source component's scene remain
untouched and cannot make the bind fail or become accidentally re-enabled.
"""
from __future__ import annotations

import argparse, json, re
from pathlib import Path
from pygltflib import GLTF2


def reachable_nodes(g: GLTF2) -> set[int]:
    if not g.scenes:
        raise ValueError('GLB has no scenes')
    si = int(g.scene or 0)
    if si < 0 or si >= len(g.scenes):
        raise ValueError(f'active scene {si} outside scene count {len(g.scenes)}')
    roots = list(g.scenes[si].nodes or [])
    seen: set[int] = set()
    stack = [int(x) for x in roots]
    while stack:
        ni = stack.pop()
        if ni in seen:
            continue
        if ni < 0 or ni >= len(g.nodes or []):
            raise ValueError(f'scene graph references invalid node {ni}')
        seen.add(ni)
        stack.extend(int(x) for x in (g.nodes[ni].children or []))
    return seen


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('input_glb',type=Path)
    ap.add_argument('--model',required=True)
    ap.add_argument('--skin-index',type=int,default=0)
    ap.add_argument('--expected-joints',type=int)
    ap.add_argument('--report',type=Path,required=True)
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args();tag=a.model.upper().removeprefix('0X')
    if not re.fullmatch(r'[0-9A-F]{8}',tag):raise ValueError('model must be 8 hex digits')

    g=GLTF2().load_binary(str(a.input_glb))
    if a.skin_index<0 or a.skin_index>=len(g.skins or []):raise ValueError('skin index outside GLB')
    skin=g.skins[a.skin_index];joint_count=len(skin.joints or [])
    if a.expected_joints is not None and joint_count!=a.expected_joints:raise ValueError(f'skin joint count {joint_count} != {a.expected_joints}')

    reachable=reachable_nodes(g)
    rows=[];dormant_matches=[]
    for ni,n in enumerate(g.nodes or []):
        if n.mesh is None:continue
        m=g.meshes[n.mesh];name=m.name or n.name or ''
        if tag not in name.upper():continue
        if ni not in reachable:
            dormant_matches.append({'node_index':ni,'mesh_index':n.mesh,'mesh_name':name})
            continue
        if len(m.primitives or [])!=1:raise ValueError(f'{name}: expected one primitive')
        p=m.primitives[0]
        if p.attributes.JOINTS_0 is None or p.attributes.WEIGHTS_0 is None:raise ValueError(f'{name}: source skin attributes absent')
        n.skin=a.skin_index
        rows.append({'node_index':ni,'mesh_index':n.mesh,'mesh_name':name})
    if not rows:raise ValueError(f'no scene-reachable mesh nodes matched source model {tag}')

    g.extras={**(g.extras or {}),'d1ExistingSkinBinding':{
        'sourceModel':tag,'skinIndex':a.skin_index,'skinJointCount':joint_count,
        'boundNodeCount':len(rows),'dormantMatchingNodeCount':len(dormant_matches),
        'policy':'Only active-scene-reachable source nodes with exact JOINTS_0/WEIGHTS_0 are connected to the existing proven skin. Dormant serialized LOD/pass nodes remain unreachable and untouched.'}}
    a.output.parent.mkdir(parents=True,exist_ok=True);g.save_binary(str(a.output))
    rep={'schema':'d1_gltf_bind_source_model_to_existing_skin/v2','input':str(a.input_glb),'output':str(a.output),'source_model':tag,
         'skin_index':a.skin_index,'skin_joint_count':joint_count,'reachable_node_count':len(reachable),'bound_node_count':len(rows),
         'dormant_matching_node_count':len(dormant_matches),'nodes':rows,'dormant_matching_nodes':dormant_matches,
         'policy':'Scene reachability is authoritative. Dormant serialized nodes are not rebound or re-enabled.'}
    a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(rep,indent=2)+'\n');print(json.dumps(rep,indent=2));return 0

if __name__=='__main__':raise SystemExit(main())
