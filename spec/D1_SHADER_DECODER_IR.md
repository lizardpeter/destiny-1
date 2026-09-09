# Destiny 1 PS4 Shader Decoder and Canonical IR — v1

Status: **architecture frozen at the metadata/native/structural boundaries; game-wide structural census in progress**  
Target: final-era Destiny 1 / Rise of Iron PS4 pixel and vertex shaders.

This specification defines the reusable decoder boundary that sits between exact
Tiger/GCN reversal and consumers such as the Rust renderer and Blender exporter.
It deliberately does **not** promote Crota-specific semantic proof scripts into a
game-wide decoder.

## 1. Pipeline

```text
D1 Tiger shader header
  |
  | exact FileEntry.Reference
  v
native shader payload
  |
  | validated OrbShdr framing
  v
exact GCN code bytes
  |
  | pinned GFX700 disassembly + byte accounting
  v
generic GCN Structural IR
  |
  | corpus opcode/form/control-flow census
  v
semantic promotion with evidence
  |
  v
canonical D1 Shader IR
  |                     |
  v                     v
Rust renderer backend   Blender/material backend
```

No later layer may weaken an earlier proof boundary. A semantic or backend failure
must not change which Tiger resource, native payload, or GCN bytes were selected.

## 2. Exact current-retail PS/VS population

Authoritative metadata checkpoint:

- `evidence/d1_ps4_shader_header_corpus_r1.json`

Source generation:

```text
packages.txt SHA-256
9ab9cac1a7798e5bd558d4db5a1dcd36a71dbba307eaac3345a4a65c31c0f9a5

physical package members = 1,275
package families         = 337
```

Current shader headers:

```text
32:8 PixelShader headers = 25,405
32:9 VertexShader headers = 12,487
---------------------------------
total logical headers     = 37,892
```

Their exact native-program graph is:

```text
32:8 -> FileEntry.Reference -> 1:8
32:9 -> FileEntry.Reference -> 1:9
```

Across the current corpus:

```text
distinct native FileEntry.Reference values = 37,179
missing current native targets              = 0
non-unique current native targets           = 0
PS/VS cross-stage shared native references  = 0
```

Logical shader identity and native-program identity are therefore separate.
The 37,892 logical headers collapse to 37,179 native references before any
byte-level deduplication.

The byte-level unique-GCN count is intentionally not copied from the logical or
reference count. It is established only after exact OrbShdr-bounded code recovery
and SHA-256 deduplication.

## 3. Identity levels

Every canonical shader record must preserve all of these identities:

### 3.1 Logical header identity

```text
stage
header_tag_hash
header type/subtype
header package id / generation / patch / entry index
exact header payload SHA-256
```

This is the identity used by materials and other D1 resources.

### 3.2 Native payload identity

```text
native_program_reference
native type/subtype
native package provenance
exact native payload SHA-256
OrbShdr metadata
```

This is reached **only** through the logical header's serialized
`FileEntry.Reference`.

### 3.3 Exact GCN program identity

```text
code_length_bytes
GCN SHA-256
exact code bytes or immutable content location
```

This is the backend compile/deduplication key. Multiple logical headers or native
payload references may eventually map to the same exact GCN SHA-256; the decoder
must retain the reverse aliases rather than discarding them.

### 3.4 Semantic instance identity

A material instance may bind different textures, samplers, constants, blend state,
vertex streams, or interpolation inputs to the same exact GCN program. Therefore a
compiled GCN-program cache entry is **not** itself a complete D1 material.

## 4. Native binary framing gate

The native payload is accepted as an executable shader only when OrbShdr metadata
resolves without ambiguity and produces a valid code length.

Required checks include:

```text
native payload exists
stage agrees with the 32:8->1:8 or 32:9->1:9 graph
OrbShdr footer is resolved by the validated formula
OrbShdr stage agrees with logical stage
code_length_bytes > 0
code_length_bytes <= OrbShdr footer offset
code_length_bytes <= native payload length
```

A fallback that merely finds one magic-looking footer is diagnostic evidence, not
an accepted binary form. Previously unseen footer/layout forms remain explicit
violations until independently closed.

## 5. Structural IR contract

The generic producer is:

- `tools/d1_gcn_cfg_ir_v2.py`

A successful program reports:

```text
D1_GCN_STRUCTURAL_IR_COMPLETE
```

For every instruction the Structural IR preserves at minimum:

```text
instruction index
byte address
raw CLRX text
opcode
operand list
exact encoding_hex
def register set
use register set
branch target label/address when present
```

Program-level structure preserves at minimum:

```text
basic blocks
CFG edges
conditional branches
unconditional branches
back edges
EXEC manipulation/divergence sites
exports
image/resource operations and their native register provenance when available
```

### Exact byte-accounting requirement

Structural acceptance is stronger than "CLRX printed instructions."

For an OrbShdr-bounded program of `N` bytes:

```text
first instruction address == 0
instruction encoding byte spans are contiguous
last instruction end == N
all encoding_hex strings are valid complete bytes
```

Only then may that program count toward exact structural byte coverage.

## 6. Corpus census

The game-wide census is produced by:

- `tools/d1_gcn_shader_corpus_structural_census.py`

It records separate populations for:

```text
logical shader headers
native FileEntry references
exact GCN SHA-256 programs
structurally complete GCN programs
exact GCN code bytes
structurally represented GCN code bytes
```

It also inventories:

```text
opcode population
exact instruction encodings
encoding widths
normalized operand / def-use structural forms
classification rules used by the structural producer
CFG/control-flow shapes
EXEC divergence
new forms relative to the exact 808EE505 baseline
```

