#!/usr/bin/env bash
set -euo pipefail

# Canonical Blender baseline for all Blender-backed Destiny tooling and CI.
# Override only for deliberate compatibility testing.
BLENDER_VERSION="${BLENDER_VERSION:-5.2.1}"
BLENDER_SERIES="${BLENDER_SERIES:-5.2}"
DEST="${1:-.blender}"
ARCHIVE="blender-${BLENDER_VERSION}-linux-x64.tar.xz"
BASE="https://download.blender.org/release/Blender${BLENDER_SERIES}"
SUMFILE="blender-${BLENDER_VERSION}.sha256"

mkdir -p "$DEST"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

curl --fail --location --retry 3 --silent --show-error \
  "$BASE/$SUMFILE" -o "$TMP/$SUMFILE"
curl --fail --location --retry 3 --silent --show-error \
  "$BASE/$ARCHIVE" -o "$TMP/$ARCHIVE"

grep "$ARCHIVE" "$TMP/$SUMFILE" > "$TMP/archive.sha256"
sed -i "s#$ARCHIVE#$TMP/$ARCHIVE#" "$TMP/archive.sha256"
sha256sum --check --strict "$TMP/archive.sha256" >&2

tar -xf "$TMP/$ARCHIVE" -C "$DEST"
BLENDER="$DEST/blender-${BLENDER_VERSION}-linux-x64/blender"
test -x "$BLENDER"
"$BLENDER" --version >&2
"$BLENDER" --version | grep -q "Blender ${BLENDER_VERSION}"

python3 - "$BLENDER" <<'PY'
import os, sys
print(os.path.abspath(sys.argv[1]))
PY
