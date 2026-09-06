#!/usr/bin/env python3
"""Probe exact D1 Spektar PS4 vertex-shader headers and OrbShdr metadata framing.

This is deliberately structural.  It starts from explicit vertex-shader FileHashes,
resolves them through verified split-TAR package catalogs, and reports:

* the Tiger FileEntry type/subtype and raw engine-header bytes;
* the exact native Orbis payload referenced by FileEntry.Reference;
* ShaderBinaryInfo stage/code accounting;
* InputUsageSlot and chunk-mask byte ranges;
* whether *all* bytes between native code and OrbShdr footer are already explained
  by those usage structures.

If unexplained metadata remains, it is preserved byte-for-byte as a candidate place
for native vertex semantic/fetch metadata.  Nothing in this probe names a semantic.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from d1_entity_model_export import byhash
from d1_investment_arrangement_probe import filehash_pkg_index
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_ps4_shader_binary_probe import find_footer, parse_binary_info, parse_usage
from d1_remote_investment_parent_probe import RemoteLogicalPackage
from d1_remote_model_export import MultiPackageReader
from d1_split_tar_extract import SplitHttpTar


def norm_hash(v: str) -> str:
    v = str(v).upper().removeprefix('0X').zfill(8)
    if len(v) != 8:
        raise ValueError(v)
    int(v, 16)
    return v


def pkg_id(tag: str) -> int:
    return filehash_pkg_index(int(tag, 16))[0]


def desc(e: dict | None) -> dict | None:
    if e is None:
        return None
    return {
        'tag_hash': e['tag_hash'].upper(),
        'reference': e['reference'].upper(),
        'type': e['type'],
        'subtype': e['subtype'],
        'file_size': e['file_size'],
        'source_package_id': f"{int(e.get('_source_package_id')):04X}" if e.get('_source_package_id') is not None else None,
        'source_file_index': e.get('_source_file_index'),
    }


def printable_words(b: bytes) -> list[str]:
    if len(b) % 4:
        return []
    return [f'{x:08X}' for x in struct.unpack('<' + 'I' * (len(b) // 4), b)]


def probe_one(tag: str, multi: MultiPackageReader, hmap: dict[str, dict]) -> dict:
    e = hmap.get(tag)
    row = {
        'vertex_shader_hash': tag,
        'required_package_id': f'{pkg_id(tag):04X}',
        'header_entry': desc(e),
    }
    if e is None:
        row['resolved_header'] = False
        return row

    hb = multi.entry(e['index'])
    row.update({
        'resolved_header': True,
        'header_size': len(hb),
        'header_sha256': hashlib.sha256(hb).hexdigest(),
        'header_hex': hb.hex(),
        'header_u32_words': printable_words(hb),
    })

    native_tag = e['reference'].upper()
    row['native_shader_hash'] = native_tag
    row['native_required_package_id'] = f'{pkg_id(native_tag):04X}'
    ne = hmap.get(native_tag)
    row['native_entry'] = desc(ne)
    if ne is None:
        row['resolved_native'] = False
        return row

    nb = multi.entry(ne['index'])
    row['resolved_native'] = True
    row['native_size'] = len(nb)
    row['native_sha256'] = hashlib.sha256(nb).hexdigest()
    row['native_prefix_64'] = nb[:64].hex()

    footer, checks = find_footer(nb)
    row['orbshdr_locator'] = checks
    if footer is None:
        row['orbshdr_resolved'] = False
        return row
    info = parse_binary_info(nb, footer)
    usage = parse_usage(nb, footer, info)
    code_end = info['code_length_bytes']
    slots_off = usage['input_usage_slots_offset']
    masks_off = usage['usage_masks_offset']
    row['orbshdr_resolved'] = True
    row['binary_info'] = info
    row['usage'] = usage
    row['code_sha256'] = hashlib.sha256(nb[:code_end]).hexdigest()
    row['metadata_layout'] = {
        'code_end': code_end,
        'input_usage_slots_offset': slots_off,
        'usage_masks_offset': masks_off,
        'footer_offset': footer,
        'bytes_code_to_slots': slots_off - code_end,
        'bytes_slots': masks_off - slots_off,
        'bytes_masks': footer - masks_off,
        'all_code_to_footer_explained_by_usage_tables': code_end == slots_off,
        'unexplained_code_to_slots_hex': nb[code_end:slots_off].hex(),
        'input_usage_slots_hex': nb[slots_off:masks_off].hex(),
        'usage_masks_hex': nb[masks_off:footer].hex(),
    }
    return row


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--vertex-shader', action='append', required=True)
    ap.add_argument('--member-catalog', type=Path, action='append', required=True)
    ap.add_argument('--base-url', required=True)
    ap.add_argument('--part-count', type=int, default=10)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('-o', '--output', type=Path, required=True)
    a = ap.parse_args()

    wanted = [norm_hash(x) for x in a.vertex_shader]
    catalogs = load_catalogs(a.member_catalog)
    missing = sorted({pkg_id(x) for x in wanted} - set(catalogs))
    if missing:
        raise SystemExit('missing vertex-shader package catalogs: ' + ', '.join(f'{x:04X}' for x in missing))

    base = a.base_url.rstrip('/')
    arc = SplitHttpTar([f'{base}/packages.tar.{i:03d}' for i in range(1, a.part_count + 1)], retries=6, timeout=90)
    views = {pkg: RemoteLogicalPackage(arc, fam, a.runtime) for pkg, fam in sorted(catalogs.items())}
    multi = MultiPackageReader(views)
    hmap = byhash(multi)
    rows = [probe_one(x, multi, hmap) for x in wanted]

    report = {
        'schema': 'd1_guardian_native_vs_layout_probe/v1',
        'vertex_shader_count': len(rows),
        'resolved_header_count': sum(bool(x.get('resolved_header')) for x in rows),
        'resolved_native_count': sum(bool(x.get('resolved_native')) for x in rows),
        'orbshdr_resolved_count': sum(bool(x.get('orbshdr_resolved')) for x in rows),
        'rows': rows,
        'policy': 'No bytes are assigned vertex semantics here. The probe only proves engine-header and native-metadata framing.',
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2) + '\n')

    for r in rows:
        md = r.get('metadata_layout') or {}
        bi = r.get('binary_info') or {}
        print('VS', r['vertex_shader_hash'],
              'header', r.get('header_entry'),
              'header_hex', r.get('header_hex'),
              'native', r.get('native_shader_hash'),
              'stage', bi.get('stage'),
              'code_to_slots', md.get('bytes_code_to_slots'),
              'slots', md.get('bytes_slots'),
              'masks', md.get('bytes_masks'),
              'unexplained', md.get('unexplained_code_to_slots_hex'))
    print('SUMMARY', {k: v for k, v in report.items() if k not in ('rows', 'policy')})
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
