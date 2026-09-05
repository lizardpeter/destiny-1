#!/usr/bin/env python3
"""Build a provenance-rich Destiny 1 Rise-of-Iron schema label registry.

This is enrichment, not ownership evidence.  It parses a pinned external source tree
(e.g. MontagueM/Charm) for explicit DESTINY1_RISE_OF_IRON SchemaStruct annotations,
converts the source's byte-order hash notation into the canonical u32 form used by our
Tiger entry census, and records the declaring struct/file/declared size.

No external schema label is promoted to `BINARY_VALIDATED` by this tool.  Consumers
must keep `evidence_status=SOURCE_DERIVED` separate from package-byte conclusions.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

ANN = re.compile(
    r'\[SchemaStruct\(TigerStrategy\.DESTINY1_RISE_OF_IRON,\s*"([0-9A-Fa-f]{8})"\s*,\s*([^\)]+)\)\]'
)
DECL = re.compile(r'public\s+(?:readonly\s+)?(?:partial\s+)?(struct|class)\s+([A-Za-z_][A-Za-z0-9_]*)')


def canonical_hash(source_hex: str) -> str:
    bs = [source_hex[i:i+2] for i in range(0, 8, 2)]
    return ''.join(reversed(bs)).upper()


def parse_size(expr: str):
    s = expr.strip()
    # Keep any nonliteral expression losslessly, but normalize literal decimal/hex.
    try:
        return {"value": int(s, 0), "expression": s}
    except Exception:
        return {"value": None, "expression": s}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--source-root', type=Path, required=True)
    ap.add_argument('--source-name', default='external')
    ap.add_argument('--source-revision', required=True)
    ap.add_argument('--source-url', default='')
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()

    root = args.source_root.resolve()
    rows = []
    for p in sorted(root.rglob('*.cs')):
        try:
            text = p.read_text(encoding='utf-8-sig', errors='replace')
        except Exception:
            continue
        matches = list(ANN.finditer(text))
        for m in matches:
            tail = text[m.end():m.end()+2000]
            dm = DECL.search(tail)
            if not dm:
                decl_kind = None; decl_name = None
            else:
                decl_kind, decl_name = dm.group(1), dm.group(2)
            src_hash = m.group(1).upper()
            rows.append({
                'canonical_hash': canonical_hash(src_hash),
                'source_hash_notation': src_hash,
                'declared_size': parse_size(m.group(2)),
                'declaration_kind': decl_kind,
                'declaration_name': decl_name,
                'source_file': str(p.relative_to(root)).replace('\\','/'),
                'source_line': text.count('\n', 0, m.start()) + 1,
                'evidence_status': 'SOURCE_DERIVED',
            })

    by_hash = defaultdict(list)
    for r in rows:
        by_hash[r['canonical_hash']].append(r)
    conflicts = {}
    for h, vals in by_hash.items():
        sigs={(v['declaration_name'],v['declared_size']['value'],v['source_file']) for v in vals}
        if len(sigs)>1:
            conflicts[h]=vals

    out = {
        'evidence_status': 'SOURCE_DERIVED',
        'source': {
            'name': args.source_name,
            'revision': args.source_revision,
            'url': args.source_url,
        },
        'policy': 'Schema names/sizes are external source-derived enrichment only. They do not establish Tiger ownership, placement, material binding, animation ownership, or runtime identity.',
        'summary': {
            'annotation_occurrences': len(rows),
            'unique_canonical_hashes': len(by_hash),
            'hashes_with_multiple_declarations': len(conflicts),
        },
        'registry': {h: vals for h, vals in sorted(by_hash.items())},
        'conflicts': conflicts,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps(out['summary'], indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
