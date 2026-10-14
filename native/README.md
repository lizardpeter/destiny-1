# d1-native — Destiny 1 running natively on an x86-64 host

Prototype of the standalone path described in `findings/LOG.md` (2026-10-12): the
PS4 CPU is x86-64, so the game's own machine code runs directly on the host. This
program loads the original `eboot.bin` plus the two game-shipped modules
(`sce_module/libc.prx`, `sce_module/libSceFios2.prx`), links them together, and
replaces the PS4 firmware with host code. Decompiled functions from
`reconstruction/` can later replace guest functions one at a time.

No game files are in this repository. You need your own decrypted 01.33 eboot,
`sce_module/` and the `/app0` tree (packages etc.).

## Build and run

d1-native builds for **Windows** (x86-64, Windows 10 2004+ / 11) and **Linux** (x86-64).
Either way everything lives in the executable's folder:

```
d1-native(.exe)   the game runtime        d1-native.cfg   settings (written on first run)
d1-backend(.exe)  the replacement server  d1-native.log   log of the last run, backend.log
game/             the installed game      data/           everything the game writes
```

Put the installed 01.33 game (decrypted `eboot.bin`, `sce_module/`, `packages/`) in `game/`,
or point `game_dir` in `d1-native.cfg` at it, and start `d1-native`. It starts `d1-backend`
from the same folder by itself (`backend = local`). **The game folder is only read**: writes
under `/app0` are refused (EROFS, as on the console) and `data/` must lie outside it.

### Windows (cross-compiled from Linux with llvm-mingw)

```bash
# llvm-mingw: https://github.com/mstorsjo/llvm-mingw (ucrt build); SDL2 mingw devel package
cmake -S native -B build/win -G Ninja -DCMAKE_TOOLCHAIN_FILE=native/cmake/windows-llvm-mingw.cmake \
      -DLLVM_MINGW=/opt/llvm-mingw -DD1_RENDERER_SHADPS4=ON -DSHADPS4_DIR=/path/shadps4 \
      -DCMAKE_PREFIX_PATH=/opt/SDL2-2.32.10/x86_64-w64-mingw32
cmake --build build/win
# backend
CARGO_TARGET_X86_64_PC_WINDOWS_GNULLVM_LINKER=/opt/llvm-mingw/bin/x86_64-w64-mingw32-clang \
RUSTFLAGS="-C target-feature=+crt-static" \
  cargo build --release --target x86_64-pc-windows-gnullvm --manifest-path backend/Cargo.toml
```

Both executables depend only on DLLs that ship with Windows (UCRT, Winsock, ...); SDL2
and the C++ runtime are linked in. Vulkan is loaded at run time from the GPU driver.

How the Windows port works (`src/os_win.cpp`, `src/os.h`):
- **Calling convention**: the game's code is System V (FreeBSD). Every host function it
  calls is registered through a System V entry point (`HLE()`/`D1_SYSV`), and every game
  function the host calls is typed `D1_SYSV`; the compiler converts.
- **Thread-local storage**: `mov r64, fs:[0]` (read the TCB) is rewritten in place to
  `mov r64, gs:[TEB TlsSlots + 8*slot]`, a `TlsAlloc` slot that holds the TCB.
- **Guest memory**: one placeholder reservation for the guest range (VirtualAlloc2 /
  MapViewOfFile3), so mappings land at exact addresses; direct memory is a pagefile-backed
  section mapped as aliasing views.
- **Faults**: a vectored exception handler serves the renderer's write tracking and crash
  reports. `scePthreadExit` returns to the thread's start without unwinding game frames.

### Linux

```bash
cmake -S native -B build/native && cmake --build build/native -j     # null GPU
cargo build --release --manifest-path backend/Cargo.toml
cp backend/target/release/d1-backend build/native/
build/native/d1-native            # or: --game /path/to/CUSA00219 --data ./data
```

### Settings

On first run d1-native writes `<data>/d1-native.cfg` (or the file given with `--config`)
with commented defaults. Environment variables override it:

