# D1 Tower fidelity checkpoint — 2026-09-20

Branch: `d1-crota-source-semantics-v1`

This checkpoint separates source-closed asset/world reconstruction from native renderer
fidelity.  "Perfect Tower" is not treated as one scalar: a scene can contain the exact
meshes/textures/actors and still look wrong if material arithmetic, light shaders,
sky selection, transparency, global buffers, fog/reflections, and runtime scenario
selection are approximated.

## Source-closed world / geometry layer

The Tower Activity `80C98019` is closed through the full map-root graph:

- 122 reachable map-data tables;
- 1,418 map-data rows;
- ten validated map-owned static cells:
  `80C98254 80C984D8 80C98A6B 80C993CD 80C993CF 80C997F5 80C99981 80CA0B70 80CA0B72 80CA0C60`;
- zero static geometry decode errors in the ten-cell exporter;
- corrected affine transforms and UVs;
- current ten-cell base checkpoint:
  11,728 baked placement nodes, 2,071 meshes, 400 materials, 537 exact images/textures;
- baked + common source-driven layer checkpoint:
  12,438 nodes, 2,234 meshes, 499 materials, 588 textures/images;
- common source layer:
  327 source records, 69 unique models, 163 selected geometry parts, 709 rendered nodes,
  99 materials, 50 exact source textures.

Conclusion: the Tower world shell is no longer the dominant fidelity blocker.

## Static material / shader layer

Common-layer material resources are exact:

- 99 exact common materials;
- 65/65 exact PS4 pixel-shader families recovered and disassembled;
- 50/50 exact common source textures recovered;
- instruction-proven texture roles exist for a substantial subset but do not yet cover
  every sampled serialized material register or reproduce every terminal equation.

New 2026-09-20 work:

- `tools/d1_tower_common_shader_semantic_coverage.py` measures family/material-weighted
  semantic coverage instead of counting exported textures;
- the 65-family workflow now emits the highest-impact unresolved shader families;
- `tools/d1_gcn_terminal_mrt0_dependency_census.py` supports ordinary and compressed
  MRT0 exports;
- the two top unresolved common families `8093E8A2` and `80CA0F50` are now queued for
  exact image/cbuffer/terminal-output slicing.

Remaining gate: promote sampled resources and terminal arithmetic family-by-family,
then replace preview PBR bindings with exact or explicitly bounded portable equations.

## Original Tower lights

Exact source structure already exists:

- 737 light records / instances;
- all 737 material references resolve to D1 material class `80801AD7`;
- 497 unique light materials;
- 32 exact native light pixel-shader families;
- all 32 native GCN programs were recoverable/disassemblable.

New 2026-09-20 work upgrades the light disassembly workflow to:

- exact image-resource provenance;
- exact ImmConstBuffer dword provenance;
- terminal MRT0 dependency slices for the eight highest-frequency light shader families.

Remaining gate: identify exact light-output equations and renderer/global inputs, then
replay them instead of using generic Blender lights/emissive approximations.

## Sky / environment

Exact Activity ownership is already closed:

- 3 sky collections;
- 109 sky records;
- 39 exact sky model resources / EntityModels;
- all 39 highest-detail sky models exported;
- exact sky material texture dependencies closed.

New 2026-09-20 workflow:
`.github/workflows/d1-tower-sky-shader-closure.yml`

It will:

- recover every exact sky pixel shader;
- disassemble the complete sky shader corpus;
- map exact image and constant-buffer provenance;
- slice terminal MRT0 dependencies for the highest-frequency sky shader families.

Remaining gates:

- native sky material arithmetic;
- active sky collection / record runtime selection;
- renderer/global state feeding sky shaders;
- atmospheric/fog/post behavior where not encoded directly in the sky material.

## Spawned actors / NPCs

Source assets are deep:

- 57 source-owned spawned actor entities in the animation census;
- 13 exact actor models;
- 30 available visual signatures, 29 used by placement alternatives;
- 320 active materials across the full 30-variant material universe;
- 6 shared exact action libraries;
- 547 exact location/visual/action placement alternatives;
- exact skinning and native-basis animation compatibility have been proven.

Three-NPC focused shader work additionally closes current-state semantics for several
high-value Tower actor pixel shaders, including `809D835A`, `809D835C`,
`809D835F`, `809D8363`, and `809D836C`.

Hard runtime gates remain:

- active scenario selection;
- active D912 group;
- active actor location alternative;
- active animation state;
- full D1 retail descriptor evaluator / dynamic TFX state;
- complete native shader replay for the remaining actor material universe.

## Renderer-global blockers

These remain the difference between an exact asset reconstruction and a near-pixel-
faithful Tower:

1. full material arithmetic for unresolved static/common families;
2. original light shader equations and global inputs;
3. sky shader equations and active sky selection;
4. runtime/global constant-buffer producers (including unresolved renderer scope data);
5. transparency / framebuffer ordering where material state alone is insufficient;
6. environment reflections / cubemap behavior and LOD control;
7. fog / atmosphere / post-processing;
8. runtime actor/scenario selection and event/state behavior;
9. VFX/ambient dynamic systems not yet source-closed.

## Practical fidelity estimate

These are engineering estimates, not source facts:

- world geometry / placement / source asset recovery: **~90–97%**;
- exact texture/resource recovery: **~90%+** for the closed static/common/sky/actor
  corpora;
- native material/shader visual reproduction across the entire Tower: **~55–70%**;
- original lighting / sky *asset* recovery: **~85–95%**, but native renderer replay is
  materially lower;
- actor asset/animation option recovery: **~80–90%**, while live state selection remains
  unresolved;
- overall "convincing D1 Tower" reconstruction: **~75–85%**;
- overall "near-pixel-perfect original renderer result": **~50–65%**.

Do not treat those percentages as proof metrics.  The objective counts above are the
authoritative checkpoints.  The remaining work is now disproportionately renderer
semantics rather than missing Tower geometry.

## Highest-value next work

1. close `8093E8A2` and `80CA0F50` terminal material semantics;
2. inspect and promote the top-eight light shader output equations;
3. inspect and promote the top sky shader equations;
4. build renderer-scope/API12/API13/global-buffer producer correlations across Tower
   common/light/sky shader families;
5. replace generic preview material/light/sky adapters with exact equation-driven
   Blender nodes where portable reproduction is defensible;
6. resume runtime actor/scenario selection only with primary/runtime evidence; never
   pick one alternative because it "looks right".
