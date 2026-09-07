# D1 universal activity / visual closure checkpoint — 2026-09-06

This note records the proof boundary reached while converting the earlier Tower/Crota-specific work into a reusable Destiny 1 PS4 activity/world asset pipeline. Claims below are source-derived or canary-derived; pending jobs are explicitly marked pending.

## Universal activity graph

The generic activity path now covers:

```
SUnkActivity_ROI
  -> activity resource parents / S6E stage resources
  -> SF603 resources
  -> runtime placement tables
  -> scripted-table-owning EntityResources
  -> D912 scripted groups / records / locations
  -> exact asset dependency seed populations
```

The dependency seed layer keeps these populations distinct:

- runtime placement `s_entity` hashes;
- D912 scripted-record EntitySK hashes;
- scripted-only entities (scripted hashes absent from runtime placement entity population);
- EntityResources, embedded models, dialogue targets, map tables and stage resources.

Only typed source-owned edges may establish semantic ownership. Aligned/raw FileHash sightings remain discovery evidence unless an intervening schema is closed.

## D912 scripted overlay correction

The historical scripted identity census asserted that a named D912 SMapDataEntry must have the same EntitySK as the independently materialized runtime placement with the same WorldID. That assertion is false for normal retail data.

Four independent activities demonstrate the same structure:

| activity | formerly fatal named mismatches | observed relationship |
| --- | ---: | --- |
| King's Fall | 441 / 441 | WorldID matches, transform matches, EntitySK differs |
| Wrath of the Machine | 765 / 765 | WorldID matches, transform matches, EntitySK differs |
| Cosmodrome strike (`strike_reliquary`) | 958 / 958 | WorldID matches, transform matches, EntitySK differs |
| Plaguelands patrol | 943 / 943 | WorldID matches, transform matches, EntitySK differs |

The associated artifacts showed zero competing D912 structural/bounds failure class for the King's Fall/Wrath cases inspected in detail. Cosmodrome/Plaguelands violation lists were likewise entirely the obsolete owner-equivalence assertion.

Therefore D912 records are treated as scripted overlay records, not redundant restatements of the runtime placement table. The corrected remote census records explicit relations:

- `WORLDID_ENTITY_TRANSFORM_MATCH`
- `WORLDID_ENTITY_MATCH_TRANSFORM_DIFFERS`
- `WORLDID_TRANSFORM_MATCH_ENTITY_DIFFERS`
- `WORLDID_MATCH_ENTITY_AND_TRANSFORM_DIFFER`
- `WORLDID_NOT_IN_RUNTIME_PLACEMENTS`

A scripted `EntityName` StringHash is eligible to attach to runtime placement identity only when WorldID and EntitySK agree. Transform equality is preserved as an independent validation signal. When EntitySK differs, both serialized hashes remain distinct and no identity alias is inferred.

Implementation: `tools/d1_remote_activity_scripted_entity_census.py`, corrected in commit `169939c9bebbeb5905b1431c1dd5721de6281323`. The eight-way scenario canary was updated to trigger on the shared scripted parsers and assert zero true scripted-census violations in commit `055373fafe51b28639971b1ef4cfc3c8c7491a9e`.

## Universal Tiger FileHash routing

All new universal remote stages route Tag/FileHashes through `tools/d1_filehash.py` rather than subtracting `0x80800000`.

The D1 bank-aware mapping is:

```python
package = ((v >> 13) & 0x3FF) + ((((v >> 23) & 3) - 1) * 0x400)
index   = v & 0x1FFF
```

This is required for later/Rise-of-Iron namespaces such as Wrath and Plaguelands. Ordinary references that numerically decode to a package are not promoted into recoverable package dependencies unless the verified current package index contains that package family; this prevents phantom package `0000` recovery while preserving the original serialized reference evidence.

## Exact dynamic entity/model closure

The activity dependency seeds feed `d1_remote_entity_dependency_closure_universal.py`, which source-closes typed paths through:

```
s_entity
  -> EntityResource
  -> embedded EntityModel
  -> skeleton resource
  -> child entities
  -> scripted/dialogue/name targets
```

Untyped aligned FileHash occurrences are recorded but do not recurse/promote ownership by default.

`d1_activity_entity_model_plan.py` selects only `s_entity_model` nodes reached through typed exact paths.

`d1_remote_activity_model_visual_dependency_closure.py` then closes each exact model into:

- `vertices1` reference-file stream;
- `vertices2` reference-file stream;
- `old_weights` reference-file stream (required for skinned models);
- index reference-file stream;
- each reference-file's exact backing payload;
- inline Material hashes where `variant_shader_index == -1`.

