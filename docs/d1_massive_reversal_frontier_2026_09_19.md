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

The attenuation-input frontier advanced materially in this run.

Exact current high-detail pair closure:
- color `8108E7A9/8108E7B2 -> PS8108E955`; partners `8108E7AB/8108E7B4 -> PS8108E958`;
- color `8108E7AA/8108E7B3 -> PS8108E956`; partners `8108E7AC/8108E7B5 -> PS8108E959`;
- color `8108E7B1 -> PS8108E953`; partner `809DD1DC -> PS80AAE1CD`.
All ten selected materials retain state-byte0 `0x88`.

Native terminal-alpha backward slicing now separates generic shader capability from selected-material behavior:
- `PS8108E958` generic terminal alpha directly consumes API0 dwords 11,12,13,16,17,23,27,48; API12 dwords 28-30; and sampled lanes t0.x/t1.w/t2.w/t4.w.
- `PS8108E959` generic terminal alpha directly consumes API0 dwords 8,9,15,19; API12 dwords 28-30; and t0.w.
- exact DXT1 block scans prove no transparent-index texels in `8108E951`, `8108E952`, or `80AACF2A`; their sampled alpha domain is exactly `{1}`.
- current `8108E958` partner material constants have m11=1, m12=6, m13=-4.499999523162842, m23=1, m27=0, m48=0. Therefore API12/view-dot influence is algebraically dead, t1.w/t2.w/t4.w are constants 1, and terminal alpha varies only with BC4 `8108E7B6:t0.x`.
- current `8108E959` partner constants have m15=1 and m19=0, while `8108E951:t0.w=1`; terminal alpha therefore reduces exactly to 1.0 and the API12/view-dot branch is dead for these selected materials.
- `PS80AAE1CD` remains exact black RGB / alpha 1.

The old R10 hand-tuned attenuation values were removed. R10 now replays the source-specialized `8108E958` BC4 equation and uses exact alpha=1 inputs for `8108E959` and `80AAE1CD`.

Important remaining boundary: the blend equation is exact, but native pass/render-target ownership and draw order remain WITHHELD. The combined Blender closure is explicitly a portable inspection reconstruction rather than a source-closed framebuffer-order claim.

Serialized geometry provides a new constraint: 14 exact duplicated color/partner geometry instances were found, and every color part is serialized before its matching partner part. This is **not** promoted to draw order. A same-target color->partner execution would erase color for the alpha=1 partner families, so naïve part-array order cannot be assumed to equal final framebuffer order.

## Animation frontier

Crota's exact body path remains source-closed at the resource graph level: physical s_entity `8108E484`, embedded model `8108E5B7`, skeleton resource `8108E4BB` with 50 nodes, runtime rig `8108E4CB`, one selected control `8108E5C0`, and 82 selector-selected clips passing the pinned native decode/retarget/localize path.

This run advanced the executable analysis beyond resource enumeration:
- retargeted clips now retain exact local-space motion variation by target track;
- motion tracks are joined back to exact 50-node skeleton hash/hierarchy identities without inventing anatomical names;
- the runtime rig/control, skin usage, dynamic motion and skeleton hierarchy domains are joined in dedicated censuses;
- state scalar timing is exact at 30 frame-intervals per scalar unit for all single-selection records and the first selected clip of both multi-selection records;
- the two multi-selection records both have scalar 1.0: one selects 31/31-frame clips and one selects 31/41-frame clips, strengthening the exact lead-selection correlation while alternate timing semantics remain withheld;
- frame-event header pointers are source-closed as pointer structures; pointed-to record semantics remain unresolved;
- a new bounded 32-byte event-target prefix census tests aligned word structure and frame-bounded candidate lanes without naming any field.

Next animation frontier: source-close the frame-event target record schema or find independent string/control evidence for behavioral clip labels. Do not infer root-motion or event semantics from numerical patterns alone.

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
