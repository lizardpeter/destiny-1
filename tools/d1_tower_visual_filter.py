#!/usr/bin/env python3
"""Filter a binary-proof D1 Tower baked-static GLB into a visual scene.

The proof exporter deliberately emits every serialized static-info placement. That is
useful for validating the map tables but is not what the D1 renderer displays. The
pinned D1 ROI implementation's StaticMapData_D1.GetStatics() keeps a static only when:

    DetailLevel in {0,1,2,3,10} AND material.Unk08 == 1

This tool applies that exact selection to an already-exported proof GLB while preserving
its byte-derived placement matrices and geometry. Material.Unk08 is read from the
current class-stable 80801AD7 material payload at offset +0x08; it is never inferred.

Safety:
- node -> table/info lookup comes from the validator report;
- material hash comes from the serialized MaterialIndex;
- the material must resolve as class 80801AD7 and have payload bytes;
- unknown/unavailable material state is a hard failure unless --allow-unresolved is set;
- no placement or transform is invented.
"""
from __future__ import annotations
import argparse, json, re, struct, sys
from pathlib import Path
import trimesh

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import d1_tower_map_schema_validate_v3 as v3

ALLOWED_DETAIL={0,1,2,3,10}
MAT_CLASS='80801AD7'
NODE_RE=re.compile(r'^([0-9A-F]{8})_info(\d+)_xform(\d+)$', re.I)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--snapshot', action='append', type=Path, required=True)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('--validation-json', type=Path, required=True)
    ap.add_argument('--d1-static-map-data', required=True)
    ap.add_argument('--input-glb', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--json', type=Path, required=True)
    ap.add_argument('--allow-unresolved', action='store_true')
    a=ap.parse_args()

    val=json.loads(a.validation_json.read_text())
    h=a.d1_static_map_data.upper()
    rr=next((r for r in val.get('static_map_data_d1',[]) if r.get('hash','').upper()==h),None)
    if rr is None: raise SystemExit(f'validator row {h} absent')
    if not rr.get('ok'): raise SystemExit(f'validator row {h} did not pass: {rr.get("violations")}')

    c=v3.Corpus([p.resolve() for p in a.snapshot], a.runtime.resolve())
    info={}
    materials={}
    for t in rr['static_tables']:
        th=t['hash'].upper()
        for row in t['info_entries']:
            si=int(row['static_index']); mi=int(row['material_index'])
            mesh=t['mesh_entries'][si]
            mh=t['material_hashes'][mi].upper()
            info[(th,int(row['index']))]={
                'detail_level':int(mesh['detail_level']),
                'material_hash':mh,
                'static_index':si,
                'material_index':mi,
            }
            materials[mh]=None

    # Resolve every referenced material exactly once.
    unresolved=[]
    for mh in sorted(materials):
        meta=c.entry_meta(mh)
        payload,src=c.payload(mh)
        row={'hash':mh,'meta':meta,'source':src,'unk08':None,'visual':False}
        if not meta or meta.get('reference','').upper()!=MAT_CLASS:
            row['error']='missing or non-80801AD7 current material'
            unresolved.append(row)
        elif payload is None or len(payload)<0x0C:
            row['error']='material payload unavailable/short'
            unresolved.append(row)
        else:
            row['unk08']=struct.unpack_from('<I',payload,0x08)[0]
            row['visual']=(row['unk08']==1)
        materials[mh]=row
    if unresolved and not a.allow_unresolved:
        raise SystemExit('unresolved material state: '+json.dumps(unresolved[:20],indent=2))

    src_scene=trimesh.load(a.input_glb,force='scene',process=False)
    survivors=[]; removed={'detail_level':0,'material_unk08':0,'unresolved':0,'intrinsic_or_unmapped':0}
    detail_population={}; material_population={}
    for node in src_scene.graph.nodes_geometry:
        m=NODE_RE.match(str(node))
        if not m:
            # Proof GLBs may include one intrinsic source node per geometry. Never
            # copy those into a visual placement scene.
            removed['intrinsic_or_unmapped']+=1
            continue
        th=m.group(1).upper(); ii=int(m.group(2))
        im=info.get((th,ii))
        if im is None:
            removed['intrinsic_or_unmapped']+=1; continue
        dl=im['detail_level']; mh=im['material_hash']
        detail_population[str(dl)]=detail_population.get(str(dl),0)+1
        material_population[mh]=material_population.get(mh,0)+1
        if dl not in ALLOWED_DETAIL:
            removed['detail_level']+=1; continue
        mr=materials[mh]
        if mr.get('unk08') is None:
            removed['unresolved']+=1
            if not a.allow_unresolved: raise AssertionError('unreachable unresolved material')
            continue
        if mr['unk08']!=1:
            removed['material_unk08']+=1; continue
        tf,g=src_scene.graph.get(node)
        survivors.append((node,tf,g,im))

    out=trimesh.Scene()
    geom_names=sorted({g for _,_,g,_ in survivors})
    gmap={}
    for i,g in enumerate(geom_names):
        ng=f'visual_g{i:05d}'
        out.geometry[ng]=src_scene.geometry[g].copy(); gmap[g]=ng
    for i,(node,tf,g,im) in enumerate(survivors):
        out.graph.update(frame_to=f'visual_p{i:06d}',frame_from=out.graph.base_frame,matrix=tf,geometry=gmap[g])

    a.out.parent.mkdir(parents=True,exist_ok=True)
    out.export(a.out,file_type='glb')
    check=trimesh.load(a.out,force='scene',process=False)
    if len(check.graph.nodes_geometry)!=len(survivors):
        raise SystemExit(f'reload node mismatch {len(check.graph.nodes_geometry)} != {len(survivors)}')

    report={
      'evidence_status':'D1_VISUAL_STATIC_SELECTION_FROM_BINARY_VALIDATED_PLACEMENTS_AND_CURRENT_MATERIAL_BYTES',
      'd1_static_map_data':h,
      'rule':{'detail_levels':sorted(ALLOWED_DETAIL),'material_class':MAT_CLASS,'material_unk08_required':1},
      'input_nodes_geometry':len(src_scene.graph.nodes_geometry),
      'visual_placements':len(survivors),
      'visual_geometry_variants':len(check.geometry),
      'removed':removed,
      'detail_population':detail_population,
      'materials':materials,
      'unique_materials':len(materials),
      'visual_materials':sum(1 for x in materials.values() if x.get('visual')),
      'bounds':check.bounds.tolist() if check.bounds is not None else None,
      'glb_bytes':a.out.stat().st_size,
      'policy':{
        'placement':'unchanged matrices from proof GLB',
        'visual_filter':'exact D1 GetStatics detail/material gate; no guessed LOD selection',
        'textures':'not attached by this tool'
      }
    }
    a.json.parent.mkdir(parents=True,exist_ok=True)
    a.json.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ('d1_static_map_data','visual_placements','visual_geometry_variants','removed','unique_materials','visual_materials','bounds','glb_bytes')},indent=2))

if __name__=='__main__': main()
