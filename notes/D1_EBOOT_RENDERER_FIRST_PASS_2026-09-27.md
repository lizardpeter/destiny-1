# Destiny 1 PS4 eboot renderer first pass — 2026-09-27

## Scope and exact input

This note records exact-build executable evidence from the owner-provided PS4
Destiny 1 `eboot.bin`:

- SHA-256: `672f03411c0503dfbcda804cbb9fb27cdd9a8d73a8bcb71bf0c4f688073b0833`
- size: 29,249,016 bytes
- source object used by the reproducible Actions probes:
  `https://r2.houseofkublai.com/destiny/CUSA00219_01.33/eboot.bin`
- ELF64 x86-64 / Orbis, entry `0xC2E200`

The directory name reports 01.33, but the executable version remains
`OWNER_PROVIDED_FINGERPRINT_VERSION_UNVERIFIED` unless independently closed by
build metadata.

Raw executable bytes are not committed. The observations below come from
`d1_executable_probe.py`, exact RIP-relative string xrefs, and bounded Capstone
x86-64 disassembly generated from that SHA.

## Evidence rules used here

- A printable string proves only that the exact executable contains the string.
- A validated RIP-relative xref proves code references that exact string.
- A bounded Capstone window proves the listed instructions around the xref but
  does not prove a complete function boundary.
- Human-readable pass/surface names are retained as authored renderer evidence,
  but execution order is not assigned from string-file ordering.
- Values in renderer descriptor initialization are retained verbatim and are not
  assigned PS4 format/state semantics until the consuming code is closed.
- A pointer in `PT_SCE_DYNLIBDATA` is loader/dynamic-link metadata and is not
  promoted as Bungie runtime render-table ownership.

## Retail render graph vocabulary present in the executable

The exact executable contains a dense graphics vocabulary that directly names the
missing runtime systems in the current reconstruction.

Pass / stage labels include:

- `generate_gbuffer`
- `lighting apply`
- `light probe apply`
- `light_shaft_occlusion`
- `depth_prepass`
- `postprocess_transparent_stencil`
- `mask_sun_light`
- `depth_3d`
- `depth_ui`
- `deferred_lights_renderer`
- `chunked_lights_renderer`
- `render_submit_lights_view_job`
- `sky transparent feature renderer`
- `speedtree feature renderer`

Named surfaces/resources include:

- `depth_stencil_default`
- `gbuffer_albedo`
- `gbuffer_normals`
- `gbuffer_normals_16bit`
- `diffuse_accum`
- `specular_accum`
- `depth_stencil_multi_sampled`
- `gbuffer_albedo_multi_sampled`
- `gbuffer_normals_multi_sampled`
- `gbuffer_normals_multi_sampled_16bit`
- `edge_mask`
- `shading_result`
- `distortion`
- `skin_prepass_format`
- `depth_stencil_quarter`
- `quarter_res_transp_surface0`
- `quarter_res_transp_surface1`
- `quarter_res_transp_surface_temp`
- `low_res_transparency_upsample_mask_surface`
- `low_res_transparency_intermediate_mask_surface`
- `light_sample_result`
- `final_combine_output_surface`
- `stencil`
- `minmax_depth`
- `light_sample_point_buf`
- `light_sample_point_last_uvs`
- `last_frame_light_probe_shadow`
- `autoexposure`
- `half_res_depth`
- `shadow_depth_stencil`
- `post_v2_transparent_stencil`
- `outline_depth`
- `min_max_depth`
- `water_reflection_depth`

This vocabulary is direct executable evidence that retail Destiny 1 uses an
explicit G-buffer + accumulation/composition pipeline rather than the current
single-pass preview approximation in Rust-test. Exact attachment formats,
producer/consumer edges and execution order remain to be closed from code.

## G-buffer surface registration neighborhood

Exact RIP-relative xrefs place the core G-buffer surface names in one code
neighborhood around `0x80A280`.

An apparent prologue occurs at `0x80A280`:

```text
0x80A280  push rbp
0x80A281  push r15
0x80A283  push r14
0x80A285  push r13
0x80A287  push r12
0x80A289  push rbx
```

The same neighborhood references, in one bounded instruction range:

```text
0x80A3CA  depth_stencil_default
0x80A3FC  gbuffer_albedo
0x80A403  gbuffer_normals
0x80A40A  gbuffer_normals_16bit
0x80A411  diffuse_accum
0x80A418  specular_accum
0x80A41F  depth_stencil_multi_sampled
0x80A42D  gbuffer_albedo_multi_sampled
0x80A434  gbuffer_normals_multi_sampled
0x80A43B  gbuffer_normals_multi_sampled_16bit
0x80A450  edge_mask
0x80A45E  shading_result
...
0x80A4BA  distortion
...
0x80A572  skin_prepass_format
```

The code writes compact descriptor-like records beside these names. For the
first descriptor the exact writes include:

