#!/usr/bin/env python3
"""Bind exact retail D1 skins to the 13 source-owned Tower spawned-actor model GLBs.

Inputs are the exact model GLBs/model report, the closed spawned-actor skin census,
and the verified universal package catalog.  For each family this tool:

* reopens the exact source skeleton and primary vertex streams;
* decodes the already source-closed D1 inline skin format;
* uses each exported range's preserved ``source_vertex_indices`` to select the
  corresponding retail JOINTS/WEIGHTS rows;
* emits JOINTS_0 as U16 and WEIGHTS_0 as bit-exact float32(U8/255), never
  renormalizing or repairing weights;
* appends the exact D1 bind hierarchy and inverse-bind matrices;
* assigns one Skin to every geometry node in that model GLB.

No animation clip, default action, actor location, or material approximation is
introduced here.  Geometry/material bytes from the input GLB remain an exact prefix
of the output binary chunk.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import sys
from pathlib import Path

import numpy as np
from pygltflib import GLTF2, Node, Skin

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))

from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_split_tar_extract import SplitHttpTar
from d1_remote_activity_placements import RemoteCorpus
from d1_gltf_bind_rigid_animation import append_accessor, FLOAT, UNSIGNED_SHORT, ARRAY_BUFFER
from d1_tower_family_e_animated_layer import decode_inline_arrays, exact_float32_weights

NULLS={'00000000','FFFFFFFF'}

def norm(x):return str(x).upper().removeprefix('0X').zfill(8)
def sha256(p:Path):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()

def model_report_row(doc,model):
 rows=[x for x in doc.get('models',[]) if norm(x.get('model'))==model]
 if len(rows)!=1:raise ValueError(f'{model}: expected one model-report row, got {len(rows)}')
 return rows[0]

def family_by_model(doc):
 out={}
 for f in doc.get('families',[]):
  model=norm(f.get('model') or ((f.get('models') or ['FFFFFFFF'])[0]))
  if model in out:raise ValueError(f'duplicate skin family model {model}')
  out[model]=f
 return out

def payload(c,h,expected_ref=None):
 h=norm(h);m=c.entry_meta(h);b,src=c.payload(h)
 if m is None or b is None:raise KeyError(f'{h}: payload unavailable')
 ref=norm(m.get('reference','FFFFFFFF'))
 if expected_ref is not None and ref!=norm(expected_ref):raise ValueError(f'{h}: ref {ref} != {expected_ref}')
 return m,b,src

def source_stream(c,mesh_row,bone_count):
 ps=mesh_row.get('primary_stream') or {};header=norm(ps.get('hash') or mesh_row.get('vertices1'))
 hm,hb,hsrc=payload(c,header)
 if len(hb)<6:raise ValueError(f'{header}: vertex header shorter than stride field')
 stride=int.from_bytes(hb[4:6],'little',signed=True)
 if stride!=int(mesh_row.get('primary_stride',stride)):raise ValueError(f'{header}: live stride {stride} != census {mesh_row.get("primary_stride")}')
 backing=norm(hm.get('reference','FFFFFFFF'))
 bm,bb,bsrc=payload(c,backing)
 joints,raw,weights,meta=decode_inline_arrays(bb,stride,bone_count)
 expected=mesh_row.get('skin') or {}
 if expected.get('storage')!='inline_primary':raise ValueError(f'{header}: census storage is not inline_primary')
 if int(expected.get('vertex_count',-1))!=int(meta['vertex_count']):raise ValueError(f'{header}: vertex-count drift')
 if dict(expected.get('mode_counts') or {})!=dict(meta['mode_counts']):raise ValueError(f'{header}: mode-count drift')
 if [int(x) for x in expected.get('bone_domain',[])]!=[int(x) for x in meta['bone_domain']]:raise ValueError(f'{header}: bone-domain drift')
 if (expected.get('weight_sum_min'),expected.get('weight_sum_max'))!=(255,255):raise ValueError(f'{header}: census raw-weight invariant not 255')
 return {'header':header,'backing':backing,'stride':stride,'joints':joints,'raw':raw,'weights':weights,'meta':meta,'header_source':hsrc,'backing_source':bsrc}

def main()->int:
 ap=argparse.ArgumentParser();ap.add_argument('--model-dir',type=Path,required=True);ap.add_argument('--model-report',type=Path,required=True);ap.add_argument('--skin-census',type=Path,required=True);ap.add_argument('--member-catalog',type=Path,action='append',required=True);ap.add_argument('--base-url',required=True);ap.add_argument('--part-count',type=int,default=10);ap.add_argument('--runtime',type=Path,required=True);ap.add_argument('--parser-root',type=Path,required=True);ap.add_argument('--out-dir',type=Path,required=True);ap.add_argument('--report',type=Path,required=True);a=ap.parse_args()
 model_doc=json.loads(a.model_report.read_text());skin_doc=json.loads(a.skin_census.read_text())
 if model_doc.get('status')!='D1_WORLD_ARTICULATED_MODEL_SET_COMPLETE':raise SystemExit('model report not complete')
 if skin_doc.get('status')!='D1_TOWER_SPAWNED_ACTOR_SKIN_CENSUS_COMPLETE' or skin_doc.get('violations') or skin_doc.get('frontiers'):raise SystemExit('spawned actor skin census not completely closed')
 fams=family_by_model(skin_doc)
 if len(fams)!=13:raise ValueError(f'expected 13 skin families, got {len(fams)}')
 cats=load_catalogs(a.member_catalog);arc=SplitHttpTar([f"{a.base_url.rstrip('/')}/packages.tar.{i:03d}" for i in range(1,a.part_count+1)],retries=6,timeout=90);c=RemoteCorpus(arc,cats,a.runtime)
 sys.path.insert(0,str(a.parser_root.resolve()))
 from tag.game_version import Game_Version
 from tag_readers.read_skeleton import read_skeleton,transform_to_np_matrix
 from matrix_operations.numpy_matrix_operations import np_decompose_matrix
 from fnv_hashes.bones_names import convert_hash_to_bungie_name
 ver=Game_Version.D1_ROI
 a.out_dir.mkdir(parents=True,exist_ok=True);reports=[];viol=[]
 for model,f in sorted(fams.items()):
  try:
   inp=a.model_dir/f'{model}.glb';outp=a.out_dir/f'{model}_SKINNED.glb'
   if not inp.exists():raise FileNotFoundError(inp)
   mr=model_report_row(model_doc,model);bone_counts=[int(x) for x in f.get('bone_counts',[])]
   sks=[norm(x) for x in f.get('skeleton_resources',[])];rigs=[norm(x) for x in f.get('runtime_rig_resources',[])]
   if len(bone_counts)!=1 or len(sks)!=1 or len(rigs)!=1:raise ValueError(f'{model}: non-singleton bones/skeleton/rig {bone_counts}/{sks}/{rigs}')
   bone_count=bone_counts[0];skh=sks[0];righ=rigs[0]
   sm,sb,ssrc=payload(c,skh,'80800861');sk=read_skeleton(io.BytesIO(sb),ver)
   if len(sk.node_defs)!=bone_count:raise ValueError(f'{model}: live skeleton nodes {len(sk.node_defs)} != {bone_count}')
   streams={int(x['mesh_index']):source_stream(c,x,bone_count) for x in f.get('meshes',[])}
   if len(streams)!=int(f.get('mesh_count',-1)):raise ValueError(f'{model}: skin mesh coverage drift')
   g=GLTF2().load_binary(str(inp));
   if len(g.buffers)!=1:raise ValueError(f'{model}: expected one-buffer GLB')
   if g.skins is None:g.skins=[]
   if g.skins:raise ValueError(f'{model}: input already has skins')
   original_blob=bytes(g.binary_blob() or b'');blob=bytearray(original_blob);original_nodes=len(g.nodes or []);original_meshes=len(g.meshes or [])
   range_by_name={str(x['name']):x for x in mr.get('ranges',[])};seen=set();bound_vertices=0;bound_prims=0;raw_min=255;raw_max=255;float_err=0.0;bind_rows=[]
   for gi,gm in enumerate(g.meshes or []):
    ex=gm.extras or {};emodel=norm(ex.get('model',model))
    if emodel!=model:raise ValueError(f'{model}: mesh {gi} model extra {emodel}')
    if len(gm.primitives)!=1:raise ValueError(f'{model}: mesh {gi} expected one primitive')
    prim=gm.primitives[0];rr=range_by_name.get(str(gm.name)) or range_by_name.get(str(gm.name).split('__')[-1])
    if rr is None:raise ValueError(f'{model}: mesh {gi} range {gm.name!r} missing from report')
    seen.add(rr['name']);mi=int(ex.get('mesh_index',rr['mesh_index']))
    if mi!=int(rr['mesh_index']):raise ValueError(f'{model}/{rr["name"]}: mesh index drift')
    src=[int(x) for x in ex.get('source_vertex_indices',[])]
    if prim.attributes.POSITION is None:raise ValueError(f'{model}/{rr["name"]}: missing POSITION')
    n=int(g.accessors[prim.attributes.POSITION].count)
    if len(src)!=n or int(rr.get('source_vertex_count',-1))!=n:raise ValueError(f'{model}/{rr["name"]}: source vertex mapping/count drift {len(src)}/{n}/{rr.get("source_vertex_count")}')
    if not src or len(set(src))!=len(src):raise ValueError(f'{model}/{rr["name"]}: source indices absent/duplicated')
    st=streams[mi]
    if min(src)<0 or max(src)>=st['meta']['vertex_count']:raise ValueError(f'{model}/{rr["name"]}: source index OOB')
    joints=st['joints'][src];raw=st['raw'][src];weights=st['weights'][src];sums=np.sum(raw.astype(np.uint16),axis=1,dtype=np.uint16)
    if not np.all(sums==255):raise ValueError(f'{model}/{rr["name"]}: raw weight sums not 255')
    expected=exact_float32_weights(raw)
    if not np.array_equal(weights.view(np.uint32),expected.view(np.uint32)):raise ValueError(f'{model}/{rr["name"]}: float transport not bit-exact U8/255')
    fs=np.sum(weights,axis=1,dtype=np.float32);fe=float(np.max(np.abs(fs-np.float32(1.0)))) if len(fs) else 0.0;float_err=max(float_err,fe)
    jacc=append_accessor(g,blob,joints,component_type=UNSIGNED_SHORT,accessor_type='VEC4',target=ARRAY_BUFFER);wacc=append_accessor(g,blob,weights,component_type=FLOAT,accessor_type='VEC4',target=ARRAY_BUFFER)
    prim.attributes.JOINTS_0=jacc;prim.attributes.WEIGHTS_0=wacc;bound_vertices+=n;bound_prims+=1
    bind_rows.append({'gltf_mesh_index':gi,'range_name':rr['name'],'source_mesh_index':mi,'vertex_count':n,'primary_stride':st['stride'],'skin_modes':st['meta']['mode_counts'],'bone_domain':sorted(set(int(x) for x in joints[raw>0])),'raw_weight_sum_min':int(np.min(sums)),'raw_weight_sum_max':int(np.max(sums)),'float32_weight_sum_abs_error_max':fe})
   if seen!=set(range_by_name):raise ValueError(f'{model}: range coverage {len(seen)} != {len(range_by_name)}')
   world=[transform_to_np_matrix(x) for x in sk.default_obj_space_tr];inv=[transform_to_np_matrix(x) for x in sk.default_inv_obj_space_tr];bone_nodes=[];names=[]
   for i,nd in enumerate(sk.node_defs):
    parent=int(nd.parent_node_index);mat=inv[parent]@world[i] if parent>=0 else world[i];scale,rot,trans=np_decompose_matrix(mat);name=convert_hash_to_bungie_name(int(nd.bone_hash)) or f'{int(nd.bone_hash)&0xffffffff:08X}'
    if name in names:name=f'{name}_{int(nd.bone_hash)&0xffffffff:08X}';names.append(name);idx=len(g.nodes);g.nodes.append(Node(name=name,children=[],translation=[float(x) for x in trans],rotation=[float(x) for x in rot.as_quat()],scale=[float(x) for x in scale],extras={'d1BoneIndex':i,'d1BoneHash':f'{int(nd.bone_hash)&0xffffffff:08X}'}));bone_nodes.append(idx)
   root=len(g.nodes);g.nodes.append(Node(name=f'D1_{model}_Skeleton',children=[],translation=[0,0,0],rotation=[0,0,0,1],scale=[1,1,1],extras={'d1Skeleton':skh,'d1RuntimeRig':righ,'d1Model':model}))
   for i,nd in enumerate(sk.node_defs):
    p=int(nd.parent_node_index)
    if p>=0:g.nodes[bone_nodes[p]].children.append(bone_nodes[i])
    else:g.nodes[root].children.append(bone_nodes[i])
   ib=np.stack([np.asarray(x.T,dtype='<f4') for x in inv],axis=0);ibacc=append_accessor(g,blob,ib,component_type=FLOAT,accessor_type='MAT4');skin_idx=len(g.skins);g.skins.append(Skin(joints=bone_nodes,inverseBindMatrices=ibacc,skeleton=root,name=f'D1_{model}_{skh}_skin'))
   bound_nodes=0
   for ni,node in enumerate(g.nodes[:original_nodes]):
    if node.mesh is not None:
     node.skin=skin_idx;bound_nodes+=1
   scene=g.scenes[g.scene or 0];scene.nodes=list(scene.nodes or [])+[root]
   g.buffers[0].byteLength=len(blob);g.set_binary_blob(bytes(blob));outp.parent.mkdir(parents=True,exist_ok=True);g.save_binary(str(outp))
   check=GLTF2().load_binary(str(outp));actual_blob=bytes(check.binary_blob() or b'')
   if actual_blob[:len(original_blob)]!=original_blob:raise ValueError(f'{model}: input binary prefix not preserved')
   if len(check.skins or [])!=1:raise ValueError(f'{model}: saved skin count drift')
   row={'model':model,'input':str(inp),'output':str(outp),'input_sha256':sha256(inp),'output_sha256':sha256(outp),'input_binary_bytes':len(original_blob),'output_binary_bytes':len(actual_blob),'binary_prefix_exact':True,'skeleton':skh,'runtime_rig':righ,'bone_count':bone_count,'source_model_mesh_count':int(f.get('mesh_count',-1)),'gltf_range_mesh_count':original_meshes,'bound_primitive_count':bound_prims,'bound_mesh_node_count':bound_nodes,'bound_vertex_count':bound_vertices,'skin_index':skin_idx,'joint_node_count':len(bone_nodes),'float32_weight_sum_abs_error_max':float_err,'bind_rows':bind_rows};reports.append(row);print('SKINNED',model,'BONES',bone_count,'RANGES',bound_prims,'VERTICES',bound_vertices,'SHA',row['output_sha256'],flush=True)
  except Exception as ex:
   viol.append(f'{model}:{ex!r}');print('ERROR',model,repr(ex),flush=True)
 out={'schema':'d1_tower_spawned_actor_skin_bind/v1','status':'D1_TOWER_SPAWNED_ACTOR_SKIN_BIND_COMPLETE' if not viol and len(reports)==13 else 'D1_TOWER_SPAWNED_ACTOR_SKIN_BIND_PARTIAL','model_count':len(reports),'expected_model_count':13,'models':reports,'violations':viol,'remote_logical_package_count':len(c.views),'remote_payload_cache_count':len(c.payload_cache),'policy':'JOINTS_0/WEIGHTS_0 are selected only through preserved source_vertex_indices from exact retail primary streams. Retail U8 sums must equal 255 and portable FLOAT values are bit-exact U8/255 with no renormalization. Skeleton hierarchy/inverse binds come directly from source skeleton resources. No animation, location, or default state is selected.'}
 a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(out,indent=2)+'\n');print('STATUS',out['status'],'MODELS',len(reports),'VIOLATIONS',viol);return 0 if out['status'].endswith('_COMPLETE') else 2
if __name__=='__main__':raise SystemExit(main())
