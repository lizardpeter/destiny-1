#!/usr/bin/env python3
"""Extract exact D1 PS4 native GCN shader code from the universal retail corpus.

This is the remote-corpus counterpart of ``d1_ps4_shader_binary_probe.py``.
The D1 shader header and its FileEntry.Reference native payload are both resolved
through the exact universal member catalog. OrbShdr metadata bounds the machine
code. Both the D1 PS4 pixel-shader header family (type 32/subtype 8) and the
vertex-shader header family (type 32/subtype 9) are accepted, with the native
OrbShdr stage required to agree with the serialized header subtype. No shader
semantics are inferred.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_activity_placements import RemoteCorpus
from d1_split_tar_extract import SplitHttpTar
from d1_ps4_shader_binary_probe import find_footer, parse_binary_info, parse_usage

NULLS = {'00000000', 'FFFFFFFF'}
HEADER_STAGE = {
    (32, 8): ('PS', 'PixelShader'),
    (32, 9): ('VS', 'VertexShader'),
}


def norm(v: object) -> str:
    return str(v).upper().removeprefix('0X').zfill(8)


def digest(b: bytes | None) -> dict:
    return {'bytes': None if b is None else len(b), 'sha256': None if b is None else hashlib.sha256(b).hexdigest()}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--shader', action='append', required=True)
    ap.add_argument('--member-catalog', type=Path, action='append', required=True)
    ap.add_argument('--base-url', required=True)
    ap.add_argument('--part-count', type=int, default=10)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('--out-dir', type=Path, required=True)
    ap.add_argument('--report', type=Path, required=True)
    a = ap.parse_args()

    catalogs = load_catalogs(a.member_catalog)
    base = a.base_url.rstrip('/')
    arc = SplitHttpTar([f'{base}/packages.tar.{i:03d}' for i in range(1, a.part_count + 1)], retries=6, timeout=90)
    c = RemoteCorpus(arc, catalogs, a.runtime)
    a.out_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    violations = []
    for shader in sorted({norm(x) for x in a.shader}):
        row = {'shader': shader, 'violations': []}
        hm = c.entry_meta(shader)
        row['header_meta'] = hm
        stage_spec = None
        if hm is None:
            row['violations'].append('header_meta_unavailable')
        else:
            key = (hm.get('type'), hm.get('subtype'))
            stage_spec = HEADER_STAGE.get(key)
            if stage_spec is None:
                row['violations'].append(f'unsupported_header_type_subtype:{key[0]}:{key[1]}')
            else:
                row['header_stage_prefix'], row['header_stage'] = stage_spec

        try:
            hb, hsrc = c.payload(shader)
        except Exception as ex:
            hb = None; hsrc = None; row['violations'].append('header_payload:' + repr(ex))
        row['header_source'] = hsrc
        row['header_payload'] = digest(hb)

        ref = norm((hm or {}).get('reference', 'FFFFFFFF'))
        row['native_payload_hash'] = ref
        if ref in NULLS:
            row['violations'].append('native_payload_reference_null')
            pb = None; psrc = None
        else:
            pm = c.entry_meta(ref); row['native_payload_meta'] = pm
            if pm is not None and stage_spec is not None:
                expected_subtype = hm.get('subtype')
                if (pm.get('type'), pm.get('subtype')) != (1, expected_subtype):
                    row['violations'].append(
                        f'native_payload_type_subtype:{pm.get("type")}:{pm.get("subtype")}!=1:{expected_subtype}'
                    )
            try:
                pb, psrc = c.payload(ref)
            except Exception as ex:
                pb = None; psrc = None; row['violations'].append('native_payload:' + repr(ex))
            row['native_payload_source'] = psrc
            row['native_payload'] = digest(pb)

        if hb is not None:
            hp = a.out_dir / f'{shader}_header.bin'; hp.write_bytes(hb); row['header_file'] = str(hp)
        if pb is not None:
            np = a.out_dir / f'{ref}_native_shader.bin'; np.write_bytes(pb); row['native_payload_file'] = str(np)
            footer, checks = find_footer(pb); row['orbshdr_locator'] = checks
            if footer is None:
                row['violations'].append('orbshdr_footer_unresolved')
            else:
                try:
                    info = parse_binary_info(pb, footer); row['binary_info'] = info
                    usage = parse_usage(pb, footer, info); row['usage'] = usage
                    if stage_spec is not None and info.get('stage') != stage_spec[1]:
                        row['violations'].append(f'orbshdr_stage:{info.get("stage")}!={stage_spec[1]}')
                    n = int(info['code_length_bytes'])
                    if n <= 0 or n > footer or n > len(pb):
                        row['violations'].append(f'invalid_code_length:{n}:footer={footer}:payload={len(pb)}')
                    else:
                        code = pb[:n]
                        prefix = stage_spec[0] if stage_spec is not None else 'UNK'
                        cp = a.out_dir / f'{prefix}_{shader}_gcn.bin'; cp.write_bytes(code)
                        row['code_file'] = str(cp); row['code'] = digest(code)
                except Exception as ex:
                    row['violations'].append('orbshdr_parse:' + repr(ex))
        if row['violations']:
            violations.extend(f'{shader}:{x}' for x in row['violations'])
        rows.append(row)

    out = {
        'schema': 'd1_remote_ps4_shader_extract/v2',
        'status': 'D1_REMOTE_PS4_SHADER_EXTRACT_COMPLETE' if not violations else 'D1_REMOTE_PS4_SHADER_EXTRACT_WITH_VIOLATIONS',
        'shader_count': len(rows),
        'pixel_shader_count': sum(r.get('header_stage') == 'PixelShader' for r in rows),
        'vertex_shader_count': sum(r.get('header_stage') == 'VertexShader' for r in rows),
        'shaders': rows,
        'violations': violations,
        'policy': 'Shader headers and referenced native payloads are exact retail FileEntry resources. Header subtype, referenced native subtype, and OrbShdr stage must agree. GCN code bounds come only from validated OrbShdr metadata; no semantic instruction interpretation occurs here.'
    }
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(out, indent=2) + '\n')
    print('STATUS', out['status'], 'SHADERS', len(rows), 'PS', out['pixel_shader_count'], 'VS', out['vertex_shader_count'], 'VIOLATIONS', len(violations))
    for r in rows:
        print(r['shader'], r.get('header_stage'), r.get('native_payload_hash'), (r.get('code') or {}).get('bytes'), (r.get('code') or {}).get('sha256'))
    return 0 if not violations else 2


if __name__ == '__main__':
    raise SystemExit(main())
