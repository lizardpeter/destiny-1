#!/usr/bin/env python3
"""Compatibility entrypoint for the exact D1 dye resolver with canonical channel names.

The underlying byte decoder is unchanged.  This wrapper replaces only the
human-readable channel-name dictionary before invoking it.  Numeric channel
indices/hashes, dye indices, manifests, relations, FileHashes and SDye_D1
payloads remain exactly the same.
"""
from __future__ import annotations

import d1_investment_dye_resolver as base
import d1_investment_dye_exact_resolver as exact
from d1_dye_channel_semantics import D1_DYE_CHANNEL_NAMES

# exact.KNOWN_CHANNELS is imported from base and references the same dictionary.
base.KNOWN_CHANNELS.clear()
base.KNOWN_CHANNELS.update(D1_DYE_CHANNEL_NAMES)
assert exact.KNOWN_CHANNELS is base.KNOWN_CHANNELS

if __name__ == "__main__":
    raise SystemExit(exact.main())
