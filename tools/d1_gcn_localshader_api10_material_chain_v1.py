#!/usr/bin/env python3
"""Join exact material ownership to LocalShader API10 typed-buffer programs.

The serialized material slot is retained as provenance only. It is NOT promoted to a
hardware shader stage. This tool proves which retail material entries reference the
LocalShader wrappers whose exact GCN programs read ImmConstBuffer API slot 10; runtime
resource-table construction and backing bytes remain a later gate.
"""
from __future__ import annotations

import argparse, collections, json, re
from pathlib import Path

OWNER_SCHEMA='d1_gcn_material_shader_owner_frontier/v1'
REF_SCHEMA='d1_gcn_material_shader_reference_probe_merged/v1'
REF_STATUS='D1_GCN_MATERIAL_SHADER_REFERENCE_PROBE_MERGED_EXACT'
USAGE_SCHEMA='d1_gcn_localshader_tbuffer_usage_binding/v1'
USAGE_STATUS='D1_GCN_LOCALSHADER_TBUFFER_USAGE_BINDING_EXACT'
SCHEMA='d1_gcn_localshader_api10_material_chain/v1'
STATUS='D1_GCN_LOCALSHADER_API10_MATERIAL_CHAIN_EXACT'
RX=re.compile(r'^shader_header_absent:([0-9A-F]{8}):(VS|PS):([0-9A-F]{8})$')


def is_exact_local(row:dict)->bool:
    te=row.get('target_entry') or {}; re_=row.get('reference_target_entry') or {}
    orb=row.get('reference_target_orbshdr_shape') or {}; bi=orb.get('binary_info') or {}
    return te.get('type')==32 and te.get('subtype')==11 and re_.get('type')==1 and re_.get('subtype')==11 and orb.get('code_bounds_valid') is True and bi.get('stage')=='LocalShader' and bi.get('stage_value')==3 and bool(orb.get('code_sha256'))


def build(owner:dict, ref:dict, usage:dict)->dict:
    violations=[]
    if owner.get('schema')!=OWNER_SCHEMA: violations.append('owner_schema')
    if ref.get('schema')!=REF_SCHEMA or ref.get('status')!=REF_STATUS or ref.get('violations'): violations.append('reference_not_exact')
    if usage.get('schema')!=USAGE_SCHEMA or usage.get('status')!=USAGE_STATUS or usage.get('violations'): violations.append('usage_not_exact')
    locals_by_wrapper={str(r['target']).upper():r for r in ref.get('targets',[]) if is_exact_local(r)}
    if len(locals_by_wrapper)!=177: violations.append(f'local_wrapper_denominator:{len(locals_by_wrapper)}')
    tbuffer_wrappers={str(w).upper():p for p in usage.get('programs',[]) for w in p.get('wrappers',[])}
    if len(tbuffer_wrappers)!=56: violations.append(f'tbuffer_wrapper_denominator:{len(tbuffer_wrappers)}')
    if not set(tbuffer_wrappers)<=set(locals_by_wrapper): violations.append('tbuffer_wrapper_not_localshader_subset')
    material_meta={str(m.get('material','')).upper():m for m in owner.get('materials',[]) if isinstance(m,dict)}
    rows=[]; local_occ=0
    for raw in owner.get('violations',[]):
        m=RX.fullmatch(str(raw))
        if not m: continue
        material,slot,wrapper=m.groups(); wrapper=wrapper.upper(); material=material.upper()
        if wrapper not in locals_by_wrapper: continue
        local_occ+=1
        if wrapper not in tbuffer_wrappers: continue
        meta=material_meta.get(material)
        if meta is None:
            violations.append(f'material_metadata_missing:{material}'); continue
        prog=tbuffer_wrappers[wrapper]
        refrow=locals_by_wrapper[wrapper]
        gcn=str((refrow.get('reference_target_orbshdr_shape') or {}).get('code_sha256','')).lower()
        if gcn!=str(prog.get('gcn_sha256','')).lower():
            violations.append(f'gcn_identity_mismatch:{wrapper}'); continue
        rows.append({
            'material':material,'material_payload_sha256':meta.get('payload_sha256'),'material_package_id':meta.get('package_id'),
            'material_logical_view':meta.get('logical_view'),'serialized_material_stage_slot':slot,'localshader_wrapper':wrapper,
            'native_program_reference':str((refrow.get('target_entry') or {}).get('reference','')).upper(),'gcn_sha256':gcn,
            'api_slot':10,'usage_name':'ImmConstBuffer','descriptor_window':prog.get('descriptor_window'),
            'tbuffer_instruction_count':prog.get('tbuffer_instruction_count'),
        })
    rows.sort(key=lambda r:(r['material'],r['localshader_wrapper']))
    if local_occ!=3967: violations.append(f'local_material_occurrence_denominator:{local_occ}')
    if len(rows)!=3386: violations.append(f'api10_material_occurrence_denominator:{len(rows)}')
    if len({r['material'] for r in rows})!=3386: violations.append('api10_material_identity_not_unique')
    if any(r['serialized_material_stage_slot']!='VS' for r in rows): violations.append('unexpected_serialized_slot')
    by_window=collections.Counter(r['descriptor_window'] for r in rows)
    by_program=collections.Counter(r['gcn_sha256'] for r in rows)
    return {
      'schema':SCHEMA,'status':STATUS if not violations else 'D1_GCN_LOCALSHADER_API10_MATERIAL_CHAIN_WITH_VIOLATIONS',
      'coverage':{'exact_localshader_wrapper_count':len(locals_by_wrapper),'localshader_material_occurrence_count':local_occ,
        'api10_tbuffer_wrapper_count':len(tbuffer_wrappers),'api10_material_occurrence_count':len(rows),'api10_unique_material_count':len({r['material'] for r in rows}),
        'api10_program_count':len(by_program),'descriptor_window_material_counts':dict(sorted(by_window.items())),
        'serialized_material_stage_slot_counts':dict(sorted(collections.Counter(r['serialized_material_stage_slot'] for r in rows).items())),
        'runtime_binding_owner_promotions':0,'shader_stage_promotions':0},
      'bindings':rows,'violations':violations,
      'semantic_boundary':{'material_to_localshader_wrapper':'EXACT','wrapper_to_gcn_program':'EXACT','gcn_program_to_api10_usage':'EXACT_IMM_CONST_BUFFER_API_SLOT_10','serialized_material_stage_slot':'PROVENANCE_ONLY_NOT_HARDWARE_STAGE','api10_runtime_binding_owner':'NEXT_GATE','api10_backing_memory_contents':'WITHHELD'},
      'policy':'Exact joins only. Serialized VS/PS material slots are provenance labels, not hardware stage semantics. No runtime API10 owner, descriptor bytes, backing address, constant-buffer layout, or fetched numeric value is inferred.'}


def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument('--owner',type=Path,required=True); ap.add_argument('--reference',type=Path,required=True); ap.add_argument('--usage',type=Path,required=True); ap.add_argument('-o','--output',type=Path,required=True); a=ap.parse_args()
    d=build(json.loads(a.owner.read_text()),json.loads(a.reference.read_text()),json.loads(a.usage.read_text()))
    a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':d['status'],'coverage':d['coverage'],'violations':d['violations'][:20]},indent=2,sort_keys=True))
    return 0 if d['status']==STATUS else 2

if __name__=='__main__': raise SystemExit(main())
