#!/usr/bin/env python3
"""Find exact articulated-entity candidates in the D1 Crota's End raid families.

This is a discovery/proof-boundary tool. It does NOT identify a candidate as Crota
from appearance, package names, size, or proximity. It scans exact retail s_entity
records in caller-selected raid package families and follows each serialized
Resource[] FileHash through the verified universal package catalog. EntityResource
roles are accepted only from the validated D1 parser.

The intended semantic target is the historical-stat identity:
  R1S2RaidMoon0Ultra0 / HiveUltraKnightA / RaidMoon0 / OversoulThrone
but that identity is not promoted onto any binary entity until a separate exact
archetype/spawn ownership edge is recovered.
"""
from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from d1_entity_resource_probe import ENTITY_RESOURCE_CLASS, parse_resource
from d1_investment_arrangement_probe import filehash_pkg_index
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_investment_parent_probe import RemoteLogicalPackage
from d1_remote_s_entity_resource_package_find import S_ENTITY_REF, parse_entity_resources
from d1_skeleton_probe import parse_skeleton_resource
from d1_split_tar_extract import SplitHttpTar

ENTITY_MODEL_CLASS = '80801AB5'
ANIMATION_CLIP_CLASS = '808005A1'
ANIMATION_WRAPPER_CLASS = '8080222A'
POST_ANIMATION_CONTROL_CLASS = '80802C0E'


def norm(v: str) -> str:
    return str(v).upper().removeprefix('0X').zfill(8)


def package_of_hash(v: str) -> int:
    return filehash_pkg_index(int(norm(v), 16))[0]


class LazyExactHashResolver:
    """Open only the exact verified package family encoded by each Tiger FileHash."""

    def __init__(self, arc: SplitHttpTar, catalogs: dict[int, dict], runtime: Path):
        self.arc = arc
        self.catalogs = catalogs
        self.runtime = runtime
        self.views: dict[int, RemoteLogicalPackage] = {}
        self.maps: dict[int, dict[str, dict]] = {}

    def view(self, pkg: int) -> RemoteLogicalPackage:
        if pkg not in self.catalogs:
            raise KeyError(f'no verified member catalog for package {pkg:04X}')
        if pkg not in self.views:
            self.views[pkg] = RemoteLogicalPackage(self.arc, self.catalogs[pkg], self.runtime)
        return self.views[pkg]

    def hash_map(self, pkg: int) -> dict[str, dict]:
        if pkg not in self.maps:
            m: dict[str, dict] = {}
            for e in self.view(pkg).entries:
                h = e['tag_hash'].upper()
                if h in m:
                    raise ValueError(f'duplicate FileHash {h} in package {pkg:04X}')
                m[h] = e
            self.maps[pkg] = m
        return self.maps[pkg]

    def locate(self, tag_hash: str) -> tuple[RemoteLogicalPackage, dict]:
        h = norm(tag_hash)
        pkg = package_of_hash(h)
        e = self.hash_map(pkg).get(h)
        if e is None:
            raise KeyError(f'{h}: not present in exact logical package {pkg:04X}')
        return self.view(pkg), e


