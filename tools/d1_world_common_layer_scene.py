#!/usr/bin/env python3
"""Assemble the D1 table-scoped common embedded model/decal layer.

Inputs are binary-validation JSONs produced from SStaticMapData BA048080 records
and per-model GLBs/diagnostics produced by d1_entity_model_corpus_export.py. The
common carrier is loaded once per map-data table; repeated SStaticMapParent rows
are *not* replayed.

D1 BA048080 stores a conventional System.Numerics/row-vector 4x4 transform in
Charm's source path. For a column-vector glTF node matrix this becomes M^T.
The scene adapter then applies the proven D1 Z-up -> glTF Y-up basis A:

    node_gltf = A @ M_d1.T

A source-valid model can intentionally have zero selected geometry under exact
D1 MostDetailed + transparentsOnly selection. Such records remain complete source
coverage and are reported explicitly; no fake geometry is emitted for them.
"""
from __future__ import annotations

import argparse,json,hashlib
from pathlib import Path
import numpy as np
import trimesh

A=np.array([
    [1.,0.,0.,0.],
    [0.,0.,1.,0.],
    [0.,-1.,0.,0.],
    [0.,0.,0.,1.],
],dtype=np.float64)


def norm(h): return str(h).upper().removeprefix('0X').zfill(8)

def sha256(p:Path):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''):h.update(b)
    return h.hexdigest()

def load_models(model_dir:Path,needed:set[str]):
    out={};missing=[];zero=[]
    for h in sorted(needed):
        p=model_dir/f'{h}.glb'; jp=model_dir/f'{h}.json'
        diag=None
        if jp.exists():
            try: diag=json.loads(jp.read_text())
            except Exception: diag=None
        if p.exists():
            s=trimesh.load(p,force='scene',process=False)
            geoms={gn:g.copy() for gn,g in s.geometry.items()}
            out[h]={'path':p,'sha256':sha256(p),'geometries':geoms,'geometry_count':len(geoms),'diagnostic':diag,'zero_selected_geometry':False}
            continue
        if diag and bool(diag.get('zero_selected_geometry')) and int(diag.get('geometry_count',0))==0:
            out[h]={'path':None,'sha256':None,'geometries':{},'geometry_count':0,'diagnostic':diag,'zero_selected_geometry':True}
            zero.append(h);continue
        missing.append(h)
    return out,missing,zero

