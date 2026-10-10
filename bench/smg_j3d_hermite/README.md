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
