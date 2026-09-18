#!/usr/bin/env python3
"""Build a visually useful three-NPC Tower Blender checkpoint.

V4 intentionally replaces the V2/V3 handoff strategy:
- each input GLB is the exact target visual with its compatible action library
  already appended by exact joint name at glTF level;
- existing production portable texture previews are retained;
- only unsafe generic glTF COLOR_0 semantics were demoted upstream;
- one low-motion diagnostic clip is chosen per exact target only after pose and
  deformed-mesh sanity checks;
- Actions from one imported actor are never cross-assigned to another actor.

The selected preview clip is NOT called retail idle/default.  It is only the
lowest-motion sane selector-owned clip found for convenient Blender inspection.
"""
from __future__ import annotations

import argparse, hashlib, json, math, sys
from pathlib import Path

import bpy
from mathutils import Matrix, Vector


def cli():
    raw=sys.argv; args=raw[raw.index('--')+1:] if '--' in raw else []
    ap=argparse.ArgumentParser()
    ap.add_argument('--input-dir',type=Path,required=True)
    ap.add_argument('--plan',type=Path,required=True)
    ap.add_argument('--out-blend',type=Path,required=True)
    ap.add_argument('--report',type=Path,required=True)
    ap.add_argument('--retain-actions-per-actor',type=int,default=4)
    ap.add_argument('--candidate-limit',type=int,default=16)
    return ap.parse_args(args)


def sha256(p:Path):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(8<<20),b''): h.update(b)
    return h.hexdigest()


def assign_action(arm,act):
    ad=arm.animation_data_create(); ad.action=act
    slots=list(ad.action_suitable_slots)
    if not slots: slots=list(act.slots)
    if len(slots)!=1:
        raise RuntimeError(f'{arm.name}/{act.name}: compatible ActionSlot count {len(slots)}')
    ad.action_slot=slots[0]
    return slots[0].identifier


def clear_action(arm):
    ad=arm.animation_data
    if ad:
        ad.action=None
        for tr in list(ad.nla_tracks): ad.nla_tracks.remove(tr)


def sample_frames(act,count=5):
    a,b=[float(x) for x in act.frame_range]
    if b<a: a,b=b,a
    if b-a<1e-6: return [int(round(a))]
    return sorted(set(int(round(a+(b-a)*i/(count-1))) for i in range(count)))


def matrix_abs_from_identity(m):
    ident=Matrix.Identity(4)
    return max(abs(float(m[r][c]-ident[r][c])) for r in range(4) for c in range(4))


def score_action(scene,arm,act):
    slot=assign_action(arm,act); arm.data.pose_position='POSE'
    frames=sample_frames(act,5); vals=[]; snapshots=[]; scales=[]; rootloc=[]
    for f in frames:
        scene.frame_set(f); bpy.context.view_layer.update()
        snap=[]
        for pb in arm.pose.bones:
            mb=pb.matrix_basis.copy(); snap.extend(float(mb[r][c]) for r in range(4) for c in range(4))
            vals.append(matrix_abs_from_identity(mb)); scales.extend(abs(float(x)) for x in pb.scale)
        snapshots.append(snap)
        if arm.pose.bones:
            rootloc.append(Vector(arm.pose.bones[0].location))
    temporal=0.0
    for x,y in zip(snapshots,snapshots[1:]):
        temporal=max(temporal,max((abs(a-b) for a,b in zip(x,y)),default=0.0))
    root_disp=0.0
    if rootloc:
        r0=rootloc[0]; root_disp=max((v-r0).length for v in rootloc)
    minscale=min(scales) if scales else 1.0; maxscale=max(scales) if scales else 1.0
    mean_dev=sum(vals)/len(vals) if vals else 0.0; max_dev=max(vals,default=0.0)
    span=max(0.0,float(act.frame_range[1]-act.frame_range[0]))
    finite=all(math.isfinite(x) for x in (mean_dev,max_dev,temporal,root_disp,minscale,maxscale,span))
    sane=finite and span>=1.0 and minscale>=0.25 and maxscale<=4.0 and max_dev<=20.0 and root_disp<=10.0
    # Favor a small but non-zero looping/idle-like pose excursion.  This is a
    # presentation heuristic only, never a semantic state-name claim.
    score=(mean_dev + 0.35*temporal + 0.20*root_disp + (0.4 if temporal<1e-6 else 0.0)) if sane else 1e30
    clear_action(arm)
    return {'action':act.name,'frame_range':[float(act.frame_range[0]),float(act.frame_range[1])],'sample_frames':frames,
            'mean_basis_deviation':mean_dev,'max_basis_deviation':max_dev,'temporal_motion':temporal,
            'root_translation_excursion':root_disp,'min_pose_scale':minscale,'max_pose_scale':maxscale,
            'finite':finite,'pose_sane':sane,'score':score,'slot_identifier':slot}


