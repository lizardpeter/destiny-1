#!/usr/bin/env python3
"""Audit D1 Guardian source joint indices against exact named skeleton semantics.

This exists because numeric range validation (e.g. `joint < 67`) is not a semantic
validation.  Guardian source vertices can contain an in-range integer whose bone at
the same slot is a completely different bone in another retail skeleton.

Inputs:
- exact source-decoded inline skin reports (`d1_guardian_inline_skin_probe/v1`)
- Bungie's exact published 72-node D1 player skeleton JSON
- one exact retail skeleton report (`d1_remote_skeleton_exact_probe/v1`) and tag

The report aggregates every used source joint by model and compares:
1. the bone name/hash at that raw index in Bungie's published player skeleton,
2. the bone hash at that same integer index in the candidate retail skeleton,
3. where the published bone hash occurs in the candidate, if it occurs at all,
4. default object-space SRT differences at the same integer index.

No remap is invented.  A hash-based candidate index is reported only as evidence;
it is not automatically applied to mesh data.
"""
from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path
from typing import Any


def hex32(v: Any) -> str | None:
    if v is None:
        return None
    try:
        return f"{int(v) & 0xffffffff:08X}"
    except Exception:
        return None


def load_published(path: Path) -> dict:
    obj=json.loads(path.read_text(encoding='utf-8-sig'))
    d=obj.get('definition',obj)
    nodes=[]
    for i,n in enumerate(d['nodes']):
        nm=n.get('name') or {}
        nodes.append({
            'index':i,
            'name':nm.get('string') if isinstance(nm,dict) else str(nm),
            'node_hash':hex32(nm.get('hash')) if isinstance(nm,dict) else None,
            'parent_node_index':int(n.get('parent_node_index',-1)),
        })
    return {
        'nodes':nodes,
        'default_object_space_transforms':d.get('default_object_space_transforms',[]),
        'default_inverse_object_space_transforms':d.get('default_inverse_object_space_transforms',[]),
    }


def load_retail(path: Path, tag: str) -> dict:
    d=json.loads(path.read_text())
    wanted=tag.removeprefix('0x').removeprefix('0X').upper()
    for x in d.get('skeletons',[]):
        if x.get('tag_hash','').upper()==wanted:
            if x.get('error') or x.get('missing'):
                raise ValueError(f'{wanted} is not a clean retail skeleton row: {x}')
            return x
    raise KeyError(f'{wanted} absent from {path}')


def srt(v: Any) -> tuple[list[float],list[float]] | None:
    if not isinstance(v,dict): return None
    r=v.get('r',v.get('rotation'))
    ts=v.get('ts',v.get('translation_scale_raw'))
    if ts is None:
        t=v.get('translation'); s=v.get('scale')
        if isinstance(t,list) and len(t)>=3 and s is not None:
            ts=[t[0],t[1],t[2],s]
    if not (isinstance(r,list) and len(r)>=4 and isinstance(ts,list) and len(ts)>=4):
        return None
    return ([float(x) for x in r[:4]],[float(x) for x in ts[:4]])


def srt_error(a: Any,b: Any) -> dict | None:
    aa=srt(a); bb=srt(b)
    if aa is None or bb is None: return None
    # q and -q represent the same orientation.
    qr=min(max(abs(x-y) for x,y in zip(aa[0],bb[0])),
           max(abs(x+y) for x,y in zip(aa[0],bb[0])))
    ts=max(abs(x-y) for x,y in zip(aa[1],bb[1]))
    return {'rotation_max_abs_error':qr,'translation_scale_max_abs_error':ts}


