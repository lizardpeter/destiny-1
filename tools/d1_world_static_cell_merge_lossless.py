#!/usr/bin/env python3
"""Loss-preserving merger for D1 retail-visible static-cell GLBs.

The per-cell static exporter creates two kinds of active-scene roots:

* serialized placement nodes: source-owned world instances which must render;
* ``static_*`` intrinsic nodes created by trimesh when a geometry object is added
  before its serialized placements are attached.  These are exporter scaffolding and
  must not render in the combined world.

The historical ten-cell merger round-tripped every mesh through trimesh.  That is
unacceptable for shader reconstruction because glTF attributes such as COLOR_0 and
application-specific ``_D1_*`` streams can be reinterpreted or discarded by that
round-trip.

This merger instead uses ``d1_world_layer_merge`` to concatenate the original glTF
JSON/BIN structures byte-for-byte, then prunes only unreachable node objects after
removing source ``static_*`` intrinsic roots from the active scene.  Meshes,
accessors, bufferViews, material payloads and attribute dictionaries are never
decoded or reconstructed.

Static-cell contract is deliberately strict: skins and animations are rejected.
Use the general world-layer merger for articulated layers.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path

from d1_world_layer_merge import merge_layers, read_glb, write_glb


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def active_roots(doc: dict) -> list[int]:
    scenes = doc.get('scenes') or []
    if not scenes:
        children = {int(c) for n in doc.get('nodes', []) for c in n.get('children', []) or []}
        return [i for i in range(len(doc.get('nodes', []))) if i not in children]
    si = int(doc.get('scene', 0))
    if si < 0 or si >= len(scenes):
        raise ValueError(f'invalid active scene {si}')
    return [int(x) for x in scenes[si].get('nodes', []) or []]


def reachable(nodes: list[dict], roots: list[int]) -> set[int]:
    seen: set[int] = set()
    stack = list(roots)
    while stack:
        i = int(stack.pop())
        if i in seen:
            continue
        if i < 0 or i >= len(nodes):
            raise ValueError(f'node reference out of bounds: {i}')
        seen.add(i)
        stack.extend(int(x) for x in nodes[i].get('children', []) or [])
    return seen


def prune_nodes(doc: dict, roots: list[int]) -> tuple[dict, dict]:
    nodes = doc.get('nodes', [])
    keep = sorted(reachable(nodes, roots))
    remap = {old: new for new, old in enumerate(keep)}
    out = copy.deepcopy(doc)
    nn = []
    for old in keep:
        n = copy.deepcopy(nodes[old])
        if 'children' in n:
            n['children'] = [remap[int(x)] for x in n['children']]
        nn.append(n)
    out['nodes'] = nn
    out['scene'] = 0
    out['scenes'] = [{'name': 'D1 merged retail-visible static placements',
                      'nodes': [remap[int(x)] for x in roots]}]
    return out, {'source_node_count': len(nodes), 'kept_node_count': len(nn),
                 'pruned_node_count': len(nodes) - len(nn)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', action='append', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--report', type=Path, required=True)
    ap.add_argument('--expected-placements', type=int)
    a = ap.parse_args()

    layers = []
    source_rows = []
    expected_attrs = []
    total_placement_roots = 0
    for i, p in enumerate(a.input):
        d, _ = read_glb(p)
        if d.get('skins') or d.get('animations'):
            raise SystemExit(f'{p}: static-cell input unexpectedly has skins/animations')
        roots = active_roots(d)
        intrinsic = []
        placements = []
        for r in roots:
            name = str((d.get('nodes') or [])[r].get('name') or '')
            if name.startswith('static_'):
                intrinsic.append(r)
            else:
                placements.append(r)
        if not placements:
            raise SystemExit(f'{p}: no serialized placement roots')
        # Record exact primitive attribute dictionaries before merge.  This is the
        # invariant that the historical scene-library merger could not guarantee.
        attrs = [[copy.deepcopy(pr.get('attributes', {})) for pr in m.get('primitives', [])]
                 for m in d.get('meshes', [])]
        expected_attrs.append(attrs)
        total_placement_roots += len(placements)
        source_rows.append({'input': p.name, 'sha256': digest(p),
                            'active_scene_roots': len(roots),
                            'placement_roots': len(placements),
                            'intrinsic_roots': len(intrinsic),
                            'mesh_count': len(d.get('meshes', [])),
                            'accessor_count': len(d.get('accessors', []))})
        layers.append((f'cell{i:02d}', p))

    if a.expected_placements is not None and total_placement_roots != a.expected_placements:
        raise SystemExit(f'expected {a.expected_placements} placement roots, got {total_placement_roots}')

    merged, binb, layer_rows = merge_layers(layers, {})
    roots = active_roots(merged)
    kept_roots = []
    removed_intrinsic = []
    for r in roots:
        name = str(merged['nodes'][r].get('name') or '')
        if name.startswith('static_'):
            removed_intrinsic.append(r)
        else:
            kept_roots.append(r)
    if len(kept_roots) != total_placement_roots:
        raise SystemExit(f'merged placement-root count changed: {len(kept_roots)} != {total_placement_roots}')

    merged, prune = prune_nodes(merged, kept_roots)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    write_glb(a.out, merged, binb)
    chk, chkbin = read_glb(a.out)
    if chkbin != binb:
        raise SystemExit('BIN changed after write/reload')

    # Prove every source mesh primitive's attribute key set survived.  Accessor
    # indices necessarily shift between concatenated cells, so compare semantics
    # and per-source relative index deltas rather than raw global numbers.
    out_meshes = chk.get('meshes', [])
    cursor = 0
    attribute_key_mismatches = []
    color_primitive_count = 0
    custom_d1_attribute_count = 0
    for si, attrs_by_mesh in enumerate(expected_attrs):
        for local_mi, prim_attrs in enumerate(attrs_by_mesh):
            om = out_meshes[cursor + local_mi]
            opr = om.get('primitives', [])
            if len(opr) != len(prim_attrs):
                attribute_key_mismatches.append({'source': si, 'mesh': local_mi, 'reason': 'primitive_count'})
                continue
            for pi, srca in enumerate(prim_attrs):
                outa = opr[pi].get('attributes', {})
                if set(outa) != set(srca):
                    attribute_key_mismatches.append({'source': si, 'mesh': local_mi, 'primitive': pi,
                                                     'source_keys': sorted(srca), 'output_keys': sorted(outa)})
                if 'COLOR_0' in outa:
                    color_primitive_count += 1
                custom_d1_attribute_count += sum(1 for k in outa if k.startswith('_D1_'))
        cursor += len(attrs_by_mesh)
    if attribute_key_mismatches:
        raise SystemExit('primitive attributes changed: ' + json.dumps(attribute_key_mismatches[:10]))

    output_roots = active_roots(chk)
    if len(output_roots) != total_placement_roots:
        raise SystemExit(f'output active roots {len(output_roots)} != placements {total_placement_roots}')
    geometry_nodes = sum(1 for i in reachable(chk.get('nodes', []), output_roots)
                         if 'mesh' in chk['nodes'][i])
    if geometry_nodes != total_placement_roots:
        raise SystemExit(f'active geometry-node count {geometry_nodes} != placements {total_placement_roots}')

    rep = {
        'schema_version': 1,
        'status': 'D1_WORLD_STATIC_CELL_GLB_LOSS_PRESERVING_MERGE',
        'input_cell_count': len(a.input),
        'serialized_placement_roots': total_placement_roots,
        'source_intrinsic_roots_removed': len(removed_intrinsic),
        'active_geometry_nodes': geometry_nodes,
        'mesh_count': len(chk.get('meshes', [])),
        'accessor_count': len(chk.get('accessors', [])),
        'buffer_view_count': len(chk.get('bufferViews', [])),
        'color0_primitive_count': color_primitive_count,
        'custom_d1_attribute_occurrence_count': custom_d1_attribute_count,
        'attribute_key_mismatches': attribute_key_mismatches,
        'node_prune': prune,
        'source_cells': source_rows,
        'layer_merge_rows': layer_rows,
        'output': {'file': str(a.out), 'bytes': a.out.stat().st_size, 'sha256': digest(a.out)},
        'policy': 'Source glTF mesh/accessor/BIN structures are never decoded or re-exported. Only exporter-created static_* active roots and the node objects unreachable after removing those roots are pruned.'
    }
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(rep, indent=2) + '\n')
    print(json.dumps({k: rep[k] for k in ('status','input_cell_count','serialized_placement_roots','source_intrinsic_roots_removed','active_geometry_nodes','mesh_count','accessor_count','color0_primitive_count','custom_d1_attribute_occurrence_count','output')}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