def combined_bbox(objs,depsgraph):
    lo=Vector((math.inf,math.inf,math.inf)); hi=Vector((-math.inf,-math.inf,-math.inf)); found=False
    for o in objs:
        if o.type!='MESH': continue
        eo=o.evaluated_get(depsgraph)
        for co0 in eo.bound_box:
            co=eo.matrix_world @ Vector(co0)
            if not all(math.isfinite(float(v)) for v in co): raise RuntimeError(f'{o.name}: non-finite evaluated bound')
            for i in range(3): lo[i]=min(lo[i],co[i]); hi[i]=max(hi[i],co[i])
            found=True
    if not found: raise RuntimeError('actor has no mesh bounds')
    dim=hi-lo; center=(lo+hi)*0.5
    return {'min':[float(x) for x in lo],'max':[float(x) for x in hi],'dimensions':[float(x) for x in dim],'center':[float(x) for x in center]}


def bbox_gate(scene,arm,objs,act):
    deps=bpy.context.evaluated_depsgraph_get(); clear_action(arm); arm.data.pose_position='REST'; scene.frame_set(0); bpy.context.view_layer.update()
    rest=combined_bbox(objs,deps); slot=assign_action(arm,act); arm.data.pose_position='POSE'
    rows=[]; max_ratio=1.0; max_center_shift=0.0
    rd=Vector(rest['dimensions']); rc=Vector(rest['center']); denom=max(max(rd),1e-6)
    for f in sample_frames(act,6):
        scene.frame_set(f); bpy.context.view_layer.update(); bb=combined_bbox(objs,deps); d=Vector(bb['dimensions']); c=Vector(bb['center'])
        ratios=[float(d[i]/max(rd[i],1e-6)) for i in range(3)]; ratio=max(ratios); shift=float((c-rc).length/denom)
        max_ratio=max(max_ratio,ratio); max_center_shift=max(max_center_shift,shift)
        rows.append({'frame':f,'bbox':bb,'dimension_ratios_vs_rest':ratios,'center_shift_rest_maxdim_units':shift})
    sane=max_ratio<=2.5 and max_center_shift<=2.0
    return {'action':act.name,'slot_identifier':slot,'rest_bbox':rest,'samples':rows,'max_dimension_ratio':max_ratio,'max_center_shift_rest_maxdim_units':max_center_shift,'deformed_mesh_sane':sane}


def import_actor(scene,path,key,label,xoff,candidate_limit,retain):
    before_obj=set(bpy.data.objects); before_actions=set(bpy.data.actions)
    bpy.ops.import_scene.gltf(filepath=str(path.resolve()),import_pack_images=True)
    objs=[o for o in bpy.data.objects if o not in before_obj]; actions=[x for x in bpy.data.actions if x not in before_actions]
    if not objs or not actions: raise RuntimeError(f'{key}: import objects/actions {len(objs)}/{len(actions)}')
    arms=[o for o in objs if o.type=='ARMATURE']
    if len(arms)!=1: raise RuntimeError(f'{key}: expected one armature, got {len(arms)}')
    arm=arms[0]
    root=bpy.data.objects.new(f'TEST_{label}_{key.replace(":","_")}',None); scene.collection.objects.link(root); root.empty_display_type='PLAIN_AXES'
    objset=set(objs); roots=[o for o in objs if o.parent not in objset]
    for o in roots:
        mw=o.matrix_world.copy(); o.parent=root; o.matrix_world=mw
    root.rotation_mode='XYZ'; root.rotation_euler.x=-math.pi/2; root.location.x=float(xoff)
    root['d1VisualVariantKey']=key; root['d1BlenderBasisCorrection']='ROT_X_NEG_90_AFTER_GLTF_IMPORT'; root['d1LaptopTestAsset']=True
    arm.data.display_type='STICK'; arm.show_in_front=False
    for o in objs: o['d1VisualVariantKey']=key; o['d1LaptopTestAsset']=True

    # Score every target-native imported Action on this exact armature.
    scored=[]
    for act in actions:
        try: scored.append(score_action(scene,arm,act))
        except Exception as ex:
            scored.append({'action':act.name,'pose_sane':False,'score':1e30,'error':repr(ex)})
    sane=sorted((r for r in scored if r.get('pose_sane')),key=lambda r:(r['score'],r['action']))
    if not sane: raise RuntimeError(f'{key}: no pose-sane Action')

    # Run the expensive evaluated-mesh gate only on the best low-motion options.
    byname={x.name:x for x in actions}; mesh_trials=[]; chosen=None
    for r in sane[:candidate_limit]:
        act=byname[r['action']]
        try: g=bbox_gate(scene,arm,objs,act)
        except Exception as ex: g={'action':act.name,'deformed_mesh_sane':False,'error':repr(ex)}
        mesh_trials.append(g)
        if g.get('deformed_mesh_sane'):
            chosen=(r,g,act); break
    if chosen is None: raise RuntimeError(f'{key}: no deformed-mesh-sane Action among {min(candidate_limit,len(sane))} low-motion candidates')
    sr,gate,selected=chosen

    # Retain selected plus the next lowest-score sane target-native Actions.
    keep=[selected]
    for r in sane:
        q=byname[r['action']]
        if q not in keep: keep.append(q)
        if len(keep)>=retain: break
    keepset=set(keep)
    for act in keep:
        old=act.name; act.name=f'D1_V4_{key.replace(":","_")}__{old}'; act.use_fake_user=True
    # Names changed; selected object identity is stable.
    selected_name=selected.name; slot=assign_action(arm,selected); arm.data.pose_position='POSE'
    arm['d1V4PreviewAction']=selected_name; arm['d1V4PreviewActionSlot']=slot; arm['d1V4PreviewPolicy']='LOW_MOTION_TARGET_NATIVE_DIAGNOSTIC_NOT_RETAIL_IDLE'
    for act in list(actions):
        if act not in keepset:
            try: bpy.data.actions.remove(act)
            except Exception: pass
    scene.frame_start=int(math.floor(float(selected.frame_range[0]))); scene.frame_end=max(scene.frame_start+1,int(math.ceil(float(selected.frame_range[1])))); scene.frame_set(scene.frame_start)
    return {'key':key,'label':label,'file':path.name,'sha256':sha256(path),'object_count':len(objs),'mesh_count':sum(o.type=='MESH' for o in objs),
            'material_slot_count':sum(len(o.data.materials) for o in objs if o.type=='MESH'),'source_action_count':len(actions),'retained_action_count':len(keep),
            'selected_action':selected_name,'selected_action_original':sr['action'],'selected_pose_score':sr,'selected_mesh_gate':gate,
            'mesh_gate_trials':mesh_trials,'root_rotation_x':float(root.rotation_euler.x),'armature':arm.name}


