# D1 Tower articulated full dependency closure — 2026-09-05

This note supersedes the **partial articulated counts** in the earlier runtime-dedup checkpoint. It does not erase that history: the earlier 10-owner / 27-runtime-placement result was correct for the then-incomplete package graph, but recursive FileHash-driven dependency expansion resolves five additional articulated SEntity owners.

## 1. Authoritative dependency closure

The source-owned Activity placement graph contains:

```text
serialized SMapDataEntry entity references     1,290
unique runtime WorldIDs                        1,215
unique placed SEntity owners                     162
```

Every placed SEntity now resolves completely through its serialized resource list:

```text
parsed SEntity owners                            162 / 162
EntityResource references                        498
unique EntityResources                           334
unresolved EntityResources                         0
unresolved dependency hashes                       0
layout violations                                  0
```

Recursive dependency expansion was driven only by unresolved serialized FileHashes. The first incomplete pass derived exactly these additional package IDs:

```text
00ec
0154
0156
0158
```

After recovering the 24 current physical members from those four families, the next pass reached zero unresolved dependency hashes.

The package names are **not semantic ownership evidence**. They are only physical containers selected after FileHash-to-package-ID derivation.

## 2. Full articulated result

The complete source-owned graph proves:

```text
articulated SEntity owners              15
unique articulated runtime WorldIDs     37
unique articulated model families        7
unique articulated EntityModels          7
unique articulated skeleton resources    7
runtime-rig-bearing families              4
```

The earlier partial checkpoint reported 10 articulated owners and 27 runtime placements. That count is superseded by this complete dependency graph.

No generic/specific EntityName resources occur in the 334 resolved EntityResources. Therefore the absence of SEntity-level names is a real binary result, not a missing-package or classifier failure.

## 3. Seven exact articulated families

### Family A — 4 bones, runtime rig

```text
SEntity        80C7A05E
model parent   80C7AD28
EntityModel    80C7AD2A
skeleton       80BC60B2   4 bones
runtime rig    80BC60B4
runtime count  1
```

WorldID:

```text
592D3113E2C5BDB4
T = [0.433, 130.468, 16.110]
R = [0, 0, -0.7071, 0.7071]
```

### Family B — 1 bone, no proven runtime rig

```text
SEntity        80C7A532
model parent   80CA0D0B
EntityModel    80CA0D19
skeleton       809D8573   1 bone
runtime count  1
```

WorldID `1A02E90A214E971E`, translation `[127.733, 93.543, -9.023]`.

### Family C — 1 bone, repeated scenario serialization

```text
SEntity        80C7A9A7
model parent   80C7A9AD
EntityModel    80C7A9BE
skeleton       80C7A9AE   1 bone
serialized refs 90
runtime WorldIDs 15
```

Each of the 15 runtime objects is serialized six times across parallel Activity/F603 ownership. Those 90 records must therefore produce **15**, not 90, scene instances.

### Family D — 10 bones, no proven runtime rig

```text
SEntity        80C7ABCD
model parent   80C7ABD2
EntityModel    80C7ABDA
skeleton       80AB0BA0   10 bones
runtime count  3
```

### Family E — 67 bones, runtime rig

```text
SEntities      80C7AD82, 80C7AE3E, 80CA0CD6
model parent   80CA0CD8
EntityModel    80CA0CFC
skeleton       809D8613   67 bones
runtime rig    809D856E
runtime count  6
```

This is the largest skeleton in the source-owned Tower articulated set and is the strongest current human/NPC-like candidate by structure alone. That structural observation is **not** a vendor/NPC semantic assignment.

This family also exposes source-owned children resource `809D8566` through `80802663 -> 80802708`.

### Family F — 2 bones, runtime rig

```text
SEntities      80C7ADE5, 80C7AE14, 80C7AE15, 80C7AE16, 80C7AE1B
model parent   80C7AF39
EntityModel    80C7AF4C
skeleton       80C7AF3A   2 bones
runtime rig    80C7AF40
runtime count  8
```

### Family G — 3 bones, runtime rig

```text
SEntities      80C7AE17, 80C7AE18, 80C7AE19
model parent   80C7AE31
EntityModel    80C7AE59
skeleton       80C7AE32   3 bones
runtime rig    80C7AE39
runtime count  3
```