| setting | env | values |
|---|---|---|
| `window_width`, `window_height` | `D1_WINDOW_SIZE=1920x1080` | window size in pixels (default 1280x720); the picture is scaled to fit, letterboxed |
| `fullscreen` | `D1_FULLSCREEN=1` | borderless fullscreen; F11 or Alt+Enter toggles while running |
| `overlay` | `D1_OVERLAY=1` | stats overlay (FPS, frame time, where a frame's time goes, render and window resolution, v-sync, GPU, game state); F3 toggles it while running. The same breakdown is logged every 10 s as a `perf:` line |
| `render_resolution` | `D1_RENDER_RESOLUTION=2560x1440` | the game's own internal resolution (1920x1080 on the console); every render target is created at this size, no upscaling |
| `vsync` | `D1_VSYNC` | `off-tearing` (default: Immediate, lowest latency, may tear), `off` (Mailbox: newest frame at the next refresh, no tearing), `on` (Fifo) |
| `fps` | `D1_FPS` | frame-rate limit: 0 / `unlimited` (default) runs one game tick per rendered frame with no limiter; a number caps it (30 = the console's rate) |
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
| `D1_GPU_LOG=t\|d\|i\|w\|e` | (renderer build) renderer log level; each repeated warning prints 20 times, then once per 10,000 |
| `D1_PIPELINE_CACHE=0` | (renderer build) don't keep compiled shaders and pipelines in `<data>/shader_cache` between runs |
| `D1_RENDER_EVERY=N` | (renderer build) draw only every Nth frame; the frames between go through the null GPU, so the game keeps its normal speed and network timing on a slow GPU or software rendering (debugging: in-world screenshots on lavapipe) |
| `D1_RENDER_ASYNC=1` | (renderer build) draw a frame only when the renderer is idle, otherwise pass it through the null GPU without waiting |
| `D1_RENDERER_LATE=<s>` | (renderer build) null GPU until `<s>` seconds into `activity:in_world`, then start the renderer |
| `D1_GPU_LOG_ALL=1` | (renderer build) don't throttle repeated renderer warnings |
| `D1_GPU_MEMORY_MB=<n>` | (renderer build) texture cache memory budget; integrated GPUs now default to the driver budget minus a quarter (at most 4 GB) instead of leaving 8 GB to the system |
| `D1_PROFILE_GPU=<file>` | (Linux renderer build) sample the GPU thread's call stacks every 1 ms of its CPU time into `<file>` |
| `D1_TRACE_IMAGE=<hex>` / `D1_TRACE_STALE=1` | (renderer build) log texture cache lookups covering an address / new images created over GPU-written data |
| `D1_NO_RT_ARRAY_MAX=1` | (renderer build) turn off patch 0011's full-size binding of render-target arrays drawn one slice at a time |
| `D1_NO_ARRAY_TO_VOLUME=1` / `D1_NO_VOLUME_SLICES=1` / `D1_NO_OVERLAP_GROW=1` | (renderer build) turn off the texture cache fixes for the colour-grading LUT (patches 0009 / 0004 / 0007) |
| `D1_INLINE_FETCH=1` | (renderer build) translate vertex fetch shaders inline as buffer loads (shadPS4's slower debugging path) |
| `D1_GPU_ID=<n>` | (renderer build) use the n-th Vulkan device instead of the automatic pick |

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
D1_NATIVE_BIN=build/native-r/d1-native native/run.sh /path/to/CUSA00219
```

Needs clang (C++23), the Vulkan loader and headers, glslangValidator, abseil,
libpng and SDL2. With a display (X11 or Wayland) the game opens in a resizable
window; without one (or with `D1_WINDOW=0`) it renders offscreen, and
`D1_FRAMES` saves frames either way.

Keyboard and mouse play natively: clicking in the window captures the mouse (F2 or
switching away releases it), and mouse motion goes straight into the game's aim as raw
counts, without stick emulation (see "Mouse look" below).

| input | action (PS4 button) |
|---|---|
| WASD | move (left stick) |
| mouse | look (raw, see below) |
| left / right mouse | fire (R2) / aim (L2) |
| Space, Enter | jump, confirm (Cross) |
| Left Ctrl, C | crouch (Circle) |
| Esc, Backspace | back (Circle) |
| R, E | reload, interact (Square) |
| 1, 2, 3, mouse wheel | switch weapon (Triangle) |
| Q / F / X | grenade (L1) / melee (R1) / super (L1+R1) |
| mouse 4 / mouse 5 | grenade (L1) / melee (R1) |
| Left Shift | sprint (L3) |
| Z, middle mouse | R3 |
| arrows | D-pad |
| IJKL | right stick (menus) |
| Tab / G | character menu (Options) / ghost (touch pad) |

### Mouse look

The game has no mouse support; its look runs pad -> input abstraction (dead zones,
0x926910) -> player control (response curves, turn-speed acceleration, aim assist, zoom
scaling, 0x91B500), which ends with this frame's yaw and pitch deltas in radians.
d1-native hooks the end of that function and adds the mouse counts there, so the mouse
skips every stick stage (no quantization, curve, acceleration, dead zone or aim assist).
Counts come from SDL's relative mode on raw input with no OS pointer acceleration, and
reach the game at most about 1 ms after the window sees them. A controller keeps working
alongside. Settings in `d1-native.cfg`:

| setting | default | meaning |
|---|---|---|
| `mouse_sensitivity` | 2.0 | Source-engine scale: 1.0 = 0.022 degrees per count (Destiny 2 PC sensitivity x 0.3) |
| `mouse_invert` | false | inverted vertical look |
| `mouse_zoom_scale` | 1.0 | 1 = the game's own aim-down-sights slowdown, 0 = none |

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