def main():
    a=cli(); plan=json.loads(a.plan.read_text())
    rows=plan.get('actors') or []
    if len(rows)!=3: raise SystemExit('plan must contain exactly three actors')
    if not (1<=a.retain_actions_per_actor<=8): raise SystemExit('retain-actions-per-actor must be 1..8')
    bpy.ops.wm.read_factory_settings(use_empty=True); scene=bpy.context.scene
    scene['d1InspectionOnly']=True; scene['d1TowerThreeNpcTestV4']=True; scene['d1RuntimeAnimationStateSelected']=False
    out=[]
    for r in rows:
        p=a.input_dir/r['animated_glb']
        if not p.is_file(): raise SystemExit(f'missing {p}')
        out.append(import_actor(scene,p,r['key'],r['label'],float(r['x']),a.candidate_limit,a.retain_actions_per_actor))
    # Use a common playback range spanning selected diagnostic clips.
    selected_arms=[o for o in bpy.data.objects if o.type=='ARMATURE' and o.get('d1V4PreviewAction')]
    starts=[]; ends=[]
    for arm in selected_arms:
        act=arm.animation_data.action; starts.append(float(act.frame_range[0])); ends.append(float(act.frame_range[1]))
    scene.frame_start=int(math.floor(min(starts))); scene.frame_end=max(scene.frame_start+1,int(math.ceil(max(ends)))); scene.frame_set(scene.frame_start)
    for im in bpy.data.images:
        if im.source=='FILE' and im.packed_file is None:
            try: im.pack()
            except Exception: pass
    txt=bpy.data.texts.new('D1_TOWER_3_NPC_TEST_V4_README')
    txt.write('Destiny 1 Tower 3-NPC V4 visual checkpoint.\n\n')
    txt.write('Textures: production evidence-scoped portable previews retained; only unsafe generic COLOR_0 multiplication was disabled upstream.\n')
    txt.write('Animation: each Action was imported inside its exact target GLB. One low-motion selector-owned target-native clip is preselected only after pose and evaluated-mesh bounds checks. It is NOT claimed to be retail idle/default.\n')
    txt.write('Press Play to inspect. Additional retained D1_V4_* Actions are target-native alternatives.\n')
    a.out_blend.parent.mkdir(parents=True,exist_ok=True); bpy.ops.wm.save_as_mainfile(filepath=str(a.out_blend.resolve()))
    rep={'schema_version':4,'status':'D1_TOWER_THREE_NPC_VISUAL_TEST_V4_COMPLETE','violations':[],
         'blend':str(a.out_blend),'blend_bytes':a.out_blend.stat().st_size,'blend_sha256':sha256(a.out_blend),
         'actor_count':3,'armature_count':len(selected_arms),'retained_action_count':sum(x['retained_action_count'] for x in out),
         'packed_image_count':sum(1 for im in bpy.data.images if im.packed_file is not None),'material_count':len(bpy.data.materials),'image_count':len(bpy.data.images),
         'scene_frame_start':scene.frame_start,'scene_frame_end':scene.frame_end,'actors':out,
         'runtime_animation_state_selected':False,'preview_animation_semantics':'LOW_MOTION_TARGET_NATIVE_DIAGNOSTIC_NOT_RETAIL_IDLE',
         'policy':'Visual checkpoint. Exact target-owned geometry/skin/materials/textures and target-native appended Action libraries are kept separate per actor. Selected preview Actions are sanity-checked convenience clips, not runtime-state claims.'}
    a.report.parent.mkdir(parents=True,exist_ok=True); a.report.write_text(json.dumps(rep,indent=2)+'\n'); print(json.dumps({k:rep[k] for k in ('status','blend_bytes','blend_sha256','packed_image_count','material_count','image_count','retained_action_count')},indent=2))

if __name__=='__main__': main()
