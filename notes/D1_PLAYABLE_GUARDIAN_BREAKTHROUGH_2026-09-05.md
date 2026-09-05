# D1 playable Guardian breakthrough — 2026-09-05

This note records the evidence chain that moved the player-character track from generic humanoid candidates to a reusable, named, retail-grounded **Destiny 1 Guardian geometry + rig + animation pipeline**.

It intentionally does not cover Tower/map work.

## 1. Named inventory armor now resolves to concrete retail models

The playable-item join now preserves class and body-role context all the way through:

```text
named inventory item
  -> art arrangement
  -> masculine / feminine assignment
  -> EntityParent
  -> EntityDataROI
  -> final s_entity
  -> EntityResource
  -> embedded s_entity_model
```

Broad census:

```text
named Guardian-class inventory items     2,655
distinct class/art arrangements          2,157
resolved distinct EntityParents          2,637 / 2,653
body branches landing in gear_player     2,431
```

Exact named examples include:

```text
Helm of Saint-14
  feminine  entity 809FCB33 -> model 809FCB35
  masculine entity 80A074C0 -> model 80A074C2

Celestial Nighthawk
  feminine  entity 80A7825B -> model 80A7825D
  masculine entity 80A7B852 -> model 80A7B854

Heart of the Praxic Fire
  feminine  entity 80A03B80 -> model 80A03B83
  masculine entity 80A044CB -> model 80A044CF
```

No body assignment is inferred from package naming; the branch comes from the retail arrangement data.

## 2. First coherent five-piece Guardian assembly

The first full equipment-set proof uses the Titan **Spektar Pandion** set:

```text
arrangement 3867  Spektar Pandion Gauntlets
arrangement 3868  Spektar Pandion Plate
arrangement 3869  Spektar Pandion Mark
arrangement 3870  Spektar Pandion Helmet
arrangement 3871  Spektar Pandion Greaves
```

Masculine exact models:

```text
gauntlets  80A8274E
plate      80A85682
mark       809FDB1E
helmet     80A816E4
greaves    80A862BA
```

Feminine exact models:

```text
gauntlets  80A82B88
plate      80A81F1C
mark       80A79AA7
helmet     80A84024
greaves    80A85E3A
```

A critical exporter correction was required here: real Guardian `s_entity_model` records may reference vertex/index FileHashes in **other package families**. `tools/d1_remote_model_export.py` now resolves those resources through a multi-package logical view instead of assuming local ownership.

Validated masculine combined export:

```text
models             5
geometry groups   69
triangles      28,140
bounds min  [-0.25967538, -0.46870875, -0.00157917]
bounds max  [ 0.42631266,  0.46870875,  1.90124083]
```

Green workflow:

```text
.github/workflows/d1-spektr-pandion-titan-assembly.yml
run 33997300649
```

## 3. Guardian rig identity: 809D8613 + 809D856E

An earlier 70-node two-arm humanoid rig was runtime-valid but failed an anatomical attachment test: named Guardian helmets carry stored rigid joint index `18`, while node 18 on that skeleton is not the head.

The `00EC` bank contains a separate normal two-arm skeleton:

```text
skeleton 809D8613
nodes    67
node 18  b_head
```

A full runtime-rig/clip bank match found exactly one 67-control runtime rig whose component fingerprint matches exact 67-node clips:

```text
runtime rig   809D856E
controls      67
component     75F560CA x67
```

Exact matching clips:

```text
809D8469   2 frames   67 nodes / 67 controls
809D846A   2 frames   67 nodes / 67 controls
809D8572 324 frames   67 nodes / 67 controls
```

Every other scanned runtime rig fails the 67-node dimension requirement for these matches.

All three clips pass the production retarget path:

```text
native control limit   67
decoded tracks          67
retargeted tracks       67
local tracks            67
result                  SUCCESS (3/3)
```

Green workflow:

```text
.github/workflows/d1-guardian-67bone-retarget-validation.yml
```

## 4. Independent render-attachment proof across both body variants

`tools/d1_remote_guardian_joint_probe.py` resolves character vertex streams across package families and applies only the already retail-validated D1 PS4 simple-rigid lane for meshes where `old_weights == FFFFFFFF`.

The five Spektar models produce the following stored joint domains.

Masculine:

```text
Gauntlets [15,17,21,22,27,28,40,42,32767]
Plate     [11,18,32767]
Mark      [32767]
Helmet    [18]
Greaves   [1,3,6,7,9,10,32767]
```

Feminine:

```text
Gauntlets [15,17,21,22,27,28,40,42,32767]
Plate     [11,32767]
Mark      [32767]
Helmet    [18]
Greaves   [1,3,6,7,9,10,32767]
```

Mapping only in-range values onto `809D8613` gives an anatomically coherent and sex-symmetric result:

