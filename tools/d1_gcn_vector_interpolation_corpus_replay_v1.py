#!/usr/bin/env python3
"""Replay source-closed GFX7 VINTRP overlays across the exact Destiny 1 shader corpus."""
from __future__ import annotations
import argparse, collections, json, multiprocessing as mp, os
from pathlib import Path
import d1_gcn_vector_interpolation_overlay_v1 as overlay

CENSUS_STATUS="D1_GCN_SHADER_CORPUS_STRUCTURAL_CENSUS_COMPLETE"
OVERLAY_STATUS="D1_GCN_VECTOR_INTERPOLATION_OVERLAY_EXACT"
SCHEMA="d1_gcn_vector_interpolation_corpus_replay/v1"
STATUS="D1_GCN_VECTOR_INTERPOLATION_CORPUS_EXACT"
EXPECTED_PROGRAMS=26464
EXPECTED_INSTRUCTIONS=4896165
EXPECTED_STAGE={"DS":20,"PS":18375,"VS":8069}
EXPECTED_INTERP_PROGRAMS=17868
EXPECTED_INTERP_INSTRUCTIONS=425370
EXPECTED_OPS={"v_interp_mov_f32":6,"v_interp_p1_f32":212682,"v_interp_p2_f32":212682}
EXPECTED_PARAM_NODES=638052
EXPECTED_VGPR_REFS=425364
EXPECTED_OLD_DEST=212682


def worker(path:str)->dict:
    p=Path(path);sha=p.stem.lower()
    try:
        d=overlay.analyze(json.loads(p.read_text()));c=d.get("coverage") or {}
        return {"sha":sha,"ok":d.get("status")==OVERLAY_STATUS and not d.get("violations"),
                "status":d.get("status"),"violations":(d.get("violations") or [])[:8],
                "instructions":d.get("instruction_count",0),"interp":c.get("interpolation_instruction_count",0),
                "components":c.get("interpolation_result_component_count",0),"params":c.get("parameter_value_identity_node_count",0),
                "m0":c.get("m0_state_reference_count",0),"vgpr":c.get("vgpr_source_state_reference_count",0),
                "old":c.get("old_destination_arithmetic_input_count",0),"mov":c.get("parameter_move_instruction_count",0),
                "nodes":c.get("overlay_node_count",0),"ops":c.get("opcode_instruction_counts") or {},
                "attrs":c.get("attribute_instruction_counts") or {},"channels":c.get("channel_instruction_counts") or {},
                "promotions":c.get("shader_expression_semantic_promotions",0)}
    except Exception as e:return {"sha":sha,"ok":False,"exception":f"{type(e).__name__}:{e}"}


