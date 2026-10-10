# BO2 T6 world light-grid RLE ownership seek benchmark

The original `T6WorldLightGridRuntime::entry_index_at_grid_coord`
scanned the decoded RLE runs in order for every exact source-grid
sample. Every row is validated to consist of strictly increasing,
gap-free column runs, so a binary seek is legal without changing
which serialized `GfxLightGridEntry` owns any integer coordinate.

The candidate uses an out-of-line `partition_point` lookup only
for **64+ run rows at columns beginning with run #32**. All
short rows and early coordinates retain the original linear scan.
This conservative dispatch followed earlier A/B benchmarks showing
unconditional binary search was substantially slower for early
columns, even in very broad rows.

The public benchmark builds **the actual original and optimized
runtime module sources** with `rustc`; every RLE row uses the real
production `validate` function. Synthetic canonical source rows
with 1–512 runs and one or four columns per run are checked for
identical entry owners at every column and boundary, including
out-of-range columns. The optimized source's real unit tests run
independently on Windows and Linux.

Seven alternating release A/B rounds measure first-four-run/early,
uniform and final-run coordinates for 500,000 or 250,000 queries.
These numbers measure only grid-to-RLE entry lookup, not retail
rendering, lighting quality, Vulkan draw submission or FPS. No
Nuketown or proprietary asset is published.

First adaptive Windows and Linux benchmark:
https://github.com/lizardpeter/destiny-1/actions/runs/38018021616

A separate independent Windows/Linux repeat is triggered by this
documentation commit. Since the number of RLE runs in live maps
has not been profiled, no overall frame-time improvement can yet
be claimed.
