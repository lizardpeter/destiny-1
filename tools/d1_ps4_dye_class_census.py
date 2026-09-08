#!/usr/bin/env python3
"""Census exact retail SDye_D1 entries in supplied PS4 package snapshots.

Uses the already source-closed D1 F41A8080 / numeric 80801AF4 class and the
exact SDye_D1 payload parser. This tool only reports physical dye records and
serialized textures/constants; it does not infer ownership by an entity or a
shader runtime binding.
"""
from __future__ import annotations
import argparse,json,sys
from collections import Counter
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import d1_tower_map_schema_validate_v5 as v5
from d1_investment_dye_resolver import DYE_CLASS,parse_dye_payload

def norm(x):return str(x).upper().removeprefix('0X').zfill(8)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--snapshot',type=Path,action='append',required=True);ap.add_argument('--runtime',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
 c=v5.v3.base.Corpus([p.resolve() for p in a.snapshot],a.runtime.resolve());rows=[];errors=[];candidate=0
 for p,r in c.readers:
  for e in r.entries:
   if int(str(e.get('reference','0')),16)!=DYE_CLASS:continue
   candidate+=1
   if not r.available(e['index']):
    errors.append({'snapshot':p.name,'material':norm(e.get('tag_hash','')),'error':'payload unavailable'});continue
   try:d=parse_dye_payload(r.entry(e['index']))
   except Exception as ex:
    errors.append({'snapshot':p.name,'tag_hash':norm(e.get('tag_hash','')),'error':repr(ex)});continue
   rows.append({'snapshot':p.name,'package_id':f"{int(r.h['pkg_id']):04X}",'entry_index':int(e['index']),'dye':norm(e['tag_hash']),'payload':d})
 rows.sort(key=lambda x:(x['dye'],x['snapshot'])); unique=sorted({x['dye'] for x in rows})
 slot=Counter(str(x['payload']['slot_type_index']) for x in rows); dd=Counter(x['payload']['detail_diffuse_texture_hash'] for x in rows); dn=Counter(x['payload']['detail_normal_texture_hash'] for x in rows)
 out={'schema_version':1,'status':'D1_PS4_SDYE_D1_CLASS_CENSUS_EXACT' if not errors else 'D1_PS4_SDYE_D1_CLASS_CENSUS_PARTIAL','direct_class_reference':'80801AF4','charm_display_class':'F41A8080','candidate_entry_count':candidate,'decoded_occurrence_count':len(rows),'unique_dye_count':len(unique),'unique_dyes':unique,'slot_type_histogram':dict(slot),'detail_diffuse_histogram':dict(dd),'detail_normal_histogram':dict(dn),'rows':rows,'decode_errors':errors,'policy':'Direct package-entry class census and exact SDye_D1 fields only; no entity ownership or shader t# binding inferred.'}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k] for k in ['status','candidate_entry_count','decoded_occurrence_count','unique_dye_count','slot_type_histogram','detail_diffuse_histogram','detail_normal_histogram','decode_errors']},indent=2));return 0 if not errors else 2
if __name__=='__main__':raise SystemExit(main())
