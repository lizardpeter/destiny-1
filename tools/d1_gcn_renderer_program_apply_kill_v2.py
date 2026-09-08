#!/usr/bin/env python3
"""Apply an independently exact 808EE505 export-kill v2 contract to renderer IR."""
from __future__ import annotations
import argparse,json
from collections import Counter
from pathlib import Path

def spans(rows):
    ids=[r["instruction"] for r in rows if r["primary_resolution"]=="STRUCTURAL_ONLY"]
    out=[]
    if not ids:return out
    s=p=ids[0]
    for x in ids[1:]:
        if x==p+1:p=x;continue
        out.append({"start_instruction":s,"end_instruction":p,"count":p-s+1});s=p=x
    out.append({"start_instruction":s,"end_instruction":p,"count":p-s+1})
    return out

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--program",type=Path,required=True)
    ap.add_argument("--kill-v2",type=Path,required=True)
    ap.add_argument("-o","--output",type=Path,required=True)
    a=ap.parse_args()
    d=json.loads(a.program.read_text()); k=json.loads(a.kill_v2.read_text())
    violations=[]
    try:
        if d.get("status")!="D1_GCN_RENDERER_PROGRAM_IR_EXACT_PARTIAL" or d.get("violations"):
            raise ValueError("renderer base not exact-partial")
        if k.get("status")!="D1_GCN_808EE505_EXPORT_KILL_MASK_V2_EXACT" or k.get("violations"):
            raise ValueError("kill v2 proof not exact")
        p=d["program"]; c=k["contract"]
        if (p.get("material"),p.get("pixel_shader"),p.get("instruction_count"))!=("80D777B6","808EE505",456):
            raise ValueError("renderer identity mismatch")
        cov=p["coverage"]
        if cov.get("exact_nonstructural_instruction_count")!=232:
            raise ValueError(f"unexpected base exact count: {cov}")
        rows=p["instruction_resolution"]
        for i in (335,338):
            if rows[i]["primary_resolution"]!="STRUCTURAL_ONLY":
                raise ValueError(f"{i} was not structural-only")
        chain=c["instruction_indices"]
        for i in chain:
            ev=[x for x in rows[i].get("evidence_tags",[]) if x!="PERSISTENT_EXPORT_KILL"]
            if "PERSISTENT_EXPORT_KILL_V2_EXACT" not in ev: ev.append("PERSISTENT_EXPORT_KILL_V2_EXACT")
            rows[i]["evidence_tags"]=ev
        for i in (335,338):
            rows[i]["primary_resolution"]="CONTROL_EXACT"
        p["persistent_export_kills"]=[c]
        counts=dict(sorted(Counter(r["primary_resolution"] for r in rows).items()))
        if counts!={"CONTROL_EXACT":18,"EXPRESSION_EXACT":161,"INPUT_PROVENANCE_EXACT":19,"RECURRENCE_EXACT":36,"STRUCTURAL_ONLY":222}:
            raise ValueError(f"unexpected corrected counts: {counts}")
        cov["primary_resolution_counts"]=counts
        cov["exact_nonstructural_instruction_count"]=234
        cov["structural_only_instruction_count"]=222
        cov["structural_only_spans"]=spans(rows)
        cov["persistent_export_kill_v2_promoted_instructions"]=[335,338]
        cov["persistent_export_kill_contract_version"]=2
        d["corrections"]=list(d.get("corrections") or [])+[{
            "kind":"PERSISTENT_EXPORT_KILL_INEQUALITY_CORRECTION",
            "old_rule":"discard sample > 0.5",
            "correct_rule":"discard sample < 0.5; survive sample >= 0.5",
            "basis":"exact v_subrev operand order + source-proven VOPC/SOP semantics"
        }]
    except Exception as exc:
        violations.append(repr(exc))
    d["violations"]=list(d.get("violations") or [])+violations
    if violations:d["status"]="D1_GCN_RENDERER_PROGRAM_IR_CORRECTION_FAILED"
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(d,indent=2)+"\n")
    print(json.dumps({"status":d["status"],"violations":violations,"coverage":d.get("program",{}).get("coverage")},indent=2))
    return 0 if not violations else 2
if __name__=="__main__":
    raise SystemExit(main())
