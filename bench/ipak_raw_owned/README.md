# IPAK single-RAW-block ownership benchmark

This public harness uses deterministic, synthetic payloads only.

The baseline owns the original range-read `Vec` and makes another output
`Vec` for the payload, performing the same accelerated IEEE CRC29 check.
The candidate checks the exact 1-command RAW header and data CRC and compacts
the payload to the front of the *existing* `Vec` with `copy_within` before
truncating. There is no unsafe code. Output pointer identity is tested.

The production importer has a separate full decoder; other layouts continue
through that existing decoder. **The public harness does not validate the
complete IPAK parser, LZO, filesystem access, scene rendering or import latency.**

The benchmark measures decode of already owned entry bytes plus the unchanged
accelerated CRC check, including a clone that emulates receiving each newly
allocated range read buffer. Synthetic payloads span 64 bytes to 1 MiB, and
13 alternating A/B paired rounds run in optimized release builds with fat LTO.
These are microbenchmarks, not game-load-time speedups. On shared CI hosts
absolute timing and ratios can fluctuate, particularly with allocator effects.
