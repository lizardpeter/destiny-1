#!/usr/bin/env python3
"""Census the validated rigid joint-index lane across remote D1 models.

For D1 PS4 meshes where s_entity_model.old_weights == FFFFFFFF, project retail
validation on Gjallarhorn proves primary vertex stream int16 lane 3 is the native
rigid joint index. This tool applies that *specific validated representation* to
other models and reports joint domains/distributions without assigning a skeleton.

Meshes with an old_weights resource are deliberately not decoded here.
"""
from __future__ import annotations
import argparse,collections,json,struct,sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from d1_remote_investment_parent_probe import RemoteLogicalPackage,parse_member
from d1_split_tar_extract import SplitHttpTar
from d1_entity_model_probe import D1_ENTITY_MODEL_CLASS,parse_model


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--package-id',type=lambda x:int(x,0),required=True)
    ap.add_argument('--base-url',required=True);ap.add_argument('--part-count',type=int,default=10)
    ap.add_argument('--runtime',type=Path,required=True);ap.add_argument('--member',action='append',type=parse_member,required=True)
    ap.add_argument('--max-models',type=int,default=10000);ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args()
    members={m.patch_id:m for m in a.member}
    if any(m.pkg_id!=a.package_id for m in a.member): raise SystemExit('member package mismatch')
    arc=SplitHttpTar([f"{a.base_url.rstrip('/')}/packages.tar.{i:03d}" for i in range(1,a.part_count+1)],retries=6,timeout=90)
    r=RemoteLogicalPackage(arc,members,a.runtime)
    by={e['tag_hash'].upper():e for e in r.entries}
    models=[e for e in r.entries if e['type']==16 and e['subtype']==0 and e['reference'].upper()==D1_ENTITY_MODEL_CLASS][:a.max_models]
    union=set();dist=collections.Counter();rows=[];errors=[]
    rigid_meshes=weighted_meshes=missing_streams=0; vertex_total=0
    for e in models:
        mr={'tag_hash':e['tag_hash'].upper(),'entry_index':e['index'],'rigid_meshes':[],'weighted_mesh_count':0}
        try: m=parse_model(r.entry(e['index']),'PS4')
        except Exception as ex:
            errors.append({'tag_hash':mr['tag_hash'],'phase':'model','error':repr(ex)});continue
        for mi,mesh in enumerate(m['meshes']):
            if mesh['old_weights'].upper()!='FFFFFFFF':
                weighted_meshes+=1;mr['weighted_mesh_count']+=1;continue
            rigid_meshes+=1
            vh=by.get(mesh['vertices1'].upper())
            if not vh:
                missing_streams+=1;continue
            vp=by.get(vh['reference'].upper())
            if not vp:
                missing_streams+=1;continue
            try:
                hb=r.entry(vh['index']); pb=r.entry(vp['index'])
                if len(hb)<6: raise ValueError('short vertex header')
                stride=struct.unpack_from('<h',hb,4)[0]
                if stride<8 or stride>128 or stride%2: raise ValueError(f'invalid stride {stride}')
                if len(pb)%stride: raise ValueError(f'payload size {len(pb)} not divisible by stride {stride}')
                vals=[]
                for off in range(0,len(pb),stride):
                    j=struct.unpack_from('<h',pb,off+6)[0]
                    vals.append(j);union.add(j);dist[j]+=1
                vertex_total+=len(vals)
                mr['rigid_meshes'].append({'mesh_index':mi,'vertices1':mesh['vertices1'],'stride':stride,
                                           'vertex_count':len(vals),'joint_min':min(vals) if vals else None,
                                           'joint_max':max(vals) if vals else None,'joint_values':sorted(set(vals))})
            except Exception as ex:
                errors.append({'tag_hash':mr['tag_hash'],'mesh_index':mi,'phase':'vertex','error':repr(ex)})
        rows.append(mr)
    rep={'schema':'d1_remote_rigid_joint_domain/v1','package_id':f'{a.package_id:04X}','logical_view':r.view.name,
         'model_count_scanned':len(models),'rigid_mesh_count':rigid_meshes,'weighted_mesh_count_skipped':weighted_meshes,
         'missing_stream_count':missing_streams,'rigid_vertex_count':vertex_total,
         'joint_domain':sorted(union),'joint_min':min(union) if union else None,'joint_max':max(union) if union else None,
         'joint_value_count':len(union),'joint_distribution':{str(k):v for k,v in sorted(dist.items())},
         'models':rows,'errors':errors,
         'policy':'Joint interpretation applies only to old_weights==FFFFFFFF meshes using the already retail-validated D1 PS4 rigid primary-stream representation. Weighted meshes are intentionally excluded.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(rep,indent=2)+'\n')
    print(json.dumps({k:rep[k] for k in ('package_id','logical_view','model_count_scanned','rigid_mesh_count','weighted_mesh_count_skipped','rigid_vertex_count','joint_domain','joint_max')},indent=2))
    return 0
if __name__=='__main__':raise SystemExit(main())
