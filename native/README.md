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

### Settings

On first run d1-native writes `<data>/d1-native.cfg` (or the file given with `--config`)
with commented defaults. Environment variables override it:

| setting | env | values |
|---|---|---|
| `window_width`, `window_height` | `D1_WINDOW_SIZE=1920x1080` | window size in pixels (default 1280x720); the picture is scaled to fit, letterboxed |
| `fullscreen` | `D1_FULLSCREEN=1` | borderless fullscreen; F11 or Alt+Enter toggles while running |
| `vsync` | `D1_VSYNC` | `off` (default: Mailbox, newest frame, no tearing), `on` (Fifo), `off-tearing` (Immediate, lowest latency) |
| `fps` | `D1_FPS` | frame-rate target for the game's own limiter; 0 keeps its 30 fps |
| `discord`, `discord_app_id` | `D1_DISCORD=0`, `D1_DISCORD_APP_ID` | Discord Rich Presence over Discord's local IPC socket; needs the Discord desktop app and an application id |

The game draws its render targets at 1080p whatever display resolution it is told about, so
the window size is the output resolution; changing the internal resolution needs an
engine-side patch (not done yet).

### Environment

| env | effect |
|---|---|
| `D1_TRACE=1` | log every firmware call with its first three arguments |
| `D1_GAME_LOG=1` or `=<substring>` | re-enable the engine's own logging (stripped thresholds in release) and print it |
| `D1_AUTOPRESS=<s>` | tap Cross for 100 ms every `<s>` seconds (no host input yet) |
| `D1_WATCHDOG=<s>` | after `<s>` seconds dump every guest thread's call stack, call counts and GPU stats, then exit |
| `D1_ABORT_ON_UNIMPL=1` | stop at the first call to an unimplemented firmware function |
| `D1_BYPASS=prereq,transport` | research hooks: report failed bootflow prerequisites as satisfied; report the DemonWare transport as started |
| `D1_NET=link` | report a connected interface, give the game real host sockets and a signed-in PSN user; DNS is refused |
| `D1_BACKEND=<host>` | replacement backend server (implies `D1_NET=link`): Bungie, DemonWare and PSN hostnames resolve to it, all others are refused; HTTP(S) requests to those services go to it as plain HTTP on `D1_BACKEND_HTTP_PORT` (default 8080) with the original `Host` header |
| `D1_FRAMES=<dir>` | (renderer build) save displayed frames as PNG; `D1_FRAME_EVERY=<n>` sets the interval (default 60) |
| `D1_RENDERER=0` | (renderer build) use the null GPU anyway |
| `D1_WINDOW=0` | (renderer build) no window: offscreen rendering only |
| `D1_PRESENT=Mailbox\|Immediate\|Fifo` | (renderer build) raw swapchain present mode, overrides `vsync` |
| `D1_PEEK=off,*off` / `D1_POKE=secs:off+delta=value;…` | research aids: dump / write eboot-relative memory (`*` dereferences a pointer) |
| `D1_GPU_LOG=t\|d\|i\|w\|e` | (renderer build) renderer log level |

## How it works

| piece | file | notes |
|---|---|---|
| ELF-SCE loader | `src/loader.cpp` | maps modules at fixed bases (eboot `0x800000000`, prx `0x900000000+`) |
| linker | `src/runtime.cpp` | resolves imports to game-module exports, host functions (by NID), or logging stubs that return 0; applies RELATIVE / 64 / GLOB_DAT / JUMP_SLOT / DTPMOD64 relocations |
| TLS | `src/runtime.cpp` | PS4 code reads its TCB with `mov r64, fs:[0]` (2,542 sites); the loader rewrites the prefix to GS and each guest thread gets its own TCB with the static TLS block below it |
| guest frames | `src/runtime.cpp` | guest code walks frame-pointer chains (allocation call-stack capture); calls into the guest start from a terminal frame |
| kernel | `src/hle_kernel.cpp`, `src/hle_pthread.cpp` | memory (direct memory is a sparse memfd so aliases share pages), time, files (`/app0` → `--app0`), modules, threads, mutex/cond/rwlock, semaphores, event flags |
| GPU | `src/hle_gpu.cpp` | event queues, video out (flip status/events, vblank), Gnm submit. Without the renderer a null GPU walks PM4 command buffers performing only their memory effects (EOP/EOS fences, WRITE_DATA, DMA_DATA) and raises the EOP interrupt. |
| renderer (optional, temporary) | `renderer/`, `src/render_bridge.h` | shadPS4's command processor, shader recompiler and Vulkan rasterizer, headless; see below |
| audio | `src/hle_audio.cpp` | paced silent audio out; AJM codec jobs complete with silence |
| input / services / net | `src/hle_input.cpp`, `src/hle_services.cpp`, `src/hle_net.cpp` | one connected pad, user/system services, libSceLibcInternal subset, network reported as unavailable |
| game hooks | `src/hooks.cpp` | eboot-specific patches (01.33 offsets only) |

## Temporary renderer

The default build draws nothing. To render, build with shadPS4's video core
(an interim step; the long-term plan is a Rust/Vulkan renderer):

```bash
git clone --recursive https://github.com/shadps4-emu/shadPS4 /path/shadps4   # tested at e0a46675
CC=clang CXX=clang++ cmake -S native -B build/native-r -G Ninja \
    -DD1_RENDERER_SHADPS4=ON -DSHADPS4_DIR=/path/shadps4
cmake --build build/native-r
D1_FRAMES=./frames build/native-r/d1-native --eboot ... --app0 ... --data ...
```

Needs clang (C++23), the Vulkan loader and headers, glslangValidator, abseil,
libpng and SDL2. With a display (X11 or Wayland) the game opens in a resizable
window; without one (or with `D1_WINDOW=0`) it renders offscreen, and
`D1_FRAMES` saves frames either way.

| input | PS4 button |
|---|---|
| Enter / Space | Cross |
| Esc / Backspace | Circle |
| R / F | Square / Triangle |
| Q / E, Z / X | L1 / R1, L2 / R2 |
| Left Shift / C | L3 / R3 |
| arrows | D-pad |
| WASD / IJKL | left / right stick |
| Tab / T | Options / touch pad |

Game controllers work through SDL's controller mapping (hot-plug supported). Any Vulkan 1.3 device works, including lavapipe. shadPS4 is
GPL-2.0-or-later, so a binary built this way is too.

The x86-64 host CPU must support AVX, BMI1, MOVBE and LZCNT (Haswell / Zen or
newer); see `evidence/generated/d1_x86_portability.json`.

## Status

See the 2026-10-12 entries in `findings/LOG.md`. The game boots through its full
start-up, runs its frame loop headless at about 30 fps, reaches the title screen,
accepts Cross, and stops at `bootflow:platform_signin`: with no network on
`error.no_ethernet_link`, with `D1_NET=link` on `error.transport_method_invalid`
(DemonWare cannot reach Bungie's STUN servers).

With the renderer the game draws the Bungie logo, the animated title and its
dialogs (see the renderer entry in `findings/LOG.md`).

Licence note: `src/` contains only new code. `renderer/` builds shadPS4 sources
from an external checkout and its glue follows shadPS4's Gnm driver, so binaries
built with `D1_RENDERER_SHADPS4=ON` are GPL-2.0-or-later.
