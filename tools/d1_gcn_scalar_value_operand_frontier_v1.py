#!/usr/bin/env python3
"""Exact operand/source-domain frontier for source-backed D1 GFX7 scalar result values."""
from __future__ import annotations
import argparse, collections, json, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import d1_gcn_scalar_value_semantics_v1 as sem
import d1_gcn_shader_corpus_structural_census as census

SCHEMA = "d1_gcn_scalar_value_operand_frontier/v1"
STATUS = "D1_GCN_SCALAR_VALUE_OPERAND_FRONTIER_EXACT"
EXPECTED_PROGRAMS = 26464
EXPECTED_INSTRUCTIONS = 4896165
SREG = re.compile(r"^s(\d+)$")


def is_scalar_def(r: str) -> bool:
    return bool(SREG.fullmatch(r or "")) or r == "m0"


def expected_width(op: str) -> int | None:
    if op in sem.COMPARE_MASK_DEST: return 2
    if op in {"s_and_saveexec_b64","s_swappc_b64","s_and_b64","s_andn2_b64","s_mov_b64","s_or_b64","s_xor_b64"}: return 2
    if op == "s_buffer_load_dwordx2": return 2
    if op in {"s_buffer_load_dwordx4","s_load_dwordx4"}: return 4
    if op == "s_load_dwordx8": return 8
    if op in {"s_buffer_load_dword","s_addk_i32","s_and_b32","s_lshl_b32","s_mov_b32","s_movk_i32","v_readfirstlane_b32","v_readlane_b32"}: return 1
    return None


