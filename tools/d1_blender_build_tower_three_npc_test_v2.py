#!/usr/bin/env python3
"""Build a corrected lightweight three-NPC Blender inspection file.

Differences from v1:
- visual GLBs are expected to have passed the conservative portable preview adapter;
- undo Blender glTF's +90deg X basis conversion at the actor root, because these
  source GLBs deliberately carry native D1 Z-up geometry/skin data underneath;
- assign one deterministic sampled Action to every test armature so pressing Play
  immediately demonstrates animation, while retaining the other sampled Actions.
"""
from __future__ import annotations

import argparse, hashlib, json, math, sys
from pathlib import Path

import bpy

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import d1_blender_build_tower_three_npc_test as v1


def cli():
    raw=sys.argv; args=raw[raw.index('--')+1:] if '--' in raw else []
    ap=argparse.ArgumentParser();ap.add_argument('--assembly-manifest',type=Path,required=True);ap.add_argument('--preview-dir',type=Path,required=True);ap.add_argument('--action-dir',type=Path,required=True);ap.add_argument('--out-blend',type=Path,required=True);ap.add_argument('--report',type=Path,required=True);ap.add_argument('--actions-per-family',type=int,default=4);return ap.parse_args(args)


def sha256(p:Path):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(8<<20),b''):h.update(b)
    return h.hexdigest()


def import_visual_upright(path:Path,key:str,xoff:float):
    before_obj=set(bpy.data.objects);before_actions=set(bpy.data.actions)
    bpy.ops.import_scene.gltf(filepath=str(path.resolve()),import_pack_images=True)
    new=[o for o in bpy.data.objects if o not in before_obj];acts=[x for x in bpy.data.actions if x not in before_actions]
    if not new: raise RuntimeError(f'{key}: no imported objects')
    if acts: raise RuntimeError(f'{key}: visual unexpectedly imported actions')
    arms=[o for o in new if o.type=='ARMATURE']
    if not arms: raise RuntimeError(f'{key}: no armature')
    root=bpy.data.objects.new(f'TEST_{key.replace(":","_")}',None);bpy.context.scene.collection.objects.link(root);root.empty_display_type='PLAIN_AXES'
    newset=set(new);roots=[o for o in new if o.parent not in newset]
    for o in roots:
        mw=o.matrix_world.copy();o.parent=root;o.matrix_world=mw
    # Blender's glTF importer interprets the native-D1 payload as glTF Y-up and
    # applies +90deg X. Undo exactly that at one parent root, leaving mesh/skin/
    # action data untouched beneath it.
    root.rotation_mode='XYZ';root.rotation_euler.x=-math.pi/2;root.location.x=float(xoff)
    root['d1VisualVariantKey']=key;root['d1LaptopTestAsset']=True;root['d1BlenderBasisCorrection']='ROT_X_NEG_90_AFTER_GLTF_IMPORT'
    for o in new:
        o['d1VisualVariantKey']=key;o['d1LaptopTestAsset']=True
    return root,arms,new


def action_span(a):
    r=a.frame_range
    return float(r[1]-r[0])


