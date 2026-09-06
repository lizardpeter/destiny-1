#!/usr/bin/env python3
"""Decode every D1 ROI 80802C0E action control in a remote logical package.

Uses the already source-closed selector-table decoder. The output preserves exact
state StringHashes and selected s_animation_clip FileHashes. Known state names are
only exact FNV1 preimages from the existing dictionary; no ownership is inferred.
"""
from __future__ import annotations

import argparse,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from d1_remote_investment_parent_probe import RemoteLogicalPackage,parse_member
from d1_split_tar_extract import SplitHttpTar
from d1_animation_control_state_map import CONTROL_REF,DEFAULTS,decode_control


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--package-id',type=lambda x:int(x,0),required=True)
    ap.add_argument('--member',action='append',type=parse_member,required=True)
    ap.add_argument('--base-url',required=True);ap.add_argument('--part-count',type=int,default=10)
    ap.add_argument('--runtime',type=Path,required=True);ap.add_argument('--name',action='append',default=[])
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args()
    if any(x.pkg_id!=a.package_id for x in a.member):raise SystemExit('member package id mismatch')
    members={x.patch_id:x for x in a.member}
    arc=SplitHttpTar([f"{a.base_url.rstrip('/')}/packages.tar.{i:03d}" for i in range(1,a.part_count+1)],retries=6,timeout=90)
    r=RemoteLogicalPackage(arc,members,a.runtime);names=list(dict.fromkeys(DEFAULTS+a.name))
    controls=[];errors=[];selected=set()
    for e in r.entries:
        if e['reference'].upper()!=CONTROL_REF:continue
        row={'tag_hash':e['tag_hash'].upper(),'entry_index':e['index'],'file_size':e['file_size']}
        try:
            d=decode_control(r.entry(e['index']),r,names);row.update({'decode_success':True,**d})
            for s in d['state_table']['records']:
                for x in s['selected_animations']:
                    selected.add(x['tag_hash'])
        except Exception as ex:
            row.update({'decode_success':False,'error':repr(ex)});errors.append({'tag_hash':row['tag_hash'],'error':repr(ex)})
        controls.append(row)
    out={'schema':'d1_remote_animation_control_census/v1','package_id':f'{a.package_id:04X}','logical_view_member':r.view.name,
         'summary':{'control_count':len(controls),'decode_success_count':sum(bool(x.get('decode_success')) for x in controls),
                    'decode_error_count':len(errors),'unique_selected_clip_count':len(selected)},
         'selected_clip_tags':sorted(selected),'controls':controls,'errors':errors,
         'policy':'Control->state->clip selection is binary-decoded. Package/control residency does not by itself prove gameplay/player ownership.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n')
    brief=[]
    for c in controls:
        if not c.get('decode_success'):continue
        brief.append({'control':c['tag_hash'],'animations':[x['tag_hash'] for x in c['animation_list']['items']],
                      'states':[{'hash':s['state_hash'],'name':s['state_name'],'selected':[x['tag_hash'] for x in s['selected_animations']]} for s in c['state_table']['records']]})
    print(json.dumps({'package_id':out['package_id'],'summary':out['summary'],'controls':brief},indent=2));return 0

if __name__=='__main__':raise SystemExit(main())
