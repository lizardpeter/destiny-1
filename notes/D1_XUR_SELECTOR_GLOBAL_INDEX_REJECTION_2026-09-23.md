# D1 Xur external-material selector: global permutation-index rejection

Date: 2026-09-23  
Target: Xur `46C55854`, model `80C88CEF`, model parent `80C88CE2`

## Result

The later MIDA/Charm-family model uses one global material permutation index and selects each external-material range by:

```text
local_member = global_permutation_index % MaterialCount
```

That rule does **not** reproduce the exact D1 Xur candidate selection.

The exact Xur evaluator was extended to test whether one global integer could simultaneously reproduce every candidate-local member index across the 81 source-decoded D1 external-material groups.

The unique candidate local indices grouped by `MaterialCount` are:

```text
MaterialCount  selected local member
2              1
3              2
4              3
6              5
12             10
13             10
14             11
24             22
```

The LCM of the group sizes is 2184. There is **no integer modulo 2184** satisfying all of those congruences, and therefore no compatible integer below the 108-entry descriptor count either.

Workflow proof:

- run: `35935703687`
- branch commit: `f860e19ee77e94d7b99c7baedf2865eed7306c67`
- evaluator: `tools/d1_xur_candidate_permutation_evaluator.py`

## Consequence

The D1 Xur external-material graph must not be implemented by copying the later global-index/modulo consumer.

The strongest current D1-specific rule remains descriptor-local:

1. take the source-decoded Xur own-model switch configuration;
2. test each member descriptor list-A against that configuration;
3. retain satisfied descriptors;
4. select the unique greatest-specificity satisfied descriptor;
5. allow the empty list-A descriptor to act as fallback when no more-specific descriptor matches.

That rule remains a **candidate retail evaluator**, not yet a source-closed consumer algorithm, even though it:

- selects uniquely for all 81 Xur groups;
- calibrates uniquely over 70,281 / 70,281 Tower placement×group evaluations;
- agrees with the exact descriptor/list-B sentinel structure;
- produces the current corpus-calibrated Xur visual material set.

## Remaining retail proof

To promote the candidate rule to retail semantics, the D1 executable consumer must be located and its behavior closed against:

- `ExternalMaterialsMap` at model-parent `+0x230`;
- indirect uint16 descriptor-index storage at `+0x250`;
- `FE1A8080` descriptors at `+0x260`;
- material bank at `+0x270`;
- switch-record containers at `+0x50`;
- the instantiated switch configuration carried by the Xur placement/resource path.

Until then, `E6/E7/E8` live-selection gates remain false.

## Policy

This negative result is a proof boundary, not a setback: it removes an incorrect implementation family. Future D1 selector work must follow the descriptor-local consumer, not the later MIDA global permutation-index abstraction.
