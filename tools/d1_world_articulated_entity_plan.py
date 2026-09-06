#!/usr/bin/env python3
"""Build an exporter-ready plan for source-owned articulated D1 world entities.

This is a pure evidence join. It consumes:
  * d1_world_activity_entity_resource_census.py placements,
  * d1_world_entity_dependency_census.py entity/resource classifications,
  * optionally d1_global_strings_resolve.py resolved retail names.

An articulated candidate is inherited only from the dependency census' proven
model+skeleton classification. This planner does not promote an object to NPC,
vendor, civilian, combatant, or other gameplay semantics by appearance or package
name.

Runtime instances come from the placement census' WorldID-deduplicated view. The
full set of serialized Activity/F603 source references remains attached to every
runtime placement, so scenario duplication is preserved as provenance without
spawning the same WorldID repeatedly in an exported scene.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

NULLS={'00000000','FFFFFFFF'}
RUNTIME_RIG_PAIR=('808008B2','8080099B')
COMPOSITION_PAIR=('8080079A','80800610')


def norm(x):return str(x).upper().removeprefix('0X').zfill(8)

def pair_of(resource):
    er=resource.get('entity_resource') or {}
    return (er.get('unk10',{}).get('class_hash'),er.get('unk18',{}).get('class_hash'))

def runtime_placements(p):
    if p.get('unique_world_placements') is not None:
        return list(p.get('unique_world_placements',[]))
    # Compatibility fallback for historical manifests: retain one exact WorldID
    # only when repeated serializations are identical.
    by={}
    for key in ('direct_tables','tables'):
        for t in p.get(key,[]):
            for x in t.get('entries',[]):
                h=norm(x.get('entity_hash','FFFFFFFF'))
                if h in NULLS:continue
                wid=x.get('world_id_hex')
                row={'world_id':x.get('world_id'),'world_id_hex':wid,'entity_hash':h,
                     'rotation':x.get('rotation'),'translation':x.get('translation'),
                     'data_resource_class':(x.get('data_resource') or {}).get('resource_class'),
                     'serialized_reference_count':1,'duplicate_serialization_count':0,'serializations_consistent':True,
                     'source_references':[{'source_kind':x.get('source_kind'),'source_hash':x.get('source_hash'),'index':x.get('index'),'record_offset':x.get('record_offset')}]}
                if wid not in by:by[wid]=row
                else:
                    old=by[wid]
                    sig=lambda z:(z['entity_hash'],tuple(z.get('rotation') or []),tuple(z.get('translation') or []),z.get('data_resource_class'))
                    if sig(old)!=sig(row):raise ValueError(f'historical placement manifest has conflicting WorldID {wid}')
                    old['serialized_reference_count']+=1;old['duplicate_serialization_count']+=1;old['source_references']+=row['source_references']
    return [by[k] for k in sorted(by)]

def name_candidates(entity_row, strings):
    comp=entity_row.get('composition') or {}
    preferred=[norm(x) for x in comp.get('preferred_name_hashes',[])]
    specific={norm(x) for x in comp.get('specific_name_hashes',[])}
    generic={norm(x) for x in comp.get('generic_name_hashes',[])}
    resolved=(strings or {}).get('resolved_targets',{})
    out=[]
    for h in preferred:
        out.append({'string_hash':h,'kind':'specific' if h in specific else ('generic' if h in generic else 'unknown'),
                    'resolved_candidates':resolved.get(h,[])})
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--placements',type=Path,required=True)
    ap.add_argument('--entity-dependencies',type=Path,required=True)
    ap.add_argument('--global-strings',type=Path)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    p=json.loads(a.placements.read_text());d=json.loads(a.entity_dependencies.read_text());s=json.loads(a.global_strings.read_text()) if a.global_strings else None
    by_entity=defaultdict(list)
    runtime_rows=runtime_placements(p)
    for row in runtime_rows:
        h=norm(row.get('entity_hash','FFFFFFFF'))
        if h not in NULLS:by_entity[h].append(row)
    candidates=[];families=defaultdict(lambda:{'entities':set(),'models':set(),'skeleton_resources':set(),'runtime_rig_resources':set(),'runtime_placements':0,'serialized_references':0})
    missing_placement=[]
    for e in d.get('entities',[]):
        comp=e.get('composition') or {};cls=comp.get('classification')
        if cls not in {'rigged_articulated_entity_candidate','model_skeleton_articulated_candidate'}:continue
        eh=norm(e['entity']);models=[];model_parents=[];skeletons=[];rigs=[];compositions=[];physics=[];children=[]
        for r in e.get('resources',[]):
            er=r.get('entity_resource') or {};role=er.get('semantic_role');pair=pair_of(r)
            if role=='entity_model':
                model_parents.append(r['resource_hash'])
                mh=er.get('embedded_model_tag_hash')
                if mh:models.append(norm(mh))
            elif role=='entity_skeleton':
                skeletons.append({'resource_hash':r['resource_hash'],**(r.get('skeleton') or {})})
            elif role=='entity_physics':physics.append({'resource_hash':r['resource_hash'],'model':er.get('embedded_physics_model_tag_hash')})
            elif role=='entity_children':children.append(r['resource_hash'])
            if pair==RUNTIME_RIG_PAIR:rigs.append(r['resource_hash'])
            if pair==COMPOSITION_PAIR:compositions.append(r['resource_hash'])
        placements=[]
        for x in by_entity.get(eh,[]):
            placements.append({'world_id':x.get('world_id'),'world_id_hex':x.get('world_id_hex'),
                               'rotation':x.get('rotation'),'translation':x.get('translation'),
                               'data_resource_class':x.get('data_resource_class'),
                               'serialized_reference_count':x.get('serialized_reference_count',1),
                               'duplicate_serialization_count':x.get('duplicate_serialization_count',0),
                               'source_references':x.get('source_references',[])})
        if not placements:missing_placement.append(eh)
        names=name_candidates(e,s)
        family_key='|'.join([','.join(sorted(set(models))),','.join(sorted(x['resource_hash'] for x in skeletons)),','.join(sorted(set(rigs)))])
        serialized_count=sum(x.get('serialized_reference_count',1) for x in placements)
        row={'entity':eh,'classification':cls,'npc_semantic_proven':False,'model_parent_resources':sorted(set(model_parents)),
             'models':sorted(set(models)),'skeletons':skeletons,'runtime_rig_resources':sorted(set(rigs)),
             'composition_resources':sorted(set(compositions)),'physics_resources':physics,'children_resources':sorted(set(children)),
             'name_candidates':names,'runtime_placement_count':len(placements),'serialized_placement_reference_count':serialized_count,
             'placements':placements,'family_key':family_key,
             'geometry_export_ready':bool(models),'rig_export_candidate':bool(models and skeletons and rigs)}
        candidates.append(row)
        f=families[family_key];f['entities'].add(eh);f['models'].update(models);f['skeleton_resources'].update(x['resource_hash'] for x in skeletons);f['runtime_rig_resources'].update(rigs);f['runtime_placements']+=len(placements);f['serialized_references']+=serialized_count
    fam_rows=[]
    for key,v in sorted(families.items()):
        fam_rows.append({'family_key':key,'entity_count':len(v['entities']),'entities':sorted(v['entities']),'models':sorted(v['models']),
                         'skeleton_resources':sorted(v['skeleton_resources']),'runtime_rig_resources':sorted(v['runtime_rig_resources']),
                         'runtime_placement_count':v['runtime_placements'],'serialized_placement_reference_count':v['serialized_references']})
    model_counts=Counter(m for c in candidates for m in c['models']);skeleton_counts=Counter(x['resource_hash'] for c in candidates for x in c['skeletons']);rig_counts=Counter(r for c in candidates for r in c['runtime_rig_resources'])
    out={'schema_version':2,'status':'D1_WORLD_ARTICULATED_ENTITY_PLAN_COMPLETE' if not missing_placement else 'D1_WORLD_ARTICULATED_ENTITY_PLAN_PARTIAL',
         'candidate_count':len(candidates),'rig_export_candidate_count':sum(c['rig_export_candidate'] for c in candidates),
         'family_count':len(fam_rows),'runtime_placement_count':sum(c['runtime_placement_count'] for c in candidates),
         'serialized_placement_reference_count':sum(c['serialized_placement_reference_count'] for c in candidates),
         'duplicate_serialized_reference_count':sum(c['serialized_placement_reference_count']-c['runtime_placement_count'] for c in candidates),
         'unique_model_count':len(model_counts),'unique_models':sorted(model_counts),'model_reference_counts':dict(model_counts),
         'unique_skeleton_resource_count':len(skeleton_counts),'skeleton_reference_counts':dict(skeleton_counts),
         'unique_runtime_rig_resource_count':len(rig_counts),'runtime_rig_reference_counts':dict(rig_counts),
         'missing_placement_entities':missing_placement,'families':fam_rows,'candidates':candidates,
         'policy':'Candidate membership comes only from model+skeleton evidence. Runtime scene instances are unique WorldIDs whose repeated source serializations were proven identical by the placement census; all Activity/F603 source references remain attached as provenance. Retail names are evidence candidates and do not by themselves assign NPC/vendor/combatant semantics.'}
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ('status','candidate_count','rig_export_candidate_count','family_count','runtime_placement_count','serialized_placement_reference_count','duplicate_serialized_reference_count','unique_model_count','unique_models','unique_skeleton_resource_count','unique_runtime_rig_resource_count','missing_placement_entities')},indent=2))
    return 0 if out['status'].endswith('_COMPLETE') else 2
if __name__=='__main__':raise SystemExit(main())
