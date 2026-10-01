#!/usr/bin/env python3
"""Join exact D1 Tower sequencer channel IDs to the exact global defaults table.

This closes the local/global index distinction:
  SD1918080.ChannelIndex -> sequencer-local Array3 ID StringHash
  StringHash -> ordered GlobalChannelDefaults row
  ordered row index -> raw RoI TFX 0x4B operand domain

No human-facing channel names are assigned here.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

REQUESTED={0x11,0x28,0x30,0x60}

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--defaults",type=Path,required=True)
    ap.add_argument("--tower-census",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()

    defaults=json.loads(a.defaults.read_text())
    tower=json.loads(a.tower_census.read_text())

    rows=defaults.get("channels",[])
    by_hash=defaultdict(list)
    for r in rows:
        by_hash[str(r["string_hash"]).upper()].append(r)

    joins=[]
    unmatched=[]
    ambiguous=[]
    for parent in tower.get("global_channel_parents",[]):
        resource_hash=parent.get("resource_hash")
        owners=parent.get("owners",[])
        for p in parent.get("decoded",{}).get("programs",[]):
            h=p.get("channel_id_string_hash")
            if h is None:
                unmatched.append({
                    "resource_hash":resource_hash,
                    "local_channel_index":p.get("local_channel_index",p.get("channel_index")),
                    "reason":"local_channel_id_missing",
                })
                continue
            matches=by_hash.get(str(h).upper(),[])
            if not matches:
                unmatched.append({
                    "resource_hash":resource_hash,
                    "local_channel_index":p.get("local_channel_index",p.get("channel_index")),
                    "channel_id_string_hash":str(h).upper(),
                    "reason":"string_hash_absent_from_global_defaults",
                })
                continue
            if len(matches)!=1:
                ambiguous.append({
                    "resource_hash":resource_hash,
                    "local_channel_index":p.get("local_channel_index",p.get("channel_index")),
                    "channel_id_string_hash":str(h).upper(),
                    "global_matches":matches,
                })
                continue
            g=matches[0]
            gi=int(g["index"])
            joins.append({
                "resource_hash":resource_hash,
                "owners":owners,
                "source_program_array":p.get("source_program_array"),
                "local_channel_index":p.get("local_channel_index",p.get("channel_index")),
                "local_channel_index_hex":p.get("local_channel_index_hex",p.get("channel_index_hex")),
                "channel_id_string_hash":str(h).upper(),
                "global_index":gi,
                "global_index_hex":f"0x{gi:02X}",
                "global_default_vec4":g.get("default_vec4"),
                "requested_by_tower_light_0x4b":gi in REQUESTED,
                "bytecode_hex":p.get("bytecode_hex"),
                "bytecode_sha256":p.get("bytecode_sha256"),
                "constant_vec4s":p.get("constant_vec4s",[]),
                "lineage_dynamic_rule":p.get("is_dynamic_lineage_rule"),
                "entry_offset_hex":p.get("entry_offset_hex"),
            })

    requested=[j for j in joins if j["requested_by_tower_light_0x4b"]]
    by_requested={f"0x{x:02X}":[j for j in requested if j["global_index"]==x] for x in sorted(REQUESTED)}
    missing=[k for k,v in by_requested.items() if not v]
    default_only_candidates = {
        k: next(
            (
                row for row in rows
                if int(row["index"]) == int(k, 16)
            ),
            None,
        )
        for k in missing
    }

    out={
        "schema":"d1_tower_global_channel_exact_join/v1",
        "status":"D1_TOWER_GLOBAL_CHANNEL_JOIN_COMPLETE" if not unmatched and not ambiguous else "D1_TOWER_GLOBAL_CHANNEL_JOIN_PARTIAL",
        "global_defaults_tag_hash":defaults.get("tag_hash"),
        "global_channel_count":defaults.get("layout",{}).get("channel_count"),
        "tower_parent_count":len(tower.get("global_channel_parents",[])),
        "joined_program_count":len(joins),
        "unmatched_program_count":len(unmatched),
        "ambiguous_program_count":len(ambiguous),
        "requested_global_indices":[f"0x{x:02X}" for x in sorted(REQUESTED)],
        "requested_global_programs":by_requested,
        "requested_global_indices_without_tower_program":missing,
        "requested_default_only_candidates":default_only_candidates,
        "joins":joins,
        "unmatched":unmatched,
        "ambiguous":ambiguous,
        "proof_boundary":(
            "The join uses exact StringHash identity between sequencer-local Array3 IDs "
            "and exact ordered GlobalChannelDefaults rows. This closes local->global "
            "index mapping. A requested index without a Tower program is retained as an "
            "exact default-only candidate, not treated as an error. This does not prove "
            "that no other runtime system can update it, nor assign a human-facing semantic name."
        ),
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps({
        "status":out["status"],
        "joined_program_count":len(joins),
        "requested_counts":{k:len(v) for k,v in by_requested.items()},
        "missing_requested":missing,
        "unmatched_program_count":len(unmatched),
        "ambiguous_program_count":len(ambiguous),
    },indent=2))
    return 0 if not unmatched and not ambiguous else 2

if __name__=="__main__":
    raise SystemExit(main())
