# D1 LocalShader API10 primary-capture contract

Status: source-closed structural gate; engine semantics intentionally withheld.

## Frozen producer chain

The API10 access-family membership is rebuilt from two independently exact upstream reports before a runtime capture is admitted:

- `D1_GCN_LOCALSHADER_TBUFFER_USAGE_BINDING_V1.json`
  - SHA-256 `6c6c07d03ed06d8b53693326cbabd9fde7c7a2f7b0c41e02939e700cf4f21127`
  - Actions artifact `10172731401`
- `D1_GCN_LOCALSHADER_API10_MATERIAL_CHAIN_V1.json`
  - SHA-256 `23415246337abdbb1543447e0123fa809027e3b9e94d5efee12a1476e7a2a113`
  - Actions artifact `10529319011`

The deterministic producer is `tools/d1_gcn_localshader_api10_access_family_census_v1.py`. Its previously verified v2 output is Actions run `35326707035`, artifact `10539900120`, uploaded ZIP digest `b64ddfd28937c6d5adddf8464817da6f836fd32c1b3e20e1b51841ce3d185897`.

The capture workflow now rebuilds the v2 membership from the two pinned upstream byte streams and byte-compares it with the previously verified artifact. Artifact expiry is therefore not semantic authority: if a frozen artifact disappears, reconstruct its producer inputs and require byte-equivalent output or stop.

## Exact structural denominator

The current source-closed denominator is:

- 39 unique GCN program SHA-256 identities;
- 56 wrappers;
- 3,386 material occurrences;
- program TBUFFER histogram: 3 -> 1, 6 -> 1, 8 -> 17, 12 -> 20;
- descriptor entry windows: `s[8:11]` and `s[12:15]`;
- six exact (TBUFFER count, descriptor-window) families.

These are structural facts only. Slot reuse does not assign engine meaning.

## Primary capture admission

`tools/d1_localshader_api10_capture_gate_v1.py` requires a primary capture to:

1. identify an exact member program by its GCN SHA-256;
2. agree with the source-derived TBUFFER-count/window family for that program;
3. provide exactly four u32 descriptor dwords;
4. provide a SHA-256 for the primary evidence stream;
5. cover the exact family contract before the corpus is called complete.

`TEST_FIXTURE_NOT_PRIMARY_EVIDENCE` rows are rejected by default. They are admitted only with the explicit `--allow-test-fixtures` regression-test switch and can never assert an engine semantic.

## Unproven boundary

No engine semantic is currently assigned to API10. To cross that boundary, primary evidence must bind an admitted exact GCN program to the actual command/user-data writer and retain the written descriptor dwords. A semantic claim additionally requires provenance to the descriptor's backing allocation/bytes. Until both writer trace and backing bytes exist, runtime writer, backing allocation, and engine semantic remain WITHHELD.

Do not infer bone, transform, material, tessellation, or other meaning from the API number, SGPR window, TBUFFER count, or slot reuse.
