# Destiny 1 programmatic bulk ripper architecture

## Goal

The production target is not a set of per-weapon scripts.  It is an evidence-driven
asset resolver/exporter capable of walking the retail Destiny 1 graph in bulk.

The system must never choose an asset because it is adjacent in a package, has a
similar name, has the same node/control counts, or happens to decode without an
exception.  Those are useful diagnostics, not ownership evidence.

## Weapon graph

The current canonical weapon graph is:

```text
InventoryItemHash
  -> retail inventory definition FileHash              [80A5FFBE]
  -> equippingBlock
       -> gearArtArrangementIndex[]
       -> weaponSandboxPatternIndex

gearArtArrangementIndex
  -> art arrangement row                                [80A5FFA7 + 80A7E1DD]
  -> EntityParent FileHash[]
  -> EntityParent +0x10 -> EntityDataROI FileHash[]
  -> s_entity / EntityResource graph
  -> s_entity_model(s)
  -> geometry / native material hashes / texture plates
  -> materials -> shaders -> texture FileHashes

weaponSandboxPatternIndex
  -> weapon pattern row                                 [80A5FFA9]
       -> WeaponTypeHash
       -> PatternHash
       -> PatternGlobalTagIdHash
  -> sandbox-pattern assignment                         [80A7E1DC]
  -> exact sandbox-pattern s_entity
  -> weapon-internal resources / rig / clips
  -> cross-package pattern action/context resources

shared first-person context
  -> exact shared s_entity owner
  -> owner Resource[]
       -> runtime rig
       -> skeleton
       -> 80802C0E action control
       -> 8080222A wrapper
  -> action StringHash -> exact clip selector
  -> runtime-rig component-prefix retarget
  -> exact weapon attachment/motion node
  -> standalone external-motion animation
```

The visual, weapon-internal, and shared-viewmodel layers are separate ownership
layers.  They are composed at export time; they must not be collapsed into one guessed
skeleton.

## Retail bulk tables already closed

### Inventory definition map

`80A5FFBE` contains 8,609 retail InventoryItemHash -> inventory-definition FileHash
rows.

The definitions are concentrated in two package families:

```text
0131 : 4,092
0132 : 4,517
-------------
       8,609
```

Reusable decoder:

```text
tools/d1_inventory_item_map.py
```

### Art arrangements

`80A5FFA7` / `80A7E1DD` decode to 4,473 art arrangements.

Every serialized EntityParent FileHash carries its own package id and file index.  The
bulk resolver therefore opens exactly the package family named by the FileHash and
reads EntityParent +0x10 for the final EntityDataROI hash.

Reusable resolver:

```text
tools/d1_remote_arrangement_parent_resolve.py
```

Validated physical split-TAR locations for the required investment-asset families are
kept separately as transport evidence:

```text
evidence/d1_investment_asset_member_catalog.json
```

The catalog never changes semantic ownership.  It only prevents rediscovering package
byte locations during every bulk run.

### Weapon patterns

`80A5FFA9` contains 208 weapon-pattern rows.  `80A7E1DC` joins all 208
PatternGlobalTagIdHash values to sandbox-pattern `s_entity` FileHashes with zero missing
assignments in the current retail dataset.

Reusable decoder:

```text
tools/d1_weapon_pattern_assignment_probe.py
```

## Per-item resolved manifests

`tools/d1_weapon_manifest_join.py` converts the retail tables into one explicit manifest
per inventory weapon candidate.

Each manifest records:

```text
inventory definition
art arrangement indices
resolved visual EntityDataROI hashes
weapon pattern index
WeaponTypeHash / PatternHash
sandbox-pattern s_entity
shared-viewmodel owner profile when proven
unresolved edges
evidence for every resolved edge
```

No unresolved field receives a guessed fallback.

`tools/d1_weapon_export_readiness.py` then creates independent queues:

```text
visual-ready
internal-ready
shared-ready
full-weapon-ready
```

This is important because a missing shared-animation owner must not prevent a completely
proven static weapon from being ripped, and a proven internal pattern rig must not be
misrepresented as first-person recoil/equip motion.

## Shared viewmodel owner profiles currently proven

```text
CA0: 80AA3CA0 -> 80AA3CB2 / 80AA3CB3 -> 80AA3CC2 / 80AA3CC4
CA1: 80AA3CA1 -> 80AA3CB8 / 80AA3CB9 -> 80AA3CC5 / 80AA3CC7
CA2: 80AA3CA2 -> 80AA3CBE / 80AA3CBF -> 80AA3CC9 / 80AA3CCB
```

The owner/resource relationships are serialized and byte-proven.  The current shared
context catalog is:

