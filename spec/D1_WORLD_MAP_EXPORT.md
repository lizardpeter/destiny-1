# Destiny 1 World / Map Export Pipeline — Living Specification

Status: **Tower baked-static placement/visibility solved across 10 map-owned cells; table-scoped common embedded model/decal layer structurally solved; affine/UV record correction solved; exact ten-cell visible texture dependency corpus closed.**  
Target: a reusable final-era D1/Rise of Iron exporter that can reconstruct every world/map without Tower-specific guesses.

## Design rule

The canonical representation is lossless D1 source data. glTF/Blender is an adapter.
Do not mutate source semantics merely to make one viewer look correct.

## Layer 1 — package / Tiger resource resolution

- D1 v24 TagHash construction is solved.
- current physical patch siblings are resolved as one logical package family;
- current-generation/class-stable cross-package resource selection is fail-closed;
- serialized-coverage sized Oodle block reader handles partial logical blocks.

## Layer 2 — map ownership / static cells

- identify map-owned `StaticMapData -> StaticMapData_D1 -> StaticTable` chains;
- preserve the exact map-data-table / parent chain establishing ownership;
- never infer world ownership from package filename or successful mesh decoding alone.

Tower fixture: **10 validated map-owned baked-static cells, 50,148 serialized placements.**
The tenth current cell is `80C98254 -> 80C98258`; it was previously excluded only because
its current `80801B75` payload could not be decoded by the legacy fixed-size Oodle reader.
The serialized-coverage sized reader recovers its exact current 48,084-byte payload and the
cell now validates and exports normally.

### Layer 2A — D1 table-scoped common embedded model/decal layer

The D1 `SMapDataTable`/`SStaticMapData` relationship has a second world-geometry layer that
must **not** be treated as additional baked statics.

For the nine Tower map-data tables, binary validation proves:

- **337** serialized `SMapDataEntry` rows;
- **337** distinct `SStaticMapParent` resources;
- only **19** unique `SStaticMapData` resources;
- **10** small/baked `SStaticMapData` resources with direct `80801B75` children;
- **9** large/common `SStaticMapData` resources with no direct `80801B75` child;
- those nine common resources contain **327** valid `BA048080` embedded records total;
- **327 / 327** records contain exactly one transform and one `s_entity_model` reference;
- those records reference **69 unique `s_entity_model` resources**.

Pinned D1 source behavior in `MapView.ExtractDataTables` is important here: for each D1
`SMapDataTable`, the exporter calls `LoadDecalsIntoExporterScene` **once**, on the
`DataEntries[0]` static-map resource, and then walks all map entries independently for the
baked-static `LoadIntoExporterScene` path. Shipped Tower bytes match that structure exactly:
each table's first row resolves to its large/common carrier.

Tower table/common-carrier fixture:

```text
80C98028 -> first 80C98191 :  38 records
80C984A0 -> first 80C984D7 :  13 records
80C9895C -> first 80C98A69 :  78 records
80C989F7 -> first 80C993A2 : 110 records
80C997DF -> first 80C997F4 :   3 records
80C99956 -> first 80C99980 :  21 records
80CA0B0E -> first 80CA0B6F :   9 records
80CA0B11 -> first 80CA0B71 :  53 records
80CA0C4E -> first 80CA0C5F :   2 records
                                    ---
                                    327
```

**Regression trap:** naively reloading each repeated common carrier once for every one of
its map-parent rows expands these 327 records to **23,141 false placements**. That number
is not a scene count and must never be exported. The common carrier is loaded once per
map-data table.

For each common embedded model, the source-crosschecked D1 selection is:

```text
EntityModel.Load(ExportDetailLevel.MostDetailed, parentResource=null, transparentsOnly=true)
```

Therefore the portable map adapter selects highest LOD categories `{0,1,2,3,10}`, requires
a directly resolvable material/VS/PS, and requires D1 material `Unk20 != 0`. External
variant-material entries are retained as unresolved when no parent EntityResource exists;
they are not guessed.

## Layer 3 — retail visibility

D1 `StaticMapData_D1.GetStatics()` visual gate:

```text
DetailLevel in {0,1,2,3,10}
AND
material.Unk08 == 1
```

Tower fixture: **50,148 serialized -> 11,728 retail-visible placements.**
No placement is removed merely because it looks unusual in Blender; visibility changes
must be supported by D1 renderer or higher-level activity/scene semantics.

## Layer 4 — baked-static instance record

A D1 baked-static instance is a 0x40-byte record, **not** a homogeneous 4x4 matrix:

```text
+0x00..+0x2F  float3x4 affine SRT transform
+0x30         float UV scale
+0x34         float UV translate X
+0x38         float UV translate Y
+0x3C         unknown/tail; not a homogeneous matrix element
```

Canonical affine matrix synthesizes final row `[0,0,0,1]`.

Per-instance UV application:

```text
u = u * scale + translateX
v = v * (-scale) + 1 - translateY
```

