# PS4 Tower spawned actor runtime + D912 location closure — 2026-09-06

This note records the source-derived Tower NPC/AI reversal checkpoint after the separate D1 Activity NPC/enemy/other-AI carrier path was closed. It intentionally separates **identity**, **runtime animation compatibility**, **source locations**, and **simultaneous placement semantics** so later export work does not accidentally promote an inference.

## 1. Population source

The spawned population comes from the D1 Activity path explicitly identified by the pinned Charm source as the NPC/enemy/other-AI path, rather than the ordinary collapsed world-placement path. Across the Tower scenario variants this closes to:

- 57 distinct spawned EntitySK / `s_entity` definitions.
- 134 distinct D912 scripted-entity tables across all variants.
- 324 source scripted records in the broader spawned-actor census.
- 57/57 SEntities successfully reopened through the universal retail package catalog.

The universal reclassification run is GitHub Actions run `34070481839`, artifact `10000295087` (`D1-TOWER-SPAWNED-ENTITY-UNIVERSAL-RECLASSIFY`). It proves:

- 57/57 are `rigged_articulated_entity_candidate`.
- 57/57 have an exact visual model.
- 57/57 have an exact skeleton resource.
- 57/57 have an exact runtime rig.
- 57/57 have an exact EntityChildren resource.
- 57/57 carry source-owned name resources.
- zero unresolved dependencies remain.

Bone-count distribution is 61×1, 63×3, 67×12, 70×29, 72×12.

## 2. Exact retail identities

Specific name StringHashes resolve through the exact retail `character_names` bank, not geometry/proximity:

- Eva Levante
- The Speaker
- Master Rahool
- Banshee-44
- Cayde-6
- Ikora Rey
- Lord Shaxx
- Executor Hideo
- Lakshmi-2
- Arach Jalaal
- Tess Everis
- Amanda Holliday
- Xûr
- Commander Zavala
- Eris Morn
- Lord Saladin
- Petra Venj

The generic City Frame hash resolves to `City Frame 22-10` and is carried by twelve 67-bone spawned SEntities.

## 3. Reusable runtime families

The 57 actors collapse to a small set of exact source-owned model/skeleton/rig/animation-owner architectures. Important shared targets are:

| Target | Skeleton | Bones | Runtime rig | Controls | Animation control |
| --- | --- | ---: | --- | ---: | --- |
| common human | `809D80C9` | 70 | `809D80D3` | 64 | `809D80FC` |
| Speaker | `8087640B` | 63 | `80C880C9` | 63 | `80C880D9` |
| City Frame | `809D8613` | 67 | `809D80EE` | 61 | `809D80FC` |
| leader shared (Ikora/Zavala/Cayde/Saladin) | `80AD27B2` | 72 | `80A7F90B` | 66 | `809D80FC` |
| Shaxx | `8087676B` | 72 | `80C88404` | 66 | `80C88439` |
| Petra | `8087676E` | 61 | `8087676F` | 55 | `809D80FC` |

The animation-control owner architecture is source-owned on every actor. The two owner halves are:

- `808020BF -> 808029D2`, control FileHash at owner payload offset `+0x110`.
- `80802B92 -> 808020BB`, control FileHash at owner payload offset `+0x448`.

For each actor, both halves converge on the same exact `80802C0E` animation control.

## 4. Native retarget proof — complete

The earlier dimensional-equality test was intentionally superseded. D1 does not require a selected clip's source skeleton/control dimensions to equal every destination actor's dimensions. The production path is:

`read_animation -> decode_animation -> calc_control_limit -> rig_retarget -> convert_obj_to_local`

The universal retarget matrix run `34071311801`, artifact `10000616446`, executes that exact pinned path for every selector-selected clip against each unique target runtime.

Result: **all six runtime targets close with zero violations**.

| Target | Selected clips | Successful retargets | Failures | Native control-limit set |
| --- | ---: | ---: | ---: | --- |
| common human 70 | 267 | 267 | 0 | 58 or 64 |
| Speaker 63 | 30 | 30 | 0 | 63 |
| City Frame 67 | 267 | 267 | 0 | 49 |
| leader 72 | 267 | 267 | 0 | 58 |
| Shaxx 72 | 267 | 267 | 0 | 49 |
| Petra 61 | 267 | 267 | 0 | 49 |

There are 297 unique selected retail clips across the three exact controls. This proves the apparently mismatched 61/67/72-bone actors are not static or malformed: the shared animation bank is deliberately retargetable to their source-owned rigs.

This proof does **not** select a startup/default/idle action. Selector state semantics remain unresolved unless an exact StringHash preimage is found.

## 5. D912 source locations and the previously opaque location tail

Charm pins `S2B138080` to size `0x30`, naming only Location Vector4 at `+0x00` and Rotation Vector4 at `+0x10`. The project preserved `+0x20..+0x2F` losslessly. Corpus-wide decoding shows four little-endian u32 words:

- `+0x20` = `811C9DC5` for every observed Tower location.
- `+0x24` = `811C9DC5` for every observed Tower location.
- `+0x28` = 0, 1, 2, or 3.
- `+0x2C` = 0 or 2.

The fail-closed probe run `34071241045`, artifact `10000520242`, proves `+0x28` is a **structural SD614/D912 group indexing key** across the Tower corpus:

- 8 scenario variants checked.
- 134 unique D912 tables.
- 779 scenario-expanded location records.
- 254 unique physical D912 location records.
- every `+0x28` value is in range for its source D912 group array.
- every table's `+0x28` sequence is nondecreasing.
- duplicated D912 tables serialize identically across scenario variants.
- zero validation violations.

This yields 193 unique exact EntitySK/location associations where the indexed source group contains one unique non-null EntitySK. 61 locations remain explicitly ambiguous because their indexed group contains multiple unique EntitySKs.

The gameplay semantic name of `+0x28` is intentionally unset. The semantics of `+0x20`, `+0x24`, and `+0x2C` are also intentionally unset.

## 6. Important placement boundary

A source-defined D912 location is not automatically proof that every listed location for an EntitySK is simultaneously active. Some identities (notably Xûr and The Speaker) occur at multiple source locations. Until the remaining D912 behavior/type semantics are resolved, exporters must preserve these as source-owned location choices/records rather than blindly instantiating duplicates.

The broom/sweeper is also **not** solved by nearest-NPC proximity:

- no D912 AI location lies within 5 m of the broom across all eight Tower scenario variants.
- the nearest source-owned AI location is about 8.72 m away and belongs to a multi-actor group.
- all four shared actor EntityChildren resources decode with child count zero, so the broom is not attached through those common actor child arrays.

The twelve City Frame actors remain the strongest source-defined sweeper family candidates, but no City Frame→broom ownership claim is promoted without a literal serialized relationship.

## 7. Export direction from this checkpoint

The correct Tower actor export pipeline is now:

1. source-owned spawned SEntity -> exact model-parent EntityResource;
2. exact stage-0 visible model ranges + owning-parent external material selection;
3. exact source skeleton/weights/runtime rig;
4. source-owned animation owner -> control -> selector-selected retail clips;
5. production D1 retarget to the concrete actor rig;
6. D912 source location graph, with simultaneous/conditional placement semantics kept separate until proven;
7. exact shader texture resources and portable Blender material approximation without dropping native inputs.

The next active build is exporting the thirteen unique source-owned spawned-actor model/parent visual families using the same already-validated D1 material and geometry pipeline used for the earlier articulated Tower layer.
