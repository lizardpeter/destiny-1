# D1 source-semantics renderer contract

The decoder must have one authoritative source representation and multiple output adapters. Blender/glTF and the Rust game renderer must not redefine the source data differently.

## Vertex data

A D1 serialized RGBA8 vertex field is decoded losslessly as a four-component source shader input. Its storage layout is proven; its shader role is not globally equivalent to glTF `COLOR_0`.

Canonical name in portable interchange: `_D1_COLOR`.

`COLOR_0` may only be emitted when a specific native vertex/pixel shader dataflow proves that the field has standard color-multiplier semantics compatible with glTF. Otherwise Blender must not silently multiply it into base color. The Rust renderer should bind the decoded vector to the native-equivalent shader input selected by the material/shader program.

The same principle already applies to `_D1_TANGENT`: storage/decoded values can be exact before generic glTF tangent-handedness semantics are proven.

## Material render state

`tools/d1_material_render_state.py` is the destination-neutral decoder for currently closed D1 material state.

Current exact contract:

- Material resource class: `80801AD7`.
- Material `+0x20` is preserved as an exact 16-bit value.
- `+0x20 == 0` belongs to the opaque draw population.
- `+0x20 != 0` belongs to the transparent draw population.
- Low selector `0x88` is independently closed as native blend-state index 8 with `Source + Destination*(1-SourceAlpha)`.
- Other nonzero states remain transparent-classified, but their exact equations are unknown until source/native proof closes them.

The Blender adapter can map the population classification to `OPAQUE`/`BLEND` as a portable view. That does not authorize inventing the source alpha channel, texture composition, blend equation, culling mode, or shader logic.

The Rust renderer should retain the raw `unk20` field and exact decoded blend-state metadata in its material IR. It can emulate the native equation only when that equation is proven.

## Decoder architecture

The intended pipeline is:

`retail package bytes -> exact D1 decode/IR -> shader/render-state semantic closure -> adapters`

Adapters include:

- Blender/glTF inspection view.
- Rust runtime renderer.
- Forensic JSON/evidence output.

An adapter is not allowed to destroy or reinterpret source bytes merely to make a preview look plausible. Unknown semantics remain explicit and loss-preserved.

## Current Crota visual failure this contract addresses

The blue terrain/static surfaces seen in Blender came from standard glTF `COLOR_0` multiplication of D1 control vectors. The source bytes were real; the portable semantic assignment was wrong. The source-semantics adapter renames those attributes losslessly to `_D1_COLOR` and derives material alpha class from the exact D1 `+0x20` state.

White/card surfaces that remain after this correction are a separate shader-composition problem: their source texture/alpha/material dataflow must be closed rather than hidden with an appearance heuristic.
