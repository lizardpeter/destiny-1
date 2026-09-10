#!/usr/bin/env python3
"""Replay exact source-closed candidate GCN programs through the universal VGPR lane SSA.

Candidate/stage provenance never changes the analyzer. The denominator is derived from
the exact structural source-closure report instead of hardcoding the global PS/VS/DS
corpus. Each emitted Structural IR is revalidated by the unchanged lane-aware analyzer
and the complete lane-SSA result is optionally frozen per exact GCN SHA-256.
"""
from __future__ import annotations
import argparse, collections, json, sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import d1_gcn_vgpr_lane_ssa_v1 as lane

STRUCT_SCHEMA='d1_gcn_source_closed_structural_promotion/v1'
STRUCT_STATUS='D1_GCN_SOURCE_CLOSED_STRUCTURAL_PROMOTION_EXACT'
RAW_SCHEMA='d1_gcn_structural_candidate_compare/v1'
IR_STATUS='D1_GCN_STRUCTURAL_IR_COMPLETE'
LANE_STATUS='D1_GCN_VGPR_LANE_SSA_EXACT'
SCHEMA='d1_gcn_candidate_vgpr_lane_ssa_replay/v1'
STATUS='D1_GCN_CANDIDATE_VGPR_LANE_SSA_REPLAY_EXACT'


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--structural-source-closure',type=Path,required=True)
    ap.add_argument('--raw-replay',type=Path,required=True)
    ap.add_argument('--ir-dir',type=Path,required=True)
    ap.add_argument('--lane-dir',type=Path)
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args()

    sc=json.loads(a.structural_source_closure.read_text())
    if sc.get('schema')!=STRUCT_SCHEMA or sc.get('status')!=STRUCT_STATUS or sc.get('violations'):
        raise SystemExit('zero-violation source-closed structural promotion required')
    raw=json.loads(a.raw_replay.read_text())
    if raw.get('schema')!=RAW_SCHEMA:
        raise SystemExit(f'unsupported raw replay schema:{raw.get("schema")!r}')

    sc_rows={str(x.get('gcn_sha256','')).lower():x for x in sc.get('programs') or []}
    raw_rows={str(x.get('gcn_sha256','')).lower():x for x in raw.get('programs') or []}
    planned=int((sc.get('coverage') or {}).get('architecture_admitted_unique_gcn_programs',-1))
    violations=[]
    if planned!=len(sc_rows): violations.append(f'structural_roster_count:{len(sc_rows)}!={planned}')
    if set(sc_rows)!=set(raw_rows): violations.append('raw_structural_sha_roster_mismatch')
    for sha,r in sc_rows.items():
        if r.get('parse_violations'): violations.append(f'{sha}:structural_parse_violations:{r["parse_violations"][:3]}')
        if r.get('architecture_violations'): violations.append(f'{sha}:structural_architecture_violations:{r["architecture_violations"][:3]}')

    if a.lane_dir: a.lane_dir.mkdir(parents=True,exist_ok=True)
    totals=collections.Counter(); stage_counts=collections.Counter(); write_ops=collections.Counter(); write_entries=collections.Counter()
    rows=[]; exact=0; max_index=-1
    for sha in sorted(sc_rows):
        rr=raw_rows[sha]; stages=sorted({str(x).upper() for x in (rr.get('stages') or [])})
        for st in stages: stage_counts[st]+=1
        rec={'gcn_sha256':sha,'stages':stages,'violations':[]}
        ip=a.ir_dir/f'{sha}.json'
        if not ip.is_file(): rec['violations'].append('structural_ir_missing')
        else:
            try: ir=json.loads(ip.read_text())
            except Exception as e:
                rec['violations'].append(f'structural_ir_json:{type(e).__name__}:{e}'); ir=None
            if ir is not None:
                if ir.get('status')!=IR_STATUS: rec['violations'].append(f'structural_ir_status:{ir.get("status")!r}')
                try: d=lane.analyze(ir)
                except Exception as e:
                    rec['violations'].append(f'lane_analyze:{type(e).__name__}:{e}'); d=None
                if d is not None:
                    if d.get('status')!=LANE_STATUS or d.get('violations'):
                        rec['violations'].append(f'lane_status:{d.get("status")!r}:{(d.get("violations") or [])[:5]}')
                    if int(d.get('instruction_count',-1))!=int(ir.get('instruction_count',-2)):
                        rec['violations'].append(f'instruction_count:{d.get("instruction_count")}!={ir.get("instruction_count")}')
                    c=d.get('coverage') or {}
                    if int(c.get('shader_expression_semantic_promotions',-1))!=0:
                        rec['violations'].append(f'semantic_promotions:{c.get("shader_expression_semantic_promotions")}')
                    if a.lane_dir:
                        (a.lane_dir/f'{sha}.json').write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
                    if not rec['violations']:
                        exact+=1
                        totals['instructions']+=int(d.get('instruction_count',0))
                        totals['blocks']+=int(d.get('basic_block_count',0))
                        totals['edges']+=int(d.get('concrete_cfg_edge_count',0))
                        totals['nodes']+=int(d.get('node_count',0))
                        for k in ('tracked_vgpr_count','entry_node_count','cfg_phi_node_count','unresolved_control_entry_block_count','unresolved_control_entry_vgpr_node_count','non_vgpr_source_leaf_count','vgpr_def_instruction_count','vgpr_def_entry_count','vgpr_use_instruction_count','vgpr_use_entry_count','exec_gated_write_node_count','single_lane_write_node_count','vgpr_result_component_node_count','dynamic_vgpr_read_boundary_count','shader_expression_semantic_promotions'):
                            totals[k]+=int(c.get(k,0))
                        max_index=max(max_index,int(c.get('max_tracked_vgpr_index',-1)))
                        write_ops.update(c.get('opcode_write_instruction_counts') or {})
                        write_entries.update(c.get('opcode_write_entry_counts') or {})
                        rec.update({'tracked_vgpr_count':c.get('tracked_vgpr_count'),'max_tracked_vgpr_index':c.get('max_tracked_vgpr_index'),'node_count':d.get('node_count'),'vgpr_def_entry_count':c.get('vgpr_def_entry_count'),'vgpr_use_entry_count':c.get('vgpr_use_entry_count')})
        if rec['violations']: violations.extend(f'{sha}:{x}' for x in rec['violations'])
        rows.append(rec)

    sc_cov=sc.get('coverage') or {}
    if totals['instructions']!=int(sc_cov.get('instruction_count',-1)):
        violations.append(f'instruction_reconciliation:{totals["instructions"]}!={sc_cov.get("instruction_count")}')
    if exact!=planned: violations.append(f'exact_programs:{exact}!={planned}')
    if totals['exec_gated_write_node_count']+totals['single_lane_write_node_count']!=totals['vgpr_def_entry_count']:
        violations.append('write_partition_mismatch')
    if totals['vgpr_result_component_node_count']!=totals['vgpr_def_entry_count']:
        violations.append('result_component_count_mismatch')
    if totals['shader_expression_semantic_promotions']!=0:
        violations.append(f'aggregate_semantic_promotions:{totals["shader_expression_semantic_promotions"]}')

    coverage={
      'planned_unique_gcn_programs':planned,'exact_lane_ssa_unique_gcn_programs':exact,
      'stage_program_counts':dict(sorted(stage_counts.items())),'exact_instructions_replayed':totals['instructions'],
      'effect_aware_basic_block_count':totals['blocks'],'concrete_cfg_edge_count':totals['edges'],
      'vgpr_ssa_node_count':totals['nodes'],'tracked_vgpr_instances':totals['tracked_vgpr_count'],
      'max_vgpr_index':max_index,'program_entry_vgpr_node_count':totals['entry_node_count'],
      'vgpr_cfg_phi_node_count':totals['cfg_phi_node_count'],
      'unresolved_control_entry_block_count':totals['unresolved_control_entry_block_count'],
      'unresolved_control_entry_vgpr_node_count':totals['unresolved_control_entry_vgpr_node_count'],
      'non_vgpr_source_leaf_count':totals['non_vgpr_source_leaf_count'],
      'vgpr_def_instruction_count':totals['vgpr_def_instruction_count'],'vgpr_def_entry_count':totals['vgpr_def_entry_count'],
      'vgpr_use_instruction_count':totals['vgpr_use_instruction_count'],'vgpr_use_entry_count':totals['vgpr_use_entry_count'],
      'exec_gated_write_node_count':totals['exec_gated_write_node_count'],'single_lane_write_node_count':totals['single_lane_write_node_count'],
      'vgpr_result_component_node_count':totals['vgpr_result_component_node_count'],'dynamic_vgpr_read_boundary_count':totals['dynamic_vgpr_read_boundary_count'],
      'opcode_write_instruction_counts':dict(sorted(write_ops.items())),'opcode_write_entry_counts':dict(sorted(write_entries.items())),
      'shader_expression_semantic_promotions':totals['shader_expression_semantic_promotions'],
    }
    out={
      'schema':SCHEMA,'status':STATUS if not violations else 'D1_GCN_CANDIDATE_VGPR_LANE_SSA_REPLAY_WITH_VIOLATIONS',
      'sources':{'structural_source_closure':str(a.structural_source_closure),'raw_replay':str(a.raw_replay),'ir_dir':str(a.ir_dir)},
      'coverage':coverage,'programs':rows,'violations':violations,
      'semantic_boundary':{
        'candidate_stage_affects_lane_analyzer':False,'physical_vgpr_lane_ssa':'EXACT' if not violations else 'NOT_PROMOTED',
        'inactive_lane_preservation':'EXACT' if not violations else 'NOT_PROMOTED','non_vgpr_sources':'INSTRUCTION_LOCAL_SYMBOLIC_LEAVES',
        'ordinary_sgpr_value_ssa':'NEXT_GATE' if not violations else 'WITHHELD','opcode_result_value_semantics':'WITHHELD',
        'shader_expression_semantics':'WITHHELD','shader_expression_semantic_promotions':0,
      },
      'policy':'Every source-closed candidate program is replayed through the unchanged universal physical-VGPR lane SSA analyzer. Stage labels are provenance only. Vector destination state remains EXEC-gated except already-source-closed special machine behavior; scalar sources remain opaque use-site leaves and shader expression semantics remain withheld.'
    }
    a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print('STATUS',out['status'],'PROGRAMS',f'{exact}/{planned}','INSTRUCTIONS',totals['instructions'],'NODES',totals['nodes'],'VGPR_DEFS',totals['vgpr_def_entry_count'],'VGPR_USES',totals['vgpr_use_entry_count'],'VIOLATIONS',len(violations))
    for x in violations[:100]: print('VIOLATION',x)
    return 0 if out['status']==STATUS else 2

if __name__=='__main__': raise SystemExit(main())
