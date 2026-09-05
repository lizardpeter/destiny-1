#!/usr/bin/env python3
"""D1 Tower map validator v4: v3 class safety + verified Oodle history fallback.

Adds only one behavior to v3: Corpus readers use HistoryEntryReader, which retries a
compressed Tiger block with the immediately preceding logical block as Oodle history
only after normal independent decoding fails. TagHash occurrence selection remains
v3's class-stable newest-reference-only policy.
"""
from __future__ import annotations
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from d1_entry_extract_history import HistoryEntryReader
import d1_tower_map_schema_validate_v3 as v3

# Corpus.__init__ resolves EntryReader from the base module globals at runtime.
v3.base.EntryReader = HistoryEntryReader

if __name__ == '__main__':
    raise SystemExit(v3.base.main())
