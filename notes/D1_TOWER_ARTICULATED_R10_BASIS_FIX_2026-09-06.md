# D1 Tower articulated r10 parser-basis fix — 2026-09-06

## Status

`D1_TOWER_ARTICULATED_R10_BASIS_FIX_GREEN`

The visually exploded/misaligned Tower articulated NPCs had a concrete coordinate-space bug in the glTF adapter, not a missing skeleton or bad retail animation payload.

Successful workflow:

- `D1 Tower articulated basis-fixed r10`
- run `34066423705`
- release `d1-tower-articulated-e-f-g-animated-r10-basis-fixed`

Corrected articulated asset:

```text
D1_TOWER_ARTICULATED_E_F_G_ANIMATED_R10_BASIS_FIXED.glb
bytes    76,007,176
sha256   d7ba8084cebe4c2d100b37fe89dec41793249b14a99b29da37f2fbad34bfc331
```

## Root cause

The pinned `tiger-animation-parser` intentionally converts native Tiger/D1 coordinates while reading skeletons and retargeting animations:

```text
native D1/Tiger [x,y,z]
        -> parser [y,z,x]
```

That parser basis is appropriate for its standalone animation export path.

The Tower articulated scene, however, keeps model geometry in native D1 model coordinates.  The placement node separately applies the already-proven Tower world adapter:

```text
D1_ZUP_TO_GLTF_YUP @ placement
```

The r8/r9 animation builder reused parser-space skeleton/animation matrices beneath that Tower placement node.  The skeleton was therefore basis-converted once by `tiger-animation-parser` and then carried through the Tower D1-to-glTF placement conversion while the mesh remained native D1 model space.

This was the source of the visible armature/body mismatch and animation tearing.

## Evidence before the fix

Family E (`80CA0CFC`, 67 bones) geometry bounds in model space:

```text
extent X/Y/Z = 0.689912 / 0.900954 / 1.851461
```

The r9 skeleton joint bounds were instead:

```text
extent X/Y/Z = 0.854148 / 1.676767 / 0.495320
```

The body was tall on native D1 Z while the skeleton was tall on parser-space Y.

Weighted geometry-to-joint alignment was correspondingly wrong:

```text
median weighted vertex-centroid -> joint distance = 1.704271 m
max distance                                    ~= 2.407 m
```

A CPU evaluation of the final glTF skin equation at actual source animation frames also reproduced the visual explosion without Blender:

```text
max animated model diagonal / bind diagonal = 2.884874x
```

So the broken appearance was already encoded in the GLB; it was not merely Blender's armature display.

## Fix

`tools/d1_gltf_unapply_parser_basis.py` converts only the parser-derived articulated domain back to native D1 model basis before the existing Tower placement transform.

For parser basis matrix `P` where:

```text
p = P * raw = [raw_y, raw_z, raw_x]
```

bind matrices are restored as:

```text
M_native = inverse(P) * M_parser * P
```

The adapter updates:

- joint local bind TRS;
- inverse bind matrices;
- animation translation output;
- animation rotation output;
- animation scale output.

It does **not** change:

- mesh POSITION data;
- JOINTS_0;
- WEIGHTS_0;
- placement matrices;
- materials or textures;
- animation times;
- topology;
- source action identity.

The correction is applied to all currently animated Tower families E/F/G so they remain in one consistent model basis.

## Validation after the fix

The formal glTF bind identity remains exact within float tolerance:

```text
max inverse(mesh) * joint * inverseBind identity error
= 2.7247281582098992e-06
```

Family-E skeleton bounds after basis restoration:

```text
extent X/Y/Z = 0.495320 / 0.854148 / 1.676767
```

which now agrees with the native body orientation and scale.

Weighted geometry/joint alignment improved from:

```text
median 1.704271 m
```

to:

```text
median 0.014324 m
min    0.004582 m
max    0.230289 m
```

The independently evaluated animated skin bounds improved from a pathological:

```text
2.884874x bind diagonal
```

to a physically bounded:

```text
1.152549x bind diagonal maximum
```

The two exact Family-E animation families now sample approximately:

```text
809D8572 : ~0.885x–0.915x bind diagonal
80C7AE98 : ~1.143x–1.153x bind diagonal
```

rather than expanding the body two-to-three times its bind size.

## Proof boundary

This closes the specific exploded/misoriented animated E/F/G skeleton bug.

It does not claim that all Tower visual issues are solved.  Remaining work includes:

- common/decal transparent cards currently rendered through incomplete portable material semantics;
- exact D1 blend/test/additive state reconstruction;
- incomplete portable texture-role coverage for many materials;
- non-moving articulated families whose runtime-rig/animation ownership is not yet source-closed;
- final Blender-friendly action/default preview behavior without changing source semantics.
