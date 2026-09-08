#!/usr/bin/env python3
"""Build a lightweight Blender inspection file containing exactly three Tower NPCs.

This is a laptop-friendly visual/rig smoke test, not a placement/runtime export.
It consumes the same corrected textured variants and shared native-D1 action
libraries as the full Tower actor inspection, but keeps only three visual assets
and a small deterministic action sample from each required rig family.
"""
from __future__ import annotations

import argparse, hashlib, json, sys
from pathlib import Path

import bpy


def cli():
    raw = sys.argv
    args = raw[raw.index('--') + 1:] if '--' in raw else []
    ap = argparse.ArgumentParser()
    ap.add_argument('--assembly-manifest', type=Path, required=True)
    ap.add_argument('--textured-dir', type=Path, required=True)
    ap.add_argument('--action-dir', type=Path, required=True)
    ap.add_argument('--out-blend', type=Path, required=True)
    ap.add_argument('--report', type=Path, required=True)
    ap.add_argument('--actions-per-family', type=int, default=5)
    return ap.parse_args(args)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(8 << 20), b''):
            h.update(b)
    return h.hexdigest()


def remove_objects(objs):
    for o in objs:
        try:
            bpy.data.objects.remove(o, do_unlink=True)
        except Exception:
            pass


def import_visual(path: Path, key: str, xoff: float):
    before_obj = set(bpy.data.objects)
    before_actions = set(bpy.data.actions)
    bpy.ops.import_scene.gltf(filepath=str(path.resolve()), import_pack_images=True)
    new = [o for o in bpy.data.objects if o not in before_obj]
    actions = [a for a in bpy.data.actions if a not in before_actions]
    if not new:
        raise RuntimeError(f'{key}: visual import created no objects')
    if actions:
        raise RuntimeError(f'{key}: textured visual unexpectedly created actions')
    arms = [o for o in new if o.type == 'ARMATURE']
    if not arms:
        raise RuntimeError(f'{key}: no armature in visual asset')

    root = bpy.data.objects.new(f'TEST_{key.replace(":", "_")}', None)
    bpy.context.scene.collection.objects.link(root)
    root.empty_display_type = 'PLAIN_AXES'
    root.location.x = float(xoff)
    root['d1VisualVariantKey'] = key
    root['d1LaptopTestAsset'] = True

    new_set = set(new)
    roots = [o for o in new if o.parent not in new_set]
    for o in roots:
        mw = o.matrix_world.copy()
        o.parent = root
        o.matrix_world = mw
    for o in new:
        o['d1VisualVariantKey'] = key
        o['d1LaptopTestAsset'] = True

    return root, arms, new


def choose_action_sample(actions, count: int):
    rows = sorted(actions, key=lambda a: a.name)
    if len(rows) <= count:
        return rows
    if count <= 1:
        return [rows[0]]
    # Deterministic spread across the complete selector-owned library instead of
    # merely keeping the first N serialized clips.
    idx = []
    for i in range(count):
        j = round(i * (len(rows) - 1) / (count - 1))
        if j not in idx:
            idx.append(j)
    return [rows[j] for j in idx]


def import_action_sample(path: Path, representative: str, keep_count: int):
    before_obj = set(bpy.data.objects)
    before_col = set(bpy.data.collections)
    before_actions = set(bpy.data.actions)
    bpy.ops.import_scene.gltf(filepath=str(path.resolve()), import_pack_images=False)
    new_obj = [o for o in bpy.data.objects if o not in before_obj]
    new_col = [c for c in bpy.data.collections if c not in before_col]
    actions = [a for a in bpy.data.actions if a not in before_actions]
    if not actions:
        raise RuntimeError(f'{representative}: action library imported zero actions')

    chosen = choose_action_sample(actions, keep_count)
    chosen_set = set(chosen)
    source_sha = sha256(path)
    for a in chosen:
        old = a.name
        a.name = f'D1_TEST_{representative}__{old}'
        a.use_fake_user = True
        a['d1ActionFamilyRepresentative'] = representative
        a['d1ActionFamilySourceGLB'] = path.name
        a['d1ActionFamilySourceGLBSha256'] = source_sha
        a['d1LaptopTestSample'] = True

    # Remove representative geometry before deleting unselected actions so no
    # temporary animation-data user can keep the unwanted hundreds of clips.
    remove_objects(new_obj)
    for a in actions:
        if a not in chosen_set:
            try:
                bpy.data.actions.remove(a)
            except Exception:
                pass
    for c in new_col:
        if len(c.objects) == 0 and len(c.children) == 0:
            try:
                bpy.data.collections.remove(c)
            except Exception:
                pass
    return chosen, len(actions), source_sha


