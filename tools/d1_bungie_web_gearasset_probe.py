#!/usr/bin/env python3
"""Probe Bungie's exact legacy D1 web GearAsset endpoint.

Archived Bungie Spasm used Destiny.GetDestinySingleDefinition for GearAsset data.
The preserved endpoint shape is:

  /d1/Platform/Destiny/Manifest/22/{itemHash}

This tool records HTTP status/body hashes first, then parses the response only when
it contains an explicit GearAsset object. It mirrors the archived Spasm web
index-set and class/gender art-selection rules and downloads only filenames named
by that exact response. No historical DB or visual inference is used.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

BASE='https://www.bungie.net'
GEAR_ROOT='/common/destiny_content/geometry/gear'
SKIP={'2','6','21'}
UA='d1-reversal-evidence/1.0 (+https://github.com/lizardpeter/destiny-1)'


def get(url:str)->tuple[int,dict,bytes]:
    req=urllib.request.Request(url,headers={'User-Agent':UA,'Accept':'application/json,*/*'})
    try:
        with urllib.request.urlopen(req,timeout=90) as r:
            return int(getattr(r,'status',200)),dict(r.headers.items()),r.read()
    except urllib.error.HTTPError as e:
        return int(e.code),dict(e.headers.items()),e.read()


def gearasset_payload(obj:Any)->dict|None:
    candidates=[]
    if isinstance(obj,dict):
        candidates.append(obj)
        for k in ('Response','response','data'):
            v=obj.get(k)
            if isinstance(v,dict):
                candidates.append(v)
                for kk in ('data','response'):
                    vv=v.get(kk)
                    if isinstance(vv,dict): candidates.append(vv)
    for x in candidates:
        ga=x.get('gearAsset') if isinstance(x,dict) else None
        if isinstance(ga,dict):
            return {'requestedId':x.get('requestedId'),'gearAsset':ga}
    return None


def web_content(ga:dict)->dict:
    for c in ga.get('content') or []:
        if c.get('platform')=='web': return c
    raise ValueError('exact GearAsset contains no platform=web content')


def index_sets(c:dict,is_female:bool)->list[dict]:
    out=[]
    if c.get('dye_index_set'): out.append({'kind':'dye','key':None,'set':c['dye_index_set']})
    regions=c.get('region_index_sets')
    if regions:
        for k,v in regions.items():
            if str(k) in SKIP: continue
            if v: out.append({'kind':'region','key':str(k),'set':v[0]})
    else:
        s=c.get('female_index_set') if is_female else c.get('male_index_set')
        if s: out.append({'kind':'female' if is_female else 'male','key':None,'set':s})
    return out


def selected(c:dict,sets:list[dict])->dict:
    idx={k:[] for k in ('geometry','textures','plate_regions')}
    for x in sets:
        s=x['set'] or {}
        for k in idx: idx[k].extend(int(v) for v in (s.get(k) or []))
    for k in idx: idx[k]=list(dict.fromkeys(idx[k]))
    result={}
    for k,inds in idx.items():
        arr=c.get(k) or []
        rows=[]
        for i in inds:
            if not 0<=i<len(arr): raise IndexError(f'{k}[{i}] outside {len(arr)}')
            rows.append({'index':i,'file_name':arr[i]})
        result[k]=rows
    return result


def art_content(gear:dict,class_hash:int)->tuple[dict,dict]:
    art=gear.get('art_content')
    evidence={'source':'art_content','selected_art_content_set_index':None}
    sets=gear.get('art_content_sets')
    if sets and len(sets)>1:
        chosen=None; ci=None
        for i,s in enumerate(sets):
            if chosen is None or int(s.get('classHash',-1))==class_hash:
                chosen=s; ci=i
        if chosen is not None and chosen.get('arrangement') is not None:
            art=chosen['arrangement']; evidence={'source':'art_content_sets.arrangement','selected_art_content_set_index':ci,'selected_class_hash':chosen.get('classHash')}
    if not isinstance(art,dict): raise ValueError('gear JSON has no selected art content')
    return art,evidence


def geometry_ids(gear:dict,class_hash:int,is_female:bool)->tuple[list[Any],dict]:
    art,ev=art_content(gear,class_hash); gs=art.get('gear_set') or {}; ids=[]; rows=[]
    regions=gs.get('regions') or []
    if regions:
        for ri,r in enumerate(regions):
            pats=r.get('pattern_list') or []
            if not pats: continue
            vals=list(pats[0].get('geometry_hashes') or []); ids.extend(vals); rows.append({'region_index':ri,'pattern_index':0,'geometry_hashes':vals})
        ev['gear_set_path']='regions[*].pattern_list[0].geometry_hashes'
    else:
        arr=gs.get('female_override_art_arrangement') if is_female else gs.get('base_art_arrangement')
        if isinstance(arr,dict):
            vals=list(arr.get('geometry_hashes') or []); ids.extend(vals); rows.append({'geometry_hashes':vals})
        ev['gear_set_path']='female_override_art_arrangement.geometry_hashes' if is_female else 'base_art_arrangement.geometry_hashes'
    return ids,{'selection':ev,'sources':rows}


def parse_hash(s:str)->int:
    s=s.strip(); return (int(s,16) if s.lower().startswith('0x') or any(c in 'abcdefABCDEF' for c in s) else int(s,10)) & 0xffffffff


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--item-hash',action='append',required=True)
    ap.add_argument('--class-hash',type=lambda x:int(x,0),default=3655393761)
    ap.add_argument('--female',action='store_true')
    ap.add_argument('--download-dir',type=Path)
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args()
    rows=[]; failures=[]
    for item in [parse_hash(x) for x in a.item_hash]:
        url=f'{BASE}/d1/Platform/Destiny/Manifest/22/{item}'
        status,h,b=get(url)
        row={'item_hash_decimal':item,'item_hash_hex':f'{item:08X}','endpoint_url':url,'http_status':status,
             'response_size':len(b),'response_sha256':hashlib.sha256(b).hexdigest(),'content_type':h.get('Content-Type')}
        if a.download_dir:
            a.download_dir.mkdir(parents=True,exist_ok=True); (a.download_dir/f'{item}_response.bin').write_bytes(b)
        try:
            obj=json.loads(b.decode('utf-8-sig'))
            row['error_code']=obj.get('ErrorCode') if isinstance(obj,dict) else None
            row['error_status']=obj.get('ErrorStatus') if isinstance(obj,dict) else None
            p=gearasset_payload(obj)
            if status!=200 or p is None: raise ValueError(f'no exact GearAsset payload (HTTP {status}, ErrorStatus={row.get("error_status")})')
            ga=p['gearAsset']; c=web_content(ga); sets=index_sets(c,a.female); files=selected(c,sets)
            gears=[]
            for name in ga.get('gear') or []:
                gurl=f'{BASE}{GEAR_ROOT}/{name}'; gs,gh,gb=get(gurl)
                if gs!=200: raise ValueError(f'gear file {name} HTTP {gs}')
                gj=json.loads(gb.decode('utf-8-sig')); gids,asel=geometry_ids(gj,a.class_hash,a.female)
                if a.download_dir: (a.download_dir/name).write_bytes(gb)
                gears.append({'file_name':name,'url':gurl,'sha256':hashlib.sha256(gb).hexdigest(),'size':len(gb),'geometry_identifiers':gids,'art_selection':asel})
            row.update({'requested_id':p.get('requestedId'),'gearasset':ga,'web_index_sets':sets,'web_selected_files':files,'gear_json':gears})
        except Exception as ex:
            row['parse_error']=repr(ex); failures.append(row['item_hash_hex'])
        rows.append(row)
        print(row['item_hash_hex'],'HTTP',status,'bytes',len(b),'error',row.get('error_status'),'parse',row.get('parse_error'))
        if row.get('gear_json'):
            print(' gear',[(x['file_name'],x['geometry_identifiers']) for x in row['gear_json']])
            print(' geometry',[(x['index'],x['file_name']) for x in row['web_selected_files']['geometry']])
    rep={'schema':'d1_bungie_web_gearasset_probe/v1','class_hash':a.class_hash,'is_female':a.female,'items':rows,'failure_item_hashes':failures,
         'policy':'Only data returned by Bungie /d1/Platform/Destiny/Manifest/22/{itemHash} and exact filenames serialized in that response are promoted. Archived Spasm selection rules are mirrored without appearance-based selection.'}
    a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(rep,indent=2)+'\n')
    return 0 if not failures else 4

if __name__=='__main__': raise SystemExit(main())
