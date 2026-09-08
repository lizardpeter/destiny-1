#!/usr/bin/env python3
"""Build shared world-space diagnostic camera views for the ten-cell Tower GLB.

The merged Tower scene stores baked-static placements as root nodes named
`cellNN_*`.  This planner reads only the GLB JSON chunk, transforms accessor
POSITION bounds through each placement node, derives robust per-cell bounds,
and then derives shared cameras that can be reused while rendering each cell in
an independent Blender process.  No geometry or texture bytes are modified.
"""
from __future__ import annotations

import argparse, json, math, mmap, struct
from pathlib import Path

GLB_MAGIC = 0x46546C67
JSON_CHUNK = 0x4E4F534A


def cli():
    ap = argparse.ArgumentParser()
    ap.add_argument('src', type=Path)
    ap.add_argument('--out', type=Path, required=True)
    return ap.parse_args()


def pct(xs, p):
    xs = sorted(float(x) for x in xs)
    if not xs:
        raise ValueError('empty percentile input')
    q = (len(xs) - 1) * p
    i = int(math.floor(q))
    j = min(i + 1, len(xs) - 1)
    t = q - i
    return xs[i] * (1 - t) + xs[j] * t


def quat_matrix(q):
    x, y, z, w = map(float, q)
    n = math.sqrt(x*x + y*y + z*z + w*w)
    if n <= 1e-20:
        x = y = z = 0.0; w = 1.0
    else:
        x /= n; y /= n; z /= n; w /= n
    xx, yy, zz = x*x, y*y, z*z
    xy, xz, yz = x*y, x*z, y*z
    wx, wy, wz = w*x, w*y, w*z
    return [
        [1 - 2*(yy+zz), 2*(xy-wz),     2*(xz+wy)],
        [2*(xy+wz),     1 - 2*(xx+zz), 2*(yz-wx)],
        [2*(xz-wy),     2*(yz+wx),     1 - 2*(xx+yy)],
    ]


def node_matrix(n):
    if 'matrix' in n:
        m = list(map(float, n['matrix']))
        if len(m) != 16:
            raise ValueError('node matrix must have 16 values')
        # glTF stores matrices column-major.
        return [
            [m[0], m[4], m[8],  m[12]],
            [m[1], m[5], m[9],  m[13]],
            [m[2], m[6], m[10], m[14]],
            [m[3], m[7], m[11], m[15]],
        ]
    t = list(map(float, n.get('translation', [0, 0, 0])))
    s = list(map(float, n.get('scale', [1, 1, 1])))
    r = quat_matrix(n.get('rotation', [0, 0, 0, 1]))
    return [
        [r[0][0]*s[0], r[0][1]*s[1], r[0][2]*s[2], t[0]],
        [r[1][0]*s[0], r[1][1]*s[1], r[1][2]*s[2], t[1]],
        [r[2][0]*s[0], r[2][1]*s[1], r[2][2]*s[2], t[2]],
        [0.0, 0.0, 0.0, 1.0],
    ]


def transform(m, p):
    x, y, z = map(float, p)
    return (
        m[0][0]*x + m[0][1]*y + m[0][2]*z + m[0][3],
        m[1][0]*x + m[1][1]*y + m[1][2]*z + m[1][3],
        m[2][0]*x + m[2][1]*y + m[2][2]*z + m[2][3],
    )


def finite3(p):
    return all(math.isfinite(float(x)) for x in p)


