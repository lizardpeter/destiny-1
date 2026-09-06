#!/usr/bin/env python3
"""Generation-safe remote D1 PS4 texture exporter.

Destiny 1 logical package file-index slots can change meaning across physical
patch snapshots.  A FileHash therefore must not be forced through the newest
entry/block table merely because its package/index still exists there.

For every requested texture header this tool searches complete serialized
texture chains newest-to-oldest:

    texture header (32:1 / 32:2)
        -> serialized reference, normally streamed mip record
        -> serialized reference when present, otherwise the stream payload

A candidate is accepted only when every required payload can be read, the
texture header decodes, the backing surface unswizzles, and Pillow can decode
the generated DDS into a PNG.  If a child reference stays in the same package
family, its snapshot may not be newer than the parent snapshot.  This prevents
an old header from silently binding to a repurposed newer slot.

The chosen physical snapshot is recorded independently for header, stream and
backing.  No neighboring-package or filename inference is used.
"""
from __future__ import annotations

import argparse
import io
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from d1_investment_arrangement_probe import filehash_pkg_index
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_investment_parent_probe import RemoteLogicalPackage
from d1_split_tar_extract import SplitHttpTar
from d1_texture_export import (
    FORMAT_NAME,
    Image,
    decode_header,
    expected_base_size,
    make_dds,
    unswizzle_ps4,
)

HEADER_TYPES = {(32, 1), (32, 2)}


def norm(value: str) -> str:
    value = value.upper().removeprefix('0X').zfill(8)
    int(value, 16)
    return value


def desc(tag: str, view: RemoteLogicalPackage, patch: int, entry: dict) -> dict:
    return {
        'tag_hash': tag,
        'package_id': f"{int(view.h['pkg_id']):04X}",
        'file_index': int(entry['index']),
        'patch_id': patch,
        'snapshot': view.view.name,
        'type': int(entry['type']),
        'subtype': int(entry['subtype']),
        'reference': entry['reference'].upper(),
        'declared_file_size': int(entry['file_size']),
    }


class SnapshotPool:
    def __init__(self, archive: SplitHttpTar, catalogs: dict, runtime: Path):
        self.archive = archive
        self.catalogs = catalogs
        self.runtime = runtime
        self._views: dict[tuple[int, int], RemoteLogicalPackage] = {}

    def view(self, pkg: int, patch: int) -> RemoteLogicalPackage:
        key = (pkg, patch)
        if key in self._views:
            return self._views[key]
        fam = self.catalogs[pkg]
        # A physical snapshot can reference blocks from earlier generations,
        # but never from later generations.
        siblings = {p: m for p, m in fam.items() if p <= patch}
        if patch not in siblings:
            raise KeyError(f'package {pkg:04X} has no patch {patch}')
        v = RemoteLogicalPackage(self.archive, siblings, self.runtime)
        if int(v.view.patch_id) != patch:
            raise RuntimeError(f'package {pkg:04X}: requested patch {patch}, opened {v.view.patch_id}')
        self._views[key] = v
        return v

    def candidates(self, tag: str, max_patch: int | None = None, expected_types: set[tuple[int, int]] | None = None):
        pkg, idx = filehash_pkg_index(int(tag, 16))
        fam = self.catalogs.get(pkg)
        if fam is None:
            return
        patches = [p for p in fam if max_patch is None or p <= max_patch]
        for patch in sorted(patches, reverse=True):
            try:
                v = self.view(pkg, patch)
            except Exception as ex:
                yield {'ok': False, 'stage': 'open_snapshot', 'tag_hash': tag, 'package_id': f'{pkg:04X}', 'patch_id': patch, 'error': repr(ex)}
                continue
            if idx >= len(v.entries):
                yield {'ok': False, 'stage': 'entry_lookup', 'tag_hash': tag, 'package_id': f'{pkg:04X}', 'patch_id': patch, 'error': f'file index {idx} outside {len(v.entries)} entries'}
                continue
            e = v.entries[idx]
            if e['tag_hash'].upper() != tag:
                yield {'ok': False, 'stage': 'entry_lookup', 'tag_hash': tag, 'package_id': f'{pkg:04X}', 'patch_id': patch, 'error': f"logical tag mismatch {e['tag_hash']}"}
                continue
            if expected_types is not None and (int(e['type']), int(e['subtype'])) not in expected_types:
                yield {'ok': False, 'stage': 'entry_type', 'entry': desc(tag, v, patch, e), 'error': f"unexpected type/subtype {(e['type'], e['subtype'])}"}
                continue
            try:
                payload = v.entry(idx)
            except Exception as ex:
                yield {'ok': False, 'stage': 'payload_read', 'entry': desc(tag, v, patch, e), 'error': repr(ex)}
                continue
            yield {'ok': True, 'view': v, 'patch_id': patch, 'entry': e, 'payload': payload, 'desc': desc(tag, v, patch, e)}

    def any_entry_exists(self, tag: str, max_patch: int | None = None) -> bool:
        pkg, idx = filehash_pkg_index(int(tag, 16))
        fam = self.catalogs.get(pkg)
        if fam is None:
            return False
        for patch in sorted((p for p in fam if max_patch is None or p <= max_patch), reverse=True):
            try:
                v = self.view(pkg, patch)
            except Exception:
                continue
            if idx < len(v.entries) and v.entries[idx]['tag_hash'].upper() == tag:
                return True
        return False


