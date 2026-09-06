#!/usr/bin/env python3
"""Create a lossless, deduplicated export plan for every named D1 Guardian item.

Inputs:
  1. d1_playable_guardian_parent_resolve/v1: all named inventory rows plus exact
     masculine/feminine arrangement->EntityParent->EntityDataROI branches.
  2. d1_playable_guardian_entity_resource_resolve/v1: exact final s_entity
     Resource[]->EntityResource->embedded s_entity_model resolution.

The planner does not infer armor sets or merge retail arrangements by names. Every
(class, arrangement, body-role) branch remains a distinct visual export identity.
Geometry/model payloads are separately deduplicated as a cache optimization, so two
retail arrangements can reuse one model without losing their independent identity.
Every named inventory item remains in an alias table mapped back to its exact branch.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
from pathlib import Path


def key(class_name,arrangement):
    return (str(class_name),int(arrangement))


def model_tags(entity:dict|None)->tuple[str,...]:
    if not isinstance(entity,dict):return ()
    out=[]
    for r in entity.get('resources',[]):
        m=r.get('embedded_model') or {}
        if m.get('resolved') and m.get('tag_hash'):
            out.append(str(m['tag_hash']).upper())
    return tuple(dict.fromkeys(out))


def resource_tags(entity:dict|None)->tuple[str,...]:
    if not isinstance(entity,dict):return ()
    return tuple(str(x.get('resource_hash')).upper() for x in entity.get('resources',[]) if x.get('resource_hash'))


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('entity_resolution',type=Path)
    ap.add_argument('render_resolution',type=Path)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()

    parent=json.loads(a.entity_resolution.read_text())
    render=json.loads(a.render_resolution.read_text())
    if parent.get('schema')!='d1_playable_guardian_parent_resolve/v1':
        raise ValueError(f'wrong parent schema {parent.get("schema")!r}')
    if render.get('schema')!='d1_playable_guardian_entity_resource_resolve/v1':
        raise ValueError(f'wrong render schema {render.get("schema")!r}')

    render_by={key(x.get('className'),x['arrangement_index']):x for x in render.get('arrangements',[])}
    parent_by={key(x.get('className'),x['arrangement_index']):x for x in parent.get('arrangements',[])}
    missing_render=sorted(set(parent_by)-set(render_by))
    extra_render=sorted(set(render_by)-set(parent_by))

    exports=[];by_export={};geometry_consumers=collections.defaultdict(list);model_consumers=collections.defaultdict(list)
    status_counts=collections.Counter();body_counts=collections.Counter();class_counts=collections.Counter()
    for k in sorted(parent_by):
        pa=parent_by[k];ra=render_by.get(k) or {}
        rendered={str(x.get('body_role')):x for x in ra.get('resolved_body_assignments',[])}
        for pb in pa.get('resolved_body_assignments',[]):
            role=str(pb.get('body_role') or 'unclassified')
            rb=rendered.get(role)
            if rb is None:
                # Fall back to exact parent/entity hash match when a shared/multiple branch label exists.
                target=str(pb.get('entity_data_hash') or '').upper()
                for x in ra.get('resolved_body_assignments',[]):
                    if str(x.get('entity_data_hash') or '').upper()==target:
                        rb=x;break
            ent=(rb or {}).get('entity_resolution') if rb else None
            models=model_tags(ent);resources=resource_tags(ent)
            if not pb.get('entity_data_hash'):
                status='missing_final_entity'
            elif rb is None:
                status='missing_render_branch'
            elif not isinstance(ent,dict) or not ent.get('resolved'):
                status='unresolved_final_entity'
            elif not ent.get('is_s_entity'):
                status='non_s_entity_final_resource'
            elif not models:
                status='resolved_entity_no_embedded_model'
            else:
                status='render_graph_resolved'
            eid=f'{k[0]}:{k[1]}:{role}'
            geom='|'.join(models) if models else None
            row={
              'export_id':eid,'className':k[0],'arrangement_index':k[1],'body_role':role,
              'assignment_hash':pb.get('assignment_hash'),'parent_hash':pb.get('parent_hash'),
              'entity_hash':str(pb.get('entity_data_hash') or '').upper() or None,
              'status':status,'resource_hashes':list(resources),'model_hashes':list(models),
              'geometry_signature':geom,'item_count':int(pa.get('item_count') or 0),
              'item_types':list(pa.get('types') or []),'examples':list(pa.get('examples') or []),
            }
            exports.append(row);by_export[eid]=row;status_counts[status]+=1;body_counts[role]+=1;class_counts[k[0]]+=1
            if geom:geometry_consumers[geom].append(eid)
            for m in models:model_consumers[m].append(eid)

    # Lossless named item aliases from the upstream item-level table.
    aliases=[];unmapped=[]
    export_ids_by_arr=collections.defaultdict(list)
    for x in exports:export_ids_by_arr[key(x['className'],x['arrangement_index'])].append(x['export_id'])
    for item in parent.get('items',[]):
        k=key(item.get('className'),item['arrangement_index'])
        targets=[]
        for b in item.get('resolved_body_assignments',[]):
            role=str(b.get('body_role') or 'unclassified')
            eid=f'{k[0]}:{k[1]}:{role}'
            if eid in by_export:targets.append(eid)
            else:
                ent=str(b.get('entity_data_hash') or '').upper()
                matches=[x['export_id'] for x in exports if x['className']==k[0] and x['arrangement_index']==k[1] and x['entity_hash']==ent]
                targets.extend(matches)
        targets=list(dict.fromkeys(targets))
        if not targets:targets=list(export_ids_by_arr.get(k,[]))
        rec={'hash':item.get('hash'),'name':item.get('name'),'className':item.get('className'),
             'itemTypeName':item.get('itemTypeName'),'tier':item.get('tier'),'arrangement_index':item.get('arrangement_index'),
             'export_ids':targets}
        aliases.append(rec)
        if not targets:unmapped.append(rec)

    geometry=[{'geometry_signature':g,'model_hashes':g.split('|'),'consumer_count':len(ids),'export_ids':ids}
              for g,ids in sorted(geometry_consumers.items())]
    models=[{'model_hash':m,'consumer_count':len(ids),'export_ids':ids} for m,ids in sorted(model_consumers.items())]
    out={
      'schema':'d1_guardian_visual_export_plan/v1','status':'D1_GUARDIAN_VISUAL_EXPORT_PLAN_COMPLETE' if not missing_render and not unmapped else 'D1_GUARDIAN_VISUAL_EXPORT_PLAN_PARTIAL',
      'source':{'entity_resolution':str(a.entity_resolution),'entity_resolution_sha256':hashlib.sha256(a.entity_resolution.read_bytes()).hexdigest(),
                'render_resolution':str(a.render_resolution),'render_resolution_sha256':hashlib.sha256(a.render_resolution.read_bytes()).hexdigest()},
      'named_item_count':len(aliases),'arrangement_count':len(parent_by),'visual_branch_count':len(exports),
      'render_graph_resolved_branch_count':status_counts['render_graph_resolved'],
      'unique_geometry_signature_count':len(geometry),'unique_model_hash_count':len(models),
      'status_counts':dict(status_counts),'class_branch_counts':dict(class_counts),'body_role_counts':dict(body_counts),
      'missing_render_arrangements':[{'className':x[0],'arrangement_index':x[1]} for x in missing_render],
      'extra_render_arrangements':[{'className':x[0],'arrangement_index':x[1]} for x in extra_render],
      'unmapped_named_items':unmapped,
      'exports':exports,'named_item_aliases':aliases,'geometry_cache':geometry,'model_cache':models,
      'policy':(
        'Every retail (class, arrangement, body-role) remains a distinct export identity. Geometry/model payload hashes may be '
        'cached once and reused, but retail arrangements/items are never semantically deduplicated from names or visual similarity. '
        'No armor-set grouping is inferred from item names; set assembly requires an exact retail grouping edge or an explicitly requested user composition.'),
    }
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ('status','named_item_count','arrangement_count','visual_branch_count','render_graph_resolved_branch_count','unique_geometry_signature_count','unique_model_hash_count','status_counts','class_branch_counts','body_role_counts')},indent=2))
    return 0

if __name__=='__main__':raise SystemExit(main())