def main():
    a = cli()
    if a.actions_per_family < 1 or a.actions_per_family > 12:
        raise SystemExit('--actions-per-family must be 1..12')
    manifest = json.loads(a.assembly_manifest.read_text())
    if manifest.get('status') != 'D1_TOWER_ACTOR_PRODUCTION_ASSEMBLY_MANIFEST_COMPLETE' or manifest.get('violations'):
        raise SystemExit('assembly manifest is not green')

    wanted = [
        {'key': '80C88CEF:SIG03', 'label': 'XUR', 'x': -3.0},
        {'key': '809D8104:SIG00', 'label': 'MODEL_809D8104', 'x': 0.0},
        {'key': '80C88434:SIG00', 'label': 'MODEL_80C88434', 'x': 3.0},
    ]
    by_key = {v['visual_variant_key']: v for v in manifest['variant_assets']}
    missing = [w['key'] for w in wanted if w['key'] not in by_key]
    if missing:
        raise SystemExit(f'wanted visual variants missing from production manifest: {missing}')

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene['d1InspectionOnly'] = True
    scene['d1LaptopThreeNpcTest'] = True
    scene['d1RuntimeScenarioSelected'] = False
    scene['d1RuntimeActorAnimationStateSelected'] = False

    asset_rows = []
    armatures_by_model = {}
    for w in wanted:
        row = by_key[w['key']]
        p = a.textured_dir / row['textured_glb_basename']
        if not p.is_file():
            raise SystemExit(f'{w["key"]}: missing textured GLB {p}')
        root, arms, objs = import_visual(p, w['key'], w['x'])
        root.name = f'TEST_{w["label"]}_{w["key"].replace(":", "_")}'
        root['d1Model'] = row['model']
        root['d1SignatureIndex'] = int(row['signature_index'])
        root['d1SourceGLBSha256'] = sha256(p)
        armatures_by_model.setdefault(row['model'], []).extend(arms)
        asset_rows.append({
            'label': w['label'], 'visual_variant_key': w['key'], 'model': row['model'],
            'signature_index': int(row['signature_index']), 'file': p.name,
            'sha256': sha256(p), 'object_count': len(objs), 'armature_count': len(arms),
            'x_offset': w['x'],
        })

    needed_models = set(armatures_by_model)
    libs = []
    for lib in manifest['action_libraries']:
        overlap = sorted(needed_models.intersection(lib['models']))
        if overlap:
            libs.append((lib, overlap))
    covered = set(m for _, overlap in libs for m in overlap)
    if covered != needed_models:
        raise RuntimeError(f'action family coverage mismatch: needed={sorted(needed_models)} covered={sorted(covered)}')

    action_rows = []
    for lib, overlap in sorted(libs, key=lambda x: x[0]['representative_model']):
        rep = lib['representative_model']
        p = a.action_dir / lib['action_library_basename']
        if not p.is_file():
            raise SystemExit(f'{rep}: missing action GLB {p}')
        chosen, source_count, source_sha = import_action_sample(p, rep, a.actions_per_family)
        for model in overlap:
            for arm in armatures_by_model[model]:
                arm['d1ActionFamilyRepresentative'] = rep
                arm['d1CompatibleSourceActionCount'] = int(lib['action_count'])
                arm['d1RetainedLaptopTestActionCount'] = len(chosen)
                arm['d1RuntimeAnimationStateSelected'] = False
                if arm.animation_data is not None:
                    arm.animation_data.action = None
                    for tr in list(arm.animation_data.nla_tracks):
                        arm.animation_data.nla_tracks.remove(tr)
        action_rows.append({
            'representative_model': rep,
            'models_in_test': overlap,
            'file': p.name,
            'sha256': source_sha,
            'source_action_count': source_count,
            'retained_action_count': len(chosen),
            'retained_actions': [x.name for x in chosen],
        })

    # Helpful inspection text inside the .blend.
    readme = bpy.data.texts.new('D1_TOWER_3_NPC_TEST_README')
    readme.write('Lightweight Destiny 1 Tower NPC inspection file.\n\n')
    readme.write('Contains exactly three corrected textured/skinned visual variants:\n')
    for r in asset_rows:
        readme.write(f'  {r["label"]}: {r["visual_variant_key"]} ({r["model"]})\n')
    readme.write('\nOnly a small deterministic sample of Actions from each compatible native-D1 family is retained.\n')
    readme.write('No Tower environment, scenario alternatives, or runtime-active state is included.\n')
    readme.write('Select an armature and choose a D1_TEST_* Action in the Action Editor to test animation.\n')

    for im in bpy.data.images:
        if im.source == 'FILE' and im.packed_file is None:
            try:
                im.pack()
            except Exception:
                pass

    # Remove unused datablocks after all three assets and sampled actions are live.
    for _ in range(4):
        try:
            result = bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
            if 'FINISHED' not in result:
                break
        except Exception:
            break

    a.out_blend.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(a.out_blend.resolve()))
    rep = {
        'schema_version': 1,
        'status': 'D1_TOWER_THREE_NPC_LAPTOP_TEST_COMPLETE',
        'blend': str(a.out_blend),
        'blend_bytes': a.out_blend.stat().st_size,
        'blend_sha256': sha256(a.out_blend),
        'actor_count': 3,
        'model_count': len(needed_models),
        'action_family_count': len(action_rows),
        'retained_action_count': sum(x['retained_action_count'] for x in action_rows),
        'source_action_count_across_used_families': sum(x['source_action_count'] for x in action_rows),
        'packed_image_count': sum(1 for im in bpy.data.images if im.packed_file is not None),
        'assets': asset_rows,
        'action_families': action_rows,
        'environment_present': False,
        'scenario_alternatives_present': False,
        'runtime_animation_state_selected': False,
        'policy': 'Laptop-friendly inspection subset only. Three exact corrected visual assets are retained with small deterministic samples from their independently proven compatible native-D1 action families. No retail active-state claim.',
    }
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(rep, indent=2) + '\n')
    print(json.dumps({k: rep[k] for k in ('status','blend_bytes','blend_sha256','actor_count','model_count','action_family_count','retained_action_count','packed_image_count')}, indent=2))


if __name__ == '__main__':
    main()
