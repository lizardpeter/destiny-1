# D1 Spektar shared glove/collar component and TGXM -> PS4 calibration

Date: 2026-09-06

## Status

The missing-hand investigation is no longer based on visual inference from unused
Spektar gauntlet ranges.  Historical Bungie-compatible GearAsset data identifies a
second geometry component in the exact Spektar Pandion Gauntlets art arrangement,
and archived Bungie renderer source gives that component a direct hand-texture
interpretation.

The retail PS4 counterpart is **not yet identified**.  This note records the proof
boundary and the calibrated cross-platform search rule used to find it.

## Exact historical Spektar Gauntlet arrangement

Exact inventory hash:

- Spektar Pandion Gauntlets: `B4BD27A2` / decimal `3032295330`

Exact historical gear JSON:

- `61fca1fe38acad19b4fba5e88ff8ae17.js`
- serialized `reference_id = 3032295330`

Masculine base art geometry identifiers:

- `750220010-0`
- `984938936-0`

Feminine override art geometry identifiers:

- `938977544-0`
- `984938936-0`

Therefore `984938936-0` is explicitly shared by both body-role arrangements.  It is
not inferred from naming, placement, or geometry similarity.

## Exact shared TGXM

Selected historical mobile geometry file:

- file: `2943ee229ea8c0c44dd610a4dd68ace3.tgxm`
- TGXM v2 `file_identifier`: `984938936-0`
- bytes: `436921`
- SHA-256: `f5e7b2efae7d7737f87997c16dbc36047e0e685bc39f36c311435afc8c47d977`

The exact manifest -> selected TGXM -> TGXM `file_identifier` chain is locked by
workflow run `34038905816`, artifact `9991047167`.

The TGXM has three render meshes.  Its historical target signature is:

| mesh | vertices | raw indices | stage-0 highest parts | highest part raw index counts |
|---:|---:|---:|---:|---|
| 0 | 6921 | 20719 | 5 | `1560, 8670, 9864, 310, 306` |
| 1 | 266 | 473 | 0 | none (`lod_category_23`) |
| 2 | 760 | 1706 | 4 | `610, 607, 25, 61` |

The active stage-0/highest-detail signature is therefore:

- active part-count sequence: **`[5, 4]`**
- active vertex-count sequence: **`[6921, 760]`**

## Why this is specifically relevant to hands/default underlay

The shared TGXM has no plated texture set.  Archived Bungie Spasm therefore falls
through its static-texture fallback.  The preserved source labels that fallback:

```text
// $HACK hard coding static texture indices for hands
```

The exact TGXM static texture metadata includes:

- `1612042359_player_gloves_dif`
- `1612042359_player_gloves_plastic_detail_dif`
- `1612042359_player_gloves_norm`
- `1612042359_player_gloves_plastic_detail_norm`
- `1612042359_player_gloves_scratch`
- `1612042359_collar_diffuse`
- `1612042359_collar_normal`

This establishes that the historical shared component contributes player gloves and
collar/default-underlay content.  It does **not** by itself identify one retail PS4
`s_entity_model` FileHash.

## Why Spektar `80A8274E` ranges `_0` / `_1` are not promoted

The retail PS4 Spektar Gauntlets model `80A8274E` does contain omitted forensic
ranges `_0` and `_1` in the hand/forearm region, and they use forearm/hand joints.
That was initially a reasonable diagnostic candidate.

However, the stronger source chain above proves that the exact inventory art
arrangement includes a separate shared gloves/collar component in addition to the
male-specific Spektar geometry.  The male-specific historical component also has the
same active mesh/part structure as the already selected retail Spektar ranges.  We
therefore keep `_0` / `_1` disabled unless a separate retail rule proves they should
be drawn.  Spatial location or hand-bone weighting is insufficient for promotion.

## Strict cross-platform signature attempt and why it was rejected

The first TGXM -> PS4 structural matcher required raw index-buffer counts and raw
per-part index-count sequences to be identical across historical TGXM and retail
PS4.  Broad scans returned no exact match.

That negative result is **not authoritative**, because a five-pair source-backed
calibration subsequently proved that raw index counts are not cross-platform
invariants.  The published TGXM and retail PS4 representations can preserve the
same model while differing materially in index serialization.

## Five-pair calibration

Calibration workflow:

- run `34041222260`
- artifact `9991725578`
- artifact digest `sha256:9d3139352a911261f13a2cc66049cf5b3134461875910d51fc69905708f72e1d`

Each pair below has independent exact Spektar item/art ownership on the historical
side and independently proven retail PS4 model ownership on the PS4 side.

| exact component | retail PS4 model | active highest-detail parts | TGXM active vertices | PS4 active vertices | delta |
|---|---|---|---|---|---|
| `750220010-0` | `80A8274E` | `[2,4]` | `[1356,3168]` | `[1356,3168]` | `[0,0]` |
| `2595162258-0` | `80A85682` | `[3,3]` | `[657,5115]` | `[657,5113]` | `[0,-2]` |
| `2890974089-0` | `809FDB1E` | `[2,3]` | `[825,1404]` | `[825,1404]` | `[0,0]` |
| `28925197-0` | `80A816E4` | `[4]` | `[3166]` | `[3167]` | `[1]` |
| `3063554348-0` | `80A862BA` | `[2,3,2]` | `[923,1068,2510]` | `[923,1065,2508]` | `[0,-3,-2]` |

All **5/5** exact pairs preserve:

1. ordered stage-0/highest-detail **active mesh** structure;
2. exact ordered highest-detail **part-count sequence**; and
3. active per-mesh vertex counts within **3 vertices**.

Maximum observed absolute vertex delta: **3**.

## Calibrated search rule

The source-calibrated TGXM -> retail PS4 candidate rule is now:

1. Parse the PS4 `s_entity_model` stage boundaries exactly.
2. Drop meshes with zero stage-0/highest-detail parts.
3. Preserve the remaining active mesh order.
4. Require the exact target active highest-detail part-count sequence.
5. Require each active mesh vertex count to be within ±3 of the historical target.
6. Record raw index counts only as corroborating evidence; do not reject on them.
7. Do not require total render-mesh count to match when a historical mesh has no
   active highest-detail draw, because zero-active packaging is not yet calibrated as
   a cross-platform invariant.

For `984938936-0`, the calibrated target is:

```text
active highest-detail part counts = [5, 4]
active vertex counts              = [6921, 760]
vertex tolerance                  = ±3
```

Reusable tools:

- `tools/d1_tgxm_ps4_active_signature_calibrate.py`
- `tools/d1_remote_model_tgxm_active_signature_match.py`

## Current exhaustive search scope

The calibrated scanner is configured to search every currently byte-verified family
from these catalogs:

- `evidence/d1_player_gear_member_catalog.json`
- `evidence/d1_investment_asset_member_catalog.json`
- `evidence/d1_tower_shader_dependency_member_catalog.json` (`00EC`, `00EE`)
- `evidence/d1_tower_00ef_member_catalog.json`

This intentionally includes inventory, player-gear, and race-set families.  The
shared gloves/collar component may be player/default body content rather than a
normal item-local model.

## Promotion boundary

A calibrated signature hit is only a candidate.  Before adding it to a Guardian GLB
we still require:

- decoded geometry/topology agreement with the exact historical component; and
- an exact retail PS4 ownership/composition edge showing how it enters the playable
  Guardian/default-armor assembly.

No candidate will be promoted from naming, visual appearance, neighboring FileHash,
bounds, hand-bone influence, or model adjacency.
