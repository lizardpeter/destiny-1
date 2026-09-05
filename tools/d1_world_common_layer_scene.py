#!/usr/bin/env python3
"""Assemble the D1 table-scoped common embedded model/decal layer.

Inputs are binary-validation JSONs produced from SStaticMapData BA048080 records
and per-model GLBs produced by d1_entity_model_corpus_export.py.  The common
carrier is loaded once per map-data table; repeated SStaticMapParent rows are
*not* replayed.

D1 BA048080 stores a conventional System.Numerics/row-vector 4x4 transform in
Charm's source path.  For a column-vector glTF node matrix this becomes M^T.
The scene adapter then applies the proven D1 Z-up -> glTF Y-up basis A:

    node_gltf = A @ M_d1.T

Model geometry remains canonical D1 local geometry.  No visual fit, distance
culling or transform repair is performed.
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
    out={};missing=[]
    for h in sorted(needed):
        p=model_dir/f'{h}.glb'
        if not p.exists():missing.append(h);continue
        s=trimesh.load(p,force='scene',process=False)
        # corpus exporter writes identity nodes; preserve geometry only and let
        # the BA048080 transform own scene placement.
        geoms={}
        for gn,g in s.geometry.items(): geoms[gn]=g.copy()
        out[h]={'path':p,'sha256':sha256(p),'geometries':geoms,'geometry_count':len(geoms)}
    return out,missing

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
    needed={r['model'] for r in records};models,missing=load_models(a.model_dir,needed)
    if missing and not a.allow_missing_models: raise SystemExit('missing model GLBs: '+','.join(missing))
    scene=trimesh.Scene();geom_map={}
    for mh,m in models.items():
        for i,(old,g) in enumerate(m['geometries'].items()):
            new=f'{mh}__g{i:03d}'
            scene.geometry[new]=g
            geom_map.setdefault(mh,[]).append(new)
    placement_rows=[];node_count=0;emitted_records=0;zero_geom=[]
    for r in records:
        mh=r['model'];m=models.get(mh)
        if m is None:
            placement_rows.append({**r,'emitted':False,'reason':'model_glb_missing'});continue
        names=geom_map.get(mh,[])
        if not names:
            zero_geom.append(mh);placement_rows.append({**r,'emitted':False,'reason':'model_has_zero_selected_geometry'});continue
        M=np.asarray(r['matrix_rows'],dtype=np.float64)
        if M.shape!=(4,4) or not np.isfinite(M).all(): raise SystemExit(f'bad transform {r}')
        N=A@M.T
        rec_nodes=[]
        for gi,gn in enumerate(names):
            nn=f'{r["carrier"]}_r{r["record_index"]:03d}_{mh}_g{gi:03d}'
            scene.graph.update(frame_to=nn,matrix=N,geometry=gn,metadata={'d1_common_carrier':r['carrier'],'d1_record_index':r['record_index'],'d1_model':mh,'d1_matrix_rows':r['matrix_rows']})
            rec_nodes.append(nn);node_count+=1
        placement_rows.append({**r,'emitted':True,'node_count':len(rec_nodes),'nodes':rec_nodes,'gltf_matrix':N.tolist()});emitted_records+=1
    a.out.parent.mkdir(parents=True,exist_ok=True);scene.export(a.out)
    rep={
        'schema_version':1,'status':'D1_WORLD_COMMON_LAYER_SCENE' if emitted_records==len(records) else 'D1_WORLD_COMMON_LAYER_SCENE_PARTIAL',
        'common_carriers':carriers,'source_record_count':len(records),'unique_model_count':len(needed),'loaded_model_count':len(models),'missing_models':missing,
        'zero_selected_geometry_models':sorted(set(zero_geom)),'emitted_record_placements':emitted_records,'scene_geometry_variants':len(scene.geometry),'scene_geometry_nodes':node_count,
        'bounds':None if scene.bounds is None else scene.bounds.tolist(),'glb':str(a.out),'glb_bytes':a.out.stat().st_size,'glb_sha256':sha256(a.out),
        'coordinate_adapter':'node_gltf = D1_ZUP_TO_GLTF_YUP @ transpose(BA048080 row-vector matrix)',
        'geometry_reuse':'Each unique selected model part geometry is stored once and instanced by scene graph nodes for its BA048080 records.',
        'placements':placement_rows,
        'policy':'Nine common carriers are loaded once each from the table-scoped D1 first-entry common layer. Repeated SStaticMapParent rows are never replayed.',
    }
    a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(rep,indent=2)+'\n')
    print(json.dumps({k:rep[k] for k in ('status','source_record_count','unique_model_count','loaded_model_count','missing_models','zero_selected_geometry_models','emitted_record_placements','scene_geometry_variants','scene_geometry_nodes','bounds','glb_bytes','glb_sha256')},indent=2))
    return 0 if rep['status']=='D1_WORLD_COMMON_LAYER_SCENE' else 2
if __name__=='__main__':raise SystemExit(main())
