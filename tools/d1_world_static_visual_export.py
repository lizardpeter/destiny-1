#!/usr/bin/env python3
"""Reusable D1 ROI retail-visible baked-static world exporter.

Consumes any validator-passing StaticMapData parent and emits only placements
selected by D1's retail GetStatics() path, with proven affine transforms, exact
per-instance UV transforms, source vertex attributes, material hashes and source
provenance. D1 source space remains canonical; glTF is an adapter.

Vertex COLOR_0 is retained even when the mesh also has UV/material data. Exact D1
tangent vectors are retained as the custom glTF vertex attribute ``_D1_TANGENT``
until their direct portable TANGENT handedness semantics are independently closed.
No shader t# role is guessed here.
"""
from __future__ import annotations
import argparse, hashlib, json, struct, sys
from collections import defaultdict
from pathlib import Path
import numpy as np
import trimesh

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))

import d1_tower_map_schema_validate_v5 as v5
import d1_tower_static_chunk_export_v2  # patches null-V1 handling into base
import d1_tower_static_chunk_export as base
from d1_world_static_common import parse_static_instance_records, apply_d1_instance_uv, d1_world_to_gltf_matrix
from d1_world_static_vertex_decode import decode_static_attributes
from d1_material_decode import parse_material

ALLOWED_DETAIL={0,1,2,3,10}
MAT_CLASS='80801AD7'


