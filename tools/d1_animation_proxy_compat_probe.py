#!/usr/bin/env python3
"""Rank ordinary D1 visible-model candidates for an animation-proxy rig.

This probe intentionally does *not* decode the still-undocumented 0x808008B2
runtime-rig payload layout. Instead it composes binary-validated primitives
already present in this repository:

* EntityResource role decoding (model / skeleton / other)
* D1 skeleton hierarchy and bone-count decoding
* standard model-parent -> s_entity_model ownership
* s_entity_model mesh/part/vertex-buffer decoding
* aligned TagHash backlink/co-occurrence scanning

The target runtime-rig component hash is treated only as a validated 32-bit
fingerprint. Candidate ranking is heuristic evidence, never an ownership
claim: exact entity/model/skeleton parentage must still be proven from bytes.
"""
from __future__ import annotations

import argparse
import json
import struct
import sys
from collections import defaultdict, deque
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from d1_entry_extract import EntryReader, decode_known
from d1_entity_model_probe import D1_ENTITY_MODEL_CLASS, annotate_resources, parse_model
from d1_entity_resource_probe import ENTITY_RESOURCE_CLASS, parse_resource
from d1_skeleton_probe import parse_skeleton_resource

DEFAULT_TARGET_MODEL = "816CE09A"
DEFAULT_TARGET_SKELETON = "816CE092"
DEFAULT_TARGET_RIG = "816CE095"
DEFAULT_COMPONENT_HASH = "76F7A98E"
DEFAULT_BONE_COUNT = 12
DEFAULT_SHARED_HASHES = ["80AADE40", "80AAE3A4", "80AAE10B", "80AAE10C"]


def norm_hash(value: str) -> str:
    value = value.strip().upper().removeprefix("0X")
    if len(value) > 8:
        raise argparse.ArgumentTypeError(f"not a 32-bit hash: {value}")
    try:
        n = int(value, 16)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"not hexadecimal: {value}") from exc
    return f"{n:08X}"


def u32(b: bytes, o: int) -> int:
    return struct.unpack_from("<I", b, o)[0]


def aligned_hash_hits(b: bytes, wanted: set[int]) -> dict[int, list[int]]:
    """Return aligned little-endian dword offsets for wanted 32-bit values."""
    out: dict[int, list[int]] = defaultdict(list)
    end = len(b) - (len(b) % 4)
    for o in range(0, end, 4):
        value = u32(b, o)
        if value in wanted:
            out[value].append(o)
    return dict(out)


def graph_distance(graph: dict[str, set[str]], starts: set[str], goal: str, max_depth: int = 8) -> int | None:
    if goal in starts:
        return 0
    q = deque((s, 0) for s in starts)
    seen = set(starts)
    while q:
        node, depth = q.popleft()
        if depth >= max_depth:
            continue
        for nxt in graph.get(node, ()):
            if nxt == goal:
                return depth + 1
            if nxt in seen:
                continue
            seen.add(nxt)
            q.append((nxt, depth + 1))
    return None


