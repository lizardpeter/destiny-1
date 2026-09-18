#!/usr/bin/env python3
"""Probe D1 PS4 native shaders through an exact logical package overlay.

Unlike d1_ps4_shader_binary_probe.py, this reader accepts all physical siblings
for one or more Tiger package families and resolves entry blocks by their exact
patch_id. This prevents a material's physical package or the newest patch member
from being mistaken for the residency of a referenced shader wrapper.

Evidence policy:
* requested wrapper identity comes from the Tiger FileHash package/index decoder;
* the latest supplied package member supplies the logical entry/block tables;
* each block is read from its table-declared patch owner and SHA1-checked by
  RemoteLogicalPackage;
* OrbShdr stage/usage metadata and bounded GCN hashes are decoded from recovered
  retail bytes;
* no engine semantic, runtime descriptor value, or tessellation ownership is
  inferred from the LocalShader stage name.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))

from d1_filehash import decode as decode_filehash
from d1_remote_investment_parent_probe import RemoteLogicalPackage,parse_member
from d1_split_tar_extract import SplitHttpTar
from d1_entry_extract import decode_known
from d1_ps4_shader_binary_probe import find_footer,parse_binary_info,parse_usage


def norm(x: object)->str:
    s=str(x).upper().removeprefix("0X").zfill(8)
    int(s,16)
    return s


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--tag-hash",action="append",required=True)
    ap.add_argument("--member",action="append",type=parse_member,required=True,
                    help="physical member NAME:DATA_OFFSET:SIZE; repeatable")
    ap.add_argument("--base-url",default="https://crypt.cohae.dev/destiny/ps4/packages/latest")
    ap.add_argument("--part-count",type=int,default=10)
    ap.add_argument("--runtime",type=Path,required=True)
    ap.add_argument("--dump-dir",type=Path)
    ap.add_argument("-o","--output",type=Path,required=True)
    a=ap.parse_args()

    groups:dict[int,dict[int,object]]=defaultdict(dict)
    for m in a.member:
        groups[m.pkg_id][m.patch_id]=m

    base=a.base_url.rstrip("/")
    arc=SplitHttpTar([f"{base}/packages.tar.{i:03d}" for i in range(1,a.part_count+1)],retries=6,timeout=120)
    views={pkg:RemoteLogicalPackage(arc,siblings,a.runtime) for pkg,siblings in sorted(groups.items())}

    package_rows=[]
    for pkg,v in sorted(views.items()):
        package_rows.append({
            "package_id":f"{pkg:04X}",
            "logical_view_member":v.view.name,
            "entry_count":len(v.entries),
            "block_count":len(v.blocks),
            "physical_members":[
                {"patch_id":p,"name":m.name,"data_offset":m.data_offset,"size":m.size}
                for p,m in sorted(v.members.items())
            ],
        })

    rows=[];viol=[]
    for raw in a.tag_hash:
        tag=norm(raw);pkg,idx=decode_filehash(tag)
        row={"tag_hash":tag,"package_id":f"{pkg:04X}","file_index":idx,"violations":[]}
        view=views.get(pkg)
        if view is None:
            row["violations"].append("package_family_not_supplied");rows.append(row);continue
        if idx>=len(view.entries):
            row["violations"].append("file_index_outside_logical_entry_table");rows.append(row);continue
        e=view.entries[idx]
        row["entry"]={k:e[k] for k in ("index","tag_hash","reference","type","subtype","file_size","starting_block","starting_block_offset") if k in e}
        row["entry"]["tag_hash"]=row["entry"]["tag_hash"].upper();row["entry"]["reference"]=row["entry"]["reference"].upper()
        if row["entry"]["tag_hash"]!=tag:
            row["violations"].append("logical_tag_hash_mismatch");rows.append(row);continue
        try: header=view.entry(idx)
        except Exception as ex:
            row["violations"].append("header_read:"+repr(ex));rows.append(row);continue

        row["header_size"]=len(header)
        row["header_sha256"]=hashlib.sha256(header).hexdigest()
        row["header_decode"]=decode_known(e,header,view.h["platform"])
        ref=row["entry"]["reference"];rpkg,ridx=decode_filehash(ref)
        row["payload_reference"]=ref
        row["payload_package_id"]=f"{rpkg:04X}"
        row["payload_file_index"]=ridx
        rview=views.get(rpkg)
        if rview is None:
            row["violations"].append("payload_package_family_not_supplied");rows.append(row);continue
        if ridx>=len(rview.entries):
            row["violations"].append("payload_index_outside_logical_entry_table");rows.append(row);continue
        pe=rview.entries[ridx]
        row["payload_entry"]={k:pe[k] for k in ("index","tag_hash","reference","type","subtype","file_size","starting_block","starting_block_offset") if k in pe}
        row["payload_entry"]["tag_hash"]=row["payload_entry"]["tag_hash"].upper();row["payload_entry"]["reference"]=row["payload_entry"]["reference"].upper()
        if row["payload_entry"]["tag_hash"]!=ref:
            row["violations"].append("payload_logical_tag_hash_mismatch");rows.append(row);continue
        try: payload=rview.entry(ridx)
        except Exception as ex:
            row["violations"].append("payload_read:"+repr(ex));rows.append(row);continue

        row["payload_size"]=len(payload)
        row["payload_sha256"]=hashlib.sha256(payload).hexdigest()
        row["header_declared_payload_matches_actual"]=row["header_decode"].get("embedded_data_size")==len(payload)
        footer,checks=find_footer(payload);row["orbshdr_locator"]=checks
        if footer is None:
            row["violations"].append("orbshdr_footer_unresolved");rows.append(row);continue
        info=parse_binary_info(payload,footer);row["binary_info"]=info
        code=payload[:info["code_length_bytes"]]
        row["code_size"]=len(code);row["code_sha256"]=hashlib.sha256(code).hexdigest()
        row["code_length_before_footer"]=info["code_length_bytes"]<=footer
        row["bytes_between_code_and_footer"]=footer-info["code_length_bytes"]
        try: row["usage"]=parse_usage(payload,footer,info)
        except Exception as ex:
            row["violations"].append("usage_parse:"+repr(ex))

        if a.dump_dir:
            a.dump_dir.mkdir(parents=True,exist_ok=True)
            (a.dump_dir/f"{tag}_header.bin").write_bytes(header)
            (a.dump_dir/f"{ref}_native_shader.bin").write_bytes(payload)
            (a.dump_dir/f"{tag}_gcn_code.bin").write_bytes(code)

        rows.append(row)
        viol.extend(f"{tag}:{x}" for x in row["violations"])

    out={
      "schema":"d1_remote_ps4_shader_binary_probe/v1",
      "status":"D1_REMOTE_PS4_SHADER_BINARY_PROBE_EXACT" if not viol else "D1_REMOTE_PS4_SHADER_BINARY_PROBE_PARTIAL",
      "base_url":base,
      "packages":package_rows,
      "shaders":rows,
      "violations":viol,
      "semantic_boundary":{
        "orbshdr_stage_and_usage":"EXACT_FROM_RETAIL_BYTES",
        "gcn_identity":"EXACT_SHA256",
        "hardware_tessellation_ownership":"WITHHELD",
        "runtime_binding_owner":"WITHHELD",
        "engine_semantic":"WITHHELD"
      }
    }
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps({"status":out["status"],"shaders":[{"tag_hash":r["tag_hash"],"payload_reference":r.get("payload_reference"),"stage":(r.get("binary_info") or {}).get("stage"),"code_sha256":r.get("code_sha256"),"violations":r["violations"]} for r in rows],"violations":viol},indent=2))
    return 0 if not viol else 2


if __name__=="__main__":raise SystemExit(main())
