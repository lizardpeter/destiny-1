# D1 Spektar Pandion exact dye closure — 2026-09-05

This note records the retail byte-level closure of the default dye state for the five-piece masculine Spektar Pandion Titan proof. It intentionally does **not** infer GStack channel meaning or approximate the native Guardian shader.

## Inventory ownership

The five exact D1 inventory definitions are consecutive records in `ps4_investment_globals_0131`:

| Piece | Arrangement | Inventory hash | Item FileHash |
|---|---:|---|---|
| Gauntlets | 3867 | `B4BD27A2` | `80A63E40` |
| Plate | 3868 | `1DF65286` | `80A63E41` |
| Mark | 3869 | `4A37316F` | `80A63E42` |
| Helmet | 3870 | `4A2AD693` | `80A63E43` |
| Greaves | 3871 | `4A5B75DC` | `80A63E44` |

All five serialize the same three dye indices in their D1 `20108080` equipping blocks. The Mark locks channel 1 / dye 8753 and defaults channels 0 and 2; the other four default all three.

## Exact channel table

The D1 global dye-channel table is on-disk FileHash `80A5E249` (Charm display literal `49E2A580`).

```text
channel 0  27785BD2  ArmorPlate
channel 1  5180A26B  ArmorSuit
channel 2  0D07754A  ArmorCloth
```

## Exact D1 resolution chain

The resolved retail chain is:

```text
InventoryItem
  -> +0x60 ResourcePointer -> 20108080 equippingBlock
  -> ChannelIndex / DyeIndex

DyeIndex
  -> 80A5FFA8 ArtDyeReference[]
  -> DyeManifestHash
  -> 80A7E1DC D1 manifest assignment map
  -> one relation FileHash
  -> relation GetReferenceFromManifest() == 63348080
  -> exact 0x18-byte generic relation payload
  -> +0x10 final DyeD1 FileHash
  -> final package-entry Reference == F41A8080 directly
  -> entry payload is SDye_D1
```

A critical format correction is now established: the final `DyeD1` entry does **not** use another `S48018080` manifest wrapper. Its package entry `Reference` is directly numeric `80801AF4`, Charm display/source class `F41A8080`.

## Dye 8752 — ArmorPlate

```text
DyeManifestHash       1C041F9C
relation              80A6A229
relation package      0135
final DyeD1           80A6A22A
final Reference       F41A8080
slot type             0
payload SHA-256       af375be40e526343ec012b8cd0f00f7726125af72b929fd6dbf8f339ebc4e522

decal                 FFFFFFFF
specular              [0.3539215922355652, 90.0, 0.4000000059604645, 0.0]
detail diffuse        80A083DD
detail normal         80A08252
detail transform      [2.5, 2.5, 0.0, 0.0]
normal contribution   [1.0, 1.0, 1.0, 1.0]
primary color         [0.3856532871723175, 0.41583436727523804, 0.5008484125137329, 1.0]
secondary color       [0.10000000149011612, 0.10000000149011612, 0.10000000149011612, 1.0]
subsurface            [32.29999923706055, 1.0, 1.0, 1.0]
detail texture pkg    0104
```

## Dye 8753 — ArmorSuit

```text
DyeManifestHash       AA575EE9
relation              80A7F1B6
relation package      013F
final DyeD1           80A7F1B7
final Reference       F41A8080
slot type             1
payload SHA-256       b9eed986ee54288723be1463b306756d83e8394ccba5cfe32fb69ed2f12d7e49

decal                 FFFFFFFF
specular              [0.21666668355464935, 55.0, 1.0, 0.0]
detail diffuse        80A07D96
detail normal         80A07D98
detail transform      [4.0, 4.0, 0.0, 0.0]
normal contribution   [1.0, 1.0, 1.0, 1.0]
primary color         [0.20132692158222198, 0.2102859765291214, 0.25165867805480957, 1.0]
secondary color       [0.007999999448657036, 0.008355999365448952, 0.009999999776482582, 1.0]
subsurface            [32.29999923706055, 1.0, 1.0, 1.0]
detail texture pkg    0103
```

## Dye 8754 — ArmorCloth

```text
DyeManifestHash       72E1A6C0
relation              80A7F20A
relation package      013F
final DyeD1           80A7F20C
final Reference       F41A8080
slot type             2
payload SHA-256       368b5400626559c01a63ad971116d57c3ccfdfa5552d6e0ff744efeb908ddbcb

decal                 FFFFFFFF
specular              [0.3931373059749603, 100.0, 1.0, -1.0]
detail diffuse        80A083E1
detail normal         80A083DF
detail transform      [2.0, 2.0, 0.0, 0.0]
normal contribution   [0.5, 0.5, 0.5, 0.5]
primary color         [0.0309443399310112, 0.03874299302697182, 0.056698016822338104, 1.0]
secondary color       [0.1012338250875473, 0.10573870688676834, 0.12654227018356323, 1.0]
subsurface            [32.29999923706055, 1.0, 1.0, 1.0]
detail texture pkg    0104
```

All three have decal `FFFFFFFF`, so this default Spektar state has no dye decal texture to recover.

## Guardian render-parent material result

A separate exact census of the already-proven masculine and feminine Spektar render parents found:

```text
models examined                    10
texture-plate parents              10 / 10
external material tag hashes        0
```

Thus the previously planned `render parent -> external material -> shader` path does not exist for these Spektar model parents. For this set, the source-backed appearance path is centered on the exact texture plates plus the inventory-selected D1 dyes. This result must not be generalized to every Guardian asset without a census.

## Validation

Green exact-dye workflow:

```text
.github/workflows/d1-spektr-pandion-dye-resolve.yml
run      34003552682
job      101406581019
artifact d1-spektr-pandion-exact-dyes
ID       9980216842
ZIP SHA  e2ce2d4f8e349b2ca1bee9af3d53abccc0ff4125a1604185041ad4a4e381e818
```

Green external-material census:

```text
.github/workflows/d1-spektr-pandion-material-hash-census.yml
run      34003611996
job      101406738598
result   0 distinct external material hashes
```

## Remaining rendering work

1. Export the six exact detail textures from packages `0103` and `0104`.
2. Preserve the three exact dye records and their detail images in the Guardian GLB/export manifest.
3. Source-close how D1 uses the texture-plate GStack and dye primary/secondary masks before altering the current neutral preview shader.
4. Do not convert the exact dye colors into guessed glTF baseColor factors and do not reinterpret GStack as metallic/roughness without retail shader evidence.
