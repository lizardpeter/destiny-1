# d1-native — Destiny 1 running natively on an x86-64 host

Prototype of the standalone path described in `findings/LOG.md` (2026-10-12): the
PS4 CPU is x86-64, so the game's own machine code runs directly on the host. This
program loads the original `eboot.bin` plus the two game-shipped modules
(`sce_module/libc.prx`, `sce_module/libSceFios2.prx`), links them together, and
replaces the PS4 firmware with host code. Decompiled functions from
`reconstruction/` can later replace guest functions one at a time.

No game files are in this repository. You need your own decrypted 01.33 eboot,
`sce_module/` and the `/app0` tree (packages etc.).

## Build and run (Linux x86-64)

```bash
cmake -S native -B build/native && cmake --build build/native -j
build/native/d1-native --eboot /path/eboot.bin --sce-module /path/sce_module \
    --app0 /path/app0 --data ./d1-data
```

| env | effect |
|---|---|
| `D1_TRACE=1` | log every firmware call with its first three arguments |
| `D1_GAME_LOG=1` or `=<substring>` | re-enable the engine's own logging (stripped thresholds in release) and print it |
| `D1_AUTOPRESS=<s>` | tap Cross for 100 ms every `<s>` seconds (no host input yet) |
| `D1_WATCHDOG=<s>` | after `<s>` seconds dump every guest thread's call stack, call counts and GPU stats, then exit |
| `D1_ABORT_ON_UNIMPL=1` | stop at the first call to an unimplemented firmware function |

## How it works

| piece | file | notes |
|---|---|---|
| ELF-SCE loader | `src/loader.cpp` | maps modules at fixed bases (eboot `0x800000000`, prx `0x900000000+`) |
| linker | `src/runtime.cpp` | resolves imports to game-module exports, host functions (by NID), or logging stubs that return 0; applies RELATIVE / 64 / GLOB_DAT / JUMP_SLOT / DTPMOD64 relocations |
| TLS | `src/runtime.cpp` | PS4 code reads its TCB with `mov r64, fs:[0]` (2,542 sites); the loader rewrites the prefix to GS and each guest thread gets its own TCB with the static TLS block below it |
| guest frames | `src/runtime.cpp` | guest code walks frame-pointer chains (allocation call-stack capture); calls into the guest start from a terminal frame |
| kernel | `src/hle_kernel.cpp`, `src/hle_pthread.cpp` | memory (direct memory is a sparse memfd so aliases share pages), time, files (`/app0` → `--app0`), modules, threads, mutex/cond/rwlock, semaphores, event flags |
| null GPU | `src/hle_gpu.cpp` | event queues, video out (flip status/events, vblank), Gnm submit; walks PM4 command buffers performing only their memory effects (EOP/EOS fences, WRITE_DATA, DMA_DATA) and raises the EOP interrupt. Nothing is drawn yet. |
| audio | `src/hle_audio.cpp` | paced silent audio out; AJM codec jobs complete with silence |
| input / services / net | `src/hle_input.cpp`, `src/hle_services.cpp`, `src/hle_net.cpp` | one connected pad, user/system services, libSceLibcInternal subset, network reported as unavailable |
| game hooks | `src/hooks.cpp` | eboot-specific patches (01.33 offsets only) |

The x86-64 host CPU must support AVX, BMI1, MOVBE and LZCNT (Haswell / Zen or
newer); see `evidence/generated/d1_x86_portability.json`.

## Status

See the 2026-10-12 entries in `findings/LOG.md`. The game boots through its full
start-up, runs its frame loop headless at about 30 fps, reaches the title screen,
accepts Cross, and stops at `bootflow:platform_signin` because there is no network.

Licence note: this directory contains only new code. Porting shadPS4's renderer or
other parts later would make the combined program GPL-2.0-or-later.