def meta_row(e: dict) -> dict:
    return {
        'tag_hash': e['tag_hash'].upper(),
        'entry_index': int(e['index']),
        'reference': e['reference'].upper(),
        'type': int(e['type']),
        'subtype': int(e['subtype']),
        'file_size': int(e['file_size']),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--raid-package-id', action='append', type=lambda x: int(x, 0), required=True)
    ap.add_argument('--hive-arch-package-id', action='append', type=lambda x: int(x, 0), default=[])
    ap.add_argument('--member-catalog', type=Path, action='append', required=True)
    ap.add_argument('--base-url', required=True)
    ap.add_argument('--part-count', type=int, default=10)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('-o', '--output', type=Path, required=True)
    a = ap.parse_args()

    raid_ids = list(dict.fromkeys(a.raid_package_id))
    hive_ids = set(a.hive_arch_package_id)
    catalogs = load_catalogs(a.member_catalog)
    missing = [x for x in raid_ids if x not in catalogs]
    if missing:
        raise SystemExit('raid package(s) absent from verified catalog: ' + ','.join(f'{x:04X}' for x in missing))

    base = a.base_url.rstrip('/')
    arc = SplitHttpTar([f'{base}/packages.tar.{i:03d}' for i in range(1, a.part_count + 1)], retries=6, timeout=90)
    resolver = LazyExactHashResolver(arc, catalogs, a.runtime)
    raid_views = {pkg: resolver.view(pkg) for pkg in raid_ids}

    package_summaries = []
    candidates = []
    errors = []
    class_totals = collections.Counter()

    for pkg, view in raid_views.items():
        refs = collections.Counter(e['reference'].upper() for e in view.entries)
        class_counts = {
            S_ENTITY_REF: refs.get(S_ENTITY_REF, 0),
            ENTITY_RESOURCE_CLASS: refs.get(ENTITY_RESOURCE_CLASS, 0),
            ENTITY_MODEL_CLASS: refs.get(ENTITY_MODEL_CLASS, 0),
            ANIMATION_CLIP_CLASS: refs.get(ANIMATION_CLIP_CLASS, 0),
            ANIMATION_WRAPPER_CLASS: refs.get(ANIMATION_WRAPPER_CLASS, 0),
            POST_ANIMATION_CONTROL_CLASS: refs.get(POST_ANIMATION_CONTROL_CLASS, 0),
        }
        class_totals.update(class_counts)
        package_summaries.append({
            'package_id': f'{pkg:04X}',
            'logical_view': view.view.name,
            'entry_count': len(view.entries),
            'class_counts': class_counts,
        })

        for e in view.entries:
            if e['reference'].upper() != S_ENTITY_REF:
                continue
            entity_hash = e['tag_hash'].upper()
            row = {
                'package_id': f'{pkg:04X}',
                'entity_hash': entity_hash,
                'entity_entry_index': int(e['index']),
                'entity_file_size': int(e['file_size']),
                'resources': [],
                'exact_roles': [],
                'embedded_models': [],
                'skeletons': [],
                'cross_package_ids': [],
                'hive_arch_cross_refs': [],
                'structural_score': 0,
            }
            try:
                raw = parse_entity_resources(view.entry(e['index']))
            except Exception as ex:
                errors.append({'entity_hash': entity_hash, 'stage': 'parse_s_entity', 'error': repr(ex)})
                row['error'] = repr(ex)
                candidates.append(row)
                continue

            row['resource_count'] = len(raw)
            cross = set()
            hive_cross = set()
            for rr in raw:
                h = norm(rr['resource_hash'])
                rp = rr.get('resource_package_id')
                rrow = dict(rr)
                if rp is not None:
                    cross.add(int(rp))
                    if int(rp) in hive_ids:
                        hive_cross.add(h)
                try:
                    rv, re = resolver.locate(h)
                    rrow['entry'] = meta_row(re)
                    ref = re['reference'].upper()
                    if ref == ENTITY_RESOURCE_CLASS and re['type'] == 16 and re['subtype'] == 0:
                        parsed = parse_resource(rv.entry(re['index']), 'PS4')
                        role = parsed.get('semantic_role')
                        rrow['entity_resource'] = parsed
                        rrow['semantic_role'] = role
                        if role:
                            row['exact_roles'].append(role)
                        model = parsed.get('embedded_model_tag_hash')
                        if model and norm(model) not in ('00000000', 'FFFFFFFF'):
                            mh = norm(model)
                            row['embedded_models'].append(mh)
                            mp, _ = filehash_pkg_index(int(mh, 16))
                            if mp in hive_ids:
                                hive_cross.add(mh)
                            row['structural_score'] += 10
                        if role == 'entity_skeleton':
                            try:
                                sk = parse_skeleton_resource(rv.entry(re['index']))
                                info = sk['skeleton_info']
                                srow = {
                                    'resource_hash': h,
                                    'node_count': int(info['node_hierarchy']['count']),
                                    'bone_hashes': [x['node_hash'] for x in info.get('bones', [])],
                                }
                                row['skeletons'].append(srow)
                                row['structural_score'] += 10
                            except Exception as ex:
                                rrow['skeleton_parse_error'] = repr(ex)
                    elif ref == ENTITY_MODEL_CLASS:
                        row['embedded_models'].append(h)
                        row['structural_score'] += 10
                    elif ref == ANIMATION_CLIP_CLASS:
                        row['structural_score'] += 3
                    elif ref in (ANIMATION_WRAPPER_CLASS, POST_ANIMATION_CONTROL_CLASS):
                        row['structural_score'] += 4
                except Exception as ex:
                    rrow['resolution_error'] = repr(ex)
                    errors.append({'entity_hash': entity_hash, 'resource_hash': h, 'stage': 'resolve_resource', 'error': repr(ex)})
                row['resources'].append(rrow)

            row['cross_package_ids'] = [f'{x:04X}' for x in sorted(cross)]
            row['hive_arch_cross_refs'] = sorted(hive_cross)
            row['structural_score'] += 2 * len(hive_cross)
            row['exact_roles'] = sorted(set(row['exact_roles']))
            row['embedded_models'] = sorted(set(row['embedded_models']))
            candidates.append(row)

    candidates.sort(key=lambda x: (-int(x.get('structural_score', 0)), x['package_id'], x['entity_hash']))
    articulated = [x for x in candidates if x.get('embedded_models') or x.get('skeletons') or x.get('hive_arch_cross_refs')]
    report = {
        'schema': 'd1_crota_raid_candidate_probe/v1',
        'semantic_target': {
            'enemy_id': 'R1S2RaidMoon0Ultra0',
            'display_name': 'Crota, Son of Oryx',
            'race_class': 'HiveUltraKnightA',
            'tier': 'Ultra',
            'activity': 'RaidMoon0',
            'location': 'OversoulThrone',
            'weapon': 'Cleaver',
            'other_weapon': 'Shredder',
            'promotion_status': 'semantic target only; no binary entity joined yet',
        },
        'raid_package_ids': [f'{x:04X}' for x in raid_ids],
        'hive_arch_package_ids': [f'{x:04X}' for x in sorted(hive_ids)],
        'package_summaries': package_summaries,
        'class_totals': dict(class_totals),
        's_entity_count': len(candidates),
        'articulated_candidate_count': len(articulated),
        'articulated_candidates': articulated,
        'all_entities': candidates,
        'error_count': len(errors),
        'errors': errors,
        'policy': (
            'Every binary edge is exact retail s_entity Resource[] equality plus verified FileHash routing and validated '
            'EntityResource parsing. Crota identity is NOT inferred from raid package membership, Hive package membership, '
            'model size, skeleton size, adjacency, or appearance. Promotion requires a separate exact RaidMoon0/'
            'OversoulThrone/HiveUltraKnightA ownership or spawn/archetype edge.'
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2) + '\n')
    print('RAID_PACKAGES', report['raid_package_ids'])
    print('S_ENTITIES', report['s_entity_count'], 'ARTICULATED', report['articulated_candidate_count'], 'ERRORS', report['error_count'])
    for x in articulated[:50]:
        print('CANDIDATE', x['entity_hash'], 'PKG', x['package_id'], 'SCORE', x['structural_score'],
              'MODELS', x['embedded_models'], 'SKELETONS', [(s['resource_hash'], s['node_count']) for s in x['skeletons']],
              'HIVE_REFS', x['hive_arch_cross_refs'])
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
