# Xbox One `arch_cabal_0059_1` — Corpus Notes

Status: analyzed secondary corpus. Not the semantic counterpart of PS4 `arch_cabal_005b_1`.

## Identity

- platform: Xbox One
- Tiger v24
- package ID: `0x0059`
- patch: 1
- size: 119,173,120 bytes
- SHA-256: `8836546ecbbbf6ba31fd50035a180c80c7bcb6407780f4b61be7a8217d24fde8`
- entries: 8,111
- block records: 2,228
- resident patch-1 blocks: 796 / 796 stored SHA-1 verified
- patch-0-owned records: 1,432; sibling `_0.pkg` missing

## Why it is valuable

Despite not matching PS4 package `005B`, it is a much larger independent Cabal/model/material corpus. It contains large numbers of vertex/index resources, textures, structured tags, entity models, Xbox DXBC shaders and shared-resource references.

## Confirmed high-level findings

- 173 `0x80800861` D1 EntityResource outer tags; 119 resident.
- 11 resident EntityResources identify embedded entity-model parents.
- 16 resident `s_entity_model` tags decode into 23 meshes / 284 parts.
- 23/23 decoded meshes satisfy the Xbox stage-tail invariants.
- model parent serialization places the embedded EntityModel TagHash at `+0x1C4`, differing from the PS4-oriented `+0x15C` source schema.
- first fully resident metadata-driven model target: `808B3A16` (two meshes; all six VB/IB dependencies resident).
- Xbox material family observed as `0x80801C32`.
- material texture indices exactly match DXBC `t#` registers in all 11 resident overlaps.
- sampler counts/register sequences match in all 11 overlaps.
- material constant vec4 counts exactly match DXBC pixel `b0` in all 11 overlaps.
- `0x80801AA5` vector-container layout is invariant across 276/276 resident examples.
- all 22 `s_animation_clip` (`0x808005A1`) entries require patch 0.
- no resident D1 skeleton-discriminator EntityResource is present in patch 1.

## Xbox-specific GPU facts

- Texture2D/Cube header size `0x44`.
- DXGI format at `+0x00`; tile mode at `+0x04`.
- `BEEFCAFE` at `+0x2C`.
- dimensions/array at `+0x30..0x37`.
- flags1/2/3 at `+0x38/+0x3C/+0x40`.
- first model's bound textures use Durango tile mode 14; semantic material binding is solved, visual export still needs detiling.
- vertex header is `0x0C`, with Xbox marker `0xBEEFDEAD`.
- index header is `0x18` and shares `0xDEADBEEF` marker semantics.

## Highest-value missing sibling

`xboxone_arch_cabal_0059_0.pkg`

It is now needed primarily for skeleton/animation and patch-complete dependency reconstruction, not for proving the package/Oodle/GPU model.
