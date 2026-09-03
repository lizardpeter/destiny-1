# Destiny 1 ROI GPU Resource Notes

Status vocabulary:
- **CONFIRMED_BINARY** — directly reproduced from the supplied package bytes.
- **CONFIRMED_CROSS_SOURCE** — binary evidence agrees with an independent public implementation/specification.
- **PARTIAL** — some fields/relationships are proven; semantic naming remains incomplete.
- **HYPOTHESIS** — useful lead only; do not consume as a stable schema.

## VertexBuffer — `32:4 -> 1:4`

Header size: **0x0C** (`CONFIRMED_CROSS_SOURCE`).

| Offset | Type | Meaning | Status |
|---:|---|---|---|
| `0x00` | u32 | referenced data size | CONFIRMED_BINARY |
| `0x04` | s16 | stride | CONFIRMED_BINARY |
| `0x06` | s16 | vertex type | CONFIRMED_BINARY |
| `0x08` | u32 | platform marker | CONFIRMED_BINARY |

Observed platform markers:
- PS4 canonical sample: `0xBEEFCACE` — 11/11.
- Xbox One resident sample: `0xBEEFDEAD` — 144/144 decoded headers.

For all 11 PS4 headers, header `data_size == referenced entry file_size`. All vertex payload sizes are exactly divisible by stride.

## IndexBuffer — `32:6 -> 1:6`

Header size: **0x18** (`CONFIRMED_CROSS_SOURCE`).

| Offset | Type | Meaning | Status |
|---:|---|---|---|
| `0x00` | u8 | unknown; observed `1` | PARTIAL |
| `0x01` | bool | 32-bit index flag | CONFIRMED_BINARY |
| `0x02` | s16 | unknown; observed `0` | PARTIAL |
| `0x04` | s32 | zero | CONFIRMED_BINARY |
| `0x08` | u64 | referenced data size | CONFIRMED_BINARY |
| `0x10` | u32 | marker `0xDEADBEEF` | CONFIRMED_BINARY |
| `0x14` | s32 | zero | CONFIRMED_BINARY |

All 9 PS4 headers satisfy `data_size == referenced entry file_size`. Index buffers decode cleanly as u16/u32 according to the flag; all nine canonical-sample index counts are divisible by three and contain no restart marker.

### Canonical PS4 mesh-resource groups

The following groups are not based on filename adjacency alone. They are supported by equal vertex counts and index maxima:

| Position VB header | Companion VB | Index header | Vertex count | Index max | Triangles if list |
|---:|---:|---:|---:|---:|---:|
| 107 | 108 | 109 | 691 | 690 | 1,177 |
| 124 | 125 | 126 | 2,046 | 2,045 | 1,768 |
| 127 | 128 | 129 | 994 | 993 | 816 |
| 172 | — | 173 | 1,077 | 1,076 | 852 |
| 174 | 175 | 176 | 111,334 | 111,333 | 76,478 |
| 177 | 178 | 179 | 100,300 | 100,299 | 79,460 |

`tools/d1_geometry_proof.py` exports topology/position GLBs from these groups. Position shorts are converted as signed-normalized values for preview only; object-level scale/offset is not yet recovered from a model/static tag, so these GLBs are **geometry proofs, not final scene-correct assets**.

## Texture2D PS4 ROI — `32:1`

Stored header size: **0x3C**.

| Offset | Type | Meaning |
|---:|---|---|
| `0x00` | u32 | data_size |
| `0x04` | u8 | unknown |
| `0x05` | u8 | unknown |
| `0x06` | u16 | packed GCN surface format; `(v >> 4) & 0x3f` |
| `0x08..0x23` | bytes | unresolved |
| `0x24` | u32 | `0xBEEFCAFE` |
| `0x28` | u16 | width |
| `0x2A` | u16 | height |
| `0x2C` | u16 | depth |
| `0x2E` | u16 | array_size |
| `0x30` | u32 | flags1 |
| `0x34` | u32 | flags2 |
| `0x38` | u32 | flags3 |

