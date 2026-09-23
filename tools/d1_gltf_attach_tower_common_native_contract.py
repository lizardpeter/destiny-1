#!/usr/bin/env python3
"""Attach exact Tower common native-render contracts to a GLB without visual mutation.

The input GLB remains a portable preview. This tool adds only glTF JSON extras:
- a top-level registry containing the exact 65-family native terminal contracts;
- one per-material exact serialized/native contract link for every D1 common material
  present in the GLB.

The BIN payload is byte-for-byte unchanged. Meshes, nodes, accessors, images,
textures, samplers, animations, skins, cameras, and standard material/PBR fields
remain JSON-identical. Existing extras are preserved and extended.

This is a loss-preserving renderer handoff, not a claim that the portable preview
already reproduces D1 native blend/MRT/global runtime state.
"""
from __future__ import annotations
import argparse,copy,hashlib,json,re,sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
if str(HERE) not in sys.path:sys.path.insert(0,str(HERE))
from d1_gltf_layer_merge import read_glb,write_glb

MAT_RE=re.compile(r'(?:TigerMaterial_|D1_)([0-9A-Fa-f]{8})')
PRESERVE=('accessors','animations','bufferViews','cameras','images','meshes','nodes',
          'samplers','skins','textures')
PRESERVE_MATERIAL_FIELDS=('pbrMetallicRoughness','normalTexture','occlusionTexture',
                          'emissiveTexture','emissiveFactor','alphaMode','alphaCutoff',
                          'doubleSided','extensions')

def digest_bytes(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def digest_json(v)->str:
    return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),
                                     ensure_ascii=False).encode()).hexdigest()

def norm(x):return str(x).upper().removeprefix('0X').zfill(8)

