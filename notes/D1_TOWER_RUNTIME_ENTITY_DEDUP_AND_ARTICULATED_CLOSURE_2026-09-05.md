# D1 Tower runtime entity dedup + articulated closure — 2026-09-05

This note continues `D1_TOWER_DYNAMIC_ENTITIES_PHYSICS_NPC_PIPELINE_2026-09-05.md` and records the next source-backed corrections and reusable tooling.

## 1. Serialized placement references are not identical to runtime world instances

The first complete two-stream Tower Activity placement census produced:

```text
serialized real SMapDataEntry references    1,290
direct Activity map-table references        1,181
F603-collapsed references                     109
unique SEntity owners                         162
unique WorldIDs                             1,215
```

The difference is not random corruption. Parallel Activity/scenario/F603 carriers can serialize the **same WorldID** repeatedly.

A complete comparison of every repeated WorldID showed the repeated records agree on:

- `EntitySK` owner;
- rotation;
- translation;
- DataResource class.

Therefore the pipeline now keeps two explicit views:

1. **serialized-reference view** — loss-preserves every source row and Activity/F603 carrier;
2. **runtime-placement view** — exactly one placement per WorldID, but only after all repeated serializations agree exactly.

Any conflicting serialization for one WorldID fails closed.

Current total:

```text
serialized entity references                1,290
unique runtime WorldIDs                     1,215
duplicate serialized references                75
```

All 75 currently observed duplicates come from the articulated `80C7A9A7` family rather than being distributed across the whole Tower population.

## 2. Articulated population: 102 references are 27 runtime placements

The first model+skeleton census proves ten source-owned articulated SEntity owners:

```text
80C7A05E
80C7A9A7
80C7ADE5
80C7AE14
80C7AE15
80C7AE16
80C7AE17
80C7AE18
80C7AE19
80C7AE1B
```

Their old serialized-reference count was 102, but their actual WorldID population is:

```text
serialized articulated references             102
unique articulated runtime WorldIDs             27
duplicate serialized references                 75
```

Breakdown:

```text
80C7A05E    1 ref    1 WorldID
80C7A9A7   90 refs  15 WorldIDs   <- repeated across 12 F603 carriers
80C7ADE5    1 ref    1 WorldID
80C7AE14    4 refs   4 WorldIDs
80C7AE15    1 ref    1 WorldID
80C7AE16    1 ref    1 WorldID
80C7AE17    1 ref    1 WorldID
80C7AE18    1 ref    1 WorldID
80C7AE19    1 ref    1 WorldID
80C7AE1B    1 ref    1 WorldID
```

`tools/d1_world_articulated_entity_plan.py` now consumes the WorldID-deduplicated runtime view and retains every source serialization as provenance. A scene exporter must use the runtime count, not the serialized-reference count.

## 3. Articulated model / skeleton / rig families

The ten current owners resolve to four visible model identities:

```text
80C7AD2A
80C7A9BE
80C7AF4C
80C7AE59
```

Known ownership examples:

```text
80C7A05E
  model parent    80C7AD28
  model           80C7AD2A
  skeleton        80BC60B2
  runtime rig     80BC60B4

80C7A9A7
  model parent    80C7A9AD
  model           80C7A9BE
  skeleton        80C7A9AE
  recognized runtime-rig pair not yet present in the base corpus

80C7ADE5 / 80C7AE14 / 80C7AE15 / 80C7AE16 / 80C7AE1B
  model parent    80C7AF39
  model           80C7AF4C
  skeleton        80C7AF3A
  runtime rig     80C7AF40

80C7AE17 / 80C7AE18 / 80C7AE19
  model parent    80C7AE31
  model           80C7AE59
  skeleton        80C7AE32
  runtime rig     80C7AE39
```

This is still **articulated-entity evidence**, not proof that every owner is a vendor/NPC/combatant.

## 4. Missing articulated dependencies are highly concentrated

Before recursive package expansion, every articulated owner was missing only a small shared global-resource set:

```text
80AB0301   package 0158
80AAC3DD   package 0156
80AADE40   package 0156
80AACC23   package 0156
```

The unrelated missing `00ec` / `0154` resources belong to non-articulated Tower objects.

Historical verified remote evidence already closes two of these exactly:

```text
80AB0301
  EntityResource / 80800861
  size 736
  +0x10 class 80802465
  +0x18 class 80802955

80AACC23
  EntityResource / 80800861
  size 448
  +0x10 class 80802667
  +0x18 class 808020CE
```

Historical `0156` evidence also pins:

```text
80AADE40
  EntityResource / 80800861
  size 736
  +0x10 class 8080279B
  +0x18 class 80802202
```

A new generic `d1_remote_filehash_probe.py` removes the need for temporary per-resource workflows and is being used to close `80AAC3DD` and revalidate the other shared resources from the current package corpus.

## 5. Correction: 80802465 -> 80802955 is not a Vex/combatant-specific semantic

Earlier Vex work deliberately scoped this pair as an *observed* 0767 combatant component because its universal meaning was not proven.

The evidence is now broader:

