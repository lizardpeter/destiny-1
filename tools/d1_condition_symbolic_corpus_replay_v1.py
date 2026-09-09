#!/usr/bin/env python3
"""Replay exact condition-mask/SCC symbolic dataflow across every D1 shader program."""
from __future__ import annotations
import argparse, collections, json, multiprocessing as mp, os
from pathlib import Path
import d1_condition_symbolic_dataflow_v1 as sym

CENSUS_STATUS='D1_GCN_SHADER_CORPUS_STRUCTURAL_CENSUS_COMPLETE'
FRONTIER_STATUS='D1_GCN_CONDITION_MACHINE_FRONTIER_EXACT'
SCHEMA='d1_gcn_condition_symbolic_corpus_replay/v1'
STATUS='D1_GCN_CONDITION_SYMBOLIC_CORPUS_REPLAY_EXACT'
EXPECTED_PROGRAMS=26464; EXPECTED_INSTRUCTIONS=4896165; EXPECTED_BLOCKS=68622; EXPECTED_EDGES=51073
EXPECTED_STAGE={'DS':20,'PS':18375,'VS':8069}

def worker(path):
    p=Path(path); sha=p.stem.lower()
    try:
        d=sym.analyze(json.loads(p.read_text()))
        return {'sha':sha,'ok':not d['violations'],'violations':d['violations'][:5],
            'instructions':d['instruction_count'],'blocks':d['basic_block_count'],'edges':d['concrete_cfg_edge_count'],
            'nodes':d['node_count'],'phis':d['phi_node_count'],'orphan':d['unresolved_control_entry_block_count'],
            'tracked_pairs':len(d['tracked_sgpr_pairs']),'compare_defs':d.get('compare_mask_definition_count',0),
            'carry_defs':d.get('carry_mask_definition_count',0),'scalar_mask_defs':d.get('scalar_mask_definition_count',0),
            'half_writes':d.get('mask_half_write_count',0),'opaque_halves':d.get('opaque_mask_half_write_count',0),
            'opaque_vcc':d.get('opaque_whole_vcc_write_count',0),'cnd_uses':d.get('cndmask_mask_use_count',0),
            'vcc_branches':d.get('vcc_branch_mask_use_count',0),'scc_defs':d.get('scc_definition_count',0),
            'scc_branches':d.get('scc_branch_use_count',0),'mask_ops':d['mask_machine_opcode_counts'],
            'scc_ops':d['scc_machine_opcode_counts']}
    except Exception as e:
        return {'sha':sha,'ok':False,'exception':f'{type(e).__name__}:{e}'}

