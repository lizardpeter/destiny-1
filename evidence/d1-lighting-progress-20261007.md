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

## Final five-area source checkpoint

Final production commits include `f43f9495` (volume inverse), `b3fe1c97` (serialized BC1 sRGB cookies), `722a9e73` (f32 volume validation) and `63828b46` (explicit unresolved null-source binding diagnostic). The complete importer library suite still passes **312 tests**.

| Source area | Local records imported | Materials translated | Lighting programs |
| --- | ---: | ---: | ---: |
| Tower | 737 / 737 | 497 / 497 | 34 |
| Cosmodrome | 3,402 / 3,402 | 2,712 / 2,712 | 71 |
| Mars | 2,029 / 2,029 | 1,474 / 1,474 | 45 |
| Venus | 2,241 / 2,242 | 1,859 / 1,860 | 49 |
| Moon | 2,250 / 2,250 | 1,551 / 1,551 | 44 |

All five models validate their neutral lighting IR. There are zero unbounded records and zero unresolved engine words in these censuses. The 163-package source audit covers 258,046 current tags and 3,506 relevant source rows with zero parsing errors. Package hashes, source owners, full warning logs and compact counts are committed. These are combined destination-table source censuses using a diagnostic Tower Activity root, not actual per-map activation/environment joins or rendered fidelity checks. Raid, PvP and other destination families are not covered by this checkpoint.

The one withheld Venus record is collection `8100A280`, record 14, map table `8100A25F`, BufferData `8100A312`, material `8100A311`, pixel shader `8100EA66`. Its serialized PS t3 hash is `FFFFFFFF`. Raw flags 88/8C are `02000428` / `00000000`; no activation semantics are inferred. The importer now reports the unclosed runtime fallback directly instead of calling this a missing downloadable texture. See `d1-venus-null-cookie-source-20261007.json` and its reproducible audit script. No fabricated white/black cookie was added.

Next fidelity work remains the real Activity/environment joins, atmosphere coefficient/LUT production, live sun/environment curve updates, null-cookie runtime handling, and rendered map comparisons. The R2 source-audit helper now hashes large package objects as a stream; all 147 previous package identities and source rows agreed with the earlier full-buffer audit.

## Atmosphere arithmetic and ownership checkpoint

New source-backed research commits: `151486e5` / `dabe0a11` (mode-2 oracle), `b3b08e64` / `4f8b47ab` (general path and imported helper), `7a68f367` / `83d73077` (settings owner/copies and pointer accessor), `4a9f2e78` / `d295fdcf` (cyclic LUT selection).

- Five mode-2 cases reproduce native float results exactly, including normalized coefficients, degree conversion, epsilon clamps and equal-bound separation. All other block bytes are unchanged.
- Twenty general-path cases verify native matrix/coefficient arithmetic and the two exponential call arguments. The executable import `8zsu04XNsZ4#w#r` resolves to `expf` by its exact SCE PLT relocation, calculated NID and pinned emulator mapping. The probe explicitly substitutes host `libm` for that import; retail libc bitwise rounding is not established. The matrix scalar is `inverse(input_matrix)[3][2]`.
- Thirty-three cyclic LUT selection cases establish the first inclusive interval rule, duplicate phase handling, atlas offsets `slot/16`, and the wrap branch: add one to the upper endpoint when it is below phase, otherwise subtract one from the lower endpoint. This covers exact boundaries and refusal when no interval contains the input phase.
- Global settings owner `0x2709aa0` allocates 0xF0 bytes. Its registered type object is `0x28d75b0`, name-hash registry entry `09FBE029`. Reset/init mode is 3; tag load zeroes a 0x90-byte temporary and copies 0x88 bytes from the supplied data pointer +0x0C, leaving mode and optional texture override zero. Accessor `0x78970` simply returns handle +0x08 and ignores the passed type-ID argument; it does not validate a serialized class. The data pointer's relationship to the serialized payload base remains unclosed. Setter preserves runtime channel indices. Renderer callbacks snapshot 0xF0 bytes into renderer +0x191F8, then context constructors copy to context +0x34. Both producer call paths use that context settings block and view +0x500.

These findings are saved with complete scripts and disassembly evidence in `uregraph` as well as Git. The production identity atmosphere provider has not been replaced: serialized source class ID, actual map joins, live channels, input view-matrix ownership and LUT texels still require closure. No rendering or screenshot comparison was performed in this checkpoint. The previously passing 312-test importer suite remains the latest production test result; no production code changed for these research probes.

## Global-channel Rand production follow-up

