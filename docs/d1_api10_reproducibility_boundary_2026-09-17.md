# D1 API10 provenance reproducibility boundary — 2026-09-17

This note freezes the current source-closed boundary for the LocalShader/API10 investigation. It deliberately does **not** promote an engine semantic for API10.

## Proven consumer contract

`tools/d1_gcn_resource_lds_provenance_v1.py` is a joiner, not an SSA reconstructor. For every program stem it requires three independently exact inputs:

1. structural GCN IR with status `D1_GCN_STRUCTURAL_IR_COMPLETE` and exact structural parse accounting;
2. integrated vector binding with status `D1_GCN_VECTOR_SPECIAL_VALUE_BINDING_EXACT` and exact parse accounting;
3. scalar/M0 SSA with status `D1_GCN_SGPR_SSA_EXACT` and exact parse accounting.

The join is fail-closed on shader identity, instruction count, and per-instruction `(index,address,opcode)` identity.

For `tbuffer_load_format_xyzw`, provenance requires the current VADDR VGPR value plus exactly four SRSRC SGPR SSA references. Each descriptor component must carry non-empty `external_graph`, `external_node`, and `external_ref` fields. Register SOFFSET must likewise resolve through an exact scalar SSA reference; literal SOFFSET remains an encoded literal rather than being reinterpreted.

For `ds_write2_b32`, provenance requires current ADDR/DATA0/DATA1 VGPR identities and an exact implicit `m0` use classified as `ARCHITECTURAL_IMPLICIT_M0` / `LDS_DS_M0_BOUNDS`. The tool proves the encoded offsets and the symbolic LDS address expressions, but intentionally leaves concrete lane addresses unresolved.

## Current reproducibility blocker

The repository contains the durable provenance joiner and the later API10 fusion gate, but the default-branch code search does not expose a durable source producer carrying either the literal status `D1_GCN_SGPR_SSA_EXACT` or the field `implicit_m0_use`. Likewise the exact vector-binding status is consumed but its producer is not discoverable by status-token search.

Therefore the historical exact artifacts must **not** be treated as reproducible evidence merely because a later joiner accepts them. The missing closure is the source path that deterministically regenerates:

- the exact scalar SGPR reaching-state graph;
- exact implicit M0 SSA use at DS instructions;
- the exact final/current VGPR lane identities consumed by the vector-binding graph;
- stable program/instruction identities matching structural IR.

## Required closure test

A replacement/recovered producer is acceptable only if a clean workflow run from durable source inputs regenerates all three input corpora and the existing provenance + API10 fusion gates reproduce the frozen census without relaxing any assertion:

- 385 API10 typed-buffer reads;
- 1,540 typed-buffer result components;
- 641 LDS writes;
- 1,026 total fused operations.

Any mismatch is evidence of an unresolved producer or identity problem, not permission to weaken the gate.

## Semantic boundary after reproducibility

Even after the census is reproducible, API10 remains only an exact API-slot/resource-binding identity. Engine ownership requires an independent runtime trace:

`Material -> OrbShdr -> LocalShader wrapper -> usage record -> user-data/resource-table construction -> API10 descriptor population`

No bone-palette, transform-buffer, material-constant, or other semantic label may be assigned until that runtime construction chain is proven from Destiny 1 evidence.

## Next evidence target

Search commit/workflow history for the producer invocation and retained artifact schema rather than reverse-engineering a new schema from the consumer. If the historical producer cannot be recovered, implement a new source-closed producer directly from the already exact structural IR while preserving the consumer's existing status/schema contract, then prove equivalence by the full frozen census above.
