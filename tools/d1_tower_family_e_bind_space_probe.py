#!/usr/bin/env python3
"""Diagnose the 67-bone Tower Family-E bind-space path used by the GLB exporter.

This probe is intentionally source-first.  It reopens the exact 00EC skeleton/runtime
rig and checks the assumptions that can visually explode a skinned character even
when ownership and animation identity are correct:

* are bone_to_control / control_to_bone identity or permutations?
* do default object-space and inverse object-space transforms multiply to identity?
* does the hierarchical local conversion used by the current exporter reconstruct
  every source object-space bind matrix exactly?
* does decomposition/recomposition introduce meaningful bind error?
* if skin joint indices were interpreted as runtime-control indices, what skeleton
  bone indices would they map to?

No mapping is promoted from this diagnostic alone.  The report exists to decide
whether JOINTS_0 must be remapped or whether the remaining visual error lies elsewhere.
"""
from __future__ import annotations

import argparse
import io
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from d1_entry_extract import EntryReader
from d1_tower_family_e_animated_layer import norm, entry_map, exact_payload, decode_all_family_streams

SKELETON='809D8613'
RIG='809D856E'
ENTITY_RESOURCE_REF='80800861'


def err(a,b):
    return float(np.max(np.abs(np.asarray(a,dtype=np.float64)-np.asarray(b,dtype=np.float64))))


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--source-pkg',type=Path,required=True)
    ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('--parser-root',type=Path,required=True)
    ap.add_argument('--skin-census',type=Path,required=True)
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args()

    r=EntryReader(a.source_pkg,a.runtime); by=entry_map(r)
    sys.path.insert(0,str(a.parser_root.resolve()))
    from tag.game_version import Game_Version
    from tag_readers.read_skeleton import read_skeleton, transform_to_np_matrix
    from tag_readers.read_rig import read_runtime_rig
    from matrix_operations.numpy_matrix_operations import np_decompose_matrix
    from fnv_hashes.bones_names import convert_hash_to_bungie_name
    import glm
    from matrix_operations.glm_matrix_operations import glm_compose_mat4
    ver=Game_Version.D1_ROI

    _,sb=exact_payload(r,by,SKELETON,ENTITY_RESOURCE_REF); sk=read_skeleton(io.BytesIO(sb),ver)
    _,rb=exact_payload(r,by,RIG,ENTITY_RESOURCE_REF); rig=read_runtime_rig(io.BytesIO(rb),ver)
    if len(sk.node_defs)!=67 or len(rig.controls_relations)!=67:
        raise ValueError('Family-E dimensions are not 67/67')

    world=[transform_to_np_matrix(x).astype(np.float64) for x in sk.default_obj_space_tr]
    inv=[transform_to_np_matrix(x).astype(np.float64) for x in sk.default_inv_obj_space_tr]
    bone_to_control=[int(x) for x in rig.bone_to_control]
    control_to_bone=[int(x) for x in rig.control_to_bone]

    # Direct inverse sanity.
    inverse_rows=[]
    inverse_max=0.0
    ident=np.eye(4,dtype=np.float64)
    for i,(w,iw) in enumerate(zip(world,inv)):
        e1=err(w@iw,ident); e2=err(iw@w,ident); inverse_max=max(inverse_max,e1,e2)
        inverse_rows.append({'bone_index':i,'world_times_inv_error':e1,'inv_times_world_error':e2})

    # Current exporter local conversion: parent_inv_world @ child_world.
    local=[]
    decomposition_rows=[]
    decomp_max=0.0
    for i,nd in enumerate(sk.node_defs):
        parent=int(nd.parent_node_index)
        m=(inv[parent]@world[i]) if parent>=0 else world[i]
        local.append(m)
        sc,rot,tr=np_decompose_matrix(m)
        # Recompose through the same parser helper semantics.
        rm=np.array(glm_compose_mat4(glm.vec3(*[float(x) for x in tr]), glm.quat(float(rot.as_quat()[3]), float(rot.as_quat()[0]), float(rot.as_quat()[1]), float(rot.as_quat()[2])), glm.vec3(*[float(x) for x in sc])),dtype=np.float64)
        de=err(m,rm); decomp_max=max(decomp_max,de)
        decomposition_rows.append({'bone_index':i,'error':de})

    # Reconstruct object/world space from the locals using parent @ local.
    reconstructed=[]; hierarchy_rows=[]; hierarchy_max=0.0
    for i,nd in enumerate(sk.node_defs):
        parent=int(nd.parent_node_index)
        rec=(reconstructed[parent]@local[i]) if parent>=0 else local[i]
        reconstructed.append(rec)
        he=err(rec,world[i]); hierarchy_max=max(hierarchy_max,he)
        hierarchy_rows.append({'bone_index':i,'parent':parent,'error':he})

    # Also test the opposite row-vector composition/order as a diagnostic contrast.
    local_alt=[]
    for i,nd in enumerate(sk.node_defs):
        parent=int(nd.parent_node_index)
        local_alt.append((world[i]@inv[parent]) if parent>=0 else world[i])
    recon_alt=[]; alt_max=0.0
    for i,nd in enumerate(sk.node_defs):
        parent=int(nd.parent_node_index)
        rec=(local_alt[i]@recon_alt[parent]) if parent>=0 else local_alt[i]
        recon_alt.append(rec); alt_max=max(alt_max,err(rec,world[i]))

    # Source skin index domain and hypothetical control->bone remap domain.
    skin_doc=json.loads(a.skin_census.read_text())
    f=[x for x in skin_doc.get('families',[]) if SKELETON in [norm(y) for y in x.get('skeleton_resources',[])]][0]
    streams=decode_all_family_streams(r,f,67)
    source_domain=sorted({int(j) for s in streams.values() for j in s['meta']['bone_domain']})
    remapped_domain=[]
    remap_possible=True
    for j in source_domain:
        if not 0<=j<len(control_to_bone) or not 0<=control_to_bone[j]<67:
            remap_possible=False
            continue
        remapped_domain.append(control_to_bone[j])
    remapped_domain=sorted(set(remapped_domain))

    bones=[]
    for i,nd in enumerate(sk.node_defs):
        h=int(nd.bone_hash)&0xffffffff
        bones.append({'bone_index':i,'parent':int(nd.parent_node_index),'hash':f'{h:08X}','name':convert_hash_to_bungie_name(h),
                      'bone_to_control':bone_to_control[i] if i<len(bone_to_control) else None})

    out={
      'schema_version':1,
      'status':'D1_TOWER_FAMILY_E_BIND_SPACE_DIAGNOSTIC_COMPLETE',
      'skeleton':SKELETON,'runtime_rig':RIG,
      'node_count':len(sk.node_defs),'control_count':len(rig.controls_relations),
      'bone_to_control':bone_to_control,'control_to_bone':control_to_bone,
      'bone_to_control_identity':bone_to_control==list(range(67)),
      'control_to_bone_identity':control_to_bone==list(range(67)),
      'bone_to_control_is_permutation':sorted(bone_to_control)==list(range(67)),
      'control_to_bone_is_permutation':sorted(control_to_bone)==list(range(67)),
      'inverse_identity_error_max':inverse_max,
      'current_hierarchy_reconstruction_error_max':hierarchy_max,
      'alternate_row_hierarchy_reconstruction_error_max':alt_max,
      'decompose_recompose_error_max':decomp_max,
      'source_skin_joint_domain':source_domain,
      'hypothetical_control_to_bone_remap_possible':remap_possible,
      'hypothetical_control_to_bone_remapped_domain':remapped_domain,
      'skin_domain_changes_under_control_to_bone':source_domain!=remapped_domain,
      'bones':bones,
      'inverse_checks':inverse_rows,
      'hierarchy_checks':hierarchy_rows,
      'decomposition_checks':decomposition_rows,
      'policy':'This is a structural diagnostic.  A non-identity runtime-rig permutation does not by itself prove that mesh JOINTS are control indices.  Conversely, exact hierarchy roundtrip rules out the current local-bind matrix order as the source of visual explosion.'
    }
    a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ('status','bone_to_control_identity','control_to_bone_identity','bone_to_control_is_permutation','control_to_bone_is_permutation','inverse_identity_error_max','current_hierarchy_reconstruction_error_max','alternate_row_hierarchy_reconstruction_error_max','decompose_recompose_error_max','source_skin_joint_domain','hypothetical_control_to_bone_remapped_domain','skin_domain_changes_under_control_to_bone')},indent=2))
    return 0

if __name__=='__main__': raise SystemExit(main())
