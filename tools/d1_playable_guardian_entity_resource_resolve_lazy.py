#!/usr/bin/env python3
"""Lazy exact-FileHash implementation of Guardian entity/resource/model resolution.

Produces the same d1_playable_guardian_entity_resource_resolve/v1 schema as the
older eager resolver, but opens package families only when an exact serialized
FileHash requires them.  This is intended for the complete 2,157-arrangement
Guardian corpus and other large entity graphs.
"""
from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))

from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_model_tgxm_signature_match import LazyExactHashResolver,package_of_hash,norm_hash
from d1_remote_s_entity_resource_package_find import S_ENTITY_REF,parse_entity_resources
from d1_entity_resource_probe import ENTITY_RESOURCE_CLASS,parse_resource
from d1_split_tar_extract import SplitHttpTar

ENTITY_MODEL_CLASS='80801AB5'


def resolve_model(tag,resolver):
    tag=norm_hash(tag);pkg=package_of_hash(tag)
    out={'tag_hash':tag,'package_id':pkg}
    try:
        v,e=resolver.locate(tag)
        return {**out,'file_index':int(e['index']),'resolved':True,'reference':str(e['reference']).upper(),
                'type':int(e['type']),'subtype':int(e['subtype']),'size':int(e['file_size']),'logical_view':v.view.name}
    except Exception as ex:return {**out,'resolved':False,'reason':repr(ex)}


def resolve_resource(row,resolver):
    tag=norm_hash(row['resource_hash']);out=dict(row)
    try:
        v,e,b=resolver.bytes(tag);ref=str(e['reference']).upper()
        out.update({'resolved':True,'file_index':int(e['index']),'reference':ref,'type':int(e['type']),'subtype':int(e['subtype']),
                    'size':int(e['file_size']),'logical_view':v.view.name})
        if ref==ENTITY_RESOURCE_CLASS:
            p=parse_resource(b,'PS4');out['entity_resource']=p;out['semantic_role']=p.get('semantic_role')
            m=p.get('embedded_model_tag_hash')
            if m and m not in ('00000000','FFFFFFFF'):out['embedded_model']=resolve_model(m,resolver)
        elif ref==ENTITY_MODEL_CLASS:
            out['semantic_role']='direct_entity_model';out['embedded_model']=resolve_model(tag,resolver)
        else:out['semantic_role']='other_direct_resource'
    except Exception as ex:out.update({'resolved':False,'reason':repr(ex)})
    return out


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('entity_resolution',type=Path)
    ap.add_argument('--member-catalog',type=Path,action='append',required=True)
    ap.add_argument('--base-url',default='https://crypt.cohae.dev/destiny/ps4/packages/latest')
    ap.add_argument('--part-count',type=int,default=10)
    ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args()
    src=json.loads(a.entity_resolution.read_text())
    if src.get('schema')!='d1_playable_guardian_parent_resolve/v1':raise ValueError(f'wrong input schema {src.get("schema")!r}')
    cats=load_catalogs(a.member_catalog);base=a.base_url.rstrip('/')
    arc=SplitHttpTar([f'{base}/packages.tar.{i:03d}' for i in range(1,a.part_count+1)],retries=6,timeout=90)
    resolver=LazyExactHashResolver(arc,cats,a.runtime)

    ctx=collections.defaultdict(list)
    for arr in src.get('arrangements',[]):
        for br in arr.get('resolved_body_assignments',[]):
            tag=br.get('entity_data_hash')
            if tag:
                ctx[norm_hash(tag)].append({'className':arr.get('className'),'arrangement_index':arr.get('arrangement_index'),
                                            'body_role':br.get('body_role'),'parent_hash':br.get('parent_hash'),'examples':arr.get('examples',[])})
    entities={};resource_pkg_counts=collections.Counter();role_counts=collections.Counter();model_pkg_counts=collections.Counter();errors=[]
    for n,tag in enumerate(sorted(ctx),1):
        pkg=package_of_hash(tag);rec={'entity_hash':tag,'package_id':pkg,'contexts':ctx[tag]}
        try:
            v,e,b=resolver.bytes(tag);ref=str(e['reference']).upper()
            rec.update({'resolved':True,'file_index':int(e['index']),'reference':ref,'type':int(e['type']),'subtype':int(e['subtype']),
                        'size':int(e['file_size']),'logical_view':v.view.name})
            if ref!=S_ENTITY_REF:
                rec['is_s_entity']=False;rec['reason']=f'final EntityDataROI reference is {ref}, not {S_ENTITY_REF}'
            else:
                raw=parse_entity_resources(b);resources=[resolve_resource(x,resolver) for x in raw]
                rec.update({'is_s_entity':True,'resource_count':len(resources),'resources':resources})
                for x in resources:
                    if x.get('resource_package_id') is not None:resource_pkg_counts[f"{int(x['resource_package_id']):04X}"]+=1
                    if x.get('semantic_role'):role_counts[x['semantic_role']]+=1
                    m=x.get('embedded_model') or {}
                    if m.get('resolved'):model_pkg_counts[f"{int(m['package_id']):04X}"]+=1
        except Exception as ex:
            rec.update({'resolved':False,'reason':repr(ex)});errors.append({'entity_hash':tag,'error':repr(ex)})
        entities[tag]=rec
        if n%100==0 or n==len(ctx):print(f'ENTITIES {n}/{len(ctx)} package_views={len(resolver.views)} errors={len(errors)}',flush=True)

    arrangements=[]
    for arr in src.get('arrangements',[]):
        branches=[]
        for br in arr.get('resolved_body_assignments',[]):
            tag=br.get('entity_data_hash');branches.append({**br,'entity_resolution':entities.get(norm_hash(tag)) if tag else None})
        arrangements.append({**arr,'resolved_body_assignments':branches})
    models=[];seen=set()
    for ent in entities.values():
        for res in ent.get('resources',[]):
            m=res.get('embedded_model') or {};tag=m.get('tag_hash')
            if m.get('resolved') and tag not in seen:seen.add(tag);models.append(m)
    report={'schema':'d1_playable_guardian_entity_resource_resolve/v1','implementation':'lazy_exact_filehash/v1','source_schema':src.get('schema'),
            'entity_count':len(entities),'resolved_entity_count':sum(bool(x.get('resolved')) for x in entities.values()),
            's_entity_count':sum(bool(x.get('is_s_entity')) for x in entities.values()),
            'resource_occurrence_count':sum(len(x.get('resources',[])) for x in entities.values()),
            'resource_package_counts':dict(resource_pkg_counts.most_common()),'resource_role_counts':dict(role_counts.most_common()),
            'unique_embedded_model_count':len(models),'embedded_model_package_counts':dict(model_pkg_counts.most_common()),
            'catalog_package_ids':[f'{x:04X}' for x in sorted(cats)],'opened_package_ids':[f'{x:04X}' for x in sorted(resolver.views)],
            'opened_package_count':len(resolver.views),'entities':entities,'models':models,'arrangements':arrangements,'errors':errors,
            'policy':'EntityDataROI->s_entity Resource[]->EntityResource->embedded s_entity_model edges come only from retail bytes. Package views are opened only from exact encoded FileHashes; no name/locality inference.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ('entity_count','resolved_entity_count','s_entity_count','resource_occurrence_count','unique_embedded_model_count','opened_package_count','opened_package_ids')},indent=2))
    return 0 if not errors else 2

if __name__=='__main__':raise SystemExit(main())