def main():
    a = cli()
    with a.src.open('rb') as f:
        mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        magic, ver, total = struct.unpack_from('<III', mm, 0)
        if magic != GLB_MAGIC or ver != 2 or total != len(mm):
            raise SystemExit('invalid GLB2 header')
        jlen, jtyp = struct.unpack_from('<II', mm, 12)
        if jtyp != JSON_CHUNK:
            raise SystemExit('first chunk is not JSON')
        doc = json.loads(mm[20:20+jlen].decode('utf-8').rstrip(' \t\r\n\x00'))
        mm.close()

    per = {i: {'x': [], 'y': [], 'z': [], 'nodes': 0, 'primitive_bounds': 0} for i in range(10)}
    for n in doc.get('nodes', []):
        name = str(n.get('name', ''))
        if not name.startswith('cell') or len(name) < 7 or not name[4:6].isdigit() or 'mesh' not in n:
            continue
        ci = int(name[4:6])
        if ci not in per:
            continue
        mid = int(n['mesh'])
        if mid < 0 or mid >= len(doc.get('meshes', [])):
            continue
        m = node_matrix(n)
        per[ci]['nodes'] += 1
        for prim in doc['meshes'][mid].get('primitives', []):
            pos = (prim.get('attributes') or {}).get('POSITION')
            if pos is None or pos < 0 or pos >= len(doc.get('accessors', [])):
                continue
            acc = doc['accessors'][pos]
            lo, hi = acc.get('min'), acc.get('max')
            if not (isinstance(lo, list) and isinstance(hi, list) and len(lo) >= 3 and len(hi) >= 3):
                continue
            pts = []
            for x in (lo[0], hi[0]):
                for y in (lo[1], hi[1]):
                    for z in (lo[2], hi[2]):
                        p = transform(m, (x, y, z))
                        if finite3(p):
                            pts.append(p)
            if len(pts) != 8:
                continue
            per[ci]['primitive_bounds'] += 1
            for x, y, z in pts:
                per[ci]['x'].append(x); per[ci]['y'].append(y); per[ci]['z'].append(z)

    cells = []
    for ci in range(10):
        d = per[ci]
        if len(d['x']) < 8:
            raise SystemExit(f'cell {ci:02d}: insufficient accessor bounds')
        row = {
            'cell': ci,
            'nodes': d['nodes'],
            'primitive_bounds': d['primitive_bounds'],
            'robust': {
                'xmin': pct(d['x'], .015), 'xmax': pct(d['x'], .985),
                'ymin': pct(d['y'], .015), 'ymax': pct(d['y'], .985),
                'zmin': pct(d['z'], .03),  'zmax': pct(d['z'], .97),
            }
        }
        b = row['robust']
        row['center'] = [(b['xmin']+b['xmax'])/2, (b['ymin']+b['ymax'])/2, (b['zmin']+b['zmax'])/2]
        cells.append(row)

    # Union the independently trimmed cell bounds.  This avoids allowing a huge
    # serialized outlier in one cell to dominate the camera for every cell.
    xmin = min(x['robust']['xmin'] for x in cells); xmax = max(x['robust']['xmax'] for x in cells)
    ymin = min(x['robust']['ymin'] for x in cells); ymax = max(x['robust']['ymax'] for x in cells)
    zmin = min(x['robust']['zmin'] for x in cells); zmax = max(x['robust']['zmax'] for x in cells)
    cx, cy, cz = (xmin+xmax)/2, (ymin+ymax)/2, (zmin+zmax)/2
    sx, sy, sz = xmax-xmin, ymax-ymin, zmax-zmin
    span = max(sx, sy, 10.0)
    height = max(span * .42, sz * 1.75, 20.0)

    views = [
        {
            'name': 'oblique_a', 'type': 'PERSP', 'lens_mm': 48.0,
            'camera': [cx + span*.78, cy - span*1.08, cz + height],
            'target': [cx, cy, cz + max(1.0, sz*.03)],
        },
        {
            'name': 'oblique_b', 'type': 'PERSP', 'lens_mm': 50.0,
            'camera': [cx - span*.90, cy + span*.86, cz + height*1.08],
            'target': [cx, cy, cz + max(1.0, sz*.03)],
        },
        {
            'name': 'top', 'type': 'ORTHO', 'ortho_scale': span*1.12,
            'camera': [cx, cy, cz + max(span*1.35, sz*4.0, 50.0)],
            'target': [cx, cy, cz],
        },
    ]

    out = {
        'status': 'D1_TOWER_SHARED_CAMERA_PLAN',
        'source': a.src.name,
        'cell_count': 10,
        'cell_bounds': cells,
        'union_robust_bounds': {'xmin': xmin, 'xmax': xmax, 'ymin': ymin, 'ymax': ymax, 'zmin': zmin, 'zmax': zmax},
        'center': [cx, cy, cz], 'span_xy': span, 'zspan': sz,
        'views': views,
        'policy': 'Shared world-space diagnostic cameras derived from per-cell robust accessor bounds. Serialized extreme outliers are excluded independently per cell; source geometry is unchanged.'
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps(out, indent=2))


if __name__ == '__main__':
    main()

# Trigger touch: all-ten composite workflow is now wired to this planner.
