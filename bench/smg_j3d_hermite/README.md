# SMG J3D Hermite animation keyframe search

The private SMG J3D/BCK/BRK/BTK/BPK animation sampler calls
`sample_track` for many authored floating-point animation curves.
Previously, finding the first key with a time strictly greater than
the requested frame scanned from index zero on every call.

The candidate preserves that exact linear sampler for short tracks,
early frames and non-finite (NaN/Inf) authored keyframe times.
For sorted, finite tracks with at least 96 keys, it uses
`partition_point` only when the requested frame lies after the 64th
source key. This avoids the severe performance regressions observed
when using binary search on early frames or short tracks.

We compile the exact original and optimized `j3d_animation.rs` source,
with benchmark-only wrappers that construct identical keyframe tracks.
Bitwise identical Hermite output is asserted on thousands of frames,
duplicate timestamps and special frame values, with additional
source-module tests. Seven alternating median A/B release rounds
benchmark early frames, widely distributed frames and terminal frames
on Windows and Linux.

This is an isolated interpolation benchmark, not whole-frame GPU/CPU
timing, a retail replay capture or a scene import performance claim.
Unusual authored non-finite timestamps follow the original linear
path rather than binary search. The benchmark does not include all
animation object allocations or scene traversal.

The initial unconditional binary-search experiment demonstrated
regressions on early frames. The adaptive method was chosen only
after that failure and source parity checking; a separate runner
repeat is triggered by this note.

## First adaptive, cold-helper source run

The candidate keeps binary lookup in a separate `#[inline(never)]`
helper so the original linear sampler remains the hot early-frame
fallthrough. Both platforms passed 11 source-module tests and bitwise
output comparisons:
https://github.com/lizardpeter/destiny-1/actions/runs/38017144548

Warm synthetic interpolation ratios (old duration divided by new):

- 128-key full-range frames: Windows 2.05×; Linux 1.74×.
- 128-key terminal frames: Windows 5.50×; Linux 3.97×.
- 512-key full-range frames: Windows 5.88×; Linux 4.06×.
- 512-key terminal frames: Windows 17.68×; Linux 11.25×.
- 128-key early frames: Windows 0.94×; Linux 0.97×.
- 512-key early frames: Windows 0.93×; Linux 0.99×.

Thus even the adaptive implementation has a small **Windows
early-frame regression**. The benefit is confined to late/distributed
sampling on long curves; real frame-time outcomes require recording
actual per-track sampling distributions and total game perf.
These ratios do not include J3D scene, GPU, shader or draw costs.
