#!/usr/bin/env python3
"""Scan current logical D1 package families for exact entry-reference classes.

This is intentionally class-first rather than FileHash-first. It is useful for
versioned singleton/bootstrap assets whose historical FileHash changes between
retail revisions while the schema/reference class may remain stable.

Evidence rules:
* package families are selected explicitly by derived/current package id;
* hits come only from the current logical Tiger entry table reference field;
* payloads are read only after an exact reference-class hit;
* aligned FileHash-looking payload words are reported structurally, not named.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
from pathlib import Path

from d1_investment_arrangement_probe import filehash_pkg_index
from d1_remote_investment_parent_probe import RemoteLogicalPackage, parse_member
from d1_split_tar_extract import SplitHttpTar


def norm(x: str) -> str:
    y=str(x).upper().removeprefix("0X").zfill(8)
    int(y,16)
    return y


def current_family_names(package_list: Path, pkgid: int) -> list[str]:
    token=f"{pkgid:04x}"
    out=[]
    for line in package_list.read_text(errors="replace").splitlines():
        name=Path(line.strip()).name
        if re.search(rf"_{token}_[0-9]+\.pkg$",name,re.I):
            out.append(name)
    return sorted(set(out))


def build_view(arc, package_list: Path, runtime: Path, pkgid: int) -> tuple[RemoteLogicalPackage|None,dict]:
    names=current_family_names(package_list,pkgid)
    row={"package_id":f"{pkgid:04X}","members":names,"violations":[]}
    if not names:
        row["violations"].append("package_family_absent")
        return None,row
    found,headers=arc.find(set(names))
    row["tar_headers_scanned"]=headers
    missing=sorted(set(names)-set(found))
    if missing:
        row["violations"].append("archive_members_missing:"+",".join(missing))
        return None,row
    specs=[]
    row["member_locations"]={}
    for name in names:
        loc=found[name]
        row["member_locations"][name]=loc
        specs.append(parse_member(f"{name}:0x{int(loc['data_offset']):X}:{int(loc['size'])}"))
    view=RemoteLogicalPackage(arc,{m.patch_id:m for m in specs},runtime)
    row["logical_view"]=view.view.name
    row["entry_count"]=len(view.entries)
    row["block_count"]=len(view.blocks)
    return view,row


def resolved_words(payload: bytes, views: dict[int,RemoteLogicalPackage]) -> list[dict]:
    out=[]
    for off in range(0,len(payload)-(len(payload)%4),4):
        value=struct.unpack_from("<I",payload,off)[0]
        pkg,idx=filehash_pkg_index(value)
        view=views.get(pkg)
        if view is None or idx>=len(view.entries):
            continue
        e=view.entries[idx]
        if int(e["tag_hash"],16)!=value:
            continue
        out.append({
            "offset":off,"offset_hex":f"0x{off:X}","tag_hash":f"{value:08X}",
            "reference":e["reference"].upper(),"type":e["type"],
            "subtype":e["subtype"],"size":e["file_size"],
        })
    return out


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--package-id",action="append",required=True,type=lambda x:int(x,0))
    ap.add_argument(
        "--reference",
        action="append",
        required=True,
        help=(
            "parsed little-endian u32 FileEntry.Reference, e.g. serialized "
            "source bytes B01B8080 are passed as 80801BB0"
        ),
    )
    ap.add_argument("--package-list",type=Path,required=True)
    ap.add_argument("--runtime",type=Path,required=True)
    ap.add_argument("--base-url",default="https://crypt.cohae.dev/destiny/ps4/packages/latest")
    ap.add_argument("--part-count",type=int,default=10)
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()

    wanted={norm(x) for x in args.reference}
    base=args.base_url.rstrip("/")
    arc=SplitHttpTar([f"{base}/packages.tar.{i:03d}" for i in range(1,args.part_count+1)],retries=6,timeout=120)

    views={}
    packages=[]
    for pkg in sorted(set(args.package_id)):
        try:
            view,row=build_view(arc,args.package_list,args.runtime,pkg)
        except Exception as ex:
            view=None
            row={"package_id":f"{pkg:04X}","members":current_family_names(args.package_list,pkg),
                 "violations":["logical_package_build:"+repr(ex)]}
        packages.append(row)
        if view is not None:
            views[pkg]=view

    hits=[]
    for pkg,view in views.items():
        for e in view.entries:
            ref=e["reference"].upper()
            if ref not in wanted:
                continue
            row={
                "package_id":f"{pkg:04X}","entry_index":e["index"],
                "tag_hash":e["tag_hash"].upper(),"reference":ref,
                "type":e["type"],"subtype":e["subtype"],"declared_size":e["file_size"],
                "available":False,"violations":[],
            }
            try:
                payload=view.entry(e["index"])
                row["available"]=True
                row["payload_size"]=len(payload)
                row["payload_sha256"]=hashlib.sha256(payload).hexdigest()
                row["prefix256"]=payload[:256].hex()
                row["aligned_resolved_tag_matches"]=resolved_words(payload,views)
            except Exception as ex:
                # RemoteLogicalPackage no longer exposes a separate availability
                # predicate. Exact readability is established by the same
                # class-stable block resolver used for the payload itself.
                row["violations"].append("payload_read:"+repr(ex))
            hits.append(row)

    violations=[f"{p['package_id']}:{v}" for p in packages for v in p.get("violations",[])]
    violations += [f"{h['tag_hash']}:{v}" for h in hits for v in h.get("violations",[])]
    report={
        "schema":"d1_remote_entry_reference_class_scan/v1",
        "status":"D1_ENTRY_REFERENCE_CLASS_SCAN_COMPLETE" if not violations else "D1_ENTRY_REFERENCE_CLASS_SCAN_PARTIAL",
        "references":sorted(wanted),
        "package_ids":[f"{x:04X}" for x in sorted(set(args.package_id))],
        "packages":packages,
        "hit_count":len(hits),
        "hits":hits,
        "violations":violations,
        "policy":"Hits are exact current logical entry-table reference matches. Payload offsets and resolved FileHashes are structural evidence only; no singleton/schema field meaning is assigned by this scanner.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({
        "status":report["status"],"references":report["references"],
        "packages":[{"package_id":p["package_id"],"entry_count":p.get("entry_count"),"violations":p.get("violations")} for p in packages],
        "hit_count":len(hits),
        "hits":[{"package_id":h["package_id"],"tag_hash":h["tag_hash"],"reference":h["reference"],"size":h["declared_size"],"available":h["available"],"resolved":h.get("aligned_resolved_tag_matches",[])} for h in hits],
        "violations":violations,
    },indent=2))
    return 0 if not violations else 2


if __name__=="__main__":
    raise SystemExit(main())
