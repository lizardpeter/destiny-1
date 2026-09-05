# D1 weapons + characters continuation — 2026-09-05

This note records the durable state of the parallel **weapons + articulated-character** reverse-engineering track. It intentionally excludes Tower/map work so that the two efforts can proceed independently on `main`.

## Executive result

This pass converted several one-off Gjallarhorn/Vex investigations into reusable, evidence-gated tooling and closed several false paths.

The most important architectural change is that **weapon first-person animation and character animation now use the same committed decode/retarget pipeline**:

```text
s_animation_clip
  -> read_animation
  -> decode_animation
  -> runtime-rig component compatibility
  -> rig_retarget
  -> convert_obj_to_local
  -> local bone tracks
```

Committed generic tool:

```text
tools/d1_animation_retarget_probe.py
```

The bridge currently calls a caller-supplied checkout of the public `SolUnshadowed/tiger-animation-parser`, pinned in CI to:

```text
b9fdc3a43dd28118113275624fcc9054b75855f4
```

This is now reusable project plumbing, but it is **not yet an internal native reimplementation of every D1 animation codec**. Loss-preserving internal reconstruction of the remaining clip schema is still a valid long-term target.

---

## 1. Inventory weapon -> exact pattern-action readiness

New tool:

```text
tools/d1_weapon_action_readiness.py
```

It joins the generic weapon-resolution manifest to the independently resolved pattern-owned action bundles **only by exact `weapon_pattern_index`**.

Latest retail census:

```text
inventory manifests:                    1,414
resolved action patterns:                 208
pattern-action-bundle ready weapons:    1,327
shared + pattern-action ready:               1
full animated-weapon candidate:              1
```

Blockers across the 1,414 inventory manifests:

```text
shared_viewmodel_context_unresolved     1,413
visual_entity_selection_unresolved        277
weapon_pattern_has_no_exact_action_bundle  87
```

So the generic weapon action side is already broad: **1,327 inventory weapons have an exact pattern-owned action bundle**. The dominant bottleneck is no longer pattern-action discovery. It is the unresolved **inventory/pattern -> shared first-person CA profile** selector.

The one complete inventory weapon remains Year-3 Gjallarhorn:

```text
inventory hash       D471D331
weapon pattern       39
pattern carrier      80AAECD6
pattern action ctrl  80AA2DCD
context table        80AADE4C
wrapper              80AA2DDB
shared FP profile    CA2 (independently proven)
```

The readiness tool deliberately does **not** claim that the pattern-owned action control and shared first-person action control are equivalent.

---

## 2. Pattern 39 is not the CA2 selector

A major false path is now closed.

The generic `0x80802C0E` control decoder was extended to support the retail-proven empty selector sentinel:

```text
packed selection 0000FFFF
  count = 0
  start = FFFF
  semantic handling = selects no clips
```

This is required by three CA0 states and is now handled in the production parser rather than a temporary tolerant script.

Using the same decoder on Pattern 39 and all three shared first-person controls gives:

```text
                     animations   states   empty sentinels
Pattern39 80AA2DCD       2           1          0
CA0       80AA3CC2      90          77          3
CA1       80AA3CC5      85          71          0
CA2       80AA3CC9      91          72          0
```

Pattern 39's sole state is:

```text
StringHash   EB22859A
known name   reload_1
scalar       ~3.80000019
selection    00010000
clip         80AA2E4A
```

Exact comparisons against CA0, CA1 and CA2 found:

```text
common action hashes      0
common selected clips     0
matching record indices   0
```

Therefore `80AA2DCD` is a **separate internal-weapon animation layer**, not a reduced CA2-like first-person selector and not a valid path for inferring which CA profile a weapon uses.

Do not derive shared-viewmodel ownership from pattern-action-control similarity.

---

## 3. Shared first-person CA profile selector remains indirect

Known profiles remain:

```text
CA0 owner     80AA3CA0
    rig       80AA3CB2
    skeleton  80AA3CB3
    control   80AA3CC2
    wrapper   80AA3CC4
    context   80AAF413

CA1 owner     80AA3CA1
    rig       80AA3CB8
    skeleton  80AA3CB9
    control   80AA3CC5
    wrapper   80AA3CC7
    context   80AAF416

CA2 owner     80AA3CA2
    rig       80AA3CBE
    skeleton  80AA3CBF
    control   80AA3CC9
    wrapper   80AA3CCB
    context   80AAF419
```

