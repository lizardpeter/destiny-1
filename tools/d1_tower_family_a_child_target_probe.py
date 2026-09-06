#!/usr/bin/env python3
"""Trace the 1-control target selected by Tower Family A's cross-package owner.

Known exact frontier:
  SEntity/model side: 80C7A05E -> 80C7AD2A, skeleton 80BC60B2 (4), rig 80BC60B4 (4)
  owner halves:       80C7A2A5 (023D) + 80BC6412 (01E3) -> control 80BC6489
  state:              idle / 6FB760FF -> clip 80BC648A
  clip component:     C3747E31 x1

The clip component does not match the model rig (69289DF6 x4). This probe therefore
searches the exact 01E3 corpus for runtime rigs whose parsed component fingerprint
matches the clip exactly, and separately inventories every Family-A SEntity resource
that can be resolved in the staged 023D+01E3 corpus. Literal FileHash co-references
are reported only as co-reference evidence, never promoted to ownership by themselves.
"""
from __future__ import annotations

import argparse
import io
import json
import struct
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from d1_entry_extract import EntryReader
from d1_entity_resource_probe import parse_resource
from d1_tower_family_f_animation_ownership import norm, entry_map, exact_payload, dyn_resources, filebacked
from d1_animation_retarget_probe import component_rows

ENTITY_RESOURCE_REF = '80800861'
CLIP_REF = '808005A1'
SENTITY = '80C7A05E'
MODEL = '80C7AD2A'
MODEL_SKELETON = '80BC60B2'
MODEL_RIG = '80BC60B4'
CONTROL = '80BC6489'
CLIP = '80BC648A'
EXPECTED_CLIP_COMPONENTS = [{'hash': 'C3747E31', 'count': 1}]


def sig(rows):
    return tuple((norm(x['hash']), int(x['count'])) for x in rows)


class Corpus:
    def __init__(self, readers):
        self.readers = readers
        self.maps = {k: entry_map(v) for k,v in readers.items()}

    def locations(self, tag, expected_ref=None):
        tag = norm(tag); out=[]
        for package,r in self.readers.items():
            e=self.maps[package].get(tag)
            if e is None: continue
            if expected_ref is not None and norm(e['reference']) != norm(expected_ref): continue
            out.append((package,r,e))
        return out

    def unique_payload(self, tag, expected_ref=None):
        locs=[]
        for package,r,e in self.locations(tag, expected_ref):
            if r.available(e['index']): locs.append((package,r,e,r.entry(e['index'])))
        if len(locs)!=1:
            raise ValueError(f'{norm(tag)}: expected one available corpus payload, got {[(x[0],x[2]["index"],norm(x[2]["reference"])) for x in locs]}')
        return locs[0]


