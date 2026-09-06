#!/usr/bin/env python3
"""Bounded retail replay for Tower pixel shader family 809DCD66 TFX c6.x.

Scope is deliberately narrow.  The 24 visible retail materials using PS 809DCD66
share a fixed eight-byte resource-setup prefix and then either stop (static c6 is
already serialized) or execute one of five observed arithmetic programs.  Every
observed dynamic program ends in bytes ``42 06`` while PS CBuffer slot 6 is
serialized as zero and native GCN consumes c6.x.  Within this family we therefore
model ``42 06`` as a retail-proven write of the expression result to PS CBuffer
slot 6; the historical engine-wide opcode name remains intentionally withheld.

Known arithmetic opcode identities are source/lineage backed and agree with the
retail streams.  Frame extern 1, element 0 is retained as an abstract ``frame0``
scalar; no seconds/tick units or phase are asserted here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

PREFIX = bytes.fromhex("4900472149014722")
OUTPUT = bytes.fromhex("4206")

# Exact six retail program families observed in the 24 visible materials.
FAMILY_BOUNDS = {
    "421be62f02cd982037e22fefb9e3ef1e708c649fd3fb0addefc84429cee5ed51": (0.0, 150.0),
    "5bcb1246713ab3b3be37b9fcf3c162ff71d86edb0b736b37cfd262caed0e48c0": (0.0, 30.0),
    "5a16de68dbe0e2f7646490606d0e5da977ffa4e53cb4340b573cff2c02095f3d": (0.15, 10.0),
    "f49ec1d4266e751432ebf4ce80f2e6b9959e82963beec175b493dc5b4f040375": (0.0, 30.0),
    "d57c6092f23200569a81b6a103a82eefa9becf307803622728f00eff545f8c7b": (4.0, 4.5),
}
STATIC_SHA = "63e3caa08d671f3587190defea7e77363413343632d9feaae424d2de932b1b90"


def splat(x: float) -> tuple[float, float, float, float]:
    x = float(x)
    return (x, x, x, x)


def vbin(a, b, fn):
    return tuple(fn(float(x), float(y)) for x, y in zip(a, b))


def vadd(a, b): return vbin(a, b, lambda x, y: x + y)
def vmul(a, b): return vbin(a, b, lambda x, y: x * y)
def vlerp(a, b, t): return tuple(float(x) + (float(y) - float(x)) * float(z) for x, y, z in zip(a, b, t))
def vsat(a): return tuple(max(0.0, min(1.0, float(x))) for x in a)


def _round_away_from_zero(x: float) -> float:
    # GPU/TFX helper lineage uses round-to-nearest for phase wrapping.  Python's
    # bankers rounding differs at .5, so keep half cases deterministic here.
    return math.floor(x + 0.5) if x >= 0 else math.ceil(x - 0.5)


def cos_rotations_estimate(a):
    out=[]
    for x in a:
        w=float(x)-_round_away_from_zero(float(x))
        y=w*(-16.0*abs(w)+8.0)
        out.append(y*(0.225*abs(y)+0.775))
    return tuple(out)


def triangle(a):
    return tuple(abs(float(x)-_round_away_from_zero(float(x)))*2.0 for x in a)


def jitter(a):
    x=float(a[0])
    rotations=(x*4.67+0.52, x*2.99+0.37, x*1.08+0.16, x*1.35+0.79)
    wrapped=tuple(v-_round_away_from_zero(v) for v in rotations)
    ma=tuple(abs(v)*-16.0+8.0 for v in wrapped)
    sa=tuple(v*0.25 for v in wrapped)
    q=sum(x*y for x,y in zip(sa,ma))+0.5
    q2=q*q
    r=(-2.0*q+3.0)*q2
    return splat(r)


def constant_vectors(row: dict) -> list[tuple[float,float,float,float]]:
    src=row.get("ps_tfx_constants")
    if src is None:
        src=(row.get("dynamic_array_candidate_scan") or {}).get("2E0")
    vecs=(src or {}).get("vectors") or (src or {}).get("candidate_vectors") or []
    return [tuple(float(x) for x in v["float4"]) for v in vecs]


def cbuffer_vectors(row: dict) -> list[tuple[float,float,float,float]]:
    src=row.get("ps_cbuffers") or row.get("array_300")
    vecs=(src or {}).get("vectors") or []
    return [tuple(float(x) for x in v["float4"]) for v in vecs]


def bytecode_hex(row: dict) -> str:
    return str((row.get("ps_tfx_bytecode") or {}).get("bytes_hex", ""))


def symbolic_x(raw: bytes, consts: list[tuple[float,float,float,float]]) -> str:
    if raw == PREFIX:
        return "serialized_c6.x"
    if not raw.startswith(PREFIX) or not raw.endswith(OUTPUT):
        raise ValueError("program is outside the proven 809DCD66 framing")
    p=len(PREFIX);end=len(raw)-len(OUTPUT);st=[]
    while p<end:
        op=raw[p];p+=1
        if op==0x34: # PushConstantVec4
            idx=raw[p];p+=1
            st.append(f"C{idx}.x({consts[idx][0]:.9g})")
        elif op==0x3C: # PushExternInputFloat
            ex,el=raw[p],raw[p+1];p+=2
            if (ex,el)!=(1,0): raise ValueError(f"unsupported extern {ex}:{el}")
            st.append("Frame[0]")
        elif op==0x03: # Multiply
            a,b=st[-2:];st[-2:]=[f"({a}*{b})"]
        elif op==0x12: # MultiplyAdd
            a,b,c=st[-3:];st[-3:]=[f"(({a}*{b})+{c})"]
        elif op==0x1F: # VecRotCos
            a=st.pop();st.append(f"cosrot({a})")
        elif op==0x23: # Saturate
            a=st.pop();st.append(f"sat({a})")
        elif op==0x27: # Triangle
            a=st.pop();st.append(f"triangle({a})")
        elif op==0x28: # Jitter
            a=st.pop();st.append(f"jitter({a})")
        elif op==0x35: # LerpConstant
            idx=raw[p];p+=1
            t=st.pop();st.append(f"lerp(C{idx}.x,C{idx+1}.x,{t})")
        else:
            raise ValueError(f"unsupported 809DCD66 arithmetic opcode 0x{op:02X} at {p-1:#x}")
    if len(st)!=1: raise ValueError(f"expression left stack depth {len(st)}")
    return st[0]


def eval_program(raw: bytes, consts: list[tuple[float,float,float,float]], cbuffers, frame0: float):
    if raw == PREFIX:
        if len(cbuffers)<=6: raise ValueError("static program missing PS CBuffer c6")
        return cbuffers[6]
    if not raw.startswith(PREFIX) or not raw.endswith(OUTPUT):
        raise ValueError("program is outside the proven 809DCD66 framing")
    p=len(PREFIX);end=len(raw)-len(OUTPUT);st=[]
    while p<end:
        op=raw[p];p+=1
        if op==0x34:
            idx=raw[p];p+=1
            if idx>=len(consts): raise ValueError(f"constant C{idx} unavailable ({len(consts)} vectors)")
            st.append(consts[idx])
        elif op==0x3C:
            ex,el=raw[p],raw[p+1];p+=2
            if (ex,el)!=(1,0): raise ValueError(f"unsupported extern {ex}:{el}")
            st.append(splat(frame0))
        elif op==0x03:
            a,b=st[-2:];st[-2:]=[vmul(a,b)]
        elif op==0x12:
            a,b,c=st[-3:];st[-3:]=[vadd(vmul(a,b),c)]
        elif op==0x1F:
            st[-1]=cos_rotations_estimate(st[-1])
        elif op==0x23:
            st[-1]=vsat(st[-1])
        elif op==0x27:
            st[-1]=triangle(st[-1])
        elif op==0x28:
            st[-1]=jitter(st[-1])
        elif op==0x35:
            idx=raw[p];p+=1
            if idx+1>=len(consts): raise ValueError(f"lerp constants C{idx}/C{idx+1} unavailable")
            t=st.pop();st.append(vlerp(consts[idx],consts[idx+1],t))
        else:
            raise ValueError(f"unsupported 809DCD66 arithmetic opcode 0x{op:02X} at {p-1:#x}")
    if len(st)!=1: raise ValueError(f"expression left stack depth {len(st)}")
    return st[0]


def normalize_material_rows(doc: dict) -> list[dict]:
    mats=doc.get("materials")
    if isinstance(mats,dict): return [dict(r, material=h) for h,r in sorted(mats.items())]
    if isinstance(mats,list): return mats
    raise ValueError("input has no material rows")


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",type=Path,required=True,help="d1_material_ps_constant_resolve.py JSON")
    ap.add_argument("--out",type=Path,required=True)
    ap.add_argument("--sample-start",type=float,default=0.0)
    ap.add_argument("--sample-end",type=float,default=12.0)
    ap.add_argument("--sample-count",type=int,default=12001)
    a=ap.parse_args()
    if a.sample_count<2 or a.sample_end<a.sample_start: raise SystemExit("invalid sampling range")
    doc=json.loads(a.input.read_text())
    rows=normalize_material_rows(doc)
    out_rows=[];groups=defaultdict(list);violations=[]
    for row in rows:
        if row.get("pixel_shader")!="809DCD66": continue
        h=row["material"]
        raw=bytes.fromhex(bytecode_hex(row));sha=hashlib.sha256(raw).hexdigest()
        consts=constant_vectors(row);cbufs=cbuffer_vectors(row)
        try:
            if len(cbufs)!=7: raise ValueError(f"expected 7 PS CBuffer vectors, got {len(cbufs)}")
            if raw==PREFIX:
                if sha!=STATIC_SHA: raise ValueError("unexpected static program hash")
                values=[float(cbufs[6][0])]
                expression="serialized_c6.x"
                mode="static_serialized"
                if values[0] not in (7.0,10.0): raise ValueError(f"unexpected static c6.x {values[0]}")
            else:
                if sha not in FAMILY_BOUNDS: raise ValueError(f"unrecognized dynamic program {sha}")
                if any(abs(x)>0.0 for x in cbufs[6]): raise ValueError(f"dynamic serialized c6 is not zero: {cbufs[6]}")
                expression=symbolic_x(raw,consts);mode="dynamic_tfx_to_c6"
                values=[]
                lo,hi=FAMILY_BOUNDS[sha]
                for i in range(a.sample_count):
                    t=a.sample_start+(a.sample_end-a.sample_start)*(i/(a.sample_count-1))
                    v=float(eval_program(raw,consts,cbufs,t)[0])
                    if not math.isfinite(v): raise ValueError("non-finite sample")
                    if v<lo-1e-5 or v>hi+1e-5: raise ValueError(f"sample {v} outside proven family envelope [{lo},{hi}]")
                    values.append(v)
            rec={
                "material":h,"program_sha256":sha,"program_bytes":len(raw),"mode":mode,
                "tfx_constant_count":len(consts),"ps_cbuffer_count":len(cbufs),
                "serialized_c6":list(cbufs[6]),"expression_x":expression,
                "sample_frame0_range":[a.sample_start,a.sample_end],"sample_count":len(values),
                "sample_c6_x_min":min(values),"sample_c6_x_max":max(values),
                "sample_c6_x_at_frame0_0":float(eval_program(raw,consts,cbufs,0.0)[0]),
            }
            if sha in FAMILY_BOUNDS: rec["mathematical_envelope_x"]=list(FAMILY_BOUNDS[sha])
            out_rows.append(rec);groups[sha].append(h)
        except Exception as ex:
            violations.append({"material":h,"error":repr(ex),"program_sha256":sha})
    fam=[]
    for sha,materials in sorted(groups.items()):
        r=next(x for x in out_rows if x["program_sha256"]==sha)
        fam.append({"program_sha256":sha,"material_count":len(materials),"materials":sorted(materials),
                    "program_bytes":r["program_bytes"],"mode":r["mode"],"tfx_constant_count":r["tfx_constant_count"],
                    "expression_x":r["expression_x"],"mathematical_envelope_x":r.get("mathematical_envelope_x")})
    out={
        "schema_version":1,
        "status":"D1_TOWER_809DCD66_TFX_REPLAY_CLOSED" if not violations and len(out_rows)==24 and len(groups)==6 else "D1_TOWER_809DCD66_TFX_REPLAY_PARTIAL",
        "material_count":len(out_rows),"program_family_count":len(groups),"dynamic_family_count":sum(1 for x in fam if x["mode"]!="static_serialized"),
        "program_families":fam,"materials":out_rows,"violations":violations,
        "retail_output_rule":"For this exact 809DCD66 family only: dynamic programs end 42 06, serialized PS CBuffer c6 is zero, and native GCN consumes c6.x. Replay treats that suffix as expression -> PS CBuffer slot 6. Engine-wide opcode name remains unresolved.",
        "frame_rule":"Extern 1 element 0 is retained as abstract Frame[0]. Sampling is dimensionless and does not assert seconds, ticks, or retail phase.",
        "resource_prefix_hex":PREFIX.hex(),
    }
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps({k:out[k] for k in ("status","material_count","program_family_count","dynamic_family_count","violations")},indent=2))
    for f in fam: print(f["program_bytes"],f["material_count"],f["expression_x"])
    return 0 if out["status"]=="D1_TOWER_809DCD66_TFX_REPLAY_CLOSED" else 2

if __name__=="__main__": raise SystemExit(main())
