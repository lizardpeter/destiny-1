# Destiny 1 source reconstruction

Skeleton of the original Bungie source tree for the PS4 retail executable
(CUSA00219 01.33, `eboot.bin` SHA-256 `672f0341…0833`), to be filled in as code is
reversed. The layout mirrors the build paths recovered from the binary:

```
d:\bungie\evil\shared\engine\source\        -> evil/shared/engine/source/
    engine\    Tiger engine core
    omaha\     game framework layer (main, game, networking, …)
    spasaha\   Destiny-specific game layer (Jam target root)
d:\bungie\external_libraries\               -> external_libraries/  (identified, not reconstructed)
```

Build output path in the binary:
`d:/bungie/evil/objects/jam_orbis_release/engine_source_spasaha_spasaha/bin/tiger_release_final.elf`,
build stamp `56578.17.04.12.1251.evil`.

## What each folder holds

| item | meaning |
|---|---|
| `README.md` | Generated block (between the `GENERATED` markers) plus hand-written notes below it. |
| `*.cpp` placeholders | Created only for source paths that appear verbatim in the binary. Start as a 3-line header with status `NOT STARTED`. |
| `decompiled/` | Unedited decompiler output for functions in this subsystem. Reference only — reconstructed code goes in real `.cpp/.h` files. |

Every folder README states its **folder path evidence**:

- `CONFIRMED_BINARY` — the directory appears in a verbatim source path string.
- `HYPOTHESIS` — the folder is a proposal from clustering RTTI class names and
  hierarchical log channels (`networking:*`, `world_controller:*`, …). Rename it
  freely when a real path turns up.

Class rows (typeinfo, vtable, virtual-slot count, bases) are `CONFIRMED_BINARY`
from Itanium RTTI. Which folder a first-party class sits in is `HYPOTHESIS`
unless its README notes otherwise. Evidence levels follow the repository rules
in the top-level `README.md`.

## Regenerating

```bash
python tools/eboot/d1_reconstruction_tree.py /path/to/eboot.bin
```

The script checks the eboot hash, applies the SCE relocations, recovers RTTI and
source-path strings, reads `reconstruction/functions.json`, and rewrites only the
generated block of each README plus `manifest.json`. Placeholders that already
exist and anything outside the generated markers are left alone.

To record a newly reversed function, add an entry to `functions.json`
(`va`, `name`, `subsystem`, `class`, `evidence`, `file`, `role`), drop its
pseudo-C into the subsystem's `decompiled/` folder if useful, and regenerate.

## Graph

The same structure is in the `uregraph` knowledge graph under the D1 build
`cusa00219-01.33`: `Subsystem` nodes (`urn:ure:d1:re_Subsystem:eboot-01.33:<key>`),
`SourceFile`, `SourceClass` (`urn:ure:d1:re_SourceClass:eboot-01.33:<typeinfo hex>`,
with `INHERITS_FROM` edges) and `FunctionOccurrence` nodes. Subsystem keys in
`manifest.json` match the graph keys.

## Coverage today

- 9 Bungie source files named in the binary (all placeholders, nothing reconstructed yet).
- ~2,350 RTTI classes placed across 37 folders; the renderer is mostly invisible
  to RTTI, so `engine/graphics` is thin until functions are traced.
- 242 decompiled functions:
  - 33 from the graphics work: the TFX VM and extern ABI, the Frame extern, auto-exposure, the
    Engine Configuration snapshot, the global channel store, and `c_sun_manager`.
  - 81 from the online work (2026-10-13), spread across `omaha/networking/bap`,
    `omaha/networking`, `omaha/world_controller`, `omaha/simulation`, `omaha/game`,
    `engine/core`, `engine/resourcerer` and `spasaha/investment`:
    - the BAP transport and message routing
    - the activity client's handling of every activity-host message the backend emulates
      (join, entity indices, membership, instance state, keep-alive)
    - engine-type bitstream decode
    - activity manager timeouts, the world transition, slice-set loading and its task graph
    - the simulation queue and player/unit assignment
    - the unlock-expression VM
  - 104 backfilled from the earlier native-runtime and backend sessions (2026-10-12/13):
    - BAP channel crypto and handshake, response matching, and the message codecs
    - investment world-server bitstreams, queuez replication and the object manager
    - account slot, unlock-flag sources, the trial check
    - sign-on and content manifest, package registration
    - bootflow state handlers, world-controller states and modes, prerequisites
  - 24 from the input path (2026-10-13), in `omaha/platform`, `omaha/game` and `omaha/camera`:
    the pad poll and engine gamepad state, the input abstraction game system (dead zones,
    per-player state, look rate) and the player control game system down to the per-frame
    yaw/pitch deltas, plus weapon zoom scaling and camera impulses
    - main loop timing, job system, logging, the engine heap
    - NP toolkit and DemonWare entry points
- The online protocol (every BAP message class, activity-host message types and handlers,
  payload types, replication families, unlock flags, the prologue scenario, rejected
  hypotheses and open questions) is in
  `knowledge/records/d1_online_protocol_2026-10-13.json`.
- Class attachment: `c_sun_manager` methods and two `c_activity_client_messaging_interface_bap`
  slots are attached so far. The other
  decompiled functions do not appear in any RTTI vtable, so they are free
  functions or non-virtual methods whose class is not yet known.
- Global channel names (FNV-1 32 preimages) are in
  `evidence/generated/d1_global_channel_names.json`.