```text
[record + 0x00] = pointer to depth_stencil_default
[record + 0x08] = 1
[record + 0x0C] = 7
[record + 0x10] = 0x2001   (16-bit write)
[record + 0x12] = 0
[record + 0x16] = 0
[record + 0x18] = 0x204704
[record + 0x1C] = 0x204704
[record + 0x20] = 0
```

These are exact serialized/runtime initialization values. Their field semantics
are not yet assigned.

A second runtime path around `0x80B1DD` constructs/selects multisampled
descriptors using the same authored names, including:

```text
depth_stencil_multi_sampled
gbuffer_albedo_multi_sampled
gbuffer_normals_multi_sampled
```

and calls renderer helpers including `0x8186C0`, `0x818930`, `0x818A30`,
`0x818A90`, `0x807DB0`, `0x807DF0`, and `0x89C5B0`. The exact roles of
those helpers await Ghidra/decompiler closure.

### Consequence for the runtime reconstruction

The current D1 renderer should not treat one color target plus ad-hoc lighting as
the intended final architecture. The executable has explicit authored resources
for:

`depth -> gbuffer albedo/normals -> diffuse/specular accumulation -> shading result`

with separate MSAA variants and edge-mask/distortion/prepass resources. The
precise pass graph still requires control-flow proof, but these resources are now
executable-side facts.

## Autoexposure / probe-history neighborhood

`autoexposure` has an exact RIP-relative xref at `0x81968B`. The same
bounded neighborhood references:

- `sky_mask`
- `debug_umbra_occl_buf`
- `light_sample_point_last_uvs`
- `last_frame_light_probe_shadow`
- `autoexposure`

The code initializes descriptor-like records with exact values such as
`0x22C003`, `0x204001`, `0x200020`, and `0x10028`. Those values are
retained without semantic labels until the consuming surface allocator/resource
decoder is understood.

This is executable evidence that exposure and light-probe history are explicit
renderer resources, not merely package-side concepts.

## Shadow surface neighborhood

`shadow_depth_stencil` is referenced at `0x88F42C` together with
`half_res_shadow_mask` and `half_res_depth`.

Exact nearby writes include repeated `0xFAC00A` values and descriptor fields
such as `2` and `0x4000`. The bounded neighborhood calls:

- `0x7E0F70`
- `0x7DE710`
- `0x7E1110`
- `0x8A5660`

The surface/state meaning of the constants is unresolved; this neighborhood is a
priority decompilation target because it can connect the package light/shadow
resources to the retail renderer.

## Final-combine surface neighborhood

`final_combine_output_surface` has an exact xref at `0x80CF99`.

Immediately before the xref the code calls `0x89FC90`; after it, a local
descriptor-like record is initialized with values including:

```text
+0x08 = 1
+0x0C = 2
+0x10 = 0x0C01
+0x18 = 0xFAC00A
+0x1C = 0xFAC00A
+0x20 = 0
```

The larger bounded neighborhood calls many renderer candidates including
`0x870800`, `0x874C30`, `0x873C80`, `0x818A30`, `0x818A90`,
`0x89C8F0`, `0x8983A0`, `0x89D280`, `0x89F9A0`, `0x8095D0`,
`0x89FC90`, `0x818930`, `0x8A2360`, `0x872680`, `0x818620`,
`0x8183E0`, and `0x873010`.

This is a high-value control-flow target for reconstructing final scene
composition once Ghidra function boundaries/prototypes are available.

## Sky renderer executable path

The exact string `sky transparent feature renderer` is referenced at
`0x7F8717`. A normal x86-64 function prologue is visible at `0x7F86D0`.

Immediately before and after the string xref, the function performs the same
32-bit Destiny package/entry index decomposition used by the Tiger FileHash
scheme:

```text
sar value, 0xD
shr temp, 0x12
or  temp, 0x3FF
and temp, value
shl temp, 6
...
and entry, 0x1FFF
imul entry, [package record + 0x30]
...
```

The bounded function neighborhood calls:

- `0x816780`
- `0x831DA0`
- `0x8363F0`
- `0x83F100`

plus assertion/helper `0x12AA7F0`.

This strongly supports a retail sky feature renderer whose construction/setup is
driven by Tiger/FileHash-backed source data rather than a synthetic hard-coded
sky. Exact argument and return semantics await decompilation.

## Launch-package render globals path

The exact string `<launch package render globals>` is referenced at
`0x82E13A`; an apparent function prologue occurs at `0x82E110`.

The function also performs Destiny FileHash-style package/entry decomposition
before calling `0x10080A0` and then following another FileHash-like value. Its
bounded neighborhood subsequently calls `0x7EA930`, recursively reaches
`0x82E110`, and calls `0x82D970`, `0x106F6A0`, and `0x7E58F0`.

This is a primary executable bridge candidate from launch-package data into
renderer-global resources.

## Ambient-occlusion container initialization

`Ambient occlusion entities container` has an exact code xref at `0x83F499`;
`Ambient occlusion speedtree entities container` follows at `0x83F4EB`.

