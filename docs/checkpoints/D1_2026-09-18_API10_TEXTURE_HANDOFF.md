# Destiny 1 checkpoint — API10 membership recovered / runtime evidence pending

Branch: `d1-crota-source-semantics-v1`

## LocalShader/API10 hard gate

The exact frozen 39-program census has been recovered and is now repository-resident. This closes membership identity only. It does **not** prove the runtime command/user-data writer, the four descriptor dwords, descriptor backing allocation/bytes, b12/b13/global producer chains, LocalShader/tessellation engine ownership, or any engine semantic for the API10 access family.

Do not infer any of those from API number, SGPR window, TBUFFER count, program ordering, adjacency, or slot reuse. The next admissible semantic advance requires a primary runtime capture tied to an exact recovered census GCN identity, with writer provenance and backing bytes/range evidence.

If that capture is unavailable, remain WITHHELD and pivot.

## Texture pivot

`tools/d1_texture_export_v2.py` is the production fail-closed entry point. Its resolver accepts only the already evidence-backed structural shapes encoded by `d1_texture_backing_chain_v1.py`: direct `32:1 -> 1:1`, two-hop `32:1 -> 65:1 -> 5:1`, and observed direct cube `32:2 -> 1:2`. These are structural storage classes only; this checkpoint assigns no official Tiger semantic names to `65:1` or `5:1`.

Regression `tools/test_d1_texture_export_v2_strict_manifest.py` additionally proves that a direct `1:1` terminates even if its own reference resolves, that `65:1` may not terminate in an arbitrary class, and that an unproven cube two-hop chain remains rejected. Synthetic records in that regression are control-flow fixtures, not retail evidence.

## Resume

1. Read current branch head; never reset newer concurrent Destiny work to this checkpoint.
2. Attempt the API10 primary runtime-capture gate first.
3. If unavailable, continue source-closed texture/package/geometry/material work.
4. Preserve exact denominators and WITHHELD semantics; do not weaken validators to obtain green CI.
