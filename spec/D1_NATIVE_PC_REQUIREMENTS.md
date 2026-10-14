# d1-native: PC requirements (owner direction, 2026-10-14)

These are standing requirements for the native Windows build. The current priority is
**the native renderer**. Everything else on this list must be kept working (or built
toward) while that happens.

## Rendering

- **Native Vulkan renderer.** Replace the embedded shadPS4 renderer by implementing the
  engine's own GPU device layer directly in Vulkan
  (see `notes/D1_NATIVE_RENDERER_DEVICE_LAYER_2026-10-14.md`). shadPS4 code may be studied
  and reused (for example its GCN → SPIR-V shader translator). It stays the fallback until
  the native path covers everything.
- **Keep the render resolution option** (`render_resolution` / `D1_RENDER_RESOLUTION`) and
  the window, fullscreen and v-sync options.

## Field of view

- **FOV slider up to at least 120**, matching Modern Warfare (2019), not stopping at
  Destiny 2's ~105.
  - Assumption to verify: MW2019's value is horizontal FOV measured at 16:9. Confirm this
    before implementing, and keep the same convention so the numbers mean the same thing.
- **Groundwork for aim-down-sights FOV scaling**, similar to MW2019's "affected" vs
  "independent" ADS FOV, so aiming doesn't zoom in as much.
  - Lay the groundwork only: find where the game derives the zoomed FOV.
  - Keep the game's native ADS values until we can test in-game.

## Mouse input

- **Sensitivity on the Destiny 2 PC scale.** It's the same scale as MW2019 and
  Overwatch: 1.0 = 0.0066° per mouse count.
- **Default sensitivity 1.5.** At 3200 DPI that is
  360 / (0.0066 × 1.5 × 3200) = 11.36 in = **28.9 cm per 360°**, matching the owner's
  Destiny 2 / MW2019 setup (~29 cm).
  - Implemented: the `sensitivity` key, default 1.5, env `D1_SENSITIVITY`.
  - Older configs' `mouse_sensitivity` used the Source scale (0.022°) and is converted
    automatically.
- **Ultra-low latency; full control of the input chain.**
  - Raw mouse counts go straight into the aim angles (already the case: the player-control
    hook adds yaw/pitch).
  - No translation to stick movement, PS4 pad mappings or any game-side input
    smoothing/acceleration.
  - Keyboard and mouse buttons should drive actions directly rather than through emulated
    pad buttons, wherever the game allows.
  - Minimise the time from input poll to the frame's camera.

## Frame rate

- **Untie frame rate from simulation.** Game speed, physics and animation must not depend
  on fps, so the frame rate can be unlimited while the game still runs correctly.
- Today the game appears to advance a capped step per frame: at ~11 fps it runs in slow
  motion.
- To do after the native renderer.