def material_hash(mat:dict)->str|None:
    m=MAT_RE.search(str(mat.get('name') or ''))
    return m.group(1).upper() if m else None

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--input-glb',type=Path,required=True)
    ap.add_argument('--contract',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--report',type=Path,required=True)
    a=ap.parse_args()

    contract=json.loads(a.contract.read_text())
    if contract.get('status')!='D1_TOWER_COMMON_NATIVE_MATERIAL_CONTRACT_EXACT':
        raise SystemExit(f"native contract not exact: {contract.get('status')}")
    if contract.get('shader_family_count')!=65 or contract.get('material_count')!=99:
        raise SystemExit('native contract corpus size drift')
    if contract.get('violations'):
        raise SystemExit(f"native contract violations: {contract['violations']!r}")

    src,binb=read_glb(a.input_glb)
    doc=copy.deepcopy(src)
    before={k:digest_json(src.get(k,[])) for k in PRESERVE}
    before_material_fields=[]
    for m in src.get('materials',[]):
        before_material_fields.append({
            k:copy.deepcopy(m.get(k)) for k in PRESERVE_MATERIAL_FIELDS if k in m
        })

    registry=copy.deepcopy(contract['shader_families'])
    materials=contract['materials']
    contract_sha=hashlib.sha256(a.contract.read_bytes()).hexdigest()

    root_extra=copy.deepcopy(doc.get('extras') or {})
    if 'd1_tower_common_native_shader_registry' in root_extra:
        raise SystemExit('input GLB already contains native shader registry')
    root_extra['d1_tower_common_native_shader_registry']={
        'schema':'d1_tower_common_native_shader_registry/v1',
        'source_contract_sha256':contract_sha,
        'shader_family_count':65,
        'flattened_equation_family_count':contract['flattened_equation_family_count'],
        'cfg_program_family_count':contract['cfg_program_family_count'],
        'shader_families':registry,
        'policy':(
            'Exact native terminal behavior registry. Portable material slots remain preview '
            'adapters. Nonmaterial runtime values, framebuffer/blend order and hardware '
            'filter/derivative behavior remain subject to each family replay boundary.'
        ),
    }
    doc['extras']=root_extra

    matched=[];unmatched=[];seen=set()
    for idx,mat in enumerate(doc.get('materials',[])):
        mh=material_hash(mat)
        if not mh:
            continue
        rec=materials.get(mh)
        if rec is None:
            unmatched.append({'material_index':idx,'name':mat.get('name'),'hash':mh})
            continue
        seen.add(mh)
        mex=copy.deepcopy(mat.get('extras') or {})
        if 'd1_native_render_contract' in mex:
            raise SystemExit(f'{mh}: material already contains native render contract')
        mex['d1_native_render_contract']={
            'schema':'d1_tower_common_material_link/v1',
            'material':mh,
            'source_contract_sha256':contract_sha,
            'vertex_shader':rec['vertex_shader'],
            'pixel_shader':rec['pixel_shader'],
            'native_pixel_shader':rec['native_pixel_shader'],
            'gcn_sha256':rec['gcn_sha256'],
            'shader_registry_key':rec['pixel_shader'],
            'texture_bindings':rec['texture_bindings'],
            'ps_sampler_records':rec['ps_sampler_records'],
            'ps_tfx_bytes_hex':rec['ps_tfx_bytes_hex'],
            'ps_vector4_container':rec['ps_vector4_container'],
            'material_api0_dwords_used':rec['material_api0_dwords_used'],
            'nonmaterial_runtime_inputs':rec['nonmaterial_runtime_inputs'],
            'initial_vgpr_inputs':rec['initial_vgpr_inputs'],
            'replay_boundary':rec['replay_boundary'],
        }
        mat['extras']=mex
        matched.append({'material_index':idx,'name':mat.get('name'),'hash':mh,
                        'pixel_shader':rec['pixel_shader']})

    if not matched:
        raise SystemExit('input GLB contains no common material contract matches')

    a.out.parent.mkdir(parents=True,exist_ok=True)
    write_glb(a.out,doc,binb)
    chk,chkbin=read_glb(a.out)

    if chkbin!=binb:
        raise SystemExit('BIN payload changed while attaching native contract')
    for k in PRESERVE:
        got=digest_json(chk.get(k,[]))
        if got!=before[k]:
            raise SystemExit(f'{k} JSON changed while attaching native contract')

    if len(chk.get('materials',[]))!=len(before_material_fields):
        raise SystemExit('material count changed')
    for i,(m,b) in enumerate(zip(chk.get('materials',[]),before_material_fields)):
        got={k:copy.deepcopy(m.get(k)) for k in PRESERVE_MATERIAL_FIELDS if k in m}
        if got!=b:
            raise SystemExit(f'material {i} portable fields changed')

    linked=[]
    for i,m in enumerate(chk.get('materials',[])):
        link=(m.get('extras') or {}).get('d1_native_render_contract')
        if link:
            sh=norm(link.get('shader_registry_key'))
            if sh not in registry:
                raise SystemExit(f'material {i}: shader registry key {sh} missing')
            linked.append(i)

    rep={
        'schema':'d1_gltf_tower_common_native_contract_attach/v1',
        'status':'D1_GLTF_TOWER_COMMON_NATIVE_CONTRACT_ATTACHED_EXACT',
        'input_glb':str(a.input_glb),
        'input_glb_sha256':hashlib.sha256(a.input_glb.read_bytes()).hexdigest(),
        'contract':str(a.contract),
        'contract_sha256':contract_sha,
        'output_glb':str(a.out),
        'output_glb_sha256':hashlib.sha256(a.out.read_bytes()).hexdigest(),
        'output_bytes':a.out.stat().st_size,
        'bin_bytes':len(binb),
        'bin_sha256':digest_bytes(binb),
        'bin_payload_unchanged':True,
        'shader_registry_family_count':len(registry),
        'glb_material_count':len(chk.get('materials',[])),
        'native_contract_link_count':len(linked),
        'unique_native_contract_material_hash_count':len(seen),
        'matched_materials':matched,
        'unmatched_d1_materials':unmatched,
        'preserved_json_arrays':list(PRESERVE),
        'portable_material_fields_unchanged':True,
        'policy':(
            'Only extras are extended. Native contract metadata is authoritative; '
            'portable PBR slots remain preview state and are not promoted to native D1 semantics.'
        ),
    }
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.report.write_text(json.dumps(rep,indent=2)+'\n')
    print(json.dumps({k:rep[k] for k in (
        'status','shader_registry_family_count','glb_material_count',
        'native_contract_link_count','unique_native_contract_material_hash_count',
        'bin_payload_unchanged','portable_material_fields_unchanged','output_bytes'
    )},indent=2))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
