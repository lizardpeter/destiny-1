# D1 native Oodle LZH decoder

Clean-room Rust implementation work for the legacy Oodle 3 LZH stream used by
the validated Destiny 1 ROI Tiger package corpus.

## Proven so far

- Validation runtime: `oo2core_3_win64.dll`, 894,752 bytes,
  SHA-256 `682c0aad216fae443e0f9561876cfabfddaeffcd48e5990613ad2cf47c49fa62`.
- D1 compressed blocks beginning `B7` parse to Oodle decode type **7**,
  subtype **0**.
- The DLL's decode-type mapper maps type 7 to compressor enum **0 = LZH**.
- The subtype-0 conservative LZH core is at VA `0x180075DC0`; its
  overread-optimized sibling is at `0x180078B20`.
- One Huffman codebook is constructed with **713 symbols**.
- Symbols 0..255 are literals.
- Symbols 256..712 map through a **457-entry** match descriptor table.
- That table is generated in `src/lib.rs` as:
  - 20 repeat-distance length classes; plus
  - 19 length classes x 23 explicit-distance buckets.
- Initial recent distances are `[20, 24, 28, 32]`.
- Base match length 157 is an escape class with a wider prefix-coded extension.

## Current frontier

The remaining blocking component is the serialized Huffman codebook reader used
to populate the 713-symbol decoder. The relevant verified DLL path is:

- LZH codebook setup: `0x18005D5E0`
- Huffman object/layout allocation: `0x18006BAD0`
- serialized codebook reader: `0x18006C5E0`
- subtype-0 token loop: `0x180075DC0`

Once that reader is behavior-matched, the token loop can be implemented using
the already-modeled descriptor and distance/length semantics and tested
byte-for-byte against the existing `d1_oodle_probe.py` corpus oracle.

The proprietary DLL is never committed or linked by this crate.
