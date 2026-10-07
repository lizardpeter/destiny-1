#!/usr/bin/env python3
"""Identify the source-null Venus cookie without guessing a runtime fallback.

Entry identities and source ownership are recovered from owner-provided packages.
The material's runtime activation and null-texture handling remain unclosed.
"""
import argparse
import hashlib
import json
from pathlib import Path
from d1_tower_map_entry_chain_resolve import Corpus, dyn_array, u32


def audit(packages, runtime, source_audit):
    corpus = Corpus(sorted(packages.glob("*.pkg")), runtime)
    def read(h):
        _, path, reader, entry = corpus.occ[h][0]
        data = reader.entry(entry["index"])
        return data, {"hash": h, "package": path.name, "class": entry["reference"],
                      "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
    material_hash = "8100A311"
    raw, identity = read(material_hash)
    array = dyn_array(raw, 0x2B8, 8)
    assert array["ok"]
    textures = [{"register": u32(raw, array["absolute"] + i * 8),
                 "texture_hash": f"{u32(raw, array['absolute'] + i * 8 + 4):08X}"}
                for i in range(array["count"])]
    assert textures == [{"register": 3, "texture_hash": "FFFFFFFF"}]
    owners = []
    for row in source_audit["source_rows"]:
        if "venus_destination" not in row["snapshot"]:
            continue
        for source in row.get("light_collections", []):
            collection, collection_identity = read(source["collection_hash"])
            lights = dyn_array(collection, 0x30, 0x90)
            assert lights["ok"]
            for index in range(lights["count"]):
                at = lights["absolute"] + index * 0x90
                if u32(collection, at + 0x80) == int(material_hash, 16):
                    owners.append({"map_table": row["hash"], "collection": collection_identity,
                                   "record_index": index, "buffer_hash": f"{u32(collection, at + 0x84):08X}",
                                   "flags88_raw": f"{u32(collection, at + 0x88):08X}",
                                   "flags8c_raw": f"{u32(collection, at + 0x8C):08X}"})
    assert len(owners) == 1
    return {"schema": "d1-venus-null-cookie-source-v1", "material": identity,
            "pixel_shader": f"{u32(raw, 0x2A8):08X}", "pixel_textures": textures, "owners": owners,
            "status": "WITHHELD_RUNTIME_NULL_BINDING_NOT_CLOSED",
            "scope": "Serialized source is null, not a missing downloadable texture; no white/black fallback or inactive-record meaning is inferred."}


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--package-dir", type=Path, required=True)
    p.add_argument("--runtime", type=Path, required=True)
    p.add_argument("--source-audit", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    result = audit(args.package_dir, args.runtime, json.loads(args.source_audit.read_text()))
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result["owners"]))
