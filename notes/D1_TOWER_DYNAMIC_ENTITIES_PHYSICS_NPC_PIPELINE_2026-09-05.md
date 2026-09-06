# D1 Tower dynamic entities / physics / NPC pipeline — 2026-09-05

This note is the durable checkpoint for extending the source-driven Tower reconstruction beyond static geometry into Activity-owned dynamic entities, articulated characters, per-entity physics models, and eventually exact NPC animation/state ownership.

The governing policy is the same as the rest of the D1 reversal: **ownership and semantics must come from serialized/source-backed edges, not package names, adjacency, or visual guesses.**

## 1. Static world baseline remains authoritative

The existing successful Tower visual scene is not replaced by this work until the richer source-driven scene reproduces it and adds the new layers without regression.

Current successful visual baseline:

- 12,438 nodes
- 2,234 meshes
- 499 materials
- 588 textures/images
- 543,317,448-byte GLB
- SHA-256 `3e8ed9febf441204d92c2f65bb1cd3cf564e4b7a050fff3cf944c19b6568f9a1`

Retail visible static placement selection remains:

```text
DetailLevel in {0,1,2,3,10}
and material.Unk08 == 1
```

## 2. Full static Activity ownership is above the old nine-table subset

The Tower static world is now discovered through the D1 Activity ownership graph rather than by supplying the old nine static-render tables:

```text
named SActivity_ROI
  -> BubbleDefinition
  -> MapContainer
  -> SMapDataTable
```

Current source-owned Tower graph:

```text
5 bubbles
17 map containers
122 map-data tables
1,418 map-data rows
```

The historical nine-table / 337-row static-render set is now classified **after** this discovery from serialized resource classes. It is regression evidence, not a discovery input.

## 3. D1 activities are package named/global tags

Charm's D1 package implementation proves that Activity roots are package named/global tags, not ordinary file entries whose `Reference` equals the Activity class.

Named-table layout:

```text
PackageHeader +0xEC  NamedTagTableCount
PackageHeader +0xF0  NamedTagTableOffset
named row stride      0x44
row +0x00             TagHash
row +0x04             TagClassHash
row +0x08             name bytes
```

Important D1 classes:

```text
SActivity_ROI       8080052E   (source schema display 2E058080)
SUnkActivity_ROI    80800616   (source schema display 16068080)
```

The Activity/entity parsers therefore select current activities from current package named-tag tables. The ordinary file-entry Reference of the named TagHash is retained as evidence but is not incorrectly required to equal the named class.

## 4. Dynamic Activity/entity ownership chain is closed

Pinned source:

```text
MontagueM/Charm
50d36ee1f9ecadad7522504c20b1f3f9c97e30af
```

The D1 activity-entity path is:

```text
SUnkActivity_ROI / 80800616
  +0x48 DynamicArray<S0C068080>
    +0x08 DynamicArray<SA8068080>
      +0x34 Tag<SF0088080> / 808008F0
        +0x1C child FileHash
          child arrays +0x08/+0x18/+0x28
            -> S6E078080 / 8080076E
              +0x30 DynamicArray<SE9058080>
                +0x10 SMapDataTable / 808009A2
                +0x18 DynamicArray<S22428080>
                  -> SF6038080 / 808003F6
```

Current exact Tower result after dependency-complete resolution:

```text
current named SUnkActivity_ROI activities      8
resource-parent references                    40
unique resource parents                       35
S6E references                               137
unique S6E resources                          28
real SMapDataTable references                137
null table sentinels                          28
unique real activity map tables               20
F603 references                             3,545
unique F603 resources                         855
unresolved real hashes                          0
layout violations                               0
```

The eight selected current named activities are the serialized scenario/ambient variants for the Tower, including default, Queen, harvest, SRL, Festival of the Lost, Crimson, Chalice, and ambient Tower scenario-client activities. Their names are evidence from the package named-tag table; no filename-only selection is used.

## 5. Both Activity entity streams must be preserved

Charm's D1 Activity map entity view consumes two independent sources of `SMapDataEntry` records:

1. ordinary Activity-owned `SMapDataTable` rows;
2. `F603` entity tables collapsed through `EntityResource.CollapseIntoDataEntry()`.

The second path is:

```text
SF6038080 / 808003F6
  +0x0C EntityResource / 80800861
    +0x10 ResourcePointer -> S2E098080 / 8080092E
    +0x18 ResourcePointer -> SDD078080 / 808007DD
      +0x60 StringPointer DevName
      +0x68 DynamicArray<SMapDataEntry>
```

Charm only collapses the F603 resource when `EntityResource +0x10` resolves to `S2E098080`. This discriminator is implemented literally rather than being inferred from table contents.

D1 `SMapDataEntry` is 0x90 bytes:

```text
+0x00 EntitySK FileHash      <- Charm GetEntityHash() for D1
+0x20 Rotation Vector4
+0x30 Translation Vector4
+0x80 WorldID u64
+0x88 DataResource ResourcePointer
```

`tools/d1_world_activity_entity_resource_census.py` materializes both streams separately and then publishes a unified source-preserving placement set.

