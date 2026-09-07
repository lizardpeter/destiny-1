#!/usr/bin/env python3
"""Current Tower dynamic target: class-correct scenarios + R8-aware textures.

Composes the two independently bounded adapters:
- d1_fresh_activity_asset_target_v2 patches only portable texture export to add the
  source-proven GCN Format8/R8_UNORM case;
- d1_fresh_tower_activity_asset_target_v2 patches only Tower seed discovery so the
  current 80800616 scenario roots, never the 8080052E map root, feed the generic
  scenario graph.
"""
from __future__ import annotations

import d1_fresh_activity_asset_target_v2 as current
# Importing this module installs the Tower scenario seed adapter into the same
# underlying d1_fresh_activity_asset_target module used by current.main().
import d1_fresh_tower_activity_asset_target_v2  # noqa: F401

if __name__ == '__main__':
    raise SystemExit(current.main())
