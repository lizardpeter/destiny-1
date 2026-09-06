#!/usr/bin/env python3
"""Parse every resident D1 s_animation_clip in a remote logical package family.

The scan compares each clip's ordered runtime-component fingerprint against an
explicit target. Exact equality is compatibility evidence only; package residency
or component equality never promotes gameplay/player ownership by itself.
"""
from __future__ import annotations

import argparse
import collections
import json
import sys
import tempfile
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from d1_remote_investment_parent_probe import RemoteLogicalPackage,parse_member
from d1_split_tar_extract import SplitHttpTar
from d1_animation_retarget_probe import component_rows,common_component_prefix

CLIP_CLASS='808005A1'


def comp(text:str)->dict:
    h,n=text.split(':',1);h=h.upper().removeprefix('0X')
    if len(h)!=8 or any(c not in '0123456789ABCDEF' for c in h):raise argparse.ArgumentTypeError(text)
    return {'hash':h,'count':int(n,0)}


def read_filebacked(read_animation,payload:bytes,version):
    with tempfile.NamedTemporaryFile() as f:
        f.write(payload);f.flush();f.seek(0);return read_animation(f,version)


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--package-id',type=lambda x:int(x,0),required=True)
    ap.add_argument('--member',action='append',type=parse_member,required=True)
    ap.add_argument('--base-url',required=True);ap.add_argument('--part-count',type=int,default=10)
    ap.add_argument('--runtime',type=Path,required=True);ap.add_argument('--parser-root',type=Path,required=True)
    ap.add_argument('--component',action='append',type=comp,required=True)
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args()
    if any(x.pkg_id!=a.package_id for x in a.member):raise SystemExit('member package id mismatch')
    members={x.patch_id:x for x in a.member}
    arc=SplitHttpTar([f"{a.base_url.rstrip('/')}/packages.tar.{i:03d}" for i in range(1,a.part_count+1)],retries=6,timeout=90)
    r=RemoteLogicalPackage(arc,members,a.runtime)

    sys.path.insert(0,str(a.parser_root.resolve()))
    from tag.game_version import Game_Version
    from tag_readers.read_animation import read_animation
    ver=Game_Version.D1_ROI

    target=a.component;target_controls=sum(x['count'] for x in target)
    rows=[];errors=[];sigs=collections.Counter()
    for e in r.entries:
        if e['reference'].upper()!=CLIP_CLASS:continue
        row={'tag_hash':e['tag_hash'].upper(),'entry_index':e['index'],'file_size':e['file_size']}
        try:
            anim=read_filebacked(read_animation,r.entry(e['index']),ver);h=anim.animation_header
            cs=component_rows(anim.runtime_rig_components);sig=tuple((x['hash'],x['count']) for x in cs);sigs[sig]+=1
            pref=common_component_prefix(target,cs);exact=cs==target
            row.update({'parse_success':True,'frame_count':int(h.frame_count),'node_count':int(h.node_count),
                        'rig_control_count':int(h.rig_control_count),'runtime_rig_components':cs,
                        'component_prefix':pref,'exact_component_match':exact,
                        'target_control_count_matches_header':int(h.rig_control_count)==target_controls})
        except Exception as ex:
            row.update({'parse_success':False,'error':repr(ex)});errors.append({'tag_hash':row['tag_hash'],'error':repr(ex)})
        rows.append(row)
    exact=[x for x in rows if x.get('exact_component_match')]
    signatures=[{'components':[{'hash':h,'count':n} for h,n in sig],'clip_count':count}
                for sig,count in sigs.most_common()]
    out={'schema':'d1_remote_animation_component_census/v1','package_id':f'{a.package_id:04X}',
         'logical_view_member':r.view.name,'target_components':target,'target_control_count':target_controls,
         'summary':{'animation_clip_count':len(rows),'parse_success_count':sum(bool(x.get('parse_success')) for x in rows),
                    'parse_error_count':len(errors),'unique_component_signature_count':len(sigs),
                    'exact_component_match_count':len(exact),
                    'exact_match_node_counts':dict(collections.Counter(str(x['node_count']) for x in exact)),
                    'exact_match_control_counts':dict(collections.Counter(str(x['rig_control_count']) for x in exact))},
         'exact_component_matches':exact,'component_signatures':signatures,'clips':rows,'errors':errors,
         'policy':'Exact ordered runtime-component equality proves clip/rig-family compatibility only. Semantic player/gameplay ownership requires a separate serialized owner/selector edge.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'package_id':out['package_id'],'view':out['logical_view_member'],'target':target,'summary':out['summary'],
                      'first_exact_matches':[{k:x[k] for k in ('tag_hash','entry_index','frame_count','node_count','rig_control_count')} for x in exact[:30]]},indent=2))
    return 0

if __name__=='__main__':raise SystemExit(main())
