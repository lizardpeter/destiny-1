# D1 Tower map-data resource closure

Status: **binary-closed table framing and ownership population; baked/common subtype regression now automated.**

This note records the map-data layer immediately above the already-solved baked-static tables. It exists specifically to prevent two regressions that occurred during reconstruction: swapping the D1 `DynamicArray` count/pointer fields, and mistaking the serialized resource sidecar for a larger `SMapDataEntry` stride.

## Exact D1 `SMapDataTable` framing

Pinned source class: `808009A2` (`A2098080` in the byte-order-normalized Charm schema).

The D1 table payload contains a `DynamicArray<SMapDataEntry>` descriptor at `+0x08`:

```text
+0x08  i32 count
+0x0C  u32 unknown (Tower: 0)
+0x10  i64 RelativePointer
```

Charm `RelativePointer` is based at the pointer field, then `DynamicArray` adds an extra `0x10`. For all nine current Tower tables:

```text
relative = 0x10
array absolute = 0x08 + 0x08 + 0x10 + 0x10 = 0x30
```

The D1 `SMapDataEntry` is exactly **0x90 bytes**. The fields used by the world pipeline are:

```text
+0x00  entity TagHash
+0x20  float4 rotation
+0x30  float4 translation
+0x80  u64 WorldID
+0x88  ResourcePointer
```

Tower current-byte census:

- **9** `SMapDataTable` resources;
- **337 / 337** rows parsed at 0x90 stride;
- **337 / 337** finite outer transforms;
- all outer rotations `[0,0,0,1]`;
- all outer translations `[0,0,0,1]`;
- all entity hashes `80AADDFD`;
- all WorldIDs `FFFFFFFFFFFFFFFF`;
- **337 / 337** non-null ResourcePointers;
- **337 / 337** resource classes `80801AEA` (`SMapDataResource`);
- **0** table-framing violations.

Per-table row counts:

```text
80C98028   39
80C984A0   14
80C9895C   79
80C989F7  112
80C997DF    4
80C99956   22
80CA0B0E   10
80CA0B11   54
80CA0C4E    3
-----------
TOTAL      337
```

## The 0x18-per-entry resource sidecar

The 0x90 entry array is followed by serialized resource data. In every current Tower table the bytes after the array are exactly:

```text
tail_bytes = count * 0x18
```

The first resource-class hash starts at `array_end + 0x04`, resource-class hashes advance by exactly `0x18`, and the final known resource field frontier reaches the exact payload end.

This produces a tempting whole-payload identity:

```text
payload_size = 0x30 + count * 0xA8
```

but **0xA8 is not an `SMapDataEntry` stride**. It is merely:

```text
0xA8 = 0x90 entry + 0x18 serialized sidecar allocation per row
```

Any parser that steps entries at 0xA8 is wrong.

## Parent and `SStaticMapData` ownership closure

Every `80801AEA` resource points at `+0x0C` to a current `80801AC6` `SStaticMapParent`. The parent points at `+0x08` to `808008B4` `SStaticMapData`.

Current Tower population:

- **337** map rows;
- **337** distinct `SStaticMapParent` resources;
- **19** unique `SStaticMapData` resources.

The 19 resources divide cleanly into two source-backed families rather than one homogeneous baked-static family:

- **10** baked-static carriers with direct `+0x30 -> 80801B75` D1 static-data children;
- **9** large/common carriers whose `+0x30` direct D1 child is absent (`FFFFFFFF` in the observed common-carrier cases).

The 10 baked carriers each occur exactly once:

```text
80C98254
80C984D8
80C98A6B
80C993CD
80C993CF
80C997F5
80C99981
80CA0B70
80CA0B72
80CA0C60
```

The nine common carriers account for the other **327** map rows:

```text
80C98028 -> 80C98191 x 38   + baked 80C98254 x 1
80C984A0 -> 80C984D7 x 13   + baked 80C984D8 x 1
80C9895C -> 80C98A69 x 78   + baked 80C98A6B x 1
80C989F7 -> 80C993A2 x110   + baked 80C993CD x 1 + 80C993CF x 1
80C997DF -> 80C997F4 x  3   + baked 80C997F5 x 1
80C99956 -> 80C99980 x 21   + baked 80C99981 x 1
80CA0B0E -> 80CA0B6F x  9   + baked 80CA0B70 x 1
80CA0B11 -> 80CA0B71 x 53   + baked 80CA0B72 x 1
80CA0C4E -> 80CA0C5F x  2   + baked 80CA0C60 x 1
```

This exactly explains the existing common-layer source behavior: the repeated common carrier is not another baked cell. It contains the table-scoped embedded model/decal records and is loaded once per table for that layer. Repeating it once per parent row creates the known false 23,141-placement explosion.

## Baked/common classification rule

Ownership closes at `SStaticMapData`. A missing direct `80801B75` child is **not** an ownership failure.

Canonical classification:

```text
parent +0x08 -> current 808008B4 SStaticMapData

if SStaticMapData +0x30 resolves as current 80801B75:
    direct_d1_baked_static
else:
    no_direct_d1_static_child
    -> hand to common/embedded-model layer parser
```

This policy is implemented in:

- `tools/d1_world_map_data_layer_census.py`
- `tools/d1_world_static_map_resource_chain_census.py`
- `tools/d1_world_static_map_content_census.py`

The content census then applies the exact baked retail gate only to the 10 direct-D1 carriers:

```text
DetailLevel in {0,1,2,3,10}
AND
material.Unk08 == 1
```

Tower regression targets are **50,148 serialized baked-static placements** and **11,728 retail-visible baked-static placements**.

## Evidence history / regression trap

An early map-layer attempt returned impossible array bounds because a local parser incorrectly interpreted the descriptor as `u64 relative + u32 count`. That was a parser bug, not evidence for a different retail entry layout.

The corrected source-backed descriptor immediately closed all nine tables at 337 rows. A later diagnostic whole-file factorization could also express the payload as `0x30 + N*0xA8`; the sidecar analysis above proves why that arithmetic is real while the implied 0xA8 entry stride is not.

The exporter must preserve these distinctions when generalized to other D1 worlds: **table framing, parent ownership, static-map subtype, and renderer visibility are separate evidence layers.**