### Exact backlink searches that are now negative evidence

A full readable-payload scan of globals `0151` found **zero aligned literal backlinks** to the CA controls/wrappers, even though the rigs and skeletons have repeated backlinks. No tested weapon-type hash co-serialized with the CA controls/wrappers.

A widened scan of globals `0156/0157` found:

- no source co-serializing a CA profile context with a tested weapon-type hash;
- no direct backlink to CA owner entities `80AA3CA0/1/2`;
- the apparent single backlinks to `80AAF411..419` are self-references, not selector owners.

Byte-diffing the parallel CA context families also rules out a hidden embedded numeric profile discriminator:

```text
80AAF411 / 414 / 417   size 7248
80AAF412 / 415 / 418   size 7136
80AAF413 / 416 / 419   size 1216
```

The triplets are essentially template-identical apart from the expected self/control/wrapper/profile-hash substitutions (plus the CA1-specific companion substitution at the matching slot).

Safe conclusion:

> The actual weapon -> CA0/CA1/CA2 selection is outside these profile resources and is likely an indexed/indirect relation in the weapon/pattern/action graph or another table not yet decoded.

Do **not** hardcode weapon type -> CA profile merely because Gjallarhorn is a rocket launcher and is proven CA2.

---

## 4. Generic articulated-character census

New tool:

```text
tools/d1_character_family_census.py
```

It discovers connected articulated-resource clusters using only byte-validated structures:

- standard model parents and embedded `s_entity_model` hashes;
- decoded D1 skeleton resources;
- runtime-rig class pair `808008B2 -> 8080099B`;
- composition pair `8080079A -> 80800610`;
- `s_animation_clip`;
- `0x8080222A` animation wrappers;
- `0x80802C0E` post/action controls;
- exact aligned local TagHash/FileHash references.

It does **not** promote a component based on package names, adjacency, or matching counts.

### 0767 census

The latest Vex `0767` member contains at least:

```text
model parents                    6
s_entity_model                   6
skeletons                        5
runtime rigs                     3
compositions                     5
s_animation_clip                 5
animation wrapper                1
post/action controls             2
```

The census automatically recovered one fully connected animated articulated cluster:

```text
model parent     816CE0DC
model            816CE1A4
skeleton         816CE0DE   3 nodes
runtime rig      816CE122   3 controls
composition      816CE109
control          816CE10A
clips            816CE113 / 816CE114 / 816CE115
```

Its gameplay semantic identity is still unknown, so it remains an `animated_articulated_entity_candidate` rather than being guessed as a particular Vex body part/archetype.

---

## 5. Exact owner/backlink scanner and the 12-bone Vex bridge

New tool:

```text
tools/d1_character_owner_backlinks.py
```

It scans **every readable entry payload**, not only type-16 structures, for aligned 32-bit target hashes. This was used to attack the missing ownership edge around the known 12-bone Vex fixture:

```text
parent       816CE12B
model        816CE09A
skeleton     816CE092
runtime rig  816CE095
composition  816CE097
component    816CE096
wrapper      816CE099
control      816CE09C
clips        816CE09D / 816CE09E
```

0767 result:

```text
readable entries scanned     588
hit-bearing source records    17
```

The scanner correctly reconstructs literal subclusters, including:

```text
816CE099 + 816CE09C
816CE09A + 816CE12B
816CE09D + 816CE09E
```

and the independently auto-discovered 3-node cluster.

However, **no readable 0767 payload co-serializes the 12-bone model/skeleton/rig/composition/control/clip groups into one literal owner bridge**.

The same 12-bone target hashes also have zero literal backlinks in the scanned `0156/0157` globals.

Safe conclusion:

> The missing 12-bone Vex owner/association bridge is not an obvious aligned literal in the readable 0767/0156/0157 records tested so far. It is likely indirect/indexed or lives in another cross-package owner.

This is a useful narrowing result, not a reason to guess ownership.

---

## 6. Reusable animation retarget pipeline — validated on characters

New generic CLI:

```text
tools/d1_animation_retarget_probe.py
```

### Canonical 12-node Vex fixture

Target:

```text
skeleton 816CE092   12 nodes
rig      816CE095   12 controls
runtime component fingerprint:
    76F7A98E x 12
```

Clip `816CE09D`:

```text
frames                31
nodes                  12
rig controls           12
runtime components     76F7A98E x 12
native control limit   12
decoded tracks         12
retargeted tracks      12
local tracks           12
result                 SUCCESS
```

