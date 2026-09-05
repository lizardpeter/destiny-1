#!/usr/bin/env python3
"""Resolve playable D1 Guardian final entities into their exact render resources.

Consumes d1_playable_guardian_parent_resolve/v1 and follows each serialized
EntityDataROI FileHash.  For concrete s_entity records it decodes the retail
Resource[] array, resolves those FileHashes against verified package-member
catalogs, parses EntityResource roles, and follows entity-model resources to the
embedded s_entity_model FileHash.

This stage deliberately keeps investment presentation names separate from the
binary graph.  A named item's class/body-role is inherited only from the prior
retail art-arrangement join; every entity/resource/model edge here comes from
package bytes.
"""
from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from d1_investment_arrangement_probe import filehash_pkg_index
from d1_remote_investment_parent_probe import Member, RemoteLogicalPackage
from d1_remote_s_entity_resource_package_find import S_ENTITY_REF, parse_entity_resources
from d1_entity_resource_probe import ENTITY_RESOURCE_CLASS, parse_resource
from d1_split_tar_extract import SplitHttpTar

ENTITY_MODEL_CLASS = '80801AB5'


def load_catalogs(paths: list[Path]) -> dict[int, dict[int, Member]]:
    out: dict[int, dict[int, Member]] = {}
    for path in paths:
        src = json.loads(path.read_text())
        for key, rows in src.get('families', {}).items():
            pkg = int(key, 16)
            fam = out.setdefault(pkg, {})
            for row in rows:
                name = row['name']
                patch = int(name.rsplit('_', 1)[1].split('.', 1)[0])
                m = Member(name, int(str(row['data_offset']), 0), int(row['size']), pkg, patch)
                prev = fam.get(patch)
                if prev is not None and prev != m:
                    raise ValueError(f'conflicting member catalog row for {pkg:04X} patch {patch}')
                fam[patch] = m
    return out


def entry_meta(view: RemoteLogicalPackage, tag: str) -> dict:
    pkg, idx = filehash_pkg_index(int(tag, 16))
    if pkg != int(view.h['pkg_id']):
        return {'resolved': False, 'reason': f'tag belongs to package {pkg:04X}, view is {int(view.h["pkg_id"]):04X}'}
    if idx >= len(view.entries):
        return {'resolved': False, 'reason': 'file index outside entry table', 'file_index': idx}
    e = view.entries[idx]
    if e['tag_hash'].upper() != tag.upper():
        return {'resolved': False, 'reason': f"logical tag mismatch {e['tag_hash']}", 'file_index': idx}
    return {
        'resolved': True,
        'file_index': idx,
        'reference': e['reference'].upper(),
        'type': e['type'],
        'subtype': e['subtype'],
        'size': e['file_size'],
        'logical_view': view.view.name,
    }


def resolve_model(tag: str, views: dict[int, RemoteLogicalPackage]) -> dict:
    pkg, idx = filehash_pkg_index(int(tag, 16))
    out = {'tag_hash': tag.upper(), 'package_id': pkg, 'file_index': idx}
    v = views.get(pkg)
    if v is None:
        return {**out, 'resolved': False, 'reason': 'package not present in supplied member catalogs'}
    return {**out, **entry_meta(v, tag)}


