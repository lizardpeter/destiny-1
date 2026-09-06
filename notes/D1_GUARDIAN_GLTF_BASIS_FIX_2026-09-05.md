# D1 Guardian glTF coordinate-basis correction — 2026-09-05

This note records the cause of the visually exploded Spektar Pandion Guardian seen in Blender after the first 28-range stage-0 rigged export, the source-backed correction, and the regression evidence. It supersedes any earlier implication that the remaining visible defect was only shader/dye fidelity.

## Symptom

The first stage-0-only rigged export was structurally valid glTF but visually wrong in Blender. Armor pieces and weighted vertices were displaced around unrelated pivots, producing separated curved shells, floating clusters, and long displaced strips rather than a coherent Guardian.

This was **not** caused by the 28-range stage-0 pruning pass. The same deformation was already latent in the 69-range rigged source and became visible when Blender evaluated its skin/animation.

## Root cause: mesh and armature used different coordinate bases

`tools/d1_entity_model_export.py` decodes D1 mesh positions and applies the serialized model scale/translation, but preserves the native Tiger coordinate basis.

For the exact Spektar Pandion masculine five-piece source, the proven static bounds are:

```text
Tiger/native bounds
min  [-0.2596753836, -0.4687087536, -0.0015791655]
max  [ 0.4263126552,  0.4687087536,  1.9012408257]
```

The ~1.90 m character height is therefore on native **Z**.

The exact animation parser pinned by the Guardian workflow (`SolUnshadowed/tiger-animation-parser` commit `b9fdc3a43dd28118113275624fcc9054b75855f4`) explicitly documents Tiger as:

```text
Z-up
X-forward
Y-right
```

and converts Tiger to its Three.js/glTF-side basis with:

```text
[x, y, z] -> [y, z, x]
```

Its skeleton translation and quaternion conversion use that remap before the skeleton, inverse-bind matrices, and animation tracks are serialized.

The old Guardian binder therefore combined:

```text
mesh vertices      native Tiger [x,y,z]
skeleton/animation converted     [y,z,x]
```

The JOINTS_0/WEIGHTS_0 data can be completely correct while that GLB still deforms catastrophically, because each vertex is evaluated around a bone pivot expressed in a different basis.

## Correction

Reusable fail-closed correction tool:

```text
tools/d1_gltf_tiger_mesh_basis_fix.py
```

Commit introducing the tool:

```text
6cc9ed19c86ce9bce6f3513eeb65953a5640efc5
Fix Tiger mesh basis before Guardian skin evaluation
```

It remaps geometry to the same basis already used by the exact D1 skeleton/animation decoder:

```text
POSITION  [x,y,z]   -> [y,z,x]
NORMAL    [x,y,z]   -> [y,z,x]   when present
TANGENT   [x,y,z,w] -> [y,z,x,w] when present
```

It does **not** alter:

```text
JOINTS_0
WEIGHTS_0
inverse-bind matrices
animation channels
materials
UVs
node indices
```

It rejects sparse/non-float geometry accessors and non-identity mesh-node transforms rather than attempting a partial or ambiguous conversion.

## Exact basis invariant on the real Guardian

The corrected 69-range rigged and textured inputs both produce:

```text
before/native Tiger
min  [-0.2596753836, -0.4687087536, -0.0015791655]
max  [ 0.4263126552,  0.4687087536,  1.9012408257]

after glTF/parser basis
min  [-0.4687087536, -0.0015791655, -0.2596753836]
max  [ 0.4687087536,  1.9012408257,  0.4263126552]
```

This is the exact component permutation, and the ~1.90 m height moves from Tiger Z to glTF Y as required.

The 69 primitives share two POSITION accessors, so the correction rewrites exactly **67 unique POSITION accessors** while still covering all **69 primitives**. This sharing is intentional and is now explicitly validated.

## Independent deformation regression check

A separate CPU glTF skin evaluator was used to compare the old and corrected 28-range textured/rigged exports at several exact retail-animation frames. It evaluates node hierarchy, animation channels, inverse-bind matrices, joints, and weights and then computes skinned vertex bounds.

Representative frame-0 spans:

```text
old mixed-basis export
span [2.087, 2.264, 2.673] m

basis-corrected export
span [0.883, 1.682, 0.999] m
```

Representative frame-100 spans:

```text
old mixed-basis export
span [2.334, 2.058, 2.764] m

basis-corrected export
span [0.950, 1.611, 0.961] m
```

Across sampled frames 0, 1, 30, 100, 200, and 323, the old file expands into ~2.1–2.8 m extents on multiple axes. The corrected file remains a coherent human-scale animated volume: roughly 1.61–1.71 m on Y and under ~1.0 m on the transverse axes for this clip/pose.

This independently matches the Blender failure mode and demonstrates that the basis correction fixes the deformation mechanism rather than merely rotating the static object for presentation.

## Corrected visual checkpoint

Workflow correction commits:

```text
49ebc432966043a440af20f7cd4ef507c579819b
Rebuild Guardian visual exports in matching Tiger/glTF basis

fecdce184aaf9aa6d52f8e03394f886fddfdb8a1
Accept shared Guardian position accessors in basis validation
```

Successful workflow run:

```text
D1 Spektar Pandion visual exports
run 34007426731
```

Artifact:

```text
D1-Spektar-Pandion-Guardian-VISUAL-EXPORTS-BASIS-FIXED
artifact ID 9981398451
artifact digest sha256:7df7b2a7aa8d8355488f8d7d0ae50a18ae40fdf778ac39c01db3ac5d4e72b9e2
```

Primary corrected animated file:

```text
SPEKTAR_PANDION_TITAN_MASCULINE_STAGE0_28_RANGE_TEXTURED_RIGGED_ANIMATED_BASIS_FIXED.glb
bytes   18,973,848
SHA256  b8ea38df1d3db102dbd9d9db0757c643fa0f2a75c75ff524e570a6edbfee524a
active stage-0 ranges  28
skin joints            67
animation              STATE_13433E07_809D8572
```

Diagnostic static control:

```text
SPEKTAR_PANDION_TITAN_MASCULINE_STAGE0_28_RANGE_TEXTURED_STATIC_BASIS_FIXED.glb
bytes   18,951,628
SHA256  c019a8ebffa61976780cd3361f96cc5cec02971f9514785738dd6840ce9b605f
active stage-0 ranges  28
skin                    none
animation               none
```

The static control isolates stage-0 geometry/material selection from skin/animation evaluation. If the static control is coherent but the animated file is not, any remaining defect is armature-side. If both are geometrically wrong in the same way, the next target is stage/draw assembly rather than the rig.

## What remains unresolved

This correction addresses coordinate-space consistency only. It does not claim final material fidelity. The existing source-closed per-vertex dye/detail multiplier and final native D1 dye/GStack shader recreation still need to be baked into the visual exporter.

The skin decoding itself remains byte-validated and unchanged:

```text
0x0C ordinary W     -> rigid one-bone
0x0C W +/-0x7FFF    -> inline 2-bone
0x10                -> inline 4-weight/4-index
```

No weights, material identities, or animation semantics were changed to obtain this fix.
