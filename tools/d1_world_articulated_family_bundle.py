#!/usr/bin/env python3
"""Join source-owned D1 articulated evidence into one exporter contract per family.

This tool performs no package parsing. It combines already validated outputs:

* d1_world_articulated_entity_plan.py
* d1_world_entity_model_material_bindings.py
* d1_world_articulated_skin_census.py
* optionally d1_world_scripted_entity_identity_census.py + GlobalStrings output

The purpose is to make downstream GLB/animation export consume one fail-closed
ownership manifest instead of independently rediscovering model parents, skeletons,
materials, skin storage, runtime rigs, WorldIDs, or names.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

NULLS={'00000000','FFFFFFFF'}


def norm(x): return str(x).upper().removeprefix('0X').zfill(8)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--articulated-plan',type=Path,required=True)
    ap.add_argument('--material-bindings',type=Path,required=True)
    ap.add_argument('--skin-census',type=Path,required=True)
    ap.add_argument('--scripted-identity',type=Path)
    ap.add_argument('--scripted-strings',type=Path)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()

    plan=json.loads(a.articulated_plan.read_text())
    mats=json.loads(a.material_bindings.read_text())
    skin=json.loads(a.skin_census.read_text())
    identity=json.loads(a.scripted_identity.read_text()) if a.scripted_identity else None
    strings=json.loads(a.scripted_strings.read_text()) if a.scripted_strings else None

    candidates={x['entity']:x for x in plan.get('candidates',[])}
    mat_by_model=defaultdict(list)
    for b in mats.get('bindings',[]):
        mat_by_model[norm(b.get('model','FFFFFFFF'))].append(b)
    skin_by_model={norm(f.get('model','FFFFFFFF')):f for f in skin.get('families',[]) if f.get('model')}

    resolved=(strings or {}).get('resolved_targets',{})
    identity_by_world=defaultdict(list)
    if identity:
        for t in identity.get('scripted_tables',[]):
            for r in t.get('records',[]):
                wid=r.get('world_id_hex'); h=r.get('entity_name_string_hash')
                match=r.get('placement_match') or {}
                if not wid or not h or h in NULLS: continue
                if not (match.get('world_id_exists') and match.get('entity_matches')): continue
                identity_by_world[wid].append({
                    'entity_hash':norm(r.get('entity_hash','FFFFFFFF')),
                    'entity_name_string_hash':h,
                    'entity_name_candidates':resolved.get(h,[]),
                    'type_string_hash':r.get('type_string_hash'),
                    'type_candidates':resolved.get(r.get('type_string_hash'),[]),
                    'transform_matches':match.get('transform_matches'),
                    'scripted_table_source':r.get('source'),
                })

    rows=[]; violations=[]; frontiers=[]
    for fi,fam in enumerate(plan.get('families',[])):
        entities=[candidates[e] for e in fam.get('entities',[]) if e in candidates]
        models=sorted({norm(m) for e in entities for m in e.get('models',[])})
        parents=sorted({norm(p) for e in entities for p in e.get('model_parent_resources',[])})
        skeletons=[]
        for e in entities:
            for s in e.get('skeletons',[]):
                key=(norm(s.get('resource_hash','FFFFFFFF')),s.get('bone_count'))
                if key not in {(x['resource_hash'],x.get('bone_count')) for x in skeletons}:
                    skeletons.append({'resource_hash':key[0],**{k:v for k,v in s.items() if k!='resource_hash'}})
        rigs=sorted({norm(r) for e in entities for r in e.get('runtime_rig_resources',[])})
        placements=[]
        for e in entities:
            for p in e.get('placements',[]):
                wid=p.get('world_id_hex')
                placements.append({
                    'entity':e['entity'],
                    **p,
                    'scripted_identity':identity_by_world.get(wid,[]),
                })
        row={
            'family_index':fi,
            'family_key':fam.get('family_key'),
            'entities':sorted(e['entity'] for e in entities),
            'models':models,
            'model_parent_resources':parents,
            'skeletons':skeletons,
            'runtime_rig_resources':rigs,
            'runtime_placement_count':len(placements),
            'serialized_placement_reference_count':sum(p.get('serialized_reference_count',1) for p in placements),
            'placements':placements,
            'violations':[],
            'frontiers':[],
        }
        if len(models)!=1:
            row['violations'].append(f'model_count_{len(models)}_not_1')
        model=models[0] if len(models)==1 else None
        mb=mat_by_model.get(model,[]) if model else []
        row['material_bindings']=mb
        valid_m=[x for x in mb if x.get('validation_ok')]
        if not mb:
            row['violations'].append('material_binding_missing')
        elif len(valid_m)!=len(mb):
            row['violations'].append('material_binding_not_fully_valid')
        row['material_binding_ready']=bool(mb) and len(valid_m)==len(mb)

        sf=skin_by_model.get(model) if model else None
        row['skin_census']=sf
        if sf is None:
            row['violations'].append('skin_family_missing')
            row['skin_closed']=False
        else:
            if sf.get('violations'):
                row['violations'].append('skin_family_has_violations')
            sf_front=list(sf.get('frontiers',[]))
            if sf_front:
                row['frontiers'].extend(sf_front)
            row['skin_closed']=not sf.get('violations') and not sf_front

        row['skeleton_ready']=len(skeletons)==1 and isinstance(skeletons[0].get('bone_count'),int) and skeletons[0]['bone_count']>0
        if not row['skeleton_ready']:
            row['violations'].append('skeleton_not_unique_or_empty')
        row['static_pose_export_ready']=bool(model) and row['material_binding_ready']
        row['rigged_export_ready']=row['static_pose_export_ready'] and row['skeleton_ready'] and row['skin_closed']
        row['animation_owner_ready']=row['rigged_export_ready'] and len(rigs)==1
        row['named_runtime_placement_count']=sum(bool(p['scripted_identity']) for p in placements)
        rows.append(row)
        violations.extend(f'family[{fi}]:{x}' for x in row['violations'])
        frontiers.extend(f'family[{fi}]:{x}' for x in row['frontiers'])

    out={
        'schema_version':1,
        'status':'D1_WORLD_ARTICULATED_FAMILY_BUNDLE_PARTIAL' if violations else (
            'D1_WORLD_ARTICULATED_FAMILY_BUNDLE_FRONTIER' if frontiers else 'D1_WORLD_ARTICULATED_FAMILY_BUNDLE_COMPLETE'),
        'family_count':len(rows),
        'entity_owner_count':len({e for r in rows for e in r['entities']}),
        'runtime_placement_count':sum(r['runtime_placement_count'] for r in rows),
        'serialized_placement_reference_count':sum(r['serialized_placement_reference_count'] for r in rows),
        'static_pose_export_ready_family_count':sum(r['static_pose_export_ready'] for r in rows),
        'rigged_export_ready_family_count':sum(r['rigged_export_ready'] for r in rows),
        'animation_owner_ready_family_count':sum(r['animation_owner_ready'] for r in rows),
        'named_runtime_placement_count':sum(r['named_runtime_placement_count'] for r in rows),
        'families':rows,
        'frontiers':frontiers,
        'violations':violations,
        'policy':(
            'This is a pure evidence join. Geometry/material ownership, skin storage, skeletons, runtime rigs, and WorldIDs come only from upstream source-validated reports. Scripted names remain per-instance annotations and never rename reusable SEntity families.'
        ),
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ('status','family_count','entity_owner_count','runtime_placement_count','serialized_placement_reference_count','static_pose_export_ready_family_count','rigged_export_ready_family_count','animation_owner_ready_family_count','named_runtime_placement_count','frontiers','violations')},indent=2))
    return 2 if violations else 0


if __name__=='__main__': raise SystemExit(main())
