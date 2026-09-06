#!/usr/bin/env python3
"""Compare Bungie's published D1 player skeleton to exact retail D1 skeletons.

This tool is deliberately identity-first.  It does not select a retail rig because
its node count is close or because mesh joint indices happen to be in range.
Instead it compares ordered bone hashes, parent edges, object-space transforms,
and the D1 RangeIndexMap/InnerIndexMap carried by each exact retail resource.

The published input is the exact JSON served as
/common/destiny_content/animations/destiny_player_skeleton.js.  Retail inputs are
reports from d1_remote_skeleton_exact_probe.py.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

CRITICAL_NAMES = {
    'b_l_clav','b_r_clav','b_l_upperarm','b_r_upperarm','b_l_forearm','b_r_forearm',
    'b_l_hand','b_r_hand','b_l_grip','b_r_grip',
    'b_l_shoulder_twist_fixup','b_r_shoulder_twist_fixup',
    'b_l_wrist_twist_fixup','b_r_wrist_twist_fixup',
}


def u32hex(v: Any) -> str | None:
    if v is None: return None
    try: return f'{int(v) & 0xffffffff:08X}'
    except Exception: return None


def published_skeleton(path: Path) -> dict:
    obj=json.loads(path.read_text(encoding='utf-8-sig'))
    d=obj.get('definition',obj)
    nodes=d.get('nodes',[])
    out=[]
    for i,n in enumerate(nodes):
        nm=n.get('name') if isinstance(n,dict) else None
        name=None; h=None
        if isinstance(nm,dict):
            name=nm.get('string')
            h=u32hex(nm.get('hash'))
        elif isinstance(nm,str):
            name=nm
        if h is None and isinstance(n,dict):
            h=u32hex(n.get('bone_hash',n.get('hash')))
        p=n.get('parent_node_index',n.get('parentNodeIndex',n.get('parent'))) if isinstance(n,dict) else None
        try: p=int(p) if p is not None else None
        except Exception: p=None
        out.append({'index':i,'name':name,'node_hash':h,'parent_node_index':p})
    return {
        'nodes':out,
        'default_object_space_transforms':d.get('default_object_space_transforms',[]),
        'default_inverse_object_space_transforms':d.get('default_inverse_object_space_transforms',[]),
        'range_index_map':d.get('range_index_map',[]),
        'inner_index_map':d.get('inner_index_map',[]),
    }


def srt(t: Any) -> tuple[list[float],list[float]] | None:
    if not isinstance(t,dict): return None
    r=t.get('r',t.get('rotation'))
    ts=t.get('ts',t.get('translation_scale_raw'))
    if ts is None:
        tr=t.get('translation'); sc=t.get('scale')
        if isinstance(tr,list) and len(tr)>=3 and sc is not None: ts=[tr[0],tr[1],tr[2],sc]
    if not (isinstance(r,list) and len(r)>=4 and isinstance(ts,list) and len(ts)>=4): return None
    try: return ([float(x) for x in r[:4]],[float(x) for x in ts[:4]])
    except Exception: return None


def srt_error(a: Any,b: Any) -> dict | None:
    aa=srt(a); bb=srt(b)
    if aa is None or bb is None: return None
    # q and -q are the same rotation.
    dr1=max(abs(x-y) for x,y in zip(aa[0],bb[0])); dr2=max(abs(x+y) for x,y in zip(aa[0],bb[0]))
    return {'rotation_max_abs_error':min(dr1,dr2),'translation_scale_max_abs_error':max(abs(x-y) for x,y in zip(aa[1],bb[1]))}


def compare(pub:dict, retail:dict)->dict:
    pn=pub['nodes']; rn=retail['node_hierarchy']['items']
    ph=[x['node_hash'] for x in pn]; rh=[x['node_hash'] for x in rn]
    pindex={h:i for i,h in enumerate(ph) if h}; rindex={h:i for i,h in enumerate(rh) if h}
    shared=[h for h in ph if h in rindex]
    missing=[{'published_index':i,'name':pn[i].get('name'),'node_hash':h} for i,h in enumerate(ph) if h not in rindex]
    extra=[{'retail_index':i,'node_hash':h} for i,h in enumerate(rh) if h not in pindex]
    same_index=[]; remapped=[]
    for h in shared:
        pi=pindex[h]; ri=rindex[h]
        row={'node_hash':h,'name':pn[pi].get('name'),'published_index':pi,'retail_index':ri}
        (same_index if pi==ri else remapped).append(row)

    # Compare parent relation by hash rather than by integer index so insertions are explicit.
    parent_edges=0; parent_edges_preserved=0; parent_mismatches=[]
    for h in shared:
        pi=pindex[h]; ri=rindex[h]
        pp=pn[pi].get('parent_node_index'); rp=rn[ri].get('parent_node_index')
        phash=ph[pp] if isinstance(pp,int) and 0<=pp<len(ph) else None
        rhash=rh[rp] if isinstance(rp,int) and 0<=rp<len(rh) else None
        if phash is None or phash in rindex:
            parent_edges+=1
            if phash==rhash: parent_edges_preserved+=1
            else: parent_mismatches.append({'node_hash':h,'name':pn[pi].get('name'),'published_parent_hash':phash,'retail_parent_hash':rhash})

    pdt=pub['default_object_space_transforms']; pit=pub['default_inverse_object_space_transforms']
    rdt=retail.get('default_object_space_transforms',{}).get('items',[])
    rit=retail.get('default_inverse_object_space_transforms',{}).get('items',[])
    transform_rows=[]
    for h in shared:
        pi=pindex[h]; ri=rindex[h]
        de=srt_error(pdt[pi] if pi<len(pdt) else None,rdt[ri] if ri<len(rdt) else None)
        ie=srt_error(pit[pi] if pi<len(pit) else None,rit[ri] if ri<len(rit) else None)
        if de is not None or ie is not None:
            transform_rows.append({'node_hash':h,'name':pn[pi].get('name'),'published_index':pi,'retail_index':ri,'default_error':de,'inverse_error':ie})
    max_default=max((max(x['default_error'].values()) for x in transform_rows if x['default_error']),default=None)
    max_inverse=max((max(x['inverse_error'].values()) for x in transform_rows if x['inverse_error']),default=None)

    critical=[]
    for i,x in enumerate(pn):
        if x.get('name') in CRITICAL_NAMES:
            h=x['node_hash']; ri=rindex.get(h)
            critical.append({'name':x.get('name'),'node_hash':h,'published_index':i,'retail_index':ri,
                             'present':ri is not None,'same_index':ri==i if ri is not None else False})

    rr=retail.get('range_index_map',{}).get('items',[])
    ri_map=retail.get('inner_index_map',{}).get('items',[])
    pr=pub.get('range_index_map',[]); pi_map=pub.get('inner_index_map',[])
    return {
        'tag_hash':retail.get('tag_hash'),
        'published_node_count':len(ph),'retail_node_count':len(rh),
        'ordered_hashes_exact':ph==rh,
        'ordered_parent_indices_exact':[x.get('parent_node_index') for x in pn]==[x.get('parent_node_index') for x in rn],
        'shared_hash_count':len(shared),'shared_hash_percent':100.0*len(shared)/len(ph) if ph else 0.0,
        'same_index_shared_count':len(same_index),'remapped_shared_count':len(remapped),
        'missing_published_bones':missing,'extra_retail_bones':extra,
        'same_index_shared':same_index,'remapped_shared':remapped,
        'parent_edge_count_compared':parent_edges,'parent_edge_preserved_count':parent_edges_preserved,
        'parent_edges_exact_for_shared':parent_edges==parent_edges_preserved,
        'parent_mismatches':parent_mismatches,
        'default_transform_max_abs_error_shared':max_default,
        'inverse_transform_max_abs_error_shared':max_inverse,
        'critical_upper_limb_bones':critical,
        'published_range_index_map':pr,'retail_range_index_map':rr,'range_index_map_exact':pr==rr,
        'published_inner_index_map':pi_map,'retail_inner_index_map':ri_map,'inner_index_map_exact':pi_map==ri_map,
        'count_invariants':retail.get('count_invariants'),
    }


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--published-skeleton',type=Path,required=True)
    ap.add_argument('--retail-report',type=Path,action='append',required=True)
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args()
    pub=published_skeleton(a.published_skeleton)
    rows=[]; errors=[]
    for p in a.retail_report:
        src=json.loads(p.read_text())
        for r in src.get('skeletons',[]):
            if r.get('error') or r.get('missing'):
                errors.append({'source':str(p),'tag_hash':r.get('tag_hash'),'error':r.get('error'),'missing':r.get('missing')}); continue
            rows.append(compare(pub,r))
    rows.sort(key=lambda x:(x['ordered_hashes_exact'],x['shared_hash_count'],x['same_index_shared_count']),reverse=True)
    exact=[x for x in rows if x['ordered_hashes_exact'] and x['ordered_parent_indices_exact']]
    rep={
        'schema':'d1_published_player_skeleton_compare/v1',
        'published_node_count':len(pub['nodes']),
        'published_node_names':[x.get('name') for x in pub['nodes']],
        'published_node_hashes':[x.get('node_hash') for x in pub['nodes']],
        'retail_candidate_count':len(rows),'exact_identity_match_count':len(exact),
        'best_candidate_tag':rows[0]['tag_hash'] if rows else None,
        'candidates':rows,'errors':errors,
        'policy':'A retail skeleton is an exact published-player-rig identity only when ordered bone hashes and ordered parent indices match exactly. Numeric joint-index range or animation compatibility is not identity evidence.'
    }
    a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(rep,indent=2)+'\n')
    print('PUBLISHED',rep['published_node_count'],'RETAIL CANDIDATES',len(rows),'EXACT',len(exact),'BEST',rep['best_candidate_tag'])
    for x in rows:
        print(x['tag_hash'],'nodes',x['retail_node_count'],'shared',x['shared_hash_count'],'same-index',x['same_index_shared_count'],
              'ordered-exact',x['ordered_hashes_exact'],'parent-shared-exact',x['parent_edges_exact_for_shared'])
        print('  missing',[(m['published_index'],m['name'],m['node_hash']) for m in x['missing_published_bones']])
        print('  critical',[(c['name'],c['published_index'],c['retail_index']) for c in x['critical_upper_limb_bones'] if not c['same_index']])
    if errors: print('ERRORS',errors)
    return 0

if __name__=='__main__': raise SystemExit(main())