## 6. Placed entity is not synonymous with NPC

Each real D1 entity hash is next validated as:

```text
SEntity / 80800734
size 0xA8
+0x20 DynamicArrayUnloaded<S15078080>
S15078080 stride 0x0C
+0x00 FileHash Resource
```

Charm explicitly notes that a D1 SEntity resource-list member can sometimes be a non-entity resource. Therefore the census preserves every resource Reference and only parses members proven to be `EntityResource / 80800861`.

For each proven EntityResource, the source-backed discriminator at `+0x10` is used to classify resource roles. Already validated D1 roles include:

```text
entity model discriminator      80801A80
entity model parent             80801A9C
entity skeleton discriminator   808006BD
entity skeleton info            8080049A
entity physics discriminator    80801A79
entity physics parent           80801BF6
entity children discriminator   80802663
entity children data            80802708
```

An entity is promoted only to an **articulated candidate** when its own source-owned resource set proves model + skeleton. The observed runtime-rig pair `808008B2 -> 8080099B` can strengthen that classification. This still does **not** prove NPC/vendor/gameplay identity.

The dependency census also decodes exact D1 skeleton bone counts and bone hashes for these candidates.

## 7. Per-entity physics is now the strongest collision lead

A broad current Tower census found **zero** Type-27/SubType-0 Havok resources even after adding the Activity package families.

Latest enlarged corpus result:

```text
current entries scanned                  69,285
Type-27/SubType-0 Havok resources             0
SStaticMapData resources                      20
unique SOcclusionBounds                       12
occlusion AABB records                     7,764
finite AABBs                               7,764
ordered XYZ AABBs                          7,764
violations                                    0
```

Therefore:

- the 7,764 AABBs remain **occlusion/visibility evidence**, not collision;
- Activity packages do not reveal a conventional Type-27 Havok collision corpus;
- the next evidence-backed collision path is D1 `entity_physics`.

Charm pins the D1 physics parent to source schema `F61B8080` / canonical `80801BF6`, size 0x840, with `PhysicsModel` at `+0x15C`.

`tools/d1_entity_resource_probe.py` now extracts this exact `embedded_physics_model_tag_hash` in addition to the ordinary visual model hash.

## 8. Reuse the existing articulated/animation pipeline

The Tower NPC work must not create a second incompatible character exporter. Once source-owned articulated Tower entity identities are known, reuse the generic D1 character/animation stack already in the repository:

```text
tools/d1_character_family_census.py
tools/d1_animation_retarget_probe.py
tools/d1_skeleton_probe.py
tools/d1_entity_model_export.py
tools/d1_remote_model_export.py
tools/d1_guardian_combined_skin_animation.py
```

The existing animation bridge is:

```text
s_animation_clip
  -> read_animation
  -> decode_animation
  -> runtime-rig component compatibility
  -> rig_retarget
  -> convert_obj_to_local
  -> local bone tracks
```

That same machinery is already shared by D1 weapon first-person animation and articulated-character work.

## 9. NPC/vendor identity path

Charm's `Entity.Load()` also recognizes separate EntityResource discriminator families for:

- generic entity name;
- specific entity name;
- model;
- skeleton;
- control/rig data;
- physics model;
- children;
- audio.

The Tower pipeline will use the placed-entity EntityResource class-pair census to recover the D1 mappings for the generic/specific-name resources and then resolve their StringHashes through the existing global-string machinery. This allows named Tower vendors/characters to be identified from serialized data instead of filenames or appearance.

Anonymous articulated ambient characters remain anonymous until equivalent identity evidence exists.

## 10. Current committed implementation

Key commits in this dynamic-world tranche:

```text
b61c50f2  Include Tower activity packages in physics census
2968f548  Use pinned Tower activity corpus for entity census
40cdf87f  Enumerate D1 entity activities from named tags
d1cc2563  Separate Tower named roots from entity dependencies
2e9430c0  Resolve Tower entity activity dependencies from full corpus
52ecf6e8  Collapse D1 activity entity resources into placements
ef692290  Materialize Tower activity entity placements
4086fdfa  Materialize direct Tower activity map entries too
32e41c5e  Trace Tower placed entities into D1 resource families
41df98b7  Expose D1 entity physics model ownership
96bdb780  Report Tower entity dependency expansion targets
944f7606  Classify articulated Tower entity candidates
```

## 11. Immediate next closure sequence

The next evidence gates are intentionally ordered:

```text
Activity entity ownership
  -> exact direct + F603 SMapDataEntry placements
  -> SEntity dependency closure
  -> deterministic package-ID expansion for unresolved FileHashes
  -> model/skeleton/physics/children composition
  -> articulated candidate set
  -> generic/specific entity-name resolution
  -> named NPC/vendor vs anonymous articulated classification
  -> model + skeleton + weights export
  -> runtime rig / animation-owner linkage
  -> animation clip/action-state export
  -> world-space placement into Tower scene
```

Only after this chain is closed should the enriched Tower scene incorporate dynamic characters or physics models.
