#!/usr/bin/env python3
"""Audit local, owner-provided R2 package snapshots for lighting source inputs.

Direct objects use https://r2.houseofkublai.com/destiny/CUSA00219_01.33/packages/<name>.
The output records package identities, current tag classes, sun component timing,
RenderGlobals and exact channel-name joins for the executable atmosphere contract.
No image fidelity or live channel closure is implied by this source census.
"""
import argparse
import hashlib
import json
import struct
from pathlib import Path

from d1_tower_map_entry_chain_resolve import Corpus, dyn_array, u32, i64
from d1_tower_recover_current_corpus import CORE
from d1_tower_recover_activity_root_corpus import MEMBERS


def audit(package_dir, runtime, atmosphere_contract):
    paths = sorted(package_dir.glob("*.pkg"))
    pins = {name: (size, digest) for name, _, size, digest in CORE + MEMBERS}
    packages = []
    for path in paths:
        size = path.stat().st_size
        with path.open("rb") as source:
            digest = hashlib.file_digest(source, "sha256").hexdigest()
        if path.name in pins and (size, digest) != pins[path.name]:
            raise ValueError(f"source package differs from pinned corpus: {path.name}")
        packages.append({"name": path.name, "bytes": size, "sha256": digest,
                         "previously_pinned": path.name in pins,
                         "url": "https://r2.houseofkublai.com/destiny/CUSA00219_01.33/packages/" + path.name})
    corpus = Corpus(paths, runtime)
    rows = []
    errors = []
    defaults = []
    for tag_hash, occurrences in sorted(corpus.occ.items()):
        generation, path, reader, entry = occurrences[0]
        reference = entry["reference"].upper()
        if reference not in ("808009A2", "80801BB0", "80800466"):
            continue
        try:
            raw = reader.entry(entry["index"])
            row = {"hash": tag_hash, "class": reference, "snapshot": path.name,
                   "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
            if reference == "808009A2":
                array = dyn_array(raw, 8, 0x90)
                # Empty retail arrays do not dereference their relative pointer;
                # the importer likewise accepts a nominal target beyond EOF.
                if not array["ok"] and array.get("count") != 0:
                    raise ValueError(array)
                row["sun_components"] = []
                row["light_collections"] = []
                for index in range(array["count"]):
                    field = array["absolute"] + index * 0x90 + 0x88
                    relative = i64(raw, field)
                    target = field + relative
                    if relative and 4 <= target and target + 24 <= len(raw) and u32(raw, target - 4) == 0x80801B13:
                        row["sun_components"].append({"entry": index, "sun_tag": f"{u32(raw, target + 12):08X}",
                            "cycle_seconds": struct.unpack_from("<f", raw, target + 16)[0],
                            "initial_phase": struct.unpack_from("<f", raw, target + 20)[0]})
                    if relative and 4 <= target and target + 16 <= len(raw) and u32(raw, target - 4) == 0x80801BEA:
                        row["light_collections"].append({"entry": index, "collection_hash": f"{u32(raw, target + 12):08X}"})
            elif reference == "80801BB0":
                row["pass_materials"] = {name: f"{u32(raw, offset):08X}" for name, offset in
                    [("composite", 0x1FC), ("sun", 0x45C), ("frame_textures", 0x30), ("global_channel_defaults", 0x34)]}
            else:
                names = dyn_array(raw, 8, 4)
                values = dyn_array(raw, 24, 16)
                if not names["ok"] or not values["ok"] or names["count"] != values["count"]:
                    raise ValueError("channel name/value arrays disagree")
                row["channels"] = [{"index": index, "hash": u32(raw, names["absolute"] + index * 4),
                    "default_vec4": list(struct.unpack_from("<4f", raw, values["absolute"] + index * 16))}
                    for index in range(names["count"])]
                defaults.append(row)
            rows.append(row)
        except Exception as error:
            errors.append({"hash": tag_hash, "class": reference, "error": str(error)})
    globals_rows = [row for row in rows if row["class"] == "80801BB0"]
    joins = []
    if len(globals_rows) == 1:
        source_hash = globals_rows[0]["pass_materials"]["global_channel_defaults"]
        channel_rows = [row for row in defaults if row["hash"] == source_hash]
        if len(channel_rows) == 1:
            for mapping in atmosphere_contract["channel_mappings_before_coefficient_transforms"]:
                matches = [channel for channel in channel_rows[0]["channels"] if channel["hash"] == mapping["hash"]]
                joins.append({**mapping, "global_channel_matches": matches,
                              "status": "EXACT_NAME_JOIN" if len(matches) == 1 else "CHANNEL_ABSENT_OR_AMBIGUOUS"})
    return {"schema": "d1-r2-lighting-source-audit-v1", "packages": packages,
            "current_tag_count": len(corpus.occ), "source_rows": rows, "errors": errors,
            "atmosphere_channel_name_joins": joins,
            "scope": "serialized inputs and executable channel routing; default Vec4s are not claimed as activity live values"}


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--package-dir", type=Path, required=True)
    ap.add_argument("--runtime", type=Path, required=True)
    ap.add_argument("--atmosphere-contract", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    report = audit(args.package_dir, args.runtime, json.loads(args.atmosphere_contract.read_text()))
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"packages": len(report["packages"]), "current_tags": report["current_tag_count"],
                      "source_rows": len(report["source_rows"]), "errors": len(report["errors"]),
                      "atmosphere_joins": len(report["atmosphere_channel_name_joins"])}))