External variant materials are not inferred from the model-local material field.

## Exact external material selection

`d1_remote_activity_model_material_bindings.py` derives exact `(EntityModel, model-parent EntityResource)` ownership pairs from the source-parsed `s_entity` resource lists, then applies the already source-pinned D1 external-material mapping semantics:

```
EntityResource model-parent payload
  +0x15C EntityModel FileHash
  +0x230 DynamicArray<SExternalMaterialMapEntry>
  +0x270 external Material array

VariantShaderIndex == -1
  -> inline model Material
otherwise
  -> external map[VariantShaderIndex]
  -> MaterialStartIndex + (0 % MaterialCount)
```

No model similarity, package adjacency, material ordering or visual guess is used.

### Anomaly canary

For PvP Anomaly (`80D8E003`, `pvp_anomaly:scenario_client`) the generic pipeline closed:

- 159 initial activity dependency seeds;
- 284 recursive dependency nodes;
- 1,598 graph edges;
- 176 typed edges;
- no truncation;
- 6 exact EntityModels;
- 29 unique model buffer headers;
- 29 exact backing payloads;
- 20 inline Materials;
- 40 external-variant model parts;
- 6 / 6 model-parent pairs validated;
- 150 model parts checked by the material resolver;
- all 40 / 40 external-variant parts resolved;
- 32 unique final retail Materials;
- zero unresolved variant models;
- zero material-binding violations.

The exact 32-material result is pinned only as a downstream regression fixture at `tests/fixtures/d1_anomaly_pvp_selected_material_plan.json`. The production pipeline still derives it from activity/entity ownership.

Source workflow run: `34079400806`, Anomaly artifact `10003228390`, artifact digest `sha256:7db926355c0aac4e53d0f30e06af7b0799855bdc83048c12b37fe61020067963`, source head `055373fafe51b28639971b1ef4cfc3c8c7491a9e`.

## Material -> shader / texture dependency closure

`tools/d1_remote_activity_material_dependency_closure.py` was added in commit `86b76f379f4cd339596d24e04ad7e3ab53957bed`.

For every exact selected `80801AD7` Material it preserves:

- vertex shader TagHash + exact payload identity;
- pixel shader TagHash + exact payload identity;
- VS/PS TFX bytecode arrays;
- VS/PS sampler descriptors;
- VS/PS Vector4 container tags and referenced payloads;
- every serialized VS/PS texture binding with its exact `TextureIndex` / `t#` register;
- Texture2D header metadata;
- direct backing or validated streamed `32:1/32:2 -> 65:1 -> 5:1` backing chain;
- payload sizes and SHA-256 digests.

Unknown shader roles remain `vertex:tN` / `pixel:tN`. The pipeline does **not** label arbitrary slots albedo, normal, roughness, etc. Known roles can only be promoted by independent shader dataflow evidence.

## Remote exact texture materialization

`tools/d1_remote_activity_texture_export.py` was added in commit `b727a7358b457910efc13ca907a1d1b1e78c9e8a`.

It consumes only the exact texture header/backing identities already proven by the material dependency closure and:

1. refetches and revalidates the Texture2D header;
2. checks header fields against the proof manifest;
3. fetches the exact final backing payload;
4. validates expected top-level byte size;
5. unswizzles PS4 GCN layout when required;
6. writes deterministic DDS and PNG outputs where supported;
7. records SHA-256 for source backing bytes, linearized bytes and output files.

It performs no material-role/PBR inference.

A focused Anomaly material/texture canary was added at `.github/workflows/d1-activity-material-dependency-canary.yml`. At the time this note was written, that newest material/texture job was queued and is therefore **not yet claimed green** here.

## Static-world status

The count-agnostic world/static chain has already passed end-to-end canaries for:

- Tower;
- Cosmodrome;
- Venus;
- Crota's End.

The generic validator treats historical Tower counts as regression fingerprints, not format laws.

## Current frontier

Still to close or integrate generically:

1. finish the new cross-activity scripted-overlay canary run, especially King's Fall/Wrath/strike/Plaguelands;
2. green the Anomaly Material -> shader/texture -> DDS/PNG canary;
3. feed the material/texture closure directly into the main deep activity workflow rather than only the pinned downstream fixture;
4. retrofit remaining older static-world helpers that still contain pre-bank FileHash package arithmetic;
5. preserve shader-native semantics for portable material recreation (do not collapse to generic PBR prematurely);
6. connect exact skeleton/weights to animation ownership and clip extraction across arbitrary activities;
7. add effects/audio dependency layers;
8. assemble static + dynamic + scripted + material + animation products into deterministic scene/GLB/Blender outputs.
