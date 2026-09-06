#!/usr/bin/env python3
"""Losslessly inspect and unpack Bungie TGXM file packs.

Format provenance is the archived Bungie Spasm ``Spasm.TGXBinLoader`` implementation:
- ASCII magic ``TGXM``
- little-endian int32 version at +0x04
- index-record byte size at +0x08
- index count at +0x0c
- v1: 128-byte filenames, index starts at +0x10
- v2: 256-byte pack identifier at +0x10, then 256-byte filenames
- every index record ends with uint64 file offset + uint64 file size

This tool deliberately does not infer geometry semantics from filenames. It preserves
pack identifiers, file table order, offsets, sizes, SHA-256 values, and exact payloads.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path


def cstring(raw: bytes) -> str:
    value = raw.split(b'\0', 1)[0]
    try:
        return value.decode('utf-8')
    except UnicodeDecodeError as ex:
        raise ValueError(f'TGXM string is not UTF-8/ASCII: {ex}') from ex


def parse_tgxm(data: bytes) -> dict:
    if len(data) < 16:
        raise ValueError('TGXM shorter than 16-byte header')
    if data[:4] != b'TGXM':
        raise ValueError(f'bad TGXM magic {data[:4]!r}')
    version, record_size, count = struct.unpack_from('<iii', data, 4)
    if version == 1:
        name_size = 128
        index_start = 16
        identifier = None
    elif version == 2:
        name_size = 256
        if len(data) < 272:
            raise ValueError('TGXM v2 shorter than identifier header')
        identifier = cstring(data[16:272])
        index_start = 272
    else:
        raise ValueError(f'unsupported TGXM version {version}')

    expected_record_size = name_size + 16
    if record_size != expected_record_size:
        raise ValueError(f'index record size {record_size} != expected {expected_record_size}')
    if count < 0:
        raise ValueError(f'negative TGXM index count {count}')
    index_end = index_start + count * record_size
    if index_end > len(data):
        raise ValueError(f'TGXM index ends at {index_end}, beyond file size {len(data)}')

    rows = []
    names = set()
    intervals = []
    for i in range(count):
        off = index_start + i * record_size
        name = cstring(data[off:off + name_size])
        payload_off, payload_size = struct.unpack_from('<QQ', data, off + name_size)
        payload_end = payload_off + payload_size
        if not name:
            raise ValueError(f'index {i}: empty filename')
        if name in names:
            raise ValueError(f'index {i}: duplicate filename {name!r}')
        names.add(name)
        if payload_off < index_end:
            raise ValueError(f'index {i} {name}: payload begins inside header/index ({payload_off} < {index_end})')
        if payload_end > len(data):
            raise ValueError(f'index {i} {name}: payload ends beyond file ({payload_end} > {len(data)})')
        payload = data[payload_off:payload_end]
        rows.append({
            'index': i,
            'file_name': name,
            'file_offset': payload_off,
            'file_size': payload_size,
            'sha256': hashlib.sha256(payload).hexdigest(),
        })
        if payload_size:
            intervals.append((payload_off, payload_end, name))

    intervals.sort()
    for a, b in zip(intervals, intervals[1:]):
        if a[1] > b[0]:
            raise ValueError(f'overlapping TGXM payloads: {a[2]!r} and {b[2]!r}')

    render_metadata = None
    metadata_row = next((x for x in rows if x['file_name'] == 'render_metadata.js'), None)
    if metadata_row is not None:
        p0 = metadata_row['file_offset']
        p1 = p0 + metadata_row['file_size']
        raw = data[p0:p1].rstrip(b'\0')
        try:
            render_metadata = json.loads(raw.decode('utf-8-sig'))
        except Exception as ex:
            raise ValueError(f'render_metadata.js is not valid JSON: {ex}') from ex

    return {
        'schema': 'd1_tgxm_unpack/v1',
        'magic': 'TGXM',
        'version': version,
        'file_identifier': identifier,
        'index_record_size': record_size,
        'file_count': count,
        'index_start': index_start,
        'index_end': index_end,
        'file_size': len(data),
        'sha256': hashlib.sha256(data).hexdigest(),
        'files': rows,
        'render_metadata': render_metadata,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('tgxm', type=Path)
    ap.add_argument('--extract-dir', type=Path)
    ap.add_argument('-o', '--output', type=Path, required=True)
    a = ap.parse_args()

    data = a.tgxm.read_bytes()
    rep = parse_tgxm(data)
    rep['source_path'] = str(a.tgxm)

    if a.extract_dir:
        a.extract_dir.mkdir(parents=True, exist_ok=True)
        for row in rep['files']:
            name = row['file_name']
            # TGXM names are expected to be flat. Reject traversal instead of sanitizing.
            if Path(name).name != name or name in ('.', '..'):
                raise ValueError(f'unsafe/non-flat TGXM filename {name!r}')
            p0 = int(row['file_offset'])
            p1 = p0 + int(row['file_size'])
            (a.extract_dir / name).write_bytes(data[p0:p1])
        rep['extract_dir'] = str(a.extract_dir)

    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(rep, indent=2) + '\n')
    print(json.dumps({
        'path': str(a.tgxm),
        'version': rep['version'],
        'file_identifier': rep['file_identifier'],
        'file_count': rep['file_count'],
        'bytes': rep['file_size'],
        'sha256': rep['sha256'],
        'render_mesh_count': len(((rep.get('render_metadata') or {}).get('render_model') or {}).get('render_meshes') or []),
        'files': [x['file_name'] for x in rep['files']],
    }, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