def model_features(r: EntryReader, entry: dict) -> dict:
    b = r.entry(entry["index"])
    model = parse_model(b, r.h["platform"])
    annotate_resources(r, model)
    strides: set[int] = set()
    vertex_counts: set[int] = set()
    variants: set[int] = set()
    inline_materials: set[str] = set()
    part_count = 0
    index_counts: list[int] = []

    for mesh in model["meshes"]:
        part_count += mesh["part_count"]
        for part in mesh["parts"]:
            variants.add(part["variant_shader_index"])
            inline_materials.add(part["material"].upper())
            index_counts.append(part["index_count"])
        for field in ("vertices1", "vertices2", "old_weights"):
            rr = mesh.get("resources", {}).get(field, {})
            if not rr.get("present") or not rr.get("available"):
                continue
            descriptor_entry = r.entries[rr["entry_index"]]
            if descriptor_entry["type"] != 32 or descriptor_entry["subtype"] != 4:
                continue
            decoded = decode_known(descriptor_entry, r.entry(descriptor_entry["index"]), r.h["platform"])
            stride = decoded.get("stride")
            data_size = decoded.get("data_size")
            if isinstance(stride, int) and stride > 0:
                strides.add(stride)
                if isinstance(data_size, int) and data_size % stride == 0:
                    vertex_counts.add(data_size // stride)

    return {
        "mesh_count": model["mesh_count"],
        "part_count": part_count,
        "vertex_buffer_strides": sorted(strides),
        "vertex_count_candidates": sorted(vertex_counts),
        "variant_shader_indices": sorted(variants),
        "inline_materials": sorted(inline_materials),
        "part_index_counts": index_counts,
    }


def analyze_package(path: Path, runtime: Path, args) -> dict:
    r = EntryReader(path, runtime)
    entry_by_hash = {e["tag_hash"].upper(): e for e in r.entries}

    resource_rows: dict[str, dict] = {}
    skeletons: dict[str, dict] = {}
    parents: dict[str, dict] = {}
    models: dict[str, dict] = {}
    structured_payloads: dict[str, bytes] = {}
    errors: list[dict] = []

    # First pass: decode only byte-validated semantic structures.
    for e in r.entries:
        if e["type"] == 16 and e["subtype"] == 0 and r.available(e["index"]):
            try:
                b = r.entry(e["index"])
                structured_payloads[e["tag_hash"].upper()] = b
            except Exception as ex:
                errors.append({"tag_hash": e["tag_hash"], "entry_index": e["index"], "phase": "read_structured", "error": repr(ex)})
                continue

            if e["reference"].upper() == ENTITY_RESOURCE_CLASS:
                try:
                    parsed = parse_resource(b, r.h["platform"])
                    row = {
                        "tag_hash": e["tag_hash"].upper(),
                        "entry_index": e["index"],
                        "size": e["file_size"],
                        "semantic_role": parsed.get("semantic_role"),
                        "unk10_class": parsed.get("unk10", {}).get("class_hash"),
                        "unk18_class": parsed.get("unk18", {}).get("class_hash"),
                        "embedded_model_tag_hash": parsed.get("embedded_model_tag_hash"),
                    }
                    resource_rows[row["tag_hash"]] = row
                    if row["semantic_role"] == "entity_model" and row.get("embedded_model_tag_hash"):
                        parents[row["tag_hash"]] = row
                    if row["semantic_role"] == "entity_skeleton":
                        try:
                            sk = parse_skeleton_resource(b)
                            count = sk["skeleton_info"]["node_hierarchy"]["count"]
                            skeletons[row["tag_hash"]] = {
                                **row,
                                "bone_count": count,
                                "bone_hashes": [x["node_hash"] for x in sk["skeleton_info"].get("bones", [])],
                            }
                        except Exception as ex:
                            errors.append({"tag_hash": e["tag_hash"], "entry_index": e["index"], "phase": "parse_skeleton", "error": repr(ex)})
                except Exception as ex:
                    errors.append({"tag_hash": e["tag_hash"], "entry_index": e["index"], "phase": "parse_entity_resource", "error": repr(ex)})

    # Parse models owned by standard parents. Animation-bundle proxy models that
    # lack a standard parent remain visible in the raw model census but are not
    # candidates for an ordinary visible-model parent ranking.
    for parent_hash, parent in parents.items():
        model_hash = parent["embedded_model_tag_hash"].upper()
        e = entry_by_hash.get(model_hash)
        if not e or e["reference"].upper() != D1_ENTITY_MODEL_CLASS or not r.available(e["index"]):
            parent["model_parse_error"] = "embedded model is absent, unavailable, or not s_entity_model"
            continue
        if model_hash not in models:
            try:
                models[model_hash] = {
                    "tag_hash": model_hash,
                    "entry_index": e["index"],
                    **model_features(r, e),
                }
            except Exception as ex:
                errors.append({"tag_hash": model_hash, "entry_index": e["index"], "phase": "parse_model", "error": repr(ex)})

    # Build a conservative TagHash graph. We scan only values whose identity is
    # known from this package plus explicit target/shared hashes; this avoids
    # treating arbitrary numeric dwords as references.
    explicit = {
        args.target_model,
        args.target_skeleton,
        args.target_rig,
        *args.shared_hash,
    }
    known_hashes = set(entry_by_hash) | explicit | set(parents) | set(models) | set(skeletons)
    wanted_int = {int(x, 16) for x in known_hashes}
    graph: dict[str, set[str]] = defaultdict(set)
    directed_refs: dict[str, set[str]] = defaultdict(set)
    reverse_refs: dict[str, set[str]] = defaultdict(set)
    backlink_rows: list[dict] = []
    component_int = int(args.component_hash, 16)
    component_sources: set[str] = set()

    for src, b in structured_payloads.items():
        hits = aligned_hash_hits(b, wanted_int | {component_int})
        refs: list[dict] = []
        for value, offsets in hits.items():
            h = f"{value:08X}"
            if h == src:
                continue
            if value == component_int:
                component_sources.add(src)
                refs.append({"hash": h, "kind": "component_fingerprint", "offsets": offsets})
                continue
            directed_refs[src].add(h)
            reverse_refs[h].add(src)
            graph[src].add(h)
            graph[h].add(src)
            refs.append({"hash": h, "kind": "tag_hash", "offsets": offsets})
        if refs:
            backlink_rows.append({"source_tag_hash": src, "source_class": entry_by_hash[src]["reference"], "hits": refs})

    compatible_skeletons = {h for h, s in skeletons.items() if s.get("bone_count") == args.bone_count}
    seed_hashes = {
        h for h in [args.target_skeleton, args.target_rig, *args.shared_hash]
        if h in graph or h in entry_by_hash or any(h in graph.get(src, set()) for src in graph)
    }
    seed_hashes |= component_sources

    candidate_rows = []
    for parent_hash, parent in parents.items():
        model_hash = parent["embedded_model_tag_hash"].upper()
        mf = models.get(model_hash, {})
        referrers = sorted(reverse_refs.get(parent_hash, set()))
        model_referrers = sorted(reverse_refs.get(model_hash, set()))
        same_container_compatible_skeletons = []
        same_container_component = []
        same_container_shared: dict[str, list[str]] = defaultdict(list)
        all_containers = set(referrers) | set(model_referrers)
        for src in sorted(all_containers):
            neighbors = directed_refs.get(src, set())
            sk = sorted(neighbors & compatible_skeletons)
            if sk:
                same_container_compatible_skeletons.append({"source": src, "skeletons": sk})
            if src in component_sources:
                same_container_component.append(src)
            for sh in args.shared_hash:
                if sh in neighbors:
                    same_container_shared[sh].append(src)

        distance = graph_distance(graph, seed_hashes, parent_hash) if seed_hashes else None
        score = 0
        evidence = []

        if same_container_compatible_skeletons:
            score += 50
            evidence.append(f"co-referenced with a decoded {args.bone_count}-bone skeleton")
        if same_container_component:
            score += 45
            evidence.append(f"co-occurs with runtime component fingerprint {args.component_hash}")
        if distance is not None:
            score += max(0, 28 - 4 * distance)
            evidence.append(f"graph distance {distance} from target/shared rig seeds")
        shared_count = sum(bool(v) for v in same_container_shared.values())
        if shared_count:
            score += 8 * shared_count
            evidence.append(f"co-referenced with {shared_count} known Vex shared/aux hash(es)")

        variants = set(mf.get("variant_shader_indices", []))
        if {0, 1}.issubset(variants):
            score += 12
            evidence.append("model exposes VariantShaderIndex 0 and 1")
        strides = set(mf.get("vertex_buffer_strides", []))
        if {12, 16}.issubset(strides):
            score += 12
            evidence.append("model uses the target-family 12/16-byte vertex-buffer stride pair")
        mats = set(mf.get("inline_materials", []))
        aux = {"80AAE10B", "80AAE10C"}
        aux_count = len(mats & aux)
        if aux_count:
            score += 10 * aux_count
            evidence.append(f"model contains {aux_count}/2 target auxiliary technique hashes")

        candidate_rows.append({
            "score": score,
            "parent_tag_hash": parent_hash,
            "model_tag_hash": model_hash,
            "parent_entry_index": parent["entry_index"],
            "model_features": mf,
            "parent_referrers": referrers,
            "model_referrers": model_referrers,
            "co_referenced_compatible_skeletons": same_container_compatible_skeletons,
            "co_referenced_component_sources": same_container_component,
            "co_referenced_shared_hashes": dict(sorted(same_container_shared.items())),
            "graph_distance_from_rig_seeds": distance,
            "evidence": evidence,
        })

    candidate_rows.sort(key=lambda x: (-x["score"], x["parent_tag_hash"], x["model_tag_hash"]))

    proxy_entry = entry_by_hash.get(args.target_model)
    target_proxy = None
    if proxy_entry and proxy_entry["reference"].upper() == D1_ENTITY_MODEL_CLASS and r.available(proxy_entry["index"]):
        try:
            target_proxy = {"tag_hash": args.target_model, "entry_index": proxy_entry["index"], **model_features(r, proxy_entry)}
        except Exception as ex:
            errors.append({"tag_hash": args.target_model, "entry_index": proxy_entry["index"], "phase": "parse_target_proxy", "error": repr(ex)})

    return {
        "package": str(r.pkg),
        "platform": r.h["platform"],
        "package_id": r.h["pkg_id"],
        "package_patch_id": r.h["patch_id"],
        "entry_count": len(r.entries),
        "target_proxy_model": target_proxy,
        "component_fingerprint_sources": sorted(component_sources),
        "decoded_skeletons": sorted(skeletons.values(), key=lambda x: x["tag_hash"]),
        "compatible_skeleton_hashes": sorted(compatible_skeletons),
        "standard_model_parent_count": len(parents),
        "candidate_count": len(candidate_rows),
        "candidates": candidate_rows[: args.top],
        "all_candidates": candidate_rows if args.include_all else None,
        "backlinks": backlink_rows if args.include_backlinks else None,
        "errors": errors,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pkg", type=Path, nargs="+", help="one or more package files; sibling patch members are resolved automatically")
    ap.add_argument("--runtime", type=Path, required=True)
    ap.add_argument("--target-model", type=norm_hash, default=DEFAULT_TARGET_MODEL)
    ap.add_argument("--target-skeleton", type=norm_hash, default=DEFAULT_TARGET_SKELETON)
    ap.add_argument("--target-rig", type=norm_hash, default=DEFAULT_TARGET_RIG)
    ap.add_argument("--component-hash", type=norm_hash, default=DEFAULT_COMPONENT_HASH)
    ap.add_argument("--bone-count", type=int, default=DEFAULT_BONE_COUNT)
    ap.add_argument("--shared-hash", type=norm_hash, action="append", default=None,
                    help="known shared Vex/config/aux TagHash seed; repeatable. Defaults to the proven 09A family seeds")
    ap.add_argument("--top", type=int, default=20)
    ap.add_argument("--include-all", action="store_true")
    ap.add_argument("--include-backlinks", action="store_true")
    ap.add_argument("-o", "--output", type=Path)
    args = ap.parse_args()
    if args.shared_hash is None:
        args.shared_hash = list(DEFAULT_SHARED_HASHES)
    if args.top < 1:
        ap.error("--top must be >= 1")
    if args.bone_count < 1:
        ap.error("--bone-count must be >= 1")

    packages = []
    for pkg in args.pkg:
        packages.append(analyze_package(pkg, args.runtime, args))

    report = {
        "purpose": "rank ordinary visible-model candidates compatible with a validated D1 animation-proxy rig without guessing runtime-rig schema offsets",
        "ranking_is_heuristic": True,
        "target": {
            "proxy_model_tag_hash": args.target_model,
            "skeleton_tag_hash": args.target_skeleton,
            "runtime_rig_tag_hash": args.target_rig,
            "runtime_component_fingerprint": args.component_hash,
            "bone_count": args.bone_count,
            "shared_hash_seeds": args.shared_hash,
        },
        "packages": packages,
    }
    text = json.dumps(report, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
        print(f"wrote {args.output}")
    else:
        print(text)


if __name__ == "__main__":
    main()
