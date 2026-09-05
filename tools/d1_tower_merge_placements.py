#!/usr/bin/env python3
"""Merge D1 Tower baked-static cell GLBs using serialized placements only.

The static-cell exporter intentionally leaves one intrinsic/base graph node per
unique geometry variant in addition to the actual serialized placement nodes.
Those base nodes are useful in a single-cell proof, but merging cell GLBs naïvely
would render every variant once at its source transform *and* at every serialized
placement.

This merger copies each unique source geometry once, then copies only graph nodes
that are not exporter intrinsic nodes (names beginning with ``static_``). The world
matrix returned by trimesh for each retained source node is preserved exactly.

Evidence boundary:
- This tool does not invent placement or transform data.
- It does not deduplicate serialized placement nodes.
- It only removes exporter-created intrinsic/base geometry nodes.
- Expected placement counts may be asserted on the command line.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import trimesh


def safe_name(s: str) -> str:
    return ''.join(c if c.isalnum() or c in '._-' else '_' for c in s)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', action='append', type=Path, required=True,
                    help='Input Tower static-cell GLB; repeat for each cell')
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--json', type=Path, required=True)
    ap.add_argument('--expected-placements', type=int)
    args = ap.parse_args()

    out = trimesh.Scene()
    cell_reports = []
    total_placements = 0
    total_source_intrinsic = 0
    total_unique_geometry = 0

    for ci, path in enumerate(args.input):
        src = trimesh.load(path, force='scene', process=False)
        prefix = f'cell{ci:02d}_{safe_name(path.stem)}'

        geom_map = {}
        for gi, (gname, geom) in enumerate(src.geometry.items()):
            new_name = f'{prefix}_g{gi:05d}_{safe_name(str(gname))}'
            out.geometry[new_name] = geom.copy()
            geom_map[gname] = new_name
        total_unique_geometry += len(geom_map)

        kept = 0
        skipped = 0
        for ni, node in enumerate(src.graph.nodes_geometry):
            if str(node).startswith('static_'):
                skipped += 1
                continue
            transform, gname = src.graph.get(node)
            if gname not in geom_map:
                raise RuntimeError(f'{path}: node {node!r} references unknown geometry {gname!r}')
            new_node = f'{prefix}_p{ni:06d}_{safe_name(str(node))}'
            out.graph.update(
                frame_to=new_node,
                frame_from=out.graph.base_frame,
                matrix=transform,
                geometry=geom_map[gname],
            )
            kept += 1

        total_placements += kept
        total_source_intrinsic += skipped
        cell_reports.append({
            'input': path.name,
            'source_geometry_variants': len(geom_map),
            'source_graph_geometry_nodes': len(src.graph.nodes_geometry),
            'serialized_placement_nodes_kept': kept,
            'exporter_intrinsic_nodes_skipped': skipped,
            'source_bounds': src.bounds.tolist() if src.bounds is not None else None,
        })

    if args.expected_placements is not None and total_placements != args.expected_placements:
        raise SystemExit(
            f'expected {args.expected_placements} serialized placements, got {total_placements}'
        )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.json.parent.mkdir(parents=True, exist_ok=True)
    out.export(args.out, file_type='glb')

    check = trimesh.load(args.out, force='scene', process=False)
    if len(check.graph.nodes_geometry) != total_placements:
        raise SystemExit(
            f'reloaded GLB has {len(check.graph.nodes_geometry)} geometry nodes; '
            f'expected {total_placements}'
        )

    report = {
        'schema_version': 1,
        'status': 'PLACEMENT_ONLY_MERGE',
        'policy': 'Exporter intrinsic nodes named static_* are omitted; all serialized placement nodes and their world matrices are preserved.',
        'input_cell_count': len(args.input),
        'serialized_placement_nodes': total_placements,
        'source_intrinsic_nodes_omitted': total_source_intrinsic,
        'copied_geometry_variants': total_unique_geometry,
        'merged_scene_geometry': len(check.geometry),
        'merged_scene_geometry_nodes': len(check.graph.nodes_geometry),
        'merged_bounds': check.bounds.tolist() if check.bounds is not None else None,
        'glb_bytes': args.out.stat().st_size,
        'cells': cell_reports,
    }
    args.json.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
