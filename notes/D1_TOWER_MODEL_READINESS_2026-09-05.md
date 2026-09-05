# Destiny 1 Tower model readiness — 2026-09-05

This checkpoint supersedes earlier rough Tower-completeness estimates. It records only evidence-backed reconstruction state.

## What is solved

### Exact map ownership and outer placement

Successful Actions run `33945026693`, artifact `9963094560`, parsed the shipped `SMapDataTable -> SMapDataEntry -> ResourcePointer -> SMapDataResource -> SStaticMapParent -> SStaticMapData` chains.

For the ten minority baked-static rows under the nine strict current Tower map tables:

- `SMapDataEntry +0x88` is a non-null relative ResourcePointer;
- pointed class is exactly `80801AEA`;
- resource `+0x0C` resolves to class `80801AC6` StaticMapParent;
- parent `+0x08` resolves to class `808008B4` StaticMapData;
- every target row has rotation `[0,0,0,1]`;
- every target row has translation `[0,0,0,1]`;
- every target row has WorldID `FFFFFFFFFFFFFFFF`.

Therefore these baked-static cells are authored in the same map coordinate frame. There is no unresolved per-cell outer placement transform before assembly.

Canonical evidence: `evidence/d1_tower_map_owned_outer_chains_confirmed.json`.

### Normal D1 baked-static geometry format

`80CA0B70 -> 80CA0B96` is fully binary validated:

- 123 exact 0x40 transforms;
- 4 static tables;
- 124 mesh records;
- 124 info records;
- 556 placed geometry references;
- every transform index 0..122 referenced;
- all required buffer targets present;
- 22 exact material hashes.

Validator v2 additionally proves that `Vertices1 == FFFFFFFF` is a legitimate null secondary stream. V0 and index remain mandatory.

### Geometry dependency coverage

Across the nine map-owned D1-static children whose current payloads are parseable in the preserved validator corpus:

- 8,552 mesh records;
- 8,255 mesh records already have all required buffers: **96.53%**;
- 40,373 serialized placed-geometry references;
- 38,276 references already point to buffer-complete meshes: **94.81%**.

This is a dependency-availability measurement, not a claim that a whole Tower GLB already exists.

Targeted package closure is unusually favorable:

- add `0157` -> **97.28%** placement readiness;
- add `0157 + 01CF` -> **99.10%**;
- add `0157 + 01CF + 01D1` -> **99.36%**;
- add `00EF + 0157 + 01CF + 01D1` -> **99.90%**.

Canonical evidence: `evidence/d1_tower_dependency_closure_priority.json`.

## Important correction: 80C98258 is not an alternate layout

The old validator report made `80C98258` appear structurally different. That conclusion was caused by an invalid cross-class generation fallback.

Physical history of the same TagHash:

- `_0`: class `80801AF2`, 496 bytes;
- `_1/_2`: class `80801A90`, 19,912 bytes;
- `_3/_4/_5`: class `80801B75`, 48,084 bytes.

The current `_3/_4/_5` payload hits an Oodle extraction failure. Legacy `Corpus.payload()` then fell back to the decodable `_2` payload even though `_2` is class `80801A90`, and parsed those bytes as if they were current `80801B75` D1 static-map data. The resulting zero transform hash / dynamic-array failures were fake symptoms.

Validator v3 (`tools/d1_tower_map_schema_validate_v3.py`) fixes this by making fallback class-stable: the newest occurrence defines the current class, and older payload bytes may be used only when their FileEntry.Reference matches that class.

Canonical correction: `evidence/d1_tower_80c98258_generation_class_correction.json`.

Current honest status for `80C98258` is therefore:

`CURRENT_CLASS_PAYLOAD_UNRESOLVED_DUE_TO_OODLE_EXTRACTION_FAILURE`

—not “alternate static-map layout.”

## Oodle failure is block-level

In `ps4_city_tower_destination_024c_5.pkg`, eight unrelated resources beginning in logical block 725 all fail the same Oodle decode, including:

- `80C98258` (`80801B75`);
- `80C9825A` (`80801A90`);
- `80C9825D` (`80801A90`);
- four `808004E6` resources;
- `80C997DE` (`808009A2`).

Other current `_5` failure clusters occur at blocks 710 and 763. This strongly localizes the problem to block handling rather than the `80C98258` asset schema.

A tiny diagnostic workflow, `.github/workflows/d1-tower-024c5-block-flag-diagnostic.yml`, was added to recover only the 1.68 MB `_5` member and report the exact raw block table fields for those failing logical blocks. Its first run was prevented from executing by the current GitHub hosted-runner provisioning incident; no workflow step ran.

The public `v4nguard/tiger-pkg` D1 ROI reader was also checked as a source-derived implementation reference. Its D1 block reader only promotes flag bit 0 as Oodle compression and invokes the same Oodle 3 ABI/arguments used by this project. Therefore no encryption semantic is being promoted from our generic flag labels without actual D1 block evidence.

## Export status

There is **not yet a finished Tower GLB**.

The prior first-cell workflow did not reach export because it recovered an incomplete patch corpus. The later validator proved that the correct first-cell corpus needs the full `0250_0..5` family plus `009F_0/1/2/4`.

The corrected exporter now uses:

- raw Tiger 0x40 matrices in their shipped column-vector convention;
- validator-v2 null-V1 handling without fabricated bytes;
- exact serialized StaticInfo -> transform ranges;
- exact material identities as provenance.

A two-cell workflow is committed to export:

- `80CA0B70 -> 80CA0B96` (556 placements), and
- `80CA0C60 -> 80CA0C6B` (1,596 placements), once the single missing `0157` buffer `80AAE174` is recovered.

The workflow itself is currently blocked before step 1 by GitHub hosted-runner provisioning, not by decoder assertions.

## Immediate model path

1. Recover `0157_0/_1` and close `80AAE174`.
2. Export the first two corrected cells and verify zero decode failures.
3. Recover `01CF`; this raises the nine-cell dependency coverage to 99.10% together with 0157.
4. Recover `01D1` and `00EF` for 99.90% of the currently parseable placement graph.
5. Re-run validator v3 on the current `80C98258` payload after the failing-block issue is resolved.
6. Merge only binary-passing map-owned cells in their already-proven common coordinate frame.
7. Bind materials/textures from serialized material arrays, then validate the common/decal layer and dynamic props.

The opaque baked-static Tower shell is therefore much closer than the final visually complete Tower: placement ownership is solved and almost all mesh dependencies are identified; remaining work is targeted byte closure, one block-decode issue, and visual/material/decal/dynamic content reconstruction.
