# Oodle 3 Runtime / Reproducibility Notes

Destiny 1 ROI Tiger compressed blocks in the supplied PS4 and Xbox One packages are decoded with Oodle 3.

## User-supplied runtime used for validation

The user supplied `oo2core_3_win64.dll` at runtime. It is intentionally **not committed or bundled** in the project snapshot.

Observed file metadata for the validation runtime:
- size: 894,752 bytes
- SHA-256: `682c0aad216fae443e0f9561876cfabfddaeffcd48e5990613ad2cf47c49fa62`
- PE32+ x86-64 DLL
- exports `OodleLZ_Decompress`

## Linux research bridge

`tools/linoodle_min.cpp` is an experimental source-available PE-loader bridge created for this project. It maps/relocates the user-owned Windows Oodle DLL, provides the small KERNEL32 surface required by the DLL and exposes a native Linux `OodleLZ_Decompress` symbol.

The Microsoft CRT `DllMain` attach path in this particular DLL currently crashes under the minimal compatibility layer, before decompression. Empirically, mapping/relocating/resolving imports and invoking the exported decoder with `LINOODLE_SKIP_DLLMAIN=1` works. Because this skips normal DLL initialization, the bridge is marked **EXPERIMENTAL** even though the decompression outputs have validated across both real corpora.

Build:

```bash
tools/build_linoodle_min.sh
```

Typical invocation:

```bash
OODLE_DLL=/path/to/oo2core_3_win64.dll \
LINOODLE_SKIP_DLLMAIN=1 \
python3 tools/d1_oodle_probe.py package.pkg \
  --runtime tools/runtime/linux-x86_64/liblinoodle3_min.so --count 12
```

## Binary validation

Representative decompression tests:
- PS4 canonical package: 12/12 tested compressed blocks returned exactly `0x40000` bytes.
- Xbox One package: 12/12 tested resident patch-1 compressed blocks returned exactly `0x40000` bytes.

The output contains coherent Tiger/resource data and has subsequently been used to reconstruct validated GPU headers, GCN shader payloads and visually correct BC texture exports. This promotes D1 ROI block decompression from a blocker to a **working pipeline stage**.
