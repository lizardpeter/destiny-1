# D1 Xur Wave 8 and external-material permutation layout frontier

Date: 2026-09-07
Target: Xur (`StringHash 46C55854`, entity model `80C88CEF`)

This note extends `notes/D1_XUR_TEXTURE_SHADER_AND_PERMUTATION_STATUS_2026-09-07.md` and records the current exact proof boundary before changing the shared D1 model-parent parser.

## Shader semantic status through Wave 8

The exact Xur native shader census remains 31 unique bounded PS4 GCN programs across the current 54-material shared-human checkpoint. Wave 8 is green.

Wave 8:

- workflow run: `34158126025`
- artifact: `D1-TOWER-XUR-SHADER-SEMANTIC-WAVE8`
- artifact ID: `10031655535`
- artifact ZIP SHA-256: `6a7e6ebcee8109648894c468de13ae21461d1cd53eda3ca0cdbf8803a9342c53`

Exact instruction-level progress after Wave 8:

- 13 / 31 native GCN programs closed;
- 18 / 38 stage structural units closed;
- 15 / 33 combined material structural families have both VS+PS closed;
- 36 / 54 materials have both current VS and PS dataflow closed;
- 38 / 54 materials have PS dataflow closed;
- 48 / 54 materials have VS dataflow closed.

Wave 8 also independently demonstrates why semantic reuse is keyed by exact bounded native GCN SHA-256 rather than serialized shader TagHash: distinct serialized PS headers `808768B7` and `80A08C16` contain the same bounded native GCN program.

The reusable registry validator is green against the Wave 8 closed-program set. The registry now contains 13 exact program handlers = 10 PS + 3 VS. Future D1 assets may reuse an instruction-level handler only when `stage + exact bounded native GCN SHA-256` matches; their literal textures, constants, TFX, samplers, runtime/global inputs, fetch layout, render state, and permutation selection remain asset-owned inputs/gates.

## Why material selection is now the highest-leverage blocker

The current shared-human checkpoint contains 54 candidate materials because model `80C88CEF` is shared by multiple Tower identities. Continuing to lift every candidate shader before retail member selection is known can spend time on materials that Xur never selects.

`tools/d1_render_owner_probe.py` currently proves and preserves:

- D1 model-parent class `0x80801A9C`;
- embedded entity model at parent `+0x15C`;
- `TexturePlatesROI` at `+0x1A8`;
- `ExternalMaterialsMap` at `+0x230`;
- `ExternalMaterials` at `+0x270`.

It still records the first member of each external-material range as a convenience selection. That is not a retail live-permutation proof.

## Newly source-closed D1 schema fact at +0x260

Pinned Charm source for `DESTINY1_RISE_OF_IRON` declares model-parent class `9C1A8080` with size `0x290` and gives the following exact D1 fields:

- `Model` at `+0x15C`;
- `TexturePlatesROI` at `+0x1A8`;
- `ExternalMaterialsMap` at `+0x230`;
- an 8-byte-element dynamic array at `+0x260`, typed by Charm as D1 class `FE1A8080`;
- `ExternalMaterials` at `+0x270`.

Charm defines D1 `FE1A8080` as four `ushort` fields (`Unk00`, `Unk02`, `Unk04`, `Unk06`). This `+0x260` array is therefore a real D1 serialized structure and is no longer an inferred gap.

## Comparative later-strategy evidence, not D1 authority

Current MIDA/Marathon source implements `ModelPermutation` from the analogous model-parent region:

- switch-record array `Unk38`;
- external-material map;
- an intermediate `SInt16` index array;
- an 8-byte descriptor array;
- external materials.

For each descriptor, MIDA treats its fields as a count/start into the intermediate int16 table. Those int16 values index switch records, each of which owns one or more exact `(SwitchKey, Value)` pairs. Sorted key/value sets are mapped to a permutation index.

The later-strategy layout places the intermediate int16 array one 0x10-byte dynamic-array slot before the 8-byte descriptor array. D1 has an unmapped 0x10-byte slot at parent `+0x250`, directly before the source-closed D1 descriptor-like array at `+0x260`.

Therefore `+0x250` is now a **high-priority structural candidate** for the D1 intermediate index array, but it is **not promoted yet**. D1 authority requires the exact retail bytes to validate its dynamic-array header, element domain, descriptor bounds, and switch-record references.

Likewise, the D1 location/layout of the switch-record array itself is not yet source-closed. It must be recovered from the exact D1 parent payload rather than copied from Marathon's `+0x28` offset.

## Next fail-closed proof

The next parser/workflow must use the exact retail Xur model-owner payload and:

1. prove the Xur `EntityResource` resolves to model parent `0x80801A9C` and embedded model `80C88CEF`;
2. decode the known D1 arrays at `+0x230`, `+0x260`, and `+0x270`;
3. inspect and validate candidate dynamic-array header `+0x250` without assuming its element type;
4. enumerate all structurally valid dynamic-array headers before `+0x15C` and identify any array whose elements can be parsed as switch-record containers containing exact 8-byte key/value pairs;
5. prove every descriptor/index/switch reference is in bounds;
6. only then implement a D1 permutation graph;
7. keep live Xur configuration-state discovery as a separate gate from static permutation-graph decoding.

No material member should be called retail-selected until both the static D1 graph and the instantiated Xur switch state are source-owned and fail-closed.
