#!/usr/bin/env python3
"""Run the exact Guardian stage-part material resolver from parent-only context.

The existing resolver consumes the model/render-parent rows produced by the
broader visual-context probe, but its material logic does not require the UV or
linked vertex-stream census.  This adapter validates the narrow
`d1_guardian_render_parent_context/v1` report, converts only its compatible
model-parent envelope to the established resolver input schema, and delegates
to the existing exact resolver unchanged.

This is deliberately an adapter rather than a second material implementation.
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import d1_guardian_stage_part_material_resolve as exact


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--parent-context', type=Path, required=True)
    ap.add_argument('--model', action='append', required=True)
    ap.add_argument('--member-catalog', type=Path, action='append', required=True)
    ap.add_argument('--base-url', required=True)
    ap.add_argument('--part-count', type=int, default=10)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('-o', '--output', type=Path, required=True)
    a = ap.parse_args()

    context = json.loads(a.parent_context.read_text())
    if context.get('schema') != 'd1_guardian_render_parent_context/v1':
        raise ValueError(f"unexpected parent-context schema {context.get('schema')!r}")
    if context.get('errors'):
        raise ValueError('parent context has errors')
    models = context.get('models') or []
    if not models:
        raise ValueError('parent context contains no models')
    for row in models:
        if row.get('error'):
            raise ValueError(f"parent-context row error for {row.get('tag_hash')}: {row['error']}")
        parent = row.get('render_parent') or {}
        if not parent.get('embedded_model_tag_hash'):
            raise ValueError(f"parent-context row lacks render parent for {row.get('tag_hash')}")

    # The established material resolver only consumes `models[].tag_hash`,
    # `models[].render_parent`, and top-level `errors`.  Preserve those exact
    # fields and mark the temporary envelope with its established schema.
    compat = {
        'schema': 'd1_guardian_visual_context_probe/v1',
        'models': models,
        'errors': [],
        'adapter_source_schema': context['schema'],
    }

    a.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False) as f:
        json.dump(compat, f, indent=2)
        f.write('\n')
        compat_path = Path(f.name)

    argv = [
        'd1_guardian_stage_part_material_resolve.py',
        '--visual-context', str(compat_path),
    ]
    for model in a.model:
        argv += ['--model', model]
    for catalog in a.member_catalog:
        argv += ['--member-catalog', str(catalog)]
    argv += [
        '--base-url', a.base_url,
        '--part-count', str(a.part_count),
        '--runtime', str(a.runtime),
        '-o', str(a.output),
    ]

    old_argv = sys.argv
    try:
        sys.argv = argv
        rc = exact.main()
    finally:
        sys.argv = old_argv
        compat_path.unlink(missing_ok=True)

    # Add durable provenance without changing the core resolver implementation.
    report = json.loads(a.output.read_text())
    report['parent_context_schema'] = context['schema']
    report['parent_context_adapter'] = 'd1_guardian_stage_part_material_resolve_from_parent/v1'
    a.output.write_text(json.dumps(report, indent=2) + '\n')
    return int(rc or 0)


if __name__ == '__main__':
    raise SystemExit(main())
