# D1 Spektar / Tiger variable Oodle block sizing breakthrough — 2026-09-05

The four unresolved Spektar texture headers in package family `013F` were not corrupt and were not generation/patch-slot mismatches.

Affected headers:

- `80A7FB3B`
- `80A7FB3E`
- `80A7FE41`
- `80A7FE47`

They share the same physical compressed Tiger block from `ps4_investment_assets_013f_1.pkg`.

## Exact finding

The block's serialized FileEntry coverage ends at `0x351EC` (217,580 bytes). D1 Oodle package blocks use a `0x4000` decompressed-size allocation quantum. The first legal raw size covering that serialized extent is therefore:

```text
align_up(0x351EC, 0x4000) = 0x38000 = 229,376 bytes
```

`OodleLZ_Decompress` succeeds at `0x38000` and fails when incorrectly forced to the nominal Tiger logical block capacity `0x40000`.

Recovered block SHA-256:

```text
edd5babd57d338b75c7de79e6d937fb37a01953576e7f7d5b2ebf6679e505e87
```

The same rule is independently corroborated by unrelated D1 Tower package blocks and by an external `oo2core_3` package implementation that probes unknown raw block sizes in `0x4000` steps.

## Oodle flags are not the issue

A call matrix compared the project's historical Oodle flags against Charm's D1 Rise of Iron package call (`fuzzSafe=0`, `checkCRC=0`, `verbosity=0`, `threadPhase=3`). Both produce byte-identical outputs for a known-good full block and the recovered `0x38000` block. The material variable is raw output length, not call flags.

## Canonical reader rule

For a logical snapshot:

1. Compute the maximum serialized FileEntry end touching each logical block.
2. Round that end upward to `0x4000`.
3. Cap at the Tiger logical capacity `0x40000`.
4. Decode compressed Oodle blocks with that exact raw length.
5. Require the decoder to return exactly that length.
6. Zero-pad only after successful decode so existing logical block addressing remains `0x40000`.
7. Continue to require stored-block SHA-1 before decode.

This rule is now integrated into `tools/d1_entry_extract.py` and `tools/d1_remote_investment_parent_probe.py`; `tools/d1_entry_extract_sized.py` remains a specialized evidence-heavy implementation of the same format rule.

## Spektar consequence

The four missing texture headers are no longer considered missing/corrupt assets. The exact texture-plate build should be rerun with the corrected reader. The target remains 159/159 exact source textures feeding the five masculine Spektar armor plate headers:

- `80A82BA3`
- `80A85683`
- `80A85F6C`
- `80A8402F`
- `80A7DC27`

No fallback or lookalike texture substitution is permitted.
