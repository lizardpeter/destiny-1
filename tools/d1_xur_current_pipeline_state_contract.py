#!/usr/bin/env python3
"""Promote the current Xur material-local pipeline-state contract fail-closed.

Inputs:
- exact D1 PS4 ROI Material +0x20 four-byte state windows;
- pinned independent Tiger PipelineState source;
- pinned Alkahest rasterizer-state binary.

This closes only *material-local overrides*. A zero lane means the material does
not override that state; it does not prove the inherited/global state itself.
"""
from __future__ import annotations
import argparse,hashlib,json,struct
from pathlib import Path

LANES=("blend_state","depth_stencil_state","rasterizer_state","depth_bias_state")
FILL={2:"WIREFRAME",3:"SOLID"}
CULL={1:"NONE",2:"FRONT",3:"BACK"}

def decode_selector(v:int):
    return (v & 0x7f) if (v & 0x80) else None

def decode_rasterizer(blob:bytes):
    if len(blob)%44:
        raise ValueError(f"rasterizer table size {len(blob)} is not 44-byte aligned")
    rows=[]
    for i in range(len(blob)//44):
        vals=struct.unpack_from("<IIiiffiiiiI",blob,i*44)
        fill,cull,front_ccw,depth_bias,depth_bias_clamp,slope,depth_clip,scissor,multisample,aa_line,pad=vals
        rows.append({
            "index":i,
            "fill_mode_raw":fill,"fill_mode":FILL.get(fill,f"UNKNOWN_{fill}"),
            "cull_mode_raw":cull,"cull_mode":CULL.get(cull,f"UNKNOWN_{cull}"),
            "front_counter_clockwise":bool(front_ccw),
            "depth_bias":depth_bias,
            "depth_bias_clamp":depth_bias_clamp,
            "slope_scaled_depth_bias":slope,
            "depth_clip_enable":bool(depth_clip),
            "scissor_enable":bool(scissor),
            "multisample_enable":bool(multisample),
            "antialiased_line_enable":bool(aa_line),
            "trailing_u32":pad,
        })
    return rows

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--state4",type=Path,required=True)
    ap.add_argument("--technique-rs",type=Path,required=True)
    ap.add_argument("--rasterizer-bin",type=Path,required=True)
    ap.add_argument("-o","--output",type=Path,required=True)
    a=ap.parse_args()
    s=json.loads(a.state4.read_text())
    tech=a.technique_rs.read_text()
    rb=a.rasterizer_bin.read_bytes()
    violations=[]
    if s.get("status")!="D1_REMOTE_PS4_ROI_MATERIAL_STATE4_COMPLETE" or s.get("violations"):
        violations.append("state4_not_exact")
    required=[
        "blend_state: u8","depth_stencil_state: u8","rasterizer_state: u8","depth_bias_state: u8",
        "if self.rasterizer_state & 0x80 != 0","Some((self.rasterizer_state & 0x7f) as usize)",
    ]
    for x in required:
        if x not in tech: violations.append("technique_source_missing:"+x)
    rast=decode_rasterizer(rb)
    if len(rast)!=9: violations.append(f"rasterizer_state_count:{len(rast)}!=9")

    rows=[]
    hist={}
    lane_selected={k:{} for k in LANES}
    selected_indices={k:set() for k in LANES}
    for r in s.get("rows",[]):
        lanes=r.get("lanes_u8")
        if not isinstance(lanes,list) or len(lanes)!=4:
            violations.append(f"{r.get('material')}:bad_lanes")
            continue
        hx="".join(f"{int(x):02X}" for x in lanes)
        hist[hx]=hist.get(hx,0)+1
        decoded={}
        for name,v in zip(LANES,lanes):
            idx=decode_selector(int(v))
            decoded[name]=idx
            lane_selected[name][r["material"]]=idx
            if idx is not None:selected_indices[name].add(idx)
        rows.append({"material":r["material"],"state4_hex":hx,"lanes_u8":lanes,"selected_indices":decoded})

    used_rasterizer=sorted(selected_indices["rasterizer_state"])
    out={
        "schema_version":1,
        "status":"D1_XUR_CURRENT_MATERIAL_LOCAL_PIPELINE_STATE_EXACT" if not violations else "D1_XUR_CURRENT_MATERIAL_LOCAL_PIPELINE_STATE_VIOLATIONS",
        "material_count":len(rows),
        "pipeline_state_lane_order":list(LANES),
        "selector_encoding":"high bit active; low seven bits table index",
        "state4_histogram":hist,
        "selected_indices_by_lane":{k:sorted(v) for k,v in selected_indices.items()},
        "material_rows":rows,
        "rasterizer_table_sha256":hashlib.sha256(rb).hexdigest(),
        "rasterizer_state_count":len(rast),
        "used_rasterizer_states":[rast[i] for i in used_rasterizer if i < len(rast)],
        "material_local_override_contract":{
            "blend_override_indices":sorted(selected_indices["blend_state"]),
            "depth_stencil_override_indices":sorted(selected_indices["depth_stencil_state"]),
            "rasterizer_override_indices":used_rasterizer,
            "depth_bias_override_indices":sorted(selected_indices["depth_bias_state"]),
        },
        "portable_implications":{
            "no_material_blend_override":not selected_indices["blend_state"],
            "no_material_depth_stencil_override":not selected_indices["depth_stencil_state"],
            "no_material_depth_bias_override":not selected_indices["depth_bias_state"],
            "rasterizer_state_1_two_sided_if_used":(
                1 in selected_indices["rasterizer_state"] and len(rast)>1 and rast[1]["cull_mode"]=="NONE"
            ),
        },
        "inherited_global_pipeline_state_closed":False,
        "violations":violations,
        "policy":"Zero state lanes mean no material-local override only. This proof does not invent inherited/global state. Rasterizer descriptions are decoded from the pinned independent Tiger renderer table, not inferred from appearance."
    }
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps({k:out[k] for k in ["status","material_count","state4_histogram","selected_indices_by_lane","used_rasterizer_states","portable_implications","violations"]},indent=2))
    return 0 if not violations else 2
if __name__=="__main__": raise SystemExit(main())
