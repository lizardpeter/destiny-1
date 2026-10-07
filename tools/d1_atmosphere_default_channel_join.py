#!/usr/bin/env python3
"""Join exact retail atmosphere producer keys to pinned RenderGlobals defaults.

Serialized defaults are not live sequencer results. This closes source indices
and initial vectors only; it must not replace atmosphere LUT/runtime ownership.
"""
import argparse
import hashlib
import json
from pathlib import Path
from d1_atmosphere_producer_contract import contract

def join(eboot, defaults_path):
    producer = contract(eboot)
    raw = defaults_path.read_bytes()
    defaults = json.loads(raw)
    if defaults['tag_hash'] != '80AE4005' or defaults['payload_sha256'] != '83e902c1f298596039911e190fec831dd1afd9faff991a7eec236c87296441af':
        raise ValueError('unexpected source defaults witness')
    channels = {row['string_hash']: row for row in defaults['channels']}
    if len(channels) != len(defaults['channels']):
        raise ValueError('ambiguous default channel hashes')
    rows = []
    missing = []
    for mapping in producer['channel_mappings_before_coefficient_transforms']:
        source = channels.get(mapping['hash_hex'])
        if source is None:
            missing.append(mapping)
            continue
        rows.append({**mapping, 'global_channel_index': source['index'],
                     'serialized_default_vec4': source['default_vec4']})
    return {'schema': 'd1-atmosphere-default-channel-join-v1',
            'eboot_sha256': producer['sha256'], 'defaults_tag': defaults['tag_hash'],
            'defaults_payload_sha256': defaults['payload_sha256'],
            'defaults_evidence_sha256': hashlib.sha256(raw).hexdigest(),
            'mappings': rows, 'missing_source_keys': missing, 'producer_instructions': producer['instructions'],
            'scope': 'Exact source index/default join only. Live channel overrides, map settings/LUT owner, coefficient transforms, and render validation remain open.'}

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('eboot', type=Path)
    ap.add_argument('--defaults', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    result = join(args.eboot, args.defaults)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print('source-exact atmosphere channel/default joins', len(result['mappings']))
