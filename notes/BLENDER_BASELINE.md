# Blender baseline

Updated: 2026-09-06

## Active project baseline

All active Destiny 1 Blender-backed tooling, CI canaries, generated `.blend`
artifacts, and Blender compatibility claims use:

```text
Blender 5.2.1 LTS
Blender 5.2 series
release/build date: 2026-08-25
LTS series supported through July 2028
```

The canonical CI installer is:

```text
tools/install_blender_lts.sh
```

Its default version is `5.2.1`. Workflows must use that installer rather than
copying a Blender download URL/version/checksum procedure inline. A deliberate
compatibility experiment may override `BLENDER_VERSION`/`BLENDER_SERIES`, but
such a run does not change the project baseline.

## Current validation

The `80CA0DDA -> 809DCD66` Tower native-equation adapter has been validated on
Blender 5.2.1 LTS at two levels.

Structural import/node/save-reopen canary:

```text
Actions run 34050905926
artifact    9994505098 d1-tower-809dcd66-blender-521-canary
artifact sha256 74aaf9224e597ecc06c722101e8bcdd2a3a4297d887f480368b3b45fcdb71f1a
```

Retail scene canary:

```text
Actions run 34050944445
artifact    9994546945 d1-tower-809dcd66-retail-blender-preview
artifact sha256 440a774e6a211554c78931da4459cbe61bad1651ecb5eb5e38f2c3bc08d835db
```

The retail build contains the exact scoped target population:

```text
12 geometry variants
64 placements
5 material variants present in Tower cell 80C98254
exact retail t0/t1 decoded images
explicit D1 normal/tangent/tangent-W application attributes
native-equation Blender node materials
```

Final packed Blender artifact from that run:

```text
D1_TOWER_809DCD66_RETAIL_64_NATIVE_EQUATION_PREVIEW.blend
bytes   316170
sha256  b6e4f2e6cfab90ede2f83e7113ae4cb1ab001b3ae9f55160ee2ae7c367fa2354
Blender version string: 5.2.1 LTS
```

## Historical compatibility evidence

Blender 4.5.13 LTS was previously used to establish the first executable
`809DCD66` adapter canary. That run remains valid historical evidence but is no
longer an active project baseline or CI target.

```text
historical run      34049476189
historical artifact 9994103064
```

Do not create new 4.5.x-pinned workflows or outputs unless explicitly performing
a backward-compatibility experiment.

## Other project repositories

An organization-wide code search performed during this migration found no other
active `lizardpeter` repository with a hard-coded Blender 4.x executable/version
pin. Repositories that merely mention Blender as an authoring/import tool require
no binary migration until they add Blender-executed tooling. Any future Blender
CI/tooling added to those projects should use Blender 5.2.1 LTS (or the then-current
explicitly adopted project baseline) rather than introducing an older pin.