The first initialization call to `0x70530` receives exact stack/register
constants including:

```text
ecx = 0x10
r8d = 8
r9d = 0xFFFFFFFF
stack: 0x400, 0x2C0, 0xE, 0, 0
```

No semantic names are assigned to these arguments yet. Their presence is
additional executable proof that ambient-occlusion entity ownership is a
separate renderer system.

## Rejected / corrected inference: pass-label pointer cluster

An exact pointer scan found the human-readable labels:

- `generate_gbuffer`
- `lighting apply`
- `light probe apply`
- `light_shaft_occlusion`
- `depth_prepass`
- `postprocess_transparent_stencil`
- `mask_sun_light`
- `deferred_lights_renderer`
- `chunked_lights_renderer`

clustered as absolute pointer values.

Those pointer locations are inside program segment type `0x61000000`, which is
Sony `PT_SCE_DYNLIBDATA`. That segment is dynamic-linker/loader metadata and
contains string/symbol/relocation/hash/dynamic tables. Therefore this cluster is
**not promoted** as Bungie's runtime render-pass table.

The pass strings themselves remain exact executable evidence. Runtime pass
ownership/order must instead come from mapped code/data references and the
Ghidra call graph.

## Renderer job-system executable path

A contiguous setup function around `0x811115..0x8113DC` registers separate
source-backed jobs for:

- `render_setup_extract_and_prepare_and_allocate_nodes_for_view_job`
- `render_submit_view_job`
- `render_submit_lights_view_job`
- `render_submit_transparents_view_job`
- `render_submit_speedtree_view_job`

For the lights/transparents/SpeedTree job records, the exact code repeatedly:

1. calls `0xF97B0`,
2. stores the returned 32-bit value,
3. decomposes that value with the same package/entry bit operations used by D1
   FileHash resolution (`sar 13`, package-mask logic, `& 0x1FFF`),
4. resolves the corresponding package entry record,
5. writes the shared job/setup pointer into `[resolved_entry + 8]`.

After these registrations, the same function allocates and zeroes two large
parameter blocks:

```text
render_submit_view_per_stage_job_parameters: 0x148840 bytes
render_submit_view_per_job_job_parameters:   0x0D1880 bytes
```

The allocation call is `0xAF600`; the zero/fill helper is `0x12AA980`.

The next diagnostic helper at `0x8113E0` reports
`render_setup_extract_and_prepare_jobs_and_allocate_nodes_for_view_packet job
(view: %s)`.

A function beginning at `0x811400` reads view fields at offsets `+0x10660`
and `+0x10698`, calls `0x7ED380`, then reports
`render_submit_view job (view: %s, render stage: %s)`.

This is direct executable evidence that retail D1 separates scene extraction /
prepare work from per-view submission and maintains distinct submission jobs for
lights, transparents and SpeedTree. Exact scheduler types, job argument schemas
and stage ordering remain pending decompilation.

## Surface descriptor ABI frontier

The G-buffer initializer around `0x80A3CA` writes the named render surfaces
into compact global records. Consecutive records for the color/normal/accumulation
family are spaced by exactly `0x28` bytes, establishing a source-executable
surface-descriptor record size for this registry.

Observed record fields include:

```text
+0x00  authored name pointer
+0x08  dword
+0x0C  dword
+0x10  word
+0x12  dword/word region
+0x16  word
+0x18  dword
+0x1C  dword
+0x20  dword
```

Examples retain exact values such as `0x2001`, `0xFAC90A`, `0xFAC00A`,
`0xFAC00C`, and `0x4000`. These field values are not yet named as PS4 pixel
format, tiling, usage, sample-count or bind flags. The next proof is to decompile
the consumers/allocator helpers and map those fields to actual Orbis surface
creation behavior.

## Current executable RE frontier

The highest-value next proofs are:

1. recover the complete function boundary/decompilation around `0x80A280` and
   identify the surface descriptor schema/allocator;
2. decompile the `0x80B1xx` G-buffer/MSAA selection path and the
   `0x8186C0/0x818930/0x818A30/0x818A90` helpers;
3. decompile the final-combine neighborhood around `0x80CF99`;
4. resolve the `render_submit_lights_view_job` code owner and connect it to
   `deferred_lights_renderer` / `chunked_lights_renderer`;
5. decompile the sky feature function at `0x7F86D0` and its resource-resolver
   calls;
6. decompile `<launch package render globals>` at `0x82E110`;
7. connect shadow surface construction at `0x88F42C` to the package-side
   LightData/material/shader contracts;
8. determine exact G-buffer formats and the producer/consumer relation between
   package GCN MRT exports and the named retail surfaces;
9. only after those are closed, port the proven renderer contracts into
   Rust-test and remove the corresponding preview/fallback ownership.

A full exact-build Ghidra function/call/string-xref graph and focused renderer
decompilation are being generated by the repository workflow; those results
supersede bounded-window function assumptions when available.
