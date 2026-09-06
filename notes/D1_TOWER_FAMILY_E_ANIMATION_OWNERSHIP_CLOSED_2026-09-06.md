# D1 Tower Family E animation ownership closure — 2026-09-06

This checkpoint closes the source-owned animation-selection chain for the Tower's 67-bone articulated family without assigning an appearance-based NPC/vendor semantic.

## 1. Family identity

The already-proven articulated family is:

```text
model parent   80CA0CD8
EntityModel    80CA0CFC
skeleton       809D8613   67 nodes
runtime rig    809D856E   67 controls
rig component  75F560CA x67
placements     6 unique WorldIDs
```

The green r7 articulated model export independently fixes the render target at:

```text
source meshes                  4
selected stage-0 draw ranges  26
triangles                 20,575
active materials               8
bounds min  [-0.21659237, -0.45047688, -0.00918162]
bounds max  [ 0.47331959,  0.45047688,  1.84227979]
```

All Family-E meshes have already passed the exact D1 articulated skin-storage census. Their primary streams use only project-closed rigid/inline2/inline4 forms; no unsupported skin mesh or validation violation remains.

## 2. Six runtime placements split into two animation-owner variants

The six placements do **not** serialize one shared animation owner.

### Tower-local owner variant

```text
SEntity 80C7AE3E
WorldID 288E250AFDC06BC7
runtime placements 1

SEntity resource list contains:
  80C7AE48
  80C7AE49

literal owner edges:
  80C7AE48 +0x110 -> 80C7AE68
  80C7AE49 +0x448 -> 80C7AE68

control 80C7AE68
  -> exactly one selected clip: 80C7AE98
```

### Generic homologous owner variant

```text
SEntity 80C7AD82
WorldID 1F763204E6BF153E
runtime placements 1

SEntity 80CA0CD6
WorldIDs:
  28F88CAFCCE615AC
  5A9D48129FB3D22A
  5F523A4A340754A7
  C588D8EE0F1F493D
runtime placements 4

Both SEntity variants contain:
  809DF581
  809DF582

literal owner edges:
  809DF581 +0x110 -> 809D856F
  809DF582 +0x448 -> 809D856F

control 809D856F
  -> exactly one selected clip: 809D8572
```

Therefore the exact current split is:

```text
1 placement  -> 80C7AE68 -> 80C7AE98
5 placements -> 809D856F -> 809D8572
```

This is source-owned selection evidence. Neither clip is called `idle`, `ambient`, `vendor`, or similar until a separate semantic state-name proof exists.

## 3. Exact clip compatibility and frame counts

Fresh-retail parsing closes both selected clips against the exact Family-E skeleton/rig:

```text
80C7AE98
  frame count           62
  node count            67
  rig control count     67
  runtime components    75F560CA x67
  exact family match    true

809D8572
  frame count          324
  node count            67
  rig control count     67
  runtime components    75F560CA x67
  exact family match    true
```

The 62-frame count for `80C7AE98` is parsed from the retail clip. It is **not** inferred from the ~2.0333335 scalar in control `80C7AE68`.

## 4. Logical-package correction

An intermediate canary attempted to open `80CA0CD6` through only physical member `ps4_city_tower_destination_0250_5.pkg` and failed the tool's single-member availability gate.

That was a validator architecture mistake, not an ownership contradiction. D1 package families are logical multi-member archives, and entry-table presence is not a safe substitute for logical-family payload resolution.

The corrected path:

1. pins all six current 0250 physical siblings by exact TAR offset, size, and SHA-256;
2. verifies current `packages.txt` family membership;
3. builds a multi-member `Corpus`;
4. chooses a class-matching resident payload through the logical package;
5. only then parses the SEntity resource list.

The green current resolution reports:

```text
80CA0CD6
  source snapshot  ps4_city_tower_destination_0250_5.pkg
  generation       5
  package          0250
  entry index      3286
  reference        80800734
  payload size     13,508 bytes
```

The important durable rule is not that this one payload happens to resolve from `_5`; it is that future validators must preserve logical multi-member resolution and must not replace it with a physical-member assumption.

New exact family catalog:

```text
evidence/d1_tower_0250_member_catalog.json
```

## 5. Fresh-retail validation

Workflow:

```text
.github/workflows/d1-tower-family-e-animation-ownership.yml
```

Green run:

```text
run       34057701526
artifact  9996502914
commit    e7cac0d78745aa08629d8a2c614fd51964124927
```

Result:

```text
status                       D1_TOWER_FAMILY_E_ANIMATION_OWNERSHIP_CLOSED
skeleton nodes               67
runtime-rig controls         67
runtime placements            6
unique WorldIDs               6
80C7AD82 selection            owner_selected
80C7AE3E selection            owner_selected
80CA0CD6 selection            owner_selected
violations                    0
```

The first failed canary stopped before animation parsing because the workflow lacked NumPy. The second failed because it still used a single physical 0250 member for `80CA0CD6`. Both failures are retained as useful provenance and were fixed narrowly; no ownership assertion was relaxed.

## 6. Current promotion boundary

We may now promote the following from `compatible candidate` to **source-owner-selected animation** for Tower Family E:

```text
80C7AE3E -> 80C7AE98
80C7AD82 -> 809D8572
80CA0CD6 -> 809D8572
```

We may **not** yet promote any of those SEntities to a named Tower vendor/NPC from appearance alone.

## 7. Next export step

The next visual checkpoint should build a six-placement Family-E animated layer with these fail-closed requirements:

1. begin from the proven 26-range / 20,575-triangle `80CA0CFC` model;
2. reconstruct every `JOINTS_0` / `WEIGHTS_0` row from exact retail D1 vertex bytes;
3. preserve all 26 draw ranges and all 20,575 triangles;
4. instantiate six separate 67-joint skeletons at the six exact WorldID transforms;
5. assign the source-selected clip per SEntity/WorldID:
   - `288E250AFDC06BC7` -> `80C7AE98`;
   - the other five -> `809D8572`;
6. preserve clip identity and owner chain in glTF extras/report metadata;
7. do not assign semantic animation names without separate StringHash/state proof;
8. only after the animated Family-E layer validates should it replace those six bind-pose instances in the integrated Tower layer.

This checkpoint deliberately leaves all other articulated families unchanged.
