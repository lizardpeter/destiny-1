#!/usr/bin/env python3
"""Merge independently validated D1 world layers without changing source semantics.

This is deliberately not Tower-specific. Each input GLB is treated as a rendered
adapter for one canonical source layer (baked statics, common/decal models,
terrain, entities, sky geometry, ...). Geometry and graph-node world matrices are
copied exactly. Logical source-record counts are supplied explicitly and are kept
separate from rendered geometry-node counts because one D1 placement can contain
multiple material/mesh parts.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
import trimesh


def safe(s:str)->str:
    return ''.join(c if c.isalnum() or c in '._-' else '_' for c in s)

def digest(p:Path)->str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''): h.update(b)
    return h.hexdigest()

def parse_layer(s:str):
    if '=' not in s: raise argparse.ArgumentTypeError('layer must be NAME=PATH')
    n,p=s.split('=',1)
    if not n or not p: raise argparse.ArgumentTypeError('layer must be NAME=PATH')
    return n,Path(p)
def parse_count(s:str):
    if '=' not in s: raise argparse.ArgumentTypeError('logical-count must be NAME=N')
    n,v=s.split('=',1)
    return n,int(v,0)

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--layer',action='append',type=parse_layer,required=True)
    ap.add_argument('--logical-count',action='append',type=parse_count,default=[])
    ap.add_argument('--out',type=Path,required=True);ap.add_argument('--report',type=Path,required=True)
    a=ap.parse_args();logical=dict(a.logical_count)
    names=[n for n,_ in a.layer]
    if len(set(names))!=len(names): raise SystemExit('duplicate layer name')
    unknown=sorted(set(logical)-set(names))
    if unknown: raise SystemExit('logical counts supplied for unknown layers: '+','.join(unknown))

    out=trimesh.Scene();rows=[];total_nodes=0;total_geom=0
    for li,(name,path) in enumerate(a.layer):
        if not path.exists(): raise SystemExit(f'{name}: missing {path}')
        src=trimesh.load(path,force='scene',process=False)
        prefix=f'L{li:02d}_{safe(name)}'
        gm={}
        for gi,(gn,g) in enumerate(src.geometry.items()):
            nn=f'{prefix}_g{gi:05d}_{safe(str(gn))}';out.geometry[nn]=g.copy();gm[gn]=nn
        copied=0
        for ni,node in enumerate(src.graph.nodes_geometry):
            M,gn=src.graph.get(node)
            if gn not in gm: raise SystemExit(f'{name}: node {node} references unknown geometry {gn}')
            nn=f'{prefix}_n{ni:07d}_{safe(str(node))}'
            out.graph.update(frame_to=nn,frame_from=out.graph.base_frame,matrix=M,geometry=gm[gn],metadata={'d1_layer':name,'source_node':str(node)})
            copied+=1
        rows.append({'name':name,'input':str(path),'input_bytes':path.stat().st_size,'input_sha256':digest(path),
                     'geometry_variants':len(src.geometry),'geometry_nodes':copied,'logical_source_records':logical.get(name),
                     'bounds':None if src.bounds is None else src.bounds.tolist()})
        total_nodes+=copied;total_geom+=len(src.geometry)
    a.out.parent.mkdir(parents=True,exist_ok=True);out.export(a.out)
    check=trimesh.load(a.out,force='scene',process=False)
    if len(check.graph.nodes_geometry)!=total_nodes: raise SystemExit(f'reload node mismatch {len(check.graph.nodes_geometry)} != {total_nodes}')
    rep={'schema_version':1,'status':'D1_WORLD_LAYER_MERGE','layers':rows,'layer_count':len(rows),
         'logical_source_records_total':sum(v for v in logical.values()),
         'geometry_nodes':len(check.graph.nodes_geometry),'geometry_variants':len(check.geometry),
         'bounds':None if check.bounds is None else check.bounds.tolist(),'glb':str(a.out),'glb_bytes':a.out.stat().st_size,'glb_sha256':digest(a.out),
         'policy':'Geometry and node world matrices are copied exactly from independently validated layer adapters. Logical source records are never inferred from geometry-node count and no visual culling/fit/rescaling is performed.'}
    a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(rep,indent=2)+'\n');print(json.dumps(rep,indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
