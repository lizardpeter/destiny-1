#!/usr/bin/env python3
"""Resolve exact D1 PS4 s_entity records and their serialized Resource[] children.

For every requested FileHash this source-proof tool:
- validates class 0x80800734,
- decodes the validated Resource[] array,
- resolves every child FileHash through the verified universal member catalog,
- parses child EntityResources with the validated PS4 parser,
- exposes exact semantic roles, source-mapped name fields and embedded models,
- source-closes skeleton node counts/hashes for entity_skeleton resources,
- source-closes serialized child EntitySK arrays for entity_children resources,
- resolves embedded model metadata without inferring ownership from locality,
  adjacency, naming, package names, or appearance.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from d1_crota_raid_candidate_probe import LazyExactHashResolver, meta_row, norm
from d1_entity_resource_probe import ENTITY_RESOURCE_CLASS, parse_resource
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_entity_child_find import parse_children_resource
from d1_remote_s_entity_resource_package_find import S_ENTITY_REF, parse_entity_resources
from d1_skeleton_probe import parse_skeleton_resource
from d1_split_tar_extract import SplitHttpTar

ENTITY_MODEL_CLASS = '80801AB5'


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--tag-hash', action='append', required=True)
    ap.add_argument('--member-catalog', action='append', type=Path, required=True)
    ap.add_argument('--base-url', required=True)
    ap.add_argument('--part-count', type=int, default=10)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('-o', '--output', type=Path, required=True)
    a = ap.parse_args()

    catalogs = load_catalogs(a.member_catalog)
    base = a.base_url.rstrip('/')
    arc = SplitHttpTar(
        [f'{base}/packages.tar.{i:03d}' for i in range(1, a.part_count + 1)],
        retries=6,
        timeout=90,
    )
    resolver = LazyExactHashResolver(arc, catalogs, a.runtime)

    entries = []
    violations = []

    for requested in a.tag_hash:
        h = norm(requested)
        row = {'tag_hash': h, 'violations': []}
        try:
            view, e = resolver.locate(h)
            row['package_id'] = f'{((int(h,16)-0x80800000)>>13)&0x7ff:04X}'
            row['logical_view'] = view.view.name
            row['entry'] = meta_row(e)
            if e['reference'].upper() != S_ENTITY_REF:
                raise ValueError(f'{h}: expected s_entity {S_ENTITY_REF}, got {e["reference"].upper()}')
            payload = view.entry(e['index'])
            row['payload_sha256'] = hashlib.sha256(payload).hexdigest()
            row['payload_size'] = len(payload)
            raw_resources = parse_entity_resources(payload)
            row['resource_count'] = len(raw_resources)
            resolved_resources = []

            for rr in raw_resources:
                rrow = dict(rr)
                rh = norm(rr['resource_hash'])
                if rh in ('00000000', 'FFFFFFFF'):
                    rrow['resolution_status'] = 'null_or_sentinel'
                    resolved_resources.append(rrow)
                    continue
                try:
                    rv, re = resolver.locate(rh)
                    rrow['resolution_status'] = 'resolved_exact'
                    rrow['entry'] = meta_row(re)
                    ref = re['reference'].upper()
                    if ref == ENTITY_RESOURCE_CLASS and re['type'] == 16 and re['subtype'] == 0:
                        child_payload = rv.entry(re['index'])
                        parsed = parse_resource(child_payload, 'PS4')
                        er = {
                            'semantic_role': parsed.get('semantic_role'),
                            'unk10_class': (parsed.get('unk10') or {}).get('class_hash'),
                            'unk18_class': (parsed.get('unk18') or {}).get('class_hash'),
                            'embedded_model_tag_hash': parsed.get('embedded_model_tag_hash'),
                            'model_field_offset_in_parent': parsed.get('model_field_offset_in_parent'),
                            'entity_name_string_hash': parsed.get('entity_name_string_hash'),
                            'entity_name_tag_hash': parsed.get('entity_name_tag_hash'),
                            'entity_name_tag_expected_class': parsed.get('entity_name_tag_expected_class'),
                            'generic_name_tag_field_offset_in_parent': parsed.get('generic_name_tag_field_offset_in_parent'),
                        }
                        rrow['entity_resource'] = er
                        model = er.get('embedded_model_tag_hash')
                        if model and norm(model) not in ('00000000', 'FFFFFFFF'):
                            mh = norm(model)
                            try:
                                _mv, me = resolver.locate(mh)
                                rrow['embedded_model_entry'] = meta_row(me)
                                if me['reference'].upper() != ENTITY_MODEL_CLASS:
                                    rrow['embedded_model_class_violation'] = (
                                        f'expected {ENTITY_MODEL_CLASS}, got {me["reference"].upper()}'
                                    )
                            except Exception as ex:
                                rrow['embedded_model_resolution_error'] = repr(ex)
                        if er.get('semantic_role') == 'entity_skeleton':
                            try:
                                sk = parse_skeleton_resource(child_payload)
                                info = sk['skeleton_info']
                                rrow['skeleton'] = {
                                    'node_count': int(info['node_hierarchy']['count']),
                                    'bone_hashes': [x['node_hash'] for x in info.get('bones', [])],
                                }
                            except Exception as ex:
                                rrow['skeleton_parse_error'] = repr(ex)
                        if er.get('semantic_role') == 'entity_children':
                            try:
                                ch = parse_children_resource(child_payload)
                                if ch is None:
                                    raise ValueError('entity_children role did not satisfy validated children parser')
                                rrow['entity_children'] = ch
                            except Exception as ex:
                                rrow['entity_children_parse_error'] = repr(ex)
                    elif ref == ENTITY_MODEL_CLASS:
                        rrow['direct_entity_model'] = True
                except Exception as ex:
                    rrow['resolution_status'] = 'resolution_error'
                    rrow['resolution_error'] = repr(ex)
                resolved_resources.append(rrow)

            row['resources'] = resolved_resources
            row['embedded_models'] = sorted({
                norm((r.get('entity_resource') or {}).get('embedded_model_tag_hash'))
                for r in resolved_resources
                if (r.get('entity_resource') or {}).get('embedded_model_tag_hash')
                and norm((r.get('entity_resource') or {}).get('embedded_model_tag_hash')) not in ('00000000', 'FFFFFFFF')
            } | {
                norm(r['resource_hash']) for r in resolved_resources if r.get('direct_entity_model')
            })
            row['skeletons'] = [
                {'resource_hash': norm(r['resource_hash']), **r['skeleton']}
                for r in resolved_resources if r.get('skeleton')
            ]
            row['specific_name_string_hashes'] = sorted({
                norm((r.get('entity_resource') or {}).get('entity_name_string_hash'))
                for r in resolved_resources
                if (r.get('entity_resource') or {}).get('entity_name_string_hash')
            })
            row['generic_name_tags'] = sorted({
                norm((r.get('entity_resource') or {}).get('entity_name_tag_hash'))
                for r in resolved_resources
                if (r.get('entity_resource') or {}).get('entity_name_tag_hash')
            })
            row['child_entities'] = [
                {'resource_hash': norm(r['resource_hash']), **c}
                for r in resolved_resources
                for c in ((r.get('entity_children') or {}).get('children') or [])
                if c.get('entity_hash') not in ('00000000', 'FFFFFFFF')
            ]
        except Exception as ex:
            msg = repr(ex)
            row['violations'].append(msg)
            violations.append({'tag_hash': h, 'error': msg})
        entries.append(row)

    report = {
        'schema': 'd1_remote_exact_s_entity_probe/v3',
        'status': 'D1_EXACT_S_ENTITY_PROBE' if not violations else 'D1_EXACT_S_ENTITY_PROBE_WITH_VIOLATIONS',
        'entries': entries,
        'violation_count': len(violations),
        'violations': violations,
        'policy': (
            'Every child edge comes from validated s_entity/EntityChildren serialization and exact FileHash routing. '
            'EntityResource roles, source-mapped name fields and embedded models come only from the validated PS4 parser; '
            'skeleton metadata comes only from the validated skeleton parser. No locality, adjacency, appearance, '
            'package-name, or semantic-name heuristics are used.'
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2) + '\n')

    for x in entries:
        print('S_ENTITY', x['tag_hash'], 'ENTRY', x.get('entry'), 'RESOURCES', x.get('resource_count'),
              'MODELS', x.get('embedded_models'),
              'SKELETONS', [(s['resource_hash'], s['node_count']) for s in x.get('skeletons', [])],
              'SPECIFIC_NAMES', x.get('specific_name_string_hashes'),
              'GENERIC_NAME_TAGS', x.get('generic_name_tags'),
              'CHILDREN', [(c['resource_hash'], c['entity_hash']) for c in x.get('child_entities', [])],
              'VIOLATIONS', x.get('violations'))
        for rr in x.get('resources', []):
            e = rr.get('entry') or {}
            er = rr.get('entity_resource') or {}
            sk = rr.get('skeleton') or {}
            ch = rr.get('entity_children') or {}
            print('  RESOURCE', rr.get('resource_index'), rr.get('resource_hash'),
                  'REF', e.get('reference'), 'ROLE', er.get('semantic_role'),
                  'CLASSES', (er.get('unk10_class'), er.get('unk18_class')),
                  'MODEL', er.get('embedded_model_tag_hash'), 'SKEL_NODES', sk.get('node_count'),
                  'SPECIFIC_NAME', er.get('entity_name_string_hash'), 'GENERIC_NAME_TAG', er.get('entity_name_tag_hash'),
                  'CHILD_COUNT', ch.get('child_count'))
    print('STATUS', report['status'], 'VIOLATIONS', report['violations'])
    return 0 if not violations else 2


if __name__ == '__main__':
    raise SystemExit(main())
