# Oodle 2.3 native Rust reversal checkpoint

## Reference binary

Verified research runtime:

- file: oo2core_3_win64.dll
- size: 894,752 bytes
- SHA-256: 682c0aad216fae443e0f9561876cfabfddaeffcd48e5990613ad2cf47c49fa62
- PE32+ x86-64
- PE link timestamp: 2016-07-14 14:47:10 UTC
- image base: 0x180000000
- entry RVA: 0x9f3e4
- 5 PE sections
- 60 exports
- imports only KERNEL32.dll

The DLL is not committed. tools/oodle3_pe_map.py reproduces the static inventory from a user-supplied copy.

## Public decompression path from the exact DLL

OodleLZ_Decompress is export ordinal 18 at RVA 0x5f8b0. Static disassembly shows argument/decoder setup followed by repeated calls into exported OodleLZDecoder_DecodeSome (ordinal 2, RVA 0x5e180).

This gives a clean decomposition for the native replacement:

1. public compatibility wrapper;
2. serialized block/quantum framing;
3. stateful decoder/history object;
4. codec-specific compressed-quantum kernels;
5. optional checksum/callback/thread-phase parity.

The Destiny package path already uses the whole-buffer decompression API with no callback and no caller-supplied scratch, so the first target is narrower than the complete DLL API.

## Exact compressor-name table in this DLL

OodleLZ_Compressor_GetName indexes a 13-entry table:

| ID | Name |
|---:|---|
| 0 | LZH |
| 1 | LZHLW |
| 2 | LZNIB |
| 3 | None |
| 4 | LZB16 |
| 5 | LZBLW |
| 6 | LZA |
| 7 | LZNA |
| 8 | Kraken |
| 9 | Mermaid |
| 10 | BitKnit |
| 11 | Selkie |
| 12 | Akkorokamui |

The binary also contains newLZ_decode_chunk_phase1 / newLZ_decode_chunk_phase2, Huffman/tANS-related corruption checks, and source-path strings rooted at oodle2/core.

## Framing implemented in Rust

The initial clean-room Rust crate implements the wire framing for decoder types 5, 6, 10, 11 and 12.

At each 0x40000 raw-output boundary there is a two-byte block header. Header byte 0 has low nibble 0xC, reserved bits 4-5 clear, bit 7 restart-decoder and bit 6 block-uncompressed. Header byte 1 stores the 7-bit decoder type plus checksum-enable in bit 7.

Decoder families currently represented:

- 5: LZNA-family stateful legacy decoder
- 6: Kraken/newLZ
- 10: Mermaid/Selkie shared format
- 11: BitKnit
- 12: Akkorokamui/newLZ-family format for this DLL generation

NewLZ-family quantum size is 0x40000. LZNA/BitKnit legacy quantum size is 0x4000. NewLZ compressed quantum headers carry an 18-bit stored_size-1. Legacy headers carry a 14-bit stored_size-1. Special zero-payload forms are represented as well.

## Complete now

- exact binary identity and PE/export/import inventory
- public decompressor entry and DecodeSome architecture
- exact compressor-name table for this DLL
- clean-room Rust block/quantum parser
- deterministic PE mapper for future address/string/export tracking

## Still open

- identify exact decoder type(s) used by every real Destiny package block
- Kraken entropy + LZ kernel
- Mermaid/Selkie kernel
- BitKnit adaptive entropy kernel
- LZNA kernel
- Akkorokamui kernel
- exact 24-bit checksum
- callback/thread-phase parity
- byte-for-byte differential validation across the Destiny corpus

## Implementation order

Do not port the entire DLL blindly. First census the decoder type from real D1 compressed block headers. Then implement only the codec families actually present in the PS4/Xbox package corpus. Validate every stage against the verified reference DLL and keep regression fixtures by hashes/metadata rather than redistributing game data.
