# D1 API10 LocalShader runtime gate — durable checkpoint

Branch: `d1-crota-source-semantics-v1`

This note is intentionally fail-closed. It records what the current repository can prove and the exact evidence still required. It must not be used to promote API numbers, SGPR windows, access counts, adjacency, or later register reuse into engine semantics.

## Source-closed boundary

The existing source-closed census remains 39 exact GCN programs / 56 wrappers / 3,386 material occurrences with TBUFFER-count families 3, 6, 8, and 12 and API10 descriptor windows `s[8:11]` or `s[12:15]`.

Runtime writer, the four runtime descriptor dwords, backing allocation, and engine semantic remain **WITHHELD** until primary PS4 runtime evidence ties an exact member to a consuming draw/dispatch.

## Capture gate strengthened 2026-09-18

`tools/d1_validate_api10_runtime_capture_v1.py` now additionally requires:

- `consumer_stage == "LOCAL_SHADER"` and a non-empty consuming draw/dispatch locator;
- the exact 16 captured descriptor bytes as well as four uint32 dwords, with byte-for-byte little-endian coherence;
- exact captured writer bytes whose SHA-256 is recomputed;
- non-empty exact backing bytes whose SHA-256 and length are recomputed;
- semantic and universal-record-schema fields to remain WITHHELD.

This closes prior fail-open cases where a capture could present dwords without the raw 16 descriptor bytes or omit the consuming draw/dispatch locator.

## Rare 3/6-load retail families

Frozen successful producer: Actions run 35388270542, job 105740277559, artifact 10564682786, artifact digest `sha256:cf5b8b040e4e1ea27a6548eae573f8fbdb98ed6427d3c76d4354e2f68ba98871`.

Exact retail GCN identities:

- wrapper `80A08667` -> native `80A08668` -> GCN SHA-256 `2611323e1fd51d609701f16bb7a6ca11da116ace11be3861659d10813154828f`: LocalShader, three `tbuffer_load_format_xyzw`, `s[8:11]`, `idxen`, `32_32_32_32,float`. The index chain is base `*3`, then `+1`, `+2`: three consecutive indexed float4 records are consumed.
- wrapper `80A0627B` -> native `80A0627C` -> GCN SHA-256 `44643993ac626aa827f90578ad0b5b6c2adc1d78e0e888a761ffb0554aeb008c`: LocalShader, six `tbuffer_load_format_xyzw`, `s[8:11]`, `idxen`, `32_32_32_32,float`. Two independent indices are each multiplied by three and expanded to +0/+1/+2, yielding two interleaved triples of indexed float4 records.

For `80A0627B`, all six API10 TBUFFER consumers occur before instruction offset `0x10c`, where `s_buffer_load_dwordx4 s[8:11], s[12:15], 0x18` overwrites the same `s[8:11]` window. This proves **post-consumption SGPR reuse only**. It is evidence against assigning stable resource meaning from an SGPR window.

The workflow now asserts these exact offsets, operands, formats, index-generation chains, and reuse ordering against the frozen GCN hashes.

## Hard gate / next capture

A primary runtime capture must provide, for an exact source-closed GCN member:

1. consuming LocalShader draw/dispatch locator;
2. exact 16 descriptor bytes and coherent four dwords at the consuming point;
3. exact command/user-data writer bytes plus capture locator/callsite;
4. exact backing allocation bytes and a primary-evidence relation between descriptor range and that allocation;
5. enough runtime context to distinguish producer provenance from coincidental SGPR/register reuse.

Until that evidence exists, `runtime_writer`, `descriptor_dwords`, `backing_allocation`, and `engine_semantic` remain WITHHELD. A blocked runtime avenue should pivot to source-closed package/shader/material/geometry/animation work rather than weakening this gate.