def replay(ir_dir:Path,census_path:Path,workers:int)->dict:
    violations=[];census=json.loads(census_path.read_text())
    if census.get("status")!=CENSUS_STATUS:violations.append(f"census_status:{census.get('status')!r}")
    stages={p["gcn_sha256"]:(p.get("stages") or []) for p in census.get("programs") or []}
    paths=sorted(ir_dir.glob("*.json"))
    if len(paths)!=EXPECTED_PROGRAMS:violations.append(f"ir_file_count:{len(paths)}!={EXPECTED_PROGRAMS}")
    totals=collections.Counter();stage_counts=collections.Counter();ops=collections.Counter();attrs=collections.Counter();channels=collections.Counter();rows=[];interp_programs=0
    pool=None;it=map(worker,map(str,paths))
    if workers>1:pool=mp.Pool(workers);it=pool.imap_unordered(worker,map(str,paths),chunksize=8)
    try:
        for r in it:
            sha=r["sha"];st=stages.get(sha)
            if not st or len(st)!=1:violations.append(f"stage:{sha}:{st}");continue
            stage=st[0];stage_counts[stage]+=1
            if not r.get("ok"):violations.append(f"analyze:{sha}:{r.get('exception') or (r.get('status'),r.get('violations'))}");continue
            for k in ("instructions","interp","components","params","m0","vgpr","old","mov","nodes","promotions"):totals[k]+=r[k]
            ops.update(r["ops"]);attrs.update({int(k):v for k,v in r["attrs"].items()});channels.update(r["channels"])
            if r["interp"]:
                interp_programs+=1
                if stage!="PS":violations.append(f"non_ps_interpolation:{sha}:{stage}:{r['interp']}")
                rows.append({"gcn_sha256":sha,"stage":stage,"interpolation_instruction_count":r["interp"],"overlay_node_count":r["nodes"]})
    finally:
        if pool:pool.close();pool.join()
    rows.sort(key=lambda x:x["gcn_sha256"])
    checks={"programs":len(paths),"instructions":totals["instructions"],"interp_programs":interp_programs,"interp":totals["interp"],"components":totals["components"],"params":totals["params"],"m0":totals["m0"],"vgpr":totals["vgpr"],"old":totals["old"],"mov":totals["mov"]}
    expected={"programs":EXPECTED_PROGRAMS,"instructions":EXPECTED_INSTRUCTIONS,"interp_programs":EXPECTED_INTERP_PROGRAMS,"interp":EXPECTED_INTERP_INSTRUCTIONS,"components":EXPECTED_INTERP_INSTRUCTIONS,"params":EXPECTED_PARAM_NODES,"m0":EXPECTED_INTERP_INSTRUCTIONS,"vgpr":EXPECTED_VGPR_REFS,"old":EXPECTED_OLD_DEST,"mov":6}
    for k,v in expected.items():
        if checks[k]!=v:violations.append(f"{k}:{checks[k]}!={v}")
    if dict(sorted(stage_counts.items()))!=EXPECTED_STAGE:violations.append(f"stage_counts:{dict(stage_counts)}!={EXPECTED_STAGE}")
    if dict(sorted(ops.items()))!=EXPECTED_OPS:violations.append(f"opcode_counts:{dict(ops)}!={EXPECTED_OPS}")
    if totals["promotions"]!=0:violations.append(f"shader_expression_semantic_promotions:{totals['promotions']}")
    coverage={"exact_programs_replayed":EXPECTED_PROGRAMS,"stage_program_counts":dict(sorted(stage_counts.items())),"exact_instructions_replayed":totals["instructions"],
              "programs_with_interpolation":interp_programs,"interpolation_instruction_count":totals["interp"],"interpolation_result_component_count":totals["components"],
              "opcode_instruction_counts":dict(sorted(ops.items())),"parameter_value_identity_node_count":totals["params"],"m0_state_reference_count":totals["m0"],
              "vgpr_source_state_reference_count":totals["vgpr"],"old_destination_arithmetic_input_count":totals["old"],"parameter_move_instruction_count":totals["mov"],
              "overlay_node_count":totals["nodes"],"attribute_instruction_counts":{str(k):v for k,v in sorted(attrs.items())},"channel_instruction_counts":dict(sorted(channels.items())),
              "shader_expression_semantic_promotions":totals["promotions"]}
    return {"schema":SCHEMA,"status":STATUS if not violations else "D1_GCN_VECTOR_INTERPOLATION_CORPUS_WITH_VIOLATIONS","coverage":coverage,"programs":rows,"violations":violations,
            "semantic_boundary":{"vintrp_formula_identity":"GLOBAL_SOURCE_CLOSED_SYMBOLIC" if not violations else "NOT_PROMOTED","vintrp_result_lane_binding":"GLOBAL_EXACT" if not violations else "NOT_PROMOTED",
                                 "vintrp_m0_state_identity":"GLOBAL_EXACT_CROSS_GRAPH" if not violations else "NOT_PROMOTED","parameter_contents":"LDS_PARAMETER_VALUE_OPAQUE",
                                 "vertex_to_pixel_varying_semantics":"NEXT_GATE","floating_numeric_replay":"WITHHELD","material_semantics":"WITHHELD","shader_expression_semantic_promotions":0},
            "policy":"All exact VINTRP instructions are represented as source-closed symbolic architectural operations attached to existing lane/scalar state. Parameter values remain opaque until VS-to-PS varying/parameter provenance is closed."}


def main()->int:
    ap=argparse.ArgumentParser();ap.add_argument("--ir-dir",type=Path,required=True);ap.add_argument("--census",type=Path,required=True);ap.add_argument("--workers",type=int,default=max(1,min(4,os.cpu_count() or 1)));ap.add_argument("-o","--output",type=Path,required=True);a=ap.parse_args()
    out=replay(a.ir_dir,a.census,max(1,a.workers));a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":out["status"],"coverage":out["coverage"],"violations":out["violations"][:50]},indent=2,sort_keys=True));return 0 if not out["violations"] else 2
if __name__=="__main__":raise SystemExit(main())