A normalized structural form is a syntax/def-use observation. It must not be named
as an AMD ISA encoding family unless that family assignment is separately proven.

## 7. Semantic promotion

Structural decoding and semantic decoding are separate states.

Canonical instruction semantics use a tiered state, for example:

```text
STRUCTURAL_ONLY
CONTROL_EXACT
INPUT_PROVENANCE_EXACT
EXPRESSION_EXACT
RECURRENCE_EXACT
EXPORT_EXACT
RESOURCE_BINDING_EXACT
```

The exact set may expand, but promotion follows these rules:

1. Raw bytes and Structural IR are immutable inputs to semantic promotion.
2. A semantic transform must cite the evidence that proves it.
3. Opcode-name familiarity alone is insufficient for a value-level contract.
4. A rule proven for one exact encoding/form is not silently applied to another
   unseen encoding/form.
5. Resource-role labels such as "albedo", "normal", "mask", or "emissive" are
   withheld unless source/native dataflow independently supports that role.
6. Sampler-state enum decoding and texture-role decoding remain separate facts.
7. Unknown semantics remain representable and do not corrupt exact structural data.

The fully closed `808EE505` program is a reference semantic fixture, not a license
to declare every matching-looking D1 shader solved.

## 8. Canonical D1 Shader IR envelope

A backend-neutral record must be able to serialize this shape losslessly:

```text
D1ShaderIR
  schema_version
  status

  source
    platform
    retail_generation / packages_txt_sha256
    stage
    logical_header_identity
    native_payload_identity
    exact_gcn_identity

  native_interface
    header_fields
    OrbShdr fields
    input-usage slots
    vertex input/export semantics when stage == VS
    interpolation/export metadata when proven

  program
    exact code length and SHA-256
    instructions[]
      structural instruction
      exact encoding bytes
      semantic tier
      optional promoted expression/control/resource contract
      evidence references[]
    basic_blocks[]
    cfg_edges[]
    control_flow
    exports[]

  resources
    texture/resource bindings[]
    sampler bindings[]
    constant-buffer bindings[]
    descriptor provenance[]
    unresolved native resource uses[]

  material_interface
    required vertex attributes[]
    required interpolators[]
    required constants[]
    required textures[]
    required samplers[]
    render/blend/depth state facts[]

  backend_contract
    exact_features[]
    portable_features[]
    unsupported_features[]
    approximation_required_features[]

  violations[]
  semantic_boundary[]
  provenance[]
```

Fields that are not proved are absent or explicitly unresolved. They are never
filled with generic PBR defaults and then treated as decoded Destiny semantics.

## 9. Rust renderer backend

The Rust consumer must treat the canonical IR as a decoded asset contract rather
than repeat Tiger/GCN reversal internally.

Required architecture:

```text
Tiger/package decoder
      |
canonical D1 asset graph
      |
D1ShaderIR + material bindings
      |
Rust GPU translation/cache
      |
runtime pipeline objects
```

Important requirements:

- cache compiled programs by exact GCN SHA-256 plus backend feature/version key;
- retain logical-header aliases and per-material bindings;
- do not derive texture roles from filenames or slot order;
- keep D1 vertex control vectors distinct from portable glTF `COLOR_0` semantics;
- fail closed when a required native operation has no exact or explicitly allowed
  backend implementation;
- keep approximation mode separately selectable and visibly marked in diagnostics;
- expose unresolved shader features in machine-readable form so reversal work can
  target real corpus blockers.

The backend may eventually lower proved canonical operations to WGSL/SPIR-V/etc.,
but that lowering is downstream of semantic promotion and is not evidence for D1
semantics itself.

## 10. Blender backend

Blender is a portability/render-authoring backend, not the semantic authority.

The adapter should consume the same canonical material/shader interface as Rust and
build Blender nodes only for proved portable operations.

Rules:

- preserve exact source textures and UV/control channels;
- do not map arbitrary D1 control vectors to `COLOR_0` merely because glTF supports
  vertex color;
- reproduce alpha/blend behavior from decoded D1 state rather than opaque defaults;
- do not assign generic base-color/normal/emissive roles to texture slots without
  proof;
- retain an inspectable record of native operations that cannot be represented by
  standard Blender nodes;
- allow an approximation path only when explicitly requested, and keep it distinct
  from exact export status.

The goal is that the Rust runtime and Blender exporter disagree only where their
backend feature sets differ, not because they contain separate reverse-engineered
interpretations of Destiny resources.

## 11. Coverage numbers

Three different percentages must never be conflated:

### Structural logical-header coverage

```text
headers whose exact GCN program has complete structural byte coverage
/
37,892 current PS/VS logical headers
```

### Structural unique-program coverage

```text
exact unique GCN SHA-256 programs with complete structural byte coverage
/
all exact unique GCN SHA-256 programs recovered from the 37,179 native references
```

### Semantic coverage

This requires a separately defined semantic acceptance criterion. Until that gate
is formalized and measured across the corpus:

```text
semantic_shader_solved_percentage = null
```

A high structural percentage is useful, but it is not evidence that Destiny's
materials have been visually or mathematically reproduced.

## 12. Current checkpoints

Frozen reference program:

```text
logical PS header = 808EE505
exact native semantic instruction closure = 456 / 456
exact sampled texture resources = 2 / 2
```

Game-wide metadata checkpoint:

```text
37,892 logical current PS/VS headers
37,179 distinct exact native references
32:8 -> 1:8 edge violations = 0
32:9 -> 1:9 edge violations = 0
cross-stage native-reference sharing = 0
```

The next promotion boundary is the exact GCN-byte deduplication and complete
Structural IR census. No game-wide semantic percentage is valid before that output
is closed and its unseen-form frontier is understood.
