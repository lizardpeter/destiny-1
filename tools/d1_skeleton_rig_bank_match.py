#!/usr/bin/env python3
"""Rank every resident D1 runtime rig against one skeleton using all package clips.

For one known skeleton, parse all byte-validated runtime-rig EntityResources and
every resident s_animation_clip in the same logical package. A rig is ranked by
clips whose ordered runtime-component fingerprint exactly equals that rig and whose
animation header node/control counts match the skeleton/rig dimensions.

This intentionally avoids tag adjacency and filename inference. It establishes a
runtime compatibility family, not gameplay semantic ownership.
"""
from __future__ import annotations

import argparse
import collections
import io
import json
import sys
import tempfile
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from d1_entry_extract import EntryReader
from d1_entity_resource_probe import ENTITY_RESOURCE_CLASS, parse_resource
from d1_animation_retarget_probe import component_rows
from d1_character_family_census import RUNTIME_RIG_DISCRIMINATOR, RUNTIME_RIG_INFO

ANIMATION_CLIP_CLASS='808005A1'


def filebacked(read_animation,payload,version):
    with tempfile.NamedTemporaryFile() as f:
        f.write(payload); f.flush(); f.seek(0)
        return read_animation(f,version)


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('pkg',type=Path)
    ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('--parser-root',type=Path,required=True)
    ap.add_argument('--skeleton',required=True)
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args()

    sys.path.insert(0,str(a.parser_root.resolve()))
    from tag.game_version import Game_Version
    from tag_readers.read_skeleton import read_skeleton
    from tag_readers.read_rig import read_runtime_rig
    from tag_readers.read_animation import read_animation

    r=EntryReader(a.pkg,a.runtime); ver=Game_Version.D1_ROI
    by={e['tag_hash'].upper():e for e in r.entries}
    stag=a.skeleton.upper().removeprefix('0X'); se=by[stag]
    skeleton=read_skeleton(io.BytesIO(r.entry(se['index'])),ver)
    node_count=len(skeleton.node_defs)

    rigs=[]; rig_errors=[]
    for e in r.entries:
        if e['reference'].upper()!=ENTITY_RESOURCE_CLASS or not r.available(e['index']): continue
        try:
            p=parse_resource(r.entry(e['index']),r.h['platform'])
        except Exception:
            continue
        u10=(p.get('unk10') or {}).get('class_hash')
        u18=(p.get('unk18') or {}).get('class_hash')
        if not (u10==RUNTIME_RIG_DISCRIMINATOR and u18==RUNTIME_RIG_INFO):
            continue
        try:
            rig=read_runtime_rig(io.BytesIO(r.entry(e['index'])),ver)
            comps=component_rows(rig.rig_components)
            rigs.append({
                'tag_hash':e['tag_hash'].upper(),'entry_index':e['index'],'size':e['file_size'],
                'control_count':len(rig.controls_relations),'runtime_rig_components':comps,
                'discriminator_class':u10,'info_class':u18,
                '_sig':tuple((x['hash'],int(x['count'])) for x in comps),
            })
        except Exception as ex:
            rig_errors.append({'tag_hash':e['tag_hash'].upper(),'error':repr(ex)})

    clips=[]; clip_errors=[]; sig_counts=collections.Counter()
    for e in r.entries:
        if e['reference'].upper()!=ANIMATION_CLIP_CLASS or not r.available(e['index']): continue
        try:
            anim=filebacked(read_animation,r.entry(e['index']),ver)
            h=anim.animation_header; comps=component_rows(anim.runtime_rig_components)
            sig=tuple((x['hash'],int(x['count'])) for x in comps)
            row={'tag_hash':e['tag_hash'].upper(),'entry_index':e['index'],'frame_count':int(h.frame_count),
                 'node_count':int(h.node_count),'rig_control_count':int(h.rig_control_count),
                 'runtime_rig_components':comps,'_sig':sig}
            clips.append(row); sig_counts[sig]+=1
        except Exception as ex:
            clip_errors.append({'tag_hash':e['tag_hash'].upper(),'error':repr(ex)})

    ranked=[]
    for rig in rigs:
        exact=[c for c in clips if c['_sig']==rig['_sig']]
        dimension=[c for c in exact if c['node_count']==node_count and c['rig_control_count']==rig['control_count']]
        node_only=[c for c in exact if c['node_count']==node_count]
        ranked.append({
            'tag_hash':rig['tag_hash'],'entry_index':rig['entry_index'],'size':rig['size'],
            'control_count':rig['control_count'],'runtime_rig_components':rig['runtime_rig_components'],
            'discriminator_class':rig['discriminator_class'],'info_class':rig['info_class'],
            'exact_component_clip_count':len(exact),
            'exact_component_and_node_count':len(node_only),
            'exact_component_dimension_match_count':len(dimension),
            'dimension_match_clips':[{
                'tag_hash':c['tag_hash'],'entry_index':c['entry_index'],'frame_count':c['frame_count'],
                'node_count':c['node_count'],'rig_control_count':c['rig_control_count']
            } for c in dimension[:100]],
        })
    ranked.sort(key=lambda x:(x['exact_component_dimension_match_count'],x['exact_component_and_node_count'],x['exact_component_clip_count']),reverse=True)

    report={
        'schema':'d1_skeleton_rig_bank_match/v2','package':str(r.pkg),'package_id':f"{int(r.h['pkg_id']):04X}",
        'skeleton':stag,'skeleton_node_count':node_count,
        'runtime_rig_discriminator':RUNTIME_RIG_DISCRIMINATOR,'runtime_rig_info':RUNTIME_RIG_INFO,
        'runtime_rig_count':len(rigs),'animation_clip_count':len(clips),
        'rig_parse_error_count':len(rig_errors),'clip_parse_error_count':len(clip_errors),
        'ranked_rigs':ranked,'rig_errors':rig_errors,'clip_errors':clip_errors,
        'policy':'Runtime rigs are selected only by byte-validated EntityResource pair 808008B2->8080099B. Rank then uses exact ordered runtime-component fingerprints and exact clip node/control dimensions. No tag adjacency, filename, or gameplay semantic inference is used.'
    }
    a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ('ranked_rigs','rig_errors','clip_errors')},indent=2))
    print('TOP RIGS')
    for x in ranked[:10]: print(x['tag_hash'],'controls',x['control_count'],'exact',x['exact_component_clip_count'],'node',x['exact_component_and_node_count'],'dim',x['exact_component_dimension_match_count'])
    return 0

if __name__=='__main__': raise SystemExit(main())