def child_max_patch(parent_tag: str, parent_patch: int, child_tag: str) -> int | None:
    ppkg, _ = filehash_pkg_index(int(parent_tag, 16))
    cpkg, _ = filehash_pkg_index(int(child_tag, 16))
    return parent_patch if ppkg == cpkg else None


def render_texture(header_tag: str, header_bytes: bytes, backing_bytes: bytes) -> tuple[dict, bytes | None, bytes | None]:
    h = decode_header(header_bytes)
    expected = expected_base_size(h['width'], h['height'], h['surface_format'], h['array_size'])
    raw = backing_bytes
    if expected and len(raw) >= expected:
        raw = raw[:expected]
    swizzled = ((h['flags1'] & 0xC00) != 0x400) or h['array_size'] == 6
    linear = unswizzle_ps4(raw, h['width'], h['height'], h['array_size'], h['surface_format']) if swizzled else raw
    fmt_name = FORMAT_NAME.get(h['surface_format']) or ('GCN%02X' % h['surface_format'])
    stem = f"{header_tag}_{h['width']}x{h['height']}_{fmt_name}"
    meta = {
        **h,
        'format_name': fmt_name,
        'backing_bytes': len(raw),
        'unswizzled': swizzled,
        'stem': stem,
    }
    if h['array_size'] != 1:
        raise RuntimeError(f'{header_tag}: plate source texture array_size={h["array_size"]}; expected 2D image')
    dds = make_dds(linear, h['width'], h['height'], h['surface_format'])
    if Image is None:
        raise RuntimeError('Pillow unavailable; PNG validation is required')
    im = Image.open(io.BytesIO(dds))
    im.load()
    png_io = io.BytesIO()
    im.save(png_io, format='PNG')
    return meta, dds, png_io.getvalue()