Production commit `21d6b276` replaces the remaining folded Rand formula in `global_channel_sequencer.rs` with the shared retail helper. The first fifteen native cases happened to agree with the old formula, so the native probe was expanded with fourteen summation-order witnesses. The new sequencer regression fails before the fix at input 5 (`40A00000`): old result `3F0BD578`, source result `3F0B4E58`. After the fix the full importer library suite passes **313 tests, zero failures**, including all 29 native bit cases and x-only broadcast checks. Native oracle commits are `088621c7` and `6d4a5b2e`; validation logs are committed in `d1-global-channel-rand-fix-validation-20261007.json` (`d98f7024`). This validates CPU sequencer arithmetic and does not establish runtime channel activation or rendered image fidelity.

## Gradient and spline arithmetic fixes, with independent native regressions

Two additional importer paths were corrected and committed:

- Gradient4/8 now read the source-initialized tolerance bits `38D1B717` (about 0.0001), matching RODATA `1610BE0` copied to BSS `1AC6320` by `94813/9486E/948D7`. Both the universal IR lowering and resolved global-channel evaluator previously used an assumed 0.000001.
- Both paths preserve separate MUL/ADD rounding, combine Gradient8 banks per lane, and use the retail pairwise reduction. Ninety independent native cases include tolerance boundaries, duplicate and descending thresholds, differing input lanes, and cancellation witnesses. Both new regressions failed before the fix and passed afterward.
- Cubic spline IR lowering now XORs adjacent reached masks and XOR-reduces selected result bits for opcodes 37/38/39. The previously duplicated two-bank lowering shares the corrected helper. Ninety native cases cover normal, duplicate and unsorted thresholds and differing input lanes. The IR regression failed before the fix; the resolved sequencer already matched these cases.

Private commits: gradient fixtures `ccf4f931`, IR `58f31196`, sequencer `ddb14095`; spline fixtures `4d66cc69`, IR `d42401c0`, sequencer regression `15ab2699`.

The full importer library suite passes **317 tests, zero failed**. These fixes affect the common D1 interpreter paths across maps; they do not constitute rendered validation. Full before/after logs and source-pinned native evidence are committed in `d1-gradient-importer-fix-validation-20261007.json`, `d1-spline-importer-fix-validation-20261007.json`, and their native-oracle files, and complete source/evidence is checkpointed in uregraph.

## Tower source ownership scopes after dependency restoration

The recovered archive contains **85 package snapshots / 90,513 current tags**. Additional missing resources were restored through exact inventory-selected R2 objects; acquisition manifests pin every downloaded object and SHA256.

The actual scenario root `80C7A005` (class `80800616`) closes the placement and sequencer-resource join: **274 runtime placements / 47 unique entities**, six scenario entity-layer tables, and two sequencer resources `809DF584/809DF585`, both with zero program entries. These entity tables contain zero local-light records.

The separate destination map root `80C98019` (class `8080052E`) closes its bubble/container/table graph to **122 tables**. Its broader census resolves **737/737 local lights / 497/497 materials**, 34 lighting programs, and valid lighting IR. Across that combined bubble graph the importer sees 58 environment entities / 66 resources and evaluates 71 channels, with overlapping owners and 16 channel names absent from current defaults. The first selected sun is `80CA0DED`, cycle 7200 seconds, phase zero.

These are distinct source scopes. A combined destination graph is not one active rendered bubble; scenario entity tables alone do not contain the destination's world lighting. The map root has an 84-byte map layout and cannot be parsed as the scenario's +48 location array. Live scalar0 meaning, descriptor construction, output-slot ownership/update order, active-world/scenario composition, atmosphere settings/LUT textures, shadow masks, and per-frame evaluation remain open.

The audit tool now exposes `--scenario-tables` and `--map-tables` and prints its scope explicitly. Structured observed counts are committed in `d1-tower-root-scoped-source-census-20261007.json`. The full local logs were inspected; the local execution service later stopped responding before their raw files could be archived, so the structured count checkpoint explicitly records that limitation.

## Actual sequencer VM cross-check checkpoint

The separate sequencer VM is `237710`, opcode jump table `239138`. Its own Rand/Spline4/Spline8/chain/Gradient4/Gradient8 handler entries were recovered at `238085/238B2F/238BA9/238C95/238D9C/238EC4`. A targeted CI job now executes these native handlers against the existing 209 material-TFX witnesses. That additional run is pending; it must not be described as passed until its result is retrieved. The owned executable is pinned and removed before artifact upload. Source scalar and runtime ownership semantics remain unclosed regardless of arithmetic equivalence.
