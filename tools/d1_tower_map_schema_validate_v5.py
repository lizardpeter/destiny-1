#!/usr/bin/env python3
"""D1 Tower map schema validator v5: sized Tiger blocks + v3 class safety.

This is the first Tower validator to use the serialized-coverage block sizing rule:
compressed D1 Tiger logical blocks are decoded with

    min(0x40000, align_up(highest serialized FileEntry byte used in block, 0x4000))

rather than assuming every Oodle block expands to exactly 0x40000 bytes.

All v3 safety remains in force:
- newest occurrence defines current FileEntry.Reference/class identity;
- payload fallback may use an older physical occurrence only when its Reference
  exactly matches that newest class;
- historical class-crossing fallback is forbidden;
- v2's explicit FFFFFFFF Vertices1 null-stream rule remains active.
"""
from __future__ import annotations
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from d1_entry_extract_sized import SizedEntryReader
import d1_tower_map_schema_validate_v3 as v3

# Corpus.__init__ resolves EntryReader from the base module global at runtime.
v3.base.EntryReader = SizedEntryReader

if __name__ == '__main__':
    raise SystemExit(v3.base.main())