```text
evidence/d1_weapon_shared_context_catalog.json
```

Only exact assignments are permitted in that catalog.  At the present checkpoint the
Gjallarhorn inventory item is explicitly assigned to CA2; no global
`rocket_launcher -> CA2` rule is asserted merely from weapon type.

## Runtime-rig compatibility rule

Clip header node/control totals are not ownership rules.

The D1 retargeter consumes ordered runtime-rig components.  Matching component hashes
advance the compatible control prefix; a differing component hash stops the retarget.
If counts differ inside a matching component, the common count is consumed and the
retarget stops at that boundary.

The Gjallarhorn CA2 proof demonstrates the rule:

```text
CA2 rig:
  D59A5FE6 : 8
  7CB60FEC : 62
  A5D99EA7 : 3
  = 73 controls

generic idle/ready/jump clips:
  D59A5FE6 : 8
  7CB60FEC : 62
  4FE5F61B : 4
  = 74 controls

native compatible prefix = 8 + 62 = 70 controls
```

The generic 76/74 clips therefore legally retarget to the serialized CA2 75/73 owner
rig.  CA2 reload/fire match all 73 controls.

## Gjallarhorn end-to-end validation

Gjallarhorn is now the production reference fixture for the architecture rather than a
special-case definition of the architecture.

The exact combined build contains:

```text
visual arrangement 1229
full retail geometry/materials/textures
internal 7-bone weapon rig
80AA2E4A / 80AA2E4B internal clips
CA2 shared owner 80AA3CA2
idle        -> 80AA3CD6
ready       -> 80AA3CDA
reload_empty-> 80AA3D40
reload_full -> 80AA3D40
fire        -> 80AA3D42
```

The corrected fire motion is evaluated from CA2 child `E6477C3B`, not the nearly-static
parent `C410084A`; the standalone fire impulse is about 3.34 cm.

Successful combined workflow:

```text
.github/workflows/build-gjallarhorn-rocket-launcher-actions.yml
run 33939153994
artifact D1-Gjallarhorn-Year3-TEXTURED-ANIMATED-SHARED-ACTIONS
```

## Pattern-owned action/context bundle frontier

The next generic bridge is being resolved from the sandbox pattern itself rather than
from weapon-type guessing.

Gjallarhorn pattern 39 `s_entity` (`80A6A017`) serializes resource `80AAECD6`.  That
resource in turn serializes an exact triple:

```text
80AA2DCD -> 80802C0E action control
80AADE4C -> 80800368 context/type table
80AA2DDB -> 8080222A wrapper
```

This is significant because it provides an item-pattern-owned path to action/context
data.  A bulk resolver now scans all 208 pattern `s_entity` Resource[] arrays and reports
such triples only when all three FileHashes are literally serialized in the carrier
resource and resolve to exact global entries:

```text
tools/d1_weapon_pattern_action_bundle_resolve.py
.github/workflows/d1-bulk-weapon-pattern-action-bundles.yml
```

The global package transport locations used by this pass are checkpointed in:

```text
evidence/d1_weapon_globals_member_catalog.json
```

The open semantic question is how the pattern-owned bundle relates to the CA0/CA1/CA2
first-person owner family.  The resolver will not call two controls equivalent merely
because some action clips happen to match.

## Visual exporter frontier

The generic low-level pieces already exist:

```text
tools/d1_entity_model_export.py     geometry / mesh parts / native material hashes
tools/d1_material_decode.py         material / shader / sampler data
tools/d1_texture_export.py          texture export
```

The remaining visual generalization is a manifest-driven arrangement assembler that
replaces fixture-specific presentation scripts such as
`d1_gjallarhorn_1229_apply_textures.py`.  It must consume each resolved arrangement's
actual EntityDataROI/model/material/texture-plate provenance rather than same-name or
package-local fallbacks.

## Category expansion beyond inventory weapons

The package/model/material/texture layer is reusable across asset categories.  Animation
ownership is not universal and must have category-specific resolvers:

```text
weapons     -> weapon pattern + shared first-person context
characters  -> character/entity animation ownership
combatants  -> enemy archetype/entity animation ownership
vehicles    -> vehicle-specific rigs/controllers
world props -> static or prop-specific animation ownership
maps        -> world/placement/instance graph plus geometry/materials
```

The same rule applies everywhere: resolve serialized ownership first, export second,
and retain unresolved edges rather than inventing them.

## Production invariant

A bulk rip is considered correct only when every exported relationship can answer:

```text
Why was this model/material/texture/rig/clip paired with this asset?
```

with a concrete serialized/table/owner/runtime-component edge.  Successful decoding or
visual plausibility alone is not sufficient evidence.
