#!/usr/bin/env python3
"""Recover the Cosmodrome f32 volume equation that aborted import.

Uses owner-provided exact packages and the shared source reader; no render claim.
The output retains entry hashes and derived arithmetic, not complete asset bytes.
"""
import argparse
import hashlib
import json
import math
import struct
from pathlib import Path
from d1_tower_map_entry_chain_resolve import Corpus, dyn_array, u32


def audit(packages, runtime):
    corpus = Corpus(sorted(packages.glob("*.pkg")), runtime)
    def read(h):
        _, path, reader, entry = corpus.occ[h][0]
        data = reader.entry(entry["index"])
        return data, {"hash": h, "package": path.name, "bytes": len(data),
                      "sha256": hashlib.sha256(data).hexdigest()}
    collection, identity = read("80CEABCE")
    lights = dyn_array(collection, 0x30, 0x90)
    assert lights["ok"] and lights["count"] > 41
    offset = lights["absolute"] + 41 * 0x90
    volume = [list(struct.unpack_from("<4f", collection, offset + 0x20 + r * 16)) for r in range(4)]
    buffer_hash = f"{u32(collection, offset + 0x84):08X}"
    buffer, buffer_identity = read(buffer_hash)
    seeds = dyn_array(buffer, 0x60, 16)
    assert seeds["ok"] and seeds["count"] == 8
    parameters = struct.unpack_from("<4f", buffer, seeds["absolute"] + 16)
    target = [math.tan(parameters[3]), math.tan(parameters[3]), 1.0 / parameters[1], 100.0 / parameters[1]]
    observed = [abs(volume[0][1]), abs(volume[1][2]), volume[3][3] + volume[2][3], volume[3][3] - volume[2][3]]
    equations = []
    for name, a, b in zip(["tan_y", "tan_z", "reciprocal_sum", "reciprocal_difference"], observed, target):
        error = abs(a - b)
        tolerance = max(1e-5, 2 * 2 ** -23 * max(abs(a), abs(b)))
        equations.append({"name": name, "observed": a, "expected": b, "absolute_error": error,
                          "previously_accepted": error <= 1e-5, "f32_rounding_tolerance": tolerance,
                          "accepted": error <= tolerance})
    assert all(e["accepted"] for e in equations)
    assert any(not e["previously_accepted"] for e in equations)
    return {"schema": "d1-light-volume-f32-rounding-v1", "collection": identity,
            "record_index": 41, "buffer": buffer_identity, "source_range": parameters[1],
            "source_angle": parameters[3], "equations": equations,
            "production_commit": "722a9e73a5df49400fd27fadd587d5436239c3ad"}


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--package-dir", type=Path, required=True)
    p.add_argument("--runtime", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    result = audit(args.package_dir, args.runtime)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result["equations"]))
