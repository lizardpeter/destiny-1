# Minecraft Bedrock exact emissive conversion LUT benchmark

Bedrock MER/MERS textures store emission as an unsigned 8-bit
linear scalar. The generic PBR runtime samples an sRGB texture, so
the importer converts each source emission byte using the existing
f32 sRGB transfer function and rounds to an 8-bit result.

The original importer called `f32::powf` once per emitted pixel.
The candidate computes **the same 256 values exactly once**, in a
read-only `OnceLock<[u8;256]>`, and hoists the table borrow before
the per-pixel conversion loop. No emitted byte, color-space
interpretation, alpha, roughness, or metalness semantic is changed.

The standalone Windows/Linux benchmark uses function bodies copied
directly from original and optimized `textures.rs` and tests all
256 source bytes exhaustively, followed by source-buffer patterns
and lengths from 0 to 65536 bytes. Nine alternating A/B release
rounds time just linear-byte->sRGB-byte conversion and table lookup,
with the lazy initialization already completed. A one-time table
build therefore occurs only before the first measured lookup, not
once per texture.

[First Windows and Linux benchmark](https://github.com/lizardpeter/destiny-1/actions/runs/38018358185)

Examples for uniform-random inputs:

| Bytes converted | Windows speedup | Linux speedup |
| --- | ---: | ---: |
| 1,024 | 30.0× | 23.7× |
| 16,384 | 29.3× | 21.1× |
| 262,144 | 23.1× | 23.4× |

The end-to-end PBR import also includes file/decompression, image
loading, RGBA output, and GPU upload, none of which are measured
in this microbenchmark. No claims about Minecraft world load time
or FPS can be made from these measurements alone.

The documentation commit starts a separate independent cross-platform
repeat.
