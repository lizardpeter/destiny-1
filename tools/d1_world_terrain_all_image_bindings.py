#!/usr/bin/env python3
"""Close every native image texture/sampler binding in the selected D1 RoI terrain corpus.

For every selected terrain material and every exact native image instruction in
its pixel shader, require:
  * exactly one source-closed texture resource index;
  * resource index 14 is the independently proven draw-owned SMeshGroup dyemap;
  * every other sampled resource index exists in the serialized SMaterial_ROI
    PS texture array with exactly one TagHash;
  * exactly one ImmSampler API slot;
  * API sampler slot N resolves to inline PS sampler record N-1;
  * that sampler TagHash resolves to an exact native 80801A42 sampler descriptor.

This is a binding census only. It does not infer texture semantic roles.
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
    resource_materials={norm(r["material"]):r for r in resources["materials"]}
    if len(resource_materials)!=resources["selected_material_count"]:
        raise SystemExit("terrain material row count mismatch")

    c=v5.v3.base.Corpus([p.resolve() for p in a.snapshot],a.runtime.resolve())
    missing=collections.Counter()
    violations=[]
    sampler_cache={}
    sampler_hash_hist=collections.Counter()
    texture_index_hist=collections.Counter()
    sampler_api_hist=collections.Counter()
    image_opcode_hist=collections.Counter()
    material_out=[]
    total_image_bindings=0
    serialized_image_bindings=0
    external_t14_bindings=0

    for mh,summary in sorted(resource_materials.items()):
        shader=norm(summary.get("pixel_shader"))
        native=flow_by_shader.get(shader)
        row={
            "material":mh,
            "pixel_shader":shader,
            "image_instruction_count":0,
            "bindings":[],
        }
        if native is None:
            row["status"]="NATIVE_DATAFLOW_MISSING"
            violations.append({"material":mh,"shader":shader,"error":"shader absent from exact native dataflow"})
            material_out.append(row)
            continue

        mm=c.entry_meta(mh)
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
            row["status"]="MATERIAL_DECODE_ERROR"
            row["error"]=repr(ex)
            violations.append({"material":mh,"error":repr(ex)})
            material_out.append(row)
            continue

        textures=collections.defaultdict(set)
        for item in dec["ps_textures"]["items"]:
            h=norm(item.get("texture"))
            if h not in NULLS:
                textures[int(item["texture_index"])].add(h)
        sampler_records=dec["ps_samplers"]["items"]
        row["serialized_texture_indices"]=sorted(textures)
        row["ps_sampler_count"]=len(sampler_records)

        material_ok=True
        for ins in native.get("instructions",[]):
            total_image_bindings+=1
            row["image_instruction_count"]+=1
            image_opcode_hist[str(ins.get("opcode"))]+=1
            resources_here=ins.get("resources",[])
            samplers_here=ins.get("samplers",[])
            b={
                "assembly":ins.get("assembly"),
                "opcode":ins.get("opcode"),
                "dmask":ins.get("dmask_channels"),
            }
            if len(resources_here)!=1:
                b["status"]="RESOURCE_CARDINALITY_MISMATCH"
                b["resources"]=resources_here
                violations.append({"material":mh,"shader":shader,"error":"image resource count != 1","instruction":ins})
                row["bindings"].append(b);material_ok=False;continue
            resource=resources_here[0]
            if resource.get("provenance_kind") not in ("ResourceTableResource","ImmResource"):
                b["status"]="RESOURCE_PROVENANCE_UNSUPPORTED"
                b["resource"]=resource
                violations.append({"material":mh,"shader":shader,"error":"image resource provenance not source-closed","resource":resource})
                row["bindings"].append(b);material_ok=False;continue
            ti=int(resource["texture_index"])
            b["texture_index"]=ti
            texture_index_hist[ti]+=1
            if ti==14:
                b["texture_owner"]="SMeshGroup.effective_dyemap"
                external_t14_bindings+=1
            else:
                hashes=textures.get(ti,set())
                if len(hashes)!=1:
                    b["status"]="SERIALIZED_TEXTURE_IDENTITY_UNRESOLVED"
                    b["serialized_hashes"]=sorted(hashes)
                    violations.append({
                        "material":mh,"shader":shader,"texture_index":ti,
                        "error":f"sampled t{ti} maps to {len(hashes)} serialized hashes",
                        "hashes":sorted(hashes),
                    })
                    row["bindings"].append(b);material_ok=False;continue
                b["texture_owner"]="SMaterial_ROI.ps_textures"
                b["texture_hash"]=next(iter(hashes))
                serialized_image_bindings+=1

            if len(samplers_here)!=1:
                b["status"]="SAMPLER_CARDINALITY_MISMATCH"
                b["samplers"]=samplers_here
                violations.append({"material":mh,"shader":shader,"error":"image sampler count != 1","instruction":ins})
                row["bindings"].append(b);material_ok=False;continue
            sampler=samplers_here[0]
            if sampler.get("provenance_kind")!="ImmSampler":
                b["status"]="SAMPLER_PROVENANCE_UNSUPPORTED"
                b["sampler"]=sampler
                violations.append({"material":mh,"shader":shader,"error":"image sampler is not ImmSampler","sampler":sampler})
                row["bindings"].append(b);material_ok=False;continue
            api=int(sampler["sampler_index"])
            b["sampler_api_slot"]=api
            sampler_api_hist[api]+=1
            index=api-1
            if index<0 or index>=len(sampler_records):
                b["status"]="SAMPLER_SLOT_OUT_OF_RANGE"
                violations.append({
                    "material":mh,"shader":shader,"sampler_api_slot":api,
                    "error":f"API sampler {api} has no PS sampler record; count={len(sampler_records)}"
                })
                row["bindings"].append(b);material_ok=False;continue
            rec=sampler_records[index]
            sh=norm(rec["first_dword_hex"])
            b["inline_sampler_index"]=index
            b["inline_sampler_raw_hex"]=rec["raw_hex"]
            b["sampler_hash"]=sh
            sampler_hash_hist[sh]+=1
            if sh in NULLS:
                b["status"]="NULL_SAMPLER"
                violations.append({"material":mh,"shader":shader,"sampler_api_slot":api,"error":"null sampler hash"})
                row["bindings"].append(b);material_ok=False;continue

            resolved=sampler_cache.get(sh)
            if resolved is None:
                sm=c.entry_meta(sh)
                if sm is None:
                    p=pkgid(sh)
                    if p: missing[p]+=1
                    resolved={"status":"MISSING","required_package_id":p}
                else:
                    sb,ssrc=c.payload(sh)
                    if sb is None:
                        p=pkgid(sh)
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
                sampler_cache[sh]=resolved
            b["native_sampler_status"]=resolved.get("status")
            if resolved.get("status")!="D1_NATIVE_SAMPLER_EXACT":
                b["status"]="SAMPLER_UNRESOLVED"
                if resolved.get("status") not in ("MISSING","PAYLOAD_MISSING"):
                    violations.append({"material":mh,"shader":shader,"sampler":sh,"error":resolved})
                row["bindings"].append(b);material_ok=False;continue

            b["status"]="D1_TERRAIN_IMAGE_BINDING_CLOSED"
            row["bindings"].append(b)

        row["status"]="D1_TERRAIN_MATERIAL_IMAGE_BINDINGS_CLOSED" if material_ok else "D1_TERRAIN_MATERIAL_IMAGE_BINDINGS_PARTIAL"
        material_out.append(row)

    missing_ids=dict(sorted(missing.items()))
    closed_materials=sum(r.get("status")=="D1_TERRAIN_MATERIAL_IMAGE_BINDINGS_CLOSED" for r in material_out)
    closed_bindings=sum(
        b.get("status")=="D1_TERRAIN_IMAGE_BINDING_CLOSED"
        for r in material_out for b in r.get("bindings",[])
    )
    complete=(
        not missing_ids and not violations
        and closed_materials==resources["selected_material_count"]
        and closed_bindings==total_image_bindings
    )
    out={
        "schema_version":1,
        "status":"D1_TERRAIN_ALL_IMAGE_BINDINGS_CLOSED" if complete else "D1_TERRAIN_ALL_IMAGE_BINDINGS_PARTIAL",
        "terrain_activity":"810B0002",
        "selected_material_count":resources["selected_material_count"],
        "closed_material_count":closed_materials,
        "pixel_shader_count":len(flow_by_shader),
        "total_material_image_bindings":total_image_bindings,
        "closed_material_image_bindings":closed_bindings,
        "serialized_texture_bindings":serialized_image_bindings,
        "external_t14_bindings":external_t14_bindings,
        "texture_index_histogram":{str(k):v for k,v in sorted(texture_index_hist.items())},
        "sampler_api_slot_histogram":{str(k):v for k,v in sorted(sampler_api_hist.items())},
        "image_opcode_histogram":dict(sorted(image_opcode_hist.items())),
        "unique_native_sampler_hash_count":len([h for h in sampler_hash_hist if h not in NULLS]),
        "native_sampler_hash_histogram":dict(sorted(sampler_hash_hist.items())),
        "native_samplers":sampler_cache,
        "missing_dependency_package_ids":missing_ids,
        "violations":violations,
        "materials":material_out,
        "proof_boundary":(
            "Every exact native terrain PS image instruction is joined to its source texture ownership "
            "(serialized SMaterial_ROI texture or independently proven draw-owned T14) and exact "
            "ImmSampler -> inline material sampler -> native 80801A42 descriptor. No default sampler, "
            "slot-number semantic inference, or synthetic texture identity is admitted."
        ),
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:out[k] for k in (
        "status","selected_material_count","closed_material_count","pixel_shader_count",
        "total_material_image_bindings","closed_material_image_bindings",
        "serialized_texture_bindings","external_t14_bindings",
        "texture_index_histogram","sampler_api_slot_histogram","image_opcode_histogram",
        "unique_native_sampler_hash_count","missing_dependency_package_ids","violations"
    )},indent=2))
    return 0 if complete else 2


if __name__=="__main__":
    raise SystemExit(main())
