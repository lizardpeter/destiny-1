#!/usr/bin/env python3
"""D1 Tower map schema validator v3: class-stable patch-generation fallback.

This layers two narrow corrections over the original validator:
1. v2's retail Vertices1 == FFFFFFFF null-secondary-stream rule.
2. Payload fallback may move to an older physical occurrence only when that
   occurrence has the SAME FileEntry.Reference/class as the newest occurrence.

Why this is required:
TagHashes can be repurposed across package generations. Tower hash 80C98258 is a
real retail example:
  _0       -> 80801AF2, 496 bytes
  _1/_2    -> 80801A90, 19,912 bytes
  _3/_4/_5 -> 80801B75, 48,084 bytes
The current _3/_4/_5 payload presently hits an Oodle extraction failure. The old
Corpus.payload() then silently fell back to _2 and parsed an 80801A90 static-table
payload as if it were current 80801B75 D1 static-map data. The resulting apparent
'alternate layout' was therefore invalid evidence.

Safety boundary:
- The newest occurrence still defines the current class identity.
- Older bytes may be used only if their reference hash equals that newest class.
- If every current-class occurrence is unavailable/undecodable, payload() returns
  unavailable rather than crossing a class boundary.
- Raw TagHash ownership/class checks remain unchanged.
- v2 V1-null semantics remain unchanged.
"""
from __future__ import annotations
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import d1_tower_map_schema_validate as base
# Importing v2 applies its narrow parse_static_table patch to `base`.
import d1_tower_map_schema_validate_v2  # noqa: F401


def payload_class_stable(self: base.Corpus, h: str):
    key = h.upper()
    occurrences = self.occ.get(key, [])
    if not occurrences:
        return None, None

    newest_reference = occurrences[0][3]['reference'].upper()
    attempted = []
    for g, p, r, e in occurrences:
        reference = e['reference'].upper()
        if reference != newest_reference:
            continue
        if not r.available(e['index']):
            attempted.append({
                'snapshot': p.name,
                'reference': reference,
                'available': False,
            })
            continue
        try:
            b = r.entry(e['index'])
            return b, {
                'snapshot': p.name,
                'package_id': f"{int(r.h['pkg_id']):04X}",
                'entry_index': int(e['index']),
                'reference': reference,
                'size': int(e['file_size']),
                'fallback_policy': 'CLASS_STABLE_NEWEST_REFERENCE_ONLY',
                'newest_reference': newest_reference,
            }
        except Exception as ex:
            attempted.append({
                'snapshot': p.name,
                'reference': reference,
                'available': True,
                'error': repr(ex),
            })

    # Do not cross into historical occurrences of another class merely because
    # their payload happens to decode.
    return None, {
        'hash': key,
        'payload_unavailable': True,
        'fallback_policy': 'CLASS_STABLE_NEWEST_REFERENCE_ONLY',
        'newest_reference': newest_reference,
        'attempted_current_class_occurrences': attempted,
        'historical_other_class_occurrence_count': sum(
            1 for _, _, _, e in occurrences if e['reference'].upper() != newest_reference
        ),
    }


base.Corpus.payload = payload_class_stable

if __name__ == '__main__':
    raise SystemExit(base.main())
