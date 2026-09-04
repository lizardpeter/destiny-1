# D1 PS4 `816CE09A` animation-proxy compatibility frontier

Date: 2026-09-03/04

This note supersedes the older working assumption that `816CE09A` merely needs its missing standard model parent / external-material table located.

## Current classification

`816CE09A` should be treated as an **animation-bundle/proxy model until contrary byte evidence is found**.

The decisive observations are already recorded in `PS4_0156_00E2_OWNER_TRACE.md`:

- `816CE09A` is immediately preceded by `816CE099`, class `0x8080222A`.
- `816CE099` contains dword `0xD3FD602F`, exactly the animation hash of `816CE09E`.
- The same `0x8080222A -> s_entity_model -> raw animation data -> animation clip(s)` layout repeats in `ps4_arch_vex_00e2_0.pkg`.
- A complete aligned-dword scan of decompressed `0767_0` entries found no ordinary reverse reference to `816CE09A`.
- No standard model parent resident in `0767_0`, `00E2_0`, `0156_0`, or the scanned `0157` resources owns `816CE09A`.
- Two provisional texture assignments to `816CE09A` were visually falsified in Blender.

Therefore the clean rigged/animated `816CE09A` GLB is retained as a **validation artifact for mesh + skeleton + skinning + animation**, not claimed as the final retail visible Vex body.

## Proven animation compatibility fingerprint

The validated proxy bundle uses:

- proxy model `816CE09A`
- skeleton EntityResource `816CE092`
- 12 skeleton nodes
- runtime rig EntityResource `816CE095`
- secondary runtime-rig class `0x808008B2`
- runtime component hash `76F7A98E`
- 12 controls
- bone -> control mapping `0..11`
- control -> bone mapping `0..11`
- clip `816CE09D` / animation hash `6FB760FF`
- clip `816CE09E` / animation hash `D3FD602F`

The component hash and mapping were validated during the successful animated export. The reusable source tree does not yet contain a byte-documented field decoder for the entire `0x808008B2` payload, so new compatibility work must not invent offsets for that structure.

## Better question

The active problem is now:

> Which **ordinary visible D1 model parent + model + skeleton/control cluster** is compatible with the `816CE092 / 816CE095 / 76F7A98E` animation bundle?

That is more useful than asking which parent owns `816CE09A`, because byte evidence increasingly says `09A` itself is not the ordinary render-owned model.

## New deterministic probe

`tools/d1_animation_proxy_compat_probe.py`

The tool deliberately reuses only already-proven binary parsers and treats `76F7A98E` as a raw validated fingerprint rather than pretending the runtime-rig schema is solved.

For every supplied package it:

1. enumerates resident structured entries;
2. decodes all `0x80800861` EntityResources;
3. identifies standard D1 model parents using `0x80801A80 -> 0x80801A9C`;
4. decodes skeleton EntityResources using `0x808006BD -> 0x8080049A` and records bone counts/hashes;
5. parses each standard parent's owned `s_entity_model`;
6. records model mesh-part variants and vertex-buffer strides;
7. scans aligned dwords for known TagHash backlinks/co-occurrences;
8. scans for the validated component fingerprint `76F7A98E` without assigning undocumented field semantics;
9. ranks ordinary visible-model candidates by explicit evidence.

Current ranking evidence includes:

- direct co-reference with a decoded 12-bone skeleton;
- direct co-occurrence with `76F7A98E`;
- graph proximity to the target rig/skeleton or shared Vex seeds;
- co-reference with `80AADE40`, `80AAE3A4`, `80AAE10B`, or `80AAE10C`;
- `VariantShaderIndex` 0 and 1 support;
- the 12/16-byte vertex-buffer stride pair used by the proxy family;
- presence of the `80AAE10B/80AAE10C` auxiliary technique family.

**The score is explicitly heuristic.** It is a triage/ranking device, not proof of ownership or animation compatibility. A final candidate still requires direct byte-level entity/skeleton/control evidence and an actual retargeted animation/export test.

## Known comparison fixtures

### `809C4B97`

This remains the closest known structural **animation-bundle** counterpart to `816CE09A`:

- 4,207 vertices
- 12/16-byte vertex-buffer family
- D1 triangle strips
- visible variants 0..3
- same `80AAE10B/80AAE10C` auxiliary technique family
- preceded by its own `0x8080222A` wrapper `809C4B96`

Because it is itself in the same animation-bundle pattern, it is a proxy-family comparison fixture, **not yet the desired ordinary visible-model answer**.

### `809C44A5 -> 809C47F4`

This is the strongest currently proven **ordinary visible Vex material-control fixture**:

- standard parent `809C44A5`
- model `809C47F4`
- external variants 0 and 1 are fully resolved
- visible materials `809C475F` and `809C4760`
- their retail texture stacks are already decoded through the `0156/0157` chain

Its render/material ownership is proven, but its compatibility with `816CE095 / 76F7A98E` is **not** yet proven. It should be tested by the new compatibility probe before any 09D/09E retargeting claim is made.

## Patch sibling status

The public manifest names:

- `ps4_arch_vex_00e2_1.pkg`
- `ps4_arch_vex_00e2_2.pkg`
- `ps4_arch_vex_00e2_4.pkg`
- `ps4_arch_vex_com01_0767_1.pkg`
- `ps4_arch_vex_com01_0767_4.pkg`

Direct public-mirror recovery of those five filenames was already attempted through GitHub Actions and returned HTTP 404 for all five. Repeating that mirror attempt is not useful.

The `0767_1/_4` files remain valuable if supplied from the user's corpus, but they are no longer the only productive route forward.

## Recommended next corpus run

When the already-used local package corpus is available, run the compatibility census across at least:

```bash
python tools/d1_animation_proxy_compat_probe.py \
  ps4_arch_vex_com01_0767_0.pkg \
  ps4_arch_vex_00e2_0.pkg \
  ps4_globals_0156_0.pkg \
  --runtime <oodle-runtime-dir> \
  --include-all \
  --include-backlinks \
  -o out/09a_visible_model_compatibility.json
```

If `ps4_globals_0157_0.pkg` and `_1.pkg` are colocated, they can be included as additional package arguments for graph evidence, although they are primarily selector/material infrastructure rather than the expected visible-model owner.

## Acceptance test for a final visible-model match

Do not promote a candidate to the final visible Vex body until all applicable checks pass:

1. candidate is owned by an ordinary standard model parent;
2. candidate has a byte-proven entity/skeleton/control relationship compatible with the 12-node animation rig;
3. runtime control mapping is proven equivalent to the 12 controls consumed by `09D/09E`;
4. animations retarget without joint-count, hierarchy, or transform anomalies;
5. model's own parent resolves its real external material variants;
6. textures come from those proven materials, not adjacency or visual guessing;
7. exported geometry/materials/animation visually validate in Blender.

## Long-term exporter rule

A model adjacent to a `0x8080222A` wrapper must no longer be automatically presented as a final textured entity model.

The exporter should distinguish at least:

- ordinary render-owned model;
- animation-bundle/proxy model;
- unresolved model whose ownership class is not yet known.

This prevents the exact failure mode that produced the rejected `816CE09A` texture hypotheses.