Clip `816CE09E`:

```text
frames                101
nodes                  12
rig controls           12
runtime components     76F7A98E x 12
native control limit   12
decoded tracks         12
retargeted tracks      12
local tracks           12
result                 SUCCESS
```

This turns the old fixture-specific success into a reusable exact-hash CLI regression.

### Auto-discovered 3-node 0767 cluster

Target:

```text
skeleton 816CE0DE   3 nodes
rig      816CE122   3 controls
runtime component fingerprint:
    44AC69CA x 3
```

All three automatically associated clips validate through the same generic tool:

```text
816CE113   4 frames    native limit 3   local tracks 3   SUCCESS
816CE114  10 frames    native limit 3   local tracks 3   SUCCESS
816CE115  10 frames    native limit 3   local tracks 3   SUCCESS
```

This is especially useful because the cluster was discovered by the generic graph census first and then independently validated at the runtime-rig/clip layer.

---

## 7. The same retargeter now handles the weapon viewmodel path

CA2 validation uses the exact shared first-person pair:

```text
skeleton 80AA3CBF   75 nodes
rig      80AA3CBE   73 controls
runtime component fingerprint:
    D59A5FE6 x 8
    7CB60FEC x 62
    A5D99EA7 x 3
```

Exact CA2 `reload` clip `80AA3D40`:

```text
frames                105
nodes                   75
rig controls            73
native control limit    73
decoded tracks          73
retargeted tracks       75
local tracks            75
result                  SUCCESS
```

Exact CA2 `fire` clip `80AA3D42`:

```text
frames                 19
nodes                   75
rig controls            73
native control limit    73
decoded tracks          73
retargeted tracks       75
local tracks            75
result                  SUCCESS
```

Therefore we no longer need separate animation engines for combatants and weapon viewmodels. The same runtime-component-aware retarget path handles both.

---

## 8. Current shared CA action selections

The generalized `0x80802C0E` decoder currently proves these common named states:

### CA0

```text
idle          record 0   -> 80AA3CD6
ready         record 5   -> 80AA3CDA
reload_empty  record 6   -> 80AA3CDB
reload_full   record 7   -> 80AA3CDB
fire          record 12  -> 80AA3CEC
jump          record 43  -> 80AA3CE2 + 80AA3CE3
```

### CA1

```text
reload_empty  record 0   -> 80AA3D2A
reload_full   record 1   -> 80AA3D2A
fire          record 4   -> 80AA3D2B
idle          record 11  -> 80AA3CD6
ready         record 15  -> 80AA3CDA
jump          record 38  -> 80AA3CE2 + 80AA3CE3
```

### CA2

```text
reload_empty  record 0   -> 80AA3D40
reload_full   record 1   -> 80AA3D40
fire          record 5   -> 80AA3D42
idle          record 13  -> 80AA3CD6
ready         record 14  -> 80AA3CDA
jump          record 39  -> 80AA3CE2 + 80AA3CE3
```

The shared idle/ready/jump clips and profile-specific reload/fire clips are now reusable decoder inputs once a weapon's CA profile is proven.

---

## 9. Current frontier

### Weapons

The high-value unsolved edge is now very specific:

```text
inventory / pattern
      -> ? exact indexed or serialized selector ?
      -> CA0 / CA1 / CA2 shared first-person profile
```

Do not spend more time trying to equate pattern-owned action controls with CA controls; that path is disproven structurally.

Once this selector is decoded, the current 1,327 pattern-action-ready weapons can be promoted through the same generic animation pipeline profile-by-profile.

### Characters

The next scalable target is to run `d1_character_family_census.py` across additional articulated enemy/player package families, then feed any exact skeleton/rig/clip candidates directly into `d1_animation_retarget_probe.py`.

For the known 12-bone Vex body, the remaining graph problem is the indirect/cross-package owner relation tying the independently proven render and animation subclusters together in a generic way.

### Export architecture

The desired reusable path is now:

```text
entity/model owner
  -> geometry/material/texture resolution
  -> exact skeleton
  -> exact runtime rig
  -> exact action/clip selection
  -> d1_animation_retarget_probe-compatible decode/retarget
  -> local tracks
  -> glTF/GLB or native project export
```

The map/Tower extraction track can remain separate and consume the same lower-level package, material and texture decoders without coupling its scene-placement work to this weapon/character graph work.
