#!/usr/bin/env python3
"""Discover exact D1 skeleton/rig/control/clip compatibility for one base family.

This is the generic successor to the player-specific 72/66 retarget proof.  It does
not assume a particular race, NPC, enemy or Guardian rig.  For one structural
package family it:

* enumerates decoded skeleton EntityResources from the corpus report;
* enumerates runtime rigs from the same exact structural family;
* enumerates every local 0x80802C0E animation control;
* decodes each control's serialized selected animation FileHashes;
* resolves every selected clip cross-package through the universal base catalog;
* requires exact clip/rig control counts and ordered runtime-component fingerprints;
* requires calc_control_limit == runtime-rig control count;
* requires the pinned D1 parser to decode, rig-retarget and localize successfully;
* retains every compatible skeleton/rig/control combination rather than guessing an
  owner when more than one same-dimension skeleton is mechanically compatible.

A successful row proves a mechanically exportable retail animation path.  Gameplay
or archetype semantics remain a separate ownership/name join.
"""
from __future__ import annotations

import argparse
import io
import json
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))

from d1_animation_control_state_map import decode_control
from d1_animation_retarget_probe import component_rows
from d1_character_family_census import RUNTIME_RIG_DISCRIMINATOR,RUNTIME_RIG_INFO
from d1_entity_resource_probe import parse_resource
from d1_playable_guardian_entity_resource_resolve import load_catalogs
from d1_remote_investment_parent_probe import Member,RemoteLogicalPackage
from d1_remote_model_tgxm_signature_match import LazyExactHashResolver
from d1_split_tar_extract import SplitHttpTar

CONTROL_CLASS='80802C0E'


def norm(x:object)->str:return str(x).upper().removeprefix('0X').zfill(8)


def read_animation_filebacked(read_animation,payload:bytes,ver):
    with tempfile.NamedTemporaryFile() as f:
        f.write(payload);f.flush();f.seek(0);return read_animation(f,ver)


