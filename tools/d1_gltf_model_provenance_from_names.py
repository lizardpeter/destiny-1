#!/usr/bin/env python3
"""Stamp exact D1 model ownership onto combined glTF mesh nodes.

The generic remote model exporter names every geometry using the byte-proven
source form:

    XXXXXXXX_meshN_rangeOFFSET_COUNT

Combined arrangement/Guardian GLBs preserve those names, but some merge paths
do not preserve trimesh metadata as glTF node extras. The generic texture-plate
layer requires `node.extras.d1Model` so it can bind a plate header only to the
model that owns the geometry.

This bridge derives no new relationship: it merely losslessly reifies the model
FileHash already encoded by our exporter into the mesh/node name. Unknown names,
conflicting mesh owners, and requested-model coverage gaps fail closed.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from pygltflib import GLTF2

NAME_RE = re.compile(r'(?P<tag>[0-9A-F]{8})_mesh(?P<mesh>\d+)_range(?P<off>\d+)_(?P<count>\d+)', re.I)


def owner_from_name(value: str | None) -> str | None:
    if not value:
        return None
    m = NAME_RE.search(value)
    return m.group('tag').upper() if m else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('input_glb', type=Path)
    ap.add_argument('--expected-model', action='append', default=[])
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--report', type=Path, required=True)
    a = ap.parse_args()

    g = GLTF2().load_binary(str(a.input_glb))
    mesh_owner: dict[int, str] = {}
    mesh_source_names: dict[int, str] = {}
    errors = []

    for mi, mesh in enumerate(g.meshes):
        tag = owner_from_name(mesh.name)
        if tag is None:
            # A node name can carry the exporter source if the mesh name was
            # rewritten by an intermediate glTF library.
            node_tags = {owner_from_name(n.name) for n in g.nodes if n.mesh == mi}
            node_tags.discard(None)
            if len(node_tags) == 1:
                tag = next(iter(node_tags))
            elif len(node_tags) > 1:
                errors.append({'mesh': mi, 'error': 'conflicting source model tags in node names', 'tags': sorted(node_tags)})
                continue
        if tag is None:
            errors.append({'mesh': mi, 'error': 'source name does not match exact D1 exporter convention', 'mesh_name': mesh.name})
            continue
        mesh_owner[mi] = tag
        mesh_source_names[mi] = mesh.name or ''

    if errors:
        raise SystemExit(json.dumps(errors, indent=2))
    if len(mesh_owner) != len(g.meshes):
        raise SystemExit(f'only resolved {len(mesh_owner)}/{len(g.meshes)} mesh owners')

    node_rows = []
    represented = set()
    for ni, node in enumerate(g.nodes):
        if node.mesh is None:
            continue
        mi = int(node.mesh)
        tag = mesh_owner.get(mi)
        if tag is None:
            raise RuntimeError(f'node {ni} references unresolved mesh {mi}')
        extras = dict(node.extras or {})
        old = extras.get('d1Model')
        if old is not None and str(old).upper() != tag:
            raise RuntimeError(f'node {ni}: existing d1Model {old} conflicts with exact name owner {tag}')
        extras['d1Model'] = tag
        extras['d1ModelProvenance'] = 'exact exporter mesh-name FileHash'
        node.extras = extras
        represented.add(tag)
        node_rows.append({'node_index': ni, 'node_name': node.name, 'mesh_index': mi, 'model_tag': tag})

    expected = {x.upper().removeprefix('0X') for x in a.expected_model}
    if expected and represented != expected:
        raise RuntimeError(f'model coverage {sorted(represented)} != expected {sorted(expected)}')

    g.extras = {
        **(g.extras or {}),
        'd1ModelProvenance': {
            'method': 'exact exporter mesh/node name',
            'modelTags': sorted(represented),
            'geometryChanged': False,
        },
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    g.save_binary(str(a.out))

    check = GLTF2().load_binary(str(a.out))
    checked = []
    for ni, node in enumerate(check.nodes):
        if node.mesh is not None:
            tag = str((node.extras or {}).get('d1Model') or '').upper()
            if tag not in represented:
                raise RuntimeError(f'roundtrip lost d1Model on node {ni}')
            checked.append(ni)
    if len(checked) != len(node_rows):
        raise RuntimeError('mesh-node count changed during provenance roundtrip')

    rep = {
        'schema': 'd1_gltf_model_provenance_from_names/v1',
        'input': str(a.input_glb),
        'output': str(a.out),
        'mesh_count': len(g.meshes),
        'mesh_node_count': len(node_rows),
        'model_count': len(represented),
        'model_tags': sorted(represented),
        'nodes': node_rows,
        'policy': 'd1Model is copied only from the exact source FileHash already encoded in exporter-generated mesh/node names; geometry and animation are not modified.',
    }
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(rep, indent=2) + '\n')
    print(json.dumps({k: v for k, v in rep.items() if k != 'nodes'}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