- Vex combatant architecture contains the pair;
- Hive combatant architecture contains the pair;
- Cabal and Fallen shared architecture census did not contain it;
- Tower articulated entities reference the global `80AB0301` instance of this same class pair.

Therefore the safe semantic name is now approximately:

```text
unresolved shared articulated/configuration component
class pair 80802465 -> 80802955
```

Do **not** promote the pair itself to `combatant`, `Vex`, or `NPC` semantics.

By contrast, the separately observed pair:

```text
80802397 -> 80802818
```

was present in the Cabal, Fallen, Hive and Vex architecture census and is genuinely cross-race architecture evidence, though its exact semantic name is still unresolved.

## 6. Parent-aware external material selection is source-closed

Charm's D1 EntityModel code proves why character geometry cannot use the map-decal exporter's old external-variant fallback.

For a D1 model-parent EntityResource:

```text
EntityResource / 80800861
  +0x10 -> 80801A80
  +0x18 -> 80801A9C model-parent payload
```

D1 model-parent fields:

```text
+0x15C EntityModel
+0x230 DynamicArray<SExternalMaterialMapEntry>   stride 0x0C
+0x270 DynamicArray<external material>           stride 0x04
```

A model part selects material as:

```text
VariantShaderIndex == -1
  -> inline part Material

VariantShaderIndex >= 0
  -> ExternalMaterialsMap[VariantShaderIndex]
  -> ExternalMaterials[MaterialStartIndex + (0 % MaterialCount)]
```

In current Charm this is the first material in the mapped variant range.

`tools/d1_world_entity_model_material_bindings.py` now reproduces this independently and fails closed on:

- parent/model mismatch;
- invalid variant index;
- empty mapped range;
- external-material index out of bounds;
- missing/non-material selected tag.

This binding manifest must pass before any Tower articulated model is called visually complete.

## 7. Per-placement DataResource is a separate layer

Of the 1,290 serialized placement references:

```text
NULL DataResource       1,259
80802B15                   18
80803450                   12
808028FA                    1
```

The known class is source-defined by Charm:

```text
80802B15 / raw 152B8080 / S152B8080
  +0x10 DynamicArray<S4E2A8080>

S4E2A8080 stride 0x08
  +0x00 TigerHash
  +0x04 StringHash Type
```

Charm comments suggest faction/type-like usage, but the exact semantic is intentionally not strengthened here.

`tools/d1_world_placement_data_resource_census.py` keeps instance DataResource separate from reusable SEntity ownership, decodes only known `S152B8080`, and preserves exact inline prefixes for undocumented `80803450` / `808028FA` resources.

## 8. Generic recursive dependency closure

`tools/d1_expand_world_entity_dependencies.py` now turns dependency closure into reusable D1 infrastructure:

```text
source-owned placed entities
  -> unresolved serialized FileHashes
  -> exact FileHash package-id derivation
  -> recover current physical family for only new package IDs
  -> rerun entity dependency census
  -> repeat until closed or no new package ID exists
```

No package ID is manually supplied by the Tower workflow. `00ec`, `0154`, `0156`, and `0158` are expected first-pass expansions only because the current unresolved hashes derive to those namespaces; the recursive driver can discover further families on later passes.

## 9. GlobalStrings identity route

D1 entity-name resource layouts are source-closed:

```text
generic name discriminator   808013E3
parent                       80801308
parent +0x278 -> name tag    808013F3
name tag +0x0C StringHash

specific name discriminator  8080209B
parent                       80802089
parent +0x114 StringHash
```

`tools/d1_global_strings_resolve.py` follows Charm's D1 `GlobalStrings` implementation:

```text
S50058080 / 80800550
  +0x68 ActivityGlobalStrings
  +0xE8 CharacterNames
    -> SLocalizedStrings / 8080035A
    -> English LocalizedStringsData / 808008BE
    -> StringHash index <-> string-part definition
```

Only hashes emitted by the entity graph are resolved. Collisions remain multiple source-proven candidates.

## 10. New reusable tools in this tranche

```text
d06f9c7a  accept zero-count placement arrays without pointer dereference
9a982be0  recursive D1 world/entity package dependency expansion
8ba4933f  D1 GlobalStrings resolver
709043d6  source-owned articulated entity export plan
c1ed5a39  explicit runtime WorldID dedup view
024ad715  articulated planner consumes unique WorldIDs
4968838a  compatibility alias while preserving runtime placement semantics
e6c65745  parent-aware D1 entity material binding manifest
6bf8eb84  generic remote FileHash payload probe
2e6fae13  per-placement DataResource census
```

## 11. Next gate

The next hard gate is:

```text
recursive dependency expansion closes
  -> exact shared 0156/0158 articulated resources classified
  -> generic/specific entity StringHashes resolved through GlobalStrings
  -> articulated export plan finalized at unique WorldID level
  -> parent-aware material bindings validated
  -> geometry + skeleton + weights exported
  -> runtime-rig / animation ownership resolved
  -> animated world-space character layer produced
```

The existing 543,317,448-byte static/common Tower GLB remains authoritative and is not overwritten during this work.
