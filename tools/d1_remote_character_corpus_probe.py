#!/usr/bin/env python3
"""Payload-level articulated-family census over the archive candidate index.

Consumes d1_remote_character_candidate_index/v1 and sparsely decompresses only
EntityResource payloads in structurally strong current families. It generalizes the
single-package d1_remote_character_asset_probe across the corpus while preserving
namespace identity.

This phase establishes structural animation/render families; it still does not call
a family a particular NPC/enemy/Guardian without an exact ownership/name edge.
"""
from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))

from d1_remote_investment_parent_probe import Member,RemoteLogicalPackage
from d1_split_tar_extract import SplitHttpTar
from d1_entity_resource_probe import ENTITY_RESOURCE_CLASS,parse_resource
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


def analyze(row:dict,arc:SplitHttpTar,runtime:Path)->dict:
    pkg=int(row['package_id'],16)
    members={}
    for x in row['physical_members']:
        gen=int(x['filename_generation'])
        m=Member(str(x['name']),int(x['data_offset']),int(x['size']),pkg,gen)
        if gen in members and members[gen]!=m:raise ValueError(f"{row['namespace_key']}: duplicate generation {gen}")
        members[gen]=m
    r=RemoteLogicalPackage(arc,members,runtime)
    if r.view.name!=row['current_member']:
        raise ValueError(f"{row['namespace_key']}: RemoteLogicalPackage selected {r.view.name}, candidate index selected {row['current_member']}")

    refs=collections.Counter(e['reference'].upper() for e in r.entries)
    resources=[];pairs=collections.Counter();roles=collections.Counter();model_parents=[];skeletons=[];runtime_rigs=[];compositions=[];children=[];errors=[]
    for e in r.entries:
        if e['reference'].upper()!=ENTITY_RESOURCE_CLASS or e['type']!=16 or e['subtype']!=0:continue
        rec={'entry_index':e['index'],'tag_hash':e['tag_hash'].upper(),'size':e['file_size']}
        try:
            b=r.entry(e['index']);p=parse_resource(b,r.h['platform'])
            sem=p.get('semantic_role');u10=p.get('unk10',{}).get('class_hash');u18=p.get('unk18',{}).get('class_hash')
            rec.update({'semantic_role':sem,'unk10_class':u10,'unk18_class':u18});roles[str(sem)]+=1
            if u10 or u18:pairs[(u10 or 'NULL',u18 or 'NULL')]+=1
            if sem=='entity_model' and p.get('embedded_model_tag_hash'):
                mh=p['embedded_model_tag_hash'].upper();model_parents.append({'tag_hash':rec['tag_hash'],'entry_index':e['index'],'model':mh,'size':e['file_size']});rec['embedded_model_tag_hash']=mh
            elif sem=='entity_skeleton':
                sk=parse_skeleton_resource(b);info=sk['skeleton_info'];bones=info.get('bones',[])
                skeletons.append({'tag_hash':rec['tag_hash'],'entry_index':e['index'],'bone_count':int(info['node_hierarchy']['count']),
                                  'bone_hashes':[q['node_hash'] for q in bones]})
            elif u10==RUNTIME_RIG_DISCRIMINATOR and u18==RUNTIME_RIG_INFO:
                runtime_rigs.append({'tag_hash':rec['tag_hash'],'entry_index':e['index'],'size':e['file_size']})
            elif u10==COMPOSITION_DISCRIMINATOR and u18==COMPOSITION_INFO:
                compositions.append({'tag_hash':rec['tag_hash'],'entry_index':e['index'],'size':e['file_size']})
            ch=parse_children_resource(b)
            if ch is not None:children.append({'tag_hash':rec['tag_hash'],'entry_index':e['index'],'child_count':ch['child_count'],'children':ch['children']})
        except Exception as ex:
            rec['error']=repr(ex);errors.append({'tag_hash':rec['tag_hash'],'entry_index':e['index'],'error':repr(ex)})
        resources.append(rec)
    skeletons.sort(key=lambda x:(-x['bone_count'],x['tag_hash']))
    pair_rows=[{'unk10_class':a,'unk18_class':b,'count':n} for (a,b),n in pairs.most_common()]
    structural=bool(model_parents and skeletons and runtime_rigs and (refs.get(ANIMATION_CLIP_CLASS,0) or refs.get(ANIMATION_WRAPPER_CLASS,0) or refs.get(POST_ANIMATION_CONTROL_CLASS,0)))
    return {
      'namespace_key':row['namespace_key'],'kind':row['kind'],'locale':row.get('locale'),'package_id':row['package_id'],
      'logical_view_member':r.view.name,'logical_view_generation':r.view.patch_id,'header_patch_id':int(r.h['patch_id']),
      'entry_count':len(r.entries),'candidate_classification':row['classification'],
      'class_counts':{h:int(refs.get(h,0)) for h in (ENTITY_RESOURCE_CLASS,ENTITY_MODEL_CLASS,ANIMATION_CLIP_CLASS,ANIMATION_WRAPPER_CLASS,POST_ANIMATION_CONTROL_CLASS)},
      'entity_resource_count':len(resources),'entity_resource_role_counts':dict(roles),'entity_resource_class_pairs':pair_rows,
      'model_parents':model_parents,'skeletons':skeletons,'runtime_rigs':runtime_rigs,'compositions':compositions,'entity_children':children,'errors':errors,
      'structural_articulated_family':structural,
      'summary':{'model_parent_count':len(model_parents),'entity_model_entry_count':int(refs.get(ENTITY_MODEL_CLASS,0)),
                 'skeleton_count':len(skeletons),'largest_skeleton_bones':skeletons[0]['bone_count'] if skeletons else 0,
                 'runtime_rig_count':len(runtime_rigs),'composition_count':len(compositions),
                 'animation_clip_count':int(refs.get(ANIMATION_CLIP_CLASS,0)),'animation_wrapper_count':int(refs.get(ANIMATION_WRAPPER_CLASS,0)),
                 'post_animation_control_count':int(refs.get(POST_ANIMATION_CONTROL_CLASS,0)),
                 'entity_children_parent_count':len(children),'entity_children_total_children':sum(x['child_count'] for x in children)},
    }