def try_texture(pool: SnapshotPool, tag: str) -> dict:
    attempts = []
    for hc in pool.candidates(tag, expected_types=HEADER_TYPES):
        if not hc.get('ok'):
            attempts.append({'header_candidate': {k: v for k, v in hc.items() if k not in ('view', 'entry', 'payload')}})
            continue
        hd = hc['desc']
        try:
            hinfo = decode_header(hc['payload'])
        except Exception as ex:
            attempts.append({'header': hd, 'error_stage': 'decode_header', 'error': repr(ex)})
            continue
        stream_tag = hc['entry']['reference'].upper()
        smax = child_max_patch(tag, hc['patch_id'], stream_tag)
        stream_had_candidate = False
        for sc in pool.candidates(stream_tag, max_patch=smax):
            stream_had_candidate = True
            if not sc.get('ok'):
                attempts.append({'header': hd, 'stream_candidate': {k: v for k, v in sc.items() if k not in ('view', 'entry', 'payload')}})
                continue
            sd = sc['desc']
            backing_tag = sc['entry']['reference'].upper()
            bmax = child_max_patch(stream_tag, sc['patch_id'], backing_tag)
            if pool.any_entry_exists(backing_tag, max_patch=bmax):
                backing_candidates = pool.candidates(backing_tag, max_patch=bmax)
            else:
                # Matches d1_texture_export: if the stream's reference is not a
                # resolvable FileHash, the stream payload itself is the backing.
                backing_candidates = iter([{
                    'ok': True,
                    'patch_id': sc['patch_id'],
                    'entry': sc['entry'],
                    'payload': sc['payload'],
                    'desc': {**sd, 'fallback': 'stream payload used as backing because serialized reference is not a catalog FileHash'},
                }])
            for bc in backing_candidates:
                if not bc.get('ok'):
                    attempts.append({'header': hd, 'stream': sd, 'backing_candidate': {k: v for k, v in bc.items() if k not in ('view', 'entry', 'payload')}})
                    continue
                bd = bc['desc']
                try:
                    rendered, dds, png = render_texture(tag, hc['payload'], bc['payload'])
                except Exception as ex:
                    attempts.append({'header': hd, 'stream': sd, 'backing': bd, 'error_stage': 'render', 'error': repr(ex)})
                    continue
                return {
                    'resolved': True,
                    'header': tag,
                    'header_entry': hd,
                    'stream': stream_tag,
                    'stream_entry': sd,
                    'backing': bd['tag_hash'],
                    'backing_entry': bd,
                    'header_info': hinfo,
                    'rendered': rendered,
                    '_dds': dds,
                    '_png': png,
                    'attempt_count_before_success': len(attempts),
                    'attempts': attempts,
                }
        if not stream_had_candidate:
            attempts.append({'header': hd, 'error_stage': 'stream_lookup', 'error': f'{stream_tag} has no candidate package snapshot'})
    return {'resolved': False, 'header': tag, 'attempts': attempts}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--plate-report', type=Path)
    ap.add_argument('--tag-hash', action='append', default=[])
    ap.add_argument('--member-catalog', type=Path, action='append', required=True)
    ap.add_argument('--base-url', required=True)
    ap.add_argument('--part-count', type=int, default=10)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()

    wanted = []
    if a.plate_report:
        src = json.loads(a.plate_report.read_text())
        for raw in src.get('source_texture_hashes', []):
            h = norm(raw)
            if h not in wanted:
                wanted.append(h)
    for raw in a.tag_hash:
        h = norm(raw)
        if h not in wanted:
            wanted.append(h)
    if not wanted:
        raise SystemExit('no texture hashes requested')

    catalogs = load_catalogs(a.member_catalog)
    base = a.base_url.rstrip('/')
    archive = SplitHttpTar([f'{base}/packages.tar.{i:03d}' for i in range(1, a.part_count + 1)], retries=6, timeout=90)
    pool = SnapshotPool(archive, catalogs, a.runtime)
    a.out.mkdir(parents=True, exist_ok=True)

    rows = []
    failures = []
    for i, tag in enumerate(wanted, 1):
        rec = try_texture(pool, tag)
        if not rec.get('resolved'):
            failures.append(rec)
            print('GENSAFE_FAILURE', tag, 'attempts', len(rec.get('attempts', [])), flush=True)
            for x in rec.get('attempts', [])[-12:]:
                print(' ', json.dumps(x, sort_keys=True), flush=True)
            continue
        rendered = rec.pop('rendered')
        dds = rec.pop('_dds')
        png = rec.pop('_png')
        stem = rendered.pop('stem')
        dds_name = stem + '.dds'
        png_name = stem + '.png'
        (a.out / dds_name).write_bytes(dds)
        (a.out / png_name).write_bytes(png)
        row = {
            **rec,
            **rendered,
            'dds': dds_name,
            'png': png_name,
            'png_error': None,
            'owner_package': rec['header_entry']['snapshot'],
            'stream_package': rec['stream_entry']['snapshot'],
            'backing_package': rec['backing_entry']['snapshot'],
        }
        rows.append(row)
        print('GENSAFE_TEXTURE', f'{i}/{len(wanted)}', tag,
              'header', rec['header_entry']['snapshot'],
              'stream', rec['stream_entry']['snapshot'],
              'backing', rec['backing_entry']['snapshot'],
              'fallback_attempts', rec['attempt_count_before_success'], flush=True)

    manifest = {
        'schema': 'd1_remote_texture_export_generation_safe/v1',
        'requested_texture_hashes': wanted,
        'requested_count': len(wanted),
        'resolved_count': len(rows),
        'failed_count': len(failures),
        'missing_requested': [x['header'] for x in failures],
        'textures': rows,
        'failures': failures,
        'catalog_package_ids': [f'{x:04X}' for x in sorted(catalogs)],
        'policy': (
            'Each requested FileHash is resolved by complete readable/decodable texture chain across verified physical snapshots, newest to oldest. '
            'Same-package child references may not use a newer snapshot than their selected parent. No filename-neighbor inference or silent resampling is used.'
        ),
    }
    (a.out / 'remote_texture_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({k: v for k, v in manifest.items() if k not in ('textures', 'failures')}, indent=2), flush=True)
    if failures:
        raise SystemExit(f"generation-safe remote texture export failed for {len(failures)}/{len(wanted)} textures")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
