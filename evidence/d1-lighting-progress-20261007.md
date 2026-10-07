# Destiny 1 lighting and texture checkpoint — 2026-10-07

Production repository: `lizardpeter/Rust-test`, default importer path. No legacy fidelity implementation was changed. This checkpoint records source and IR validation; no rendered screenshot comparison was performed.

## Committed production fixes

- Preserve authored shader texture dimensions, mip levels and cube faces instead of applying the preview size cap (`517a14da`, with fixture/CI follow-ups).
- Rebuild GlobalLighting settings words 38..41 from executable defaults `[0, 0, 1, 1]` (`b5ffd477`). Live settings overrides remain uncaptured.
- Use the source sun component's initial phase for lighting and material TFX, and the verified Frame +0x1C default of 20 (`6aebe9e`, `184a829e`, `b99a4fe9`). Per-frame sun curve re-evaluation remains open.
- Lower retail Rand opcode 0x2A without reassociating its coefficient multiplies or summation; synchronize the CPU/light helpers (`b53d734f`, `c5ccd487`, `b33a13d9`, `89ae87a4`). Verified against 15 native executable arithmetic cases.
- Reconstruct DeferredLight matrix element 8 from the authored volume, instance and camera transform (`f43f9495`). Twelve native arithmetic cases prove `inverse(volume * instance * translation(-camera))`, including projective volumes. Import uses f64 pivoting narrowed to f32 constants; mathematical equivalence is checked with tolerance, not asserted bit-identical.
- Include serialized material light-cookie texture registers and decode authored BC1 sRGB cookies through the shared decoder (`b3fe1c97`). This closes the two cookie textures needed by 14 previously withheld local lights. Lighting texture mip residency is not established by this top-level texture path.
- CI now runs the complete importer library suite (`c5cdb95b`). Corrected stale source fixtures/oracle scope in separate commits (`e60edd60`, `35ed33ae`).

## Reproducible verification

`cargo test --manifest-path asset_import/importers/destiny1/Cargo.toml --lib`: **311 passed, zero failed**.

The 66-package R2 snapshot is identified by every object's size and SHA256 in `d1-r2-lighting-source-audit-20261007.json`. It contains 60,309 current tags, 144 relevant source rows and zero source audit errors. The executable SHA256 is `672f03411c0503dfbcda804cbb9fb27cdd9a8d73a8bcb71bf0c4f688073b0833`.

Copy `tools/d1_lighting_importer_source_audit.rs` into `asset_import/importers/destiny1/examples/lighting_source_audit.rs`. Build with `RUSTFLAGS='-L native=/absolute/runtime' cargo build --manifest-path asset_import/importers/destiny1/Cargo.toml --example lighting_source_audit`. The runtime requires the owner-provided Oodle 3 DLL and verified linoodle bridge, with `LD_LIBRARY_PATH` set to that directory. Run from that directory with the package directory followed by these table hashes:

`80C984AA 80C9802C 80C984A3 80C98960 80C98A30 80C997E1 80C9995A 80CA0B12 80CA0C05 80CA0C51`

This is a broad census of every light-collection owner found in the recovered Tower destination families, with a source sun component. It combines source tables and does not claim that a single playable map activates all these records simultaneously.

Final production importer census: **737/737 local lights, 497/497 local light materials, 34 lighting programs, 92 light constant programs, five lighting textures, zero unbounded records, zero translation failures, and zero unresolved engine words**. A global sun adds one SceneLight. See `d1-lighting-importer-source-census-20261007.log` for all warnings and counts. Legacy flags were unset.

## Remaining fidelity work

- Activity root `80C98019` is 84 bytes and cannot supply the Activity +0x48 location array expected by the live sequencer join. The source boundary must be resolved rather than guessing channel indices.
- Atmosphere producer `0x8426c0` and 24 channel routes are recovered. Nineteen channel names join exact current defaults; five do not. Nonlinear coefficient transforms, map settings ownership, camera transforms, LUT generation and live channel values remain open. Current production atmosphere is still the reported identity provider.
- Screen-space ambient occlusion, live settings overrides, dynamic curve updates and rendered comparisons across destinations remain unvalidated.

Source assets and executable bytes are not redistributed by these scripts or evidence files.

## Cosmodrome expansion checkpoint

Recovered 21 initial Cosmodrome destination snapshots and 13 shared dependency snapshots. The 100-package source audit identifies 127,428 current tags, 956 relevant source rows and zero source parsing errors. The initial inventory filter omitted the hexadecimal destination family `026d`; it is being added, so this result covers the 42 recovered light-collection tables rather than all Cosmodrome content.

The exact authored sun component `80CEC1A2` points to `80CEC1A4`, cycle 3600 seconds, initial phase 0.7699999809265137. The phase fix is exercised on real nonzero source data.

Production commit `722a9e73` fixes a cross-destination import abort: source collection `80CEABCE`, record 41, has a reciprocal difference of 80.0000114440918 versus the equation's 80.0. The validator now retains its 1e-5 near-zero floor and adds a two-f32-epsilon scale allowance. Non-finite and materially incorrect values remain rejected. Exact source entry identities and arithmetic are in `d1-light-volume-rounding-source-20261007.json`; the full importer suite now passes **312 tests**.

The recovered 42-table Cosmodrome census translates **2,250/2,250 local lights and 1,788/1,788 materials**, with 65 lighting programs, 364 constant programs, six textures, zero unbounded records and zero translation failures. See `d1-cosmo-lighting-importer-source-census-20261007.log`. This synthetic source census uses the Tower Activity root as a diagnostic placeholder; it does not close actual Cosmodrome Activity/environment joins or rendered image fidelity.
