#!/usr/bin/env python3
"""Corrected production driver for exact Tower spawned-actor model skin binding.

This reuses only the pure evidence/helper functions from v1 and owns the glTF mutation
path here.  It exists to keep the first experimental binder checkpoint immutable while
making the production implementation explicit and testable.
"""
from __future__ import annotations
import argparse,io,json,sys
from pathlib import Path
import numpy as np
from pygltflib import GLTF2,Node,Skin
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from d1_tower_spawned_actor_skin_bind import norm,sha256,model_report_row,family_by_model,payload,source_stream
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_split_tar_extract import SplitHttpTar
from d1_remote_activity_placements import RemoteCorpus
from d1_gltf_bind_rigid_animation import append_accessor,FLOAT,UNSIGNED_SHORT,ARRAY_BUFFER
from d1_tower_family_e_animated_layer import exact_float32_weights

def main()->int:
 ap=argparse.ArgumentParser();ap.add_argument('--model-dir',type=Path,required=True);ap.add_argument('--model-report',type=Path,required=True);ap.add_argument('--skin-census',type=Path,required=True);ap.add_argument('--member-catalog',type=Path,action='append',required=True);ap.add_argument('--base-url',required=True);ap.add_argument('--part-count',type=int,default=10);ap.add_argument('--runtime',type=Path,required=True);ap.add_argument('--parser-root',type=Path,required=True);ap.add_argument('--out-dir',type=Path,required=True);ap.add_argument('--report',type=Path,required=True);a=ap.parse_args()
 md=json.loads(a.model_report.read_text());sd=json.loads(a.skin_census.read_text())
 if md.get('status')!='D1_WORLD_ARTICULATED_MODEL_SET_COMPLETE':raise SystemExit('model report not complete')
 if sd.get('status')!='D1_TOWER_SPAWNED_ACTOR_SKIN_CENSUS_COMPLETE' or sd.get('violations') or sd.get('frontiers'):raise SystemExit('skin census not closed')
 fams=family_by_model(sd)
 if len(fams)!=13:raise ValueError(f'expected 13 families, got {len(fams)}')
 cats=load_catalogs(a.member_catalog);arc=SplitHttpTar([f"{a.base_url.rstrip('/')}/packages.tar.{i:03d}" for i in range(1,a.part_count+1)],retries=6,timeout=90);c=RemoteCorpus(arc,cats,a.runtime)
 sys.path.insert(0,str(a.parser_root.resolve()))
 from tag.game_version import Game_Version
 from tag_readers.read_skeleton import read_skeleton,transform_to_np_matrix
 from matrix_operations.numpy_matrix_operations import np_decompose_matrix
 from fnv_hashes.bones_names import convert_hash_to_bungie_name
 ver=Game_Version.D1_ROI;a.out_dir.mkdir(parents=True,exist_ok=True);done=[];viol=[]
 for model,f in sorted(fams.items()):
  try:
   inp=a.model_dir/f'{model}.glb';dst=a.out_dir/f'{model}_SKINNED.glb';mr=model_report_row(md,model)
   bones=[int(x) for x in f.get('bone_counts',[])];sks=[norm(x) for x in f.get('skeleton_resources',[])];rigs=[norm(x) for x in f.get('runtime_rig_resources',[])]
   if len(bones)!=len(sks)!=1:pass
   if len(bones)!=1 or len(sks)!=1 or len(rigs)!=1:raise ValueError(f'non-singleton family dimensions {bones}/{sks}/{rigs}')
   bone_count=bones[0];skh=sks[0];righ=rigs[0];_,sb,ssrc=payload(c,skh,'80800861');sk=read_skeleton(io.BytesIO(sb),ver)
   if len(sk.node_defs)!=bone_count:raise ValueError(f'skeleton nodes {len(sk.node_defs)} != {bone_count}')
   streams={int(x['mesh_index']):source_stream(c,x,bone_count) for x in f.get('meshes',[])}
   g=GLTF2().load_binary(str(inp));
   if len(g.buffers)!=1:raise ValueError('not one-buffer GLB')
   if g.skins is None:g.skins=[]
   if g.skins:raise ValueError('input already skinned')
   original=bytes(g.binary_blob() or b'');blob=bytearray(original);original_nodes=len(g.nodes or []);original_meshes=len(g.meshes or [])
   ranges={str(x['name']):x for x in mr.get('ranges',[])};seen=set();bound_vertices=0;bind=[];float_err=0.0
   for gi,gm in enumerate(g.meshes or []):
    if len(gm.primitives)!=1:raise ValueError(f'mesh {gi} primitive count !=1')
    ex=gm.extras or {};rr=ranges.get(str(gm.name)) or ranges.get(str(gm.name).split('__')[-1])
    if rr is None:raise ValueError(f'mesh {gi} range {gm.name!r} not in report')
    seen.add(str(rr['name']));mi=int(ex.get('mesh_index',rr['mesh_index']));src=[int(x) for x in ex.get('source_vertex_indices',[])]
    prim=gm.primitives[0]
    if prim.attributes.POSITION is None:raise ValueError(f'{rr["name"]}: no POSITION')
    n=int(g.accessors[prim.attributes.POSITION].count)
    if mi!=int(rr['mesh_index']) or len(src)!=n or int(rr['source_vertex_count'])!=n or not src or len(set(src))!=len(src):raise ValueError(f'{rr["name"]}: exact source vertex mapping drift')
    st=streams[mi]
    if min(src)<0 or max(src)>=st['meta']['vertex_count']:raise ValueError(f'{rr["name"]}: source vertex OOB')
    joints=st['joints'][src];raw=st['raw'][src];weights=st['weights'][src];sums=np.sum(raw.astype(np.uint16),axis=1,dtype=np.uint16)
    if not np.all(sums==255):raise ValueError(f'{rr["name"]}: raw sums !=255')
    if not np.array_equal(weights.view(np.uint32),exact_float32_weights(raw).view(np.uint32)):raise ValueError(f'{rr["name"]}: float32 conversion drift')
    fs=np.sum(weights,axis=1,dtype=np.float32);fe=float(np.max(np.abs(fs-np.float32(1.0)))) if len(fs) else 0.0;float_err=max(float_err,fe)
    prim.attributes.JOINTS_0=append_accessor(g,blob,joints,component_type=UNSIGNED_SHORT,accessor_type='VEC4',target=ARRAY_BUFFER)
    prim.attributes.WEIGHTS_0=append_accessor(g,blob,weights,component_type=FLOAT,accessor_type='VEC4',target=ARRAY_BUFFER)
    bound_vertices+=n;bind.append({'gltf_mesh_index':gi,'range_name':rr['name'],'source_mesh_index':mi,'vertex_count':n,'primary_stride':st['stride'],'skin_modes':st['meta']['mode_counts'],'bone_domain':sorted(set(int(x) for x in joints[raw>0])),'raw_weight_sum_min':int(np.min(sums)),'raw_weight_sum_max':int(np.max(sums)),'float32_weight_sum_abs_error_max':fe})
   if seen!=set(ranges):raise ValueError(f'range coverage {len(seen)}/{len(ranges)}')
   world=[transform_to_np_matrix(x) for x in sk.default_obj_space_tr];inv=[transform_to_np_matrix(x) for x in sk.default_inv_obj_space_tr];bn=[];used_names=set()
   for i,nd in enumerate(sk.node_defs):
    parent=int(nd.parent_node_index);mat=inv[parent]@world[i] if parent>=0 else world[i];scale,rot,trans=np_decompose_matrix(mat);name=convert_hash_to_bungie_name(int(nd.bone_hash)) or f'{int(nd.bone_hash)&0xffffffff:08X}'
    if name in used_names:name=f'{name}_{int(nd.bone_hash)&0xffffffff:08X}'
    used_names.add(name);idx=len(g.nodes);g.nodes.append(Node(name=name,children=[],translation=[float(x) for x in trans],rotation=[float(x) for x in rot.as_quat()],scale=[float(x) for x in scale],extras={'d1BoneIndex':i,'d1BoneHash':f'{int(nd.bone_hash)&0xffffffff:08X}'}));bn.append(idx)
   if len(bn)!=bone_count:raise ValueError(f'joint-node construction {len(bn)} != {bone_count}')
   root=len(g.nodes);g.nodes.append(Node(name=f'D1_{model}_Skeleton',children=[],translation=[0,0,0],rotation=[0,0,0,1],scale=[1,1,1],extras={'d1Model':model,'d1Skeleton':skh,'d1RuntimeRig':righ}))
   for i,nd in enumerate(sk.node_defs):
    p=int(nd.parent_node_index)
    if p>=0:g.nodes[bn[p]].children.append(bn[i])
    else:g.nodes[root].children.append(bn[i])
   ib=np.stack([np.asarray(m.T,dtype='<f4') for m in inv],axis=0);ibacc=append_accessor(g,blob,ib,component_type=FLOAT,accessor_type='MAT4');si=len(g.skins);g.skins.append(Skin(joints=bn,inverseBindMatrices=ibacc,skeleton=root,name=f'D1_{model}_{skh}_skin'))
   bound_nodes=0
   for node in g.nodes[:original_nodes]:
    if node.mesh is not None:node.skin=si;bound_nodes+=1
   scene=g.scenes[g.scene or 0];scene.nodes=list(scene.nodes or [])+[root];g.buffers[0].byteLength=len(blob);g.set_binary_blob(bytes(blob));g.save_binary(str(dst))
   chk=GLTF2().load_binary(str(dst));cb=bytes(chk.binary_blob() or b'')
   if cb[:len(original)]!=original:raise ValueError('input binary prefix changed')
   if len(chk.skins or [])!=1 or len((chk.skins or [])[0].joints or [])!=bone_count:raise ValueError('saved skin/joint count drift')
   r={'model':model,'input':str(inp),'output':str(dst),'input_sha256':sha256(inp),'output_sha256':sha256(dst),'binary_prefix_exact':True,'input_binary_bytes':len(original),'output_binary_bytes':len(cb),'skeleton':skh,'runtime_rig':righ,'bone_count':bone_count,'source_model_mesh_count':int(f.get('mesh_count',-1)),'gltf_range_mesh_count':original_meshes,'bound_primitive_count':len(bind),'bound_mesh_node_count':bound_nodes,'bound_vertex_count':bound_vertices,'float32_weight_sum_abs_error_max':float_err,'bind_rows':bind};done.append(r);print('SKINNED',model,'BONES',bone_count,'RANGES',len(bind),'VERTICES',bound_vertices,'SHA',r['output_sha256'],flush=True)
  except Exception as ex:
   viol.append(f'{model}:{ex!r}');print('ERROR',model,repr(ex),flush=True)
 out={'schema':'d1_tower_spawned_actor_skin_bind/v2','status':'D1_TOWER_SPAWNED_ACTOR_SKIN_BIND_COMPLETE' if len(done)==13 and not viol else 'D1_TOWER_SPAWNED_ACTOR_SKIN_BIND_PARTIAL','model_count':len(done),'expected_model_count':13,'models':done,'violations':viol,'remote_logical_package_count':len(c.views),'remote_payload_cache_count':len(c.payload_cache),'policy':'Exact source_vertex_indices select exact retail JOINTS/WEIGHTS. U8 sums must be 255; FLOAT transport is bit-exact U8/255 with no renormalization. Skeleton hierarchy/inverse-bind matrices are decoded from exact source skeletons. No animation or location is selected.'}
 a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(out,indent=2)+'\n');print('STATUS',out['status'],'MODELS',len(done),'VIOLATIONS',viol);return 0 if not viol and len(done)==13 else 2
if __name__=='__main__':raise SystemExit(main())
