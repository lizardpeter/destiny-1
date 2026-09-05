#!/usr/bin/env python3
"""Decode and validate D1 ROI inline skinning in Guardian primary vertex streams.

Retail D1 entity meshes use two inline skeletal representations in the primary
vertex stream when no OldWeights resource exists:

* stride 0x0C: position is four int16 values. If position W is ±0x7FFF on a
  skeletal model, bytes 8,9 are two bone indices and bytes 10,11 are two UNORM8
  weights. Ordinary non-sentinel non-negative W is the rigid one-bone index.
* stride 0x10: position is four int16 values, bytes 8..11 are four UNORM8
  weights, and bytes 12..15 are four bone indices.

This tool validates those rules directly against exact remote Guardian model
bytes. It reports every nonzero influence, weight-sum failures, and out-of-range
bone indices. No influence is synthesized or renormalized.
"""
from __future__ import annotations

import argparse
import collections
import json
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from d1_entity_model_probe import parse_model
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_investment_parent_probe import RemoteLogicalPackage
from d1_remote_model_export import MultiPackageReader, models_from_report
from d1_split_tar_extract import SplitHttpTar

SENTINELS = {32767, -32767}


def decode_stream(payload: bytes, stride: int, node_count: int) -> dict:
    if stride not in (0x0C, 0x10):
        return {'supported': False, 'stride': stride}
    if len(payload) % stride:
        raise ValueError(f'payload size {len(payload)} not divisible by stride {stride}')
    vertices=[]; mode_counts=collections.Counter(); bone_use=collections.Counter()
    sum_fail=[]; range_fail=[]; unresolved=[]
    for vi,off in enumerate(range(0,len(payload),stride)):
        wpos=struct.unpack_from('<h',payload,off+6)[0]
        if stride==0x0C:
            if wpos in SENTINELS:
                inds=list(payload[off+8:off+10]); vals=list(payload[off+10:off+12]); mode='inline2'
            elif wpos>=0:
                inds=[wpos]; vals=[255]; mode='rigid_w'
            else:
                inds=[]; vals=[]; mode='unresolved_negative_w'; unresolved.append({'vertex':vi,'w':wpos})
        else:
            vals=list(payload[off+8:off+12]); inds=list(payload[off+12:off+16]); mode='inline4'
        mode_counts[mode]+=1
        influences=[]
        if vals and sum(vals)!=255:
            sum_fail.append({'vertex':vi,'mode':mode,'indices':inds,'weights':vals,'sum':sum(vals)})
        for j,v in zip(inds,vals):
            if v==0: continue
            if not (0<=j<node_count):
                range_fail.append({'vertex':vi,'mode':mode,'bone':j,'weight':v,'indices':inds,'weights':vals})
            else:
                bone_use[j]+=v
            influences.append({'bone':j,'weight_u8':v,'weight':v/255.0})
        vertices.append({'vertex':vi,'position_w':wpos,'mode':mode,'influences':influences})
    return {
        'supported':True,'stride':stride,'vertex_count':len(vertices),'mode_counts':dict(mode_counts),
        'weight_sum_failure_count':len(sum_fail),'weight_sum_failures':sum_fail[:100],
        'out_of_range_influence_count':len(range_fail),'out_of_range_influences':range_fail[:100],
        'unresolved_vertex_count':len(unresolved),'unresolved_vertices':unresolved[:100],
        'bone_domain':sorted(bone_use),'bone_weight_u8_totals':{str(k):v for k,v in sorted(bone_use.items())},
        'vertices':vertices,
    }


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--report',type=Path,required=True)
    ap.add_argument('--body-role',choices=('masculine','feminine'),required=True)
    ap.add_argument('--node-count',type=int,default=67)
    ap.add_argument('--member-catalog',type=Path,action='append',required=True)
    ap.add_argument('--base-url',required=True);ap.add_argument('--part-count',type=int,default=10)
    ap.add_argument('--runtime',type=Path,required=True);ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args()
    selected=models_from_report(json.loads(a.report.read_text()),a.body_role)
    catalogs=load_catalogs(a.member_catalog)
    arc=SplitHttpTar([f"{a.base_url.rstrip('/')}/packages.tar.{i:03d}" for i in range(1,a.part_count+1)],retries=6,timeout=90)
    views={pkg:RemoteLogicalPackage(arc,fam,a.runtime) for pkg,fam in sorted(catalogs.items())}
    r=MultiPackageReader(views); by={e['tag_hash'].upper():e for e in r.entries}
    rows=[]; total=collections.Counter(); all_bones=set(); failures=[]
    for sel in selected:
        tag=sel['tag_hash'].upper(); e=by[tag]; model=parse_model(r.entry(e['index']),'PS4')
        mr={**sel,'tag_hash':tag,'meshes':[]}
        for mi,mesh in enumerate(model['meshes']):
            vh=by[mesh['vertices1'].upper()]; vp=by[vh['reference'].upper()]
            hb=r.entry(vh['index']); payload=r.entry(vp['index']); stride=struct.unpack_from('<h',hb,4)[0]
            dec=decode_stream(payload,stride,a.node_count)
            row={'mesh_index':mi,'vertices1':mesh['vertices1'].upper(),'payload':vh['reference'].upper(),**dec}
            mr['meshes'].append(row)
            if dec.get('supported'):
                total['vertices']+=dec['vertex_count'];total['weight_sum_failures']+=dec['weight_sum_failure_count'];
                total['out_of_range']+=dec['out_of_range_influence_count'];total['unresolved']+=dec['unresolved_vertex_count']
                for k,v in dec['mode_counts'].items():total[f'mode:{k}']+=v
                all_bones.update(dec['bone_domain'])
                if dec['weight_sum_failure_count'] or dec['out_of_range_influence_count'] or dec['unresolved_vertex_count']:
                    failures.append({'model':tag,'mesh':mi,'sum_fail':dec['weight_sum_failure_count'],'range_fail':dec['out_of_range_influence_count'],'unresolved':dec['unresolved_vertex_count']})
        rows.append(mr)
    rep={'schema':'d1_guardian_inline_skin_probe/v1','body_role':a.body_role,'node_count':a.node_count,
         'model_count':len(rows),'totals':dict(total),'bone_domain':sorted(all_bones),'failure_meshes':failures,'models':rows,
         'policy':'D1 inline skin bytes are decoded exactly as stored. U8 weights are not normalized or repaired; zero-weight indices are ignored; nonzero indices must fit node_count.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(rep,indent=2)+'\n')
    print(json.dumps({k:rep[k] for k in ('body_role','node_count','model_count','totals','bone_domain','failure_meshes')},indent=2))
    for m in rows:
        name=(m.get('examples') or [{}])[0].get('name')
        print('\n',name,m['tag_hash'])
        for x in m['meshes']:
            if x.get('supported'): print(' mesh',x['mesh_index'],'stride',hex(x['stride']),'modes',x['mode_counts'],'bones',x['bone_domain'],'sumfail',x['weight_sum_failure_count'],'rangefail',x['out_of_range_influence_count'])
    return 0
if __name__=='__main__':raise SystemExit(main())
