# D1 global Tag manifest class vs SchemaStruct — 2026-09-05

Status: **binary distinction confirmed; typed-edge validator updated.**

This checkpoint records an important D1 ROI format rule discovered while deriving the Tower map roots from the named Activity rather than supplying map-table hashes manually.

## Named Tower Activity

The current Tower root corpus has one semantic named `SActivity_ROI` TagHash:

```text
80C98019
```

It appears in two current named-tag rows (aliases):

```text
patrol_destination
rise_of_iron_social
```

The `SActivity_ROI` payload is 84 bytes and its source-backed `+0x10 DynamicArray<S0A418080>` is structurally valid with five child-map entries.

The five serialized child TagHashes in the validated payload are:

```text
80C98036
80C98073
80C98140
80C99252
80CA0BD2
```

Their ordinary file-entry References are:

```text
80C98036 -> 8106388B
80C98073 -> 810618B7
80C98140 -> 8106388C
80C99252 -> 81063884
80CA0BD2 -> 81063889
```

The exact D1 `FileHash.PackageId` formula from pinned Charm source derives two shared-manifest package dependencies from those references:

```text
810618B7                         -> package 0430
8106388B / 8C / 84 / 89        -> package 0431
```

Thus `0430/0431` are dependency-plan outputs, not Tower parser inputs.

## S48018080 identity closure

After recovering those two manifest families, every one of the five ordinary References resolves to a current entry of class:

```text
S48018080
project/raw class 80800148
```

Every parent payload has an exact `+0x10` backlink to its original child TagHash. This closes global-Tag identity independently of the child payload schema.

For all five children the parent `+0x0C TagClassHash` is:

```text
80800580
```

However, pinned D1 source declares the serialized field itself as:

```text
SActivity_ROI.Bubbles[]
    -> Tag<SBubbleDefinition>
```

and declares `SBubbleDefinition` with SchemaStruct identifier:

```text
Charm: E0918080
project/raw: 808091E0
```

Therefore **D1 global manifest TagClassHash is not universally identical to the SchemaStruct identifier used to deserialize a source-typed `Tag<T>` target.**

The previous root parser incorrectly equated those two namespaces and rejected all five valid Bubble edges as `80800580 != 808091E0`.

## Correct validation rule

For a pinned source-typed D1 `Tag<T>` edge:

```text
if ordinary file-entry Reference == expected SchemaStruct class:
    accept as class-direct Tag
else:
    ordinary Reference must resolve to S48018080
    S48018080 +0x10 must backlink exactly to the original TagHash
    preserve S48018080 +0x0C TagClassHash as manifest metadata
    use the source field's Tag<T> type as the payload SchemaStruct
    validate the target payload's structural invariants for T
```

The manifest TagClassHash is never discarded; it is simply no longer misused as a mandatory equality check against the SchemaStruct identifier.

## Code split

`tools/d1_tag_manifest_resolver.py` now separates:

- `resolve_manifest_identity()` — validates S48018080 parent and exact child backlink;
- `resolve_tag_class()` — strict TagClassHash equality for cases that genuinely need it;
- `resolve_typed_tag()` — source-typed `Tag<T>` identity + schema validation path.

`tools/d1_world_map_root_census.py` uses `resolve_typed_tag()` for:

```text
Activity -> SBubbleDefinition
SBubbleDefinition -> SMapContainer
SMapContainer -> SMapDataTable
```

The standalone exact TagClassHash scanner is retained only as a conservative diagnostic; it is not authoritative D1 world selection.

## Physical manifest evidence

The 14 physical generations of shared-manifest packages `0430` and `0431` were recovered successfully in workflow run `33999723638`. Their exact split-TAR offsets, sizes and SHA-256 values are pinned in:

```text
evidence/d1_shared_manifest_0430_0431_member_catalog.json
```

That catalog optimizes physical recovery only. The semantic dependency planner must still discover which package IDs are required from serialized Activity child references before selecting catalog families.

## Next invariant

The next binary closure is deliberately stricter than the old class comparison:

```text
80C98019 named SActivity_ROI
  -> 5 typed Bubble edges
  -> valid S48018080 identities/backlinks
  -> SBubbleDefinition payload arrays structurally valid
  -> typed SMapContainer targets structurally valid
  -> typed SMapDataTable targets structurally valid
  -> exact known Tower nine-table set
  -> exact 337 total SMapDataEntry rows
```

Only after that passes should Activity-owned roots be promoted as the authoritative upstream manifest for the already-closed 337-row static/common pipeline.
