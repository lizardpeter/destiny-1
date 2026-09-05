#!/usr/bin/env python3
"""Decode and retarget arbitrary D1 ROI animation clips against a target rig.

This promotes the previously fixture-local tiger-animation-parser bridge into a
reusable evidence tool.  It performs the same production sequence already
validated for Vex and shared first-person weapon animations:

    read_animation -> decode_animation -> rig_retarget -> convert_obj_to_local

The caller supplies the retail package containing the resources, exact skeleton
and runtime-rig FileHashes, one or more clip FileHashes, and a checkout of the
pinned public tiger-animation-parser implementation.

The report preserves both sides' runtime-component fingerprints and the native
``calc_control_limit`` result. Successful retargeting proves runtime compatibility
for that concrete clip/rig pair; it does not by itself prove semantic ownership.
"""
from __future__ import annotations

import argparse
import io
import json
import sys
import tempfile
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from d1_entry_extract import EntryReader


def component_rows(xs) -> list[dict]:
    return [
        {"hash": f"{int(x.hash) & 0xFFFFFFFF:08X}", "count": int(x.count)}
        for x in xs
    ]


def common_component_prefix(target: list[dict], clip: list[dict]) -> dict:
    """Pure-Python description of the ordered runtime-component common prefix.

    This mirrors the semantics used by tiger-animation-parser's calc_control_limit
    for reporting/testing purposes; the actual probe still calls the parser's
    native implementation and records that value separately.
    """
    consumed = 0
    matched = []
    stop_reason = "both_exhausted"
    for i in range(max(len(target), len(clip))):
        if i >= len(target):
            stop_reason = "target_exhausted"
            break
        if i >= len(clip):
            stop_reason = "clip_exhausted"
            break
        a, b = target[i], clip[i]
        if a["hash"] != b["hash"]:
            stop_reason = "component_hash_mismatch"
            break
        n = min(int(a["count"]), int(b["count"]))
        consumed += n
        matched.append({
            "index": i,
            "hash": a["hash"],
            "target_count": int(a["count"]),
            "clip_count": int(b["count"]),
            "consumed": n,
        })
        if int(a["count"]) != int(b["count"]):
            stop_reason = "component_count_mismatch"
            break
    else:
        stop_reason = "both_exhausted"
    return {"control_limit": consumed, "matched_components": matched, "stop_reason": stop_reason}


def _entry(reader: EntryReader, tag: str) -> tuple[dict, bytes]:
    wanted = tag.upper()
    for e in reader.entries:
        if e["tag_hash"].upper() == wanted:
            if not reader.available(e["index"]):
                raise RuntimeError(f"{wanted} is not resident/readable in {reader.pkg}")
            return e, reader.entry(e["index"])
    raise KeyError(f"{wanted} is absent from logical package {reader.h['pkg_id']:04X}")


