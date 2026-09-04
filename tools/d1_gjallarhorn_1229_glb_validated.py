#!/usr/bin/env python3
"""Run the Gjallarhorn 1229 proof exporter with strict GPU-header snapshot validation.

Physical ROI patch snapshots can contain an entry-table view whose referenced
compressed block is readable but is no longer the historical GPU resource with
the same FileHash/index. The base exporter searches snapshots newest-to-oldest.
This shim strengthens candidate acceptance so it only stops on the requested,
byte-valid D1 VertexBufferHeader (32:4) or IndexBufferHeader (32:6) whose
linked payload satisfies the serialized data size.

No geometry interpretation is changed; this only prevents a repurposed or
malformed physical snapshot from winning over an older intact copy.
"""
from __future__ import annotations
import struct
import d1_gjallarhorn_1229_glb as base
from d1_investment_arrangement_probe import filehash_pkg_index


def _entry_bytes(reader, table, tag):
    e = table[tag.upper()]
    if not reader.available(e['index']):
        raise RuntimeError(f'{tag} unavailable in {reader.pkg.name}')
    return reader.entry(e['index'])


def validated_linked_payload(reader_sets, tag, kind=None):
    tag = tag.upper()
    pkg, _ = filehash_pkg_index(int(tag, 16))
    candidates = reader_sets.get(pkg)
    if not candidates:
        raise KeyError(f'{tag} belongs to unprovided logical package {pkg:04X}')
    expected_kind = {'vertex': (32, 4), 'index': (32, 6)}.get(kind)
    errors = []
    for r, table in candidates:
        e = table.get(tag)
        if e is None:
            continue
        entry_kind = (int(e['type']), int(e['subtype']))
        if expected_kind is not None and entry_kind != expected_kind:
            errors.append({'snapshot': r.pkg.name, 'error': f'expected {expected_kind}, got repurposed entry {entry_kind}'})
            continue
        if expected_kind is None and entry_kind not in ((32, 4), (32, 6)):
            errors.append({'snapshot': r.pkg.name, 'error': f'unexpected GPU header kind {entry_kind}'})
            continue
        ref = e['reference'].upper()
        pe = table.get(ref)
        if pe is None:
            errors.append({'snapshot': r.pkg.name, 'error': f'linked payload {ref} absent'})
            continue
        try:
            h = _entry_bytes(r, table, tag)
            p = _entry_bytes(r, table, ref)
            if entry_kind == (32, 4):
                if len(h) < 12:
                    raise ValueError(f'vertex header too short: {len(h)}')
                data_size = struct.unpack_from('<I', h, 0)[0]
                stride = struct.unpack_from('<h', h, 4)[0]
                marker = struct.unpack_from('<I', h, 8)[0]
                if stride <= 0 or stride > 256 or stride % 2:
                    raise ValueError(f'invalid vertex stride {stride}')
                if data_size <= 0:
                    raise ValueError(f'invalid vertex data_size {data_size}')
                if len(p) < data_size:
                    raise ValueError(f'vertex payload short {len(p)} < serialized {data_size}')
                if marker != 0xBEEFCACE:
                    raise ValueError(f'invalid vertex marker {marker:08X}')
                validation = {'kind': 'VertexBufferHeader', 'stride': stride, 'data_size': data_size, 'marker': 'BEEFCACE'}
            else:
                if len(h) < 24:
                    raise ValueError(f'index header too short: {len(h)}')
                data_size = struct.unpack_from('<Q', h, 8)[0]
                marker = struct.unpack_from('<I', h, 16)[0]
                if data_size <= 0:
                    raise ValueError(f'invalid index data_size {data_size}')
                if len(p) < data_size:
                    raise ValueError(f'index payload short {len(p)} < serialized {data_size}')
                if marker != 0xDEADBEEF:
                    raise ValueError(f'invalid index marker {marker:08X}')
                validation = {'kind': 'IndexBufferHeader', 'is32bit': bool(h[1]), 'data_size': data_size, 'marker': 'DEADBEEF'}
            return h, p, {
                'header_tag': tag,
                'payload_tag': ref,
                'header_reference': ref,
                'package_id': f'{pkg:04X}',
                'snapshot': r.pkg.name,
                'header_type': entry_kind[0],
                'header_subtype': entry_kind[1],
                'validation': validation,
                'fallback_errors': errors,
            }
        except Exception as ex:
            errors.append({'snapshot': r.pkg.name, 'error': repr(ex)})
    raise RuntimeError(f'could not recover a byte-valid {kind or "GPU"} {tag} in package {pkg:04X}: {errors}')


base.linked_payload = validated_linked_payload

if __name__ == '__main__':
    base.main()
