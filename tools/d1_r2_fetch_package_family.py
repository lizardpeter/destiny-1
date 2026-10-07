#!/usr/bin/env python3
"""Recover exact listed package objects from owner-provided R2, atomically.

Use an anchored --match regex against a local package inventory. Existing files
are reused only when their size agrees with HEAD. This is an acquisition manifest,
not an independent integrity proof; source audit pins should be supplied later.
Requires curl. Never prints credentials or downloads objects outside the inventory.
"""
import argparse
import concurrent.futures
import hashlib
import json
import re
import subprocess
from pathlib import Path

BASE = "https://r2.houseofkublai.com/destiny/CUSA00219_01.33/packages/"


def fetch(name, destination):
    if not re.fullmatch(r"[A-Za-z0-9_]+\.pkg", name):
        raise ValueError("invalid package basename")
    url = BASE + name
    response = subprocess.run(["curl", "-fsSI", "--retry", "2", "--max-time", "30", url],
                              check=True, capture_output=True, text=True)
    lengths = re.findall(r"(?im)^content-length:\s*(\d+)", response.stdout)
    if not lengths:
        raise ValueError(f"{name}: no source object length")
    size = int(lengths[-1])
    path = destination / name
    if not path.is_file() or path.stat().st_size != size:
        partial = path.with_suffix(".pkg.part")
        subprocess.run(["curl", "-fsSL", "--retry", "2", "--max-time", "180", url,
                        "-o", str(partial)], check=True)
        if partial.stat().st_size != size:
            raise ValueError(f"{name}: HEAD/download size disagreement")
        partial.replace(path)
    with path.open("rb") as source:
        digest = hashlib.file_digest(source, "sha256").hexdigest()
    result = {"name": name, "bytes": size, "sha256": digest, "url": url}
    print(json.dumps(result), flush=True)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--match", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()
    names = sorted(set(n for n in args.inventory.read_text().splitlines() if re.fullmatch(args.match, n)))
    if not names:
        raise ValueError("no exact inventory objects matched")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        objects = list(pool.map(lambda name: fetch(name, args.output_dir), names))
    args.manifest.write_text(json.dumps({"schema": "d1-r2-acquisition-manifest-v1", "objects": objects}, indent=2) + "\n")