Total runtime count across A–G is 37.

## 4. Shared articulated resources closed

The formerly missing shared resources are now exact:

```text
80AAC3DD  EntityResource  640 bytes  80802397 -> 80802818
80AADE40  EntityResource  752 bytes  8080279B -> 80802202
80AACC23  EntityResource  448 bytes  80802667 -> 808020CE
80AB0301  EntityResource  736 bytes  80802465 -> 80802955
```

The current exact payload proves `80AADE40` is **752 bytes**; older notes that recorded 736 bytes should be treated as superseded physical-generation evidence.

Semantic caution:

- `80802465 -> 80802955` occurs in Hive/Vex enemy architecture and Tower articulated entities, so it is not safely called a Vex/combatant-specific component.
- `80802397 -> 80802818` occurs across Cabal/Fallen/Hive/Vex enemy architecture and Tower articulated entities, so it is a broadly shared articulated/actor-side component, not an enemy-only semantic.

## 5. Names are not in the reusable SEntity owner graph

Charm's D1 mappings used by the project are:

```text
generic name discriminator   808013E3
  parent                     80801308
  name tag class             808013F3

specific name discriminator  8080209B
  parent                     80802089
```

None of the complete Tower EntityResource graph uses these pairs.

This means a Tower vendor/NPC name must come from a higher-level instance/scenario path if present. The new scripted-identity census therefore follows the separate Charm source chain:

```text
SA7058080 / 808005A7
  -> SD9128080 / 808012D9
    -> SD614 type groups
      -> S48138080 ResourcePointer
        -> SMapDataEntry / 80800406
          -> S33138080 / 80801333
             +0x20 EntityName StringHash
```

A scripted name is accepted as runtime placement evidence only if its SMapDataEntry WorldID exists in the independently materialized Activity placement census **and** its EntitySK matches that placement owner.

## 6. Parent-aware materials

Tower articulated models cannot use the map-decal exporter's old inline-material-only shortcut.

Charm's D1 material rule is:

```text
VariantShaderIndex == -1
  -> inline part.Material

VariantShaderIndex >= 0
  -> owning model-parent EntityResource
  -> ExternalMaterialsMap[VariantShaderIndex]
  -> ExternalMaterials[MaterialStartIndex + (0 % MaterialCount)]
```

`tools/d1_world_entity_model_material_bindings.py` validates this independently before geometry export.

## 7. Skinning gate

`tools/d1_world_articulated_skin_census.py` now classifies exact retail skin storage per family.

Only already-proven D1 PS4 forms are decoded:

```text
old_weights == FFFFFFFF, primary stride 0x08
  int16 lane 3 = rigid joint index

old_weights == FFFFFFFF, primary stride 0x0C
  ordinary lane 3 >= 0 = rigid joint
  lane 3 == +/-32767 = 2-weight inline form

old_weights == FFFFFFFF, primary stride 0x10
  bytes 8..11  = four U8 weights
  bytes 12..15 = four U8 joint indices
```

Every weighted vertex must sum to exactly 255 and every nonzero joint index must be within the source-decoded skeleton bone count.

A separate legacy `OldWeights` stream or unknown stride remains an explicit frontier. No influence is fabricated.

## 8. Current validation workflows

```text
.github/workflows/d1-tower-articulated-validation.yml
.github/workflows/d1-tower-scripted-entity-identity.yml
```

The articulated workflow reproduces:

```text
Activity ownership
-> direct/F603 placements
-> recursive SEntity dependency closure
-> GlobalStrings target resolution
-> 7-family articulated plan
-> per-placement DataResource census
-> parent-aware material binding
-> exact skin-storage census
```

The scripted identity workflow independently tests the higher-level WorldID/name path.

## 9. Scene integration policy

The authoritative 543,317,448-byte Tower GLB is not modified yet.

The enriched scene can add articulated objects only after:

1. parent-aware material binding passes;
2. skin storage is either fully decoded or explicitly classified rigid;
3. exact source skeleton bind data is attached;
4. every scene instance comes from a unique runtime WorldID;
5. names, if used, come from script/GlobalStrings evidence rather than appearance.

Only then should the 37 articulated runtime placements be merged into the existing Tower static/common scene.
