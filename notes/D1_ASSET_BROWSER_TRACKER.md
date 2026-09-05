# Destiny 1 Asset Browser / Tracker

Status: active, 2026-09-05.

The project now has a human-facing inventory layer in addition to the low-level Tiger reverse-engineering tools.

Current first-cut browser data:

- 2,105 physical PS4 package files
- 337 unique logical package IDs in the archive package census
- 1,045 collapsed package-family prefixes
- 54 archive-level map/world/activity roots
- 1,414 retail weapon candidates with exact `weaponSandboxPatternIndex`
- 1,137 weapon candidates with a resolved visual `EntityDataROI` selection
- 1,414 weapon candidates with an exact weapon-pattern entity
- shared first-person owner/context remains proven for Gjallarhorn Year 3 and unresolved generically for the other weapon candidates

## Presentation metadata policy

Historical/public D1 manifest definitions may be used to enrich a browser card with:

- item/activity human-readable name
- description
- item/activity type
- rarity
- native Bungie icon
- PGCR/background art when present

These fields are presentation metadata only. They MUST NOT be used to claim an archive/Tiger ownership edge is solved. Resolution badges always come from the byte-proven package/investment graph.

The preserved `nmlorg/destiny-db` D1 definitions are suitable for weapon-card enrichment. A record such as Gjallarhorn contains `itemName`, `itemTypeName`, `tierTypeName`, `icon`, `gearArtArrangementIndex`, and `weaponSandboxPatternIndex`; the latter two independently corroborate but do not replace our retail-byte join.

## Browser behavior

The standalone HTML browser currently supports:

- Weapons tab with native D1 icon/name enrichment, pagination, filters, and export-status badges.
- Weapon detail panel showing inventory hash, definition FileHash, art arrangements, resolved EntityDataROI hashes, weapon-pattern index/type/pattern entity, shared-owner status, and unresolved edges.
- Maps/world roots tab containing the 54 archive-derived roots.
- Package families tab for browsing collapsed package namespaces.

`tools/d1_asset_browser_seed.py` builds the embedded resolver seed from:

- `resolved_weapon_manifests.json`
- `d1_map_content_roots.csv`
- `archive_package_inventory.json`

## Image hierarchy

Preferred visual for each catalog record, in order:

1. Native Bungie/D1 manifest icon or activity/PGCR image.
2. Recovered UI/Director texture from the actual PS4 package archive.
3. Automatically rendered thumbnail/turntable from an exported model or world fragment.
4. Neutral hash/category placeholder only while no proven visual has been associated yet.

Weapon native inventory icons are therefore useful immediately, while maps are being upgraded by an explicit UI-art census of `ps4_ui_core`, `ps4_ui_menus`, `ps4_ui_orbit`, `ps4_ui_pve`, and `ps4_ui_pvp`.

## UI art census

`.github/workflows/d1-ui-art-census.yml`:

- recovers all physical siblings for UI families `000A`, `0018`, `0026`, `002D`, and `0034` from the split PS4 archive,
- opens the highest logical snapshot with sibling files present for block-patch resolution,
- bulk exports resident texture headers through `tools/d1_texture_export.py`,
- decodes portable PNGs,
- creates labeled contact sheets with `tools/d1_contact_sheet.py`,
- publishes manifests and extracted PNGs as an Actions artifact.

The purpose is to identify Director map fragments, destination artwork, activity icons/backgrounds, decals, and other game-UI-only imagery that the public D1 definitions do not fully expose.

## Next browser expansions

The same tracker should grow into tabs for armor, characters/enemies, ships/vehicles/ghosts, props/architecture, textures/materials, animations, cinematics, UI, audio, and unknown resources. Each card should carry provenance and separate readiness for geometry, materials/textures, rig, animation, placement/assembly, and full export.
