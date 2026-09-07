#!/usr/bin/env python3
"""Export every serialized D1 ROI baked-static placement and material variant.

This is the forensic companion to d1_world_static_visual_export.py. The retail
exporter correctly applies GetStatics() visibility rules (detail level and material
Unk08). This tool deliberately does not: every serialized static-table info range,
instance transform, LOD/detail level and material reference is preserved.

The normal retail-visible exporter remains the scene users should inspect visually.
This file exists so nonvisual/depth/LOD/pass geometry is never lost from the archive.
It also emits an explicit dependency-selector adapter containing every serialized
material hash. The adapter's ``visual`` compatibility bit exists only because the
legacy generic texture closer consumes that field; ``retail_visual`` preserves the
actual material Unk08==1 result and no semantic visibility claim is made.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from collections import defaultdict
from pathlib import Path

import numpy as np
import trimesh

import d1_world_static_visual_export as retail


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--snapshot', type=Path, action='append', required=True)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('--validation-json', type=Path, required=True)
    ap.add_argument('--static-map-data', required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--json', type=Path)
    ap.add_argument('--material-selector', type=Path)
    ap.add_argument('--basis', choices=('d1-z-up','gltf-y-up'), default='gltf-y-up')
    a = ap.parse_args()

    validation = json.loads(a.validation_json.read_text())
    selected = retail.base.select_validated_map(validation, a.static_map_data)
    d1 = selected['d1_validation']
    c = retail.v5.v3.base.Corpus([p.resolve() for p in a.snapshot], a.runtime.resolve())

    th = retail.norm(d1['instance_transforms'])
    tb, tsrc, _ = retail.base.payload_with_meta(c, th)
    inst = retail.parse_static_instance_records(tb, int(d1['instance_count']))

    material_cache = {}
    def material_record(mh):
        mh = retail.norm(mh)
        if mh in material_cache:
            return material_cache[mh]
        meta = c.entry_meta(mh); b, src = c.payload(mh)
        r = {'hash':mh,'meta':meta,'source':src,'unk08':None,'retail_visual':False}
        if not meta or retail.norm(meta.get('reference','')) != retail.MAT_CLASS or b is None or len(b) < 0x0C:
            r['error'] = 'material unavailable/non-80801AD7'
        else:
            r['unk08'] = retail.u32(b,0x08)
            r['retail_visual'] = r['unk08'] == 1
            try:
                md = retail.parse_material(b,'PS4')
                r['vertex_shader'] = retail.norm(md['vertex_shader'])
                r['pixel_shader'] = retail.norm(md['pixel_shader'])
                r['vs_textures'] = md['vs_textures']['items']
                r['ps_textures'] = md['ps_textures']['items']
            except Exception as ex:
                r['material_parse_error'] = repr(ex)
        material_cache[mh] = r
        return r

    ref_cache = {}
    def ref_file(h):
        h = retail.norm(h)
        if h not in ref_cache:
            ref_cache[h] = retail.base.read_reference_file(c,h)
        return ref_cache[h]

    groups = defaultdict(list)
    theoretical = 0
    detail_counts = defaultdict(int)
    material_usage = defaultdict(int)
    for table in d1['static_tables']:
        meshes = table['mesh_entries']; mats = table['material_hashes']
        for info in table['info_entries']:
            mesh = meshes[int(info['static_index'])]
            mh = retail.norm(mats[int(info['material_index'])])
            n = int(info['instance_count']); start = int(info['transform_index'])
            theoretical += n
            detail_counts[int(mesh['detail_level'])] += n
            material_usage[mh] += n
            material_record(mh)
            mesh_key = (
                retail.norm(mesh['vertices0']), retail.norm(mesh['vertices1']), retail.norm(mesh['indices']),
                int(mesh['index_offset']), int(mesh['index_count']), int(mesh['primitive_type']), mh,
                int(mesh['detail_level']),
            )
            for li in range(n):
                ti = start + li; r = inst[ti]
                uv_key = struct.pack('<3f',r.uv_scale,r.uv_translate_x,r.uv_translate_y).hex()
                groups[(mesh_key,uv_key)].append({
                    'table_hash':retail.norm(table['hash']),'info_index':int(info['index']),
                    'static_index':int(info['static_index']),'material_index':int(info['material_index']),
                    'material_hash':mh,'detail_level':int(mesh['detail_level']),
                    'transform_index':ti,'instance':r,
                })

    scene = trimesh.Scene(); geom_reports=[]; node_reports=[]; decode_errors=[]
    for gi, ((key,uv_key),placements) in enumerate(sorted(groups.items(), key=lambda x:(x[0][0],x[0][1]))):
        v0h,v1h,ibh,off,cnt,prim,mh,detail = key
        try:
            v0=ref_file(v0h); v1=ref_file(v1h); ib=ref_file(ibh)
            s0=retail.base.hdr_stride(v0['header']); s1=retail.base.hdr_stride(v1['header'])
            attrs=retail.decode_static_attributes(v0['backing'],s0,None if v1h=='FFFFFFFF' else v1['backing'],None if v1h=='FFFFFFFF' else s1)
            is32=retail.base.index_is32(ib['header']); inds=retail.base.decode_indices(ib['backing'],is32)
            if off<0 or cnt<0 or off+cnt>len(inds): raise ValueError(f'index slice {off}+{cnt}>{len(inds)}')
            fg=retail.base.primitive_faces(inds[off:off+cnt],prim,is32)
            if len(fg)==0 or fg.min()<0 or fg.max()>=len(attrs.positions): raise ValueError('decoded face range invalid')
            used,inv=np.unique(fg.reshape(-1),return_inverse=True); faces=inv.reshape((-1,3)); verts=attrs.positions[used]
            r0=placements[0]['instance']; uv=None
            if attrs.uv0 is not None:
                uv=retail.apply_d1_instance_uv(attrs.uv0[used],r0.uv_scale,r0.uv_translate_x,r0.uv_translate_y)
            normals=attrs.normals[used] if attrs.normals is not None else None
            tangents=attrs.tangents[used] if attrs.tangents is not None else None
            colors=attrs.colors[used] if attrs.colors is not None else None
            mat=trimesh.visual.material.PBRMaterial(name=f'TigerMaterial_{mh}')
            visual=trimesh.visual.TextureVisuals(uv=uv,material=mat) if uv is not None else trimesh.visual.TextureVisuals(material=mat)
            if colors is not None:
                visual.vertex_attributes['color']=np.clip(colors*255.0+0.5,0,255).astype(np.uint8)
            tm=trimesh.Trimesh(vertices=verts,faces=faces,visual=visual,process=False,validate=False)
            if normals is not None and len(normals)==len(verts): tm.vertex_normals=normals
            if tangents is not None and len(tangents)==len(verts): tm.vertex_attributes['D1_TANGENT']=tangents.astype(np.float32)
            gname=f'd1all_g{gi:05d}_d{detail}_{v0h}_{ibh}_o{off}_n{cnt}_p{prim}_m{mh}_uv{uv_key[:8]}'
            scene.geometry[gname]=tm
            geom_reports.append({'geometry':gname,'detail_level':detail,'source_key':{'vertices0':v0h,'vertices1':v1h,'indices':ibh,'index_offset':off,'index_count':cnt,'primitive_type':prim,'material_hash':mh},'uv_transform':[r0.uv_scale,r0.uv_translate_x,r0.uv_translate_y],'uv_transform_key':uv_key,'placement_count':len(placements),'vertices':len(verts),'triangles':len(faces),'stride0':s0,'stride1':s1,'layout':attrs.layout,'has_uv':uv is not None,'has_normals':normals is not None,'has_tangents':tangents is not None,'has_colors':colors is not None,'source_vertex_indices':used.tolist()})
            for p in placements:
                ir=p['instance']; m=ir.affine
                export_m=retail.d1_world_to_gltf_matrix(m) if a.basis=='gltf-y-up' else m
                node=f"ALL_{p['table_hash']}_info{p['info_index']}_xform{p['transform_index']}"
                scene.graph.update(frame_to=node,frame_from=scene.graph.base_frame,matrix=export_m,geometry=gname)
                node_reports.append({'node':node,'geometry':gname,'table_hash':p['table_hash'],'info_index':p['info_index'],'static_index':p['static_index'],'material_index':p['material_index'],'material_hash':mh,'detail_level':p['detail_level'],'transform_index':p['transform_index'],'source_affine':m.tolist(),'uv_transform':[ir.uv_scale,ir.uv_translate_x,ir.uv_translate_y],'tail_0x3c':ir.tail_3c})
        except Exception as ex:
            decode_errors.append({'geometry_key':key,'uv_key':uv_key,'error':repr(ex),'placements':len(placements)})

    a.out.parent.mkdir(parents=True,exist_ok=True); scene.export(a.out,file_type='glb')
    check=trimesh.load(a.out,force='scene',process=False)
    if len(check.graph.nodes_geometry)!=len(node_reports): raise SystemExit(f'reload node count mismatch {len(check.graph.nodes_geometry)}!={len(node_reports)}')

    rep={
        'status':'D1_ALL_SERIALIZED_BAKED_STATIC_WORLD_EXPORT_WITH_UV',
        'static_map_data':retail.norm(a.static_map_data),'d1_static_map_data':retail.norm(d1['hash']),'basis':a.basis,
        'serialized_placements':theoretical,'exported_placements':len(node_reports),'detail_level_placement_counts':dict(sorted(detail_counts.items())),
        'unique_serialized_material_count':len(material_cache),'material_instance_counts':dict(sorted(material_usage.items())),
        'geometry_variants':len(geom_reports),'decode_error_count':len(decode_errors),'decode_errors':decode_errors,
        'instance_transform_hash':th,'instance_transform_source':tsrc,'materials':material_cache,'geometry':geom_reports,'nodes':node_reports,
        'attribute_coverage':{'uv':sum(g['has_uv'] for g in geom_reports),'normals':sum(g['has_normals'] for g in geom_reports),'tangents':sum(g['has_tangents'] for g in geom_reports),'colors':sum(g['has_colors'] for g in geom_reports)},
        'bounds':check.bounds.tolist() if check.bounds is not None else None,'glb_bytes':a.out.stat().st_size,'glb_sha256':hashlib.sha256(a.out.read_bytes()).hexdigest(),
        'forensic_policy':'No detail-level or material-Unk08 visibility filtering is applied. Every serialized non-empty static placement is retained. The normal retail-visible exporter remains the presentation adapter.'
    }
    jp=a.json or a.out.with_suffix('.json'); jp.write_text(json.dumps(rep,indent=2)+'\n')
    if a.material_selector:
        selector={'status':'D1_ALL_SERIALIZED_STATIC_MATERIAL_DEPENDENCY_SELECTOR','selection_semantics':'Every material FileHash serialized by the validated StaticMapData. The visual=true compatibility bit is transport-only for the legacy generic texture closer; retail_visual records actual Unk08==1 semantics.','materials':{h:{'visual':True,'dependency_selected':True,'retail_visual':bool(r.get('retail_visual')),'unk08':r.get('unk08')} for h,r in sorted(material_cache.items())}}
        a.material_selector.parent.mkdir(parents=True,exist_ok=True); a.material_selector.write_text(json.dumps(selector,indent=2)+'\n')
    print(json.dumps({k:rep[k] for k in ('static_map_data','serialized_placements','exported_placements','detail_level_placement_counts','unique_serialized_material_count','geometry_variants','decode_error_count','attribute_coverage','bounds','glb_bytes')},indent=2))
    return 0 if not decode_errors and len(node_reports)==theoretical else 2


if __name__=='__main__': raise SystemExit(main())
