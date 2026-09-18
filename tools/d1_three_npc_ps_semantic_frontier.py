#!/usr/bin/env python3
"""Build the fail-closed semantic-lifting frontier for the three Tower NPC test actors.

Inputs are exact products only:
- the per-visible-material correctness audit;
- exact bounded native GCN SHA -> semantic-registry matches;
- exact native image-resource usage recovered from CLRX disassembly; and
- the CLRX disassembly itself.

This tool does NOT promote structural similarity to shader semantics.  It ranks
unclosed native programs by visible primitive impact and records exact t# usage and
per-material texture bindings so each remaining program can be lifted deliberately.
"""
from __future__ import annotations

import argparse
import collections
import json
import math
import re
from pathlib import Path

OP_RE = re.compile(r"^\s*(?:/\*[^*]*\*/\s*)?([sv]_[A-Za-z0-9_]+)\b")


def op_hist(text: str) -> collections.Counter[str]:
    out: collections.Counter[str] = collections.Counter()
    for line in text.splitlines():
        m = OP_RE.search(line)
        if m:
            out[m.group(1)] += 1
    return out


def cosine(a: collections.Counter[str], b: collections.Counter[str]) -> float:
    if not a or not b:
        return 0.0
    keys = set(a) | set(b)
    dot = sum(a[k] * b[k] for k in keys)
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    return dot / (na * nb) if na and nb else 0.0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--audit", type=Path, required=True)
    ap.add_argument("--registry-match", type=Path, required=True)
    ap.add_argument("--image-usage", type=Path, required=True)
    ap.add_argument("--disasm-dir", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--markdown", type=Path, required=True)
    a = ap.parse_args()

    audit = json.loads(a.audit.read_text())
    match = json.loads(a.registry_match.read_text())
    usage = json.loads(a.image_usage.read_text())
    assert audit.get("status") == "D1_TOWER_THREE_NPC_MATERIAL_CORRECTNESS_AUDIT_COMPLETE" and not audit.get("violations"), audit
    assert match.get("status") == "D1_TOWER_THREE_NPC_NATIVE_PS_REGISTRY_MATCH_EXACT" and not match.get("violations"), match
    assert usage.get("status") == "D1_GCN_IMAGE_RESOURCE_USAGE_EXACT", usage

    usage_by = {r["shader"].upper(): r for r in usage.get("shaders", [])}
    programs = match["programs"]

    # Preserve exact actor/material rows from the correctness audit, including t# -> texture.
    audit_material = {}
    for actor in audit["actors"]:
        for m in actor["materials"]:
            audit_material[(actor["key"], m["material"])] = m

    groups: dict[str, dict] = {}
    for actor in match["actors"]:
        for m in actor["materials"]:
            sh = m["pixel_shader"].upper()
            p = programs[sh]
            sha = p["gcn_sha256"]
            am = audit_material[(actor["key"], m["material"])]
            g = groups.setdefault(sha, {
                "gcn_sha256": sha,
                "gcn_bytes": int(p["gcn_bytes"]),
                "serialized_ps_headers": set(),
                "native_shader_tags": set(),
                "registry_match": p.get("registry_match"),
                "materials": [],
                "primitive_count": 0,
            })
            # Exact SHA identity requires registry match consistency within a group.
            assert g["registry_match"] == p.get("registry_match"), (sha, g["registry_match"], p.get("registry_match"))
            g["serialized_ps_headers"].add(sh)
            g["native_shader_tags"].add(p["native_shader"])
            g["primitive_count"] += int(m["primitive_count"])
            g["materials"].append({
                "actor": actor["key"],
                "label": actor["label"],
                "material": m["material"],
                "primitive_count": int(m["primitive_count"]),
                "pixel_shader": sh,
                "portable_state": am["portable_state"],
                "exact_ps_bindings": am.get("exact_ps_bindings", []),
            })

    # CLRX disassembly and exact image-resource usage are attached by representative header.
    hist_by_sha: dict[str, collections.Counter[str]] = {}
    for sha, g in groups.items():
        headers = sorted(g["serialized_ps_headers"])
        reps = []
        for sh in headers:
            path = a.disasm_dir / f"PS_{sh}.s"
            assert path.is_file(), path
            h = op_hist(path.read_text(errors="replace"))
            reps.append((sh, path, h))
        # Same bounded GCN SHA must produce the same opcode histogram.
        base = reps[0][2]
        assert all(x[2] == base for x in reps), (sha, [(x[0], x[2]) for x in reps])
        hist_by_sha[sha] = base
        sh = reps[0][0]
        u = usage_by.get(sh)
        assert u is not None, sh
        g["serialized_ps_headers"] = headers
        g["native_shader_tags"] = sorted(g["native_shader_tags"])
        g["material_count"] = len(g["materials"])
        g["actor_count"] = len({x["actor"] for x in g["materials"]})
        g["representative_disassembly"] = str(reps[0][1])
        g["instruction_opcode_histogram"] = dict(base.most_common())
        g["image_usage"] = {
            "image_instruction_count": u["image_instruction_count"],
            "image_opcodes": u["image_opcodes"],
            "used_texture_indices": u["used_texture_indices"],
            "texture_instruction_counts": u["texture_instruction_counts"],
            "sampler_instruction_counts": u["sampler_instruction_counts"],
            "unmatched_image_instruction_count": u["unmatched_image_instruction_count"],
        }
        assert u["unmatched_image_instruction_count"] == 0, (sh, u["unmatched_image_instructions"])

    known = [g for g in groups.values() if g["registry_match"]]
    unmatched = [g for g in groups.values() if not g["registry_match"]]

    # Similarity is only a triage hint. It is never evidence for semantic reuse.
    for g in unmatched:
        h = hist_by_sha[g["gcn_sha256"]]
        sims = []
        for k in known:
            sims.append((cosine(h, hist_by_sha[k["gcn_sha256"]]), k))
        sims.sort(key=lambda x: (-x[0], x[1]["gcn_sha256"]))
        g["non_authoritative_nearest_closed_opcode_shape"] = [
            {
                "cosine": round(score, 6),
                "gcn_sha256": k["gcn_sha256"],
                "semantic_class": k["registry_match"]["semantic_class"],
                "handler": k["registry_match"]["handler"],
            }
            for score, k in sims[:3]
        ]

    unmatched.sort(key=lambda g: (-g["primitive_count"], -g["material_count"], g["gcn_sha256"]))
    for i, g in enumerate(unmatched, 1):
        g["priority_rank"] = i

    # Actor-weighted queue makes it obvious which closure removes the most bad pixels.
    actor_unmatched = collections.Counter()
    for g in unmatched:
        for m in g["materials"]:
            actor_unmatched[m["actor"]] += m["primitive_count"]

    out = {
        "schema_version": 1,
        "status": "D1_TOWER_THREE_NPC_PS_SEMANTIC_FRONTIER_EXACT",
        "visible_unique_gcn_program_count": len(groups),
        "closed_registry_program_count": len(known),
        "unmatched_program_count": len(unmatched),
        "closed_primitive_count": sum(g["primitive_count"] for g in known),
        "unmatched_primitive_count": sum(g["primitive_count"] for g in unmatched),
        "actor_unmatched_primitive_counts": dict(sorted(actor_unmatched.items())),
        "closed_programs": sorted(known, key=lambda g: (-g["primitive_count"], g["gcn_sha256"])),
        "unmatched_priority_queue": unmatched,
        "gates": {
            "all_visible_pixel_shader_programs_semantically_closed": len(unmatched) == 0,
            "heuristic_basecolor_allowed": False,
            "portable_recreation_complete": False,
            "retail_material_permutation_selected": False,
        },
        "policy": (
            "Priority is based on exact visible primitive impact. Native GCN SHA is the only reusable semantic identity. "
            "Opcode-shape similarity is explicitly non-authoritative and may only guide which proof handler to inspect first. "
            "Every material retains its own exact t# texture bindings for subsequent source-closed equation validation."
        ),
        "violations": [],
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=2) + "\n")

    lines = [
        "# Tower three-NPC pixel-shader semantic frontier",
        "",
        f"Status: `{out['status']}`",
        "",
        f"- Unique bounded native PS programs: **{len(groups)}**",
        f"- Already source-closed in registry: **{len(known)}**",
        f"- Still requiring instruction-level semantic lift: **{len(unmatched)}**",
        f"- Visible primitives already covered: **{out['closed_primitive_count']}**",
        f"- Visible primitives still blocked: **{out['unmatched_primitive_count']}**",
        "",
        "## Unmatched priority queue",
        "",
        "| rank | primitives | materials | actors | PS headers | GCN SHA | image ops | used t# |",
        "|---:|---:|---:|---:|---|---|---:|---|",
    ]
    for g in unmatched:
        lines.append(
            f"| {g['priority_rank']} | {g['primitive_count']} | {g['material_count']} | {g['actor_count']} | "
            f"`{','.join(g['serialized_ps_headers'])}` | `{g['gcn_sha256'][:16]}…` | "
            f"{g['image_usage']['image_instruction_count']} | "
            f"`{','.join('t'+str(x) for x in g['image_usage']['used_texture_indices']) or 'none'}` |"
        )
    lines += ["", "## Required proof boundary", "",
              "No entry above is allowed into a correctness material until its native color equation and required inputs are source-closed. "
              "The nearest-closed opcode-shape field in JSON is triage metadata only, not semantic evidence."]
    a.markdown.parent.mkdir(parents=True, exist_ok=True)
    a.markdown.write_text("\n".join(lines) + "\n")

    print(json.dumps({
        "status": out["status"],
        "programs": len(groups),
        "closed": len(known),
        "unmatched": len(unmatched),
        "closed_primitives": out["closed_primitive_count"],
        "unmatched_primitives": out["unmatched_primitive_count"],
        "top5": [(g["priority_rank"], g["primitive_count"], g["serialized_ps_headers"], g["gcn_sha256"][:12]) for g in unmatched[:5]],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