```text
Helmet
  18  b_head

Plate
  11  b_spine_3
  masculine variant also uses 18 b_head

Greaves
   1  b_pelvis
   3  b_l_thigh
   6  b_l_calf
   7  b_r_calf
   9  b_l_foot
  10  b_r_foot

Gauntlets
  15  b_l_upperarm
  17  b_r_upperarm
  21  b_l_hand
  22  b_r_hand
  40  b_l_ring_1
  42  b_r_index_1
  27/28 are valid skeleton indices whose names are absent from the current public hash dictionary
```

The Mark contains only `0x7FFF` in this lane.

This independent render-attachment evidence converges with the exact runtime-rig/animation evidence. Therefore `809D8613 + 809D856E` is promoted to the **playable Guardian body rig family**.

Caveat retained: the higher-level literal/indexed owner record that explicitly connects the player-entity system to this rig has not yet been recovered. The identity does not rely on such a missing literal because two independent retail evidence axes already converge.

Green anatomical workflow:

```text
.github/workflows/d1-spektr-pandion-joint-skeleton-validation.yml
run 33997824729
```

## 5. Exact animation-control ownership inside the 67-node family

A full readable-payload scan of `00EC` finds:

```text
control 809D8466 (class 80802C0E)
  -> clip 809D8469
  -> clip 809D846A

control 809D856F (class 80802C0E)
  -> clip 809D8572
```

`809D8466` decodes as:

```text
animations  2
states      3

state 6FB760FF  name idle      selects none
state AA1774A7  name unknown   selects 809D8469
state 87EE229C  name unknown   selects 809D846A
```

`809D856F` decodes as:

```text
animations  1
states      1
state 13433E07  name unknown
scalar ~10.766667
selects 809D8572
```

The long state remains intentionally unnamed.

Literal backlinks above the short control reveal two EntityResources:

```text
809D8886 -> 809D8466
809D8887 -> 809D8466
```

Their pointer-class triples are currently unschematized:

```text
809D8886
  unk08  8080080F
  unk10  808020BF
  unk18  808029D2

809D8887
  unk08  8080080F
  unk10  80802B92
  unk18  808020BB
```

No semantic label is assigned to these unknown classes.

## 6. First named Guardian gear exported with a real skin and retail animation

New reusable tool:

```text
tools/d1_gltf_bind_rigid_animation.py
```

It is deliberately limited to a model whose retail joint lane has already been proven to be one uniform rigid joint. It does not infer weights.

First proof target:

```text
Spektar Pandion Helmet, Titan, masculine
final s_entity       80A816E2
EntityResource       80A816E3
s_entity_model       80A816E4
retail joint domain  [18]
```

The exported GLB binds every vertex to:

```text
JOINTS_0  (18,0,0,0)
WEIGHTS_0 (1,0,0,0)
```

using the exact inverse bind matrices from `809D8613`, then serializes the exact retargeted `809D8572` local tracks.

Validated result:

```text
output bytes          1,519,312
model meshes                 10
bound primitives             10
bound vertices            3,483
skin joints                  67
animation frames            324
decoded tracks               67
retargeted tracks            67
local tracks                 67
animation channels          201
rigid joint                  18 = b_head
SHA-256
3edbab7f9058fb8b494fd74f3aac0809987086ae8a76773d90b385dfb967f0ae
```

Green workflow:

```text
.github/workflows/d1-spektr-pandion-helmet-rigged-animation.yml
run 33997907860
artifact 9978610084
```

This is the first current-pipeline **named playable Guardian equipment model with an actual D1 skeleton skin and an exact retail D1 animation**, rather than a static model or unrelated humanoid proof.

## 7. The remaining full-character blocker is now narrow: 0x7FFF

Every ordinary in-range Spektar attachment joint maps correctly to `809D8613`, but some meshes contain stored lane value:

```text
0x7FFF = 32767
```

Key observations:

- it is the sole out-of-range value;
- it appears symmetrically in masculine/feminine variants;
- the Titan Mark uses it exclusively;
- all five exact models still report `old_weights == FFFFFFFF`, so simply looking for the legacy `old_weights` field does not explain it.

Current policy:

> Preserve `0x7FFF` as an unresolved non-skeleton value. Do not assign it to a bone, do not clamp it, and do not synthesize weights.

New forensic tool/workflow:

```text
tools/d1_guardian_vertex_representation_probe.py
.github/workflows/d1-spektr-pandion-7fff-representation-probe.yml
```

The next goal is to identify the exact alternate vertex/cloth/attachment representation associated with these meshes. Once that is decoded, the existing five-piece Spektar assembly can be promoted from static full-body geometry to a complete rigged animated Guardian without fabricating the Mark or sentinel-coded vertices.