def build(ir_dir: Path) -> dict:
    violations=[]
    paths=sorted(ir_dir.glob('*.json'))
    if len(paths)!=EXPECTED_PROGRAMS: violations.append(f"ir_file_count:{len(paths)}!={EXPECTED_PROGRAMS}")
    total_ins=0
    op_counts=collections.Counter(); entry_counts=collections.Counter(); category_counts=collections.Counter(); category_entries=collections.Counter()
    operand_forms=collections.defaultdict(collections.Counter); use_kind_forms=collections.defaultdict(collections.Counter)
    special_use_counts=collections.Counter(); special_use_opcodes=collections.Counter(); examples={}
    program_category=collections.defaultdict(set)
    unresolved=[]
    for p in paths:
        sha=p.stem.lower(); d=json.loads(p.read_text())
        if d.get('status')!='D1_GCN_STRUCTURAL_IR_COMPLETE': violations.append(f"ir_status:{sha}:{d.get('status')!r}")
        if (d.get('parse_accounting') or {}).get('status')!='D1_GCN_STRUCTURAL_PARSE_ACCOUNTING_EXACT': violations.append(f"parse_status:{sha}")
        ins=d.get('instructions') or []; total_ins += len(ins)
        for x in ins:
            sd=[r for r in (x.get('defs') or []) if is_scalar_def(r)]
            if not sd: continue
            op=x['opcode']; op_counts[op]+=1; entry_counts[op]+=len(sd)
            if op not in sem.OBSERVED:
                unresolved.append({'gcn_sha256':sha,'instruction':x['index'],'opcode':op,'problem':'UNREGISTERED_SGPR_DEF_OPCODE'})
                continue
            beh=sem.behavior(op); cat=beh['category']; category_counts[cat]+=1; category_entries[cat]+=len(sd); program_category[cat].add(sha)
            ew=expected_width(op)
            if ew is None or len(sd)!=ew:
                violations.append(f"def_width:{sha}:{x['index']}:{op}:{len(sd)}!={ew}")
            operands=tuple(census.normalized_operand(z) for z in (x.get('operands') or []))
            operand_forms[op][operands]+=1
            kinds=tuple(census.reg_kind(z) for z in (x.get('uses') or []))
            use_kind_forms[op][kinds]+=1
            special=tuple(k for k in kinds if k in {'EXEC','VCC','SCC','VGPR','M0'})
            if special:
                special_use_counts[special]+=1; special_use_opcodes[op]+=1
            examples.setdefault((op,operands,kinds),{
                'gcn_sha256':sha,'instruction':x['index'],'address':x['address_hex'],'opcode':op,
                'operands':x.get('operands') or [],'defs':sd,'uses':x.get('uses') or [],
                'normalized_operands':list(operands),'use_kinds':list(kinds),'category':cat,
            })
    if total_ins!=EXPECTED_INSTRUCTIONS: violations.append(f"instruction_count:{total_ins}!={EXPECTED_INSTRUCTIONS}")
    if set(op_counts)!=sem.OBSERVED: violations.append(f"opcode_surface:{sorted(op_counts)}!={sorted(sem.OBSERVED)}")
    if len(op_counts)!=31: violations.append(f"opcode_count:{len(op_counts)}!=31")
    if unresolved:
        violations.extend(f"unresolved:{r['gcn_sha256']}:{r['instruction']}:{r['opcode']}:{r['problem']}" for r in unresolved[:50])
    def encode_forms(src):
        return {op:[{'signature':list(sig),'count':n} for sig,n in sorted(c.items(), key=lambda kv:str(kv[0]))] for op,c in sorted(src.items())}
    coverage={
        'exact_program_count':len(paths),'exact_instruction_count':total_ins,
        'sgpr_def_instruction_count':sum(op_counts.values()),'sgpr_def_entry_count':sum(entry_counts.values()),
        'sgpr_def_opcode_count':len(op_counts),'opcode_instruction_counts':dict(sorted(op_counts.items())),
        'opcode_def_entry_counts':dict(sorted(entry_counts.items())),
        'category_instruction_counts':dict(sorted(category_counts.items())),
        'category_def_entry_counts':dict(sorted(category_entries.items())),
        'category_program_counts':{k:len(v) for k,v in sorted(program_category.items())},
        'operand_form_count':sum(len(v) for v in operand_forms.values()),
        'use_kind_form_count':sum(len(v) for v in use_kind_forms.values()),
        'instructions_with_special_structural_use_kinds':sum(special_use_counts.values()),
        'special_structural_use_signature_counts':{'|'.join(k):v for k,v in sorted(special_use_counts.items(), key=lambda kv:str(kv[0]))},
        'special_structural_use_opcode_counts':dict(sorted(special_use_opcodes.items())),
        'architectural_value_semantic_opcode_count':len(sem.OBSERVED-sem.MEMORY_OPAQUE),
        'opaque_memory_value_opcode_count':len(sem.MEMORY_OPAQUE),
        'shader_expression_semantic_promotions':0,
    }
    return {
        'schema':SCHEMA,'status':STATUS if not violations else 'D1_GCN_SCALAR_VALUE_OPERAND_FRONTIER_WITH_VIOLATIONS',
        'source_registry':sem.document(),'coverage':coverage,
        'operand_forms_by_opcode':encode_forms(operand_forms),'structural_use_kinds_by_opcode':encode_forms(use_kind_forms),
        'examples':[v for _,v in sorted(examples.items(), key=lambda kv:str(kv[0]))],
        'unresolved':unresolved,'violations':violations,
        'semantic_boundary':{
            'physical_sgpr_m0_ssa':'GLOBAL_EXACT_PREREQUISITE',
            'nonmemory_architectural_value_rules':'SOURCE_CLOSED_OPCODE_LEVEL',
            'actual_operand_source_domains':'GLOBAL_EXACT',
            'cross_domain_value_graph':'NEXT_GATE' if not violations else 'WITHHELD',
            'scalar_memory_load_values':'OPAQUE_RESOURCE_ADDRESS_BOUNDARY',
            'shader_expression_semantics':'WITHHELD','shader_expression_semantic_promotions':0,
        },
        'policy':'Every exact scalar-def instruction is assigned to a source-backed machine-value category and its normalized operand/source-domain form is censused. This does not yet splice EXEC/VGPR/condition nodes into scalar SSA and does not interpret scalar-memory resource contents or shader/material intent.'
    }

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--ir-dir',type=Path,required=True); ap.add_argument('-o','--output',type=Path,required=True); a=ap.parse_args()
    out=build(a.ir_dir); a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':out['status'],'coverage':out['coverage'],'violations':out['violations'][:20]},indent=2,sort_keys=True)); return 0 if not out['violations'] else 2
if __name__=='__main__': raise SystemExit(main())
