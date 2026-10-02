#!/usr/bin/env python3
"""Close D1 RoI terrain T14 sampler identities across the exact Crota corpus.

Inputs:
* authoritative terrain PS resource census (selected materials + exact PS headers);
* exact native GCN image dataflow (T14 resource and sampler API slot);
* current package snapshots.

For every selected material whose native PS samples T14, this proves:
  native T14 image_sample -> exact ImmSampler API slot N
  -> SMaterial_ROI PS inline sampler record N-1
  -> exact 80801A42 native sampler TagHash and descriptor.

This tool does not infer filter semantics beyond the already decoded native Gnm
sampler fields and does not synthesize a fallback sampler.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
from pathlib import Path

import d1_tower_map_schema_validate_v5 as v5
from d1_filehash import package_hex
from d1_material_decode import parse_material
from d1_ps4_sampler_probe import SAMPLER_CLASS, decode_blob as decode_sampler

NULLS={"00000000","FFFFFFFF"}


def norm(v: object) -> str:
    return str(v).upper().removeprefix("0X").zfill(8)


def pkgid(h: object) -> str | None:
    h=norm(h)
    if h in NULLS:
        return None
    try:
        return package_hex(h).lower()
    except Exception:
        return None


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--snapshot",type=Path,action="append",required=True)
    ap.add_argument("--runtime",type=Path,required=True)
    ap.add_argument("--terrain-resources",type=Path,required=True)
    ap.add_argument("--native-dataflow",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()

    resources=json.loads(a.terrain_resources.read_text(encoding="utf-8"))
    flow=json.loads(a.native_dataflow.read_text(encoding="utf-8"))
    if resources.get("status")!="D1_WORLD_TERRAIN_PS_RESOURCE_CENSUS_COMPLETE":
        raise SystemExit("terrain resource census is not complete")
    if flow.get("status")!="D1_CROTA_TERRAIN_NATIVE_PS_DATAFLOW_EXACT":
        raise SystemExit("native terrain dataflow is not exact")

    flow_by_shader={norm(r["shader"]):r for r in flow["pixel_shaders"]}
    material_rows={norm(r["material"]):r for r in resources["materials"]}

    # Recover the one exact sampler API slot used by T14 in each native PS.
    shader_t14={}
    violations=[]
    for shader,row in sorted(flow_by_shader.items()):
        hits=[]
        for ins in row.get("instructions",[]):
            if any(int(r.get("texture_index",-1))==14 for r in ins.get("resources",[])):
                hits.append(ins)
        if not hits:
            continue
        if len(hits)!=1:
            violations.append({"shader":shader,"error":"T14 image instruction count != 1","count":len(hits)})
            continue
        samplers=hits[0].get("samplers",[])
        if len(samplers)!=1:
            violations.append({"shader":shader,"error":"T14 sampler count != 1","samplers":samplers})
            continue
        sampler=samplers[0]
        if sampler.get("provenance_kind")!="ImmSampler":
            violations.append({"shader":shader,"error":"T14 sampler is not ImmSampler","sampler":sampler})
            continue
        shader_t14[shader]={
            "sampler_api_slot":int(sampler["sampler_index"]),
            "instruction":hits[0]["assembly"],
            "dmask":hits[0].get("dmask_channels"),
            "opcode":hits[0].get("opcode"),
        }

    c=v5.v3.base.Corpus([p.resolve() for p in a.snapshot],a.runtime.resolve())
    missing=collections.Counter()
    sampler_hash_hist=collections.Counter()
    sampler_api_hist=collections.Counter()
    material_out=[]
    decoded_sampler_cache={}

    for mh,summary in sorted(material_rows.items()):
        shader=norm(summary.get("pixel_shader"))
        t14=shader_t14.get(shader)
        if t14 is None:
            continue

        mm=c.entry_meta(mh)
        row={
            "material":mh,
            "pixel_shader":shader,
            "sampler_api_slot":t14["sampler_api_slot"],
            "t14_instruction":t14["instruction"],
            "t14_dmask":t14["dmask"],
        }
        if mm is None:
            p=pkgid(mh)
            if p: missing[p]+=1
            row["status"]="MATERIAL_MISSING"
            material_out.append(row)
            continue
        payload,src=c.payload(mh)
        row["material_source"]=src
        if payload is None:
            p=pkgid(mh)
            if p: missing[p]+=1
            row["status"]="MATERIAL_PAYLOAD_MISSING"
            material_out.append(row)
            continue
        try:
            dec=parse_material(payload,"PS4")
        except Exception as ex:
            row["status"]="MATERIAL_DECODE_ERROR";row["error"]=repr(ex)
            violations.append({"material":mh,"error":repr(ex)})
            material_out.append(row);continue

        slot=t14["sampler_api_slot"]
        records=dec["ps_samplers"]["items"]
        row["ps_sampler_count"]=len(records)
        index=slot-1
        if index<0 or index>=len(records):
            row["status"]="SAMPLER_SLOT_OUT_OF_RANGE"
            violations.append({
                "material":mh,"pixel_shader":shader,
                "error":f"native T14 sampler API slot {slot} has no PS sampler record; count={len(records)}"
            })
            material_out.append(row);continue

        rec=records[index]
        sampler_hash=norm(rec["first_dword_hex"])
        row.update({
            "inline_sampler_index":index,
            "inline_sampler_offset":int(rec["offset"]),
            "inline_sampler_raw_hex":rec["raw_hex"],
            "sampler_hash":sampler_hash,
        })
        sampler_api_hist[slot]+=1
        sampler_hash_hist[sampler_hash]+=1
        if sampler_hash in NULLS:
            row["status"]="NULL_SAMPLER"
            violations.append({"material":mh,"pixel_shader":shader,"error":f"T14 sampler API slot {slot} is null"})
            material_out.append(row);continue

        if sampler_hash in decoded_sampler_cache:
            resolved=decoded_sampler_cache[sampler_hash]
        else:
            sm=c.entry_meta(sampler_hash)
            if sm is None:
                p=pkgid(sampler_hash)
                if p: missing[p]+=1
                resolved={"status":"MISSING","required_package_id":p}
            else:
                sb,ssrc=c.payload(sampler_hash)
                if sb is None:
                    p=pkgid(sampler_hash)
                    if p: missing[p]+=1
                    resolved={"status":"PAYLOAD_MISSING","required_package_id":p,"meta":sm,"source":ssrc}
                elif norm(sm.get("reference"))!=SAMPLER_CLASS:
                    resolved={"status":"CLASS_MISMATCH","meta":sm,"source":ssrc}
                else:
                    try:
                        decoded=decode_sampler(sb)
                        resolved={
                            "status":"D1_NATIVE_SAMPLER_EXACT",
                            "meta":sm,
                            "source":ssrc,
                            "payload_sha256":hashlib.sha256(sb).hexdigest(),
                            "decoded":decoded,
                        }
                    except Exception as ex:
                        resolved={"status":"DECODE_ERROR","meta":sm,"source":ssrc,"error":repr(ex)}
            decoded_sampler_cache[sampler_hash]=resolved

        row["native_sampler"]=resolved
        row["status"]="D1_TERRAIN_T14_SAMPLER_CLOSED" if resolved.get("status")=="D1_NATIVE_SAMPLER_EXACT" else "SAMPLER_UNRESOLVED"
        if row["status"]!="D1_TERRAIN_T14_SAMPLER_CLOSED" and resolved.get("status") not in ("MISSING","PAYLOAD_MISSING"):
            violations.append({"material":mh,"sampler":sampler_hash,"error":resolved})
        material_out.append(row)

    missing_ids=dict(sorted(missing.items()))
    selected_t14_materials=sum(1 for r in material_rows.values() if norm(r.get("pixel_shader")) in shader_t14)
    closed=sum(r.get("status")=="D1_TERRAIN_T14_SAMPLER_CLOSED" for r in material_out)
    complete=not missing_ids and not violations and closed==selected_t14_materials

    out={
        "schema_version":1,
        "status":"D1_TERRAIN_T14_SAMPLER_CLOSURE_COMPLETE" if complete else "D1_TERRAIN_T14_SAMPLER_CLOSURE_PARTIAL",
        "terrain_activity":"810B0002",
        "t14_shader_count":len(shader_t14),
        "selected_t14_material_count":selected_t14_materials,
        "closed_t14_material_count":closed,
        "t14_sampler_api_slot_histogram":{str(k):v for k,v in sorted(sampler_api_hist.items())},
        "unique_t14_sampler_hash_count":len([h for h in sampler_hash_hist if h not in NULLS]),
        "t14_sampler_hash_histogram":dict(sorted(sampler_hash_hist.items())),
        "missing_dependency_package_ids":missing_ids,
        "violations":violations,
        "shader_t14_sampler_contract":shader_t14,
        "native_samplers":decoded_sampler_cache,
        "materials":material_out,
        "proof_boundary":(
            "Exact native T14 image_sample -> ImmSampler API slot -> SMaterial_ROI PS inline "
            "sampler record -> 80801A42 native Gnm sampler descriptor. No fallback/default "
            "sampler is admitted by this evidence."
        ),
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:out[k] for k in (
        "status","t14_shader_count","selected_t14_material_count","closed_t14_material_count",
        "t14_sampler_api_slot_histogram","unique_t14_sampler_hash_count",
        "missing_dependency_package_ids","violations"
    )},indent=2))
    return 0 if complete else 2


if __name__=="__main__":
    raise SystemExit(main())
