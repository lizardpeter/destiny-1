#!/usr/bin/env python3
"""Validate source-backed VALU base formulas against the frozen exact D1 vector frontier."""
from __future__ import annotations
import argparse, collections, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import d1_gcn_vector_formula_semantics_v1 as sem

SCHEMA='d1_gcn_vector_formula_frontier/v1'
STATUS='D1_GCN_VECTOR_BASE_FORMULA_FRONTIER_EXACT'
SOURCE_SCHEMA='d1_gcn_vector_value_operand_frontier/v1'
SOURCE_STATUS='D1_GCN_VECTOR_VALUE_OPERAND_FRONTIER_EXACT'
EXPECTED_FORMULA_INSTRUCTIONS=2_994_322
EXPECTED_FORMULA_COMPONENTS=2_994_369
EXPECTED_PROGRAMS=26_464
EXPECTED_TOTAL_INSTRUCTIONS=4_896_165
EXPECTED_VGPR_DEF_INSTRUCTIONS=3_690_362
EXPECTED_VGPR_DEF_COMPONENTS=3_864_039
EXPECTED_CLAMP_INSTRUCTIONS=129_395
EXPECTED_ABS_INSTRUCTIONS=47_624
EXPECTED_NEG_INSTRUCTIONS=158_330
EXPECTED_OMOD_INSTRUCTIONS=28_931
EXPECTED_ANY_MODIFIER_INSTRUCTIONS=313_444
EXPECTED_BIT_EXACT_INSTRUCTIONS=389_102
EXPECTED_BIT_EXACT_COMPONENTS=389_149

def has_neg(sig: list[str]) -> bool: return any(x.startswith('-') or ' -' in x for x in sig)
def has_abs(sig: list[str]) -> bool: return any('abs(' in x for x in sig)
def has_clamp(sig: list[str]) -> bool: return any('clamp' in x for x in sig)
def has_omod(sig: list[str]) -> bool: return any('mul:' in x or 'div:' in x for x in sig)

