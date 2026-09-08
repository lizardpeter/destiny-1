#!/usr/bin/env python3
"""Build a memory-efficient animated Tower Blender inspection scene.

Production representation:
- import the 29 used corrected TEXTURED visual variants exactly once;
- import the six shared native-D1 action-library GLBs only long enough to retain
  their Blender Action datablocks, then delete their representative geometry;
- annotate every visual armature with its exact compatible action-family identity;
- create collection instances for all 547 exact source placement alternatives,
  grouped under eight separately toggleable scenario collections;
- optionally import the card-corrected static/common Tower environment;
- leave every scenario and every Action unselected.

This file is for inspection, not a claim that all serialized alternatives are
simultaneously active in retail Destiny 1.
"""
from __future__ import annotations

import argparse, hashlib, json, sys
from pathlib import Path

try:
    import bpy
    from mathutils import Matrix
except Exception as ex:  # pragma: no cover
    raise SystemExit(f'This tool must run inside Blender Python: {ex!r}')


def cli():
    raw=sys.argv; args=raw[raw.index('--')+1:] if '--' in raw else []
    ap=argparse.ArgumentParser()
    ap.add_argument('--assembly-manifest',type=Path,required=True)
    ap.add_argument('--textured-dir',type=Path,required=True)
    ap.add_argument('--action-dir',type=Path,required=True)
    ap.add_argument('--environment-glb',type=Path)
    ap.add_argument('--out-blend',type=Path,required=True)
    ap.add_argument('--report',type=Path,required=True)
    return ap.parse_args(args)


def sha256(p:Path)->str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(8<<20),b''): h.update(b)
    return h.hexdigest()


def unlink_obj(obj):
    for c in list(obj.users_collection): c.objects.unlink(obj)


def remove_import_objects(objs):
    for o in objs:
        try: bpy.data.objects.remove(o,do_unlink=True)
        except Exception: pass


def purge_orphans():
    # Recursive orphan purge keeps datablocks used by the retained visual asset
    # collections and fake-user Action libraries.
    for _ in range(4):
        try:
            r=bpy.ops.outliner.orphans_purge(do_local_ids=True,do_linked_ids=True,do_recursive=True)
            if 'FINISHED' not in r: break
        except Exception:
            break


def import_environment(path:Path):
    before=set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(path.resolve()),import_pack_images=True)
    new=[o for o in bpy.data.objects if o not in before]
    if not new: raise RuntimeError('environment import created no objects')
    env=bpy.data.collections.new('D1_TOWER_ENVIRONMENT_CARD_FIXED')
    bpy.context.scene.collection.children.link(env)
    for o in new: unlink_obj(o); env.objects.link(o)
    env['d1SourceGLB']=path.name; env['d1SourceGLBSha256']=sha256(path)
    return {'file':path.name,'sha256':sha256(path),'object_count':len(new)}


def import_visual_asset(path:Path,key:str,model:str,sig:int):
    before_obj=set(bpy.data.objects); before_col=set(bpy.data.collections); before_actions=set(bpy.data.actions)
    bpy.ops.import_scene.gltf(filepath=str(path.resolve()),import_pack_images=True)
    new_obj=[o for o in bpy.data.objects if o not in before_obj]
    new_col=[c for c in bpy.data.collections if c not in before_col]
    new_actions=[x for x in bpy.data.actions if x not in before_actions]
    if not new_obj: raise RuntimeError(f'{key}: visual glTF import produced no objects')
    if new_actions: raise RuntimeError(f'{key}: textured visual unexpectedly imported {len(new_actions)} actions')
    asset=bpy.data.collections.new(f'D1_ASSET_{key.replace(":","_")}')
    bpy.context.scene.collection.children.link(asset)
    arms=[]
    for o in new_obj:
        unlink_obj(o); asset.objects.link(o)
        o['d1VisualVariantKey']=key; o['d1Model']=model; o['d1SignatureIndex']=sig
        if o.type=='ARMATURE': arms.append(o)
    if not arms: raise RuntimeError(f'{key}: visual asset has no armature')
    for c in new_col:
        if c is asset: continue
        if len(c.objects)==0 and len(c.children)==0:
            try: bpy.data.collections.remove(c)
            except Exception: pass
    # Asset collection exists only as an instance source, not at origin.
    bpy.context.scene.collection.children.unlink(asset)
    return asset,arms,len(new_obj)