def resolve_resource(row: dict, views: dict[int, RemoteLogicalPackage]) -> dict:
    tag = row['resource_hash'].upper()
    pkg = row.get('resource_package_id')
    idx = row.get('resource_file_index')
    out = {**row}
    if pkg is None or idx is None:
        return {**out, 'resolved': False, 'reason': 'null resource FileHash'}
    v = views.get(int(pkg))
    if v is None:
        return {**out, 'resolved': False, 'reason': 'resource package not present in supplied member catalogs'}
    meta = entry_meta(v, tag)
    out.update(meta)
    if not meta.get('resolved'):
        return out
    try:
        if meta['reference'] == ENTITY_RESOURCE_CLASS:
            payload = v.entry(idx)
            parsed = parse_resource(payload, v.h['platform'])
            out['entity_resource'] = parsed
            out['semantic_role'] = parsed.get('semantic_role')
            model = parsed.get('embedded_model_tag_hash')
            if model and model not in ('00000000', 'FFFFFFFF'):
                out['embedded_model'] = resolve_model(model, views)
        elif meta['reference'] == ENTITY_MODEL_CLASS:
            out['semantic_role'] = 'direct_entity_model'
            out['embedded_model'] = resolve_model(tag, views)
        else:
            out['semantic_role'] = 'other_direct_resource'
    except Exception as ex:
        out['parse_error'] = repr(ex)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('entity_resolution', type=Path)
    ap.add_argument('--member-catalog', type=Path, action='append', required=True)
    ap.add_argument('--base-url', required=True)
    ap.add_argument('--part-count', type=int, default=10)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('-o', '--output', type=Path, required=True)
    a = ap.parse_args()

    src = json.loads(a.entity_resolution.read_text())
    catalogs = load_catalogs(a.member_catalog)
    base = a.base_url.rstrip('/')
    arc = SplitHttpTar([f'{base}/packages.tar.{i:03d}' for i in range(1, a.part_count + 1)], retries=6, timeout=90)
    views = {pkg: RemoteLogicalPackage(arc, fam, a.runtime) for pkg, fam in sorted(catalogs.items())}

    entity_context: dict[str, list[dict]] = collections.defaultdict(list)
    for arr in src.get('arrangements', []):
        for branch in arr.get('resolved_body_assignments', []):
            tag = branch.get('entity_data_hash')
            if not tag:
                continue
            entity_context[tag.upper()].append({
                'className': arr.get('className'),
                'arrangement_index': arr.get('arrangement_index'),
                'body_role': branch.get('body_role'),
                'parent_hash': branch.get('parent_hash'),
                'examples': arr.get('examples', []),
            })

    entities = {}
    resource_pkg_counts = collections.Counter()
    role_counts = collections.Counter()
    model_pkg_counts = collections.Counter()
    errors = []

    for tag in sorted(entity_context):
        pkg, idx = filehash_pkg_index(int(tag, 16))
        rec = {
            'entity_hash': tag, 'package_id': pkg, 'file_index': idx,
            'contexts': entity_context[tag],
        }
        v = views.get(pkg)
        if v is None:
            rec.update({'resolved': False, 'reason': 'entity package not present in supplied member catalogs'})
            entities[tag] = rec
            continue
        meta = entry_meta(v, tag)
        rec.update(meta)
        if not meta.get('resolved'):
            entities[tag] = rec
            continue
        if meta['reference'] != S_ENTITY_REF:
            rec['resolved'] = True
            rec['is_s_entity'] = False
            rec['reason'] = f"final EntityDataROI reference is {meta['reference']}, not {S_ENTITY_REF}"
            entities[tag] = rec
            continue
        try:
            payload = v.entry(idx)
            raw_resources = parse_entity_resources(payload)
            resources = [resolve_resource(x, views) for x in raw_resources]
            rec.update({'resolved': True, 'is_s_entity': True, 'resource_count': len(resources), 'resources': resources})
            for x in resources:
                if x.get('resource_package_id') is not None:
                    resource_pkg_counts[f"{int(x['resource_package_id']):04X}"] += 1
                if x.get('semantic_role'):
                    role_counts[x['semantic_role']] += 1
                m = x.get('embedded_model') or {}
                if m.get('resolved'):
                    model_pkg_counts[f"{int(m['package_id']):04X}"] += 1
        except Exception as ex:
            rec['parse_error'] = repr(ex)
            errors.append({'entity_hash': tag, 'error': repr(ex)})
        entities[tag] = rec

    # Attach concrete resolved entity/resource data back to each named arrangement.
    arrangements = []
    for arr in src.get('arrangements', []):
        branches = []
        for branch in arr.get('resolved_body_assignments', []):
            tag = branch.get('entity_data_hash')
            branches.append({**branch, 'entity_resolution': entities.get(str(tag).upper()) if tag else None})
        arrangements.append({**arr, 'resolved_body_assignments': branches})

    model_rows = []
    seen_models = set()
    for ent in entities.values():
        for res in ent.get('resources', []):
            m = res.get('embedded_model') or {}
            if m.get('resolved') and m.get('tag_hash') not in seen_models:
                seen_models.add(m['tag_hash'])
                model_rows.append(m)

    report = {
        'schema': 'd1_playable_guardian_entity_resource_resolve/v1',
        'source_schema': src.get('schema'),
        'entity_count': len(entities),
        'resolved_entity_count': sum(bool(x.get('resolved')) for x in entities.values()),
        's_entity_count': sum(bool(x.get('is_s_entity')) for x in entities.values()),
        'resource_occurrence_count': sum(len(x.get('resources', [])) for x in entities.values()),
        'resource_package_counts': dict(resource_pkg_counts.most_common()),
        'resource_role_counts': dict(role_counts.most_common()),
        'unique_embedded_model_count': len(model_rows),
        'embedded_model_package_counts': dict(model_pkg_counts.most_common()),
        'catalog_package_ids': [f'{x:04X}' for x in sorted(catalogs)],
        'entities': entities,
        'models': model_rows,
        'arrangements': arrangements,
        'errors': errors,
        'policy': (
            'Item name/class/body-role context is inherited from the prior retail arrangement join. '
            'EntityDataROI->s_entity Resource[]->EntityResource role->embedded s_entity_model edges are decoded '
            'directly from retail package bytes. No model or body assignment is guessed from package names.'
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2) + '\n')
    summary = {k: v for k, v in report.items() if k not in ('entities','models','arrangements','errors')}
    print(json.dumps(summary, indent=2))
    for ent in entities.values():
        print('\nENTITY', ent['entity_hash'], f"pkg={ent['package_id']:04X}", 'ref=', ent.get('reference'), 'resources=', ent.get('resource_count'))
        for res in ent.get('resources', []):
            m = res.get('embedded_model') or {}
            print(' ', res.get('resource_hash'), res.get('semantic_role'), 'pkg=', f"{int(res['resource_package_id']):04X}" if res.get('resource_package_id') is not None else None,
                  'model=', m.get('tag_hash'), 'model_ref=', m.get('reference'))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
