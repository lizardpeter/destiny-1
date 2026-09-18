#!/usr/bin/env python3
"""Fail-closed source exclusion proof for assigning a TfxScope name to API10.

Pinned D1 Charm source says TfxScope is based on CBuffer index but contains no
index 10. The exact LocalShader API10 membership corpus therefore cannot inherit
an engine-facing scope name from this source. This is deliberately negative
proof: it preserves runtime writer, backing allocation and engine semantic as
WITHHELD.
"""
import argparse, json, re
from pathlib import Path

EXPECTED={1:'Instance',2:'Transparent',3:'Unk3',8:'Unk8',9:'Decal',12:'View',13:'Frame'}
CHARM_COMMIT='50d36ee1f9ecadad7522504c20b1f3f9c97e30af'
CHARM_BLOB='7311688c71ab3a9e9d6eacd5393d07254688bace'

def parse(text):
    m=re.search(r'public\s+enum\s+TfxScope\s*:\s*byte\s*\{(.*?)\}',text,re.S)
    if not m: raise ValueError('TfxScope enum missing')
    return {int(v):n for n,v in re.findall(r'^\s*([A-Za-z_]\w*)\s*=\s*(\d+)\s*,?',m.group(1),re.M)}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--externs',type=Path,required=True); ap.add_argument('--membership-manifest',type=Path,required=True); ap.add_argument('-o','--out',type=Path,required=True); a=ap.parse_args()
    violations=[]; text=a.externs.read_text(encoding='utf-8-sig')
    if '//Based on CBuffer index' not in text: violations.append('cbuffer_index_declaration_missing')
    try: scope=parse(text)
    except Exception as e: scope={}; violations.append(f'parse:{e}')
    if scope!=EXPECTED: violations.append(f'tfxscope_mapping_drift:{scope!r}')
    m=json.loads(a.membership_manifest.read_text())
    if m.get('schema')!='d1_localshader_api10_membership_provenance/v1' or m.get('status')!='SOURCE_CLOSED_EXACT': violations.append('api10_membership_manifest_not_exact')
    if m.get('exact_denominators',{}).get('program_count')!=39: violations.append('api10_program_denominator_drift')
    boundary=m.get('semantic_boundary',{})
    for k in ('runtime_writer','backing_allocation','engine_semantic'):
        if boundary.get(k)!='WITHHELD': violations.append(f'api10_boundary_weakened:{k}')
    if 10 in scope: violations.append(f'api10_unexpected_tfxscope_name:{scope[10]}')
    exact=not violations
    out={'schema':'d1_ps4_api10_tfxscope_exclusion_proof/v1','status':'D1_PS4_API10_TFXSCOPE_NAME_EXCLUDED_EXACT' if exact else 'D1_PS4_API10_TFXSCOPE_EXCLUSION_VIOLATIONS','source':{'repository':'MontagueM/Charm','commit':CHARM_COMMIT,'blob_sha1':CHARM_BLOB,'path':'Tiger/Schema/Shaders/TFX Bytecode/Externs.cs','declaration':'TfxScope : byte // Based on CBuffer index','mapping':{str(k):v for k,v in sorted(scope.items())}},'api10':{'present_in_tfxscope':10 in scope,'source_scope_name':scope.get(10),'source_scope_name_status':'WITHHELD_NO_TFXSCOPE_INDEX_10','exact_program_membership_count':m.get('exact_denominators',{}).get('program_count'),'runtime_writer':'WITHHELD','backing_allocation':'WITHHELD','engine_semantic':'WITHHELD'},'violations':violations,'policy':'Absence of CBuffer index 10 from the pinned TfxScope enum excludes deriving an API10 scope name from this source. It does not prove that API10 lacks a runtime scope, writer, allocation, or semantic.'}
    a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2)); return 0 if exact else 2
if __name__=='__main__': raise SystemExit(main())