def main()->int:
    ap=argparse.ArgumentParser();ap.add_argument('--validation',type=Path,action='append',required=True);ap.add_argument('--model-dir',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--report',type=Path,required=True);ap.add_argument('--allow-missing-models',action='store_true')
    a=ap.parse_args();records=[];carriers=[]
    for vp in a.validation:
        d=json.loads(vp.read_text());sm=norm(d['static_map_data']);carriers.append(sm)
        if not d.get('ok'): raise SystemExit(f'{vp}: validation not ok')
        for r in d.get('decals',[]):
            if not r.get('ok') or not r.get('singleton_transform_model'):
                raise SystemExit(f'{vp}: record {r.get("index")} not valid singleton')
            m=r['models'][0];tr=r['transforms'][0]
            if not m.get('reference_matches'): raise SystemExit(f'{vp}: record {r["index"]} model invalid')
            records.append({'carrier':sm,'record_index':int(r['index']),'model':norm(m['hash']),'matrix_rows':tr['rows']})
    needed={r['model'] for r in records};models,missing,zero_models=load_models(a.model_dir,needed)
    if missing and not a.allow_missing_models: raise SystemExit('missing model GLBs/diagnostics: '+','.join(missing))
    scene=trimesh.Scene();geom_map={}
    for mh,m in models.items():
        for i,(old,g) in enumerate(m['geometries'].items()):
            new=f'{mh}__g{i:03d}'
            scene.geometry[new]=g
            geom_map.setdefault(mh,[]).append(new)
    placement_rows=[];node_count=0;emitted_records=0;zero_record_count=0;unresolved_records=0
    for r in records:
        mh=r['model'];m=models.get(mh)
        if m is None:
            placement_rows.append({**r,'source_resolved':False,'emitted_geometry':False,'reason':'model_export_unresolved'});unresolved_records+=1;continue
        if m.get('zero_selected_geometry'):
            placement_rows.append({**r,'source_resolved':True,'emitted_geometry':False,'reason':'valid_zero_selected_geometry'});zero_record_count+=1;continue
        names=geom_map.get(mh,[])
        if not names:
            placement_rows.append({**r,'source_resolved':False,'emitted_geometry':False,'reason':'unexpected_empty_model_geometry'});unresolved_records+=1;continue
        M=np.asarray(r['matrix_rows'],dtype=np.float64)
        if M.shape!=(4,4) or not np.isfinite(M).all(): raise SystemExit(f'bad transform {r}')
        N=A@M.T
        rec_nodes=[]
        for gi,gn in enumerate(names):
            nn=f'{r["carrier"]}_r{r["record_index"]:03d}_{mh}_g{gi:03d}'
            scene.graph.update(frame_to=nn,matrix=N,geometry=gn,metadata={'d1_common_carrier':r['carrier'],'d1_record_index':r['record_index'],'d1_model':mh,'d1_matrix_rows':r['matrix_rows']})
            rec_nodes.append(nn);node_count+=1
        placement_rows.append({**r,'source_resolved':True,'emitted_geometry':True,'node_count':len(rec_nodes),'nodes':rec_nodes,'gltf_matrix':N.tolist()});emitted_records+=1
    a.out.parent.mkdir(parents=True,exist_ok=True)
    if len(scene.geometry): scene.export(a.out)
    source_resolved_records=emitted_records+zero_record_count
    complete=(source_resolved_records==len(records) and unresolved_records==0 and not missing)
    rep={
        'schema_version':2,'status':'D1_WORLD_COMMON_LAYER_SCENE_COMPLETE_SOURCE_COVERAGE' if complete else 'D1_WORLD_COMMON_LAYER_SCENE_PARTIAL',
        'common_carriers':carriers,'source_record_count':len(records),'unique_model_count':len(needed),'resolved_model_count':len(models),'missing_models':missing,
        'zero_selected_geometry_models':sorted(set(zero_models)),'valid_zero_geometry_records':zero_record_count,'source_resolved_records':source_resolved_records,
        'geometry_emitting_record_placements':emitted_records,'unresolved_records':unresolved_records,'scene_geometry_variants':len(scene.geometry),'scene_geometry_nodes':node_count,
        'bounds':None if scene.bounds is None else scene.bounds.tolist(),'glb':str(a.out) if a.out.exists() else None,'glb_bytes':a.out.stat().st_size if a.out.exists() else 0,'glb_sha256':sha256(a.out) if a.out.exists() else None,
        'coordinate_adapter':'node_gltf = D1_ZUP_TO_GLTF_YUP @ transpose(BA048080 row-vector matrix)',
        'geometry_reuse':'Each unique selected model part geometry is stored once and instanced by scene graph nodes for its BA048080 records.',
        'placements':placement_rows,
        'policy':'Nine common carriers are loaded once each from the table-scoped D1 first-entry common layer. Repeated SStaticMapParent rows are never replayed. Valid zero-geometry records are preserved as resolved source records, not fabricated meshes.',
    }
    a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(rep,indent=2)+'\n')
    print(json.dumps({k:rep[k] for k in ('status','source_record_count','unique_model_count','resolved_model_count','missing_models','zero_selected_geometry_models','valid_zero_geometry_records','source_resolved_records','geometry_emitting_record_placements','unresolved_records','scene_geometry_variants','scene_geometry_nodes','bounds','glb_bytes','glb_sha256')},indent=2))
    return 0 if complete else 2
if __name__=='__main__':raise SystemExit(main())