def skeleton_signature(sk:dict)->str:
    # Ordered bone hashes are the source identity; count alone is not sufficient.
    import hashlib
    payload=('|'.join(str(x).upper() for x in sk.get('bone_hashes',[]))).encode()
    return hashlib.sha256(payload).hexdigest()


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('candidate_index',type=Path)
    ap.add_argument('--base-url',default='https://crypt.cohae.dev/destiny/ps4/packages/latest')
    ap.add_argument('--part-count',type=int,default=10)
    ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('--all-articulated-signatures',action='store_true',help='probe all signature families instead of strong candidates only')
    ap.add_argument('--kind',action='append',choices=['base','localized','special'],help='optional namespace-kind filter; repeatable')
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    src=json.loads(a.candidate_index.read_text())
    if src.get('schema')!='d1_remote_character_candidate_index/v1':raise ValueError('wrong candidate-index schema')
    source=src['articulated_signature_families'] if a.all_articulated_signatures else src['strong_character_payload_candidates']
    allowed=set(a.kind or ['base','localized','special'])
    todo=[x for x in source if x.get('kind') in allowed]
    base=a.base_url.rstrip('/');arc=SplitHttpTar([f'{base}/packages.tar.{i:03d}' for i in range(1,a.part_count+1)],retries=6,timeout=90)
    reports=[];fatal=[]
    for i,row in enumerate(todo,1):
        try:reports.append(analyze(row,arc,a.runtime))
        except Exception as ex:fatal.append({'namespace_key':row.get('namespace_key'),'error':repr(ex)})
        print(f'FAMILIES {i}/{len(todo)} structural={sum(bool(x.get("structural_articulated_family")) for x in reports)} fatal={len(fatal)}',flush=True)

    sig_groups=collections.defaultdict(list);bone_counts=collections.Counter();class_pairs=collections.Counter()
    for r in reports:
        for sk in r['skeletons']:
            sig=skeleton_signature(sk);sk['ordered_bone_hash_signature_sha256']=sig
            sig_groups[sig].append({'namespace_key':r['namespace_key'],'skeleton':sk['tag_hash'],'bone_count':sk['bone_count']})
            bone_counts[sk['bone_count']]+=1
        for p in r['entity_resource_class_pairs']:
            class_pairs[f"{p['unk10_class']}->{p['unk18_class']}"]+=int(p['count'])
    skeleton_families=[{'signature_sha256':s,'occurrence_count':len(xs),'bone_count_set':sorted({x['bone_count'] for x in xs}),'occurrences':xs} for s,xs in sorted(sig_groups.items())]
    structural=[r for r in reports if r['structural_articulated_family']]
    out={'schema':'d1_remote_character_corpus_probe/v1','status':'D1_CHARACTER_CORPUS_PROBE_COMPLETE' if not fatal else 'D1_CHARACTER_CORPUS_PROBE_PARTIAL',
         'source_candidate_schema':src.get('schema'),'requested_family_count':len(todo),'probed_family_count':len(reports),'fatal_family_count':len(fatal),
         'structural_articulated_family_count':len(structural),'skeleton_occurrence_count':sum(len(r['skeletons']) for r in reports),
         'unique_ordered_skeleton_family_count':len(skeleton_families),'skeleton_bone_count_frequency':dict(sorted(bone_counts.items())),
         'entity_resource_class_pair_frequency':dict(class_pairs.most_common()),'skeleton_families':skeleton_families,
         'structural_articulated_families':structural,'families':reports,'fatal_errors':fatal,
         'policy':'Structural family identity is based on exact decoded resources and ordered skeleton hashes. Gameplay archetype names are not inferred from package names, bone count, adjacency, or appearance.'}
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ('status','requested_family_count','probed_family_count','fatal_family_count','structural_articulated_family_count','skeleton_occurrence_count','unique_ordered_skeleton_family_count','skeleton_bone_count_frequency')},indent=2))
    return 0 if not fatal else 2

if __name__=='__main__':raise SystemExit(main())
