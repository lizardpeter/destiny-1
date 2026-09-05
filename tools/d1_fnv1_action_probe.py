#!/usr/bin/env python3
"""Scan D1 ROI structured entries for exact FNV1 lowercase action/state hashes.

Destiny 1 uses 32-bit FNV1 string hashes extensively. This tool is intentionally
semantic-conservative: a name is reported only when its exact FNV1 hash occurs
as an aligned uint32 in retail bytes. It does not infer that the containing
record *uses* the value as an animation state unless surrounding structure
proves that separately.
"""
from __future__ import annotations
import argparse,json,struct,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from d1_entry_extract import EntryReader

DEFAULTS=[
 'base','fire','fire_1','fire_2','fire_3','recoil','reload','reload_1','reload_2','reload_3',
 'reload_empty','reload_full','idle','ready','ready_1','ready_2','equip','stow','sprint','zoom',
 'aim','ads','melee','inspect','lower','raise','charge','release','shoot','firing','trigger',
 'primary_fire','secondary_fire','fire_primary','fire_secondary','hip_fire','aim_fire','fire_hip',
 'fire_ads','ads_fire','zoom_fire','jump','land','walk','run','rocket_launcher','first_person','weapon'
]

def fnv1(s:str)->int:
    h=0x811C9DC5
    for c in s.lower().encode('utf-8'):
        h=(h*0x01000193)&0xffffffff
        h^=c
    return h

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('pkg',type=Path)
    ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('--name',action='append',default=[])
    ap.add_argument('--all-types',action='store_true',help='scan all readable entries, not just structured type 16')
    ap.add_argument('--entry-radius',type=int,default=0,help='include metadata for neighboring entries around each hit')
    ap.add_argument('-o','--output',type=Path)
    a=ap.parse_args()
    names=[]
    for s in DEFAULTS+a.name:
        s=s.strip().lower()
        if s and s not in names:names.append(s)
    mapping={fnv1(s):s for s in names}
    # Self-calibration from byte-proven project discoveries.
    assert fnv1('rocket_launcher')==0xC9EB0270
    assert fnv1('reload_1')==0xEB22859A
    assert fnv1('fire')==0x9FAC79C9
    assert fnv1('reload_empty')==0x6D507AD8
    assert fnv1('reload_full')==0x28F43BD2
    r=EntryReader(a.pkg,a.runtime)
    hits=[]
    for e in r.entries:
        if not a.all_types and e['type']!=16:continue
        if not r.available(e['index']):continue
        try:b=r.entry(e['index'])
        except Exception:continue
        eh=[]
        for off in range(0,len(b)-(len(b)%4),4):
            v=struct.unpack_from('<I',b,off)[0]
            if v in mapping:eh.append({'offset':off,'hash':f'{v:08X}','name':mapping[v]})
        if eh:
            q={'entry':{'index':e['index'],'tag_hash':e['tag_hash'].upper(),'reference':e['reference'].upper(),'type':e['type'],'subtype':e['subtype'],'size':e['file_size']},'hits':eh}
            if a.entry_radius:
                nb=[]
                for i in range(max(0,e['index']-a.entry_radius),min(len(r.entries),e['index']+a.entry_radius+1)):
                    x=r.entries[i];nb.append({'relative_index':i-e['index'],'index':i,'tag_hash':x['tag_hash'].upper(),'reference':x['reference'].upper(),'type':x['type'],'subtype':x['subtype'],'size':x['file_size']})
                q['neighborhood']=nb
            hits.append(q)
    out={'package':str(r.pkg),'pkg_id':r.h['pkg_id'],'hashes':{s:f'{fnv1(s):08X}' for s in names},'hit_entry_count':len(hits),'hits':hits,
         'evidence_policy':'Reported names are exact lowercase FNV1 preimages from the requested dictionary. Container semantics require independent structural evidence.'}
    text=json.dumps(out,indent=2)
    if a.output:a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(text+'\n');print('wrote',a.output)
    else:print(text)
    return 0
if __name__=='__main__':raise SystemExit(main())
