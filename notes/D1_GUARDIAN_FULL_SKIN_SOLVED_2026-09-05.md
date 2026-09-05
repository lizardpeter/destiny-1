# D1 Guardian full skin solved — 2026-09-05

This note supersedes the older `0x7FFF`-unresolved conclusion in `D1_PLAYABLE_GUARDIAN_BREAKTHROUGH_2026-09-05.md`. It records the byte-validated D1 Rise of Iron Guardian skinning rules and the first complete named five-piece playable Guardian export with exact retail skin weights, skeleton, runtime rig, and animation.

## 1. `0x7FFF` is not a bone and not a cloth sentinel

The D1 ROI vertex decoder establishes three primary-stream skin representations used by Guardian gear:

```text
primary stride 0x0C, position W ordinary nonnegative value != 0x7FFF
    -> rigid one-bone skin
       joint = W
       weight = 255

primary stride 0x0C, position W == +0x7FFF or -0x7FFF
    -> bytes 8..11 are inline skin data
       byte 8  joint0
       byte 9  joint1
       byte 10 weight0
       byte 11 weight1

primary stride 0x10
    -> bytes 8..11  = four U8 weights
       bytes 12..15 = four U8 joint indices
```

The Spektar Pandion meshes have no separate legacy weight resource: `old_weights == FFFFFFFF` throughout, and the model's otherwise-unknown fourth resource is likewise `FFFFFFFF`. The skin information is resident in the primary vertex bytes.

## 2. Exact full-set validation

New reusable decoder/probe:

```text
tools/d1_guardian_inline_skin_probe.py
```

Green validation workflow:

```text
.github/workflows/d1-spektr-pandion-inline-skin-validation.yml
run 33998183972
artifact 9978699756
artifact ZIP SHA-256
d564ddc0ffdfcc5c10de8ea7902abb3c8784c31d851054e44d8126dc66f2176b
```

Masculine five-piece Spektar Pandion source vertices:

```text
vertices                    21,117
rigid one-bone              14,420
inline two-bone              2,804
inline four-bone             3,893
weight-sum failures              0
out-of-range nonzero joints      0
unresolved vertices              0
```

Feminine:

```text
vertices                    21,100
rigid one-bone              14,374
inline two-bone              3,304
inline four-bone             3,422
weight-sum failures              0
out-of-range nonzero joints      0
unresolved vertices              0
```

Every decoded U8 weight tuple was required to sum to 255. Every nonzero joint index was required to fit the 67-node Guardian skeleton. No value was clamped, normalized to hide a malformed source tuple, or guessed.

The Titan Mark is therefore not a separate cloth representation. Its previously all-`0x7FFF` lane is simply weighted skinning encoded in the inline formats. Its joint domain lands on the pelvis/lower-spine chain, anatomically matching a class item hanging from the waist.

## 3. Playable Guardian rig family remains 809D8613 + 809D856E

Independent equipment-attachment anatomy and runtime animation compatibility converge on:

```text
skeleton       809D8613   67 nodes
runtime rig    809D856E   67 controls
component      75F560CA x67
```

Exact matching clips:

```text
809D8469     2 frames
809D846A     2 frames
809D8572   324 frames
```

All three decode and retarget 67 -> 67 -> 67 successfully.

The long clip is selected by control `809D856F`, state hash `13433E07`, with duration scalar ~10.766667 seconds. Its semantic name remains unresolved and is not guessed.

## 4. First complete named rigged animated Guardian

Reusable full-set binder:

```text
tools/d1_guardian_combined_skin_animation.py
```

Green workflow:

```text
.github/workflows/d1-spektr-pandion-full-rigged-animation.yml
run 33998302925
```

Exact masculine Spektar Pandion models:

```text
Gauntlets  80A8274E
Plate      80A85682
Mark       809FDB1E
Helmet     80A816E4
Greaves    80A862BA
```

Validated output:

```text
SPEKTAR_PANDION_TITAN_MASCULINE_FULL_RIGGED_ANIMATED.glb

output bytes                 2,777,740
models                               5
geometry groups / primitives        69
bound exported vertices         22,537
multi-weight exported vertices    4,778
skin joints                          67
runtime-rig controls                 67
animation clip                 809D8572
animation frames                    324
decoded tracks                       67
retargeted tracks                    67
local tracks                         67
animation channels                  201
animation samplers                  201
```

GLB SHA-256:

```text
32bc5021b6783b7e10480576d40072a9400ad1a10e9b275a907384c583e67c88
```

Artifact:

```text
D1-Spektar-Pandion-Titan-Masculine-FULL-RIGGED-ANIMATED
artifact ID 9978726450
artifact ZIP SHA-256
812631626fd3b4ea49441828186f1874206e0548bd8317afebf51800d14dbc8e
```

Every exported primitive is mapped back to its exact retail model/mesh/index range. Skin influences are read from the exact source vertex indices before glTF serialization. The output validator checks that all 69 mesh nodes share the 67-joint skin, every primitive contains `JOINTS_0` and `WEIGHTS_0`, all exported weight rows sum to 1.0, and every nonzero joint is in range.

## 5. Character pipeline status after this closure

The following are now solved for named Guardian equipment:

```text
inventory item -> art arrangement
art arrangement -> masculine/feminine entity branch
entity -> EntityResource -> s_entity_model
cross-package vertex/index resource routing
geometry / triangle topology
D1 Guardian rigid + inline2 + inline4 skin weights
67-node playable Guardian skeleton
67-control compatible runtime rig
exact retail clip decode / retarget / local tracks
multi-piece glTF skin serialization
full five-piece animated character assembly
```

The next character-side frontier is visual fidelity, not structural rigging:

```text
1. exact per-mesh D1 UV-source selection
2. exact per-model texture-plate ownership and composition
3. native material / shader role binding
4. inventory dye-channel / dye-index resolution and shader coloration
```

Important UV caveat: for primary stride `0x0C`, bytes 8..11 are UV data only in the non-inline-skin case. When position W is `±0x7FFF`, those bytes are skin indices/weights instead. UV decoding must therefore follow the D1 stream-pair rules rather than treating every 0x0C primary stream uniformly.

## Evidence policy

No character identity, skin influence, animation semantic, UV source, material role, texture role, or dye color is promoted from adjacency or visual plausibility. Each stage must be backed by a serialized retail relation, source-backed D1 layout, or an independent validation invariant that fails closed.