def literal_tag_hits(payload: bytes, tag_map: dict[int,list[dict]]) -> list[dict]:
    hits=[]
    # FileHashes are 32-bit; report aligned matches only. They remain co-reference evidence.
    for off in range(0, len(payload)-3, 4):
        v=struct.unpack_from('<I',payload,off)[0]
        for target in tag_map.get(v,[]):
            hits.append({'offset':off,'value':f'{v:08X}',**target})
    return hits


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--activity-pkg',type=Path,required=True)
    ap.add_argument('--cinematic-pkg',type=Path,required=True)
    ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('--parser-root',type=Path,required=True)
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args()

    readers={'023D':EntryReader(a.activity_pkg,a.runtime),'01E3':EntryReader(a.cinematic_pkg,a.runtime)}
    corpus=Corpus(readers)

    sys.path.insert(0,str(a.parser_root.resolve()))
    from tag.game_version import Game_Version
    from tag_readers.read_rig import read_runtime_rig
    from tag_readers.read_skeleton import read_skeleton
    from tag_readers.read_animation import read_animation
    ver=Game_Version.D1_ROI

    # Reopen the exact selected clip and pin its real component fingerprint.
    cpkg,cr,ce,cb=corpus.unique_payload(CLIP,CLIP_REF)
    anim=filebacked(read_animation,cb,ver)
    h=anim.animation_header
    clip_components=component_rows(anim.runtime_rig_components)
    if sig(clip_components) != sig(EXPECTED_CLIP_COMPONENTS):
        raise ValueError(f'{CLIP}: component fingerprint drift {clip_components}')
    if (int(h.frame_count),int(h.node_count),int(h.rig_control_count)) != (31,1,1):
        raise ValueError(f'{CLIP}: expected 31f/1node/1control, got {(h.frame_count,h.node_count,h.rig_control_count)}')

    # Reopen Family-A SEntity and preserve its exact serialized resource list.
    _,ar,ae,ab=corpus.unique_payload(SENTITY,'80800734')
    family_resources=dyn_resources(ab)
    if MODEL_SKELETON not in family_resources or MODEL_RIG not in family_resources:
        raise ValueError('Family-A SEntity resource list no longer carries the proven model skeleton/rig')

    # Inventory all exact runtime rigs and skeletons in 01E3. The parser secondary-class
    # checks act as a structural filter; arbitrary EntityResources are not accepted.
    rigs=[]; skeletons=[]
    r01=readers['01E3']
    for e in r01.entries:
        if norm(e['reference']) != ENTITY_RESOURCE_REF or not r01.available(e['index']):
            continue
        payload=r01.entry(e['index'])
        try:
            rig=read_runtime_rig(io.BytesIO(payload),ver)
            rows=component_rows(rig.rig_components)
            rigs.append({
                'tag_hash':norm(e['tag_hash']),'entry_index':int(e['index']),'size':int(e['file_size']),
                'control_count':len(rig.controls_relations),'components':rows,
                'clip_component_exact_match':sig(rows)==sig(clip_components),
                'is_family_a_serialized_resource':norm(e['tag_hash']) in family_resources,
            })
        except Exception:
            pass
        try:
            sk=read_skeleton(io.BytesIO(payload),ver)
            skeletons.append({
                'tag_hash':norm(e['tag_hash']),'entry_index':int(e['index']),'size':int(e['file_size']),
                'node_count':len(sk.node_defs),
                'one_node_candidate':len(sk.node_defs)==1,
                'is_family_a_serialized_resource':norm(e['tag_hash']) in family_resources,
            })
        except Exception:
            pass

    matching_rigs=[x for x in rigs if x['clip_component_exact_match']]
    one_node_skeletons=[x for x in skeletons if x['one_node_candidate']]

    # Classify every Family-A serialized resource that is physically present in this
    # 023D+01E3 corpus and try the strict rig/skeleton readers on it independently.
    resource_rows={}
    for tag in family_resources:
        locs=corpus.locations(tag)
        row={'tag_hash':tag,'locations':[],'resolved_payload':False}
        for package,r,e in locs:
            lr={'package':package,'entry_index':int(e['index']),'reference':norm(e['reference']),
                'size':int(e['file_size']),'available':bool(r.available(e['index']))}
            row['locations'].append(lr)
        avail=[(p,r,e) for p,r,e in locs if r.available(e['index'])]
        if len(avail)==1:
            package,r,e=avail[0]; payload=r.entry(e['index']); row['resolved_payload']=True; row['package']=package
            if norm(e['reference'])==ENTITY_RESOURCE_REF:
                try: row['entity_resource']=parse_resource(payload,r.h['platform'])
                except Exception as ex: row['entity_resource_error']=repr(ex)
                try:
                    rig=read_runtime_rig(io.BytesIO(payload),ver)
                    rr=component_rows(rig.rig_components)
                    row['runtime_rig']={'control_count':len(rig.controls_relations),'components':rr,
                                        'clip_component_exact_match':sig(rr)==sig(clip_components)}
                except Exception:
                    pass
                try:
                    sk=read_skeleton(io.BytesIO(payload),ver)
                    row['skeleton']={'node_count':len(sk.node_defs)}
                except Exception:
                    pass
        resource_rows[tag]=row

    # Build a tag dictionary for literal aligned co-reference scans across the exact
    # owner/control/Sentity resources. This can expose a direct FileHash edge to a
    # matching child rig/skeleton, but a literal match alone is not promoted.
    all_targets=[]
    for package,r in readers.items():
        for e in r.entries:
            all_targets.append({'package':package,'tag_hash':norm(e['tag_hash']),'reference':norm(e['reference']),
                                'entry_index':int(e['index'])})
    tag_map=defaultdict(list)
    for x in all_targets: tag_map[int(x['tag_hash'],16)].append(x)

    scan_tags=[SENTITY,'80C7A2A5','80BC6412',CONTROL,CLIP,*family_resources]
    literal_scans={}
    for tag in dict.fromkeys(scan_tags):
        try:
            package,r,e,payload=corpus.unique_payload(tag)
        except Exception:
            continue
        hits=literal_tag_hits(payload,tag_map)
        # retain useful inter-entry hits, excluding self and zero-like noise
        hits=[x for x in hits if x['tag_hash'] != norm(tag)]
        literal_scans[norm(tag)]={'package':package,'reference':norm(e['reference']),'size':len(payload),'hits':hits}

    matching_rig_tags={x['tag_hash'] for x in matching_rigs}
    one_node_tags={x['tag_hash'] for x in one_node_skeletons}
    direct_family_matching_rigs=sorted(matching_rig_tags & set(family_resources))
    direct_family_one_node_skeletons=sorted(one_node_tags & set(family_resources))
    literal_edges_to_matching=[]
    for source,row in literal_scans.items():
        for hit in row['hits']:
            if hit['tag_hash'] in matching_rig_tags or hit['tag_hash'] in one_node_tags:
                literal_edges_to_matching.append({'source':source,**hit})

    out={
        'schema_version':1,
        'status':'D1_TOWER_FAMILY_A_CHILD_TARGET_CENSUS_COMPLETE',
        'family_a':{
            'sentity':SENTITY,'model':MODEL,'model_skeleton':MODEL_SKELETON,'model_runtime_rig':MODEL_RIG,
            'serialized_resources':family_resources,
        },
        'selected_animation':{
            'control':CONTROL,'clip':CLIP,'clip_package':cpkg,'clip_entry_index':int(ce['index']),
            'frame_count':31,'node_count':1,'rig_control_count':1,'runtime_rig_components':clip_components,
        },
        '01e3_runtime_rig_count':len(rigs),
        '01e3_skeleton_count':len(skeletons),
        'matching_runtime_rigs':matching_rigs,
        'one_node_skeleton_candidates':one_node_skeletons,
        'family_serialized_resource_details':resource_rows,
        'matching_rigs_directly_in_family_resource_list':direct_family_matching_rigs,
        'one_node_skeletons_directly_in_family_resource_list':direct_family_one_node_skeletons,
        'literal_edges_to_matching_rig_or_one_node_skeleton':literal_edges_to_matching,
        'closure':{
            'unique_matching_runtime_rig':len(matching_rigs)==1,
            'matching_runtime_rig_is_direct_family_resource':len(direct_family_matching_rigs)==1,
            'unique_direct_family_one_node_skeleton':len(direct_family_one_node_skeletons)==1,
        },
        'policy':'Runtime-rig/skeleton candidates are accepted only when the pinned parsers pass their exact secondary-class/layout checks. Literal aligned FileHash matches are co-reference evidence only and never establish ownership by themselves.',
    }
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({
        'status':out['status'],'clip_components':clip_components,
        'matching_runtime_rigs':matching_rigs,
        'family_matching_rigs':direct_family_matching_rigs,
        'direct_family_one_node_skeletons':direct_family_one_node_skeletons,
        'literal_edges_to_matching_count':len(literal_edges_to_matching),
        'closure':out['closure'],
    },indent=2))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
