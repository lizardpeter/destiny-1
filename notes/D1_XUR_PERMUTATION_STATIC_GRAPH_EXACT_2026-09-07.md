# D1 Xur external-material static permutation graph — exact checkpoint

Date: 2026-09-07
Target model: `80C88CEF`
Model-owner EntityResource: `80C88CE2`
Serialized Xur SEntities: `80C7ACC8`, `80C885AA`

Status: **`D1_XUR_MODEL_PARENT_PERMUTATION_STATIC_REFERENCE_GRAPH_EXACT`**

This checkpoint closes the **static serialized reference graph** used by the shared-human D1 model parent. It does not yet claim which member Xur selects at runtime.

## Provenance

Exploratory retail-layout workflow:

- run `34159275748`
- artifact `10032044604`
- artifact SHA-256 `9237d933626e4b93997859b91487e0f62ee85fa1c444cea33a6a7a327dea2333`

Static-graph closure workflow:

- run `34159783006`
- artifact `10032195917`
- artifact SHA-256 `6cb45ab3bb0d683969b6e253f967942cc54185613c3dcfbded7936eb1a208a91`
- workflow commit `80c625968c762d5bac5dd28d0aac69323d00a24e`

Both source Xur SEntities independently resolve the same exact `80C88CE2` payload. Its SHA-256 is:

`335d93b8eb6f02489d4f5308bcd4b09a0a8448900bbeccecf47d76997645aadc`

## Exact D1 model-parent graph

The retail D1 parent resolves these exact structures:

- parent `+0x50`: **55** switch-record containers;
- parent `+0x230`: **81** `ExternalMaterialsMap` entries;
- parent `+0x250`: **46** `uint16` indirect switch-record indices;
- parent `+0x260`: **108** D1 `FE1A8080` descriptors, each four `uint16` fields;
- parent `+0x270`: **820** external Material TagHashes.

The 55 switch records contain a total of **164 exact nonzero `(uint32 key, uint32 value)` pairs**. Every parent `+0x50` outer record validates as a 0x18-byte container whose nested array at `+0x08` contains exact 8-byte key/value pairs. No other aligned early-parent dynamic array passes that complete shape.

## `ExternalMaterialsMap.Unk08` is a descriptor start index

Across all 81 external-material map entries, `Unk08` plus `MaterialCount` partitions the complete 108-entry descriptor bank exactly into these ranges:

```text
start  count
0      12
12     14
26     13
39     24
63     24
87      4
91      6
97      2
99      4
103     3
106     2
```

For local member `j` of an external-material range:

```text
material_bank_index = MaterialStartIndex + j
descriptor_index    = Unk08 + j
```

All 820 material-bank positions therefore receive an exact descriptor association.

## Exact compact descriptor-list encoding

Each D1 `FE1A8080` descriptor serializes:

```text
[countA, startA, countB, startB]
```

For each A/B list independently, the exact retail corpus closes this compact reference encoding:

```text
count == 0:
    start == 0xFFFF
    no switch records

count == 1:
    start is the switch-record index directly

count > 1:
    start is an offset into the +0x250 uint16 list
    read `count` uint16 values
    each value is a switch-record index
```

This interpretation validates all **216 descriptor halves** with zero failures. Every one of the 46 `+0x250` positions is consumed by at least one multi-record descriptor list; there is no unexplained tail.

The logical distinction between descriptor **list A** and **list B** remains intentionally unnamed until runtime evaluation semantics are source-closed.

## Exact switch-key domain

The complete static graph uses four switch keys:

- `51E7A18D`
- `4C58EF8F`
- `26170C92`
- `6EECD523`

The static values include `871AC0EA` under keys `26170C92` and `6EECD523`. Later-strategy MIDA source independently contains a commented configuration path that explicitly skips value `0x871AC0EA`; that is useful comparative evidence for a default/sentinel role, but it is not promoted as D1 semantic authority here.

## Xur-neighborhood material facts

The Xur-specific material hashes occupy particularly informative positions:

- `80C885E6` appears in a member whose descriptor is entirely null/default (`[0,FFFF,0,FFFF]`).
- `80C885E7` likewise appears at a null/default descriptor member.
- `80C885E8` appears at descriptor 96, also null/default.
- `80C885E9` occupies maps whose six alternatives all resolve to the same `80C885E9` material hash; only the descriptors vary.
- `80C885EA` has the same selection-invariant pattern across its six-member ranges.

This is strong evidence that Xur's E6/E7/E8 materials are the fallback members of their shared-human variant groups. It is **not yet** a live-selection proof. The current next gate is to establish Xur's instantiated switch configuration and the A/B descriptor evaluation logic.

## Current proof boundary

Now exact:

- static switch-record bank;
- exact key/value pairs;
- indirect switch-index list;
- descriptor bank;
- descriptor compact-list encoding;
- `ExternalMaterialsMap.Unk08` descriptor-start role;
- exact material-member -> descriptor mapping for all 820 material positions.

Still open:

- human-readable meanings of the four switch keys/values unless exact GlobalStrings resolution succeeds;
- logical evaluation semantics of descriptor list A versus list B;
- Xur's live configuration values;
- exact retail-selected member for each `VariantShaderIndex`;
- final portable material recreation/render state for the selected set.

The exporter must continue to fail closed rather than promote a first-member/default guess as retail selection.