Canonical sample formats seen: BC1, BC3, BC4, BC5. All 30 PS4 Texture2D headers have now been reconstructed, deswizzled and exported successfully to DDS/PNG previews.

Storage modes:
- direct payload: header reference points directly to data.
- two-hop / large-buffer mode: `32:1 -> 65:1 -> 5:1` and the second reference supplies the main texture data. The exact semantic role of the `65:1` bytes beyond acting as the first hop remains unresolved.

PS4 ROI deswizzle follows 8x8 groups of format blocks with Morton ordering and power-of-two alignment for compressed formats, matching current QuickTag behavior.

## Texture2D / TextureCube Xbox One ROI

Observed header size: **0x44**. Decompressed bytes resolve the previously unparsed tail:

| Offset | Type | Meaning | Status |
|---:|---|---|---|
| `0x00` | u32 | DXGI format | CONFIRMED_CROSS_SOURCE |
| `0x04` | u32 | tile mode | CONFIRMED_CROSS_SOURCE |
| `0x08..0x2B` | bytes | unresolved | UNKNOWN |
| `0x2C` | u32 | `0xBEEFCAFE` | CONFIRMED_BINARY |
| `0x30` | u16 | width | CONFIRMED_BINARY |
| `0x32` | u16 | height | CONFIRMED_BINARY |
| `0x34` | u16 | depth | CONFIRMED_BINARY |
| `0x36` | u16 | array_size | CONFIRMED_BINARY |
| `0x38` | u32 | flags1 | CONFIRMED_BINARY |
| `0x3C` | u32 | flags2 | CONFIRMED_BINARY |
| `0x40` | u32 | flags3 | CONFIRMED_BINARY |

Thus the old `0x38..0x43 unknown tail` is retired from the unknown ledger.

## GPU subtype 7 — `32:7 -> 1:7`

All 122 canonical PS4 headers are exactly 16 bytes:

| Offset | Observed role |
|---:|---|
| `0x00` | always zero in this sample |
| `0x04` | always `0x00100000` in this sample |
| `0x08` | unit count |
| `0x0C` | marker `0x20077FAC` |

**Critical binary invariant:** for all 122/122 local pairs,

`referenced_data_size == u32(header+0x08) * 16`.

Current QuickTag maps subtype 7 to ConstantBuffer in later Destiny engines but deliberately comments the D1 mapping out. The exact 16-byte-size relation and technique references make a constant-buffer interpretation **strongly supported**, but the project retains the neutral name `GpuSubtype7` until D1-specific semantic confirmation is complete.

Additionally, 88 `s_technique` tags contain a local subtype-7 header TagHash at the exact byte offset `0x32C` (812), strengthening the material/shader-resource association.

## PS4 PixelShader — `32:8 -> 1:8`

Seven canonical headers/data pairs are present.

### Bungie header packed word 0

For every pair:
- low 24 bits of header word 0 = referenced shader payload byte size (**7/7**).
- high 8 bits = `ShaderBinaryInfo.num_input_usage_slots` from the native PS4 shader footer (**7/7**).

Therefore the first word is now structurally decoded as:

`packed0 = (num_input_usage_slots << 24) | shader_payload_size`

### Native PS4 shader payload

All seven payloads have this reproduced structure:

1. u32 `0xBEEB03FF` — PS4 GCN `s_mov_b32 vcc_hi, #imm` token.
2. u32 qword count.
3. `qword_count * 8` bytes of native GCN shader region.
4. 28-byte `ShaderBinaryInfo` footer beginning with ASCII `OrbShdr`.

Total payload size is exactly:

`8 + qword_count*8 + 28`

The `OrbShdr` footer parses using the public PS4 BinaryInfo layout: 7-byte signature, version, packed source/type/length bits, chunk-usage offset, input-usage-slot count, SRT flags, 64-bit shader hash and CRC32. All seven canonical shaders report binary type 0 (pixel shader) in that footer, independently corroborating Tiger subtype 8.

Evidence: `evidence/decoded/ps4_pixel_shader_payloads.json`.