def main():
    a=cli();m=json.loads(a.assembly_manifest.read_text())
    if m.get('status')!='D1_TOWER_ACTOR_PRODUCTION_ASSEMBLY_MANIFEST_COMPLETE' or m.get('violations'): raise SystemExit('assembly manifest not green')
    wanted=[{'key':'80C88CEF:SIG03','label':'XUR','x':-3.0},{'key':'809D8104:SIG00','label':'MODEL_809D8104','x':0.0},{'key':'80C88434:SIG00','label':'MODEL_80C88434','x':3.0}]
    bykey={x['visual_variant_key']:x for x in m['variant_assets']}
    if any(w['key'] not in bykey for w in wanted): raise SystemExit('wanted variant missing')

    bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene
    scene['d1InspectionOnly']=True;scene['d1LaptopThreeNpcTestV2']=True;scene['d1RuntimeScenarioSelected']=False;scene['d1RuntimeActorAnimationStateSelected']=False;scene['d1TestPreviewAnimationAssigned']=True

    assets=[];arms_by_model={}
    for w in wanted:
        row=bykey[w['key']];p=a.preview_dir/row['textured_glb_basename']
        if not p.is_file(): raise SystemExit(f'{w["key"]}: preview GLB missing {p}')
        root,arms,objs=import_visual_upright(p,w['key'],w['x']);root.name=f'TEST_{w["label"]}_{w["key"].replace(":","_")}';root['d1Model']=row['model'];root['d1SignatureIndex']=int(row['signature_index']);root['d1SourcePreviewGLBSha256']=sha256(p)
        arms_by_model.setdefault(row['model'],[]).extend(arms)
        assets.append({'label':w['label'],'visual_variant_key':w['key'],'model':row['model'],'signature_index':int(row['signature_index']),'file':p.name,'sha256':sha256(p),'object_count':len(objs),'armature_count':len(arms),'root_rotation_x_radians':float(root.rotation_euler.x),'x_offset':w['x']})

    needed=set(arms_by_model);libs=[]
    for lib in m['action_libraries']:
        overlap=sorted(needed.intersection(lib['models']))
        if overlap: libs.append((lib,overlap))
    if set(x for _,ov in libs for x in ov)!=needed: raise RuntimeError('action family coverage mismatch')

    action_rows=[];assigned=[];starts=[];ends=[]
    for lib,overlap in sorted(libs,key=lambda x:x[0]['representative_model']):
        rep=lib['representative_model'];p=a.action_dir/lib['action_library_basename']
        chosen,source_count,source_sha=v1.import_action_sample(p,rep,a.actions_per_family)
        # Prefer a visibly non-zero-duration sample; tie-break by name.
        preview=sorted(chosen,key=lambda x:(-action_span(x),x.name))[0]
        fr=[float(preview.frame_range[0]),float(preview.frame_range[1])];starts.append(fr[0]);ends.append(fr[1])
        for model in overlap:
            for arm in arms_by_model[model]:
                arm.animation_data_create();arm.animation_data.action=preview
                arm['d1ActionFamilyRepresentative']=rep;arm['d1RetainedLaptopTestActionCount']=len(chosen);arm['d1TestPreviewActionAssigned']=preview.name;arm['d1RuntimeAnimationStateSelected']=False
                assigned.append({'armature':arm.name,'model':model,'action':preview.name,'frame_range':fr})
        action_rows.append({'representative_model':rep,'models_in_test':overlap,'file':p.name,'sha256':source_sha,'source_action_count':source_count,'retained_action_count':len(chosen),'retained_actions':[x.name for x in chosen],'preview_action':preview.name,'preview_frame_range':fr})

    scene.frame_start=int(math.floor(min(starts))) if starts else 0;scene.frame_end=max(scene.frame_start+1,int(math.ceil(max(ends)))) if ends else 1;scene.frame_set(scene.frame_start)

    readme=bpy.data.texts.new('D1_TOWER_3_NPC_TEST_V2_README');readme.write('Corrected lightweight Destiny 1 Tower NPC inspection file.\n\n');readme.write('Actors are upright through one -90 degree X root correction that undoes Blender glTF import of native-D1 Z-up payloads.\n');readme.write('Standard glTF COLOR_0 use is withheld in the source preview GLBs; only PROVEN portable base textures remain visible.\n');readme.write('Each armature already has a D1_TEST_* Action assigned. Press Play immediately. Other retained D1_TEST_* Actions remain available in Dope Sheet -> Action Editor.\n');readme.write('Assigned Actions are diagnostic samples only, NOT a claim of retail runtime-active state.\n')

    for im in bpy.data.images:
        if im.source=='FILE' and im.packed_file is None:
            try: im.pack()
            except Exception: pass
    for _ in range(4):
        try:
            r=bpy.ops.outliner.orphans_purge(do_local_ids=True,do_linked_ids=True,do_recursive=True)
            if 'FINISHED' not in r:break
        except Exception:break

    a.out_blend.parent.mkdir(parents=True,exist_ok=True);bpy.ops.wm.save_as_mainfile(filepath=str(a.out_blend.resolve()))
    rep={'schema_version':2,'status':'D1_TOWER_THREE_NPC_LAPTOP_TEST_V2_COMPLETE','blend':str(a.out_blend),'blend_bytes':a.out_blend.stat().st_size,'blend_sha256':sha256(a.out_blend),'actor_count':3,'model_count':len(needed),'action_family_count':len(action_rows),'retained_action_count':sum(x['retained_action_count'] for x in action_rows),'assigned_preview_action_count':len(assigned),'scene_frame_start':scene.frame_start,'scene_frame_end':scene.frame_end,'packed_image_count':sum(1 for im in bpy.data.images if im.packed_file is not None),'assets':assets,'action_families':action_rows,'assigned_preview_actions':assigned,'environment_present':False,'scenario_alternatives_present':False,'basis_adapter':'native D1 Z-up payload -> Blender glTF import (+90deg X) -> root -90deg X correction','runtime_animation_state_selected':False,'test_preview_animation_assigned':True,'policy':'Laptop inspection adapter. Preview Actions are deliberately assigned for testing but are not retail active-state claims.'}
    a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(rep,indent=2)+'\n');print(json.dumps({k:rep[k] for k in ('status','blend_bytes','blend_sha256','actor_count','retained_action_count','assigned_preview_action_count','scene_frame_start','scene_frame_end')},indent=2))

if __name__=='__main__':main()
