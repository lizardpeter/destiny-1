# D1 reversal checkpoint — API10 provenance + PS4 sampler hardening

This checkpoint records only evidence-backed changes from the 2026-09-18 continuation session.

## API10 transaction

The exact API10 population remains 39 GCN SHA-256 identities / 56 wrappers / 3,386 material occurrences and six `(TBUFFER count, descriptor window)` families. No engine semantic was promoted.

`tools/d1_localshader_api10_capture_gate_v1.py` now closes a provenance loophole that previously treated arbitrary truthy `writer_trace` and `backing_bytes` values as sufficient structure for semantic promotion. Primary capture evidence must have a non-empty source plus exact 64-hex SHA-256. A semantic promotion additionally requires **two independently hash-addressed evidence records**, one for the writer trace and one for backing bytes; the same `(source, sha256)` record cannot satisfy both proof legs.

Synthetic policy regression tests live in `tests/test_d1_localshader_api10_capture_provenance_v1.py`; they are explicitly not runtime evidence. CI run 35347016720 completed successfully after the policy tests were wired into the exact-membership reconstruction gate. Earlier run 35346976594 also completed successfully after the validator hardening.

The hard semantic boundary is unchanged: an admitted retail program must still be observed with its actual user-data/command writer and exact four descriptor dwords, and semantic promotion requires independently retained backing-allocation bytes. API number, SGPR window, TBUFFER count, ordering, and slot reuse remain non-semantic.

## Pivot transaction — PS4 sampler decoder

Because no new primary runtime writer capture is present in the repository, work pivoted to the already retail-backed PS4 sampler layout.

`tests/test_d1_ps4_sampler_probe.py` freezes the three recovered retail descriptor vectors already documented in `spec/D1_MATERIALS_SHADERS.md`:

- main 2D: `00000000 00F00000 0A503F80 00000000`;
- main cube: `00000092 00F00000 0A503F80 00000000`;
- circuitry: `000001B6 00F00000 0A503F80 80000000`.

The regression checks raw words, wrap-field values, LOD raw fields, signed 14-bit bias, filter fields, border value, malformed size, and declared-size mismatch. CI run 35347044845 passed the initial vector suite.

The probe was then hardened so a 24-byte blob is not decoded merely because its size resembles class `80801A42`. `decode_validated_class()` requires the validated class hash before applying the layout, and package probing emits `decode_withheld` for same-sized/non-matching classes. The class gate is regression-tested with a synthetic `DEADBEEF` class. CI run 35347093225 passed the class-aware decoder implementation; the follow-up test commit is `184ad0d04415dee0cb847c30d54a633020101ca1`.

Source-correlated Gnm enum labels remain convenience labels; raw descriptor words are canonical retail evidence.

## Resume gates

1. API10: obtain primary writer trace + exact descriptor dwords for one of the 39 admitted GCN identities; retain independently hashed backing bytes before any engine-semantic promotion.
2. Samplers: if expanding beyond the three target vectors, build a retail-byte census keyed by class `80801A42` and preserve each tag hash + raw 24 bytes; do not infer material role from descriptor equality.
3. Next source-closed pivots with existing evidence: render/blend-state ownership for circuitry, `b12`/`b13` producer provenance, shader interface/vertex-stage evidence, or promotion of existing skeleton/animation decode into a reusable exact exporter.
