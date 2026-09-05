#!/usr/bin/env python3
"""Sparse character/Guardian asset census for final-era D1 PS4 package families.

This intentionally separates *articulated/render structure* from gameplay identity.
It reads the highest patch snapshot of a logical package family through HTTP ranges
and decompresses only EntityResource payloads needed to identify model parents,
skeletons, runtime rigs, compositions and EntityChildren graphs. Entry-table class
counts provide model/animation coverage without downloading whole packages.

A large skeleton or a package name is NOT by itself proof of a playable Guardian or
combatant. This probe exists to find strong candidates for subsequent ownership and
assembly tracing.
"""
from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))

from d1_remote_investment_parent_probe import RemoteLogicalPackage, parse_member
from d1_split_tar_extract import SplitHttpTar
from d1_entity_resource_probe import ENTITY_RESOURCE_CLASS, parse_resource
from d1_skeleton_probe import parse_skeleton_resource
from d1_remote_entity_child_find import parse_children_resource

ANIMATION_CLIP_CLASS='808005A1'
ENTITY_MODEL_CLASS='80801AB5'
ANIMATION_WRAPPER_CLASS='8080222A'
POST_ANIMATION_CONTROL_CLASS='80802C0E'
RUNTIME_RIG_DISCRIMINATOR='808008B2'
RUNTIME_RIG_INFO='8080099B'
COMPOSITION_DISCRIMINATOR='8080079A'
COMPOSITION_INFO='80800610'


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--package-id',type=lambda x:int(x,0),required=True)
    ap.add_argument('--base-url',required=True)
    ap.add_argument('--part-count',type=int,default=10)
    ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('--member',action='append',type=parse_member,required=True)
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args()

    if any(m.pkg_id!=a.package_id for m in a.member):
        raise SystemExit('all --member package ids must equal --package-id')
    members={m.patch_id:m for m in a.member}
    base=a.base_url.rstrip('/')
    arc=SplitHttpTar([f'{base}/packages.tar.{i:03d}' for i in range(1,a.part_count+1)],retries=6,timeout=90)
    r=RemoteLogicalPackage(arc,members,a.runtime)

    refs=collections.Counter(e['reference'].upper() for e in r.entries)
    relevant={
        ENTITY_RESOURCE_CLASS,
        ENTITY_MODEL_CLASS,
        ANIMATION_CLIP_CLASS,
        ANIMATION_WRAPPER_CLASS,
        POST_ANIMATION_CONTROL_CLASS,
    }
    class_counts={k:refs.get(k,0) for k in sorted(relevant)}

    resources=[]
    pair_counts=collections.Counter()
    role_counts=collections.Counter()
    model_parents=[]
    skeletons=[]
    runtime_rigs=[]
    compositions=[]
    children=[]
    errors=[]

    for e in r.entries:
        if e['reference'].upper()!=ENTITY_RESOURCE_CLASS or e['type']!=16 or e['subtype']!=0:
            continue
        row={'entry_index':e['index'],'tag_hash':e['tag_hash'].upper(),'size':e['file_size']}
        try:
            b=r.entry(e['index'])
            p=parse_resource(b,r.h['platform'])
            sem=p.get('semantic_role')
            u10=p.get('unk10',{}).get('class_hash')
            u18=p.get('unk18',{}).get('class_hash')
            row.update({'semantic_role':sem,'unk10_class':u10,'unk18_class':u18})
            role_counts[sem]+=1
            if u10 or u18: pair_counts[(u10 or 'NULL',u18 or 'NULL')]+=1

            if sem=='entity_model' and p.get('embedded_model_tag_hash'):
                x={'tag_hash':row['tag_hash'],'entry_index':e['index'],'model':p['embedded_model_tag_hash'].upper(),'size':e['file_size']}
                model_parents.append(x); row['embedded_model_tag_hash']=x['model']
            elif sem=='entity_skeleton':
                sk=parse_skeleton_resource(b)
                info=sk['skeleton_info']
                bones=info.get('bones',[])
                x={'tag_hash':row['tag_hash'],'entry_index':e['index'],'bone_count':info['node_hierarchy']['count'],
                   'bone_hashes':[q['node_hash'] for q in bones]}
                skeletons.append(x); row['bone_count']=x['bone_count']
            elif u10==RUNTIME_RIG_DISCRIMINATOR and u18==RUNTIME_RIG_INFO:
                runtime_rigs.append({'tag_hash':row['tag_hash'],'entry_index':e['index'],'size':e['file_size']})
            elif u10==COMPOSITION_DISCRIMINATOR and u18==COMPOSITION_INFO:
                compositions.append({'tag_hash':row['tag_hash'],'entry_index':e['index'],'size':e['file_size']})

            ch=parse_children_resource(b)
            if ch is not None:
                children.append({'tag_hash':row['tag_hash'],'entry_index':e['index'],'child_count':ch['child_count'],
                                 'children':ch['children']})
        except Exception as ex:
            row['error']=repr(ex)
            errors.append({'tag_hash':row['tag_hash'],'entry_index':e['index'],'error':repr(ex)})
        resources.append(row)

    skeletons.sort(key=lambda x:(-x['bone_count'],x['tag_hash']))
    model_parents.sort(key=lambda x:x['tag_hash'])
    pair_rows=[{'unk10_class':a,'unk18_class':b,'count':n} for (a,b),n in pair_counts.most_common()]

    rep={
        'schema':'d1_remote_character_asset_probe/v1',
        'package_id':f'{a.package_id:04X}',
        'logical_view_member':r.view.name,
        'logical_view_patch':r.view.patch_id,
        'entry_count':len(r.entries),
        'class_counts':class_counts,
        'entity_resource_count':len(resources),
        'entity_resource_role_counts':dict(role_counts),
        'entity_resource_class_pairs':pair_rows,
        'model_parents':model_parents,
        'skeletons':skeletons,
        'runtime_rigs':runtime_rigs,
        'compositions':compositions,
        'entity_children':children,
        'errors':errors,
        'summary':{
            'model_parent_count':len(model_parents),
            'entity_model_entry_count':refs.get(ENTITY_MODEL_CLASS,0),
            'skeleton_count':len(skeletons),
            'largest_skeleton_bones':skeletons[0]['bone_count'] if skeletons else 0,
            'runtime_rig_count':len(runtime_rigs),
            'composition_count':len(compositions),
            'animation_clip_count':refs.get(ANIMATION_CLIP_CLASS,0),
            'animation_wrapper_count':refs.get(ANIMATION_WRAPPER_CLASS,0),
            'post_animation_control_count':refs.get(POST_ANIMATION_CONTROL_CLASS,0),
            'entity_children_parent_count':len(children),
            'entity_children_total_children':sum(x['child_count'] for x in children),
        },
        'policy':(
            'This report identifies structural character/player-asset candidates only. Package names, model counts, '
            'bone counts and animation presence do not prove playable-Guardian or combatant identity. Semantic promotion '
            'requires an exact gameplay/investment/entity assembly or ownership edge.'
        ),
    }
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(rep,indent=2)+'\n')
    print(json.dumps({'package_id':rep['package_id'],'view':rep['logical_view_member'],'summary':rep['summary'],
                      'top_class_pairs':pair_rows[:12]},indent=2))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
