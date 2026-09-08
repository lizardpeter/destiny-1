#!/usr/bin/env python3
"""Build a Blender inspection scene from corrected animated Tower actor GLBs.

The scene is deliberately an inspection representation, not a runtime-state claim:
- every corrected visual variant is imported exactly once as an unlinked asset collection;
- all imported actions are preserved with fake users, but no action/NLA track is selected;
- source placement alternatives become collection instances under one collection per
  source scenario, using the exact precomputed D1->glTF/Blender matrix;
- every scenario collection is hidden by default so the user explicitly chooses which
  source scenario to inspect;
- an optional card-corrected Tower environment GLB can be imported into the same file.

Run in Blender 5.2.1+::
  blender --background --factory-startup --python tools/d1_blender_build_tower_animated_inspection.py -- \
    --assembly-manifest D1_TOWER_ACTOR_PRODUCTION_ASSEMBLY_MANIFEST.json \
    --animated-dir models --environment-glb D1_TOWER_BAKED_PLUS_COMMON_TEXTURED_CARD_FIXED.glb \
    --out-blend D1_TOWER_ANIMATED_INSPECTION.blend --report inspection.json
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
    raw=sys.argv
    args=raw[raw.index('--')+1:] if '--' in raw else []
    ap=argparse.ArgumentParser()
    ap.add_argument('--assembly-manifest',type=Path,required=True)
    ap.add_argument('--animated-dir',type=Path,required=True)
    ap.add_argument('--environment-glb',type=Path)
    ap.add_argument('--out-blend',type=Path,required=True)
    ap.add_argument('--report',type=Path,required=True)
    return ap.parse_args(args)


def sha256(p:Path)->str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(8<<20),b''): h.update(b)
    return h.hexdigest()


def unlink_object_everywhere(obj):
    for c in list(obj.users_collection): c.objects.unlink(obj)


def import_glb_to_asset_collection(path:Path, key:str, assets_parent, action_index:dict):
    before_obj=set(bpy.data.objects)
    before_col=set(bpy.data.collections)
    before_actions=set(bpy.data.actions)
    bpy.ops.import_scene.gltf(filepath=str(path.resolve()), import_pack_images=True)
    new_obj=[o for o in bpy.data.objects if o not in before_obj]
    new_col=[c for c in bpy.data.collections if c not in before_col]
    new_actions=[x for x in bpy.data.actions if x not in before_actions]
    if not new_obj: raise RuntimeError(f'{key}: glTF import created no objects')
    asset=bpy.data.collections.new(f'D1_ASSET_{key.replace(":","_")}')
    assets_parent.children.link(asset)
    for o in new_obj:
        unlink_object_everywhere(o)
        asset.objects.link(o)
        o['d1VisualVariantKey']=key
        if o.animation_data is not None:
            o.animation_data.action=None
            for tr in list(o.animation_data.nla_tracks): o.animation_data.nla_tracks.remove(tr)
    for act in new_actions:
        act.use_fake_user=True
        act['d1VisualVariantKey']=key
    # Remove importer-created collections that became empty after rehoming objects.
    for c in new_col:
        if c is asset: continue
        if len(c.objects)==0 and len(c.children)==0:
            try: bpy.data.collections.remove(c)
            except Exception: pass
    # The asset collection must exist as a datablock but not draw at source origin.
    if asset.name in [c.name for c in assets_parent.children]:
        assets_parent.children.unlink(asset)
    action_index[key]=sorted(a.name for a in new_actions)
    return asset,new_obj,new_actions


def import_environment(path:Path):
    before=set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(path.resolve()), import_pack_images=True)
    new=[o for o in bpy.data.objects if o not in before]
    env=bpy.data.collections.new('D1_TOWER_ENVIRONMENT_CARD_FIXED')
    bpy.context.scene.collection.children.link(env)
    for o in new:
        unlink_object_everywhere(o); env.objects.link(o)
    env['d1SourceGLB']=path.name
    env['d1SourceGLBSha256']=sha256(path)
    return env,new


def main():
    a=cli()
    m=json.loads(a.assembly_manifest.read_text())
    if m.get('status')!='D1_TOWER_ACTOR_PRODUCTION_ASSEMBLY_MANIFEST_COMPLETE' or m.get('violations'):
        raise SystemExit('assembly manifest is not green')
    if int(m.get('used_visual_variant_count',-1))!=29 or int(m.get('placement_alternative_count',-1))!=547:
        raise SystemExit('unexpected assembly population')
    if any(v is not False for v in (m.get('gates') or {}).values()):
        raise SystemExit('assembly manifest promoted a runtime gate')

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene=bpy.context.scene
    scene['d1InspectionOnly']=True
    scene['d1RuntimeScenarioSelected']=False
    scene['d1RuntimeActorAnimationStateSelected']=False

    env_info=None
    if a.environment_glb is not None:
        if not a.environment_glb.is_file(): raise SystemExit(f'environment GLB missing: {a.environment_glb}')
        env,new=import_environment(a.environment_glb)
        env_info={'file':a.environment_glb.name,'sha256':sha256(a.environment_glb),'object_count':len(new)}

    # Temporary scene-linked parent used only while the importer is active.
    assets_parent=bpy.data.collections.new('D1_ACTOR_ASSET_LIBRARY_INTERNAL')
    scene.collection.children.link(assets_parent)
    asset_by_key={}; action_index={}; asset_rows=[]
    for v in sorted(m['variant_assets'],key=lambda x:x['visual_variant_key']):
        key=v['visual_variant_key']
        name=v['textured_glb_basename'][:-4]+'_ALL_ACTIONS.glb'
        p=a.animated_dir/name
        if not p.is_file(): raise SystemExit(f'{key}: animated actor GLB missing: {p}')
        asset,objs,actions=import_glb_to_asset_collection(p,key,assets_parent,action_index)
        asset_by_key[key]=asset
        asset['d1VisualVariantKey']=key
        asset['d1Model']=v['model']
        asset['d1SignatureIndex']=int(v['signature_index'])
        asset['d1ActionCount']=int(v['action_count'])
        asset['d1SourceGLBSha256']=sha256(p)
        if len(actions)!=int(v['action_count']):
            raise RuntimeError(f'{key}: Blender imported {len(actions)} actions, expected {v["action_count"]}')
        asset_rows.append({'visual_variant_key':key,'file':p.name,'sha256':sha256(p),'object_count':len(objs),'action_count':len(actions)})
    # No raw source asset collections are linked into the scene; only instances are.
    scene.collection.children.unlink(assets_parent)
    bpy.data.collections.remove(assets_parent)

    scenarios_root=bpy.data.collections.new('D1_TOWER_SOURCE_SCENARIOS_TOGGLE_ONE')
    scene.collection.children.link(scenarios_root)
    scenario_cols={}
    for s in m['scenarios']:
        h=s['scenario']
        c=bpy.data.collections.new(f'D1_SCENARIO_{h}_SOURCE_ALTERNATIVES')
        scenarios_root.children.link(c)
        c.hide_viewport=True; c.hide_render=True
        c['d1ScenarioHash']=h
        c['d1RuntimeActive']=False
        c['d1PlacementAlternativeCount']=int(s['placement_alternative_count'])
        scenario_cols[h]=c

    placement_count=0
    for r in m['placements']:
        key=r['visual_variant_key']; scenario=r['scenario']
        asset=asset_by_key[key]; col=scenario_cols[scenario]
        name=f'D1_{scenario}_{r["d912"]}_L{int(r["location_index"]):02d}_{r["entity_hash"]}_{key.replace(":","_")}'
        e=bpy.data.objects.new(name,None)
        e.empty_display_type='PLAIN_AXES'; e.instance_type='COLLECTION'; e.instance_collection=asset
        e.matrix_world=Matrix(r['gltf_node_matrix'])
        e['d1Scenario']=scenario; e['d1D912']=r['d912']; e['d1Entity']=r['entity_hash']
        e['d1Model']=r['model']; e['d1VisualVariantKey']=key
        e['d1LocationIndex']=int(r['location_index']); e['d1CandidateGroupIndex']=int(r['candidate_group_index'])
        e['d1RuntimeActive']=False; e['d1RuntimeAnimationStateSelected']=False
        col.objects.link(e); placement_count+=1
    if placement_count!=547: raise RuntimeError(f'placed {placement_count}, expected 547')

    # Durable in-file explanation and action index.
    text=bpy.data.texts.new('D1_TOWER_INSPECTION_README')
    text.write('Destiny 1 Tower inspection scene.\n')
    text.write('All eight scenario collections are hidden by default. Enable ONE D1_SCENARIO_* collection to inspect its source alternatives.\n')
    text.write('No scenario, D912 group, location, or animation action is claimed runtime-active.\n')
    text.write('Actor asset actions are preserved with fake users but intentionally unselected. Choose an Action in the Action Editor to inspect motion.\n')
    text.write('The 80CA0B97 card-corrected environment is included only when an environment GLB was supplied.\n')
    idx=bpy.data.texts.new('D1_TOWER_ACTOR_ACTION_INDEX_JSON')
    idx.write(json.dumps(action_index,indent=2))

    # Embedded images must survive as a self-contained inspection file.
    packed=0
    for im in bpy.data.images:
        if im.source=='FILE' and im.packed_file is None:
            try: im.pack(); packed+=1
            except Exception: pass

    a.out_blend.parent.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(a.out_blend.resolve()))
    report={
        'schema_version':1,'status':'D1_TOWER_ANIMATED_BLENDER_INSPECTION_COMPLETE',
        'blend':str(a.out_blend),'blend_bytes':a.out_blend.stat().st_size,'blend_sha256':sha256(a.out_blend),
        'environment':env_info,'actor_asset_variant_count':len(asset_rows),'scenario_collection_count':len(scenario_cols),
        'placement_alternative_instance_count':placement_count,'total_action_datablocks':len(bpy.data.actions),
        'packed_image_count':sum(1 for im in bpy.data.images if im.packed_file is not None),
        'newly_packed_image_count':packed,'assets':asset_rows,
        'runtime_active_scenario_selected':False,'runtime_active_D912_group_selected':False,
        'runtime_active_actor_location_selected':False,'runtime_actor_animation_state_selected':False,
        'policy':'Inspection-only Blender scene. Scenario collections and actions are deliberately unselected. Exact corrected actor assets are instanced at source alternative transforms; runtime activation remains unresolved.'
    }
    a.report.parent.mkdir(parents=True,exist_ok=True); a.report.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ('status','blend_bytes','blend_sha256','actor_asset_variant_count','scenario_collection_count','placement_alternative_instance_count','total_action_datablocks','packed_image_count')},indent=2))

if __name__=='__main__': main()