def selected(control:dict)->dict[str,list[dict]]:
    out=defaultdict(list)
    for st in control['state_table']['records']:
        for a in st['selected_animations']:
            out[norm(a['tag_hash'])].append({
              'record_index':int(st['record_index']),'state_hash':norm(st['state_hash']),
              'state_name':st.get('state_name'),'scalar_f32':st['scalar_f32'],'packed_selection':st['packed_selection']})
    return dict(out)


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('corpus_report',type=Path)
    ap.add_argument('--namespace-key',required=True)
    ap.add_argument('--member-catalog',type=Path,required=True)
    ap.add_argument('--base-url',default='https://crypt.cohae.dev/destiny/ps4/packages/latest')
    ap.add_argument('--part-count',type=int,default=10)
    ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('--parser-root',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()

    corpus=json.loads(a.corpus_report.read_text())
    if corpus.get('schema')!='d1_remote_character_corpus_probe/v1':raise ValueError('wrong corpus schema')
    fam=next((x for x in corpus.get('families',[]) if x.get('namespace_key')==a.namespace_key),None)
    if fam is None:raise KeyError(f'namespace family not found: {a.namespace_key}')
    if fam.get('kind')!='base':raise ValueError('this probe currently requires base namespace family')
    pkg=int(fam['package_id'],16)

    cats=load_catalogs([a.member_catalog])
    if pkg not in cats:raise KeyError(f'{pkg:04X}: family absent from universal base catalog')
    base=a.base_url.rstrip('/');arc=SplitHttpTar([f'{base}/packages.tar.{i:03d}' for i in range(1,a.part_count+1)],retries=6,timeout=90)
    local=RemoteLogicalPackage(arc,cats[pkg],a.runtime)
    resolver=LazyExactHashResolver(arc,cats,a.runtime)

    sys.path.insert(0,str(a.parser_root.resolve()))
    from tag.game_version import Game_Version
    from tag_readers.read_skeleton import read_skeleton
    from tag_readers.read_rig import read_runtime_rig
    from tag_readers.read_animation import read_animation
    from animation_decoding.decode_animation import decode_animation
    from runtime_rig.rig_retarget import rig_retarget,calc_control_limit
    from animation_export.convert_animation_object_to_local import convert_obj_to_local
    ver=Game_Version.D1_ROI

    skeletons=[]
    for x in fam.get('skeletons',[]):
        h=norm(x['tag_hash']);_v,e,b=resolver.bytes(h);sk=read_skeleton(io.BytesIO(b),ver)
        row={'tag_hash':h,'entry_index':int(e['index']),'node_count':len(sk.node_defs),'object':sk}
        if row['node_count']!=int(x['bone_count']):raise ValueError(f'{h}: parser/corpus node count mismatch')
        skeletons.append(row)

    rigs=[]
    for x in fam.get('runtime_rigs',[]):
        h=norm(x['tag_hash']);_v,e,b=resolver.bytes(h)
        outer=parse_resource(b,'PS4');u10=(outer.get('unk10') or {}).get('class_hash');u18=(outer.get('unk18') or {}).get('class_hash')
        if (u10,u18)!=(RUNTIME_RIG_DISCRIMINATOR,RUNTIME_RIG_INFO):raise ValueError(f'{h}: runtime rig class changed {u10}->{u18}')
        rig=read_runtime_rig(io.BytesIO(b),ver)
        rigs.append({'tag_hash':h,'entry_index':int(e['index']),'control_count':len(rig.controls_relations),
                     'components':component_rows(rig.rig_components),'object':rig})

    controls=[]
    for e in local.entries:
        if norm(e['reference'])!=CONTROL_CLASS:continue
        h=norm(e['tag_hash'])
        try:
            b=local.entry(int(e['index']));d=decode_control(b,None,[]);sel=selected(d)
            controls.append({'tag_hash':h,'entry_index':int(e['index']),'animation_count':int(d['animation_list']['count']),
                             'state_count':int(d['state_table']['count']),'unique_selected_clip_count':len(sel),'selected':sel})
        except Exception as ex:
            controls.append({'tag_hash':h,'entry_index':int(e['index']),'error':repr(ex),'selected':{}})

    clip_cache={};errors=[]
    def clip_info(h:str):
        if h in clip_cache:return clip_cache[h]
        try:
            _v,e,b=resolver.bytes(h);anim=read_animation_filebacked(read_animation,b,ver);hdr=anim.animation_header
            row={'tag_hash':h,'entry_index':int(e['index']),'frame_count':int(hdr.frame_count),'node_count':int(hdr.node_count),
                 'rig_control_count':int(hdr.rig_control_count),'components':component_rows(anim.runtime_rig_components),
                 'payload':b,'object':anim}
        except Exception as ex:
            row={'tag_hash':h,'error':repr(ex)};errors.append({'clip':h,'error':repr(ex)})
        clip_cache[h]=row;return row

    paths=[]
    for c in controls:
        for ch,states in sorted(c.get('selected',{}).items()):
            ci=clip_info(ch)
            if ci.get('error'):continue
            matching_rigs=[r for r in rigs if r['control_count']==ci['rig_control_count'] and r['components']==ci['components']]
            matching_skeletons=[s for s in skeletons if s['node_count']==ci['node_count']]
            for r in matching_rigs:
                try:limit=int(calc_control_limit(r['object'],ci['object'].runtime_rig_components))
                except Exception as ex:
                    errors.append({'clip':ch,'rig':r['tag_hash'],'phase':'control_limit','error':repr(ex)});continue
                if limit!=r['control_count']:
                    errors.append({'clip':ch,'rig':r['tag_hash'],'phase':'control_limit','error':f'{limit}!={r["control_count"]}'});continue
                decoded=None
                try:decoded=decode_animation(ci['object'])
                except Exception as ex:
                    errors.append({'clip':ch,'rig':r['tag_hash'],'phase':'decode','error':repr(ex)});continue
                if len(decoded)!=r['control_count']:
                    errors.append({'clip':ch,'rig':r['tag_hash'],'phase':'decoded_domain','error':f'{len(decoded)}!={r["control_count"]}'});continue
                for s in matching_skeletons:
                    try:
                        ret=rig_retarget(ci['object'],decoded,s['object'],r['object']);local_tracks=convert_obj_to_local(ci['object'],ret,s['object'])
                        ok=len(ret)==s['node_count'] and len(local_tracks)==s['node_count']
                        if not ok:raise ValueError(f'track domains ret/local {len(ret)}/{len(local_tracks)} != {s["node_count"]}')
                        channel_nodes={'translation':0,'rotation':0,'scale':0}
                        frame_sets={k:set() for k in channel_nodes}
                        for tr in local_tracks:
                            for k,attr in (('translation','translations'),('rotation','rotations'),('scale','scales')):
                                vals=getattr(tr,attr,[])
                                if len(vals):channel_nodes[k]+=1;frame_sets[k].add(len(vals))
                        paths.append({'skeleton':s['tag_hash'],'skeleton_node_count':s['node_count'],'runtime_rig':r['tag_hash'],
                                      'runtime_rig_control_count':r['control_count'],'control':c['tag_hash'],'clip':ch,
                                      'clip_frame_count':ci['frame_count'],'states':states,'native_control_limit':limit,
                                      'decoded_track_count':len(decoded),'retargeted_track_count':len(ret),'local_track_count':len(local_tracks),
                                      'local_channel_node_counts':channel_nodes,'local_channel_frame_count_sets':{k:sorted(v) for k,v in frame_sets.items()},
                                      'retarget_success':True})
                    except Exception as ex:
                        errors.append({'clip':ch,'rig':r['tag_hash'],'skeleton':s['tag_hash'],'phase':'retarget','error':repr(ex)})

    groups=defaultdict(list)
    for p in paths:groups[(p['skeleton'],p['runtime_rig'],p['control'])].append(p)
    families=[]
    for (sk,rig,ctrl),xs in sorted(groups.items()):
        clips=sorted({x['clip'] for x in xs})
        families.append({'skeleton':sk,'runtime_rig':rig,'control':ctrl,'clip_count':len(clips),'clips':clips,
                         'path_count':len(xs),'state_selection_count':sum(len(x['states']) for x in xs)})
    clip_ambiguity={h:sum(1 for p in paths if p['clip']==h) for h in sorted({p['clip'] for p in paths})}
    out={'schema':'d1_remote_animation_family_probe/v1','status':'D1_ANIMATION_FAMILY_PROBE_COMPLETE',
         'namespace_key':a.namespace_key,'package_id':f'{pkg:04X}','logical_view':local.view.name,
         'skeleton_count':len(skeletons),'runtime_rig_count':len(rigs),'control_count':len(controls),
         'selected_unique_clip_count':len(clip_cache),'successful_path_count':len(paths),'animation_family_count':len(families),
         'mechanically_compatible_clip_count':len({p['clip'] for p in paths}),
         'ambiguous_mechanical_clip_count':sum(n>1 for n in clip_ambiguity.values()),
         'skeletons':[{k:v for k,v in x.items() if k!='object'} for x in skeletons],
         'runtime_rigs':[{k:v for k,v in x.items() if k!='object'} for x in rigs],
         'controls':controls,'animation_families':families,'paths':paths,'clip_mechanical_path_counts':clip_ambiguity,'errors':errors,
         'policy':'Successful paths are exact control-selected clips with exact rig component/dimension compatibility and parser retarget success. Multiple mechanically compatible skeletons are retained as ambiguity; gameplay ownership is never selected from dimensions or package adjacency.'}
    # Remove potentially bulky selected maps duplicated by paths only from errors? Keep controls for provenance.
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ('namespace_key','skeleton_count','runtime_rig_count','control_count','selected_unique_clip_count','successful_path_count','animation_family_count','mechanically_compatible_clip_count','ambiguous_mechanical_clip_count')},indent=2))
    return 0

if __name__=='__main__':raise SystemExit(main())