def probe(
    pkg: Path,
    runtime: Path,
    parser_root: Path,
    skeleton_tag: str,
    rig_tag: str,
    clip_tags: list[str],
) -> dict:
    parser_root = parser_root.resolve()
    if not parser_root.exists():
        raise FileNotFoundError(parser_root)
    sys.path.insert(0, str(parser_root))

    from tag.game_version import Game_Version
    from tag_readers.read_skeleton import read_skeleton
    from tag_readers.read_rig import read_runtime_rig
    from tag_readers.read_animation import read_animation
    from animation_decoding.decode_animation import decode_animation
    from runtime_rig.rig_retarget import rig_retarget, calc_control_limit
    from animation_export.convert_animation_object_to_local import convert_obj_to_local

    reader = EntryReader(pkg, runtime)
    version = Game_Version.D1_ROI
    sk_entry, sk_bytes = _entry(reader, skeleton_tag)
    rig_entry, rig_bytes = _entry(reader, rig_tag)
    skeleton = read_skeleton(io.BytesIO(sk_bytes), version)
    rig = read_runtime_rig(io.BytesIO(rig_bytes), version)
    target_components = component_rows(rig.rig_components)

    clips = []
    for clip_tag in clip_tags:
        e, clip_bytes = _entry(reader, clip_tag)
        row = {
            "tag_hash": clip_tag.upper(),
            "entry": {
                "index": e["index"],
                "reference": e["reference"].upper(),
                "type": e["type"],
                "subtype": e["subtype"],
                "size": e["file_size"],
            },
        }
        try:
            with tempfile.NamedTemporaryFile() as f:
                f.write(clip_bytes)
                f.flush()
                f.seek(0)
                animation = read_animation(f, version)
            header = animation.animation_header
            clip_components = component_rows(animation.runtime_rig_components)
            row.update({
                "frame_count": int(header.frame_count),
                "node_count": int(header.node_count),
                "rig_control_count": int(header.rig_control_count),
                "runtime_rig_components": clip_components,
                "component_prefix": common_component_prefix(target_components, clip_components),
                "native_control_limit": int(calc_control_limit(rig, animation.runtime_rig_components)),
                "static_codec": int(animation.static_bones_header.codec_type) if animation.static_bones_header else None,
                "animated_codec": int(animation.animated_bones_header.codec_type) if animation.animated_bones_header else None,
            })
            decoded = decode_animation(animation)
            retargeted = rig_retarget(animation, decoded, skeleton, rig)
            local = convert_obj_to_local(animation, retargeted, skeleton)
            row.update({
                "decoded_track_count": len(decoded),
                "retargeted_track_count": len(retargeted),
                "local_track_count": len(local),
                "success": True,
            })
            if row["native_control_limit"] != row["component_prefix"]["control_limit"]:
                raise RuntimeError(
                    "internal component-prefix report disagrees with native calc_control_limit: "
                    f"{row['component_prefix']['control_limit']} != {row['native_control_limit']}"
                )
        except Exception as ex:
            row.update({
                "success": False,
                "error_type": type(ex).__name__,
                "error": str(ex),
                "trace_tail": traceback.format_exc().splitlines()[-10:],
            })
        clips.append(row)

    return {
        "schema": "d1_animation_retarget_probe/v1",
        "package": str(reader.pkg),
        "platform": reader.h["platform"],
        "package_id": reader.h["pkg_id"],
        "target": {
            "skeleton": skeleton_tag.upper(),
            "skeleton_entry": {
                "index": sk_entry["index"], "reference": sk_entry["reference"].upper(),
                "size": sk_entry["file_size"],
            },
            "skeleton_node_count": len(skeleton.node_defs),
            "runtime_rig": rig_tag.upper(),
            "runtime_rig_entry": {
                "index": rig_entry["index"], "reference": rig_entry["reference"].upper(),
                "size": rig_entry["file_size"],
            },
            "runtime_rig_control_count": len(rig.controls_relations),
            "runtime_rig_components": target_components,
        },
        "clips": clips,
        "summary": {
            "clip_count": len(clips),
            "success_count": sum(1 for x in clips if x.get("success")),
            "failure_count": sum(1 for x in clips if not x.get("success")),
        },
        "policy": (
            "Successful decode/retarget proves runtime compatibility for the supplied concrete clip/rig pair. "
            "It does not establish gameplay semantics or ownership unless a separate serialized/table owner edge is proven."
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pkg", type=Path)
    ap.add_argument("--runtime", type=Path, required=True)
    ap.add_argument("--parser-root", type=Path, required=True)
    ap.add_argument("--skeleton", required=True)
    ap.add_argument("--rig", required=True)
    ap.add_argument("--clip", action="append", required=True)
    ap.add_argument("-o", "--output", type=Path, required=True)
    args = ap.parse_args()

    out = probe(args.pkg, args.runtime, args.parser_root, args.skeleton, args.rig, args.clip)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({"target": out["target"], "summary": out["summary"], "clips": [
        {k: x.get(k) for k in (
            "tag_hash", "frame_count", "node_count", "rig_control_count",
            "runtime_rig_components", "native_control_limit", "decoded_track_count",
            "retargeted_track_count", "local_track_count", "success", "error_type", "error",
        ) if k in x}
        for x in out["clips"]
    ]}, indent=2))
    return 0 if out["summary"]["failure_count"] == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