def build(frontier_path: Path) -> dict:
    src=json.loads(frontier_path.read_text());violations=[]
    if src.get('schema')!=SOURCE_SCHEMA: violations.append(f"source_schema:{src.get('schema')!r}")
    if src.get('status')!=SOURCE_STATUS: violations.append(f"source_status:{src.get('status')!r}")
    if src.get('violations'): violations.append(f"source_violations:{len(src.get('violations') or [])}")
    if sem.validate(): violations.extend('registry:'+x for x in sem.validate())
    cov=src.get('coverage') or {}
    checks={'exact_program_count':EXPECTED_PROGRAMS,'exact_instruction_count':EXPECTED_TOTAL_INSTRUCTIONS,'vgpr_def_instruction_count':EXPECTED_VGPR_DEF_INSTRUCTIONS,'vgpr_def_entry_count':EXPECTED_VGPR_DEF_COMPONENTS,'vgpr_def_opcode_count':74}
    for k,v in checks.items():
        if cov.get(k)!=v: violations.append(f"coverage:{k}:{cov.get(k)}!={v}")
    source_pending=set(((src.get('source_registry') or {}).get('categories') or {}).get('VALU_FORMULA_PENDING') or [])
    if source_pending!=sem.PENDING: violations.append(f"pending_surface:missing={sorted(sem.PENDING-source_pending)}:extra={sorted(source_pending-sem.PENDING)}")
    op_counts=cov.get('opcode_instruction_counts') or {};width_by_op=src.get('vgpr_result_widths_by_opcode') or {};forms=src.get('operand_forms_by_opcode') or {}
    result_components=0;formula_instructions=0;modifier_counts=collections.Counter();any_modifier=0
    op_modifier_counts=collections.defaultdict(collections.Counter);op_form_counts={};exact_replay_instructions=0;exact_replay_components=0
    formula_class_counts=collections.Counter();formula_class_instructions=collections.Counter();unresolved=[]
    for op in sorted(sem.PENDING):
        ent=sem.FORMULAS[op];n=op_counts.get(op)
        if not isinstance(n,int) or n<=0: violations.append(f"opcode_instruction_count:{op}:{n}");n=0
        formula_instructions+=n;formula_class_counts[ent['semantic_kind']]+=1;formula_class_instructions[ent['semantic_kind']]+=n
        widths=width_by_op.get(op);expected_width=ent['result_components']
        if widths!=[{'component_count':expected_width,'instruction_count':n}]: violations.append(f"result_width:{op}:{widths}!={expected_width}x{n}")
        result_components+=expected_width*n
        if op in sem.BIT_EXACT_REPLAY_READY: exact_replay_instructions+=n;exact_replay_components+=expected_width*n
        rows=forms.get(op)
        if not isinstance(rows,list) or not rows: violations.append(f"operand_forms_missing:{op}");continue
        form_total=0;expected_arity=1+ent['explicit_source_count']
        for r in rows:
            sig=r.get('signature') or [];c=r.get('count')
            if not isinstance(c,int) or c<=0: violations.append(f"bad_form_count:{op}:{c}");continue
            form_total+=c
            if len(sig)!=expected_arity: violations.append(f"operand_arity:{op}:{sig}:{len(sig)}!={expected_arity}")
            flags={'NEG':has_neg(sig),'ABS':has_abs(sig),'CLAMP':has_clamp(sig),'OMOD':has_omod(sig)}
            for k,on in flags.items():
                if on: modifier_counts[k]+=c;op_modifier_counts[op][k]+=c
            if any(flags.values()): any_modifier+=c
            if op in sem.BIT_EXACT_REPLAY_READY and any(flags.values()): unresolved.append({'opcode':op,'signature':sig,'count':c,'problem':'BIT_EXACT_READY_OPCODE_HAS_OBSERVED_FP_MODIFIER'})
        op_form_counts[op]=len(rows)
        if form_total!=n: violations.append(f"operand_form_total:{op}:{form_total}!={n}")
    if formula_instructions!=EXPECTED_FORMULA_INSTRUCTIONS: violations.append(f"formula_instructions:{formula_instructions}!={EXPECTED_FORMULA_INSTRUCTIONS}")
    if result_components!=EXPECTED_FORMULA_COMPONENTS: violations.append(f"formula_components:{result_components}!={EXPECTED_FORMULA_COMPONENTS}")
    if exact_replay_instructions!=EXPECTED_BIT_EXACT_INSTRUCTIONS: violations.append(f"bit_exact_instructions:{exact_replay_instructions}!={EXPECTED_BIT_EXACT_INSTRUCTIONS}")
    if exact_replay_components!=EXPECTED_BIT_EXACT_COMPONENTS: violations.append(f"bit_exact_components:{exact_replay_components}!={EXPECTED_BIT_EXACT_COMPONENTS}")
    expected_mod={'CLAMP':EXPECTED_CLAMP_INSTRUCTIONS,'ABS':EXPECTED_ABS_INSTRUCTIONS,'NEG':EXPECTED_NEG_INSTRUCTIONS,'OMOD':EXPECTED_OMOD_INSTRUCTIONS}
    for k,v in expected_mod.items():
        if modifier_counts[k]!=v: violations.append(f"modifier_count:{k}:{modifier_counts[k]}!={v}")
    if any_modifier!=EXPECTED_ANY_MODIFIER_INSTRUCTIONS: violations.append(f"any_modifier:{any_modifier}!={EXPECTED_ANY_MODIFIER_INSTRUCTIONS}")
    if unresolved: violations.extend(f"unresolved:{x['opcode']}:{x['problem']}" for x in unresolved[:50])
    modifier_opcodes={k:sum(1 for op,c in op_modifier_counts.items() if c[k]) for k in ['NEG','ABS','CLAMP','OMOD']}
    return {
        'schema':SCHEMA,'status':STATUS if not violations else 'D1_GCN_VECTOR_BASE_FORMULA_FRONTIER_WITH_VIOLATIONS',
        'source_vector_frontier':{'schema':src.get('schema'),'status':src.get('status'),'coverage_identity':{k:cov.get(k) for k in checks}},
        'formula_registry':sem.document(),
        'coverage':{
            'exact_program_count':cov.get('exact_program_count'),'exact_instruction_count':cov.get('exact_instruction_count'),
            'formula_opcode_count':len(sem.PENDING),'formula_instruction_count':formula_instructions,'formula_result_component_count':result_components,
            'source_documented_base_formula_opcode_count':len(sem.FORMULAS),'source_documented_base_formula_instruction_count':formula_instructions,
            'bit_exact_replay_ready_opcode_count':len(sem.BIT_EXACT_REPLAY_READY),'bit_exact_replay_ready_instruction_count':exact_replay_instructions,
            'bit_exact_replay_ready_result_component_count':exact_replay_components,
            'floating_or_special_symbolic_opcode_count':len(sem.PENDING-sem.BIT_EXACT_REPLAY_READY),'floating_or_special_symbolic_instruction_count':formula_instructions-exact_replay_instructions,
            'operand_form_count':sum(op_form_counts.values()),'modifier_touched_instruction_count':any_modifier,
            'neg_modifier_instruction_count':modifier_counts['NEG'],'abs_modifier_instruction_count':modifier_counts['ABS'],'omod_modifier_instruction_count':modifier_counts['OMOD'],
            'clamp_modifier_instruction_count':modifier_counts['CLAMP'],'clamp_numeric_semantics_withheld_instruction_count':modifier_counts['CLAMP'],
            'modifier_opcode_counts':modifier_opcodes,'semantic_kind_opcode_counts':dict(sorted(formula_class_counts.items())),'semantic_kind_instruction_counts':dict(sorted(formula_class_instructions.items())),
            'shader_expression_semantic_promotions':0,
        },
        'modifier_instruction_counts_by_opcode':{op:dict(sorted(c.items())) for op,c in sorted(op_modifier_counts.items())},
        'operand_form_counts_by_opcode':dict(sorted(op_form_counts.items())),'unresolved':unresolved,'violations':violations,
        'semantic_boundary':{
            'all_50_base_opcode_formulas':'SOURCE_CLOSED_SYMBOLIC','integer_bit_exact_subset':'READY_FOR_LANE_SSA_VALUE_NODE_REPLAY',
            'floating_numeric_replay':'WITHHELD_MODE_AND_OPCODE_SPECIFIC_HARDWARE_BEHAVIOR','vop3_abs_neg_order':'SOURCE_CLOSED','vop3_omod':'SOURCE_CLOSED',
            'vop3_clamp_numeric_range':'WITHHELD_AMD_REV1_3_INTERNAL_SOURCE_CONFLICT','clamp_affected_exact_instruction_count':modifier_counts['CLAMP'],
            'resource_lds_interpolation_values':'UNCHANGED_OPAQUE_BOUNDARIES','shader_expression_semantics':'WITHHELD','shader_expression_semantic_promotions':0,
            'next_gate':'EMIT_SOURCE_BACKED_BASE_VALUE_NODES_INTO_LANE_AWARE_VGPR_SSA_WITH_MODIFIER_AND_MODE_NODES_PRESERVED',
        },
        'policy':'The exact retail VALU surface is now source-closed at base-op formula identity. No CLAMP range is guessed across the AMD source conflict, no FP special function is replaced by a host math primitive, and no shader/material meaning is promoted.'
    }

def main() -> int:
    ap=argparse.ArgumentParser();ap.add_argument('--vector-frontier',type=Path,required=True);ap.add_argument('-o','--output',type=Path,required=True);a=ap.parse_args()
    out=build(a.vector_frontier);a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':out['status'],'coverage':out['coverage'],'violations':out['violations'][:20]},indent=2,sort_keys=True));return 0 if not out['violations'] else 2
if __name__=='__main__': raise SystemExit(main())