def aggregate_skin(path: Path) -> dict:
    d=json.loads(path.read_text())
    if d.get('schema')!='d1_guardian_inline_skin_probe/v1':
        raise ValueError(f'{path}: wrong skin schema {d.get("schema")}')
    by_joint=collections.defaultdict(lambda:{'influence_occurrences':0,'weight_u8_total':0,'models':collections.defaultdict(lambda:{'influence_occurrences':0,'weight_u8_total':0,'vertices':set()})})
    for model in d.get('models',[]):
        mh=model['tag_hash']
        for mesh in model.get('meshes',[]):
            for v in mesh.get('vertices',[]):
                vi=int(v['vertex'])
                for inf in v.get('influences',[]):
                    w=int(inf.get('weight_u8',0)); j=int(inf['bone'])
                    if w==0: continue
                    x=by_joint[j]; x['influence_occurrences']+=1; x['weight_u8_total']+=w
                    m=x['models'][mh]; m['influence_occurrences']+=1; m['weight_u8_total']+=w; m['vertices'].add((int(mesh['mesh_index']),vi))
    clean={}
    for j,x in by_joint.items():
        clean[j]={
            'influence_occurrences':x['influence_occurrences'],
            'weight_u8_total':x['weight_u8_total'],
            'models':{m:{'influence_occurrences':q['influence_occurrences'],'weight_u8_total':q['weight_u8_total'],'unique_source_vertices':len(q['vertices'])} for m,q in sorted(x['models'].items())}
        }
    return {'body_role':d.get('body_role'),'node_count_claim':d.get('node_count'),'joint_domain':sorted(clean),'by_joint':clean}


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--skin-report',type=Path,action='append',required=True)
    ap.add_argument('--published-skeleton',type=Path,required=True)
    ap.add_argument('--retail-report',type=Path,required=True)
    ap.add_argument('--retail-tag',required=True)
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args()

    pub=load_published(a.published_skeleton)
    ret=load_retail(a.retail_report,a.retail_tag)
    pn=pub['nodes']; rn=ret['node_hierarchy']['items']
    rh=[x['node_hash'].upper() for x in rn]
    rbyhash={h:i for i,h in enumerate(rh)}
    pdt=pub['default_object_space_transforms']; rdt=ret['default_object_space_transforms']['items']
    pit=pub['default_inverse_object_space_transforms']; rit=ret['default_inverse_object_space_transforms']['items']

    skins=[aggregate_skin(p) for p in a.skin_report]
    used=sorted({j for s in skins for j in s['joint_domain']})
    rows=[]
    mismatch=[]
    for j in used:
        if not 0<=j<len(pn):
            raise ValueError(f'source joint {j} is outside exact published skeleton domain {len(pn)}')
        p=pn[j]; same=rh[j] if j<len(rh) else None
        candidate_hash_index=rbyhash.get(p['node_hash'])
        exact_same_index=(same==p['node_hash'])
        de=srt_error(pdt[j] if j<len(pdt) else None,rdt[j] if j<len(rdt) else None)
        ie=srt_error(pit[j] if j<len(pit) else None,rit[j] if j<len(rit) else None)
        roles={}
        for s in skins:
            x=s['by_joint'].get(j)
            if x: roles[s['body_role']]=x
        row={
            'source_joint_index':j,
            'published_name':p['name'],'published_hash':p['node_hash'],'published_parent_index':p['parent_node_index'],
            'retail_same_index_hash':same,
            'retail_same_index_parent_index':rn[j]['parent_node_index'] if j<len(rn) else None,
            'same_index_hash_exact':exact_same_index,
            'published_hash_index_in_retail':candidate_hash_index,
            'published_hash_missing_from_retail':candidate_hash_index is None,
            'default_srt_same_index_error':de,
            'inverse_srt_same_index_error':ie,
            'source_usage':roles,
        }
        rows.append(row)
        if not exact_same_index: mismatch.append(row)

    bad_weight={}
    for row in mismatch:
        for role,x in row['source_usage'].items():
            z=bad_weight.setdefault(role,{'weight_u8_total':0,'influence_occurrences':0,'joints':[]})
            z['weight_u8_total']+=x['weight_u8_total']; z['influence_occurrences']+=x['influence_occurrences']; z['joints'].append(row['source_joint_index'])

    rep={
        'schema':'d1_guardian_joint_semantic_audit/v1',
        'published_skeleton_node_count':len(pn),
        'retail_tag':a.retail_tag.removeprefix('0x').removeprefix('0X').upper(),
        'retail_skeleton_node_count':len(rn),
        'body_roles':[x['body_role'] for x in skins],
        'used_source_joint_count':len(used),'used_source_joint_domain':used,
        'same_index_semantic_match_count':len(rows)-len(mismatch),
        'same_index_semantic_mismatch_count':len(mismatch),
        'same_index_semantics_safe':len(mismatch)==0,
        'mismatched_source_joint_indices':[x['source_joint_index'] for x in mismatch],
        'mismatch_source_weight_totals':bad_weight,
        'joints':rows,
        'policy':(
            'Source blend indices are never accepted against a candidate skeleton merely because they are numerically in range. '
            'A direct-index bind is semantically safe only if every used raw index names the same ordered bone hash in the exact named skeleton domain. '
            'Hash locations in another skeleton are evidence only; this audit does not invent or apply a remap.'
        ),
    }
    a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(rep,indent=2)+'\n')
    print('USED',used)
    print('RETAIL',rep['retail_tag'],'nodes',len(rn),'SAFE',rep['same_index_semantics_safe'],'MISMATCH',rep['mismatched_source_joint_indices'])
    for x in mismatch:
        print('JOINT',x['source_joint_index'],x['published_name'],x['published_hash'],'retail-same',x['retail_same_index_hash'],'hash-at',x['published_hash_index_in_retail'])
        for role,u in x['source_usage'].items():
            print(' ',role,'occ',u['influence_occurrences'],'weight_u8',u['weight_u8_total'],'models',u['models'])
    # Deliberately return nonzero when a caller asks whether raw direct binding is safe.
    return 2 if mismatch else 0

if __name__=='__main__': raise SystemExit(main())
