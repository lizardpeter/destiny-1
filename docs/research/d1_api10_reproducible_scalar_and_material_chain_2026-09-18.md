# D1 API10 reproducible scalar + material chain — 2026-09-18

This checkpoint records two source-closed closures. It does not promote API10 runtime ownership or fetched values.

## Scalar/M0 provenance is reproducible again

Historical source recovery established that `tools/d1_gcn_sgpr_ssa_v1.py` is the exact checked-in producer; it was not lost. `tools/d1_gcn_resource_lds_rebuild_v1.py` now regenerates all scalar/M0 SSA directly from the 65 pinned structural IR programs before invoking the existing resource/LDS provenance gate. The historical scalar artifact is no longer a trust input.

Workflow run `35301499525` succeeded from commit `f1432d6f083fc2f729e6a76835ff26abed83b432`; artifact `10530431434` (`D1-GCN-RESOURCE-LDS-REBUILD-V1`, digest `sha256:e0b93db8bde16bf68bbc0705d288b27e12679de2463c3245e418270019e9ddc8`) contains the regenerated 65 scalar reports and joined provenance.

Frozen reproduced census, without weakened gates:

- 65/65 programs exact
- 10,858 structural instructions
- 385/385 `tbuffer_load_format_xyzw`
- 641/641 `ds_write2_b32`
- 1,026/1,026 exact symbolic provenance instructions
- zero provenance violations
- 385 concrete resources still unresolved
- 641 external lane/LDS allocation states still unresolved

The first run `35301460211` already regenerated the complete exact corpus successfully; only a newly-added CI assertion used obsolete coverage key names. The assertion was corrected to the actual frozen schema, and run `35301499525` passed end-to-end. No analyzer or denominator was changed to obtain the pass.

## Material → LocalShader wrapper → GCN → API10 chain

`tools/d1_gcn_localshader_api10_material_chain_v1.py` joins three independently frozen exact corpora by exact identities:

1. retail material owner frontier (`shader_header_absent:MATERIAL:SLOT:TARGET`),
2. exact 32:11 wrapper → 1:11 OrbShdr LocalShader reference proof,
3. exact LocalShader typed-buffer usage binding.

Workflow run `35301666961` succeeded from commit `bcb8b4bc33454639d04c3d23d055a0dcbab51928`; artifact `10529319011` (`D1-GCN-LOCALSHADER-API10-MATERIAL-CHAIN-V1`, digest `sha256:000649c14e93ce7c17180779f2bc380668d2157e0ed84c1426665b6541cd0b14`) freezes the complete join.

Exact result:

- 177 proven LocalShader wrappers account for 3,967 retail material occurrences.
- 56 of those wrappers map to the 39 GCN programs that perform the 385 exact API10 typed-buffer reads.
- Those 56 wrappers are referenced by exactly 3,386 unique retail material entries.
- All 3,386 references originate from the serialized material `VS` slot. This is retained strictly as serialized-slot provenance and is **not** promoted to a hardware VertexShader stage; the referenced OrbShdr binaries are independently proven LocalShader stage 3.
- Each joined row retains exact material identity/package/logical view/payload hash, wrapper identity, native program reference, GCN SHA-256, descriptor window, typed-buffer instruction count, and `ImmConstBuffer` API slot 10 identity.
- Runtime binding-owner promotions remain zero.

## Next hard gate

The chain is now exact through:

`retail Material -> serialized slot -> 32:11 LocalShader wrapper -> 1:11 OrbShdr LocalShader -> exact GCN program -> program-entry descriptor window -> ImmConstBuffer API slot 10 -> exact typed-buffer reads`

What is still unproven is the runtime producer of the API10 descriptor/backing allocation. The next admissible promotion requires primary evidence for the code/data path that constructs the LocalShader user-data/resource table and writes the descriptor corresponding to API slot 10. Required evidence is an exact association between the proven wrapper/program/material identity and the runtime descriptor population (descriptor bytes or equivalent source-closed construction record). Until that exists, API10 backing address, buffer layout, numeric contents, engine semantic name, and any bone/material/transform interpretation remain withheld.
