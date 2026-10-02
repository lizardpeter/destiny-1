#!/usr/bin/env python3
"""Exact byte-layout probe for D1 PS4 cubemap 80AACC28 / payload 80AACC29.

This does not assume the lower-mip ordering. It records the exact header and
payload metadata, then tests a small set of explicit candidate layouts against
the payload byte count and PS4 8x8 Morton spans already closed for D1 textures.

The probe is deliberately fail-closed: a byte-count match is only a layout
candidate, not semantic proof of face/level order.
"""
from __future__ import annotations
import argparse, hashlib, json, sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from d1_entry_extract import EntryReader
from d1_texture_export import (
    build_global_index, decode_header, expected_base_size, logical_package_family_key
)

HEADER="80AACC28"
PAYLOAD="80AACC29"
RGBA8=0x0A


def ceil_pow2(v:int)->int:
    return max(1,v).bit_length() and 1<<(max(1,v)-1).bit_length()


def swizzled_level_span(w:int,h:int,gfmt:int)->int:
    # Same D1 ROI rule already proven in the Rust decoder: dimensions round up
    # to powers of two before 8x8 tile count. RGBA8 = 4 bytes/block, 1 px/block.
    if gfmt != RGBA8:
        raise ValueError(f"probe currently expects RGBA8, got {gfmt:#x}")
    ws=ceil_pow2(w); hs=ceil_pow2(h)
    tiles_x=(ws+7)//8; tiles_y=(hs+7)//8
    return tiles_x*tiles_y*64*4


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--pkg",type=Path,action="append",required=True)
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()

    readers=[]
    seen=set()
    for p in a.pkg:
        key=logical_package_family_key(p)
        if key in seen:
            continue
        seen.add(key)
        readers.append(EntryReader(p))
    by=build_global_index(readers)

    hrec=by.get(HEADER)
    prec=by.get(PAYLOAD)
    if hrec is None or prec is None:
        missing=[x for x,r in ((HEADER,hrec),(PAYLOAD,prec)) if r is None]
        raise SystemExit(f"missing exact tag(s): {missing}")

    hr,he=hrec; pr,pe=prec
    hb=hr.entry(he["index"])
    pb=pr.entry(pe["index"])
    hdr=decode_header(hb)

    if (hdr["width"],hdr["height"],hdr["array_size"],hdr["surface_format"]) != (64,64,6,RGBA8):
        raise SystemExit(f"unexpected cube header: {hdr}")

    top_face=expected_base_size(64,64,RGBA8,1)
    top_all=expected_base_size(64,64,RGBA8,6)
    levels=[]
    w=h=64
    level=0
    while True:
        per_face_linear=expected_base_size(w,h,RGBA8,1)
        per_face_swizzled=swizzled_level_span(w,h,RGBA8)
        levels.append({
            "level":level,"width":w,"height":h,
            "linear_face_bytes":per_face_linear,
            "swizzled_face_span":per_face_swizzled,
            "linear_six_face_bytes":per_face_linear*6,
            "swizzled_six_face_span":per_face_swizzled*6,
        })
        if w==1 and h==1: break
        w=max(1,w//2); h=max(1,h//2); level+=1

    lower_swizzled=sum(x["swizzled_six_face_span"] for x in levels[1:])
    lower_linear=sum(x["linear_six_face_bytes"] for x in levels[1:])
    full_swizzled=levels[0]["swizzled_six_face_span"]+lower_swizzled
    full_linear=levels[0]["linear_six_face_bytes"]+lower_linear

    # Explicit candidate organizations. These are byte-span tests only.
    candidates={
        "top_level_only":{
            "expected_bytes":top_all,
            "matches":len(pb)==top_all,
        },
        "level_major_swizzled_full_chain":{
            "expected_bytes":full_swizzled,
            "matches":len(pb)==full_swizzled,
        },
        "level_major_linear_full_chain":{
            "expected_bytes":full_linear,
            "matches":len(pb)==full_linear,
        },
        "top_plus_swizzled_lower_tail":{
            "expected_bytes":top_all+lower_swizzled,
            "matches":len(pb)==top_all+lower_swizzled,
        },
        "top_plus_linear_lower_tail":{
            "expected_bytes":top_all+lower_linear,
            "matches":len(pb)==top_all+lower_linear,
        },
    }

    report={
        "schema_version":1,
        "status":"D1_80AACC28_CUBE_MIP_BYTE_FRONTIER",
        "header_tag":HEADER,
        "payload_tag":PAYLOAD,
        "header_owner_package":str(hr.pkg),
        "payload_owner_package":str(pr.pkg),
        "header_entry":he,
        "payload_entry":pe,
        "header_payload_bytes":len(hb),
        "payload_bytes":len(pb),
        "header_payload_sha256":hashlib.sha256(hb).hexdigest(),
        "payload_sha256":hashlib.sha256(pb).hexdigest(),
        "header":hdr,
        "levels":levels,
        "top_level_bytes":top_all,
        "lower_linear_bytes":lower_linear,
        "lower_swizzled_span":lower_swizzled,
        "full_linear_bytes":full_linear,
        "full_swizzled_span":full_swizzled,
        "candidate_layouts":candidates,
        "payload_prefix_sha256_98304":hashlib.sha256(pb[:top_all]).hexdigest() if len(pb)>=top_all else None,
        "payload_tail_bytes_after_top":max(0,len(pb)-top_all),
        "payload_tail_sha256_after_top":hashlib.sha256(pb[top_all:]).hexdigest() if len(pb)>top_all else None,
        "proof_boundary":"A candidate byte-count match identifies only a possible storage span. Face/level ordering and native mip semantics require independent byte/dataflow evidence before promotion."
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2,sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