def replay(ir_dir,census_path,frontier_path,workers):
    violations=[]; cen=json.loads(census_path.read_text()); fr=json.loads(frontier_path.read_text())
    if cen.get('status')!=CENSUS_STATUS: violations.append(f'census_status:{cen.get("status")}')
    if fr.get('status')!=FRONTIER_STATUS: violations.append(f'frontier_status:{fr.get("status")}')
    stages={p['gcn_sha256']:(p.get('stages') or []) for p in cen.get('programs') or []}
    if len(stages)!=EXPECTED_PROGRAMS: violations.append(f'stage_map:{len(stages)}')
    paths=sorted(ir_dir.glob('*.json')); tot=collections.Counter(); stagec=collections.Counter(); maskops=collections.Counter(); sccops=collections.Counter(); rows=[]
    if len(paths)!=EXPECTED_PROGRAMS: violations.append(f'ir_file_count:{len(paths)}!={EXPECTED_PROGRAMS}')
    pool=None; it=map(worker,map(str,paths))
    if workers>1:
        pool=mp.Pool(workers); it=pool.imap_unordered(worker,map(str,paths),chunksize=16)
    try:
        for r in it:
            sha=r['sha']; st=stages.get(sha)
            if not st or len(st)!=1: violations.append(f'stage:{sha}:{st}'); continue
            stage=st[0]; stagec[stage]+=1
            if not r.get('ok'): violations.append(f'analyze:{sha}:{r.get("exception") or r.get("violations")}'); continue
            for k in ('instructions','blocks','edges','nodes','phis','orphan','tracked_pairs','compare_defs','carry_defs','scalar_mask_defs','half_writes','opaque_halves','opaque_vcc','cnd_uses','vcc_branches','scc_defs','scc_branches'): tot[k]+=r[k]
            maskops.update(r['mask_ops']); sccops.update(r['scc_ops'])
            rows.append({'gcn_sha256':sha,'stage':stage,'tracked_sgpr_pair_count':r['tracked_pairs'],
                'compare_mask_definition_count':r['compare_defs'],'cndmask_mask_use_count':r['cnd_uses'],
                'scc_definition_count':r['scc_defs'],'scc_branch_use_count':r['scc_branches'],
                'node_count':r['nodes'],'phi_node_count':r['phis']})
    finally:
        if pool: pool.close(); pool.join()
    rows.sort(key=lambda x:x['gcn_sha256'])
    for k,w in [('programs',EXPECTED_PROGRAMS),('instructions',EXPECTED_INSTRUCTIONS),('blocks',EXPECTED_BLOCKS),('edges',EXPECTED_EDGES)]:
        got=len(rows) if k=='programs' else tot[k]
        if got!=w: violations.append(f'{k}:{got}!={w}')
    if dict(sorted(stagec.items()))!=EXPECTED_STAGE: violations.append(f'stage_counts:{dict(stagec)}')
    fc=fr['coverage']
    for sk,fk in [('compare_defs','compare_instruction_count'),('carry_defs','carry_instruction_count'),('cnd_uses','cndmask_instruction_count'),('vcc_branches','vcc_branch_consumer_count'),('scc_defs','scc_producer_instruction_count'),('scc_branches','scc_branch_consumer_count')]:
        if tot[sk]!=fc[fk]: violations.append(f'frontier_{sk}:{tot[sk]}!={fc[fk]}')
    return {'schema':SCHEMA,'status':STATUS if not violations else 'D1_GCN_CONDITION_SYMBOLIC_CORPUS_REPLAY_WITH_VIOLATIONS',
        'sources':{'ir_dir':str(ir_dir),'structural_census':str(census_path),'condition_frontier':str(frontier_path)},
        'coverage':{'exact_programs_replayed':len(rows),'stage_program_counts':dict(sorted(stagec.items())),
            'exact_instructions_replayed':tot['instructions'],'effect_aware_basic_block_count':tot['blocks'],'concrete_cfg_edge_count':tot['edges'],
            'condition_symbolic_node_count':tot['nodes'],'condition_cfg_phi_node_count':tot['phis'],'unresolved_control_entry_block_count':tot['orphan'],
            'tracked_sgpr_pair_instances':tot['tracked_pairs'],'compare_mask_definition_count':tot['compare_defs'],
            'carry_mask_definition_count':tot['carry_defs'],'scalar_mask_definition_count':tot['scalar_mask_defs'],
            'mask_half_write_count':tot['half_writes'],'opaque_mask_half_write_count':tot['opaque_halves'],'opaque_whole_vcc_write_count':tot['opaque_vcc'],
            'cndmask_mask_use_count':tot['cnd_uses'],'vcc_branch_mask_use_count':tot['vcc_branches'],
            'scc_definition_count':tot['scc_defs'],'scc_branch_use_count':tot['scc_branches'],
            'mask_machine_opcode_counts':dict(sorted(maskops.items())),'scc_machine_opcode_counts':dict(sorted(sccops.items())),
            'shader_expression_semantic_promotions':0},
        'programs':rows,'violations':violations,
        'semantic_boundary':{'exec_symbolic_dataflow':'GLOBAL_EXACT_PREREQUISITE','condition_mask_symbolic_dataflow':'GLOBAL_EXACT',
            'scc_symbolic_dataflow':'GLOBAL_EXACT','branch_feasibility':'WITHHELD','lane_aware_vgpr_ssa':'NEXT_GATE',
            'shader_expression_semantics':'WITHHELD','shader_expression_semantic_promotions':0},
        'policy':'All exact programs are replayed with general SGPR-pair/VCC predicate SSA and source-closed SCC SSA. Compare/carry lane-mask definitions merge under exact EXEC provenance. Unknown mask carrier writes remain explicit opaque boundaries. No branch feasibility or shader expression is promoted.'}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--ir-dir',type=Path,required=True); ap.add_argument('--structural-census',type=Path,required=True); ap.add_argument('--condition-frontier',type=Path,required=True); ap.add_argument('-o','--output',type=Path,required=True); ap.add_argument('--workers',type=int,default=max(1,min(4,os.cpu_count() or 1))); a=ap.parse_args()
    o=replay(a.ir_dir,a.structural_census,a.condition_frontier,a.workers); a.output.write_text(json.dumps(o,indent=2,sort_keys=True)+'\n'); print(json.dumps({'status':o['status'],'coverage':o['coverage'],'violations':o['violations'][:20]},indent=2)); return 0 if not o['violations'] else 2
if __name__=='__main__': raise SystemExit(main())