def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def norm(h): return base.norm_hash(h)


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--snapshot',type=Path,action='append',required=True)
    ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('--validation-json',type=Path,required=True)
    ap.add_argument('--static-map-data',required=True,help='validated outer StaticMapData hash')
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--json',type=Path)
    ap.add_argument('--basis',choices=('d1-z-up','gltf-y-up'),default='gltf-y-up')
    a=ap.parse_args()

    validation=json.loads(a.validation_json.read_text())
    selected=base.select_validated_map(validation,a.static_map_data)
    d1=selected['d1_validation']
    c=v5.v3.base.Corpus([p.resolve() for p in a.snapshot],a.runtime.resolve())

    th=norm(d1['instance_transforms'])
    tb,tsrc,tmeta=base.payload_with_meta(c,th)
    inst=parse_static_instance_records(tb,int(d1['instance_count']))

    material_cache={}
    def material_record(mh):
        mh=norm(mh)
        if mh in material_cache:return material_cache[mh]
        meta=c.entry_meta(mh);b,src=c.payload(mh)
        r={'hash':mh,'meta':meta,'source':src,'unk08':None,'visual':False}
        if not meta or norm(meta.get('reference',''))!=MAT_CLASS or b is None or len(b)<0x0C:
            r['error']='material unavailable/non-80801AD7'
        else:
            r['unk08']=u32(b,0x08);r['visual']=(r['unk08']==1)
            try:
                md=parse_material(b,'PS4')
                r['vertex_shader']=norm(md['vertex_shader']);r['pixel_shader']=norm(md['pixel_shader'])
                r['vs_textures']=md['vs_textures']['items'];r['ps_textures']=md['ps_textures']['items']
            except Exception as ex:r['material_parse_error']=repr(ex)
        material_cache[mh]=r;return r

    ref_cache={}
    def ref_file(h):
        h=norm(h)
        if h not in ref_cache: ref_cache[h]=base.read_reference_file(c,h)
        return ref_cache[h]

    # glTF has no per-node UV transform, so the adapter geometry key includes the
    # exact serialized UV triple. Source identity remains mesh/material + instance.
    groups=defaultdict(list)
    rejected={'detail_level':0,'material_unk08':0}
    theoretical=0
    for table in d1['static_tables']:
        meshes=table['mesh_entries'];mats=table['material_hashes']
        for info in table['info_entries']:
            mesh=meshes[int(info['static_index'])]
            mh=norm(mats[int(info['material_index'])])
            n=int(info['instance_count']);start=int(info['transform_index'])
            theoretical+=n
            if int(mesh['detail_level']) not in ALLOWED_DETAIL:
                rejected['detail_level']+=n;continue
            mr=material_record(mh)
            if mr.get('unk08')!=1:
                rejected['material_unk08']+=n;continue
            mesh_key=(norm(mesh['vertices0']),norm(mesh['vertices1']),norm(mesh['indices']),
                      int(mesh['index_offset']),int(mesh['index_count']),int(mesh['primitive_type']),mh)
            for li in range(n):
                ti=start+li;r=inst[ti]
                uv_key=struct.pack('<3f',r.uv_scale,r.uv_translate_x,r.uv_translate_y).hex()
                groups[(mesh_key,uv_key)].append({
                    'table_hash':norm(table['hash']),'info_index':int(info['index']),
                    'static_index':int(info['static_index']),'material_index':int(info['material_index']),
                    'material_hash':mh,'detail_level':int(mesh['detail_level']),
                    'transform_index':ti,'instance':r,
                })

    scene=trimesh.Scene();geom_reports=[];node_reports=[];decode_errors=[]
    for gi,((key,uv_key),placements) in enumerate(sorted(groups.items(),key=lambda x:(x[0][0],x[0][1]))):
        v0h,v1h,ibh,off,cnt,prim,mh=key
        try:
            v0=ref_file(v0h);v1=ref_file(v1h);ib=ref_file(ibh)
            s0=base.hdr_stride(v0['header']);s1=base.hdr_stride(v1['header'])
            attrs=decode_static_attributes(v0['backing'],s0,None if v1h=='FFFFFFFF' else v1['backing'],None if v1h=='FFFFFFFF' else s1)
            is32=base.index_is32(ib['header']);inds=base.decode_indices(ib['backing'],is32)
            if off<0 or cnt<0 or off+cnt>len(inds):raise ValueError(f'index slice {off}+{cnt}>{len(inds)}')
            fg=base.primitive_faces(inds[off:off+cnt],prim,is32)
            if len(fg)==0 or fg.min()<0 or fg.max()>=len(attrs.positions):raise ValueError('decoded face range invalid')
            used,inv=np.unique(fg.reshape(-1),return_inverse=True);faces=inv.reshape((-1,3))
            verts=attrs.positions[used]
            uv=None;r0=placements[0]['instance']
            if attrs.uv0 is not None:
                uv=apply_d1_instance_uv(attrs.uv0[used],r0.uv_scale,r0.uv_translate_x,r0.uv_translate_y)
            normals=attrs.normals[used] if attrs.normals is not None else None
            tangents=attrs.tangents[used] if attrs.tangents is not None else None
            colors=attrs.colors[used] if attrs.colors is not None else None

            mat=trimesh.visual.material.PBRMaterial(name=f'TigerMaterial_{mh}')
            visual=trimesh.visual.TextureVisuals(uv=uv,material=mat) if uv is not None else trimesh.visual.TextureVisuals(material=mat)
            # trimesh's glTF exporter maps TextureVisuals.vertex_attributes['color']
            # to standard COLOR_0, allowing UV + vertex colour simultaneously.
            if colors is not None:
                visual.vertex_attributes['color']=np.clip(colors*255.0+0.5,0,255).astype(np.uint8)
            tm=trimesh.Trimesh(vertices=verts,faces=faces,visual=visual,process=False,validate=False)
            if normals is not None and len(normals)==len(verts): tm.vertex_normals=normals
            if tangents is not None and len(tangents)==len(verts):
                # Preserve exact decoded D1 tangent as an application-specific
                # attribute; do not falsely promote its W to glTF handedness yet.
                tm.vertex_attributes['D1_TANGENT']=tangents.astype(np.float32)
            gname=f'd1static_g{gi:05d}_{v0h}_{ibh}_o{off}_n{cnt}_p{prim}_m{mh}_uv{uv_key[:8]}'
            scene.geometry[gname]=tm
            geom_reports.append({
                'geometry':gname,'source_key':{'vertices0':v0h,'vertices1':v1h,'indices':ibh,
                    'index_offset':off,'index_count':cnt,'primitive_type':prim,'material_hash':mh},
                'uv_transform':[r0.uv_scale,r0.uv_translate_x,r0.uv_translate_y],
                'uv_transform_key':uv_key,'placement_count':len(placements),
                'vertices':len(verts),'triangles':len(faces),'stride0':s0,'stride1':s1,
                'layout':attrs.layout,'has_uv':uv is not None,'has_normals':normals is not None,
                'has_tangents':tangents is not None,'tangent_gltf_attribute':'_D1_TANGENT' if tangents is not None else None,
                'has_colors':colors is not None,'color_gltf_attribute':'COLOR_0' if colors is not None else None,
                'source_vertex_indices':used.tolist(),
            })
            for p in placements:
                ir=p['instance'];m=ir.affine
                export_m=d1_world_to_gltf_matrix(m) if a.basis=='gltf-y-up' else m
                node=f"{p['table_hash']}_info{p['info_index']}_xform{p['transform_index']}"
                scene.graph.update(frame_to=node,frame_from=scene.graph.base_frame,matrix=export_m,geometry=gname)
                node_reports.append({
                    'node':node,'geometry':gname,'table_hash':p['table_hash'],'info_index':p['info_index'],
                    'static_index':p['static_index'],'material_index':p['material_index'],'material_hash':mh,
                    'detail_level':p['detail_level'],'transform_index':p['transform_index'],
                    'source_affine':m.tolist(),'uv_transform':[ir.uv_scale,ir.uv_translate_x,ir.uv_translate_y],
                    'tail_0x3c':ir.tail_3c,
                })
        except Exception as ex:
            decode_errors.append({'geometry_key':key,'uv_key':uv_key,'error':repr(ex),'placements':len(placements)})

    a.out.parent.mkdir(parents=True,exist_ok=True);scene.export(a.out,file_type='glb')
    check=trimesh.load(a.out,force='scene',process=False)
    if len(check.graph.nodes_geometry)!=len(node_reports):raise SystemExit('reload node count mismatch')
    bad=[]
    for n in check.graph.nodes_geometry:
        m,_=check.graph.get(n)
        if not np.allclose(m[3],[0,0,0,1],atol=1e-7):bad.append(n)
    if bad:raise SystemExit(f'non-affine exported nodes remain: {bad[:5]}')

    rep={
      'status':'D1_RETAIL_VISIBLE_BAKED_STATIC_WORLD_EXPORT_WITH_UV',
      'static_map_data':norm(a.static_map_data),'d1_static_map_data':norm(d1['hash']),
      'basis':a.basis,'serialized_placements':theoretical,'retail_visible_placements':len(node_reports),
      'rejected':rejected,'geometry_variants':len(geom_reports),'decode_error_count':len(decode_errors),
      'decode_errors':decode_errors,'instance_transform_hash':th,'instance_transform_source':tsrc,
      'materials':material_cache,'geometry':geom_reports,'nodes':node_reports,
      'attribute_coverage':{
          'uv':sum(g['has_uv'] for g in geom_reports),'normals':sum(g['has_normals'] for g in geom_reports),
          'tangents':sum(g['has_tangents'] for g in geom_reports),'colors':sum(g['has_colors'] for g in geom_reports),
      },
      'bounds':check.bounds.tolist() if check.bounds is not None else None,
      'glb_bytes':a.out.stat().st_size,'glb_sha256':hashlib.sha256(a.out.read_bytes()).hexdigest(),
      'adapter_policy':'D1 source affine/UV/vertex attributes canonical; glTF UV transform baked per geometry+UV variant; COLOR_0 retained; exact D1 tangent retained as _D1_TANGENT pending portable handedness closure; arbitrary t# roles not guessed.'
    }
    jp=a.json or a.out.with_suffix('.json');jp.write_text(json.dumps(rep,indent=2)+'\n')
    print(json.dumps({k:rep[k] for k in ('static_map_data','d1_static_map_data','serialized_placements','retail_visible_placements','rejected','geometry_variants','decode_error_count','attribute_coverage','bounds','glb_bytes')},indent=2))
    return 0 if not decode_errors else 2

if __name__=='__main__':raise SystemExit(main())
