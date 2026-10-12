#!/usr/bin/env bash
# Starts the replacement backend and d1-native together.
#
#   native/run.sh <game dir> [data dir]
#
# <game dir> is the installed game (CUSA00219, 01.33): eboot.bin (decrypted), sce_module/,
# packages/. It is only ever read. Everything the game writes (saves, settings, caches,
# crash reports, d1-native.cfg) goes to [data dir], default ~/.local/share/d1-native.
#
# Builds are looked for in build/native and backend/target/release (see native/README.md);
# override with D1_NATIVE_BIN / D1_BACKEND_BIN. Extra env (D1_FPS, D1_VSYNC, ...) passes through.
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
game="${1:?usage: native/run.sh <game dir> [data dir]}"
data="${2:-${XDG_DATA_HOME:-$HOME/.local/share}/d1-native}"
game="$(cd "$game" && pwd)"
mkdir -p "$data"

native="${D1_NATIVE_BIN:-$root/build/native/d1-native}"
backend="${D1_BACKEND_BIN:-$root/backend/target/release/d1-backend}"
for b in "$native" "$backend"; do
    [[ -x "$b" ]] || { echo "missing $b — build it first (native/README.md)" >&2; exit 1; }
done
[[ -f "$game/eboot.bin" ]] || { echo "$game/eboot.bin not found" >&2; exit 1; }

"$backend" --packages-dir "$game/packages" >"$data/backend.log" 2>&1 &
backend_pid=$!
trap 'kill $backend_pid 2>/dev/null || true' EXIT
sleep 0.5

D1_BACKEND="${D1_BACKEND:-127.0.0.1}" D1_BYPASS="${D1_BYPASS:-prereq,transport}" \
    "$native" --app0 "$game" --data "$data" 2>&1 | tee "$data/d1-native.log"
