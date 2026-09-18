#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,math,sys
from pathlib import Path
import bpy

def cli():
    raw=sys.argv;args=raw[raw.index('--')+1:] if '--' in raw else []
    ap=argparse.ArgumentParser();ap.add_argument('--report',type=Path,required=True);return ap.parse_args(args)

def pose_vector(arm):
    out=[]
    for pb in arm.pose.bones:
        m=pb.matrix
        for row in m:
            out.extend(float(x) for x in row)
    return out

def main():
    a=cli();s=bpy.context.scene;rows=[];viol=[]
    arms=[o for o in bpy.data.objects if o.type=='ARMATURE' and o.get('d1LaptopTestAsset')]
    if len(arms)!=3:viol.append(f'armature_count:{len(arms)}')
    for arm in arms:
        act=arm.animation_data.action if arm.animation_data else None
        if act is None:
            viol.append(f'{arm.name}:no_action');continue
        lo,hi=map(float,act.frame_range);samples=sorted(set(int(round(lo+(hi-lo)*q)) for q in (0,.2,.4,.6,.8,1.0)))
        vecs=[]
        for fr in samples:
            s.frame_set(fr);bpy.context.view_layer.update();vecs.append(pose_vector(arm))
        base=vecs[0];score=0.0
        for v in vecs[1:]:
            if len(v)!=len(base):continue
            score=max(score,max((abs(x-y) for x,y in zip(base,v)),default=0.0))
        moving=score>1e-5
        if not moving:viol.append(f'{arm.name}:no_pose_motion:{score}')
        rows.append({'armature':arm.name,'action':act.name,'frame_range':[lo,hi],'sample_frames':samples,'pose_matrix_max_abs_delta':score,'moving':moving,'pose_bone_count':len(arm.pose.bones)})
    s.frame_set(int(s.frame_start))
    rep={'schema_version':1,'status':'D1_ASSIGNED_TEST_ACTION_MOTION_VALIDATION','violations':viol,'armature_count':len(arms),'moving_armature_count':sum(x['moving'] for x in rows),'rows':rows}
    a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(rep,indent=2)+'\n');print(json.dumps(rep,indent=2))
    if viol:raise SystemExit('motion validation failed: '+','.join(viol))
if __name__=='__main__':main()
