#!/usr/bin/env python3
"""Recover exact D1 GearAsset rows from a pinned Bungie asset manifest database.

This is an evidence tool, not an API guesser.  It consumes an explicit Bungie
`asset_sql_content_*.content` URL (normally taken from a dated archived D1
Manifest response), queries `DestinyGearAssetsDefinition`, downloads the exact
`gear/*.js` files named by each row, and mirrors the archived Bungie Spasm web
selection logic for class/gender/index sets.

No geometry or region is selected from visual appearance.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import sqlite3
import tempfile
import urllib.request
import zipfile
from pathlib import Path
from typing import Any

BUNGIE='https://www.bungie.net'
GEAR_ROOT='/common/destiny_content/geometry/gear'
SKIP_REGION_KEYS={'2','6','21'}  # archived Spasm: hud, ammo, reticle


def get(url:str)->bytes:
    req=urllib.request.Request(url,headers={'User-Agent':'d1-reversal-evidence/1.0'})
    with urllib.request.urlopen(req,timeout=90) as r:
        return r.read()


def unwrap_sqlite(data:bytes)->bytes:
    if data.startswith(b'SQLite format 3\x00'):
        return data
    if data.startswith(b'PK\x03\x04'):
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            names=[n for n in z.namelist() if not n.endswith('/')]
            if len(names)!=1:
                raise ValueError(f'expected exactly one SQLite payload in Bungie content ZIP, got {names}')
            out=z.read(names[0])
            if not out.startswith(b'SQLite format 3\x00'):
                raise ValueError(f'{names[0]} is not SQLite')
            return out
    raise ValueError('asset content is neither SQLite nor a ZIP-wrapped SQLite database')


def signed32(v:int)->int:
    v &= 0xffffffff
    return v-0x100000000 if v>=0x80000000 else v


def pick_web_content(row:dict)->dict:
    content=row.get('content') or []
    selected=None
    for c in content:
        selected=c
        if c.get('platform')=='web':
            break
    if not selected:
        raise ValueError('GearAsset row has no content entries')
    if selected.get('platform')!='web':
        raise ValueError('GearAsset row has no web platform content')
    return selected


def exact_index_sets(c:dict,is_female:bool)->list[dict]:
    # Exact archived Spasm.TGXAssetLoader.onLoadAssetManifest contract.
    out=[]
    dye=c.get('dye_index_set')
    if dye: out.append({'kind':'dye','key':None,'set':dye})
    regions=c.get('region_index_sets')
    if regions:
        for key in regions:
            if str(key) in SKIP_REGION_KEYS:
                continue
            sets=regions[key]
            if sets:
                out.append({'kind':'region','key':str(key),'set':sets[0]})
    else:
        s=c.get('female_index_set') if is_female else c.get('male_index_set')
        if s: out.append({'kind':'female' if is_female else 'male','key':None,'set':s})
    return out


def selected_files(c:dict,index_sets:list[dict])->dict:
    gi=[]; ti=[]; pi=[]
    for entry in index_sets:
        s=entry['set'] or {}
        gi += list(s.get('geometry') or [])
        ti += list(s.get('textures') or [])
        pi += list(s.get('plate_regions') or [])
    # JS object maps used by Spasm deduplicate indices while preserving no semantic ordering.
    gi=list(dict.fromkeys(int(x) for x in gi)); ti=list(dict.fromkeys(int(x) for x in ti)); pi=list(dict.fromkeys(int(x) for x in pi))
    def names(field,inds):
        arr=c.get(field) or []
        rows=[]
        for i in inds:
            if i<0 or i>=len(arr): raise IndexError(f'{field}[{i}] out of range {len(arr)}')
            rows.append({'index':i,'file_name':arr[i]})
        return rows
    return {'geometry':names('geometry',gi),'textures':names('textures',ti),'plate_regions':names('plate_regions',pi)}


def choose_art_content(gear:dict,class_hash:int)->tuple[dict,dict]:
    art=gear.get('art_content')
    selection={'source':'art_content','class_hash':class_hash,'selected_art_content_set_index':None}
    sets=gear.get('art_content_sets')
    if sets and len(sets)>1:
        chosen=None; chosen_i=None
        for i,s in enumerate(sets):
            if chosen is None or int(s.get('classHash',-1))==class_hash:
                chosen=s; chosen_i=i
        if chosen is not None and chosen.get('arrangement') is not None:
            art=chosen['arrangement']; selection={'source':'art_content_sets.arrangement','class_hash':class_hash,'selected_art_content_set_index':chosen_i,'selected_class_hash':chosen.get('classHash')}
    if art is None: raise ValueError('gear JSON has no selected art content')
    return art,selection


def gear_identifiers(gear:dict,class_hash:int,is_female:bool)->tuple[list[Any],dict]:
    art,sel=choose_art_content(gear,class_hash)
    gs=art.get('gear_set') or {}
    ids=[]; detail=[]
    regions=gs.get('regions') or []
    if regions:
        for ri,region in enumerate(regions):
            pats=region.get('pattern_list') or []
            if not pats: continue
            geom=list(pats[0].get('geometry_hashes') or [])
            ids += geom
            detail.append({'region_index':ri,'pattern_index':0,'geometry_hashes':geom})
        sel['gear_set_path']='regions[*].pattern_list[0].geometry_hashes'
    else:
        aa=gs.get('female_override_art_arrangement') if is_female else gs.get('base_art_arrangement')
        if aa is not None:
            geom=list(aa.get('geometry_hashes') or [])
            ids += geom; detail.append({'geometry_hashes':geom})
        sel['gear_set_path']='female_override_art_arrangement.geometry_hashes' if is_female else 'base_art_arrangement.geometry_hashes'
    return ids,{'selection':sel,'sources':detail}


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--asset-db-url',required=True)
    ap.add_argument('--item-hash',action='append',required=True,help='hex or decimal inventory/GearAsset id')
    ap.add_argument('--class-hash',type=lambda x:int(x,0),default=3655393761)
    ap.add_argument('--female',action='store_true')
    ap.add_argument('--download-gear-dir',type=Path)
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args()
    wanted=[]
    for s in a.item_hash:
        ss=s.strip(); wanted.append(int(ss,16) if ss.lower().startswith('0x') or any(c in 'abcdefABCDEF' for c in ss) else int(ss,10))
        wanted[-1] &= 0xffffffff

    raw=get(a.asset_db_url); dbbytes=unwrap_sqlite(raw)
    with tempfile.NamedTemporaryFile(suffix='.sqlite') as f:
        f.write(dbbytes); f.flush(); con=sqlite3.connect(f.name)
        tables={r[0] for r in con.execute("select name from sqlite_master where type='table'")}
        if 'DestinyGearAssetsDefinition' not in tables:
            raise ValueError(f'DestinyGearAssetsDefinition absent; tables={sorted(tables)}')
        rows=[]
        for item in wanted:
            r=con.execute('select id,json from DestinyGearAssetsDefinition where id=?',(signed32(item),)).fetchone()
            if r is None:
                r=con.execute('select id,json from DestinyGearAssetsDefinition where id=?',(item,)).fetchone()
            if r is None: raise KeyError(f'GearAsset {item} / 0x{item:08X} absent from pinned DB')
            obj=json.loads(r[1]); c=pick_web_content(obj); sets=exact_index_sets(c,a.female); files=selected_files(c,sets)
            gears=[]
            for gname in obj.get('gear') or []:
                url=f"{BUNGIE}{GEAR_ROOT}/{gname}"
                gb=get(url); gj=json.loads(gb.decode('utf-8-sig'))
                ids,artsel=gear_identifiers(gj,a.class_hash,a.female)
                if a.download_gear_dir:
                    a.download_gear_dir.mkdir(parents=True,exist_ok=True); (a.download_gear_dir/gname).write_bytes(gb)
                gears.append({'file_name':gname,'url':url,'sha256':hashlib.sha256(gb).hexdigest(),'geometry_identifiers':ids,'art_selection':artsel})
            rows.append({
                'item_hash_decimal':item,'item_hash_hex':f'{item:08X}','database_id':r[0],
                'gearasset':obj,'web_content_index_sets':sets,'web_selected_files':files,'gear_json':gears,
            })
        con.close()

    rep={
      'schema':'d1_legacy_gearasset_rows/v1','asset_db_url':a.asset_db_url,
      'asset_db_download_sha256':hashlib.sha256(raw).hexdigest(),'sqlite_sha256':hashlib.sha256(dbbytes).hexdigest(),
      'class_hash':a.class_hash,'is_female':a.female,'items':rows,
      'policy':('Rows come directly from the explicitly pinned Bungie DestinyGearAssetsDefinition SQLite database. '
                'Web index-set and art-content selection mirrors archived Bungie Spasm.TGXAssetLoader. No geometry is enabled by appearance.')
    }
    a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(rep,indent=2)+'\n')
    print('DB',len(raw),'bytes',rep['asset_db_download_sha256'],'sqlite',len(dbbytes),rep['sqlite_sha256'])
    for x in rows:
        print(x['item_hash_hex'],'gear',[(g['file_name'],g['geometry_identifiers']) for g in x['gear_json']],
              'selected geometry files',[z['file_name'] for z in x['web_selected_files']['geometry']])
    return 0

if __name__=='__main__': raise SystemExit(main())
