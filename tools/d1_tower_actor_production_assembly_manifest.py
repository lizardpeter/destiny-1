#!/usr/bin/env python3
"""Build the production handoff manifest for corrected Tower actor assets.

The manifest joins three already-independent layers without choosing runtime state:
  location alternative -> exact visual signature -> compatible shared action family.

It also serializes the proven D1 placement matrix in glTF coordinates:
    N = D1_ZUP_TO_GLTF_YUP @ transpose(System.Numerics row transform)

No active scenario, D912 group, actor location or animation state is selected.
"""
from __future__ import annotations

import argparse, collections, json, math
from pathlib import Path

A=(
    (1.0,0.0,0.0,0.0),
    (0.0,0.0,1.0,0.0),
    (0.0,-1.0,0.0,0.0),
    (0.0,0.0,0.0,1.0),
)


def norm(x): return str(x).upper().removeprefix('0X').zfill(8)


def matmul(a,b):
    return [[sum(float(a[i][k])*float(b[k][j]) for k in range(4)) for j in range(4)] for i in range(4)]


def transpose(m): return [[m[j][i] for j in range(4)] for i in range(4)]


def d1_row_matrix(rotation, translation):
    if len(rotation)!=4 or len(translation)<3: raise ValueError('bad D1 transform dimensions')
    x,y,z,w=[float(v) for v in rotation]; tx,ty,tz=[float(v) for v in translation[:3]]
    vals=(x,y,z,w,tx,ty,tz)
    if not all(math.isfinite(v) for v in vals): raise ValueError('non-finite D1 transform')
    qn=math.sqrt(x*x+y*y+z*z+w*w)
    if not (0.999<=qn<=1.001): raise ValueError(f'non-unit quaternion {qn}')
    x/=qn;y/=qn;z/=qn;w/=qn
    xx=x*x;yy=y*y;zz=z*z;xy=x*y;xz=x*z;yz=y*z;wx=w*x;wy=w*y;wz=w*z
    return [
        [1-2*(yy+zz),2*(xy+wz),2*(xz-wy),0.0],
        [2*(xy-wz),1-2*(xx+zz),2*(yz+wx),0.0],
        [2*(xz+wy),2*(yz-wx),1-2*(xx+yy),0.0],
        [tx,ty,tz,1.0],
    ]


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--location-visual-join',type=Path,required=True)
    ap.add_argument('--action-compatibility',type=Path,required=True)
    ap.add_argument('--visual-checkpoint',type=Path,required=True)
    ap.add_argument('-o','--out',type=Path,required=True)
    a=ap.parse_args()

    loc=json.loads(a.location_visual_join.read_text())
    act=json.loads(a.action_compatibility.read_text())
    vis=json.loads(a.visual_checkpoint.read_text())
    violations=[]
    if loc.get('status')!='D1_TOWER_ACTOR_LOCATION_VISUAL_SIGNATURE_JOIN_COMPLETE' or loc.get('violations'):
        violations.append('location_visual_join_not_green')
    if act.get('status')!='D1_TOWER_ACTOR_SHARED_ACTION_FAMILY_COMPATIBILITY_CLOSED' or act.get('violations'):
        violations.append('action_family_compatibility_not_green')
    if vis.get('status')!='D1_TOWER_ACTOR_PRODUCTION_VISUAL_CHECKPOINT_PINNED':
        violations.append('production_visual_checkpoint_not_pinned')
    tv=vis.get('textured_variant_checkpoint') or {}
    if int(tv.get('variant_count',-1))!=30 or int(tv.get('actor_model_count',-1))!=13 or int(tv.get('active_material_count',-1))!=320:
        violations.append('textured_variant_checkpoint_counts_wrong')

    action_by_model={}
    action_libs={}
    for r in act.get('models') or []:
        model=norm(r['model']); rep=norm(r['representative_model'])
        src_name=str(r['representative_action_glb'])
        if not src_name.endswith('_ALL_ACTIONS.glb'):
            violations.append(f'{model}:unexpected_action_library_name:{src_name}'); continue
        native_name=src_name[:-4]+'_NATIVE_D1.glb'
        row={
            'representative_model':rep,
            'skeleton':norm(r['skeleton']),
            'runtime_rig':norm(r['runtime_rig']),
            'control':norm(r['control']),
            'joint_count':int(r['joint_count']),
            'action_count':int(r['action_count']),
            'selector_state_count':int(r['selector_state_count']),
            'selected_clip_count':int(r['selected_clip_count']),
            'action_library_basename':native_name,
            'assignable_by_joint_name':bool(r['shared_action_library_assignable_by_joint_name']),
        }
        if not row['assignable_by_joint_name']: violations.append(f'{model}:action_library_not_assignable')
        action_by_model[model]=row
        key=(rep,row['skeleton'],row['control'])
        action_libs.setdefault(key,{**row,'models':[]})['models'].append(model)
    if len(action_by_model)!=13: violations.append(f'action_model_count_{len(action_by_model)}_not_13')
    if len(action_libs)!=6: violations.append(f'action_library_count_{len(action_libs)}_not_6')

    placements=[]; variant_usage=collections.Counter(); scenario_rows=collections.defaultdict(list)
    for i,r in enumerate(loc.get('exact_location_visual_alternatives') or []):
        model=norm(r['model']); af=action_by_model.get(model)
        if af is None:
            violations.append(f'placement_{i}:{model}:missing_action_family'); continue
        xyz=[float(x) for x in r['location'][:3]]; quat=[float(x) for x in r['rotation']]
        try: M=d1_row_matrix(quat,xyz); N=matmul(A,transpose(M))
        except Exception as ex:
            violations.append(f'placement_{i}:transform:{ex}'); continue
        key=str(r['visual_variant_key'])
        variant_usage[key]+=1
        row={
            'scenario':norm(r['scenario']),
            'd912':norm(r['d912']),
            'location_index':int(r['location_index']),
            'candidate_group_index':int(r['candidate_group_index']),
            'tail_unk2c':int(r['tail_unk2c']),
            'group_type_string_hash':norm(r['group_type_string_hash']),
            'entity_hash':norm(r['entity_hash']),
            'model':model,
            'visual_signature_index':int(r['visual_signature_index']),
            'visual_variant_key':key,
            'textured_glb_basename':str(r['textured_glb_basename']),
            'visual_signature_resolution':str(r['visual_signature_resolution']),
            'location_d1_xyz':xyz,
            'rotation_d1_xyzw':quat,
            'gltf_node_matrix':N,
            'action_family_representative_model':af['representative_model'],
            'action_library_basename':af['action_library_basename'],
            'action_count':af['action_count'],
            'runtime_animation_state_selected':False,
        }
        placements.append(row);scenario_rows[row['scenario']].append(row)

    expected=int(loc.get('exact_location_alternative_count',-1))
    if expected!=547 or len(placements)!=547: violations.append(f'placement_count_{len(placements)}_expected_{expected}_required_547')
    used=set(variant_usage)
    if len(used)!=29: violations.append(f'used_variant_count_{len(used)}_not_29')

    variant_assets=[]
    for key,count in sorted(variant_usage.items()):
        model,sigtext=key.split(':SIG'); si=int(sigtext); af=action_by_model[model]
        variant_assets.append({
            'visual_variant_key':key,'model':model,'signature_index':si,'placement_alternative_use_count':count,
            'textured_glb_basename':f'{model}_SIG{si:02d}_SKINNED_NATIVE_D1_TEXTURED.glb',
            'action_library_basename':af['action_library_basename'],'action_count':af['action_count'],
        })

    scenario_summary=[]
    for scenario,rows in sorted(scenario_rows.items()):
        scenario_summary.append({
            'scenario':scenario,'placement_alternative_count':len(rows),
            'unique_d912_count':len({x['d912'] for x in rows}),
            'unique_entity_count':len({x['entity_hash'] for x in rows}),
            'unique_model_count':len({x['model'] for x in rows}),
            'unique_visual_variant_count':len({x['visual_variant_key'] for x in rows}),
            'runtime_active':False,
        })

    out={
        'schema_version':1,
        'status':'D1_TOWER_ACTOR_PRODUCTION_ASSEMBLY_MANIFEST_COMPLETE' if not violations else 'D1_TOWER_ACTOR_PRODUCTION_ASSEMBLY_MANIFEST_PARTIAL',
        'actor_model_count':13,
        'available_visual_signature_count':30,
        'used_visual_variant_count':len(variant_assets),
        'unused_visual_variant_keys':['809D8104:SIG04'],
        'shared_action_library_count':len(action_libs),
        'scenario_count':len(scenario_summary),
        'placement_alternative_count':len(placements),
        'textured_variant_artifact':tv,
        'location_visual_join_artifact':vis.get('location_visual_join_checkpoint'),
        'transparency_artifact':vis.get('transparency_checkpoint'),
        'action_libraries':sorted(action_libs.values(),key=lambda x:(x['representative_model'],x['skeleton'],x['control'])),
        'variant_assets':variant_assets,
        'scenarios':scenario_summary,
        'placements':placements,
        'source_entities_without_exact_group_location':loc.get('source_entities_without_exact_group_location',[]),
        'ambiguous_location_groups_with_spawned_actor_overlap':loc.get('ambiguous_location_groups_with_spawned_actor_overlap',[]),
        'violations':violations,
        'coordinate_adapter':'gltf_node_matrix = D1_ZUP_TO_GLTF_YUP @ transpose(System.Numerics.CreateFromQuaternion+Translation row matrix)',
        'gates':{
            'runtime_active_scenario_selected':False,
            'runtime_active_D912_group_selected':False,
            'runtime_active_actor_location_selected':False,
            'runtime_actor_animation_state_selected':False,
            'D1_retail_descriptor_evaluator_source_closed':False,
        },
        'policy':'This is an assembly handoff over source alternatives. Each placement points to an exact corrected textured visual variant and a compatible full shared action library. It does not state which scenario/group/location or animation is active at runtime.'
    }
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:out[k] for k in ('status','actor_model_count','available_visual_signature_count','used_visual_variant_count','shared_action_library_count','scenario_count','placement_alternative_count','violations')},indent=2))
    return 0 if not violations else 2

if __name__=='__main__': raise SystemExit(main())
