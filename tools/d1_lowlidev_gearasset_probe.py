#!/usr/bin/env python3
"""Probe lowlines' historical D1 GearAsset manifest mirror by exact item hash.

lowlines documented this endpoint in 2018 as a testing endpoint backed by the D1
manifest and intentionally shaped like Bungie's former D1 GearAsset response:

    https://lowlidev.com.au/destiny/api/gearasset/{itemHash}?destiny

This tool treats the service only as a historical *secondary evidence source*.
Nothing is promoted merely because the mirror returns it. The exact requestedId,
gear ``reference_id``, explicitly selected content platform, filenames, hashes and
response bytes are preserved so they can be cross-checked against proven retail
PS4 data.

Geometry download URL provenance is lowlines/destiny-tgx-loader at commit
``a40ac48ca27b5ad4c2e437616f8cc65137ad6b8a``:

    contentpath+'/geometry/platform/'+platform+'/geometry/'+geometry

No nearby item, class substitute, visual match, guessed default armor, implicit
platform fallback, or unselected geometry file is used.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import urllib.error
import urllib.request
from pathlib import Path

from d1_bungie_web_gearasset_probe import geometry_ids, index_sets, selected

BASE = 'https://lowlidev.com.au'
BUNGIE_CONTENT = 'https://www.bungie.net/common/destiny_content'
GEAR_ROOT = f'{BUNGIE_CONTENT}/geometry/gear'
UA = 'd1-reversal-evidence/1.0 (+https://github.com/lizardpeter/destiny-1)'


def get(url: str) -> tuple[int, dict, bytes, str | None]:
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': 'application/json,*/*'})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return int(getattr(r, 'status', 200)), dict(r.headers.items()), r.read(), None
    except urllib.error.HTTPError as e:
        return int(e.code), dict(e.headers.items()), e.read(), f'HTTPError:{e.code}'
    except Exception as e:
        return 0, {}, b'', f'{type(e).__name__}:{e}'


def parse_hash(s: str) -> int:
    s = s.strip()
    return (int(s, 16) if s.lower().startswith('0x') or any(c in 'abcdefABCDEF' for c in s) else int(s, 10)) & 0xffffffff


def exact_platform_content(ga: dict, platform: str) -> dict:
    rows = [x for x in (ga.get('content') or []) if isinstance(x, dict) and x.get('platform') == platform]
    if len(rows) != 1:
        available = [x.get('platform') for x in (ga.get('content') or []) if isinstance(x, dict)]
        raise ValueError(f'exact GearAsset platform={platform!r} count {len(rows)}; available={available!r}')
    return rows[0]


def download_selected_tgxm(files: dict, platform: str, output_dir: Path) -> list[dict]:
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for entry in files.get('geometry') or []:
        index = int(entry['index'])
        name = str(entry['file_name'])
        if Path(name).name != name or not name.lower().endswith('.tgxm'):
            raise ValueError(f'unsafe/non-TGXM selected geometry filename {name!r}')
        url = f'{BUNGIE_CONTENT}/geometry/platform/{platform}/geometry/{name}'
        status, headers, body, transport_error = get(url)
        if status != 200:
            raise ValueError(f'exact selected geometry {name} HTTP {status} transport={transport_error}')
        path = output_dir / name
        path.write_bytes(body)
        rows.append({
            'index': index,
            'file_name': name,
            'url': url,
            'http_status': status,
            'content_type': headers.get('Content-Type'),
            'size': len(body),
            'sha256': hashlib.sha256(body).hexdigest(),
        })
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--item-hash', action='append', required=True)
    ap.add_argument('--class-hash', type=lambda x: int(x, 0), default=3655393761)
    ap.add_argument('--female', action='store_true')
    ap.add_argument('--platform', choices=('web', 'mobile'), required=True)
    ap.add_argument('--download-dir', type=Path)
    ap.add_argument('--download-tgxm-dir', type=Path)
    ap.add_argument('-o', '--output', type=Path, required=True)
    a = ap.parse_args()

    rows = []
    failures = []
    for item in [parse_hash(x) for x in a.item_hash]:
        url = f'{BASE}/destiny/api/gearasset/{item}?destiny'
        status, headers, body, transport_error = get(url)
        row = {
            'item_hash_decimal': item,
            'item_hash_hex': f'{item:08X}',
            'endpoint_url': url,
            'http_status': status,
            'transport_error': transport_error,
            'response_size': len(body),
            'response_sha256': hashlib.sha256(body).hexdigest(),
            'content_type': headers.get('Content-Type'),
            'requested_platform': a.platform,
        }
        if a.download_dir:
            a.download_dir.mkdir(parents=True, exist_ok=True)
            (a.download_dir / f'{item}_response.bin').write_bytes(body)
        try:
            if status != 200:
                raise ValueError(f'HTTP {status}')
            obj = json.loads(body.decode('utf-8-sig'))
            if not isinstance(obj, dict) or not isinstance(obj.get('gearAsset'), dict):
                raise ValueError('response is not exact D1 GearAsset-shaped JSON')
            requested = int(str(obj.get('requestedId')))
            if requested != item:
                raise ValueError(f'requestedId mismatch {requested} != {item}')
            ga = obj['gearAsset']
            content = exact_platform_content(ga, a.platform)
            sets = index_sets(content, a.female)
            files = selected(content, sets)
            gear_rows = []
            for gear_name in ga.get('gear') or []:
                gear_url = f'{GEAR_ROOT}/{gear_name}'
                gs, gh, gb, ge = get(gear_url)
                if gs != 200:
                    raise ValueError(f'exact gear file {gear_name} HTTP {gs} transport={ge}')
                gear = json.loads(gb.decode('utf-8-sig'))
                reference = int(str(gear.get('reference_id')))
                if reference != item:
                    raise ValueError(f'{gear_name}: reference_id {reference} != requested item {item}')
                geometry, art_evidence = geometry_ids(gear, a.class_hash, a.female)
                if a.download_dir:
                    (a.download_dir / gear_name).write_bytes(gb)
                gear_rows.append({
                    'file_name': gear_name,
                    'url': gear_url,
                    'size': len(gb),
                    'sha256': hashlib.sha256(gb).hexdigest(),
                    'reference_id': reference,
                    'geometry_identifiers': geometry,
                    'art_selection': art_evidence,
                    'default_dye_count': len(gear.get('default_dyes') or []),
                    'locked_dye_count': len(gear.get('locked_dyes') or []),
                    'custom_dye_count': len(gear.get('custom_dyes') or []),
                })

            tgxm_rows = []
            if a.download_tgxm_dir:
                tgxm_rows = download_selected_tgxm(
                    files,
                    a.platform,
                    a.download_tgxm_dir / f'{item:08X}',
                )

            row.update({
                'requested_id': requested,
                'gearasset': ga,
                'selected_platform': content.get('platform'),
                'platform_index_sets': sets,
                'platform_selected_files': files,
                'gear_json': gear_rows,
                'downloaded_selected_tgxm': tgxm_rows,
                'exact_requested_id_match': True,
                'all_gear_reference_ids_match': all(x['reference_id'] == item for x in gear_rows),
            })
        except Exception as ex:
            row['parse_error'] = repr(ex)
            failures.append(row['item_hash_hex'])
        rows.append(row)
        print(row['item_hash_hex'], 'HTTP', status, 'bytes', len(body), 'platform', a.platform, 'transport', transport_error, 'parse', row.get('parse_error'))
        if row.get('gear_json'):
            print(' gear', [(x['file_name'], x['reference_id'], x['geometry_identifiers']) for x in row['gear_json']])
            print(' selected geometry', [(x['index'], x['file_name']) for x in row['platform_selected_files']['geometry']])
            if row.get('downloaded_selected_tgxm'):
                print(' downloaded TGXM', [(x['index'], x['file_name'], x['size'], x['sha256']) for x in row['downloaded_selected_tgxm']])

    report = {
        'schema': 'd1_lowlidev_gearasset_probe/v3',
        'source': 'lowlines historical D1 manifest testing endpoint documented in Porting Bungie Spasm to Three.js (2018)',
        'geometry_url_provenance': 'lowlines/destiny-tgx-loader a40ac48ca27b5ad4c2e437616f8cc65137ad6b8a: contentpath/geometry/platform/{platform}/geometry/{geometry}',
        'class_hash': a.class_hash,
        'is_female': a.female,
        'requested_platform': a.platform,
        'items': rows,
        'failure_item_hashes': failures,
        'promotion_policy': 'Secondary evidence only. Exact requestedId, explicitly selected platform, gear reference_id, and exact selected index-set filenames are required. Returned geometry must still be cross-checked against independent retail PS4 evidence before promotion.',
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2) + '\n')
    return 0 if not failures else 4


if __name__ == '__main__':
    raise SystemExit(main())