Tower ten-cell fixture: **2,071 retail-visible geometry variants**. The exporter retains
exact per-instance UV metadata and creates an adapter geometry variant when glTF cannot
represent a per-node UV transform directly.

## Layer 5 — coordinate adapters

D1 world space is retained canonically as Z-up.

glTF adapter:

```text
D1 Z-up -> glTF Y-up
[ 1  0  0  0 ]
[ 0  0  1  0 ]
[ 0 -1  0  0 ]
[ 0  0  0  1 ]
```

Blender then performs its standard glTF Y-up -> Blender Z-up import conversion.
No per-object cosmetic rotation is part of the source data.

## Layer 6 — static vertex attributes

Source-crosschecked D1 Static layouts currently covered:

Primary stream:
- stride 8: position
- stride 12: position + UV at +8
- stride 28: position + UV at +8 + normal at +0xC
- stride 32: position + UV at +8 + vertex colour near tail

Secondary stream:
- stride 12: UV + normal
- stride 16: normal
- stride 20: UV+normal, or normal+vertex colour if primary UV already exists
- stride 24: UV + normal with the D1 static-specific gap

Position/UV/normal packed components are signed normalized int16 / 32767 for these
layouts. Unsupported attribute layouts fail closed **without deleting otherwise-valid
geometry**: position/index geometry remains exportable while UV/normal enrichment is
marked unavailable. Current ten-cell Tower result has **0 geometry decode failures** and
**5 geometry variants with secondary attributes intentionally left undecoded**.

## Layer 7 — material / shader / texture dependencies

PS4 ROI material class: `80801AD7`.

Exact material bindings are preserved as:

```text
material
  -> vertex shader
  -> VS TextureIndex t# -> Texture TagHash
  -> pixel shader
  -> PS TextureIndex t# -> Texture TagHash
  -> sampler / constant resources
```

`TextureIndex` is proven to be the shader `t#` register.

Texture resources are reconstructed through the PS4 ROI Texture2D header/stream/
backing chain, deswizzled, and exported to DDS/PNG.

Current ten-cell Tower exact texture census:

- **400** retail-visible materials;
- **506** unique texture TagHashes;
- **506 / 506** texture resources reconstructed;
- **0** material decode errors;
- **0** texture decode errors;
- **561** PNG outputs including cubemap faces.

Material constants are preserved independently of role interpretation. Current ten-cell
visible-material census has **264** unique external constant containers, of which **235**
are byte-decoded in the current dependency corpus; the remaining 29 are explicit dependency
resolution gaps, not zero/default constants.

Semantic rule: do not call arbitrary `t0` an albedo map. Shader/register roles are
named only after shader dataflow proves them. The exact register binding remains
usable even before the higher-level PBR interpretation is solved.

## Layer 8 — glTF material adapter

For each shader family:

1. preserve the exact D1 material recipe in glTF extras/sidecar;
2. map proven surface/normal/emissive/etc. resources to glTF PBR slots where valid;
3. preserve unsupported resources and shader constants instead of discarding them;
4. bake the D1 per-instance UV transform into a geometry variant only when required
   by glTF's lack of per-node UV-transform state.

The current broad ten-cell Tower visual adapter textures **1,786 / 2,071** geometry
variants and supplies portable normal maps to **1,469 / 2,071**. These counts include
explicitly evidence-scoped preview candidates; they do **not** promote those candidates
to canonical D1 shader semantics.

## Layers still to integrate for complete worlds

Baked statics are only one layer of a D1 destination. A complete world exporter must
also enumerate and reconstruct, without guessed ownership:

- the now-identified table-scoped embedded/common model layer;
- entity/model placements and animated/dynamic props outside that layer;
- standalone map decals;
- terrain/natural geometry families;
- sky/environment resources;
- lighting/probes/environment maps;
- particles/VFX where exportable;
- activity/runtime variants and conditional scene content;
- collision/nav/physics as separate optional data products;
- locale/UI/signage content where relevant.

## Current Tower regression fixture

Tower is the first full regression world. A change is not accepted if it breaks any
of these proven invariants:

- **10** map-owned baked-static cells;
- **50,148** serialized baked-static placements;
- **11,728** retail-visible baked-static placements;
- **2,071** baked-static visual geometry variants;
- zero baked-static geometry decode holes;
- only 5 baked-static variants currently lacking secondary UV/normal enrichment, with geometry preserved;
- **9** table-scoped common carriers loaded once per table;
- **327** structurally valid singleton transform/model common records;
- **69** unique common-layer `s_entity_model` references;
- never expand the common layer into the false **23,141** repeated-parent count;
- affine-only baked-static node matrices;
- exact per-instance baked-static UV metadata retained;
- D1 source Z-up retained canonically;
- **400 baked-static visible materials / 506 unique texture resources / 506 reconstructed**;
- visible material/texture dependencies remain exact TagHash/register relationships.