def import_action_family(path:Path,representative:str,expected:int):
    before_obj=set(bpy.data.objects); before_col=set(bpy.data.collections); before_actions=set(bpy.data.actions)
    bpy.ops.import_scene.gltf(filepath=str(path.resolve()),import_pack_images=False)
    new_obj=[o for o in bpy.data.objects if o not in before_obj]
    new_col=[c for c in bpy.data.collections if c not in before_col]
    actions=[x for x in bpy.data.actions if x not in before_actions]
    if len(actions)!=expected:
        raise RuntimeError(f'{representative}: imported {len(actions)} actions, expected {expected}')
    rows=[]
    for i,act in enumerate(actions):
        old=act.name; act.name=f'D1_{representative}__{old}'; act.use_fake_user=True
        act['d1ActionFamilyRepresentative']=representative
        act['d1ActionFamilySourceGLB']=path.name
        act['d1ActionFamilySourceGLBSha256']=sha256(path)
        rows.append(act.name)
    remove_import_objects(new_obj)
    for c in new_col:
        if len(c.objects)==0 and len(c.children)==0:
            try: bpy.data.collections.remove(c)
            except Exception: pass
    purge_orphans()
    return rows


def main():
    a=cli(); m=json.loads(a.assembly_manifest.read_text())
    if m.get('status')!='D1_TOWER_ACTOR_PRODUCTION_ASSEMBLY_MANIFEST_COMPLETE' or m.get('violations'):
        raise SystemExit('assembly manifest is not green')
    if (m.get('used_visual_variant_count'),m.get('shared_action_library_count'),m.get('placement_alternative_count'))!=(29,6,547):
        raise SystemExit('unexpected assembly counts')
    if any(v is not False for v in (m.get('gates') or {}).values()): raise SystemExit('runtime gate promoted')

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene=bpy.context.scene
    scene['d1InspectionOnly']=True; scene['d1RuntimeScenarioSelected']=False; scene['d1RuntimeActorAnimationStateSelected']=False

    env=None
    if a.environment_glb:
        if not a.environment_glb.is_file(): raise SystemExit(f'environment missing: {a.environment_glb}')
        env=import_environment(a.environment_glb)

    asset_by_key={}; armatures_by_model={}; asset_rows=[]
    for v in sorted(m['variant_assets'],key=lambda x:x['visual_variant_key']):
        key=v['visual_variant_key']; model=v['model']; sig=int(v['signature_index'])
        p=a.textured_dir/v['textured_glb_basename']
        if not p.is_file(): raise SystemExit(f'{key}: textured GLB missing: {p}')
        asset,arms,nobj=import_visual_asset(p,key,model,sig)
        asset['d1VisualVariantKey']=key; asset['d1Model']=model; asset['d1SignatureIndex']=sig
        asset['d1SourceGLBSha256']=sha256(p)
        asset_by_key[key]=asset; armatures_by_model.setdefault(model,[]).extend(arms)
        asset_rows.append({'visual_variant_key':key,'model':model,'signature_index':sig,'file':p.name,'sha256':sha256(p),'object_count':nobj,'armature_count':len(arms)})

    action_rows=[]; action_names_by_rep={}
    for lib in sorted(m['action_libraries'],key=lambda x:x['representative_model']):
        rep=lib['representative_model']; p=a.action_dir/lib['action_library_basename']; expected=int(lib['action_count'])
        if not p.is_file(): raise SystemExit(f'{rep}: action library missing: {p}')
        names=import_action_family(p,rep,expected); action_names_by_rep[rep]=names
        action_rows.append({'representative_model':rep,'file':p.name,'sha256':sha256(p),'action_count':len(names),'models':sorted(lib['models'])})
        for model in lib['models']:
            for arm in armatures_by_model.get(model,[]):
                arm['d1ActionFamilyRepresentative']=rep
                arm['d1CompatibleActionCount']=expected
                arm['d1RuntimeAnimationStateSelected']=False
                if arm.animation_data is not None:
                    arm.animation_data.action=None
                    for tr in list(arm.animation_data.nla_tracks): arm.animation_data.nla_tracks.remove(tr)
    if len(action_rows)!=6 or sum(x['action_count'] for x in action_rows)<=0: raise RuntimeError('action family import incomplete')

    root=bpy.data.collections.new('D1_TOWER_SOURCE_SCENARIOS_TOGGLE_ONE')
    scene.collection.children.link(root); scenario_cols={}
    for s in m['scenarios']:
        h=s['scenario']; c=bpy.data.collections.new(f'D1_SCENARIO_{h}_SOURCE_ALTERNATIVES')
        root.children.link(c); c.hide_viewport=True; c.hide_render=True
        c['d1ScenarioHash']=h; c['d1RuntimeActive']=False; c['d1PlacementAlternativeCount']=int(s['placement_alternative_count'])
        scenario_cols[h]=c

    n=0
    for r in m['placements']:
        key=r['visual_variant_key']; c=scenario_cols[r['scenario']]
        e=bpy.data.objects.new(f'D1_{r["scenario"]}_{r["d912"]}_L{int(r["location_index"]):02d}_{r["entity_hash"]}_{key.replace(":","_")}',None)
        e.empty_display_type='PLAIN_AXES'; e.instance_type='COLLECTION'; e.instance_collection=asset_by_key[key]
        e.matrix_world=Matrix(r['gltf_node_matrix'])
        for k,v in {
            'd1Scenario':r['scenario'],'d1D912':r['d912'],'d1Entity':r['entity_hash'],'d1Model':r['model'],
            'd1VisualVariantKey':key,'d1LocationIndex':int(r['location_index']),'d1CandidateGroupIndex':int(r['candidate_group_index']),
            'd1RuntimeActive':False,'d1RuntimeAnimationStateSelected':False,
        }.items(): e[k]=v
        c.objects.link(e); n+=1
    if n!=547: raise RuntimeError(f'placement instance count {n} != 547')

    readme=bpy.data.texts.new('D1_TOWER_INSPECTION_README')
    readme.write('Destiny 1 Tower animated inspection scene.\n')
    readme.write('All eight D1_SCENARIO_* collections are hidden by default. Enable ONE to inspect its source alternatives.\n')
    readme.write('No scenario, D912 group, location, or animation state is claimed runtime-active.\n')
    readme.write('Actions are shared by exact compatible rig family. Select an actor armature and choose a D1_<family>__* Action in the Action Editor.\n')
    if env is None: readme.write('Static/common Tower environment is not embedded in this actor-only inspection file. Import D1_TOWER_BAKED_PLUS_COMMON_TEXTURED_CARD_FIXED.glb at identity.\n')
    idx=bpy.data.texts.new('D1_TOWER_ACTION_FAMILY_INDEX_JSON'); idx.write(json.dumps({'families':action_rows},indent=2))

    newly_packed=0
    for im in bpy.data.images:
        if im.source=='FILE' and im.packed_file is None:
            try: im.pack(); newly_packed+=1
            except Exception: pass

    a.out_blend.parent.mkdir(parents=True,exist_ok=True); bpy.ops.wm.save_as_mainfile(filepath=str(a.out_blend.resolve()))
    rep={
        'schema_version':2,'status':'D1_TOWER_ANIMATED_BLENDER_INSPECTION_V2_COMPLETE',
        'blend':str(a.out_blend),'blend_bytes':a.out_blend.stat().st_size,'blend_sha256':sha256(a.out_blend),
        'environment':env,'actor_asset_variant_count':len(asset_rows),'actor_model_count':len(armatures_by_model),
        'shared_action_family_count':len(action_rows),'shared_action_count':sum(x['action_count'] for x in action_rows),
        'scenario_collection_count':len(scenario_cols),'placement_alternative_instance_count':n,
        'packed_image_count':sum(1 for im in bpy.data.images if im.packed_file is not None),'newly_packed_image_count':newly_packed,
        'assets':asset_rows,'action_families':action_rows,
        'runtime_active_scenario_selected':False,'runtime_active_D912_group_selected':False,
        'runtime_active_actor_location_selected':False,'runtime_actor_animation_state_selected':False,
        'policy':'Inspection-only Blender scene. Exact corrected visual assets and shared compatible native-D1 Action families are retained once; source alternatives are instanced by exact placement matrix. Runtime activation remains fail-closed.'
    }
    a.report.parent.mkdir(parents=True,exist_ok=True); a.report.write_text(json.dumps(rep,indent=2)+'\n')
    print(json.dumps({k:rep[k] for k in ('status','blend_bytes','blend_sha256','actor_asset_variant_count','actor_model_count','shared_action_family_count','shared_action_count','scenario_collection_count','placement_alternative_instance_count','packed_image_count')},indent=2))

if __name__=='__main__': main()
