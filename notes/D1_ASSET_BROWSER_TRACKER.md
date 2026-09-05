# Destiny 1 Asset Browser / Tracker

Status: active, 2026-09-05.

The project now has a human-facing inventory/browser layer in addition to the low-level Tiger reverse-engineering tools.

## Current census

Archive:

- 2,105 physical PS4 package files
- 337 unique logical package IDs
- 1,045 collapsed package-family prefixes
- 54 archive-level map/world/activity content roots

Retail inventory (`80A5FFBE`):

- 8,609 exact retail inventory hashes/FileHashes
- 7,541 of the 8,609 hashes have a preserved historical D1 manifest definition; 1,068 do not
- 7,252 records have a preserved native D1 icon path
- 6,508 of those native icons were successfully mirrored locally/offline
- 3,981 records are marked `hasGeometry` by the historical presentation manifest
- 1,101 records classify as actual weapon item types (Auto Rifle, Scout Rifle, Hand Cannon, Pulse Rifle, Sniper Rifle, Shotgun, Fusion Rifle, Rocket Launcher, Machine Gun, Sidearm, Sword)

Pattern/resolver layer:

- 1,414 retail pattern candidates carry an exact `weaponSandboxPatternIndex`
- all 1,414 resolve to an exact sandbox-pattern `s_entity`
- 1,137 currently have a resolved visual `EntityDataROI` selection
- shared first-person owner/context is currently proven for Gjallarhorn Year 3; the generic context->owner resolver remains active work

Historical D1 activity/destination presentation layer:

- 546 Activity definitions
- 541/546 have PGCR/background paths and all 541 were mirrored locally/offline
- 203 activity icons mirrored
- 15 unique activity destinations
- 10 destination icons mirrored
- 33 explicit named Crucible map definitions with non-placeholder PGCR art (e.g. The Anomaly, Bannerfall, Twilight Gap, Rusted Lands, Shores of Time, Icarus, Vertigo)

The 33 public Crucible map definitions and the archive's internal `ps4_pvp_*` roots are kept as separate evidence layers until an exact serialized package/activity join proves each mapping. Similar-looking names are not enough.

## Presentation metadata policy

Historical/public D1 manifest definitions may enrich browser cards with:

- human-readable name and description
- item/activity type
- rarity
- native Bungie icon
- Activity PGCR/background art
- destination/place name and icon

These fields are presentation metadata only. They MUST NOT be used to claim an archive/Tiger ownership edge is solved. Resolution badges always come from the byte-proven package/investment graph.

The preserved `nmlorg/destiny-db` definitions are used for this enrichment. For example, a Gjallarhorn definition contains `itemName`, `itemTypeName`, `tierTypeName`, `icon`, `gearArtArrangementIndex`, and `weaponSandboxPatternIndex`; the latter two corroborate but do not replace our retail-byte join.

## Browser V3 behavior

The standalone V3 HTML browser supports:

- All Items: all 8,609 retail inventory records.
- Weapons: 1,101 actual weapon item definitions, no longer conflating ships/vehicles/Ghosts with weapon-pattern candidates.
- Armor.
- Ships / Vehicles / Ghosts.
- Has Geometry.
- Activities: 546 historical D1 activities with PGCR art, destination/place/type metadata, party size and matchmaking data.
- Crucible Maps: 33 explicit named map records with PGCR art.
- Archive World Roots: the 54 separately byte-derived package roots.
- Package Families: all 1,045 collapsed package namespaces.

Item detail panels expose:

- inventory hash and retail definition FileHash
- native icon source
- historical geometry flag
- arrangement/pattern metadata
- exact resolver pattern entity/type hashes where applicable
- resolved `EntityDataROI` hashes
- current shared owner status
- unresolved graph edges

The UI supports search, category/type/status filters, pagination, and CSV export.

## Image hierarchy

Preferred visual for each catalog record:

1. Native D1 manifest icon or Activity PGCR image.
2. Recovered UI/Director texture from the actual PS4 package archive.
3. Automatically rendered thumbnail/turntable from an exported model/world fragment.
4. Neutral hash/category placeholder only while no proven visual has been associated yet.

Current offline bundle already contains 6,508 native inventory icons and 541 Activity PGCR backgrounds.

## Raw UI / Director art recovery

The first strict UI census located exact split-TAR members for:

- `ps4_ui_core_000a`
- `ps4_ui_menus_0018`
- `ps4_ui_orbit_0026`
- `ps4_ui_pve_002d`
- `ps4_ui_pvp_0034`

Those exact offsets are checkpointed in `evidence/d1_ui_member_catalog.json`, eliminating future archive walks.

The strict exporter recovered multiple genuine `ui_core` PNGs before one snapshot-specific Oodle backing block failed. The recovered set includes several 1230x495 presentation/banner images and UI glyphs, proving the UI texture route is valid.

For full discovery, `tools/d1_texture_census_tolerant.py` and `.github/workflows/d1-ui-art-census-v2.yml` now perform a per-TagHash, newest-to-oldest generation-safe census. Individual bad generations are recorded rather than aborting the family. This is targeted especially at `ui_orbit`, where Director imagery is expected to be concentrated.

## Reproducibility tools/workflows

- `tools/d1_asset_browser_seed.py`
- `tools/d1_contact_sheet.py`
- `.github/workflows/d1-full-inventory-manifest-catalog.yml`
- `.github/workflows/d1-full-inventory-icon-mirror.yml`
- `.github/workflows/d1-activity-image-catalog.yml`
- `evidence/d1_ui_member_catalog.json`
- `tools/d1_texture_census_tolerant.py`
- `.github/workflows/d1-ui-art-census-v2.yml`

## Next expansions

The browser should continue growing into explicit resolver-backed sections for characters/enemies, props/architecture, textures/materials, animations, cinematics, UI, audio, and unknown resources. Each card should preserve separate readiness for geometry, materials/textures, rig, animation, placement/assembly, and full export rather than collapsing everything into one guessed status.
