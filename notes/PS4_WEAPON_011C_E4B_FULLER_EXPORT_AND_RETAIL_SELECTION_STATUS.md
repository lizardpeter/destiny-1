# PS4 011C E4B fuller export and retail-selection boundary

Status: binary-verified working export; exact Investment ownership remains unresolved.

## Native 011C fuller model

The 011C family contains the following native entity-backed model chain:

- s_entity `80A39E47`
- EntityResource `80A39E48`
- s_entity_model `80A39E4B`
- texture plate header `80A39E4C`

`80A39E4B` is a native geometric superset of the earlier `80A39E12` shell. Its one mesh has 4044 vertices and these exact LOD1 ranges:

- offset 114, count 2015 -> 1294 nondegenerate triangles, material `80A382A6`
- offset 2240, count 2188 -> 1310 nondegenerate triangles, material `80A382A6`
- offset 4429, count 2706 -> 1694 nondegenerate triangles, material `80A3CED5`

Total: **4298 LOD1 triangles**. No geometry is mirrored or synthesized.

The two native materials share the final PS4 shader program:

- VS `80A3D28E`
- PS `80A3D145`

The E4B owner plate is `80A39E4C` with albedo `80A39E50`, normal `80A39E51`, and gstack `80A39E52`; each plate has five transforms.

## Working GLB outputs

Workflow `.github/workflows/build-weapon-011c-e4b-full.yml` completed successfully in run `33909740957` from commit `829542f2d01a2da43ac7ceb610994795b9008326`.

Artifact `80A39E4B-fuller-weapon-visible-animations` contains:

### `80A39E4B_WEAPON_FULLER_PROOF_RIG_12CLIPS.glb`

- 9,598,412 bytes
- SHA-256 `cec669d6c1603b887c3695272b4be298b0aa9ca30db2855a68a3586680e75be0`
- 1 mesh / 3 native LOD1 primitives
- 4044 vertices / 4298 LOD1 triangles
- 2 materials
- 10 images
- recovered 73-bone skeleton / 1 skin
- all 12 source animation clips
- rigid attachment to recovered weapon Pedestal control `C410084A`

### `80A39E4B_WEAPON_FULLER_VISIBLE_ANIMATIONS.glb`

- 9,322,940 bytes
- SHA-256 `40d3215dfc885552c4320f704751c0ce901e6620827a5966913a557f2368aea9`
- same fuller geometry and textures
- four source clips whose recovered hierarchy produces measurable visible whole-weapon motion are compatibility-baked directly to a `WeaponRoot` node:
  - `80A39DF7_VISIBLE_WEAPON`
  - `80A39DFA_VISIBLE_WEAPON`
  - `80A39DFB_VISIBLE_WEAPON`
  - `80A39DFF_VISIBLE_WEAPON`

This bake does not invent internal magazine/trigger/bolt motion. Native skin/part weights for those mechanisms remain unproven.

## Important retail-selection correction

A previous working hypothesis was that ten Investment ArtArrangement indices connected through 0140 entities into the 011C E12/E4B model family. That hypothesis is now disproven.

The ten arrangements were successfully reversed through the retail inventory item map and their exact selected 0140 model EntityResources were decoded. Their selected models are:

- 4184 -> `80A81DF0`
- 4191 -> `80A81D1C`
- 4202 -> `80A8195F`
- 4203 -> `80A81D3E`
- 4211 -> `80A818E2`
- 4213 -> `80A816D6`
- 4242 -> `80A81A6A`
- 4270 -> `80A81F05`
- 4271 -> `80A81A48` and `80A818F1`
- 4283 -> `80A818C3` and `80A81641`

None selects `80A39E12` or `80A39E4B` as its model. Some of those 0140 models reference 011C material hashes; that is material/resource reuse, not proof of 011C model ownership.

The earlier exhaustive ArtArrangement EntityParent reverse solve resolved 8230 of 8280 unique parents and found **zero direct `EntityDataROI` matches for `80A39E0E`**. The saved resolution corpus also contains no `80A39E47` string among resolved parents. Fifty parents failed Oodle decode and therefore prevent a strict 100% negative statement.

Separate scans also found no proven parent linkage for `80A39E0E`/`80A39E47` through the known D1 EntityChildren resource path or direct raw structured-payload backlinks in the scanned Investment/gear package families.

Therefore the current proven statement is:

> `80A39E12` and `80A39E4B` are genuine native 011C weapon models with native materials, texture plates, skeleton-compatible attachment, and recovered animation hierarchy, but their exact retail Investment item-selection role is not yet byte-closed.

It is plausible that this family serves a first-person, animation, preview, component, or other internal weapon role, but that remains inference and must not be promoted to binary fact.

## Next closure targets

1. Resolve or classify the remaining 50 failed Investment EntityParents and explicitly test `80A39E47` as well as `80A39E0E`.
2. Reverse the resource classes behind the generic imported 011C resources (`80802475/80802733` and `80800594/808008F6`) rather than treating those resources as model selectors.
3. Continue searching for a byte-proven owner/selector of `80A39E47`/`80A39E4B` outside the already-eliminated direct ArtArrangement path.
4. Keep the fuller E4B GLB as the best current native geometry/texture/animation export fixture while exact retail role is investigated.
