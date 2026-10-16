#!/usr/bin/env python3
"""Build backend/data/activities.json: what the activity host needs for every activity.

Inputs:
  * the client's activity definitions, as d1-native logs them with D1_DUMP_ACTIVITIES=-1
    ("activities: [<index>] hash <h> tag <t> mm <m> +88='<scenario>'"): definition table at
    0x25A6E0, 0x100-byte entries, +0 activity hash, +0x58 relative string = scenario name,
    +0x88 activity type tag, +0xA4 matchmaking content hash;
  * a named-tag catalog (JSON list of {name, class, tag, pkgs}) of the package named tables;
  * the package directory and an Oodle 3 runtime (see d1_entry_extract.py).

For each scenario name the activity tag (class 0x808008BA, 72 bytes) has its
`:scenario_client` child (class 0x80800616) at +0x40. The scenario tag holds the activity
checksums at +0xC (private instance) and +0x10 (public instance) and the bubble (zone) count
at +0x48; the host's instance state must carry both (0x80800E76 +0x5C / +0x10). The client
compares +0x5C with the checksum of its activity client's kind (0x299B00: +0xC + kind * 4). The child link is used rather than the named entry
`<name>:scenario_client`, which in later package generations can name a reused entry.

Usage: d1_activity_table.py <activities.log> <named.json> <packages dir> <oodle runtime> <out.json>
"""
from __future__ import annotations

import json
import re
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from d1_entry_extract import EntryReader  # noqa: E402
from d1_pkg_probe import parse_header  # noqa: E402

LINE = re.compile(r"activities: \[(\d+)\] hash ([0-9a-f]{8}) tag ([0-9a-f]{8}) mm ([0-9a-f]{8})(?: \+88='([^']*)')?")
GEN = re.compile(r"^(.*)_(\d+)\.pkg$")


def package_index(pkg_dir: Path) -> dict[int, Path]:
    """pkg id -> newest generation file of that package."""
    best: dict[int, tuple[int, Path]] = {}
    for f in pkg_dir.glob("*.pkg"):
        g = GEN.match(f.name)
        if not g:
            continue
        try:
            with f.open("rb") as fh:
                pid = parse_header(fh)["pkg_id"]
        except Exception:
            continue
        if pid not in best or int(g.group(2)) > best[pid][0]:
            best[pid] = (int(g.group(2)), f)
    return {k: v[1] for k, v in best.items()}


def main() -> None:
    log, named_json, pkg_dir, runtime, out = sys.argv[1:6]
    pkg_dir, runtime = Path(pkg_dir), Path(runtime)
    named = {r["name"]: r for r in json.load(open(named_json)) if r["class"] == "808008BA"}
    readers: dict[Path, EntryReader] = {}
    by_id = package_index(pkg_dir)

    def read_tag(tag: int) -> bytes:
        pkg = by_id[(tag - 0x80800000) >> 13]
        rd = readers.get(pkg) or readers.setdefault(pkg, EntryReader(pkg, runtime))
        return rd.entry(tag & 0x1FFF)

    rows = []
    for line in open(log, errors="replace"):
        m = LINE.search(line)
        if not m:
            continue
        idx, h, tag, mm, name = int(m.group(1)), m.group(2), m.group(3), m.group(4), m.group(5)
        row = {"index": idx, "hash": f"0x{h}", "type_tag": f"0x{tag}", "mm_hash": f"0x{mm}", "name": name}
        r = named.get(name or "")
        if r:
            try:
                act = read_tag(int(r["tag"], 16))
                child = struct.unpack_from("<I", act, 0x40)[0]
                sc = read_tag(child)
                row.update(scenario_tag=f"0x{child:08x}", checksum=f"0x{struct.unpack_from('<I', sc, 0xC)[0]:08x}",
                           checksum_public=f"0x{struct.unpack_from('<I', sc, 0x10)[0]:08x}",
                           bubbles=struct.unpack_from("<I", sc, 0x48)[0])
            except Exception as e:  # missing package generation, unreadable block, ...
                row["error"] = str(e)
        rows.append(row)
        print(idx, name, row.get("checksum"), row.get("bubbles"), row.get("error", ""), file=sys.stderr)
    json.dump(rows, open(out, "w"), indent=1)
    ok = sum(1 for r in rows if "checksum" in r)
    print(f"{len(rows)} activities, {ok} with scenario data", file=sys.stderr)


if __name__ == "__main__":
    main()
