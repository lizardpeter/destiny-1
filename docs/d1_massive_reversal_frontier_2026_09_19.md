# D1 massive reversal frontier checkpoint — 2026-09-19

Branch: `d1-crota-source-semantics-v1`

Purpose: keep long reversal runs broad. API10 runtime capture is one blocked frontier, not the whole project. When primary runtime evidence is unavailable, continue source-closed shader/material/animation/geometry work rather than weakening a gate.

## Material / TFX correction that must propagate

Bungie's D1-era GDC shader-system bytecode example is already recorded in `tools/d1_roi_tfx_resource_assignment_prefix_proof.py` and proves that later/community opcode labels cannot be applied blindly to D1 retail streams in this region. The current exact structural closure is:

- repeated PS prefix `49 <texture_index> 47 <destination_code>`;
- across the pinned Xur + three-NPC material checkpoints it covers every independently serialized PS texture entry;
- every observed pair satisfies `destination_code == 0x21 + texture_index`;
- six exact runtime/default holes remain isolated:
  - shader `808768C0`, t2, for material `80876688` in both corpora;
  - shader `808768C0`, t2, for material `808768BB` in both corpora;
  - shader `8087670E`, t4, for material `808766B2`;
  - shader `8087670E`, t4, for material `808766B6`.

Do **not** assign a fallback/default texture to those holes without primary evidence.

The generic `d1_tfx_program_inventory.py` still carries many lineage/community opcode names. Its own comments already withhold semantics in unresolved regions, but future work must distinguish:
1. D1-official identities;
2. retail-corpus structural framing;
3. continued-engine/community lineage names;
4. unknown semantics.

Do not let category 3 silently become category 1.

## 8087670E material frontier

Existing exact work has:
- a physical peer-material census for PS `8087670E`;
- typed closure of a t5 chain including current `80AB04C7`;
- explicit t4 runtime/default holes for `808766B2` and `808766B6`;
- TFX assignment-prefix evidence showing the material program requests those absent serialized slots.

Next productive material transaction: correlate all `8087670E` peers by complete PS texture-index map, sampler record, material-state bytes, TFX tail, and VS pairing. Separate stable shader-family structure from per-material variation. The objective is to constrain t4 by evidence from exact peers without copying a peer resource into a hole unless identity is proven.

## Crota native material frontier

The Blender R10 reconstruction is deliberately not fully source-closed: its node graph names unresolved attenuation terms `D1_PROXY_*`. Keep those proxies visibly separate from exact retail evidence.

Next productive shader/material transaction:
- reopen exact Crota paired color/attenuation PS programs;
- trace each sampled resource index through the corrected D1 assignment-prefix model;
- classify each scalar/color input as exact serialized binding, runtime/default hole, inline/cbuffer value, or unresolved;
- replace a `D1_PROXY_*` factor only when the producer/value is source-closed.

Do not tune constants by appearance and call them solved.

## Animation frontier

Crota's exact body path is already source-closed at the resource graph level: physical s_entity `8108E484`, embedded model `8108E5B7`, skeleton resource `8108E4BB` with 50 nodes, runtime rig `8108E4CB`, plus calibrated animation-owner class pairs and pinned native retarget execution.

Next productive animation transaction:
- move beyond resource enumeration into clip semantics and timing;
- census exact selected clips/control hashes for Crota and structurally comparable Hive actors;
- compare track/bone coverage, frame/sample timing, constant-vs-animated channels, root-motion candidates, and selector/control-state reuse;
- keep behavioral labels withheld unless source strings/script/control evidence establishes them.

## API10 frontier

The runtime gate in `docs/d1_api10_runtime_gate_checkpoint.md` remains fail-closed. Runtime writer, four descriptor dwords, backing allocation, and engine semantic stay WITHHELD absent primary PS4 runtime evidence.

The rare 3/6-load programs are still useful source evidence: exact indexed float4 access topology and later SGPR reuse constrain layout while warning against assigning resource identity from SGPR number alone.

## Long-run policy

A normal `continue` run should pursue multiple connected transactions before stopping:
1. recover/validate newest authoritative branch state and CI;
2. advance one shader/material proof;
3. advance one animation/rig/geometry proof when evidence permits;
4. checkpoint blockers and pivot instead of weakening evidence standards;
5. commit durable tools/proofs/checkpoints, not just prose status.
